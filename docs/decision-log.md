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
