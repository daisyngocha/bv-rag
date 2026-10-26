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


def build_converter(ocr: bool = False, num_threads: int = 4, backend=None) -> DocumentConverter:
    try:
        from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
    except ImportError:
        from docling.datamodel.pipeline_options import AcceleratorOptions, AcceleratorDevice
    opts = PdfPipelineOptions(do_ocr=ocr, do_table_structure=True)
    opts.table_structure_options.mode = TableFormerMode.ACCURATE
    opts.table_structure_options.do_cell_matching = True
    opts.accelerator_options = AcceleratorOptions(num_threads=num_threads, device=AcceleratorDevice.CPU)
    fmt = PdfFormatOption(pipeline_options=opts, backend=backend) if backend else PdfFormatOption(pipeline_options=opts)
    return DocumentConverter(format_options={InputFormat.PDF: fmt})

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
