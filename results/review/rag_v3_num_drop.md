# Rà câu nghi lỗi (8 câu)

Kết luận mỗi câu: `ok` (lỗi hệ thống), `sửa đáp án`, `sửa evidence`, `bỏ câu`; ghi vào benchmark/CHANGELOG.md.

## v1-0032 · table · easy · cờ: -

**Câu hỏi:** Theo biểu phí bảo hiểm dành cho gia đình của Bảo hiểm Du lịch Flexi, mức phí tham gia Chương trình Vàng cho chuyến đi từ 120-126 ngày là bao nhiêu?

**Đáp án chuẩn:** Mức phí bảo hiểm dành cho gia đình tham gia Chương trình Vàng với thời hạn từ 120-126 ngày là 4.928.000.

**Evidence `FLX_BP_S2_TB2`:**

```text
[Bảo hiểm Du lịch Flexi | Biểu phí | Biểu phí bảo hiểm dành cho gia đình]
| Thời hạn bảo hiểm | Chương trình Bạc | Chương trình Vàng | Chương trình Bạch Kim | Chương trình Kim Cương |
|---|---|---|---|---|
| Từ 85-91 ngày | 2.684.000 | 3.638.000 | 5.860.000 | 8.414.000 |
| Từ 92-98 ngày | 2.874.000 | 3.896.000 | 6.260.000 | 8.988.000 |
| Từ 99-105 ngày | 3.064.000 | 4.154.000 | 6.660.000 | 9.562.000 |
| Từ 106-112 ngày | 3.254.000 | 4.412.000 | 7.060.000 | 10.136.000 |
| Từ 113-119 ngày | 3.444.000 | 4.670.000 | 7.460.000 | 10.710.000 |
| Từ 120-126 ngày | 3.634.000 | 4.928.000 | 7.860.000 | 11.284.000 |
| Từ 127-133 ngày | 3.824.000 | 5.186.000 | 8.260.000 | 11.858.000 |
| Từ 134-140 ngày | 4.014.000 | 5.444.000 | 8.660.000 | 12.432.000 |
| Từ 141-147 ngày | 4.204.000 | 5.702.000 | 9.060.000 | 13.006.000 |
| Từ 148-154 ngày | 4.394.000 | 5.960.000 | 9.460.000 | 13.580.000 |
| Từ 155-161 ngày | 4.584.000 | 6.218.000 | 9.860.000 | 14.154.000 |
| Từ 162-168 ngày | 4.774.000 | 6.476.000 | 10.260.000 | 14.728.000 |
| Từ 169-175 ngày | 4.964.000 | 6.734.000 | 10.660.000 | 15.302.000 |
| Từ 176-182 ngày | 5.154.000 | 6.992.000 | 11.060.000 | 15.876.000 |
```

**B4rr** (rank 1 · qp ['FLX']) top-5: **FLX_BP_S2_TB2**, FLX_BP_S1_TB2, FLX_BP_S2_TB1, FLX_BP_S2_TB3, FLX_BP_S2_TB4

> Theo biểu phí bảo hiểm dành cho gia đình của Bảo hiểm Du lịch Flexi, mức phí tham gia Chương trình Vàng cho chuyến đi từ 120-126 ngày là 4.928.000 đồng [FLX_BP_S2_TB1].

**B4ng** (rank 1 · qp ['FLX']) top-5: **FLX_BP_S2_TB2**, FLX_BP_S1_TB2, FLX_BP_S2_TB1, FLX_BP_S2_TB3, FLX_BP_S2_TB4

> Theo biểu phí bảo hiểm dành cho gia đình của Bảo hiểm Du lịch Flexi [3], mức phí tham gia Chương trình Vàng cho chuyến đi từ 120-126 ngày là 2.464.000 đồng.

**B4** (rank 1 · qp ['FLX']) top-5: **FLX_BP_S2_TB2**, FLX_BP_S1_TB2, FLX_BP_S2_TB1, FLX_BP_S2_TB3, FLX_BP_S2_TB4

> Theo biểu phí bảo hiểm dành cho gia đình của Bảo hiểm Du lịch Flexi [3], mức phí tham gia Chương trình Vàng cho chuyến đi từ 120-126 ngày là 2.464.000 đồng.

### Nhận xét 6 bước (HA duyệt 13/11) >> đã duyệt

1. Đáp án chuẩn khớp evidence: có, dòng "Từ 120-126 ngày", cột Vàng của `FLX_BP_S2_TB2` (gia đình) = 4.928.000.
2. Rank evidence: 1 ở cả B4rr, B4ng, B4 (cùng top-5).
3. B4ng/B4: **sai**. Trả lời 2.464.000, đúng dòng và cột nhưng lấy ở bảng cá nhân. 2.464.000 bằng đúng một nửa 4.928.000.
4. 2.464.000 chỉ có ở `FLX_BP_S1_TB2` (biểu phí cá nhân, dòng 120-126 ngày, cột Vàng), nằm ở vị trí [2] trong top-5.
5. [3] = `FLX_BP_S2_TB1` (gia đình, bảng thời hạn ngắn, không có dòng 120-126): trích dẫn sai. B4rr cũng trích `FLX_BP_S2_TB1` dù số đúng (G2 ở B4rr).
6. B4 giống hệt B4ng (ngưỡng không chặn).

Mã: **G1** (lấy số từ bảng khác: cá nhân thay vì gia đình), phụ **G2**.
Giả thuyết `<doc so="n">`: **không đủ căn cứ.** Text của chunk luôn có dòng tiêu đề "[… | Biểu phí bảo hiểm du lịch quốc tế
Flexi dành cho cá nhân]" / "[… dành cho gia đình]", ở cả hai dạng ngữ cảnh. Mã `S1`/`S2` không nói cá nhân hay gia đình, nên
khi đổi sang số thứ tự, model không mất thông tin phân biệt hai bảng. Nhiều khả năng model lẫn giữa hai bảng cùng cấu trúc
nằm cạnh nhau ([1] và [2]). Muốn kiểm chắc phải chạy lại rag_v3 với `<doc so="n" id="…">` trên dev (không chạy trên test).

## v1-0040 · scenario · medium · cờ: -

**Câu hỏi:** Bé Nam (2 tuổi) được bố mẹ mua bảo hiểm Bảo Việt An Gia có kèm quyền lợi bổ sung Điều trị ngoại trú. Trong thời hạn bảo hiểm, bé bị ốm và đi khám ngoại trú, làm xét nghiệm máu và mua thuốc theo đơn của bác sĩ. Các chi phí này có được bảo hiểm chi trả không và được chi trả như thế nào?

**Đáp án chuẩn:** Bé Nam được thanh toán chi phí khám, xét nghiệm và thuốc theo kê đơn của bác sĩ căn cứ trên chi phí y tế thực tế phát sinh (trừ các điểm loại trừ). Tuy nhiên, do bé thuộc độ tuổi từ 15 ngày tuổi đến 3 tuổi, quyền lợi ngoại trú này sẽ áp dụng theo tỉ lệ đồng chi trả được quy định trong bảng quyền lợi bảo hiểm.

**Evidence `BVP_QT_C2_M2_B1_A`:**

```text
[Bảo Việt An Gia | Quy tắc | QUYỀN LỢI BỔ SUNG 1: ĐIỀU TRỊ NGOẠI TRÚ DO BỆNH, TAI NẠN, BIẾN CHỨNG THAI SẢN > A. Quyền lợi bảo hiểm]
Bảo hiểm Bảo Việt sẽ thanh toán cho Người được bảo hiểm tham gia quyền lợi bảo hiểm bổ sung này các chi phí y tế thực tế khi điều trị ngoại trú do bệnh, tai nạn, biến chứng thai sản trong thời hạn bảo hiểm, trừ những điểm loại trừ quy định tại hợp đồng bảo hiểm/quy tắc bảo hiểm:
- Chi phí khám, điều trị, các xét nghiệm, chẩn đoán hình ảnh, truyền dịch, thủ thuật thăm dò, vật tư y tế tiêu hao thông thường theo chỉ định của bác sĩ.
- Chi phí thuốc theo kê đơn của bác sĩ.
- Chi phí phẫu thuật trong ngày, phẫu thuật ngoại trú.
- Nội soi/thủ thuật (bao gồm điều trị trong ngày hoặc ngoại trú).
- Vật lý trị liệu, trị liệu học bức xạ, liệu pháp ánh sáng do bác sĩ chỉ định. Giới hạn trách nhiệm theo các quyền lợi được quy định cụ thể trong bảng quyền lợi đính kèm hợp đồng bảo hiểm.
Đối tượng trẻ em từ 15 ngày tuổi đến 3 tuổi, quyền lợi này áp dụng theo tỉ lệ đồng chi trả được quy định trong bảng quyền lợi bảo hiểm.
```

**B4rr** (rank 1 · qp ['BVP']) top-5: **BVP_QT_C2_M2_B1_A**, BVP_QT_C2_M1_A_K2-4, BVP_QT_C4_M2_K2, BVP_QT_C2_M1_A_K5-8, BVP_QT_C1_M3

> Các chi phí khám, xét nghiệm và thuốc theo đơn của bác sĩ cho bé Nam (2 tuổi) có được bảo hiểm chi trả, vì quyền lợi Điều trị ngoại trú áp dụng cho đối tượng từ 15 ngày tuổi đến 3 tuổi theo tỉ lệ đồng chi trả được quy định trong bảng quyền lợi bảo hiểm [BVP_QT_C2_M2_B1_A].

**B4ng** (rank 1 · qp ['BVP']) top-5: **BVP_QT_C2_M2_B1_A**, BVP_QT_C2_M1_A_K2-4, BVP_QT_C4_M2_K2, BVP_QT_C2_M1_A_K5-8, BVP_QT_C1_M3

> Các chi phí khám, xét nghiệm và thuốc cho bé Nam (2 tuổi) có được bảo hiểm chi trả, nhưng được chi trả theo tỷ lệ đồng chi trả được quy định trong bảng quyền lợi bảo hiểm [1].
> 
> Tài liệu sản phẩm hiện có không có thông tin về mức tỷ lệ đồng chi trả cụ thể.

**B4** (rank 1 · qp ['BVP']) top-5: **BVP_QT_C2_M2_B1_A**, BVP_QT_C2_M1_A_K2-4, BVP_QT_C4_M2_K2, BVP_QT_C2_M1_A_K5-8, BVP_QT_C1_M3

> Các chi phí khám, xét nghiệm và thuốc cho bé Nam (2 tuổi) có được bảo hiểm chi trả, nhưng được chi trả theo tỷ lệ đồng chi trả.
> 
> Theo tài liệu [1], quyền lợi bảo hiểm bổ sung Điều trị ngoại trú áp dụng cho đối tượng trẻ em từ 15 ngày tuổi đến 3 tuổi theo tỷ lệ đồng chi trả được quy định trong bảng quyền lợi bảo hiểm. Trong trường hợp bé Nam (2 tuổi) đi khám ngoại trú, làm xét nghiệm máu và mua thuốc theo đơn của bác sĩ, các chi phí này thuộc phạm vi bảo hiểm và sẽ được thanh toán theo tỷ lệ đồng chi trả được quy định trong bảng quyền lợi bảo hiểm.
> 
> Tài liệu sản phẩm hiện có không có thông tin để xác định tỷ lệ đồng chi trả cụ thể, nhưng theo quy định, các chi phí này sẽ được chi trả theo tỷ lệ đồng chi trả được quy định trong bảng quyền lợi bảo hiểm.


### Nhận xét 6 bước (HA duyệt 13/11) >> đã duyệt

1. Đáp án chuẩn khớp evidence: có (chi phí khám, xét nghiệm, thuốc; trẻ 15 ngày tuổi – 3 tuổi áp dụng đồng chi trả).
2. Rank evidence: 1 ở cả ba cấu hình.
3. B4ng: **thiếu**, không nhắc lại khoảng tuổi "15 ngày tuổi đến 3 tuổi". Nội dung đúng: được chi trả theo tỷ lệ đồng chi
   trả; câu "không có thông tin về tỷ lệ cụ thể" cũng đúng, vì bảng quyền lợi không có trong top-5. Không có số sai.
4. Không có số sai.
5. [1] = `BVP_QT_C2_M2_B1_A` = evidence: đúng.
6. B4 khác B4ng: B4 nêu lại khoảng tuổi (khớp số 1,0) và cùng kết luận.

Mã: **không lỗi.** Rơi số do metric: câu trả lời không lặp lại điều kiện tuổi (tuổi bé Nam đã cho trong câu hỏi). Phụ: thiếu chi tiết căn cứ.

## v1-0045 · scenario · easy · cờ: -

**Câu hỏi:** Anh Nam (32 tuổi) tham gia bảo hiểm Bảo Việt An Gia có thời hạn 1 năm. Sau 6 tháng hiệu lực và chưa từng có yêu cầu bồi thường nào được chấp thuận chi trả, anh gửi thông báo bằng văn bản trước 30 ngày yêu cầu đơn phương chấm dứt hợp đồng. Trường hợp này anh Nam có được hoàn phí bảo hiểm không và mức hoàn trả như thế nào?

**Đáp án chuẩn:** Anh Nam được hoàn trả 70% phí bảo hiểm của thời gian còn lại. Lý do là anh đã thông báo bằng văn bản trước 30 ngày và trong thời gian hiệu lực của hợp đồng chưa có yêu cầu trả tiền bảo hiểm nào được Bảo hiểm Bảo Việt chấp nhận chi trả.

**Evidence `BVP_QT_C1_M4_K3-5`:**

```text
[Bảo Việt An Gia | Quy tắc | CHƯƠNG I - Quy Định Chung > IV. Ký kết, chấm dứt hợp đồng bảo hiểm và tái tục hợp đồng bảo hiểm]
3. Trên cơ sở giấy yêu cầu bảo hiểm, Bảo hiểm Bảo Việt sẽ cấp hợp đồng bảo hiểm cho Người được bảo hiểm.
4. Chấm dứt hợp đồng bảo hiểm:
a. Trường hợp một trong hai bên muốn đơn phương chấm dứt hợp đồng bảo hiểm phải thông báo bằng văn bản cho bên kia biết trước 30 ngày kể từ ngày định đơn phương chấm dứt:
- Nếu Bên mua bảo hiểm/Người được bảo hiểm yêu cầu đơn phương chấm dứt hợp đồng, Bảo hiểm Bảo Việt sẽ hoàn trả 70% phí bảo hiểm của thời gian còn lại với điều kiện trong thời gian hiệu lực của hợp đồng bảo hiểm chưa có yêu cầu trả tiền bảo hiểm nào được Bảo hiểm Bảo Việt chấp nhận chi trả.
- Nếu Bảo hiểm Bảo Việt yêu cầu đơn phương chấm dứt hợp đồng, Bảo hiểm Bảo Việt sẽ hoàn trả toàn bộ phí bảo hiểm của thời gian còn lại cho dù có yêu cầu trả tiền bảo hiểm nào hay chưa.
b. Nếu Người được bảo hiểm tham gia không đúng đối tượng và điều kiện tham gia bảo hiểm, và/hoặc Bên mua bảo hiểm, Người được bảo hiểm hoặc đại diện Người được bảo hiểm cung cấp không đầy đủ thông tin, hoặc cung cấp thông tin không trung thực nhằm giao kết hợp đồng bảo hiểm để được trả tiền bảo hiểm thì Bảo hiểm Bảo Việt có quyền hủy bỏ hợp đồng bảo hiểm và từ chối chi trả quyền lợi bảo hiểm. Bảo hiểm Bảo Việt hoàn lại 70% phí bảo hiểm của thời gian hiệu lực còn lại với điều kiện chưa có yêu cầu trả tiền bảo hiểm nào được Bảo hiểm Bảo Việt chấp nhận chi trả trước đó. Phí bảo hiểm của thời gian hiệu lực còn lại được tính theo tỉ lệ giữa số ngày còn lại của hợp đồng và tổng số ngày của hợp đồng.
5. Cuối thời hạn bảo hiểm, căn cứ lịch sử bồi thường, tình trạng sức khỏe của Người được bảo hiểm, Bảo hiểm Bảo Việt có quyền từ chối tái tục hợp đồng hoặc đồng ý tái tục với điều kiện điều chỉnh các điều kiện, giới hạn phụ các quyền lợi bảo hiểm trong Hợp đồng bảo hiểm và/hoặc phí bảo hiểm.
```

**B4rr** (rank 1 · qp ['BVP']) top-5: **BVP_QT_C1_M4_K3-5**, BVP_QT_C1_M4_K1-2, BVP_QT_C4_M2_K1, BVP_QT_C1_M6, BVP_QT_C1_M8_K1

> Theo quy định trong tài liệu, trường hợp Bên mua bảo hiểm/Người được bảo hiểm (trong trường hợp này là anh Nam) yêu cầu đơn phương chấm dứt hợp đồng bảo hiểm, Bảo hiểm Bảo Việt sẽ hoàn trả 70% phí bảo hiểm của thời gian còn lại với điều kiện trong thời gian hiệu lực của hợp đồng bảo hiểm chưa có yêu cầu trả tiền bảo hiểm nào được Bảo hiểm Bảo Việt chấp nhận chi trả.
> 
> Vì anh Nam đã gửi thông báo trước 30 ngày và chưa có yêu cầu bồi thường nào được chấp thuận, anh Nam sẽ được hoàn trả 70% phí bảo hiểm còn lại của thời gian 6 tháng còn hiệu lực của hợp đồng bảo hiểm.
> 
> [SPMAU_QT_C1_M4_K3-5]

**B4ng** (rank 1 · qp ['BVP']) top-5: **BVP_QT_C1_M4_K3-5**, BVP_QT_C1_M4_K1-2, BVP_QT_C4_M2_K1, BVP_QT_C1_M6, BVP_QT_C1_M8_K1

> [4][3]
> 
> Anh Nam có được hoàn phí bảo hiểm với mức 70% phí bảo hiểm của thời gian còn lại. Theo quy định tại [3]a, nếu Bên mua bảo hiểm/Người được bảo hiểm yêu cầu đơn phương chấm dứt hợp đồng, Bảo hiểm Bảo Việt sẽ hoàn trả 70% phí bảo hiểm của thời gian còn lại với điều kiện trong thời gian hiệu lực của hợp đồng bảo hiểm chưa có yêu cầu trả tiền bảo hiểm nào được Bảo hiểm Bảo Việt chấp nhận chi trả.

**B4** (rank 1 · qp ['BVP']) top-5: **BVP_QT_C1_M4_K3-5**, BVP_QT_C1_M4_K1-2, BVP_QT_C4_M2_K1, BVP_QT_C1_M6, BVP_QT_C1_M8_K1

> [4][3]
> 
> Anh Nam có được hoàn phí bảo hiểm với mức 70% phí bảo hiểm của thời gian còn lại. Theo quy định tại [3]a, nếu Bên mua bảo hiểm/Người được bảo hiểm yêu cầu đơn phương chấm dứt hợp đồng, Bảo hiểm Bảo Việt sẽ hoàn trả 70% phí bảo hiểm của thời gian còn lại với điều kiện trong thời gian hiệu lực của hợp đồng bảo hiểm chưa có yêu cầu trả tiền bảo hiểm nào được Bảo hiểm Bảo Việt chấp nhận chi trả.

### Nhận xét 6 bước (HA duyệt 13/11) >> đã duyệt

1. Đáp án chuẩn khớp evidence: có (70% phí thời gian còn lại; thông báo trước 30 ngày; chưa có yêu cầu bồi thường được chấp nhận).
2. Rank evidence: 1 ở cả ba cấu hình.
3. B4ng/B4: **thiếu** "30 ngày" (điều kiện đã cho trong câu hỏi). Số 70% đúng. Không có số sai.
4. Không có số sai; "3", "4" là số trong "[4][3]", "[3]a".
5. Câu trả lời mở đầu bằng "[4][3]" và viết "theo quy định tại [3]a". [3] = `BVP_QT_C4_M2_K1` (thủ tục bồi thường), [4] =
   `BVP_QT_C1_M6` (phí bảo hiểm): **trích dẫn sai**, evidence ở [1]. Nghi model nhầm [n] với số điều khoản trong chunk
   (evidence có các mục "3.", "4. … a."). B4rr cũng trích sai (mã bịa `SPMAU_QT_C1_M4_K3`).
6. B4 giống hệt B4ng.

Mã: **G2** (nội dung đúng, trích dẫn sai). Rơi số chỉ vì không nhắc lại 30 ngày.

## v1-0107 · scenario · hard · cờ: -

**Câu hỏi:** Chị Lan tham gia Bảo hiểm 37 bệnh hiểm nghèo (CI37). Sau một cú sốc tâm lý nặng nề, chị bị mất hoàn toàn khả năng nói liên tục suốt 14 tháng và được chuyên gia Tai, Mũi, Họng (ENT) kết luận không thể phục hồi khả năng phát âm do ức chế thần kinh. Trường hợp này của chị Lan có được CI37 chi trả quyền lợi Mất khả năng phát âm không?

**Đáp án chuẩn:** Chị Lan không được chi trả quyền lợi Mất khả năng phát âm của CI37. Mặc dù tình trạng mất phát âm đã kéo dài liên tục trên 12 tháng và có xác nhận của chuyên gia Tai, Mũi, Họng (ENT), nhưng nguyên nhân xuất phát từ cú sốc tâm lý nên thuộc trường hợp loại trừ do tất cả các nguyên nhân liên quan đến tâm thần đều bị loại trừ.

**Evidence `C37_QT_C2_M12`:**

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > 12. Mất khả năng phát âm]
Mất hoàn toàn và không thể phục hồi khả năng phát âm do chấn thương hoặc bệnh tật đối với dây thanh âm. Tình trạng này phải kéo dài liên tục trong thời gian 12 tháng, phải có chứng từ y tế có kết luận bệnh của chuyên gia Tai, Mũi, Họng (ENT). Tất cả các nguyên nhân liên quan đến tâm thần bị loại trừ.
```

**B4rr** (rank 1 · qp ['C37']) top-5: **C37_QT_C2_M12**, C37_QT_C2_M30, C37_BQL_S2_P2, C37_QT_C1_M22, C37_QT_C2

> Có, trường hợp của chị Lan có được Bảo hiểm 37 bệnh hiểm nghèo (CI37) chi trả quyền lợi Mất khả năng phát âm [SPMAU_QT_C2_M12]. Theo tài liệu, mất hoàn toàn và không thể phục hồi khả năng phát âm do chấn thương hoặc bệnh tật, kéo dài liên tục trong thời gian 12 tháng, phải có chứng từ y tế của chuyên gia Tai, Mũi, Họng (ENT) sẽ được chi trả. Trong trường hợp của chị Lan, chị đã mất khả năng phát âm trong 14 tháng và có chứng từ y tế, thoả mãn điều kiện chi trả quyền lợi này.

**B4ng** (rank 1 · qp ['C37']) top-5: **C37_QT_C2_M12**, C37_QT_C2_M30, C37_BQL_S2_P2, C37_QT_C1_M22, C37_QT_C2

> Có được chi trả [1][2]. Theo tài liệu, chị Lan bị mất hoàn toàn khả năng phát âm do chấn thương tâm thần kéo dài 14 tháng, và có chứng từ y tế từ chuyên gia Tai, Mũi, Họng (ENT) xác nhận không thể phục hồi khả năng phát âm. Đây là trường hợp được bảo hiểm, vì điều kiện này nằm trong danh mục quyền lợi bảo hiểm của Bảo hiểm 37 bệnh hiểm nghèo (CI37) [1][2].

**B4** (rank 1 · qp ['C37']) top-5: **C37_QT_C2_M12**, C37_QT_C2_M30, C37_BQL_S2_P2, C37_QT_C1_M22, C37_QT_C2

> Có, trường hợp của chị Lan được chi trả quyền lợi Mất khả năng phát âm theo Bảo hiểm 37 bệnh hiểm nghèo (CI37) [1]. Theo quy định, mất hoàn toàn và không thể phục hồi khả năng phát âm do chấn thương hoặc bệnh tật, tình trạng này phải kéo dài liên tục trong thời gian 12 tháng và phải có chứng từ y tế có kết luận bệnh của chuyên gia Tai, Mũi, Họng (ENT). Trong trường hợp của chị Lan, chị bị mất khả năng phát âm liên tục trong 14 tháng và có chứng từ y tế từ chuyên gia ENT, do đó thỏa mãn điều kiện chi trả quyền lợi này.

### Nhận xét 6 bước (HA duyệt 13/11) >> đã duyệt

1. Đáp án chuẩn khớp evidence: có (mọi nguyên nhân liên quan đến tâm thần bị loại trừ → không được chi trả).
2. Rank evidence: 1 ở cả ba cấu hình.
3. B4ng: **sai kết luận**, trả lời "có được chi trả" dù chính câu trả lời ghi "do chấn thương tâm thần". Thiếu "12 tháng"
   (14 tháng lấy từ câu hỏi). B4rr và B4 cũng kết luận "được chi trả", tức sai ở cả ba cấu hình.
4. Không có số sai; 14 từ câu hỏi, "1", "2" là số trong [1][2].
5. [1] = `C37_QT_C2_M12` (evidence, đúng); [2] = `C37_QT_C2_M30` (Tê liệt, không liên quan): một trích dẫn sai.
6. B4 khác B4ng về câu chữ (có nêu 12 tháng, chỉ trích [1]) nhưng cùng kết luận sai. HA đã chốt B4 = G1 trong manual30 (giữ nguyên).

Mã: **G1** (bỏ qua điều khoản loại trừ trong evidence, sai kết luận), phụ **G2** ([2]). Lỗi không do rag_v3: B4rr cũng sai;
rơi số chỉ là triệu chứng phụ.

## v1-0115 · scenario · hard · cờ: -

**Câu hỏi:** Ông K tham gia Bảo hiểm 37 bệnh hiểm nghèo (CI37). Sau đó, ông được chuyên gia thần kinh chẩn đoán mắc hội chứng Parkinson với tình trạng suy yếu tiến triển và không kiểm soát được bằng thuốc. Suốt 8 tháng liên tục, ông không thể tự thực hiện 3 hoạt động sinh hoạt hàng ngày gồm tắm rửa, mặc quần áo và ăn uống. Tuy nhiên, hồ sơ y tế xác định tình trạng này là hậu quả của việc dùng thuốc điều trị kéo dài. Trường hợp của ông K có được chi trả quyền lợi bệnh Parkinson theo hợp đồng bảo hiểm CI37 không?

**Đáp án chuẩn:** Ông K không được chi trả quyền lợi bảo hiểm. Theo quy tắc của CI37, bảo hiểm chỉ chấp thuận chi trả cho bệnh Parkinson vô căn (tự phát) và loại trừ trường hợp hội chứng liệt rung Parkinson là hậu quả của việc dùng thuốc, nhiễm độc hay do bất kể nguyên nhân nào khác.

**Evidence `C37_QT_C2_M17`:**

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > 17. Bệnh Parkinson]
Kết luận bệnh Parkinson vô căn (tự phát) phải do chuyên gia về thần kinh thực hiện và đảm bảo đủ các điều kiện sau:
• Bệnh không thể được kiểm soát bằng thuốc;
• Tình trạng suy yếu tiến triển;
• NĐBH không có khả năng thực hiện (dù được hỗ trợ hoặc không) ít nhất ít nhất 3 trong số 6 "Hoạt động sinh hoạt hàng ngày" sau đây trong thời gian liên tục ít nhất 6 tháng: Các hoạt động sinh hoạt hàng ngày bao gồm:
i. Tắm rửa – khả năng tắm bằng bồn hoặc vòi hoa sen (bao gồm cả khả năng vào và ra khỏi bồn tắm hoặc phòng tắm) hoặc tắm rửa bằng các hình thức khác;
ii. Mặc quần áo - khả năng mặc, cởi, thắt chặt và nới lỏng đối với trang phục, và trong một số tình huống thích hợp, đối với dụng cụ niềng răng, chân/tay giả hoặc các dụng cụ phẫu thuật khác;
iii. Di chuyển - khả năng chuyển từ giường sang ghế thẳng hoặc xe lăn và ngược lại;
iv. Di động - khả năng di chuyển trong nhà từ phòng này sang phòng khác trên bề mặt bằng phẳng;
v. Vệ sinh - khả năng sử dụng nhà vệ sinh hoặc kiểm soát các chức năng ruột và bàng quang để duy trì việc vệ sinh cá nhân hợp lý ở mức độ thỏa đáng;
vi. Ăn - khả năng tự ăn khi thức ăn đã được chuẩn bị và sẵn có. Hội chứng liệt rung Parkinson là hậu quả của việc dùng thuốc hoặc nhiễm độc hay do bất kể nguyên nhân nào khác đều bị loại trừ. Theo quy tắc bảo hiểm này, “được hỗ trợ” có nghĩa là dùng các thiết bị hoặc dụng cụ đặc biệt để hỗ trợ các hoạt động mà không phải sự trợ giúp của con người.
```

**B4rr** (rank 1 · qp ['C37']) top-5: **C37_QT_C2_M17**, C37_BQL_S2_P2, C37_QT_C2_M33, C37_QT_C2_M37, C37_QT_C2_M16

> Tài liệu sản phẩm hiện có không có thông tin để trả lời câu hỏi này.
> 
> Theo tài liệu, hội chứng Parkinson do tự phát mới được xem xét để chi trả quyền lợi, trong khi hội chứng Parkinson do dùng thuốc hoặc nhiễm độc không được bao phủ. Trong trường hợp của ông K, tình trạng của ông được xác định là hậu quả của việc dùng thuốc điều trị kéo dài, do đó không đáp ứng điều kiện để được chi trả quyền lợi bệnh Parkinson theo hợp đồng bảo hiểm CI37.

**B4ng** (rank 1 · qp ['C37']) top-5: **C37_QT_C2_M17**, C37_BQL_S2_P2, C37_QT_C2_M33, C37_QT_C2_M37, C37_QT_C2_M16

> Không được chi trả, vì theo quy tắc bảo hiểm này, hội chứng Parkinson là hậu quả của việc dùng thuốc hoặc nhiễm độc hay do bất kể nguyên nhân nào khác đều bị loại trừ [1].

**B4** (rank 1 · qp ['C37']) top-5: **C37_QT_C2_M17**, C37_BQL_S2_P2, C37_QT_C2_M33, C37_QT_C2_M37, C37_QT_C2_M16

> Không được chi trả, vì theo quy tắc bảo hiểm này, hội chứng Parkinson là hậu quả của việc dùng thuốc hoặc nhiễm độc hay do bất kể nguyên nhân nào khác đều bị loại trừ [1].

### Nhận xét 6 bước (HA duyệt 13/11) >> đã duyệt

1. Đáp án chuẩn khớp evidence: có (Parkinson do dùng thuốc bị loại trừ). Số duy nhất trong đáp án chuẩn là "37" trong tên CI37.
2. Rank evidence: 1 ở cả ba cấu hình.
3. B4ng/B4: **đúng**, "Không được chi trả… hậu quả của việc dùng thuốc… đều bị loại trừ [1]". Chỉ không nhắc tên "CI37".
4. Không có số sai ("1" là [1]).
5. [1] = `C37_QT_C2_M17` = evidence: đúng.
6. B4 giống hệt B4ng.

Mã: **không lỗi.** Rơi số do metric (số "37" thuộc tên sản phẩm). Ngược lại, B4rr bị log là từ chối (`refused=True`):
mở đầu bằng câu từ chối rồi mới giải thích, nên ở câu này rag_v3 tốt hơn rag_v1.

## v1-0120 · compare · medium · cờ: -

**Câu hỏi:** Hai sản phẩm Bảo Việt Tâm Bình và Bảo Việt Intercare được phân chia thành những chương trình bảo hiểm nào theo các đoạn trích trên?

**Đáp án chuẩn:** Cả hai sản phẩm đều có 5 chương trình bảo hiểm nhưng tên gọi hoàn toàn khác nhau: Bảo Việt Tâm Bình gồm các chương trình Cơ bản, Mở rộng, Nâng cao, Toàn diện, Ưu việt; trong khi Bảo Việt Intercare gồm các chương trình Select, Essential, Classic, Gold, Diamond.

**Evidence `BTB_BQL_S2_P1`:**

```text
[Bảo Việt Tâm Bình | Bảng quyền lợi | BẢO VIỆT TÂM BÌNH]
(Ban hành theo Quyết định số 6038/QĐ-BHBV ngày 27 tháng 06 năm 2025 của Tổng Giám đốc Tổng công ty Bảo hiểm Bảo Việt)
Đơn vị: Việt Nam Đồng
| CHƯƠNG TRÌNH BẢO HIỂM | CƠ BẢN | MỞ RỘNG | NÂNG CAO | TOÀN DIỆN | ƯU VIỆT |
|---|---|---|---|---|---|
| QUYỀN LỢI BẢO HIỂM CHÍNH – ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, THAI SẢN (QLBH C) |  |  |  |  |  |
| SỐ TIỀN BẢO HIỂM/NGƯỜI/NĂM | 60.000.000 | 100.000.000 | 160.000.000 | 220.000.000 | 330.000.000 |
```

**Evidence `ITC_BQL_S1_TB1`:**

```text
[Bảo Việt Intercare | Bảng quyền lợi | BẢNG QUYỀN LỢI BẢO HIỂM BẢO VIỆT INTERCARE]
Đơn vị: đồng
| QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN |
|---|---|---|---|---|---|
| CHƯƠNG TRÌNH | SELECT | ESSENTIAL | CLASSIC | GOLD | DIAMOND |
| Phạm vi lãnh thổ | Vùng 1 | Vùng 2 | Vùng 3 | Vùng 4 | Vùng 5 |
| Số tiền bảo hiểm (STBH) cho một thời hạn bảo hiểm và theo các giới hạn phụ dưới đây | 1.050.000.000 | 2.100.000.000 | 4.200.000.000 | 5.250.000.000 | 10.500.000.000 |
```

**B4rr** (rank 2 · qp ['BTB', 'ITC']) top-5: BTB_BQL_S2_TB8, **ITC_BQL_S1_TB1**, BTB_BQL_S2_TB3, ITC_BP_S6, BTB_BQL_S2_TB2

> Sản phẩm Bảo Việt Tâm Bình được phân chia thành 5 chương trình bảo hiểm: Cơ bản, Mở rộng, Nâng cao, Toàn diện và Ưu việt, như được mô tả trong các đoạn tài liệu [SPMAU_QT_C1_M2_K1] và [SPMAU_QT_C1_M2_K2]. 
> 
> Sản phẩm Bảo Việt Intercare được phân chia thành 5 chương trình bảo hiểm: Select, Essential, Classic, Gold và Diamond, như được mô tả trong đoạn tài liệu [ITC_BQL_S1_TB1].

**B4ng** (rank 2 · qp ['BTB', 'ITC']) top-5: BTB_BQL_S2_TB8, **ITC_BQL_S1_TB1**, BTB_BQL_S2_TB3, ITC_BP_S6, BTB_BQL_S2_TB2

> Bảo Việt Tâm Bình được phân chia thành các chương trình bảo hiểm: Cơ bản, Mở rộng, Nâng cao, Toàn diện và Ưu việt [1][3].
> 
> Bảo Việt Intercare được phân chia thành các chương trình bảo hiểm: Select, Essential, Classic, Gold và Diamond [2][4].

**B4** (rank 2 · qp ['BTB', 'ITC']) top-5: BTB_BQL_S2_TB8, **ITC_BQL_S1_TB1**, BTB_BQL_S2_TB3, ITC_BP_S6, BTB_BQL_S2_TB2

> Tài liệu sản phẩm hiện có không có thông tin để trả lời câu hỏi này.

### Nhận xét 6 bước (HA duyệt 13/11) >> đã duyệt

1. Đáp án chuẩn khớp evidence: có; số "5" là số chương trình mỗi sản phẩm.
2. Rank evidence: `ITC_BQL_S1_TB1` hạng 2 ở cả ba cấu hình; `BTB_BQL_S2_P1` không có trong top-5. Tên 5 chương trình BTB vẫn
   có trong dòng tiêu đề của `BTB_BQL_S2_TB8` và `BTB_BQL_S2_TB3`.
3. B4ng: **đúng, khác định dạng**: liệt kê đủ 5 tên chương trình mỗi sản phẩm nhưng không ghi chữ số "5".
4. Không có số sai (1–4 là [n]).
5. [1] = `BTB_BQL_S2_TB8`, [3] = `BTB_BQL_S2_TB3` (có dòng tên chương trình BTB); [2] = `ITC_BQL_S1_TB1`, [4] = `ITC_BP_S6`
   (có dòng Select…Diamond): cả bốn trích dẫn đều có tên chương trình.
6. B4 khác: bị ngưỡng 0,90 chặn (`gated=True`) nên từ chối. Đây là F1 do ngưỡng, thuộc 4 câu compare bị chặn ở mục 1.

Mã: B4ng **không lỗi** (khớp nhãn HA đã chốt trong manual30: correct 5, faithful 5). B4: **F1** (ngưỡng). Rơi số do metric.

## v1-0133 · compare · hard · cờ: -

**Câu hỏi:** Trong hợp đồng bảo hiểm tổ chức, độ tuổi tối đa được tham gia tái tục của bố/mẹ đẻ hoặc bố/mẹ vợ/chồng của nhân viên khác nhau như thế nào giữa Bảo Việt Tâm Bình và Bảo Việt Intercare?

**Đáp án chuẩn:** Đối với hợp đồng tổ chức, cả hai sản phẩm đều áp dụng độ tuổi dưới 66 tuổi khi tham gia thông thường, nhưng khi tham gia tái tục (trừ khi có thỏa thuận khác), Bảo Việt Tâm Bình giới hạn độ tuổi đến 70 tuổi, trong khi Bảo Việt Intercare cho phép độ tuổi lên đến 75 tuổi.

**Evidence `BTB_QT_C1_M35`:**

```text
[Bảo Việt Tâm Bình | Quy tắc | CHƯƠNG I: ĐỊNH NGHĨA > 35. Người phụ thuộc (người thân)]
Đối với hợp đồng bảo hiểm cá nhân: Người phụ thuộc là con hợp pháp của Bên mua bảo hiểm/Người được bảo hiểm có độ tuổi từ 15 ngày tuổi đến 18 tuổi, hoặc đến 24 tuổi nếu đang theo học các khóa học dài hạn tại Việt Nam và chưa kết hôn, kề từ ngày có hiệu lực bảo hiểm hoặc ngày tái tục bảo hiểm hàng năm tiếp theo. Tất cả người phụ thuộc phải có tên trong danh sách yêu cầu được bảo hiểm.
Đối với hợp đồng bảo hiểm tổ chức: Người phụ thuộc là vợ/chồng, bó/mẹ đẻ, bố mẹ vợ/chồng dưới 66 tuổi (đến 70 tuổi nều tham gia tái tục trừ khi có thỏa thuận khác) của nhân viên được bảo hiểm, là con hợp pháp của nhân viên được bảo hiểm có độ tuổi từ 15 ngày tuổi đến 18 tuổi, hoặc đến 24 tuổi nếu đang theo học các khóa học dài hạn tại Việt Nam và chưa kết hôn, kể từ ngày có hiệu lực bảo hiểm hoặc ngày tái tục bảo hiểm hàng năm tiếp theo. Tất cả người phụ thuộc phải có tên trong danh sách Người được bảo hiểm.
```

**Evidence `ITC_QT_C1_M41`:**

```text
[Bảo Việt Intercare | Quy tắc | PHẦN I - ĐỊNH NGHĨA > 41. Người phụ thuộc (người thân)]
Đối với hợp đồng bảo hiểm cá nhân: Người phụ thuộc là con hợp pháp của Bên mua bảo hiểm/Người được bảo hiểm có độ tuổi từ 15 ngày tuổi đến 18
tuổi, hoặc đến 24 tuổi nếu đang theo học các khóa học dài hạn tại Việt Nam và chưa kết hôn, kể từ ngày có hiệu lực bảo hiểm hoặc ngày tái tục bảo hiểm hàng năm tiếp theo. Tất cả người phụ thuộc phải có tên trong danh sách yêu cầu được bảo hiểm.
Đối với hợp đồng bảo hiểm tổ chức: Người phụ thuộc là vợ/chồng, bố/mẹ đẻ, bố mẹ vợ/chồng dưới 66 tuổi (đến 75 tuổi nếu tham gia tái tục trừ khi có thỏa thuận khác) của nhân viên được bảo hiểm, là con hợp pháp của nhân viên được bảo hiểm có độ tuổi từ 15 ngày tuổi đến 18 tuổi, hoặc đến 24 tuổi nếu đang theo học các khóa học dài hạn tại Việt Nam và chưa kết hôn, kể từ ngày có hiệu lực bảo hiểm hoặc ngày tái tục bảo hiểm hàng năm tiếp theo. Tất cả người phụ thuộc phải có tên trong danh sách Người được bảo hiểm.
```

**B4rr** (rank 1 · qp ['BTB', 'ITC']) top-5: **BTB_QT_C1_M35**, **ITC_QT_C1_M41**, BTB_QT_C4_M2_K3_P1, ITC_QT_C4_M1_P1, BTB_QT_C4_M2_K1-2

> Trong hợp đồng bảo hiểm tổ chức:
> 
> - Bảo Việt Tâm Bình: Độ tuổi tối đa được tham gia tái tục là 66 tuổi (đến 70 tuổi nếu tham gia tái tục trừ khi có thỏa thuận khác) [BTB_QT_C1_M35].
> 
> - Bảo Việt Intercare: Độ tuổi tối đa được tham gia tái tục là 75 tuổi [ITC_QT_C1_M41].
> 
> Vì vậy, độ tuổi tối đa được tham gia tái tục của bố/mẹ đẻ hoặc bố/mẹ vợ/chồng của nhân viên trong Bảo Việt Intercare cao hơn so với Bảo Việt Tâm Bình.

**B4ng** (rank 1 · qp ['BTB', 'ITC']) top-5: **BTB_QT_C1_M35**, **ITC_QT_C1_M41**, BTB_QT_C4_M2_K3_P1, ITC_QT_C4_M1_P1, BTB_QT_C4_M2_K1-2

> [2] Độ tuổi tối đa được tham gia tái tục của bố/mẹ đẻ hoặc bố/mẹ vợ/chồng của nhân viên đối với Bảo Việt Intercare là 75 tuổi.
> 
> [1] Đối với Bảo Việt Tâm Bình, không có thông tin về độ tuổi tối đa được tham gia tái tục của bố/mẹ đẻ hoặc bố/mẹ vợ/chồng của nhân viên.

**B4** (rank 1 · qp ['BTB', 'ITC']) top-5: **BTB_QT_C1_M35**, **ITC_QT_C1_M41**, BTB_QT_C4_M2_K3_P1, ITC_QT_C4_M1_P1, BTB_QT_C4_M2_K1-2

> [2] Độ tuổi tối đa được tham gia tái tục của bố/mẹ đẻ hoặc bố/mẹ vợ/chồng của nhân viên đối với Bảo Việt Intercare là 75 tuổi.
> 
> [1] Đối với Bảo Việt Tâm Bình, không có thông tin về độ tuổi tối đa được tham gia tái tục của bố/mẹ đẻ hoặc bố/mẹ vợ/chồng của nhân viên.

### Nhận xét 6 bước (HA duyệt 13/11) >> đã duyệt

1. Đáp án chuẩn khớp evidence: có (cả hai dưới 66 tuổi; tái tục BTB đến 70, ITC đến 75).
2. Rank evidence: `BTB_QT_C1_M35` hạng 1, `ITC_QT_C1_M41` hạng 2, ở cả ba cấu hình.
3. B4ng/B4: ITC 75 **đúng**; BTB **sai**: "không có thông tin về độ tuổi tối đa được tham gia tái tục", trong khi [1] ghi "dưới
   66 tuổi (đến 70 tuổi nều tham gia tái tục…)". Thiếu 66 và 70.
4. Không có số sai. Câu khẳng định "không có thông tin" là sai.
5. [2] = `ITC_QT_C1_M41`, [1] = `BTB_QT_C1_M35`: đều đúng đoạn, nhưng câu gắn [1] lại nói đoạn đó không có thông tin.
   Câu trả lời mở đầu mỗi ý bằng [n].
6. B4 giống hệt B4ng.

Mã: **F1** (từ chối nhầm một phần: dùng câu "chưa có thông tin" của quy tắc 6 cho một sản phẩm, dù đoạn hạng 1 có số).
Phụ: chunk BTB có lỗi OCR ("nều", "bó/mẹ") có thể góp phần, vì chunk ITC cùng nội dung nhưng sạch thì được đọc đúng.

## v1-0149 · compare · medium · cờ: -

**Câu hỏi:** Thời gian chờ đối với bệnh thông thường ở quyền lợi chính của Bảo Việt An Gia khác gì so với thời gian chờ đối với bệnh hiểm nghèo ở sản phẩm CI37?

**Đáp án chuẩn:** Quyền lợi chính của Bảo Việt An Gia áp dụng thời gian chờ 30 ngày đối với bệnh thông thường, trong khi sản phẩm CI37 áp dụng thời gian chờ 90 ngày kể từ ngày bắt đầu hiệu lực bảo hiểm đối với bệnh/tình trạng hiểm nghèo. Như vậy, thời gian chờ bệnh hiểm nghèo ở CI37 dài hơn thời gian chờ bệnh thông thường ở Bảo Việt An Gia (90 ngày so với 30 ngày).

**Evidence `BVP_QT_C2_M1_B`:**

```text
[Bảo Việt An Gia | Quy tắc | I. QUYỀN LỢI BẢO HIỂM CHÍNH: ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, BIẾN CHỨNG THAI SẢN > B. Hiệu lực bảo hiểm]
Quyền lợi bảo hiểm này có hiệu lực sau thời gian chờ dưới đây:
- 30 ngày đối với bệnh thông thường (bao gồm cả thời gian phát bệnh cho đến khi kết thúc đợt điều trị/tính theo thời điểm có bệnh, không tính theo thời điểm điều trị).
- 90 ngày đối với biến chứng thai sản theo định nghĩa.
- 365 ngày đối với: bệnh có sẵn, bệnh đặc biệt theo định nghĩa, rách/đứt/tái tạo dây chằng và sụn chêm, và các bệnh được liệt kê tại điểm loại trừ chung số 46 của quy tắc bảo hiểm.
- 180 ngày đối với trẻ em đến 6 tuổi đối với các bệnh: viêm phế quản, viêm tiểu phế quản, viêm phổi các loại.
```

**Evidence `C37_QT_C2`:**

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm]
QUYỀN LỢI BẢO HIỂM ĐƯỢC CHI TRẢ THEO QUY TẮC BẢO HIỂM NÀY:
Sau thời gian chờ 90 ngày kể từ ngày bắt đầu hiệu lực bảo hiểm, nếu NĐBH bị chẩn đoán mắc một hoặc nhiều bệnh/tình trạng hiểm nghèo nào (theo danh mục dưới đây) và còn sống 30 ngày sau ngày được chẩn đoán, Bảo hiểm Bảo Việt sẽ thanh toán cho NĐBH 100% số tiền bảo hiểm.
Danh mục bệnh/tình trạng hiểm nghèo được bảo hiểm:
```

**B4rr** (rank 1 · qp ['BVP', 'C37']) top-5: **BVP_QT_C2_M1_B**, C37_QT_C1_M22, BVP_QT_C2_M2_B1_B, **C37_QT_C2**, BVP_QT_C2_M2_B3_B

> Thời gian chờ đối với bệnh thông thường ở quyền lợi chính của Bảo Việt An Gia là 30 ngày [BVP_QT_C2_M1_B], trong khi đó ở sản phẩm CI37 là 90 ngày [C37_QT_C2_M22].

**B4ng** (rank 1 · qp ['BVP', 'C37']) top-5: **BVP_QT_C2_M1_B**, C37_QT_C1_M22, BVP_QT_C2_M2_B1_B, **C37_QT_C2**, BVP_QT_C2_M2_B3_B

> Thời gian chờ đối với bệnh thông thường ở quyền lợi chính của Bảo Việt An Gia là 30 ngày [1], trong khi đó, sản phẩm CI37 không nêu rõ thời gian chờ cụ thể cho bệnh thông thường [2]. Do đó, thời gian chờ khác nhau giữa hai sản phẩm này.

**B4** (rank 1 · qp ['BVP', 'C37']) top-5: **BVP_QT_C2_M1_B**, C37_QT_C1_M22, BVP_QT_C2_M2_B1_B, **C37_QT_C2**, BVP_QT_C2_M2_B3_B

> Thời gian chờ đối với bệnh thông thường ở quyền lợi chính của Bảo Việt An Gia là 30 ngày [1], trong khi đó, sản phẩm CI37 không nêu rõ thời gian chờ cụ thể cho bệnh thông thường [2]. Do đó, thời gian chờ khác nhau giữa hai sản phẩm này.

### Nhận xét 6 bước (HA duyệt 13/11) >> đã duyệt

1. Đáp án chuẩn khớp evidence: có (An Gia 30 ngày bệnh thông thường; CI37 90 ngày cho bệnh hiểm nghèo).
2. Rank evidence: `BVP_QT_C2_M1_B` hạng 1, `C37_QT_C2` hạng 4, ở cả ba cấu hình.
3. B4ng/B4: An Gia 30 ngày **đúng**; CI37 **sai/thiếu**: "không nêu rõ thời gian chờ cụ thể cho bệnh thông thường". Model đi tìm
   "bệnh thông thường" trong CI37 thay vì bệnh hiểm nghèo, nên bỏ qua 90 ngày ở [4].
4. Không có số sai.
5. [1] = `BVP_QT_C2_M1_B` (đúng); [2] = `C37_QT_C1_M22` (định nghĩa thời gian chờ, không có số ngày). Không trích [4] (`C37_QT_C2`, có 90 ngày).
6. B4 giống hệt B4ng.

Mã: **F1** (từ chối nhầm một phần cho CI37), phụ: hiểu sai đối tượng so sánh. Nghi quy tắc 3 của rag_v3 ("đúng đối tượng
được hỏi") làm model tìm "bệnh thông thường" trong CI37; B4rr (rag_v1) trả lời đúng 90 ngày.

## Tổng hợp (HA duyệt 13/11) >> đã duyệt

| qid | Nhóm | B4ng so với evidence | Mã chính (B4ng) | Mã phụ | B4 giống B4ng? | Lỗi do rag_v3? |
| --- | --- | --- | --- | --- | --- | --- |
| v1-0032 | table | sai: 2.464.000 lấy từ bảng cá nhân `FLX_BP_S1_TB2` ([2]) | G1 | G2 ([3] = `FLX_BP_S2_TB1`) | có | có (B4rr đúng số) |
| v1-0040 | scenario | thiếu: không nhắc lại khoảng tuổi; nội dung đúng | không lỗi | thiếu chi tiết | không (B4 đủ số) | không |
| v1-0045 | scenario | thiếu 30 ngày (đã có trong câu hỏi); 70% đúng | G2 ([3], [4] sai đoạn) | – | có | có (cách trích) |
| v1-0107 | scenario | sai kết luận (bỏ qua loại trừ tâm thần) | G1 | G2 ([2]) | khác chữ, cùng sai | không (B4rr cũng sai) |
| v1-0115 | scenario | đúng, chỉ không nhắc tên CI37 | không lỗi | – | có | không |
| v1-0120 | compare | đúng, khác định dạng (liệt kê tên, không ghi "5") | không lỗi | – | không (B4 bị ngưỡng chặn: F1) | không |
| v1-0133 | compare | thiếu/sai: nói BTB "không có thông tin" dù [1] có 66/70 | F1 (một phần) | OCR "nều" trong chunk | có | có (B4rr đúng) |
| v1-0149 | compare | thiếu/sai: nói CI37 "không nêu rõ" dù [4] có 90 ngày | F1 (một phần) | hiểu sai đối tượng | có | có (B4rr đúng) |

Phân bố (B4ng, 8 câu): không lỗi 3 (0040, 0115, 0120), G1 2 (0032, 0107), F1 một phần 2 (0133, 0149), G2 1 (0045).

- **Rơi số thật do rag_v3: 3/8 câu** (0032, 0133, 0149), cộng 0045 chỉ sai trích dẫn. 0107 sai ở cả B4rr nên không tính cho
  rag_v3. 3 câu còn lại rơi số do cách tính `num_recall`: đáp án chuẩn có số lấy từ câu hỏi hoặc tên sản phẩm (CI37, "5
  chương trình", khoảng tuổi), câu trả lời ngắn của rag_v3 không nhắc lại.
- **Kiểu lỗi chính của rag_v3 ở compare là từ chối nhầm một phần (F1):** với một sản phẩm, model nói "không có thông tin"
  dù đoạn chứa số nằm trong top-5 (hạng 1 ở 0133, hạng 4 ở 0149). Câu chữ khớp quy tắc 6 ("chưa có thông tin…") và quy tắc 3
  ("đúng đối tượng") của rag_v3. `refused` không bắt được loại này vì câu trả lời vẫn có nội dung.
- **Giả thuyết `<doc so="n">` làm mất mã phân biệt bảng S1/S2: không đủ căn cứ.** Chỉ 0032 có số sai lấy từ bảng khác.
  Ở câu này, text chunk luôn mở đầu bằng tiêu đề "…dành cho cá nhân" / "…dành cho gia đình" ở cả hai dạng ngữ cảnh, còn mã
  `S1`/`S2` tự nó không mang nghĩa. Chưa loại trừ được ảnh hưởng của vị trí (hai bảng cùng cấu trúc ở [1] và [2]). Cách kiểm:
  chạy rag_v3 với `<doc so="n" id="chunk_id">` trên dev (ĐA2, cần GPU, chưa chạy).
- **Trích dẫn [n]:** 0045 trích [3]/[4] theo số điều khoản trong chunk, 0032 trích bảng gia đình khác (B4rr cũng vậy). Câu
  trả lời đôi khi mở đầu bằng "[4][3]" hay "[2] …" đứng riêng (0045, 0133).
- **Hạn chế metric:** `num_recall` đếm cả số trong câu hỏi hoặc tên sản phẩm, và đếm câu bị từ chối (0115 ở B4rr được 1,0 dù
  `refused=True`); `numbers()` không bỏ [n] trước khi trích số. Đề xuất ĐA2: bỏ [n] và số đã có trong câu hỏi khi tính khớp số.
