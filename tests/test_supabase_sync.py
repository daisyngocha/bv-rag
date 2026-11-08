"""Đồng bộ Supabase: dựng dòng từ file thật của repo, ghi qua DB giả (không cần mạng)."""
import csv
import json
from pathlib import Path

import pytest

from scripts import seed_demo_users as seed
from scripts import sync_supabase as sync

CATALOG = json.load(open("data/catalog.json", encoding="utf-8"))
SOURCES = list(csv.DictReader(open("data/raw/sources.csv", encoding="utf-8")))


def fake_chunks():
    out = []
    for p in CATALOG["products"]:
        for i, d in enumerate(p["documents"]):
            out.append({"chunk_id": f"{p['product_code']}_X_{i}", "product_code": p["product_code"],
                        "doc_type": d["doc_type"], "source_file": Path(d["file"]).name, "section_path": "Mục 1",
                        "page": 1, "is_table": False, "effective_date": d.get("effective_date"),
                        "text": f"[{p['product_name']} | x | Mục 1]\nNội dung"})
    return out


class FakeDB:
    def __init__(self, users=None):
        self.calls, self.users, self.next_id = [], list(users or []), 1

    def upsert(self, table, rows, on_conflict, returning=False, batch=500, ignore_duplicates=False):
        rows = list(rows)
        self.calls.append(("upsert", table, on_conflict, rows))
        if table == "documents" and returning:
            return [{**r, "id": i} for i, r in enumerate(rows, 1)]
        return []

    def update(self, table, values, returning=False, **filters):
        self.calls.append(("update", table, values, filters))
        return []

    def select(self, table, **params):
        return {"pipeline_configs": [{"name": n} for n in ("B0", "B1", "B2", "B3", "B3hyb", "B4", "B4rr", "B4ng")],
                "data_versions": [{"version": "v1"}]}[table]

    def list_users(self):
        return self.users

    def create_user(self, email, password, user_metadata=None, app_metadata=None):
        u = {"id": f"uid-{self.next_id}", "email": email}
        self.next_id += 1
        self.calls.append(("create_user", email, password, user_metadata, app_metadata))
        return u

    def update_user(self, user_id, **attrs):
        self.calls.append(("update_user", user_id, attrs))
        return {"id": user_id}


def test_build_kb_rows_maps_documents_and_skips_legal():
    kb = sync.build_kb_rows("v1", CATALOG, SOURCES, fake_chunks())
    assert len(kb["products"]) == 5
    assert {d["doc_type"] for d in kb["documents"]} <= sync.DOC_TYPES
    assert all("/" not in d["source_file"] for d in kb["documents"])
    assert kb["skipped_sources"], "văn bản pháp luật phải bị bỏ qua"
    assert kb["data_version"]["n_chunks"] == len(kb["chunks"])


def test_build_kb_rows_rejects_unknown_source_and_manifest_mismatch():
    bad = fake_chunks()
    bad[0]["source_file"] = "khong_co.pdf"
    with pytest.raises(ValueError, match="source_file"):
        sync.build_kb_rows("v1", CATALOG, SOURCES, bad)
    with pytest.raises(ValueError, match="manifest"):
        sync.build_kb_rows("v1", CATALOG, SOURCES, fake_chunks(), {"counts": {"structure": {"total": 634}}})


def test_sync_kb_writes_in_fk_order_and_activates(tmp_path):
    (tmp_path / "chunks.jsonl").write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in fake_chunks()),
                                           encoding="utf-8")
    db = FakeDB()
    sync.sync_kb(db, "v1", tmp_path, activate=True, manifest_dir=tmp_path)
    tables = [c[1] for c in db.calls]
    assert tables == ["data_versions", "products", "documents", "chunks", "data_versions", "data_versions"]
    chunk_rows = db.calls[3][3]
    assert all(isinstance(r["document_id"], int) and "source_file" not in r for r in chunk_rows)
    assert db.calls[4][2] == {"is_active": False} and db.calls[5][2] == {"is_active": True}


def test_config_rows_include_ablation_and_skip_non_pipeline():
    rows = sync.build_config_rows()
    names = {r["name"] for r in rows}
    assert {"B0", "B1", "B2", "B3", "B4", "B3hyb", "B4rr", "B4ng"} <= names
    b0 = next(r for r in rows if r["name"] == "B0")
    assert b0["description"] and b0["params"]["data_version"] == "v1"


def test_sample_questions_dev_only():
    rows = sync.build_sample_rows("benchmark/benchmark_v1.jsonl")
    assert len(rows) == 24 and {r["question_group"] for r in rows} == sync.SAMPLE_GROUPS
    with pytest.raises(ValueError):
        sync.build_sample_rows("benchmark/benchmark_v1.jsonl", split="test")


def test_eval_rows_from_results_csv():
    configs = {r["name"] for r in sync.build_config_rows()}
    runs, evals = sync.build_eval_rows("results", "runs", configs, "benchmark/benchmark_v1.jsonl")
    ids = {r["run_id"] for r in runs}
    assert "B4_v1_test_20261107-1335" in ids
    b4 = next(r for r in runs if r["run_id"] == "B4_v1_test_20261107-1335")
    assert b4["split"] == "test" and b4["data_version"] == "v1" and b4["n"] == 120
    assert b4["started_at"].startswith("2026-11-07T13:35")
    keys = [(e["run_id"], e["question_group"], e["metric"]) for e in evals]
    assert len(keys) == len(set(keys))
    r5 = next(e for e in evals if e["run_id"] == "B4_v1_test_20261107-1335" and e["question_group"] == "all"
              and e["metric"] == "recall@5")
    assert r5["value"] == pytest.approx(0.9062)
    assert not any(e["metric"] == "official" for e in evals)


def test_eval_rows_require_known_config():
    with pytest.raises(ValueError, match="pipeline_configs"):
        sync.build_eval_rows("results", "runs", {"B0"})


def test_seed_creates_missing_and_updates_existing(monkeypatch, tmp_path):
    monkeypatch.setenv("DEMO_PW_DEMO01", "MatKhau#2026")
    monkeypatch.delenv("DEMO_PW_ADMIN01", raising=False)
    db = FakeDB(users=[{"id": "uid-old", "email": "demo02@bv-rag.local"}])
    out = {r["username"]: r for r in seed.seed_users(db)}
    assert out["demo01"]["action"] == "created" and out["demo01"]["temp_password"] is None
    assert out["admin01"]["temp_password"]                     # thiếu biến môi trường → sinh mật khẩu tạm
    assert out["demo02"]["action"] == "updated"
    upd = next(c for c in db.calls if c[0] == "update_user")
    assert "password" not in upd[2] and upd[2]["app_metadata"] == {"role": "user"}
    created = {c[1]: c for c in db.calls if c[0] == "create_user"}
    assert created["admin01@bv-rag.local"][4] == {"role": "admin"}
    profiles = [c[3][0] for c in db.calls if c[0] == "upsert" and c[1] == "profiles"]
    assert {p["username"]: p["role"] for p in profiles}["admin01"] == "admin"


def test_seed_spec_rejects_real_email(tmp_path):
    p = tmp_path / "u.yaml"
    p.write_text("users:\n  - {username: x, email: x@gmail.com, role: user}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="bv-rag.local"):
        seed.load_spec(p)
