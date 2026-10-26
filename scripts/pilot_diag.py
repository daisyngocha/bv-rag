import collections, warnings
warnings.filterwarnings("ignore", message="Provenance bbox")
from pypdf import PdfReader, PdfWriter
from docling_core.types.doc import DoclingDocument
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from src.ingest.parser import build_converter

# A. Bản chất 26k item text
doc = DoclingDocument.load_from_json("logs/pilot_bvp/parsed_pdfium/bvp_quytac.docling.json")
per_page, flat, short, junk = collections.Counter(), 0, 0, []
for it, _ in doc.iterate_items():
    if it.label.value != "text" or not it.prov: continue
    pr = it.prov[0]; b = pr.bbox
    per_page[pr.page_no] += 1
    is_flat = abs(b.r - b.l) < 1 or abs(b.t - b.b) < 1
    flat += is_flat; short += len(it.text.strip()) <= 2
    if is_flat and len(junk) < 8: junk.append((pr.page_no, it.text[:40]))
print(f"text: {sum(per_page.values())} | bbox phẳng: {flat} | <=2 ký tự: {short}")
print("nhiều nhất:", per_page.most_common(8))
print("mẫu rác:", junk)

# B. Đọc thẳng trang đôi (bản gốc, trang 11–13: mục IV → VIII)
r, w = PdfReader("data/raw/products/BVP/bvp_quytac.pdf"), PdfWriter()
for i in (11, 12, 13): w.add_page(r.pages[i - 1])
test = "logs/pilot_bvp/parsed_pdfium/_orig_p11-13.pdf"; w.write(open(test, "wb"))
d2 = build_converter(num_threads=8, backend=PyPdfiumDocumentBackend).convert(test).document
print("== Trang đôi: tiêu đề theo thứ tự đọc (T=nửa trái, P=nửa phải)")
for it, _ in d2.iterate_items():
    if it.label.value == "section_header" and it.prov:
        p = it.prov[0]; side = "T" if p.bbox.l < d2.pages[p.page_no].size.width / 2 else "P"
        print(f"  {p.page_no}{side}: {it.text[:60]}")
n_text = sum(1 for it, _ in d2.iterate_items() if it.label.value == "text")
print("text items (3 trang đôi):", n_text, "| Ð:", d2.export_to_markdown().count("Ð"))
