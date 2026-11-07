"""Soạn nháp benchmark bằng Gemini → người duyệt trên Excel → benchmark/benchmark_v1.jsonl. Chạy trên WSL, ở gốc repo.

Chỉ gửi Gemini chunk từ tài liệu công khai. Gemini viết câu hỏi/đáp án; evidence do code chọn; số trong đáp án
được code đối chiếu với text evidence (không để LLM quyết định con số).

    export GEMINI_API_KEY=...                                    # hoặc: set -a; source .env; set +a
    PYTHONPATH=. python -m eval.bench_draft models               # chọn model, ghi vào benchmark/draft_config.yaml
    PYTHONPATH=. python -m eval.bench_draft sample  --tag w3     # → benchmark/drafts/w3_tasks.jsonl
    PYTHONPATH=. python -m eval.bench_draft draft   --tag w3     # → benchmark/drafts/w3_drafts.jsonl (chạy lại để tiếp)
    PYTHONPATH=. python -m eval.bench_draft review  --tag w3     # → benchmark/drafts/w3_review.csv (duyệt trên Excel)
    PYTHONPATH=. python -m eval.bench_draft build                # mọi *_review.csv → benchmark/benchmark_v1.jsonl
    PYTHONPATH=. python -m eval.bench_draft sample --tag w3b --only out_of_scope   # soạn bổ sung 1 nhóm
"""
import argparse, csv, difflib, json, os, random, re, sys, time
from datetime import datetime
from itertools import combinations
from pathlib import Path

import yaml

from eval.benchmark import GROUPS, load_chunks, missing_numbers, read_jsonl, summary, validate
from src.ingest.catalog import FIELDS as CATALOG_FIELDS, numbers
from src.ingest.glossary import norm_term

CFG_PATH, DRAFTS = Path("benchmark/draft_config.yaml"), Path("benchmark/drafts")
CFG_DIR = Path("configs/products")
SCENARIO_RE = re.compile(r"thời gian chờ|loại trừ|đồng chi trả|không chi trả|không thuộc phạm vi|chỉ chi trả|giới hạn", re.I)
REVIEW_COLS = ["draft_id", "group", "difficulty", "products", "split", "decision", "question", "answer",
               "edited_question", "edited_answer", "evidence_ids", "flags", "evidence_text", "note"]

PROMPTS = {
    "lookup": """Bạn soạn câu hỏi kiểm thử cho hệ thống hỏi đáp về sản phẩm bảo hiểm {product_names}.
Từ ĐOẠN dưới đây, viết 1 câu hỏi tra cứu một thông tin cụ thể mà khách hàng hoặc tư vấn viên có thể hỏi.""",
    "table": """Bạn soạn câu hỏi kiểm thử cho hệ thống hỏi đáp về sản phẩm bảo hiểm {product_names}.
ĐOẠN dưới đây là bảng (quyền lợi hoặc biểu phí). Viết 1 câu hỏi cần đọc đúng một ô của bảng (giao của một dòng và một cột,
ví dụ một quyền lợi ở một chương trình, hoặc mức phí ở một nhóm tuổi). Đáp án ghi đúng giá trị ô đó.""",
    "compare": """Bạn soạn câu hỏi kiểm thử cho hệ thống hỏi đáp về sản phẩm bảo hiểm.
Các ĐOẠN dưới đây thuộc các sản phẩm {product_names}{topic}. Viết 1 câu hỏi so sánh các sản phẩm này về cùng một khía cạnh;
đáp án nêu giá trị của từng sản phẩm và điểm khác nhau.""",
    "scenario": """Bạn soạn câu hỏi kiểm thử cho hệ thống hỏi đáp về sản phẩm bảo hiểm {product_names}.
Từ ĐOẠN dưới đây (điều kiện, thời gian chờ, loại trừ hoặc giới hạn chi trả), viết 1 tình huống cụ thể của một khách hàng
(tuổi, thời điểm tham gia, sự kiện xảy ra) và hỏi có được chi trả không hoặc được chi trả thế nào.
Đáp án nêu kết luận và căn cứ trong đoạn.""",
    "out_of_scope": """Hệ thống hỏi đáp chỉ có quy tắc, bảng quyền lợi và biểu phí của 5 sản phẩm: {product_names}.
Viết 1 câu hỏi tự nhiên mà khách hàng có thể hỏi nhưng các tài liệu này KHÔNG trả lời được, thuộc loại: {hint}.
Không hỏi điều có thể suy ra từ quy tắc, bảng quyền lợi hay biểu phí.""",
}
RULES = """
Yêu cầu:
- Diễn đạt tự nhiên bằng tiếng Việt, KHÔNG chép nguyên câu trong tài liệu.
- Câu hỏi phải nêu tên sản phẩm để không mơ hồ giữa các sản phẩm.
- Đáp án ngắn (1–3 câu), CHỈ dùng thông tin trong đoạn, giữ nguyên số liệu và đơn vị như trong đoạn.
- Nếu đoạn không đủ để đặt một câu hỏi rõ ràng có một đáp án duy nhất, trả {{"skip": true, "reason": "..."}}.
Trả về đúng một đối tượng JSON: {{"question": "...", "answer": "...", "difficulty": "easy|medium|hard"}}
"""
OOS_RULES = """
Trả về đúng một đối tượng JSON: {{"question": "...", "reason": "vì sao tài liệu không trả lời được", "difficulty": "easy|medium|hard"}}
"""


def cfg() -> dict:
    return yaml.safe_load(open(CFG_PATH, encoding="utf-8"))


def product_meta() -> tuple[dict, dict]:
    names, def_prefix = {}, {}
    for p in CFG_DIR.glob("*.yaml"):
        pc = yaml.safe_load(open(p, encoding="utf-8"))
        names[pc["product_code"]] = pc["product_name"]
        if d := (pc.get("checks") or {}).get("definitions"):
            def_prefix[pc["product_code"]] = d["prefix"]
    return names, def_prefix


# ---------- sample ----------
def pick_round_robin(pool: dict[str, list], n: int, rng: random.Random, used: set) -> list[dict]:
    for v in pool.values():
        rng.shuffle(v)
    out, products = [], sorted(pool)
    while len(out) < n and any(pool[p] for p in products):
        for p in products:
            while pool[p] and pool[p][-1]["chunk_id"] in used:
                pool[p].pop()
            if pool[p] and len(out) < n:
                c = pool[p].pop()
                used.add(c["chunk_id"])
                out.append(c)
    return out


def compare_pairs(c: dict, chunks: dict) -> list[dict]:
    """Cặp từ catalog (cùng trường) và glossary (cùng thuật ngữ, định nghĩa khác nhau)."""
    pairs = []
    cat = json.load(open("data/catalog.json", encoding="utf-8"))["products"]
    avoid = c.get("avoid_catalog", {})
    fields = ["age_min", "age_max", "renewal_age_max", "term", "waiting_period", "territory", "programs", "sum_insured"]
    for f in fields:
        have = []
        for p in cat:
            v = p["fields"].get(f)
            if v and f not in avoid.get(p["product_code"], []):
                v = v[0] if isinstance(v, list) else v
                have.append((p["product_code"], v["source"]))
        for (p1, s1), (p2, s2) in combinations(have, 2):
            pairs.append({"topic": f"catalog:{f}", "evidence_ids": [s1, s2], "products": [p1, p2]})
    gl = json.load(open("data/glossary.json", encoding="utf-8"))["entries"]
    by_term: dict[str, list] = {}
    for e in gl:
        if e["scope"] != "general":
            by_term.setdefault(norm_term(e["term"]), []).append(e)
    for term, es in by_term.items():
        for a, b in combinations(es, 2):
            if a["scope"] != b["scope"] and norm_term(a["definition"]) != norm_term(b["definition"]):
                pairs.append({"topic": f"glossary:{a['term']}", "evidence_ids": [a["source"], b["source"]],
                              "products": [a["scope"], b["scope"]]})
    return [p for p in pairs if all(e in chunks for e in p["evidence_ids"])]


def sample(tag: str, processed: Path, only: str | None = None) -> Path:
    c, chunks = cfg(), load_chunks(processed)
    names, def_prefix = product_meta()
    rng, used, tasks = random.Random(c["seed"]), set(), []
    is_def = lambda ch: any(ch["chunk_id"].startswith(px) for px in def_prefix.values())

    def pool(pred):
        d: dict[str, list] = {}
        for ch in chunks.values():
            if pred(ch):
                d.setdefault(ch["product_code"], []).append(ch)
        return d

    n = c["per_group"]
    n_def = round(n["lookup"] * c["lookup_def_share"])
    groups = {
        "lookup": pick_round_robin(pool(lambda x: x["doc_type"] == "quy_tac" and not x["is_table"] and not is_def(x)
                                        and len(x["text"]) >= 300), n["lookup"] - n_def, rng, used)
                  + pick_round_robin(pool(is_def), n_def, rng, used),
        "table": pick_round_robin(pool(lambda x: x["is_table"]), n["table"], rng, used),
        "scenario": pick_round_robin(pool(lambda x: x["doc_type"] == "quy_tac" and not x["is_table"] and not is_def(x)
                                          and SCENARIO_RE.search(x["text"])), n["scenario"], rng, used),
    }
    for g, chs in groups.items():
        for ch in chs:
            tasks.append({"group": g, "evidence_ids": [ch["chunk_id"]], "products": [ch["product_code"]]})
    pairs = compare_pairs(c, chunks)
    rng.shuffle(pairs)
    cat_pairs = [p for p in pairs if p["topic"].startswith("catalog")]
    gl_pairs = [p for p in pairs if p["topic"].startswith("glossary")]
    half = n["compare"] // 2
    for p in cat_pairs[:half] + gl_pairs[:n["compare"] - min(half, len(cat_pairs))]:
        tasks.append({"group": "compare", **p})
    for cat_name, spec in c["out_of_scope"].items():
        for _ in range(spec["n"]):
            tasks.append({"group": "out_of_scope", "evidence_ids": [], "products": [], "topic": cat_name})
    if only:
        tasks = [t for t in tasks if t["group"] == only]
    for i, t in enumerate(tasks, 1):
        t["task_id"] = f"{tag}-{i:03d}"
    DRAFTS.mkdir(parents=True, exist_ok=True)
    out = DRAFTS / f"{tag}_tasks.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    from collections import Counter
    print(f"{len(tasks)} task: {dict(Counter(t['group'] for t in tasks))} → {out}")
    return out


# ---------- draft ----------
def build_prompt(t: dict, chunks: dict, names: dict, c: dict, avoid: list[str] = ()) -> str:
    if t["group"] == "out_of_scope":
        spec = c["out_of_scope"][t["topic"]]
        prev = "".join(f"\n- {q}" for q in avoid)
        extra = f"\nKhông lặp lại ý của các câu đã có:{prev}\n" if prev else ""
        return (PROMPTS["out_of_scope"].format(product_names=", ".join(names.values()), hint=spec["hint"])
                + extra + OOS_RULES.format())
    pn = ", ".join(names[p] for p in t["products"])
    topic = ""
    if t["group"] == "compare":
        kind, val = t["topic"].split(":", 1)
        label = CATALOG_FIELDS[val][0].split(" (")[0].lower() if kind == "catalog" else f"định nghĩa '{val}'"
        topic = f" (khía cạnh gợi ý: {label})"
    doan = "\n\n".join(f"[{e}]\n{chunks[e]['text']}" for e in t["evidence_ids"])
    return PROMPTS[t["group"]].format(product_names=pn, topic=topic) + RULES.format() + f"\nĐOẠN:\n{doan}\n"


def draft(tag: str, processed: Path) -> None:
    from google import genai
    from google.genai import types
    c, chunks = cfg(), load_chunks(processed)
    if not c.get("model"):
        sys.exit("Chưa đặt model trong benchmark/draft_config.yaml (chạy lệnh models để xem)")
    names, _ = product_meta()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    tasks = read_jsonl(DRAFTS / f"{tag}_tasks.jsonl")
    out = DRAFTS / f"{tag}_drafts.jsonl"
    done = {d["task_id"] for d in read_jsonl(out)} if out.exists() else set()
    oos_seen = {}                                # câu ngoài phạm vi đã có (mọi tag) theo loại, để Gemini không lặp ý
    for path in DRAFTS.glob("*_drafts.jsonl"):
        for d in read_jsonl(path):
            if d["group"] == "out_of_scope" and d["output"].get("question"):
                oos_seen.setdefault(d["topic"], [])
                if d["output"]["question"] not in oos_seen[d["topic"]]:
                    oos_seen[d["topic"]].append(d["output"]["question"])
    with open(out, "a", encoding="utf-8") as f:
        for i, t in enumerate(tasks):
            if t["task_id"] in done:
                continue
            gen_cfg = types.GenerateContentConfig(temperature=c["temperature"], seed=c["seed"] + i,  # seed riêng mỗi task
                                                  response_mime_type="application/json")
            rec = {**t, "model": c["model"], "prompt_version": c["prompt_version"],
                   "created_at": datetime.now().isoformat(timespec="seconds")}
            try:
                avoid = oos_seen.get(t.get("topic"), []) if t["group"] == "out_of_scope" else []
                resp = client.models.generate_content(model=c["model"], contents=build_prompt(t, chunks, names, c, avoid),
                                                      config=gen_cfg)
                rec["output"] = json.loads(resp.text)
                if t["group"] == "out_of_scope" and rec["output"].get("question"):
                    oos_seen.setdefault(t["topic"], []).append(rec["output"]["question"])
            except Exception as e:                       # ghi lỗi để chạy lại; không dừng cả lô
                rec["error"] = f"{type(e).__name__}: {e}"[:300]
            if "error" not in rec:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
            print(t["task_id"], t["group"], "lỗi: " + rec["error"] if "error" in rec else "ok")
            time.sleep(c["sleep_s"])


# ---------- review ----------
def longest_common_words(a: str, b: str) -> int:
    wa, wb = a.lower().split(), b.lower().split()
    m = difflib.SequenceMatcher(None, wa, wb, autojunk=False).find_longest_match(0, len(wa), 0, len(wb))
    return m.size


def review(tag: str, processed: Path, force: bool = False) -> Path:
    out = DRAFTS / f"{tag}_review.csv"
    if out.exists() and not force and any(r["decision"] and not r["decision"].startswith("drop")
                                          for r in csv.DictReader(open(out, encoding="utf-8-sig"))):
        sys.exit(f"{out} đã có quyết định duyệt; không ghi đè (thêm --force nếu chắc chắn)")
    c, chunks = cfg(), load_chunks(processed)
    drafts = read_jsonl(DRAFTS / f"{tag}_drafts.jsonl")
    rows, seen_q, dev_count = [], [], {g: 0 for g in GROUPS}
    for d in drafts:
        o, flags = d["output"], []
        if o.get("skip"):
            flags.append(f"LLM bỏ qua: {o.get('reason', '')}")
        q = o.get("question", "")
        ans = c["refusal"] if d["group"] == "out_of_scope" else o.get("answer", "")
        texts = [chunks[e]["text"] for e in d["evidence_ids"]]
        if d["group"] != "out_of_scope":
            if miss := missing_numbers(ans, texts):
                flags.append(f"SỐ KHÔNG CÓ TRONG EVIDENCE {miss}")
            for p in d["products"]:
                if bad := set(numbers(ans)) & {x.replace(".", "") for x in c["avoid_numbers"].get(p, [])}:
                    flags.append(f"ô cần tránh {sorted(bad)}")
            if any(chunks[e].get("ocr") for e in d["evidence_ids"]):
                flags.append("evidence OCR")
            if max((longest_common_words(q, t) for t in texts), default=0) >= 8:
                flags.append("câu hỏi chép ≥ 8 từ liên tiếp của tài liệu")
        else:
            flags.append(f"ngoài phạm vi ({d['topic']}): {o.get('reason', '')}")
        sim = max((difflib.SequenceMatcher(None, q.lower(), s).ratio() for s in seen_q), default=0)
        if sim >= 0.8:
            flags.append(f"gần trùng câu khác ({sim:.2f})")
        seen_q.append(q.lower())
        split = "test"
        if not o.get("skip") and dev_count[d["group"]] < c["dev_prefill"]:
            split, dev_count[d["group"]] = "dev", dev_count[d["group"]] + 1
        rows.append({"draft_id": d["task_id"], "group": d["group"], "difficulty": o.get("difficulty", "medium"),
                     "products": ";".join(d["products"]), "split": split,
                     "decision": "drop" if o.get("skip") else "", "question": q, "answer": ans,
                     "edited_question": "", "edited_answer": "", "evidence_ids": ";".join(d["evidence_ids"]),
                     "flags": " | ".join(flags),
                     "evidence_text": "\n\n".join(f"[{e}]\n{chunks[e]['text']}" for e in d["evidence_ids"])[:6000],
                     "note": ""})
    with open(out, "w", encoding="utf-8-sig", newline="") as f:     # utf-8-sig: Excel mở đúng tiếng Việt
        w = csv.DictWriter(f, fieldnames=REVIEW_COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} câu, {sum(bool(r['flags']) and r['group'] != 'out_of_scope' for r in rows)} câu có cờ → {out}")
    return out


# ---------- build ----------
def build(processed: Path, out: Path, final: bool) -> None:
    c, chunks = cfg(), load_chunks(processed)
    old = {r["source_draft"]: r["qid"] for r in read_jsonl(out)} if out.exists() else {}
    next_no = max((int(q.split("-")[1]) for q in old.values()), default=0) + 1
    rows = []
    for path in sorted(DRAFTS.glob("*_review.csv")):
        for r in csv.DictReader(open(path, encoding="utf-8-sig")):
            dec = r["decision"].strip().lower()
            if dec not in ("keep", "edit"):
                continue
            answerable = r["group"] != "out_of_scope"
            qid = old.get(r["draft_id"])
            if not qid:
                qid, next_no = f"{c['data_version']}-{next_no:04d}", next_no + 1
            rows.append({"qid": qid, "question": (r["edited_question"] or r["question"]).strip(),
                         "answer": (r["edited_answer"] or r["answer"]).strip() if answerable else c["refusal"],
                         "evidence_ids": [e for e in r["evidence_ids"].split(";") if e] if answerable else [],
                         "products": [p for p in r["products"].split(";") if p],
                         "group": r["group"], "difficulty": r["difficulty"].strip(), "answerable": answerable,
                         "split": r["split"].strip(), "created_by": "llm_draft+human", "version": "v1",
                         "source_draft": r["draft_id"]})
    rows.sort(key=lambda r: r["qid"])
    errors, warnings = validate(rows, chunks, c["refusal"], final)
    print(f"{len(rows)} câu\n{summary(rows) if rows else ''}")
    for w in warnings:
        print("  cảnh báo:", w)
    if errors:
        sys.exit("Lỗi, chưa ghi file:\n  " + "\n  ".join(errors))
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"→ {out}")


def models() -> None:
    from google import genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    for m in client.models.list():
        if "generateContent" in (getattr(m, "supported_actions", None) or []):
            print(m.name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["models", "sample", "draft", "review", "build"])
    ap.add_argument("--tag", default="w3")
    ap.add_argument("--processed", type=Path, default=Path("data/processed/v1"))
    ap.add_argument("--out", type=Path, default=Path("benchmark/benchmark_v1.jsonl"))
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--only", choices=GROUPS, help="sample: chỉ lấy task của 1 nhóm")
    ap.add_argument("--force", action="store_true", help="review: ghi đè file duyệt đã có")
    a = ap.parse_args()
    {"models": models, "sample": lambda: sample(a.tag, a.processed, a.only), "draft": lambda: draft(a.tag, a.processed),
     "review": lambda: review(a.tag, a.processed, a.force), "build": lambda: build(a.processed, a.out, a.final)}[a.cmd]()


if __name__ == "__main__":
    main()
