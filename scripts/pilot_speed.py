import time
from pypdf import PdfReader, PdfWriter
from src.ingest.parser import build_converter

src = "logs/pilot_bvp/parsed/bvp_quytac_split.pdf"
r = PdfReader(src)
def sub(pages, path):
    w = PdfWriter(); [w.add_page(r.pages[i - 1]) for i in pages]; w.write(open(path, "wb")); return path
warm = sub([6], "logs/pilot_bvp/parsed/_warm.pdf")
test = sub(range(28, 35), "logs/pilot_bvp/parsed/_p28-34.pdf")
for th in (4, 8):
    conv = build_converter(num_threads=th)
    conv.convert(warm)                                   # nạp model, không tính giờ
    t0 = time.time(); conv.convert(test)
    print(f"{th} luồng: {(time.time() - t0) / 7:.1f} s/trang", flush=True)
