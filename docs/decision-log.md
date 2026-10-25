# Decision log – ĐA1

| Ngày | Quyết định | Lý do / căn cứ |
| --- | --- | --- |
| 2026-10-23 | Benchmark v1: dev 30 câu (6/nhóm), test 120 câu | Dev để tinh chỉnh ngưỡng/prompt, test chỉ để báo cáo |
| 2026-10-24 | Rút ĐA1 còn 10 tuần; MT4 (gợi ý sản phẩm) chuyển sang ĐA2 thành tool check_eligibility() | Giữ tuần 7–10 cho demo, thực nghiệm và báo cáo; pipeline B4 xong tuần 6 |
| 2026-10-24 | Chunk theo Chương/Mục/Điều/Khoản: đơn vị = Điều, tách theo Khoản nếu > 512 token; bảng = 1 chunk | Cân bằng ngữ cảnh và độ chính xác trích dẫn; kiểm chứng bằng B1 vs B2 (RQ1) |
| 2026-10-24 | Văn bản pháp luật KDBH (Luật 08/2022/QH15, Luật 139/2025/QH15, NĐ 46/2023/NĐ-CP, TT 67/2023/TT-BTC) chỉ là nguồn định nghĩa chung cho glossary; không đưa vào kho truy xuất | Tránh nhiễu truy xuất; hỏi đáp luật để sang ĐA2 |
| 2026-10-24 | Glossary 2 cấp: mỗi mục có scope (general hoặc product_code) và source; định nghĩa của sản phẩm được ưu tiên | Quy tắc từng sản phẩm có thể định nghĩa lại thuật ngữ chung |
| 2026-10-24 | Không dùng bộ vector có sẵn trên Hugging Face; lấy văn bản gốc từ nguồn chính thức | Khác model embedding với bge-m3, có thể đã cũ |
| 2026-10-24 | Tên đề tài: "Xây dựng hệ thống hỏi đáp có trích dẫn về sản phẩm bảo hiểm cá nhân dựa trên RAG" | Bao quát mọi loại tài liệu trong phạm vi, không chỉ Quy tắc |
| 2026-10-24 | Đồng bộ lộ trình với đề cương ĐA1: 10 tuần, mốc tuần 4/5/6, MT4 sang ĐA2, thêm 2 rủi ro ĐA1 | Hai tài liệu gửi giảng viên hướng dẫn phải nhất quán |
| 2026-10-24 | Chốt danh sách sản phẩm sau khi thầy xác nhận 10 tuần, MT4 sang ĐA2, dùng Gemini API soạn nháp benchmark | Tránh làm lại nếu phạm vi đổi |
| 2026-10-24 | Smoke test: WSL CPU 8 nhân, 12 GB RAM, không GPU; Qwen 7B prefill 19 / decode 4,7 tok/s; rerank 88 s/30 cặp; pin Qdrant v1.20.0 | Chạy local toàn bộ mất ~20–28 giờ/lần test, demo 3–4 phút/câu |
| 2026-10-24 | Hạ tầng GPU: Google Colab Pay As You Go; WSL để phát triển, xây kho tri thức và phân tích; Colab chạy embed, B0–B4 end-to-end và demo; code qua GitHub, artifact qua Google Drive (rclone) | Giữ Qwen2.5 7B như đề cương, chỉ đổi phần cứng; chi phí ước tính ≤ 100 compute unit cho ĐA1 |
| 2026-10-24 | Số liệu báo cáo lấy từ lần chạy trên Colab, cùng một loại GPU cho B0–B4; log ghi GPU, version Ollama, digest model; Qdrant Docker trên WSL chỉ để debug | Tái lập kết quả, độ trễ p95 đo trên một môi trường |
| 2026-10-24 | Gemini API chỉ soạn nháp benchmark và làm judge Ragas, không tham gia sinh câu trả lời | Tách hệ thống được đánh giá khỏi công cụ đánh giá |
| 2026-10-25 | Chuyển repo bv-rag sang public | Colab clone không cần token; repo chỉ chứa code, config, benchmark và kết quả, không chứa tài liệu gốc hay dữ liệu thật |
| 2026-10-25 | LLMClient: nạp Ollama trước PyTorch, num_ctx=4096, num_gpu=99, keep_alive=-1, warm-up một lượt sinh ngắn; mọi request dùng cùng load options | v1: decode 7,8 tok/s do chia layer sang CPU; v2: prefill 49 tok/s do lượt đầu gánh chi phí khởi tạo kernel |
| 2026-10-25 | Chọn GPU L4 trên Colab Pay As You Go cho mọi lần chạy chính thức B0–B4; T4 chỉ dự phòng và phải đo lại trước khi dùng | L4 v3: prefill 3.470 / decode 52,2 tok/s, 100% GPU, ~0,62 giờ/lần test (~1 unit) |
| 2026-10-25 | Hoãn 2 ghi chú cho ĐA2/ĐATN (so sánh RAG và Agentic RAG dùng cùng LLM; hợp đồng thật chỉ xử lý trên WSL), làm rõ khi bắt đầu ĐA2 | Chưa cần cho ĐA1; quyết định khi chọn LLM điều phối và hạ tầng cho dữ liệu thật |
