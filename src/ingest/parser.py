import re
from copy import copy
from pypdf import PdfReader, PdfWriter
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode


def split_2up(src: str, dst: str) -> list[int]:
    """Cắt trang ngang thành 2 nửa trái/phải; trả về map trang mới -> trang gốc (1-based)."""
    r, w, page_map = PdfReader(src), PdfWriter(), []
    for i, pg in enumerate(r.pages, 1):
        x0, y0, x1, y1 = map(float, pg.mediabox)
        if (x1 - x0) <= (y1 - y0):
            w.add_page(pg); page_map.append(i); continue
        mid = (x0 + x1) / 2
        for a, b in ((x0, mid), (mid, x1)):
            half = copy(pg)
            half.mediabox.lower_left, half.mediabox.upper_right = (a, y0), (b, y1)
            half.cropbox.lower_left, half.cropbox.upper_right = (a, y0), (b, y1)
            w.add_page(half); page_map.append(i)
    with open(dst, "wb") as fh:
        w.write(fh)
    return page_map


def build_converter(ocr: dict | bool | None = None, num_threads: int = 4, backend=None) -> DocumentConverter:
    """ocr: None/False = không OCR (giữ nguyên hành vi cũ); dict = Tesseract CLI, OCR toàn trang (bỏ qua lớp chữ có sẵn).
    Khóa dict: lang (mặc định ["vie"]), scale (3.0 = 216 dpi), psm, tessdata (thư mục traineddata)."""
    try:
        from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
    except ImportError:
        from docling.datamodel.pipeline_options import AcceleratorOptions, AcceleratorDevice
    if ocr is True:
        ocr = {}
    opts = PdfPipelineOptions(do_ocr=ocr is not None and ocr is not False, do_table_structure=True)
    if opts.do_ocr:
        from docling.datamodel.pipeline_options import OcrMode, TesseractCliOcrOptions
        opts.ocr_options = TesseractCliOcrOptions(
            lang=ocr.get("lang", ["vie"]), mode=OcrMode.FULL_PAGE,     # thay force_full_page_ocr (deprecated, docling 2.142)
            scale=ocr.get("scale", 3.0), psm=ocr.get("psm"), path=ocr.get("tessdata"))
    opts.table_structure_options.mode = TableFormerMode.ACCURATE
    opts.table_structure_options.do_cell_matching = True
    opts.accelerator_options = AcceleratorOptions(num_threads=num_threads, device=AcceleratorDevice.CPU)
    fmt = PdfFormatOption(pipeline_options=opts, backend=backend) if backend else PdfFormatOption(pipeline_options=opts)
    return DocumentConverter(format_options={InputFormat.PDF: fmt})


def ocr_provenance(ocr: dict) -> dict:
    """Ghi lại engine và traineddata để tái lập (data/parsed/{P}/{stem}.ocr.json, report.json)."""
    import glob, hashlib, os, subprocess
    from pathlib import Path
    ver = subprocess.run(["tesseract", "--version"], capture_output=True, text=True)
    ver = (ver.stdout or ver.stderr).splitlines()[0].strip()
    lang = ocr.get("lang", ["vie"])
    tdir = ocr.get("tessdata")
    if not tdir:
        out = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True)
        m = re.search(r'"(.+?)/?"', (out.stdout or "") + (out.stderr or ""))   # tesseract 5 in đường dẫn
        cands = [m[1]] if m else []
        cands += [os.environ.get("TESSDATA_PREFIX", "")] + sorted(glob.glob("/usr/share/tesseract-ocr/*/tessdata"))
        tdir = next((d for d in cands if d and Path(d, f"{lang[0]}.traineddata").exists()), "")   # 4.1.1 không in
    sha = {l: hashlib.sha256(Path(tdir, f"{l}.traineddata").read_bytes()).hexdigest()[:12]
           for l in lang if Path(tdir, f"{l}.traineddata").exists()}
    return {"engine": ver, "mode": "full_page", "config": ocr, "tessdata_dir": tdir, "traineddata_sha256": sha}

LABELS_TO_CHECK = {"text", "list_item", "section_header", "caption", "page_header", "page_footer"}

def drop_offpage_items(doc, min_inside: float = 0.5) -> int:
    """Xóa item có bbox phẳng hoặc nằm phần lớn ngoài trang.
    pypdfium2 lấy cả lớp chữ ẩn/trùng của PDF Illustrator; tọa độ của chúng nằm ngoài khung trang."""
    junk = []
    for it, _ in doc.iterate_items():
        if it.label.value not in LABELS_TO_CHECK or not it.prov:
            continue
        p = it.prov[0]
        page = doc.pages.get(p.page_no)
        if page is None:
            continue
        W, H = page.size.width, page.size.height
        l, r = sorted((p.bbox.l, p.bbox.r))
        lo, hi = sorted((p.bbox.t, p.bbox.b))          # chạy đúng với cả 2 gốc tọa độ
        w, h = r - l, hi - lo
        if w < 1 or h < 1:
            junk.append(it); continue
        ix = max(0.0, min(r, W) - max(l, 0.0))
        iy = max(0.0, min(hi, H) - max(lo, 0.0))
        if (ix * iy) / (w * h) < min_inside:              # dưới 50% diện tích nằm trong trang
            junk.append(it)
    if junk:
        doc.delete_items(node_items=junk)
    return len(junk)

def parse_pdf(path: str, converter: DocumentConverter):
    doc = converter.convert(path).document
    dropped = drop_offpage_items(doc)
    return doc, [t.export_to_markdown(doc=doc) for t in doc.tables], dropped
