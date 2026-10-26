import os, torch
from docling.datamodel.settings import settings
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from src.ingest.parser import build_converter

print("nproc:", os.cpu_count(), "| torch threads:", torch.get_num_threads())
settings.debug.profile_pipeline_timings = True
warm, test = "logs/pilot_bvp/parsed/_warm.pdf", "logs/pilot_bvp/parsed/_p28-34.pdf"

for name, be in [("docling-parse (mặc định)", None), ("pypdfium2", PyPdfiumDocumentBackend)]:
    conv = build_converter(num_threads=8, backend=be)
    conv.convert(warm)
    res = conv.convert(test)
    print(f"== {name}")
    for k, v in res.timings.items():
        print(f"  {k:28s} {sum(v.times):7.1f} s  (n={len(v.times)})")
