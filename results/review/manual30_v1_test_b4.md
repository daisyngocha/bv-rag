# Chấm tay B4 (test): mẫu 30 câu + mẫu phụ câu bị ngưỡng chặn

Run `B4_v1_test_20261107-1335`; seed 42; mẫu chính 30 câu, mẫu phụ 4 câu. Điền điểm vào `manual30_v1_test_b4.csv` (mở bằng Excel, UTF-8).

## Thang chấm

- `correct_1_5` (đúng so với đáp án chuẩn): 5 đúng và đủ mọi ý/số; 4 đúng ý chính, thiếu chi tiết phụ;
  3 đúng một phần, thiếu ý quan trọng hoặc lẫn 1 chi tiết sai không đổi kết luận; 2 phần lớn sai hoặc kết luận
  đúng nhưng lý do sai; 1 sai hoặc trả lời câu khác.
- `faithful_1_5` (trung thành với ngữ cảnh đã cấp, không xét đáp án chuẩn): 5 mọi khẳng định có trong ngữ cảnh;
  4 có diễn giải nhẹ nhưng không thêm thông tin; 3 có 1 khẳng định không có căn cứ; 2 nhiều khẳng định không căn cứ;
  1 bịa số/điều khoản.
- `cite_ok`: số trích dẫn [n] mà đoạn [n] thật sự chứa thông tin của câu mang trích dẫn đó (≤ `cite_total`).
  Trích dẫn đúng = Σ cite_ok / Σ cite_total.
- `error_code` (bỏ trống nếu không lỗi): R1 truy xuất trượt, R2 lọc nhầm sản phẩm, P1 bảng parse sai,
  G1 sinh sai/bịa số, G2 trích dẫn sai, F1 từ chối nhầm, D1 lỗi benchmark. Một nhãn chính.
- `auto_cite_in_evidence` chỉ để tham khảo (cận dưới tự động: trích dẫn trỏ đúng evidence_ids); chấm theo nội dung đoạn.

## v1-0008 · lookup · medium · C37

**Câu hỏi:** Theo quy tắc Bảo hiểm 37 bệnh hiểm nghèo (CI37), thuật ngữ "được hỗ trợ" được định nghĩa như thế nào?

**Đáp án chuẩn:** "Được hỗ trợ" có nghĩa là sử dụng các thiết bị hoặc dụng cụ đặc biệt để hỗ trợ các hoạt động mà không phải là sự trợ giúp từ con người.

**Evidence:** `C37_QT_C2_GC1`

**Câu trả lời:**

> Theo quy tắc Bảo hiểm 37 bệnh hiểm nghèo (CI37), thuật ngữ "được hỗ trợ" có nghĩa là dùng các thiết bị hoặc dụng cụ đặc biệt để hỗ trợ các hoạt động mà không phải sự trợ giúp của con người. Đây là định nghĩa được sử dụng trong các trường hợp như loạn dưỡng cơ [1], mất khả năng sống độc lập [2], và bệnh Parkinson [4].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] C37_QT_C2_M16 ★</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > 16. Loạn dưỡng cơ]
Một nhóm các bệnh thoái hóa di truyền của cơ bắp có đặc trưng làm yếu và teo cơ. Chẩn đoán loạn dưỡng cơ phải do chuyên gia về thần kinh chuẩn đoán và có kết luận chắc chắn. Điều kiện cần thiết để khẳng định mắc bệnh này là người đó không thể thực hiện được ít nhất ít nhất 3 trong số 6 "Hoạt động sinh hoạt hàng ngày" sau đây trong thời gian liên tục ít nhất 6 tháng: Các hoạt động sinh hoạt hàng ngày bao gồm:
i. Tắm rửa – khả năng tắm bằng bồn hoặc vòi hoa sen (bao gồm cả khả năng vào và ra khỏi bồn tắm hoặc phòng tắm) hoặc tắm rửa bằng các hình thức khác;
ii. Mặc quần áo - khả năng mặc, cởi, thắt chặt và nới lỏng đối với trang phục, và trong một số tình huống thích hợp, đối với dụng cụ niềng răng, chân/tay giả hoặc các dụng cụ phẫu thuật khác;
iii. Di chuyển - khả năng chuyển từ giường sang ghế thẳng hoặc xe lăn và ngược lại;
iv. Di động - khả năng di chuyển trong nhà từ phòng này sang phòng khác trên bề mặt bằng phẳng;
i. Vệ sinh - khả năng sử dụng nhà vệ sinh hoặc kiểm soát các chức năng ruột và bàng quang để duy trì việc vệ sinh cá nhân hợp lý ở mức độ thỏa đáng;
ii. Ăn - khả năng tự ăn khi thức ăn đã được chuẩn bị và sẵn có. Theo quy tắc bảo hiểm này, “được hỗ trợ” có nghĩa là dùng các thiết bị hoặc dụng cụ đặc biệt để hỗ trợ các hoạt động mà không phải sự trợ giúp của con người.
```
</details>

<details open><summary>[2] C37_QT_C2_M37 ★</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > 37. Mất khả năng sống độc lập]
Do hậu quả của bệnh hoặc thương tật mà NĐBH không có khả năng thực hiện (dù được hỗ trợ hoặc không) ít nhất 3 trong số 6 "Hoạt động sinh hoạt hàng ngày" sau đây trong thời gian liên tục ít nhất 6 tháng: Các hoạt động sinh hoạt hàng ngày bao gồm:
i. Tắm rửa – khả năng tắm bằng bồn hoặc vòi hoa sen (bao gồm cả khả năng vào và ra khỏi bồn tắm hoặc phòng tắm) hoặc tắm rửa bằng các hình thức khác;
ii. Mặc quần áo - khả năng mặc, cởi, thắt chặt và nới lỏng đối với trang phục, và trong một số tình huống thích hợp, đối với dụng cụ niềng răng, chân/tay giả hoặc các dụng cụ phẫu thuật khác;
iii. Di chuyển - khả năng chuyển từ giường sang ghế thẳng hoặc xe lăn và ngược lại;
i. Di động - khả năng di chuyển trong nhà từ phòng này sang phòng khác trên bề mặt bằng phẳng;
ii. Vệ sinh - khả năng sử dụng nhà vệ sinh hoặc kiểm soát các chức năng ruột và bàng quang để duy trì việc vệ sinh cá nhân hợp lý ở mức độ thỏa đáng;
iii. Ăn - khả năng tự ăn khi thức ăn đã được chuẩn bị và sẵn có. Tình trạng này phải được bác sĩ do CTBH chỉ định xác nhận. Theo quy tắc bảo hiểm này, “được hỗ trợ” có nghĩa là dùng các thiết bị hoặc dụng cụ đặc biệt để hỗ trợ các hoạt động mà không phải sự trợ giúp của con người. Loại trừ các bệnh lý không phải do thực thể như bệnh loạn thần kinh và các bệnh tâm thần.
```
</details>

<details><summary>[3] C37_QT_C2_GC1 ✓</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > Ghi chú:]
(*) Tình trạng tổn thương thần kinh vĩnh viễn: Tổn thương thần kinh vĩnh viễn có nghĩa là các triệu chứng rối loạn chức năng trong hệ thống thần kinh xuất hiện khi khám lâm sàng và dự kiến sẽ kéo dài trong suốt cuộc đời của Người được bảo hiểm.
i. Di động - khả năng di chuyển trong nhà từ phòng này sang phòng khác trên bề mặt bằng phẳng;
ii. Vệ sinh - khả năng sử dụng nhà vệ sinh hoặc kiểm soát các chức năng ruột và bàng quang để duy trì việc vệ sinh cá nhân hợp lý ở mức độ thỏa đáng;
iii. Ăn - khả năng tự ăn khi thức ăn đã được chuẩn bị và sẵn có.
Tình trạng này phải được bác sĩ do CTBH chỉ định xác nhận. Theo quy tắc bảo hiểm này, "được hỗ trợ" có nghĩa là dùng các thiết bị hoặc dụng cụ đặc biệt để hỗ trợ các hoạt động mà không phải sự trợ giúp của con người.
Loại trừ các bệnh lý không phải do thực thể như bệnh loạn thần kinh và các bệnh tâm thần.
```
</details>

<details open><summary>[4] C37_QT_C2_M17 ★</summary>

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
</details>

<details><summary>[5] C37_QT_C1_M20 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 20. Sự kiện được bảo hiểm:]
Là các sự kiện khách quan do các bên thỏa thuận với nhau hoặc do pháp luật quy định khi sự kiện xảy ra mà CTBH sẽ phải trả tiền bảo hiểm cho người thụ hưởng hoặc bồi thường cho NĐBH.
```
</details>

---

## v1-0009 · lookup · easy · FLX

**Câu hỏi:** Theo quy tắc Bảo hiểm Du lịch Flexi, hoạt động lặn nước sâu đến độ sâu nào sẽ bị loại trừ bảo hiểm?

**Đáp án chuẩn:** Bảo hiểm Bảo Việt loại trừ trách nhiệm bảo hiểm đối với tổn thất phát sinh khi người được bảo hiểm tham gia lặn nước sâu ở độ sâu hơn 40m.

**Evidence:** `FLX_QT_C3_K1_P1`

**Câu trả lời:**

> Theo quy tắc Bảo hiểm Du lịch Flexi được nêu trong đoạn [1], hoạt động lặn nước sâu dưới độ sâu hơn 40m sẽ bị loại trừ bảo hiểm.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] FLX_QT_C3_K1_P1 ★✓</summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | CHƯƠNG III - Các điểm loại trừ chung - Áp dụng đối với tất cả các mục]
1. Bảo hiểm Bảo Việt không chịu trách nhiệm chi trả tiền bảo hiểm đối với những rủi ro, hạng mục, điều kiện, các hành động, nguyên nhân, bệnh, phương pháp điều trị như được liệt kê sau đây và các chi phí phát sinh liên quan hay hậu quả của chúng: Tổn thất phát sinh trực tiếp hay gián tiếp từ:
a. Nổi loạn, bạo loạn dân sự, chiến tranh, xâm lược, hành động của kẻ thù nước ngoài, chiến sự (cho dù có tuyên bố chiến tranh hay không), nội chiến, bạo loạn, cách mạng, khởi nghĩa, hành động quân sự hay cướp chính quyền, sung công, quốc hữu hóa, đạo luật hay chỉ thị của bất kỳ chính phủ hay chính quyền địa phương nào.
b. Bức xạ ion hóa hay nhiễm xạ từ nhiên liệu hạt nhân hay từ chất thải hạt nhân từ bất kỳ quá trình phân rã hạt nhân nào hoặc từ bất kỳ nguyên liệu vũ khí hạt nhân nào.
c. Tự sát hay có ý định tự sát, cố ý gây thương tích trên thân thể, mất trí, khuyết tật bẩm sinh, tâm thần, bệnh/rối loạn tâm thần, bệnh /rối loạn về thần kinh, các rủi ro phát sinh trực tiếp hoặc gián tiếp từ việc: Người được bảo hiểm nghiện rượu/bia, ma túy, chất kích thích; hoặc sử dụng, lạm dụng hay nghiện bất cứ chất có cồn/chất kích thích/chất gây nghiện nào, tự tìm đến các nguy hiểm không cần thiết (trừ trong truờng hợp nỗ lực cứu người), bệnh lây qua đường tình dục, AIDS hoặc các phức hợp liên quan đến AIDS, các bệnh về máu, các bệnh liên quan đến ung thư, đi du lịch nhằm mục đích điều trị bệnh.
d. Bệnh đặc biệt, bệnh/thương tật có sẵn, nha khoa và thai sản;
e. Tham gia vào:
i. Bất kỳ hoạt động đua nào;
ii. Lặn nước sâu (lặn xuống dưới độ sâu hơn 40m);
```
</details>

<details><summary>[2] FLX_QT_C3_K2-9 </summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | CHƯƠNG III - Các điểm loại trừ chung - Áp dụng đối với tất cả các mục]
2. Đại dịch/ tình trạng y tế khẩn cấp theo thông báo chính thức của Tổ chức Y tế Thế giới (WHO) hoặc chính quyền địa phương tại điểm đến theo lịch trình.
3. Thảm họa tự nhiên bao gồm: bão, lũ lụt, động đất, sóng thần, núi lửa, cháy rừng, lở đất, lở tuyết, vòi rồng (trừ khi hợp đồng có quy định khác).
4. Người được bảo hiểm không đủ sức khoẻ để du lịch, đi lại hoặc du lịch, đi lại trái với lời khuyên của bác sỹ hành nghề hợp pháp;
5. Mọi rủi ro và hậu quả liên quan đến không tặc, bắt cóc hoặc tống tiền;
6. Kiểm tra sức khỏe / điều trị định kỳ; xét nghiệm định kỳ; kiểm tra sức khỏe tổng quát dù có kết luận chẩn đoán có bệnh hay không; tầm soát ung thư; khám/điều
trị cho tình trạng thiếu/rối loạn hooc-môn sinh trưởng, tiền mãn kinh hay mãn kinh ở phụ nữ; tất cả các hình thức tiêm chủng, vắc xin và thuốc phòng ngừa.
7. Điều trị thẩm mỹ, phẫu thuật thẩm mỹ, phẫu thuật tạo hình, các biến chứng của việc điều trị thẩm mỹ/phẫu thuật thẩm mỹ/phẫu thuật tạo hình; khám và điều trị sẹo, sụp mí mắt, nốt ruồi; chỉnh hình vì mục đích thẩm mỹ.
8. Người được bảo hiểm từ 14 tuổi trở lên vi phạm pháp luật bị khởi tố hình sự; vi phạm nội quy, quy định của chính quyền địa phương hoặc các tổ chức xã hội; vi phạm nội quy của cơ quan theo Luật lao động; vi phạm Luật Giao thông đường bộ; vi phạm quy định của các Cơ quan có thẩm quyền tại nước sở tại.
9. Người được bảo hiểm tử vong do lỗi cố ý của Bên mua bảo hiểm hoặc lỗi cố ý của Người thụ hưởng. Chi phí y tế và thương tật (toàn bộ) vĩnh viễn phát sinh do lỗi cố ý của chính bản thân Người được bảo hiểm hoặc Bên mua bảo hiểm hoặc Người thụ hưởng.
```
</details>

<details><summary>[3] FLX_QT_C1_M1_K7 </summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | I. ĐỊNH NGHĨA > 7. Các hoạt động có tính chất nguy hiểm]
Là các hoạt động bao gồm nhưng không giới hạn: tất cả các hình thức thi đấu võ thuật (boxing, đấu vật, karate, taekwondo và các hình thức võ thuật khác), nhảy dù, nhào lộn trên không, nhảy bungee, lướt sóng và/hoặc các hoạt động khám phá bờ biển nhiều vách đá bằng cách leo, trèo, bơi lội; các chuyến thám hiểm;trượt tuyết mạo hiểm; leo núi đá, leo núi tuyết, leo núi băng hoặc leo núi tự do hoặc leo không dùng dây và tất cả các hình thức leo núi một mình; Đối với các hoạt động leo núi theo tuyến đường cố định hoặc các hoạt động mạo hiểm, khám phá khác không có hệ thống phân cấp hoặc đơn vị tổ chức không đưa ra chỉ dẫn về cấp độ khó, Người được bảo hiểm cần thông báo cho Công ty bảo hiểm và được Công ty bảo hiểm chấp thuận.
```
</details>

<details><summary>[4] FLX_QT_C1_M2 </summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | CHƯƠNG I - Định nghĩa và quy định chung > II. PHẠM VI LÃNH THỔ]
VÙNG 1
VÙNG 2
VÙNG 3
Trong đó,
Nếu một chuyến đi bao gồm nhiều hơn một vùng - khu vực rộng nhất sẽ được áp dụng để tính phí bảo hiểm;
Các quốc gia/khu vực bị cấm vận bao gồm Afghanistan, Cuba, Congo, Iran, Iraq, Syria, Belarus, Nicaragua, Bắc Triều Tiên, Lebanon, Liberia, Libya, Somalia, Sudan, Nam Sudan, Venezuela, Crimea, và Zimbabwe. Danh sách các quốc gia bị loại trừ có thể thay đổi và được cập nhật trên Giấy chứng nhận bảo hiểm và/hoặc Hợp đồng bảo hiểm.
ASEAN: Brunei, Cam-pu-chia, Indonesia, Lào, Malaysia, Myanmar, Philippines, Singapore và Thái Lan
Châu Á – Thái Bình Dương: bao gồm các nước ở Vùng 1 và các nước sau đây: Australia (Úc), Trung Quốc, đảo Guam, HongKong, Nhật Bản, Hàn Quốc, Macao, New Zealand, Đài Loan và Ấn Độ.
Toàn thế giới (trừ Việt Nam và các quốc gia/khu vực bị cấm vận)
```
</details>

<details><summary>[5] FLX_QT_C3_K1_P2 </summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | CHƯƠNG III - Các điểm loại trừ chung - Áp dụng đối với tất cả các mục]
iii. Tham dự hoạt động thể thao hoặc bất kỳ hoạt động về khả năng chuyên môn qua đó Người được bảo hiểm có thể giành được hay nhận thù lao, trao tặng, bảo trợ hay món tặng thưởng bất kỳ;
iv. Các hoạt động hàng không trừ khi là hành khách đi trên máy bay thuộc hãng hàng không có giấy phép hợp pháp kinh doanh chuyên chở hành khách .
v. Các hoạt động có tính chất nguy hiểm.
```
</details>

---

## v1-0010 · lookup · easy · ITC

**Câu hỏi:** Theo quy tắc bảo hiểm Bảo Việt Intercare, công ty cứu trợ do Bảo Việt chỉ định có trực tiếp khám chữa bệnh cho người được bảo hiểm không và ai là người có quyền chọn cơ sở y tế?

**Đáp án chuẩn:** Công ty cứu trợ không trực tiếp điều trị hay chẩn đoán bệnh. Quyền quyết định lựa chọn bác sĩ và cơ sở điều trị thuộc về Người được bảo hiểm.

**Evidence:** `ITC_QT_C6_M1`

**Câu trả lời:**

> Công ty cứu trợ do Bảo Việt chỉ định không trực tiếp khám chữa bệnh cho người được bảo hiểm [1]. Quyền quyết định lựa chọn bác sĩ và cơ sở điều trị thuộc về người được bảo hiểm [1].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] ITC_QT_C6_M1 ★✓</summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN VI. VẬN CHUYỂN Y TẾ CẤP CỨU VÀ HỒI HƯƠNG > 1. Hỗ trợ dịch vụ y tế]
Công ty cứu trợ do Bảo Việt chỉ định, khi có yêu cầu, sẽ cung cấp tên, địa chỉ, số điện thoại và, nếu có thể, giờ làm việc của bác sĩ, bệnh viện, phòng khám, nha sĩ, phòng khám răng trong phạm vi lãnh thổ của chương trình lựa chọn (gọi chung là "Người cung cấp dịch vụ y tế"). Công ty cứu trợ sẽ không trực tiếp điều trị hay chẩn đoán và mặc dù Công ty cứu trợ cung cấp những thông tin trên nhưng quyền quyết định lựa chọn bác sĩ và cơ sở điều trị nào thuộc về Người được bảo hiểm. Tuy nhiên Công ty cứu trợ sẽ cố gắng hết sức và cẩn trọng khi tư vấn "Người cung cấp dịch vụ y tế" cho Người được bảo hiểm.
```
</details>

<details><summary>[2] ITC_QT_C6_M7 </summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN VI. VẬN CHUYỂN Y TẾ CẤP CỨU VÀ HỒI HƯƠNG > 7. Cung cấp thuốc đặc trị]
(chỉ áp dụng khi Người được bảo hiểm ra khỏi lãnh thổ Việt Nam)
Công ty cứu trợ do Bảo Việt chỉ định sau khi nhận được ủy quyền của Bảo Việt sẽ điều phối các loại thuốc đặc trị cần thiết cho việc chăm sóc và/hoặc điều trị
cho Người được bảo hiểm nhưng với điều kiện những loại thuốc đó không sẵn có tại địa phương đó. Việc cung cấp các loại thuốc đặc trị sẽ tuân thủ theo luật pháp và quy chế địa phương liên quan tới nhập khẩu và cung cấp những sản phẩm đó. Bảo Việt sẽ chi trả những chi phí liên quan tới việc cung cấp thuốc thiết yếu kể trên.
8.Bảo lãnh chi trả các chi phí y tế phát sinh trong thời gian nằm viện, theo dõi sức khoẻ trong và sau khi nằm viện
Ngoài lãnh thổ Việt Nam (áp dụng trong trường hợp chi phí phát sinh trên 2.500 USD và sự kiện bảo hiểm phát sinh sau khi Người được bảo hiểm ra ngoài lãnh thổ Việt Nam thuộc phạm vi của hợp đồng bảo hiểm):
Nếu Người được bảo hiểm gặp sự cố ốm đau hay tai nạn cần phải nằm viện, và yêu cầu được sự đồng ý của Bảo Việt thì Công ty cứu trợ sẽ giúp thu xếp nhập viện cho Người được bảo hiểm. Công ty cứu trợ cũng sẽ, khi có ủy quyền của Bảo Việt, thay mặt Bảo Việt bảo lãnh chi trả viện phí cho Người được bảo hiểm và giám sát tình trạng sức khoẻ của Người được bảo hiểm cùng với bác sĩ điều trị; và sẽ đảm bảo tuân thủ nghĩa vụ bảo mật thông tin và thực thi trách nhiệm trong phạm vi quyền hạn cho phép.
Trong lãnh thổ Việt Nam:
Nếu Người được bảo hiểm điều trị tại bệnh viện nằm trong hệ thống bảo lãnh chi trả viện phí của Bảo Việt thì Bảo Việt sẽ chi trả trực tiếp cho bệnh viện các chi phí thuộc phạm vi bảo hiểm.
Nếu bệnh viện chưa có thỏa thuận với Bảo Việt, Người được bảo hiểm phải tự chi trả các chi phí phát sinh trước khi xuất viện.
THƯƠNG HIỆU BẢO HIỂM ĐƯỢC TÍN NHIỆM NHẤT CHÂU Á
VINH DANH BỞI GLOBAL BRAND MAGAZINE
```
</details>

<details><summary>[3] ITC_QT_C1_M20 </summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN I - ĐỊNH NGHĨA > 20. Công ty cứu trợ do Bảo Việt chỉ định]
Là công ty cứu trợ quốc tế do Bảo hiểm Bảo Việt ủy quyền thực hiện các dịch vụ cứu trợ y tế và hồi hương.
```
</details>

<details><summary>[4] ITC_QT_C6_M2 </summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN VI. VẬN CHUYỂN Y TẾ CẤP CỨU VÀ HỒI HƯƠNG > 2. Thu xếp hẹn bác sĩ]
(Chỉ áp dụng khi Người được bảo hiểm ra khỏi lãnh thổ Việt Nam)
Công ty cứu trợ do Bảo Việt chỉ định sẽ thu xếp cho Người được bảo hiểm hẹn gặp bác sĩ địa phương để khám hoặc điều trị.
```
</details>

<details><summary>[5] ITC_QT_C6_M3 </summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN VI. VẬN CHUYỂN Y TẾ CẤP CỨU VÀ HỒI HƯƠNG > 3. Thu xếp nhập viện]
(Chỉ áp dụng khi Người được bảo hiểm ra khỏi lãnh thổ Việt Nam)
Nếu Người được bảo hiểm lâm vào tình trạng nguy kịch cần phải nhập viện thì Công ty cứu trợ do Bảo Việt chỉ định sẽ thu xếp nhập viện cho Người được bảo hiểm khi có yêu cầu.
```
</details>

---

## v1-0013 · lookup · easy · C37

**Câu hỏi:** Theo quy tắc Bảo hiểm 37 bệnh hiểm nghèo (CI37), hợp đồng cần duy trì hiệu lực liên tục trong bao lâu để công ty bảo hiểm không truy xét các lỗi kê khai sai sót không cố ý?

**Đáp án chuẩn:** Công ty bảo hiểm sẽ không truy xét các lỗi kê khai sai sót không cố ý nếu hợp đồng bảo hiểm có hiệu lực liên tục trong hơn bảy trăm ba mươi (730) ngày liên tiếp kể từ ngày hiệu lực.

**Evidence:** `C37_QT_C4_M6`

**Câu trả lời:**

> Theo quy tắc Bảo hiểm 37 bệnh hiểm nghèo (CI37), hợp đồng cần duy trì hiệu lực liên tục trong hơn bảy trăm ba mươi (730) ngày liên tiếp kể từ ngày hiệu lực để công ty bảo hiểm không truy xét các lỗi kê khai sai sót không cố ý [1].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] C37_QT_C4_M6 ★✓</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG IV - Điều kiện chung > 6. Miễn truy xét]
Với điều kiện HĐBH có hiệu lực liên tục trong hơn bảy trăm ba mươi (730) ngày liên tiếp kể từ ngày hiệu lực, CTBH sẽ không truy xét đối với các lỗi kê khai sai sót không cố ý các thông tin trong Giấy yêu cầu bảo hiểm và các tài liệu liên quan.
Quy định này không được áp dụng đối với việc vi phạm nghĩa vụ của BMBH/NĐBH trong các trường hợp sau đây:
- BMBH/NĐBH cố ý cung cấp thông tin không trung thực trong quá trình tham gia bảo hiểm để được hưởng quyền lợi bảo hiểm hoặc được bảo hiểm;
- BMBH/NĐBH cố ý không cung cấp đầy đủ thông tin cho CTBH trong trường hợp có thể gia tăng rủi ro hoặc trách nhiệm của CTBH trong quá trình thực hiện hợp đồng;
- Trong trường hợp BMBH cố ý kê khai sai tuổi của NĐBH, CTBH có quyền đơn phương đình chỉ thực hiện HĐBH hoặc thu phí đến ngày đình chỉ thực hiện HĐBH;
- Trong trường hợp BMBH không thanh toán đầy đủ phí bảo hiểm hoặc không thanh toán phí bảo hiểm theo thỏa thuận trong Hợp đồng và theo quy định của pháp luật, CTBH có quyền chấm dứt Hợp đồng.
```
</details>

<details><summary>[2] C37_QT_C1_M21 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 21. Thời hạn bảo hiểm]
Thời hạn bảo hiểm được tính từ thời điểm Bảo hiểm Bảo Việt bắt đầu nhận bảo hiểm cho đến khi kết thúc bảo hiểm. Thời hạn bảo hiểm bắt đầu từ 0 giờ 1 phút sáng ngày bắt đầu hiệu lực bảo hiểm và được kết thúc vào 23 giờ 59 phút ngày hết hạn hiệu lực bảo hiểm.
Đối với hợp đồng bảo hiểm cá nhân: Thời hạn bảo hiểm là 01 năm và được quy định cụ thể trong hợp đồng bảo hiểm.
Đối với hợp đồng bảo hiểm tổ chức: Thời hạn bảo hiểm là 01 năm hoặc ít hơn, và được quy định cụ thể trong hợp đồng bảo hiểm.
```
</details>

<details><summary>[3] C37_QT_C1_M13 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 13. Ngày bắt đầu hiệu lực bảo hiểm:]
Là ngày hiệu lực của hợp đồng bảo hiểm đầu tiên (được tính từ 0 giờ 1 phút của ngày quy định trên hợp đồng) khi Bên mua bảo hiểm tham gia chương trình bảo hiểm này hoặc của hợp đồng bảo hiểm tái tục liên tục hàng năm. Đối với những hợp đồng bảo hiểm không được tái tục liên tục hàng năm, ngày bắt đầu hiệu lực bảo hiểm đầu tiên là ngày hiệu lực của hợp đồng bảo hiểm mới nhất trừ khi có thỏa thuận khác.
```
</details>

<details><summary>[4] C37_QT_C1_M11 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 11. Hợp đồng tái tục liên tục]
Là hợp đồng bảo hiểm được tái tục vào ngày hoặc trước ngày hết hạn hiệu
lực của hợp đồng bảo hiểm cũ. Bảo hiểm Bảo Việt không yêu cầu Người được bảo hiểm phải kê khai lại giấy yêu cầu bảo hiểm trong trường hợp tái tục liên tục.
```
</details>

<details><summary>[5] C37_QT_C1_M22 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 22. Thời gian chờ]
Là khoảng thời gian mà các sự kiện bảo hiểm xảy ra sẽ không được Bảo hiểm Bảo Việt chi trả đối với các quyền lợi bảo hiểm có liên quan, không chi trả cả những trường hợp thời điểm phát sinh rủi ro nằm trong thời gian chờ nhưng chi phí phát sinh hoặc hậu quả của đợt điều trị rủi ro này lại kéo dài quá thời gian chờ quy định. Thời gian chờ được tính kể từ Ngày bắt đầu hiệu lực bảo hiểm. Đối với các hợp đồng bảo hiểm tái tục liên tục hàng năm và không thay đổi quyền lợi bảo hiểm, thời gian chờ được tính từ Ngày bắt đầu hiệu lực bảo hiểm của hợp đồng bảo hiểm năm đầu tiên.
```
</details>

---

## v1-0080 · lookup · easy · BTB

**Câu hỏi:** Trong bảo hiểm Bảo Việt Tâm Bình, quy tắc giới hạn chi trả khi đã được hợp đồng bảo hiểm khác thanh toán sẽ không áp dụng đối với những quyền lợi nào?

**Đáp án chuẩn:** Quy định này không áp dụng đối với quyền lợi bảo hiểm tử vong và thương tật vĩnh viễn.

**Evidence:** `BTB_QT_C4_M15`

**Câu trả lời:**

> Quy tắc giới hạn chi trả khi đã được hợp đồng bảo hiểm khác thanh toán sẽ không áp dụng đối với quyền lợi bảo hiểm tử vong và thương tật vĩnh viễn [1].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] BTB_QT_C4_M15 ★✓</summary>

```text
[Bảo Việt Tâm Bình | Quy tắc | CHƯƠNG IV: QUY ĐỊNH CHUNG > 15. Các hợp đồng/loại hình bảo hiểm tương tự khác]
Hợp đồng bảo hiểm cấp theo quy tắc này là ưu tiên đầu tiên. Nếu tại thời điểm phát sinh bồi thường bảo hiểm, Người được bảo hiểm đang được một hợp đồng bảo hiểm khác có hiệu lực chi trả cho cùng những chi phí và tổn thất đòi khiếu nại, Người được bảo hiểm có quyền yêu cầu bồi thường ở bắt kỳ hợp đồng bảo hiểm nào có hiệu lực. Trong trường hợp bồi thường đã được thanh toán bởi hợp đồng khác thì hợp đồng bảo hiểm cấp theo quy tắc này sẽ chỉ chi trả cho Người được bảo hiểm các khoản không được thanh toán dưới hợp đồng bảo hiểm khác đó. Tuy nhiên, quy định này sẽ không áp dụng đối với quyền lợi bảo hiểm tử vong và thương tật vĩnh viễn.
```
</details>

<details><summary>[2] BTB_QT_C4_M6 </summary>

```text
[Bảo Việt Tâm Bình | Quy tắc | CHƯƠNG IV: QUY ĐỊNH CHUNG > 6. Thay đổi quyền lợi bảo hiểm]
Giới hạn trách nhiệm của các quyền lợi không thể thay đổi trong suốt thời hạn hợp đồng bảo hiểm. Những quyền lợi này chỉ có thể được thay đổi vào ngày tái tục của hợp đồng bảo hiểm trên cơ sở có xác nhận của Bảo hiểm Bảo Việt.
Quy định này không áp dụng trong hợp đồng bảo hiểm tổ chức đối với trường hợp Người được bảo hiểm thay đổi vị trí trong công tác/thay đổi cấp bậc theo chính sách nhân sự của Bên mua bảo hiểm. Quyền lợi bảo hiểm sẽ thay đổi với các điều kiện sau:
- _ Nằm trong giới hạn của các nhóm quyền lợi đã khai báo đầu hiệu lực hợp đồng.
- _ Yêu cầu có sửa đổi bổ sung và nộp phí bổ sung khi có sự thay đổi lương/thay đổi cấp; trong trường hợp cần thiết, khách hàng phải cung cấp được các chứng từ chứng minh việc thay đổi này theo chính sách nhân sự của Bên mua bảo hiểm.
- _ Lịch sử bồi thường sẽ được tính tiếp vào nhóm quyền lợi mới.
Áp dụng với cả hợp đồng bảo hiểm cá nhân và hợp đồng bảo hiểm tổ chức: Trường hợp tái tục với Số tiền bảo hiểm/hạn mức phụ cao hơn và/hoặc tham gia thêm quyền lợi mới so với năm trước phải được sự chấp thuận của Bảo hiểm Bảo Việt: phần chênh lệch về số tiền bảo hiểm/hạn mức phụ cũng như quyền lợi tham gia thêm mới sẽ không được coi là tái tục liên tục, và thời gian chờ đối với phần chênh lệch vẻ số tiền bảo hiểm/hạn mức phụ cũng như quyền lợi tham gia thêm mới sẽ được tính từ thời điểm hợp đồng tái tục (có số tiền bảo hiểm/hạn mức phụ cao hơn và/hoặc tham gia thêm quyền lợi mới) có hiệu lực, trừ trường hợp có thỏa thuận khác trong hợp đồng bảo hiểm.
```
</details>

<details><summary>[3] BTB_QT_C2_B_M3_P2 </summary>

```text
[Bảo Việt Tâm Bình | Quy tắc | QUYỀN LỢI BẢO HIỂM BỎ SUNG > 3. Bảo hiểm Trợ cấp mắt giảm thu nhập/Trợ cấp lương (áp dụng với hợp đồng bảo hiểm tổ chức) Trợ cấp ]
Lưu ý: Mức lương (không bao gồm tiền làm thêm giờ, tiền thưởng hay các khoản thu nhập không mang tính cố định...) trên hợp đồng lao động hay trên chứng từ khác tương đương áp dụng để chi trả bồi thường đối với tất cả các quyền lợi bảo hiểm sẽ là mức lương tính tại thời điểm xảy ra sự kiện bảo hiểm. Mức lương thay đổi phải có thông báo với Công ty Bảo hiểm và nộp phí đầy đủ.
se Lưu ý áp dụng chung với tất cả các quyền lợi bảo hiểm:
-_ Đối với phương pháp điều trị Đông y, các mức giới hạn quyền lợi bảo hiểm sẽ được thanh toán tối đa không vượt quá 50% số tiền bảo hiểm của quyền lợi tương ứng.
-_ Đối với điều trị/trợ cấp/tử vong/thương tật toàn bộ vĩnh viễn do bệnh ung thư và biến chứng/hậu quả liên quan đến bệnh ung thư (Sau thời gian chờ 2 năm, từ năm thứ 3 tham gia liên tục): Chi trả tối đa 50% số tiền bảo hiểm tương ứng với từng quyền lợi.
-_ Quy định đồng chi trả đối với trẻ em từ 15 ngày tuổi đến 3 tuổi:
- Tỷ lệ áp đồng chi trả: 70/30 (Bảo hiểm Bảo Việt chi trả 70%, Người được bảo hiểm tự chi trả 30%).
- Quy định này không áp dụng trong trường hợp Người được bảo hiểm khám và điều trị tại các cơ sở y tế/bệnh viện công lập (trừ các Khoa quốc tế/Khoa điều trị tự nguyện/Khoa điều trị theo yêu cầu của Bệnh viện công lập).
```
</details>

<details><summary>[4] BTB_BQL_S3 </summary>

```text
[Bảo Việt Tâm Bình | Bảng quyền lợi | Lưu ý áp dụng chung với tất cả các quyền lợi bảo hiểm:]
- Đối với phương pháp điều trị Đông y, các mức giới hạn quyền lợi bảo hiểm sẽ được thanh toán tối đa không vượt quá 50% số tiền bảo hiểm của quyền lợi tương ứng.
- Đối với điều trị/trợ cấp/tử vong/thương tật toàn bộ vĩnh viễn do bệnh ung thư và biến chứng/hậu quả liên quan đến bệnh ung thư (Sau thời gian chờ 2 năm, từ năm thứ 3 tham gia liên tục): Chi trả tối đa 50% số tiền bảo hiểm tương ứng với từng quyền lợi.
- Quy định đồng chi trả đối với trẻ em từ 15 ngày tuổi đến 3 tuổi:
- Tỷ lệ áp đồng chi trả: 70/30 (Bảo hiểm Bảo Việt chi trả 70%, Người được bảo hiểm tự chi trả 30%).
- Quy định này không áp dụng trong trường hợp Người được bảo hiểm khám và điều trị tại các Cơ sở y tế/Bệnh viện công lập (trừ các Khoa quốc tế/Khoa điều trị tự nguyện/Khoa điều trị theo yêu cầu của Bệnh viện công lập).
- Lưu ý về điều trị răng:
Hợp đồng bảo hiểm bồi thường cho các chi phí khám chữa răng hợp lý, hợp lệ và được thực hiện tại các cơ sở y tế theo quy định sau:
- Chuyên khoa Nha tại tất cả các bệnh viện hoạt động hợp pháp trong phạm vi lãnh thổ Việt Nam.
- Tại Thành phố Hà Nội và Thành Phố Hồ Chí Minh: ngoài Chuyên khoa nha tại tất cả các bệnh viện nói trên, Công ty bảo hiểm chỉ chấp thuận bồi thường cho các chi phí phát sinh tại các Phòng khám/Nha khoa trong hệ thống bảo lãnh viện phí của Công ty bảo hiểm.
- Đối với các Tỉnh thành khác: ngoài Chuyên khoa Nha tại tất cả các bệnh viện nói trên, chấp thuận bồi thường cho các chi phí phát sinh tại các Phòng khám/Nha khoa có giấy phép đăng ký kinh doanh và giấy phép hành nghề hợp pháp và cấp được hóa đơn hợp lệ theo quy định của Bộ Tài Chính.
- Bảo hiểm Bảo Việt không chi trả cho các chi phí khám và điều trị tại cơ sở y tế thuộc danh sách Cơ sở y tế không chi trả bảo hiểm được cập nhật tại trang thông tin điện tử chính thức của Bảo hiểm Bảo Việt.
```
</details>

<details><summary>[5] BTB_QT_C1_M27 </summary>

```text
[Bảo Việt Tâm Bình | Quy tắc | CHƯƠNG I: ĐỊNH NGHĨA > 27. Đồng chi trả]
Là số tiền theo tỷ lệ mà Công ty bảo hiểm và Người được bảo hiểm cùng chi trả trên các quyền lợi liên quan phát sinh thuộc phạm vi bảo hiểm. Đồng chi trả được tính theo tỷ lệ phân trăm (%) trên tổng chi phí thực tế phát sinh thuộc phạm vi bảo hiểm hoặc trên các mức giới hạn phụ của quyền lợi bảo hiểm, tùy theo số tiền nào thấp hơn thì được áp dụng.
Giới hạn chi phí được bảo hiểm sau khi áp dụng đồng chi trả tối đa bằng giới hạn của mục quyền lợi trong bảng quyền lợi bảo hiểm.
Khi hợp đồng bảo hiểm quy định áp dụng đồng chi trả theo cơ sở y tế, việc đồng chi trả này được áp dụng cho mọi chi phí phát sinh tại cơ sở y tế đó và các chi phí phát sinh liên quan do bác sĩ tại cơ sở y tế đó chỉ định.
Khi Hợp đồng bảo hiểm quy định nhiều tỷ lệ đồng chi trả thì sẽ áp dụng đồng thời và lần lượt từng tỷ lệ đồng chi trả.
```
</details>

---

## v1-0082 · lookup · medium · C37

**Câu hỏi:** Theo quy tắc sản phẩm Bảo hiểm 37 bệnh hiểm nghèo (CI37), nếu Người được bảo hiểm đơn phương chấm dứt hợp đồng thì Bên mua bảo hiểm được hoàn lại phí bảo hiểm như thế nào?

**Đáp án chuẩn:** Bên mua bảo hiểm sẽ được hoàn lại 80% phí bảo hiểm cho thời hạn bảo hiểm còn lại đã đóng phí, trừ trường hợp Công ty bảo hiểm đã thanh toán các quyền lợi theo điều khoản và điều kiện của hợp đồng.

**Evidence:** `C37_QT_C4_M10`

**Câu trả lời:**

> Theo quy tắc sản phẩm Bảo hiểm 37 bệnh hiểm nghèo (CI37) [1], nếu Người được bảo hiểm (NĐBH) đơn phương chấm dứt Hợ đồng bảo hiểm (HĐBH), Bên mua bảo hiểm (BMBH) sẽ được CTBH hoàn trả một khoản phí bảo hiểm theo tỷ lệ 80% cho thời hạn bảo hiểm còn lại của HĐBH đã được đóng phí bảo hiểm (trừ khi CTBH đã thanh toán (các) quyền lợi theo các điều khoản và điều kiện của HĐBH này).

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] C37_QT_C4_M10 ★✓</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG IV - Điều kiện chung > 10. Chấm dứt HĐBH]
HĐBH sẽ chấm dứt ngay lập tức khi xảy ra các sự kiện sau, tùy sự kiện nào đến trước:
- HĐBH chấm dứt trước Ngày hết hạn bảo hiểm theo yêu cầu của NĐBH hoặc CTBH được quy định tại mục 4 theo Quy tắc bảo hiểm này;
- HĐBH chấm dứt vào Ngày hết hạn bảo hiểm ghi trên HĐBH;
- Số tiền bảo hiểm của Hợp đồng được thanh toán toàn bộ;
- NĐBH tử vong;
- Các trường hợp khác theo quy định của pháp luật hiện hành.
Trong trường hợp NĐBH đơn phương chấm dứt HĐBH: CTBH sẽ hoàn trả cho BMBH một khoản phí bảo hiểm theo tỷ lệ 80% cho thời hạn bảo hiểm còn lại của Hợp đồng đã được đóng phí bảo hiểm (trừ khi CTBH đã thanh toán (các) quyền lợi theo các điều khoản và điều kiện của Hợp đồng này).
Trong trường hợp CTBH đơn phương chấm dứt HĐBH: CTBH sẽ hoàn trả cho BMBH 100% phí bảo hiểm cho thời hạn bảo hiểm còn lại của Hợp đồng đã được đóng phí bảo hiểm nếu chưa có khiếu nại đòi trả tiền bảo hiểm.
```
</details>

<details><summary>[2] C37_QT_C1_M10 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 10. Hợp đồng bảo hiểm (HĐBH):]
Là hợp đồng bảo hiểm/giấy chứng nhận bảo hiểm (sau đây gọi chung là hợp đồng bảo hiểm) do Bảo hiểm Bảo Việt phát hành dựa trên yêu cầu bảo hiểm và cam kết của Bên mua bảo hiểm/Người được bảo hiểm đã đọc kỹ và hiểu toàn bộ nội dung tại quy tắc bảo hiểm, theo đó Bên mua bảo hiểm/Người được bảo hiểm phải đóng phí bảo hiểm, Bảo hiểm Bảo Việt cung cấp dịch vụ bảo hiểm như được liệt kê trong hợp đồng bảo hiểm/quy tắc bảo hiểm. Giấy yêu cầu bảo hiểm, quy tắc bảo hiểm, hợp đồng bảo hiểm, phụ lục hợp đồng, sửa đổi bổ sung của hợp đồng là những bộ phận cấu thành và không tách rời của hợp đồng bảo hiểm.
```
</details>

<details><summary>[3] C37_QT_C4_M4 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG IV - Điều kiện chung > 4. Nhầm lẫn về độ tuổi và giới tính]
Trong trường hợp độ tuổi hoặc giới tính của NĐBH bị sai lệch do BMBH kê khai không chính xác trong GYCBH, phí bảo hiểm của chương trình bảo hiểm này sẽ được điều chỉnh tương ứng theo độ tuổi; giới tính chính xác dựa trên Số tiền bảo hiểm và điều khoản thanh toán phí bảo hiểm, cụ thể như sau:
Nếu phí bảo hiểm đã thanh toán ít hơn mức phí bảo hiểm thực tế theo độ tuổi và/hoặc giới tính chính xác, CTBH sẽ điều chỉnh Phí bảo hiểm thực tế phải trả tương ứng với độ tuổi; giới tính chính xác và BMBH sẽ trả thêm khoản chênh lệch giữa phí bảo hiểm đã thanh toán và phí bảo hiểm thực tế.
Nếu phí bảo hiểm đã thanh toán cao hơn mức phí bảo hiểm thực tế theo độ tuổi và/ hoặc giới tính chính xác, thì CTBH sẽ trả lại cho BMBH phần dư không bao gồm lãi suất. Nếu căn cứ theo độ tuổi chính xác mà NĐBH bị từ chối bảo hiểm theo các điều khoản và điều kiện của hợp đồng thì HĐBH sẽ chấm dứt và CTBH sẽ trả lại cho BMBH khoản phí đã đóng cho toàn bộ hợp đồng không có lãi suất sau khi trừ phí khám y khoa, (các) khoản nợ và các chi phí liên quan khác, nếu có.
```
</details>

<details><summary>[4] C37_QT_C4_M2 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG IV - Điều kiện chung > 2. Phí bảo hiểm]
- Đối với hợp đồng bảo hiểm cá nhân: Phí bảo hiểm là khoản tiền mà Bên mua bảo hiểm/Người được bảo hiểm phải trả cho Bảo hiểm Bảo Việt dựa trên độ tuổi và giới tính và được quy định theo thời hạn ghi trong Hợp đồng bảo hiểm.
- Đối với hợp đồng bảo hiểm doanh nghiệp/tổ chức:
- Phí bảo hiểm được tính dựa trên độ tuổi và giới tính của từng NĐBH, hoặc:
- Theo đánh giá rủi ro của CTBH tùy từng đối tượng khách hàng để áp dụng tính phí trung bình: Phí bảo hiểm là khoản tiền mà Bên mua bảo hiểm phải trả cho Bảo hiểm Bảo Việt dựa trên độ tuổi trung bình, làm tròn xuống của tổng số người tham gia cùng giới tính và được quy định theo thời hạn ghi trong Hợp đồng bảo hiểm.
Phí bảo hiểm và thời hạn thanh toán phí bảo hiểm ghi trong HĐBH phù hợp với quy định của pháp luật.
```
</details>

<details><summary>[5] C37_QT_C1_M2 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 2. Bên mua bảo hiểm]
Là tổ chức được thành lập và hoạt động hợp pháp tại Việt Nam, hoặc cá nhân tại Việt Nam từ đủ 18 tuổi trở lên có năng lực hành vi dân sự đầy đủ tại thời điểm giao kết hợp đồng bảo hiểm với Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải đáp ứng các điều kiện để mua bảo hiểm theo quy tắc, điều kiện, điều khoản bảo hiểm và đóng phí bảo hiểm cho Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải có quyền lợi có thể được bảo hiểm theo quy định của pháp luật.
Bên mua bảo hiểm có quyền lợi có thể được bảo hiểm đối với những người sau đây:
- Bản thân Bên mua bảo hiểm;
- Bố/mẹ của Bên mua bảo hiểm;
- Vợ/chồng, con của Bên mua bảo hiểm;
- Người có quan hệ nuôi dưỡng và cấp dưỡng hợp pháp với Bên mua bảo hiểm;
- Người khác, nếu người đó đồng ý cho Bên mua bảo hiểm mua bảo hiểm cho mình.
```
</details>

---

## v1-0091 · lookup · medium · BVP

**Câu hỏi:** Theo quy tắc bảo hiểm Bảo Việt An Gia, bệnh di truyền có bao gồm trường hợp di truyền đột biến gen lặn không và việc xác định bệnh phải do ai thực hiện?

**Đáp án chuẩn:** Theo quy tắc bảo hiểm Bảo Việt An Gia, bệnh di truyền bao gồm cả di truyền đột biến gen lặn. Việc xác định bệnh di truyền phải do bác sĩ thực hiện.

**Evidence:** `BVP_QT_C1_M1_K7`

**Câu trả lời:**

> Theo quy tắc bảo hiểm Bảo Việt An Gia, bệnh di truyền bao gồm di truyền đột biến gen lặn [1]. Việc xác định bệnh di truyền phải do bác sĩ thực hiện [1].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] BVP_QT_C1_M1_K7 ★✓</summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 7. Bệnh di truyền]
Là bất kỳ bệnh nào xuất hiện ở những người có cùng huyết thống hay sự chuyển những bệnh lý của bố, mẹ cho con cái thông qua gen của bố, mẹ và/hoặc được truyền từ đời này sang đời khác, từ thế hệ này sang thế hệ khác trong những người có cùng huyết thống, bao gồm cả di truyền đột biến gen lặn. Việc xác định bệnh di truyền phải do bác sĩ thực hiện.
```
</details>

<details><summary>[2] BVP_QT_C1_M1_K5 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 5. Bệnh bẩm sinh/dị tật bẩm sinh]
Là bất kỳ bệnh/dị tật nào được hình thành trên thai nhi trong quá trình mang thai của người mẹ dưới tác động của yếu tố môi trường lên sự phát triển của thai nhi và có thể được cơ quan y tế mô tả dưới nhiều tên gọi khác nhau như "bệnh bẩm sinh, dị tật bẩm sinh, khuyết tật bẩm sinh, bất thường của nhiễm sắc thể". Bệnh/dị tật bẩm sinh có thể được phát hiện trong quá trình mang thai, sinh con của người mẹ hoặc trong quá trình phát triển của Người được bảo hiểm. Việc xác định tình trạng bệnh/dị tật bẩm sinh phải do bác sĩ thực hiện.
```
</details>

<details><summary>[3] BVP_QT_C3_K19-20 </summary>

```text
[Bảo Việt An Gia | Quy tắc | CHƯƠNG III - Các điểm loại trừ chung]
19. Kiểm tra và điều trị các bệnh lây qua đường tình dục như: hạ cam mềm, u hạt bẹn, lậu, giang mai, herpes sinh dục, sùi mào gà (mồng gà), HPV sinh dục, bệnh do rận mu (chấy cua), chlamydia, trichomonas, trùng roi, bệnh hột xoài (u lympho sinh dục), nhiễm cytomegalo virus, u mềm lây ở người trên 10 tuổi, hội chứng suy giảm miễn dịch mắc phải (AIDS), tình trạng và bệnh liên quan đến virut HIV, các bệnh khác lây qua đường tình dục; và mọi biến chứng/hậu quả liên quan đến những bệnh/hội chứng/tình trạng kể trên.
20. Các bệnh bẩm sinh, dị tật bẩm sinh, bệnh di truyền, bệnh dị dạng về gen, và mọi biến chứng/hậu quả liên quan đến những bệnh này; bao gồm những danh mục liệt kê dưới đây và/hoặc các danh mục được liệt kê trong Sửa đổi bổ sung như là một bộ phận đính kèm của quy tắc/hợp đồng bảo hiểm như: bệnh tim bẩm sinh, bệnh Down, hở môi, hở hàm ếch, tích nước trong não, hẹp hậu môn, hẹp/ngắn/dài bao quy đầu, vẹo vách ngăn bẩm sinh, hoặc các bệnh bẩm sinh/dị tật bẩm sinh/bệnh di truyền/bệnh dị dạng về gen khác theo kết luận của bác sĩ.
```
</details>

<details><summary>[4] BVP_QT_C1_M1_K6 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 6. Bệnh có sẵn]
Là tình trạng bệnh tật hoặc thương tật của Người được bảo hiểm có từ trước ngày bắt đầu được nhận bảo hiểm theo hợp đồng bảo hiểm và là bệnh/thương tật mà Người được bảo hiểm:
a. Đã được bác sĩ chẩn đoán hoặc điều trị trước ngày bắt đầu hiệu lực bảo hiểm, và/hoặc
b. Dấu hiệu, triệu chứng của bệnh/thương tật khởi phát trong vòng 36 tháng trước ngày bắt đầu hiệu lực bảo hiểm mà Người được bảo hiểm đã biết hoặc ý thức được cho dù Người được bảo hiểm có thực sự khám, điều trị hay không.
Việc xác định bệnh có sẵn phải căn cứ vào: hồ sơ y tế được lưu trữ tại bệnh viện hoặc cơ sở y tế được thành lập hợp pháp; các tài liệu y khoa được Bộ Y tế và các cơ quan có thẩm quyền ban hành; hoặc các thông tin do Bên mua bảo hiểm, Người được bảo hiểm tự kê khai trên hồ sơ yêu cầu bảo hiểm hoặc phiếu bổ sung thông tin; hoặc lịch sử bồi thường của Người được bảo hiểm.
```
</details>

<details><summary>[5] BVP_QT_C1_M1_K8_TB1 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 8. Bệnh đặc biệt]
| Theo quy tắc bảo hiểm này, những bệnh sau đây được coi là bệnh đặc biệt: | Theo quy tắc bảo hiểm này, những bệnh sau đây được coi là bệnh đặc biệt: |
|---|---|
| 1. Bệnh hệ thần kinh: | Các bệnh viêm hệ thần kinh trung ương (não), teo hệ thống ảnh hưởng lên hệ thần kinh trung ương (teo cơ cột sống và hội chứng liên quan), rối loạn vận động ngoài tháp (Parkison, rối loạn trương lực cơ, rối loạn vận động và ngoại tháp khác), Alzheimer, hội chứng Apallic, hội chứng mất trí nhớ, động kinh, hôn mê, các bệnh bại não và hội chứng liệt khác. |
| 2. Bệnh hệ hô hấp: | Bệnh suy phổi, tràn khí phổi, phổi tắc nghẽn mãn tính (COPD). |
| 3. Bệnh hệ tuần hoàn: | Bệnh của tim, tăng/cao huyết áp, tăng áp lực động mạch vô căn, các bệnh mạch máu não, đột quỵ, và các hậu quả/di chứng của các bệnh này. |
| 4. Bệnh hệ tiêu hóa: | Viêm gan A, viêm gan B, viêm gan C, viêm gan D, xơ gan, suy gan, sỏi mật. |
| 5. Bệnh hệ tiết niệu: | Bệnh của cầu thận, bệnh của ống thận, sỏi thận, sỏi niệu quản, sỏi đường tiết niệu, suy thận, hội chứng thận hư. |
```
</details>

---

## v1-0025 · table · easy · FLX

**Câu hỏi:** Theo biểu phí bảo hiểm du lịch quốc tế Flexi dành cho cá nhân, mức phí cho Chương trình Bạch Kim với thời hạn bảo hiểm từ 15-21 ngày là bao nhiêu?

**Đáp án chuẩn:** Mức phí bảo hiểm cho Chương trình Bạch Kim với thời hạn từ 15-21 ngày là 900.000.

**Evidence:** `FLX_BP_S1_TB1`

**Câu trả lời:**

> Theo biểu phí bảo hiểm du lịch quốc tế Flexi dành cho cá nhân [3], mức phí cho Chương trình Bạch Kim với thời hạn bảo hiểm từ 15-21 ngày là 900.000 đồng.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details><summary>[1] FLX_BP_S1_TB1 ✓</summary>

```text
[Bảo hiểm Du lịch Flexi | Biểu phí | Biểu phí bảo hiểm du lịch quốc tế Flexi dành cho cá nhân]
| Thời hạn bảo hiểm | Chương trình Bạc | Chương trình Vàng | Chương trình Bạch Kim | Chương trình Kim Cương |
|---|---|---|---|---|
| Đến 3 ngày | 149.000 | 180.000 | 300.000 | 450.000 |
| Từ 4-6 ngày | 189.000 | 250.000 | 400.000 | 600.000 |
| Từ 7-10 ngày | 243.000 | 300.000 | 530.000 | 795.000 |
| Từ 11-14 ngày | 297.000 | 400.000 | 700.000 | 1.050.000 |
| Từ 15-21 ngày | 392.000 | 529.000 | 900.000 | 1.337.000 |
| Từ 22-28 ngày | 487.000 | 658.000 | 1.100.000 | 1.624.000 |
| Từ 29-35 ngày | 582.000 | 787.000 | 1.300.000 | 1.911.000 |
| Từ 36-42 ngày | 677.000 | 916.000 | 1.500.000 | 2.198.000 |
| Từ 43-49 ngày | 772.000 | 1.045.000 | 1.700.000 | 2.485.000 |
| Từ 50-56 ngày | 867.000 | 1.174.000 | 1.900.000 | 2.772.000 |
| Từ 57-63 ngày | 962.000 | 1.303.000 | 2.100.000 | 3.059.000 |
| Từ 64-70 ngày | 1.057.000 | 1.432.000 | 2.300.000 | 3.346.000 |
| Từ 71-77 ngày | 1.152.000 | 1.561.000 | 2.500.000 | 3.633.000 |
| Từ 78-84 ngày | 1.247.000 | 1.690.000 | 2.700.000 | 3.920.000 |
```
</details>

<details><summary>[2] FLX_BP_S2_TB1 </summary>

```text
[Bảo hiểm Du lịch Flexi | Biểu phí | Biểu phí bảo hiểm dành cho gia đình]
| Thời hạn bảo hiểm | Chương trình Bạc | Chương trình Vàng | Chương trình Bạch Kim | Chương trình Kim Cương |
|---|---|---|---|---|
| Đến 3 ngày | 298.000 | 360.000 | 600.000 | 900.000 |
| Từ 4-6 ngày | 378.000 | 500.000 | 800.000 | 1.200.000 |
| Từ 7-10 ngày | 486.000 | 600.000 | 1.060.000 | 1.590.000 |
| Từ 11-14 ngày | 594.000 | 800.000 | 1.460.000 | 2.100.000 |
| Từ 15-21 ngày | 784.000 | 1.058.000 | 1.860.000 | 2.674.000 |
| Từ 22-28 ngày | 974.000 | 1.316.000 | 2.260.000 | 3.248.000 |
| Từ 29-35 ngày | 1.164.000 | 1.574.000 | 2.660.000 | 3.822.000 |
| Từ 36-42 ngày | 1.354.000 | 1.832.000 | 3.060.000 | 4.396.000 |
| Từ 43-49 ngày | 1.544.000 | 2.090.000 | 3.460.000 | 4.970.000 |
| Từ 50-56 ngày | 1.734.000 | 2.348.000 | 3.860.000 | 5.544.000 |
| Từ 57-63 ngày | 1.924.000 | 2.606.000 | 4.260.000 | 6.118.000 |
| Từ 64-70 ngày | 2.114.000 | 2.864.000 | 4.660.000 | 6.692.000 |
| Từ 71-77 ngày | 2.304.000 | 3.122.000 | 5.060.000 | 7.266.000 |
| Từ 78-84 ngày | 2.494.000 | 3.380.000 | 5.460.000 | 7.840.000 |
```
</details>

<details open><summary>[3] FLX_BP_S1_TB2 ★</summary>

```text
[Bảo hiểm Du lịch Flexi | Biểu phí | Biểu phí bảo hiểm du lịch quốc tế Flexi dành cho cá nhân]
| Thời hạn bảo hiểm | Chương trình Bạc | Chương trình Vàng | Chương trình Bạch Kim | Chương trình Kim Cương |
|---|---|---|---|---|
| Từ 85-91 ngày | 1.342.000 | 1.819.000 | 2.900.000 | 4.207.000 |
| Từ 92-98 ngày | 1.437.000 | 1.948.000 | 3.100.000 | 4.494.000 |
| Từ 99-105 ngày | 1.532.000 | 2.077.000 | 3.300.000 | 4.781.000 |
| Từ 106-112 ngày | 1.627.000 | 2.206.000 | 3.500.000 | 5.068.000 |
| Từ 113-119 ngày | 1.722.000 | 2.335.000 | 3.700.000 | 5.355.000 |
| Từ 120-126 ngày | 1.817.000 | 2.464.000 | 3.900.000 | 5.642.000 |
| Từ 127-133 ngày | 1.912.000 | 2.539.000 | 4.100.000 | 5.929.000 |
| Từ 134-140 ngày | 2.007.000 | 2.722.000 | 4.300.000 | 6.216.000 |
| Từ 141-147 ngày | 2.102.000 | 2.851.000 | 4.500.000 | 6.503.000 |
| Từ 148-154 ngày | 2.197.000 | 2.980.000 | 4.700.000 | 6.790.000 |
| Từ 155-161 ngày | 2.292.000 | 3.109.000 | 4.900.000 | 7.077.000 |
| Từ 162-168 ngày | 2.387.000 | 3.238.000 | 5.100.000 | 7.364.000 |
| Từ 169-175 ngày | 2.482.000 | 3.367.000 | 5.300.000 | 7.651.000 |
| Từ 176-182 ngày | 2.577.000 | 3.496.000 | 5.500.000 | 7.938.000 |
```
</details>

<details><summary>[4] FLX_BP_S1_TB3 </summary>

```text
[Bảo hiểm Du lịch Flexi | Biểu phí | Biểu phí bảo hiểm du lịch quốc tế Flexi dành cho cá nhân]
| Thời hạn bảo hiểm | Chương trình Bạc | Chương trình Vàng | Chương trình Bạch Kim | Chương trình Kim Cương |
|---|---|---|---|---|
| Từ 183-189 ngày | 2.672.000 | 3.625.000 | 5.700.000 | 8.225.000 |
| Từ 190-196 ngày | 2.767.000 | 3.754.000 | 5.900.000 | 8.512.000 |
| Từ 197-203 ngày | 2.862.000 | 3.883.000 | 6.100.000 | 8.799.000 |
| Từ 204-210 ngày | 2.957.000 | 4.012.000 | 6.300.000 | 9.086.000 |
| Từ 211-217 ngày | 3.052.000 | 4.141.000 | 6.500.000 | 9.373.000 |
| Từ 218-224 ngày | 3.147.000 | 4.270.000 | 6.700.000 | 9.660.000 |
| Từ 225-231 ngày | 3.242.000 | 4.399.000 | 6.900.000 | 9.947.000 |
| Từ 232-238 ngày | 3.337.000 | 4.528.000 | 7.100.000 | 10.234.000 |
| Từ 239-245 ngày | 3.432.000 | 4.657.000 | 7.300.000 | 10.521.000 |
| Từ 246-252 ngày | 3.527.000 | 4.786.000 | 7.500.000 | 10.808.000 |
| Từ 253-259 ngày | 3.622.000 | 4.915.000 | 7.700.000 | 11.095.000 |
| Từ 260-266 ngày | 3.717.000 | 5.044.000 | 7.900.000 | 11.382.000 |
| Từ 267-273 ngày | 3.812.000 | 5.173.000 | 8.100.000 | 11.669.000 |
| Từ 274-280 ngày | 3.907.000 | 5.302.000 | 8.300.000 | 11.956.000 |
```
</details>

<details><summary>[5] FLX_BP_S1_TB4 </summary>

```text
[Bảo hiểm Du lịch Flexi | Biểu phí | Biểu phí bảo hiểm du lịch quốc tế Flexi dành cho cá nhân]
| Thời hạn bảo hiểm | Chương trình Bạc | Chương trình Vàng | Chương trình Bạch Kim | Chương trình Kim Cương |
|---|---|---|---|---|
| Từ 281-287 ngày | 4.002.000 | 5.431.000 | 8.500.000 | 12.243.000 |
| Từ 288-294 ngày | 4.097.000 | 5.560.000 | 8.700.000 | 12.530.000 |
| Từ 295-301 ngày | 4.192.000 | 5.689.000 | 8.900.000 | 12.817.000 |
| Từ 302-308 ngày | 4.287.000 | 5.818.000 | 9.100.000 | 13.104.000 |
| Từ 309-315 ngày | 4.382.000 | 5.947.000 | 9.300.000 | 13.391.000 |
| Từ 316-322 ngày | 4.477.000 | 6.076.000 | 9.500.000 | 13.678.000 |
| Từ 323-329 ngày | 4.572.000 | 6.205.000 | 9.700.000 | 13.965.000 |
| Từ 330-336 ngày | 4.667.000 | 6.334.000 | 9.900.000 | 14.252.000 |
| Từ 337-343 ngày | 4.762.000 | 6.463.000 | 10.100.000 | 14.539.000 |
| Từ 344-350 ngày | 4.857.000 | 6.592.000 | 10.300.000 | 14.826.000 |
| Từ 351-357 ngày | 4.952.000 | 6.721.000 | 10.500.000 | 15.113.000 |
| Từ 358-364 ngày | 5.047.000 | 6.850.000 | 10.700.000 | 15.400.000 |
| Đến 365 ngày | 5.142.000 | 6.979.000 | 10.900.000 | 15.687.000 |
```
</details>

---

## v1-0033 · table · easy · ITC

**Câu hỏi:** Theo bảng quyền lợi bảo hiểm nha khoa của chương trình Bảo Việt Intercare, chi phí kiểm tra răng định kỳ (gồm cạo vôi và đánh bóng) ở chương trình Classic được bảo hiểm với hạn mức bao nhiêu mỗi năm?

**Đáp án chuẩn:** Hạn mức chi trả cho kiểm tra răng định kỳ (bao gồm cạo vôi và đánh bóng) ở chương trình Classic là 2.000.000/ năm.

**Evidence:** `ITC_BQL_S5_TB1`

**Câu trả lời:**

> Theo bảng quyền lợi bảo hiểm nha khoa của chương trình Bảo Việt Intercare, chi phí kiểm tra răng định kỳ (gồm cạo vôi và đánh bóng) ở chương trình Classic được bảo hiểm với hạn mức 2.000.000 đồng mỗi năm [1].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] ITC_BQL_S5_TB1 ★✓</summary>

```text
[Bảo Việt Intercare | Bảng quyền lợi | 3. BẢO HIỂM NHA KHOA]
| CHƯƠNG TRÌNH | SELECT | ESSENTIAL | CLASSIC | GOLD | DIAMOND |
|---|---|---|---|---|---|
| Phạm vi lãnh thổ | Vùng 1 | Vùng 2 | Vùng 3 | Vùng 4 | Vùng 5 |
| Số tiền bảo hiểm cho một thời hạn bảo hiểm và theo các giới hạn phụ dưới đây | 21.000.000 | 21.000.000 | 31.500.000 | 31.500.000 | 31.500.000 |
| a. Các chi phí chăm sóc răng thông thường: • Khám và chẩn đoán bệnh • Lấy cao răng | Kiểm tra răng định kỳ (bao gồm cạo vôi và đánh bóng) 1.000.000/ năm | Kiểm tra răng định kỳ (bao gồm cạo vôi và đánh bóng) 1.000.000/ năm | Kiểm tra răng định kỳ (bao gồm cạo vôi và đánh bóng) 2.000.000/ năm | Kiểm tra răng định kỳ (bao gồm cạo vôi và đánh bóng) 2.000.000/ năm | Kiểm tra răng định kỳ (bao gồm cạo vôi và đánh bóng) 2.000.000/ năm |
| b. Các chi phí điều trị răng: • Trám răng bằng các chất liệu thông thường (amalgam, composite, fuji hoặc chất liệu tương tự) • Nhổ răng sâu. • Nhổ những răng bị ảnh hưởng, răng bị phủ nướu hoặc không thể mọc được • Nhổ chân răng • Lấy u vôi răng (lấy vôi răng sâu dưới nướu) • Phẫu thuật cắt chóp răng • Chữa tủy răng | Tối đa đến Số tiền bảo hiểm | Tối đa đến Số tiền bảo hiểm | Tối đa đến Số tiền bảo hiểm | Tối đa đến Số tiền bảo hiểm | Tối đa đến Số tiền bảo hiểm |
```
</details>

<details><summary>[2] ITC_BQL_S5_TB2 </summary>

```text
[Bảo Việt Intercare | Bảng quyền lợi | 3. BẢO HIỂM NHA KHOA]
| CHƯƠNG TRÌNH | SELECT | ESSENTIAL | CLASSIC | GOLD | DIAMOND |
|---|---|---|---|---|---|
| c. Các chi phí điều trị đặc biệt, làm răng giả • Làm mới hoặc sửa cầu răng, phủ chóp răng, răng giả • Điều trị viêm nướu, viêm nha chu | 21.000.000 | 21.000.000 | 31.500.000 | 31.500.000 | 31.500.000 |
| c. Các chi phí điều trị đặc biệt, làm răng giả • Làm mới hoặc sửa cầu răng, phủ chóp răng, răng giả • Điều trị viêm nướu, viêm nha chu |  |  | Đồng chi trả 50% Đồng chi trả 50% Đồng chi trả 50% Đồng chi trả 50% Đồng chi trả 50% |  |  |
| 19. Bảo hiểm AIDS/ HIV Xảy ra trong thời gian hiệu lực hợp đồng, bao gồm những năm tái tục và xuất hiện sau khi hợp đồng liên tục trong 5 năm kể từ ngày hiệu lực đầu tiên | 105.000.000/ cả đời | 210.000.000/ cả đời | 420.000.000/ cả đời | 525.000.000/ cả đời | 1.050.000.000/ cả đời |
```
</details>

<details><summary>[3] ITC_BQL_S1_TB5 </summary>

```text
[Bảo Việt Intercare | Bảng quyền lợi | BẢNG QUYỀN LỢI BẢO HIỂM BẢO VIỆT INTERCARE]
| QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN |
|---|---|---|---|---|---|
| 10. Chi phí hội chẩn chuyên khoa (tối đa một lần một ngày và 90 ngày/năm) | 4.200.000/ngày | Tối đa đến STBH | Tối đa đến STBH | Tối đa đến STBH | Tối đa đến STBH |
| 11. Chi phí điều trị tai nạn thai kỳ khẩn cấp ngay sau khi tai nạn | Tối đa đến STBH | Tối đa đến STBH | Tối đa đến STBH | Tối đa đến STBH | Tối đa đến STBH |
| 12. Chi phí cấp cứu tai nạn răng khẩn cấp (điều trị nội trú trong vòng 24 giờ tại phòng cấp cứu khẩn cấp của bệnh viện sau khi tai nạn xảy ra) | 21.000.000 | Tối đa đến STBH | Tối đa đến STBH | Tối đa đến STBH | Tối đa đến STBH |
```
</details>

<details><summary>[4] ITC_BQL_S8 </summary>

```text
[Bảo Việt Intercare | Bảng quyền lợi | LƯU Ý CHUNG:]
1. Quy định đồng chi trả với trẻ em đến 3 tuổi:
- Tỷ lệ áp đồng chi trả áp dụng: 70/30 (Bảo Việt chi trả 70%, Người được bảo hiểm tự chi trả 30%)
- Quy định này không áp dụng trong trường hợp Người được bảo hiểm khám và điều trị tại các cơ sở y tế/bệnh viện công lập (trừ các khoa điều trị tự nguyện/điều trị theo yêu cầu của Bệnh viện công lập)
2. Tại các Cơ sở y tế (CSYT) Y học cổ truyền, CSYT Vật lý trị liệu, CSYT Phục hồi chức năng:
- Quyền lợi Trợ cấp ngày nằm viện và Trợ cấp mất giảm thu nhập trong thời gian nghỉ điều trị do tai nạn/ốm bệnh (nếu có) chỉ áp dụng tối đa 05 ngày/đợt nằm viện, không quá 03 đợt nằm viện/năm.
3. Giới hạn giường bệnh:
- Trường hợp Người được bảo hiểm (NĐBH) sử dụng phòng từ 02 giường trở lên, CTBH chỉ chi trả chi phí cho 01 giường bệnh phục vụ cho NĐBH.
4. Với quyền lợi Bảo hiểm Nha khoa:
- Quy định về giới hạn cơ sở y tế điều trị răng tại địa bàn tỉnh Bình Dương, tỉnh Bà Rịa – Vũng Tàu (đơn vị hành chính cấp tỉnh trước 01/07/2025) áp dụng như đối với các tỉnh thành khác ngoài TP. Hà Nội và TP Hồ Chí Minh.
```
</details>

<details><summary>[5] ITC_QT_C2_B_M3 </summary>

```text
[Bảo Việt Intercare | Quy tắc | B. Quyền lợi bảo hiểm bổ sung > 3. Bảo hiểm nha khoa]
Các quyền lợi như được liệt kê dưới đây, chi tiết quy định trong bảng quyền lợi bảo hiểm:
a. Các chi chăm sóc răng thông thường
- Khám và chẩn đoán bệnh
- Lấy cao răng
b. Các chi phí điều trị răng
- Trám răng bằng các chất liệu thông thường (amalgam, composite, fuji hoặc chất liệu tương tự)
- Nhổ răng sâu
- Nhổ những răng bị ảnh hưởng, răng bị phủ nướu hoặc không thể mọc được
- Nhổ chân răng
- Lấy u vôi răng (lấy vôi răng sâu dưới nướu)
- Phẫu thuật cắt chóp răng
- Chữa tủy răng
- Điều trị viêm nướu, viêm nha chu
c. Các chi phí điều trị răng đặc biệt, làm răng giả
- Làm mới hoặc sửa cầu răng, phủ chóp răng, răng giả
```
</details>

---

## v1-0093 · table · medium · BVP

**Câu hỏi:** Theo bảng quyền lợi nội trú của bảo hiểm Bảo Việt An Gia, người tham gia chương trình Bạch Kim được chi trả tối đa bao nhiêu tiền một năm cho chi phí tái khám trong vòng 30 ngày sau khi xuất viện?

**Đáp án chuẩn:** Hạn mức chi trả cho chi phí tái khám trong vòng 30 ngày sau khi xuất viện của chương trình Bạch Kim là 7.500.000/năm.

**Evidence:** `BVP_BQL_S1_TB2`

**Câu trả lời:**

> Theo bảng quyền lợi nội trú của bảo hiểm Bảo Việt An Gia, người tham gia chương trình Bạch Kim được chi trả tối đa 150.000.000/năm cho chi phí tái khám trong vòng 30 ngày sau khi xuất viện [1].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] BVP_BQL_S1_TB2 ★✓</summary>

```text
[Bảo Việt An Gia | Bảng quyền lợi | BẢNG QUYỀN LỢI BẢO HIỂM - BẢO VIỆT AN GIA]
| CHƯƠNG TRÌNH BẢO HIỂM | ĐỒNG | BẠC | VÀNG | BẠCH KIM | KIM CƯƠNG |
|---|---|---|---|---|---|
| I. QUYỀN LỢI BẢO HIỂM CHÍNH – ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, BIẾN CHỨNG THAI SẢN |  |  |  |  |  |
| 3. Chi phí tái khám sau khi xuất viện (trong vòng 30 ngày sau khi xuất viện) | 2.000.000/năm | 3.000.000/năm | 5.000.000/năm | 7.500.000/năm | 10.000.000/năm |
| 4. Dịch vụ xe cứu thương, xe cấp cứu đường bộ | 5.000.000/năm | 5.000.000/năm | 10.000.000/năm | 10.000.000/năm | 10.000.000/năm |
| 5. Chi phí phẫu thuật | 40.000.000/năm | 60.000.000/năm | 100.000.000/năm | 150.000.000/năm | 200.000.000/năm |
| 6. Phục hồi chức năng | 4.000.000/năm | 6.000.000/năm | 10.000.000/năm | 15.000.000/năm | 20.000.000/năm |
| 7. Trợ cấp bệnh viện công (không quá 60 ngày/năm) | 80.000/ngày | 120.000/ngày | 200.000/ngày | 300.000/ngày | 400.000/ngày |
| 8. Trợ cấp mai táng phí trong trường hợp tử vong tại bệnh viện | 1.000.000/vụ | 1.000.000/vụ | 1.000.000/vụ | 1.000.000/vụ | 1.000.000/vụ |
```
</details>

<details><summary>[2] BVP_BQL_S1_TB1 </summary>

```text
[Bảo Việt An Gia | Bảng quyền lợi | BẢNG QUYỀN LỢI BẢO HIỂM - BẢO VIỆT AN GIA]
Đơn vị: Việt Nam đồng
| CHƯƠNG TRÌNH BẢO HIỂM | ĐỒNG | BẠC | VÀNG | BẠCH KIM | KIM CƯƠNG |
|---|---|---|---|---|---|
| I. QUYỀN LỢI BẢO HIỂM CHÍNH – ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, BIẾN CHỨNG THAI SẢN |  |  |  |  |  |
| Tổng hạn mức quyền lợi bảo hiểm chính/ng/năm | 94.000.000/người/năm | 138.000.000/người/năm | 230.000.000/người/năm | 342.000.000/người/năm | 454.000.000/người/năm |
| Phạm vi lãnh thổ | Việt Nam | Việt Nam | Việt Nam | Việt Nam | Việt Nam |
| 1. Chi phí nằm viện (không quá 60 ngày/năm) | 2.000.000/ngày | 3.000.000/ngày | 5.000.000/ngày | 7.500.000/ngày | 10.000.000/ngày |
| • Chi phí phòng và giường, suất ăn theo tiêu chuẩn phòng tại bệnh viện • Chi phí phòng chăm sóc đặc biệt, điều trị cấp cứu | Lên đến 40.000.000/năm | Lên đến 60.000.000/năm | Lên đến 100.000.000/năm | Lên đến 150.000.000/năm | Lên đến 200.000.000/năm |
| • Các chi phí bệnh viện tổng hợp | Lên đến 40.000.000/năm | Lên đến 60.000.000/năm | Lên đến 100.000.000/năm | Lên đến 150.000.000/năm | Lên đến 200.000.000/năm |
| 2. Chi phí khám trước khi nhập viện (trong vòng 30 ngày trước khi nhập viện) | 2.000.000/năm | 3.000.000/năm | 5.000.000/năm | 7.500.000/năm | 10.000.000/năm |
```
</details>

<details><summary>[3] BVP_BQL_S1_TB4 </summary>

```text
[Bảo Việt An Gia | Bảng quyền lợi | BẢNG QUYỀN LỢI BẢO HIỂM - BẢO VIỆT AN GIA]
| CHƯƠNG TRÌNH BẢO HIỂM | ĐỒNG | BẠC | VÀNG | BẠCH KIM | KIM CƯƠNG |
|---|---|---|---|---|---|
| II. QUYỀN LỢI BẢO HIỂM BỔ SUNG |  |  |  |  |  |
| 3. Bảo hiểm Sinh mạng cá nhân | Lựa chọn tham gia từ 20triệu đến 200triệu đồng | Lựa chọn tham gia từ 20triệu đến 300triệu đồng | Lựa chọn tham gia từ 20triệu đến 500triệu đồng | Lựa chọn tham gia từ 20triệu đến 700triệu đồng | Lựa chọn tham gia từ 20triệu đến 1tỷ đồng |
| 4. Bảo hiểm Nha khoa | 2.000.000/năm 1.000.000/lần khám | 2.000.000/năm 1.000.000/lần khám | 5.000.000/năm 2.500.000/lần khám | 10.000.000/năm 5.000.000/lần khám | 15.000.000/năm 7.500.000/lần khám |
| 5. Bảo hiểm Thai sản | Không | 21.000.000/năm | 21.000.000/năm | 21.000.000/năm | 31.500.000/năm |
```
</details>

<details><summary>[4] BVP_BQL_S1_TB3 </summary>

```text
[Bảo Việt An Gia | Bảng quyền lợi | BẢNG QUYỀN LỢI BẢO HIỂM - BẢO VIỆT AN GIA]
| CHƯƠNG TRÌNH BẢO HIỂM | ĐỒNG | BẠC | VÀNG | BẠCH KIM | KIM CƯƠNG |
|---|---|---|---|---|---|
| II. QUYỀN LỢI BẢO HIỂM BỔ SUNG |  |  |  |  |  |
| 1. Điều trị ngoại trú do bệnh, tai nạn, biến chứng thai sản | 6.000.000/năm | 7.000.000/năm | 8.000.000/năm | 10.000.000/năm | 15.000.000/năm |
| Giới hạn/lần khám (không quá 10 lần khám/năm) | 1.200.000/lần | 1.400.000/lần | 1.600.000/lần | 2.000.000/lần | 3.000.000/lần |
| Điều trị vật lý trị liệu (không quá 60 ngày/năm) | 60.000/ngày | 70.000/ngày | 80.000/ngày | 100.000/ngày | 150.000/ngày |
| 2. Bảo hiểm Tai nạn cá nhân | Lựa chọn tham gia từ 20triệu đến 1tỷ đồng | Lựa chọn tham gia từ 20triệu đến 1tỷ đồng | Lựa chọn tham gia từ 20triệu đến 1tỷ đồng | Lựa chọn tham gia từ 20triệu đến 1tỷ đồng | Lựa chọn tham gia từ 20triệu đến 1tỷ đồng |
```
</details>

<details><summary>[5] BVP_QT_C2_M1_A_K2-4 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. QUYỀN LỢI BẢO HIỂM CHÍNH: ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, BIẾN CHỨNG THAI SẢN > A. Quyền lợi bảo hiểm]
2. Chi phí khám trước khi nhập viện (trong vòng 30 ngày trước khi nhập viện)
Bảo hiểm Bảo Việt sẽ chi trả cho Người được bảo hiểm các chi phí khám, kiểm tra, siêu âm, chụp chiếu, xét nghiệm cơ bản và tiền thuốc theo chỉ định của bác sĩ, liên quan trực tiếp đến bệnh/thương tật cần phải nhập viện, và là cơ sở trực tiếp để bác sĩ đưa ra chỉ định nhập viện để điều trị. Chi phí khám trước khi nhập viện chỉ được chấp nhận một lần gần nhất được thực hiện trong vòng 30 ngày trước khi nhập viện.
3. Chi phí tái khám sau khi xuất viện (trong vòng 30 ngày sau khi xuất viện)
Bảo hiểm Bảo Việt sẽ chi trả cho Người được bảo hiểm các chi phí y tế
phát sinh theo chỉ định của bác sĩ ngay khi Người được bảo hiểm xuất viện
và có liên quan trực tiếp đến đợt điều trị nội trú trước đó. Các chi phí này
bao gồm chi phí khám, xét nghiệm, chẩn đoán hình ảnh và thuốc phát sinh
trong vòng 30 ngày kể từ ngày Người được bảo hiểm xuất viện.
4. Dịch vụ xe cứu thương, xe cấp cứu đường bộ
Bảo hiểm Bảo Việt sẽ chi trả cho chi phí sử dụng xe cứu thương/xe cấp cứu bằng đường bộ (không phải là dịch vụ vận chuyển bằng đường hàng không) trong trường hợp Người được bảo hiểm trong tình trạng bệnh/tai nạn nguy kịch ảnh hưởng đến tính mạng buộc phải đưa Người được bảo hiểm đến bệnh viện/phòng khám gần nhất hoặc từ bệnh viện này đến bệnh viện khác theo chỉ định của bác sĩ.
```
</details>

---

## v1-0097 · table · hard · BVP

**Câu hỏi:** Theo bảng tỷ lệ trả tiền thương tật bộ phận vĩnh viễn của bảo hiểm Bảo Việt An Gia, trường hợp người được bảo hiểm bị tổn thương ở chi trên dẫn đến mất trọn ngón giữa hoặc ngón đeo nhẫn và bao gồm cả đốt bàn thì tỷ lệ chi trả là bao nhiêu phần trăm?

**Đáp án chuẩn:** Tỷ lệ trả tiền bảo hiểm cho trường hợp này là 18%.

**Evidence:** `BVP_QT_PL1_TB3`

**Câu trả lời:**

> [2][3]
> 
> Tỷ lệ chi trả là 18% [3].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details><summary>[1] BVP_QT_PL1_TB3 ✓</summary>

```text
[Bảo Việt An Gia | Quy tắc | PHỤ LỤC 1]
| STT | Quyền lợi | Tỷ lệ trả tiền |
|---|---|---|
| III – THƯƠNG TẬT BỘ PHẬN VĨNH VIỄN |  |  |
| CHI TRÊN |  |  |
| 22 | Mất nửa đốt ngoài của ngón cái | 07% |
| 23 | Mất trọn ngón trỏ và đốt bàn | 20% |
| 24 | Mất trọn ngón trỏ | 18% |
| 25 | Mất hai đốt 2 và 3 của ngón trỏ | 10% |
| 26 | Mất đốt 3 của ngón trỏ | 08% |
| 27 | Mất trọn ngón giữa hoặc ngón đeo nhẫn (bao gồm cả đốt bàn) | 18% |
| 28 | Mất trọn ngón giữa hoặc ngón đeo nhẫn | 15% |
| 29 | Mất hai đốt 2 và 3 của ngón giữa hoặc ngón đeo nhẫn | 08% |
| 30 | Mất đốt 3 của ngón giữa hoặc ngón đeo nhẫn | 04% |
| 31 | Mất cả ngón út và đốt bàn | 15% |
| 32 | Mất trọn ngón út | 10% |
| 33 | Mất hai đốt 2 và 3 của ngón út | 08% |
| 34 | Mất đốt 3 của ngón út | 04% |
| 35 | Cứng khớp bả vai | 30% |
| 36 | Cứng khớp khuỷu tay | 25% |
| 37 | Cứng khớp cổ tay | 20% |
| 38 | Gãy tay can lệch hoặc mất xương làm chi ngắn trên 3cm và chức năng quay sấp ngửa hạn chế hoặc tạo thành khớp giả | 25% |
```
</details>

<details open><summary>[2] BVP_QT_PL1_TB2 ★</summary>

```text
[Bảo Việt An Gia | Quy tắc | PHỤ LỤC 1]
| STT | Quyền lợi | Tỷ lệ trả tiền |
|---|---|---|
| III – THƯƠNG TẬT BỘ PHẬN VĨNH VIỄN |  |  |
| CHI TRÊN |  |  |
| 5 | Mất một cánh tay từ vai xuống (Tháo khớp vai) | 75% |
| 6 | Cắt cụt cánh tay từ dưới vai xuống | 70% |
| 7 | Cắt cụt một cánh tay từ khuỷu xuống (Tháo khớp khuỷu) | 65% |
| 8 | Mất trọn một bàn tay hoặc toàn bộ cả 5 ngón tay | 60% |
| 9 | Mất đồng thời cả bốn ngón tay của một bàn tay | 40% |
| 10 | Mất đồng thời cả ngón cái và ngón trỏ | 35% |
| 11 | Mất 3 ngón: ngón trỏ, ngón giữa và ngón đeo nhẫn | 30% |
| 12 | Mất ngón cái và 2 ngón khác | 35% |
| 13 | Mất ngón cái và một ngón khác | 30% |
| 14 | Mất ngón trỏ và hai ngón khác | 35% |
| 15 | Mất ngón trỏ và một ngón khác | 25% |
| 16 | Mất ngón giữa và ngón đeo nhẫn | 19% |
| 17 | Mất ngón giữa và ngón út | 18% |
| 18 | Mất ngón đeo nhẫn và ngón út | 18% |
| 19 | Mất trọn ngón cái và đốt bàn | 25% |
| 20 | Mất trọn ngón cái | 20% |
| 21 | Mất cả đốt ngoài của ngón cái | 10% |
```
</details>

<details open><summary>[3] BVP_QT_PL1_TB5 ★</summary>

```text
[Bảo Việt An Gia | Quy tắc | PHỤ LỤC 1]
| STT | Quyền lợi | Tỷ lệ trả tiền |
|---|---|---|
| III – THƯƠNG TẬT BỘ PHẬN VĨNH VIỄN |  |  |
| CHI DƯỚI |  |  |
| 54 | Mất một ngón cái và ngón 2 | 20% |
| 55 | Mất một ngón cái và một ngón khác (trừ ngón 2) | 16% |
| 56 | Mất một ngón 2 và ngón khác (trừ ngón cái) | 11% |
| 57 | Mất hai ngón 3 và 4; hoặc mất hai ngón 3 và 5; hoặc mất hai ngón 4 và 5 | 6% |
| 58 | Mất một ngón cái | 15% |
| 59 | Mất một ngón ngoài ngón cái | 10% |
| 60 | Mất một đốt ngoài của ngón cái | 8% |
| 61 | Mất một đốt của ngón khác | 1% |
| 62 | Mất hai đốt của ngón khác | 2% |
| 63 | Cứng khớp hông | 45% |
| 64 | Cứng khớp gối | 30% |
| 65 | Mất phần lớn xương bánh chè và giới hạn nhiều khả năng duỗi cẳng chân trên đùi | 45% |
| 66 | Gãy chân can lệch hoặc mất xương làm ngắn chi |  |
|  | Gãy chân can lệch hoặc mất xương làm ngắn chi: Ít nhất 5 cm | 40% |
|  | Gãy chân can lệch hoặc mất xương làm ngắn chi: Từ 3 cm đến 5 cm | 35% |
| 67 | Liệt hoàn toàn dây thần kinh hông khoeo ngoài | 35% |
| 68 | Liệt hoàn toàn dây thần kinh hông khoeo trong | 25% |
```
</details>

<details><summary>[4] BVP_QT_PL1_P11 </summary>

```text
[Bảo Việt An Gia | Quy tắc | PHỤ LỤC 1]
| STT | Quyền lợi | Tỷ lệ trả tiền |
|---|---|---|
| III – THƯƠNG TẬT BỘ PHẬN VĨNH VIỄN |  |  |
| MẶT |  |  |
| 115 | Mất toàn bộ xương hàm trên và một phần xương hàm dưới từ cành cao trở xuống: |  |
|  | - Khác bên | 80% |
|  | - Cùng bên | 70% |
| 116 | Mất toàn bộ xương hàm trên hoặc dưới | 70% |
| 117 | Mất một phần xương hàm trên hoặc một phần xương hàm dưới từ 1/3 đến 1/2 bị mất từ cành cao trở xuống | 35% |
| 118 | Mất 3/4 lưỡi, còn gốc lưỡi (từ đường gai V trở ra) | 75% |
| 119 | Mất 2/3 lưỡi từ đầu lưỡi | 50% |
| 120 | Mất 1/3 lưỡi ảnh hưởng đến phát âm | 15% |
| 121 | Mất một phần nhỏ lưỡi (dưới 1/3) ảnh hưởng đến phát âm | 10% |
NGUYÊN TẮC XÉT TRẢ TIỀN BẢO HIỂM
a) Trường hợp có nhiều thương tật ở cùng một bộ phận cơ thể, tổng số tiền trả cho các thương tật không được vượt quá tỉ lệ mất bộ phận cơ thể đó.
b) Trường hợp Người được bảo hiểm bị một thương tật vĩnh viễn mà thương tật vĩnh viễn này được liệt kê trong nhiều quyền lợi chi trả khác nhau, thì mức chi trả cho phần thương tật nằm trong hạng mục nào cao hơn (hoặc cao nhất) sẽ được áp dụng. Nếu quyền lợi bảo hiểm đã được chi trả cho việc mất toàn bộ bộ phận cơ thể, thì sẽ không còn quyền lợi chi trả cho việc mất một phần của bộ phận cơ thể đó nữa.
```
</details>

<details><summary>[5] BVP_QT_PL1_TB4 </summary>

```text
[Bảo Việt An Gia | Quy tắc | PHỤ LỤC 1]
| STT | Quyền lợi | Tỷ lệ trả tiền |
|---|---|---|
| III – THƯƠNG TẬT BỘ PHẬN VĨNH VIỄN |  |  |
| CHI DƯỚI |  |  |
| 39 | Mất một chân từ háng xuống (Tháo khớp không một đùi) | 75% |
| 40 | Cắt cụt một đùi |  |
|  | - Cắt cụt một đùi 1/3 trên | 70% |
|  | - Cắt cụt một đùi 1/3 giữa hoặc dưới | 55% |
| 41 | Cắt cụt một chân từ gối xuống (Tháo khớp gối) | 60% |
| 42 | Tháo khớp cổ chân hoặc mất một bàn chân | 55% |
| 43 | Mất xương sên | 35% |
| 44 | Mất xương gót | 35% |
| 45 | Mất đoạn xương chày, mác gây khớp giả cẳng chân | 35% |
| 46 | Mất đoạn xương mác | 20% |
| 47 | Mất mắt cá chân: Mắt cá ngoài | 10% |
| 48 | Mất mắt cá chân: Mắt cá trong | 15% |
| 49 | Mất cả năm ngón chân | 45% |
| 50 | Mất bốn ngón chân bao gồm cả ngón cái | 38% |
| 51 | Mất bốn ngón chân không bao gồm ngón cái | 35% |
| 52 | Mất ba ngón chân không bao gồm ngón cái | 25% |
| 53 | Mất ba ngón chân bao gồm cả ngón cái | 30% |
```
</details>

---

## v1-0100 · table · medium · BTB

**Câu hỏi:** Theo biểu phí quyền lợi bảo hiểm chính của Bảo hiểm Bảo Việt Tâm Bình, người tham gia 45 tuổi lựa chọn chương trình Toàn diện cần đóng mức phí bảo hiểm là bao nhiêu?

**Đáp án chuẩn:** Mức phí bảo hiểm cho người ở độ tuổi 41 đến 50 tuổi tham gia chương trình Toàn diện là 1.448.000.

**Evidence:** `BTB_BP_S1_TB1`

**Câu trả lời:**

> [4] Theo biểu phí quyền lợi bảo hiểm chính của Bảo hiểm Bảo Việt Tâm Bình, người tham gia 45 tuổi lựa chọn chương trình Toàn diện cần đóng mức phí bảo hiểm là 1.448.000 đồng.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details><summary>[1] BTB_BP_S1_TB2 </summary>

```text
[Bảo Việt Tâm Bình | Biểu phí | BIỂU PHÍ BẢO HIỂM BẢO VIỆT TÂM BÌNH]
| Chương trình bảo hiểm | Cơ bản | Mở rộng | Nâng cao | Toàn diện | Ưu việt |
|---|---|---|---|---|---|
| Quyền lợi bổ sung - Bảo hiểm Tai nạn cá nhân |  |  |  |  |  |
| Số tiền bảo hiểm Nhóm tuổi | 20.000.000 | 30.000.000 | 50.000.000 | 70.000.000 | 100.000.000 |
| Đến 6 tuổi (phí bảo hiểm theo số tiền) | 116.000 | 176.000 | 292.000 | 408.000 | 580.000 |
| 7 tuổi đến 18 tuổi (phí bảo hiểm theo số tiền) | 104.000 | 156.000 | 260.000 | 364.000 | 520.000 |
| 19 tuổi đến 40 tuổi (phí bảo hiểm theo số tiền) | 100.000 | 152.000 | 252.000 | 352.000 | 500.000 |
| 41 tuổi đến 50 tuổi (phí bảo hiểm theo số tiền) | 108.000 | 164.000 | 272.000 | 380.000 | 540.000 |
| 51 tuổi đến 65 tuổi (phí bảo hiểm theo số tiền) | 112.000 | 172.000 | 284.000 | 400.000 | 568.000 |
```
</details>

<details><summary>[2] BTB_BP_S1_P4 </summary>

```text
[Bảo Việt Tâm Bình | Biểu phí | BIỂU PHÍ BẢO HIỂM BẢO VIỆT TÂM BÌNH]
| Chương trình bảo hiểm | Cơ bản | Mở rộng | Nâng cao | Toàn diện | Ưu việt |
|---|---|---|---|---|---|
| Quyền lợi bổ sung - Điều trị ngoại trú do bệnh. tai nạn. biến chứng thai sản. điều trị răng |  |  |  |  |  |
| Số tiền bảo hiểm Nhóm tuổi | 3.000.000 | 3.000.000 | 6.000.000 | 8.000.000 | 10.000.000 |
| Đến 6 tuổi (phí bảo hiểm theo số tiền) | 408.000 | 408.000 | 816.000 | 1.084.000 | 1.356.000 |
| 7 tuổi đến 18 tuổi (phí bảo hiểm theo số tiền) | 320.000 | 320.000 | 644.000 | 856.000 | 1.072.000 |
| 19 tuổi đến 40 tuổi (phí bảo hiểm theo số tiền) | 300.000 | 300.000 | 600.000 | 800.000 | 1.000.000 |
| 41 tuổi đến 50 tuổi (phí bảo hiểm theo số tiền) | 344.000 | 344.000 | 684.000 | 916.000 | 1.144.000 |
| 51 tuổi đến 65 tuổi (phí bảo hiểm theo số tiền) | 384.000 | 384.000 | 772.000 | 1.028.000 | 1.284.000 |
Đơn vị: Việt Nam Đồng
```
</details>

<details><summary>[3] BTB_BP_S1_TB3 </summary>

```text
[Bảo Việt Tâm Bình | Biểu phí | BIỂU PHÍ BẢO HIỂM BẢO VIỆT TÂM BÌNH]
| Chương trình bảo hiểm | Cơ bản | Mở rộng | Nâng cao | Toàn diện | Ưu việt |
|---|---|---|---|---|---|
| Quyền lợi bổ sung - Bảo hiểm Sinh mạng và Tai nạn cá nhân |  |  |  |  |  |
| Số tiền bảo hiểm Nhóm tuổi | 20.000.000 | 30.000.000 | 50.000.000 | 70.000.000 | 100.000.000 |
| Đến 6 tuổi (phí bảo hiểm theo số tiền) | 132.000 | 196.000 | 324.000 | 456.000 | 652.000 |
| 7 tuổi đến 18 tuổi (phí bảo hiểm theo số tiền) | 116.000 | 172.000 | 288.000 | 404.000 | 576.000 |
| 19 tuổi đến 40 tuổi (phí bảo hiểm theo số tiền) | 108.000 | 164.000 | 272.000 | 384.000 | 548.000 |
| 41 tuổi đến 50 tuổi (phí bảo hiểm theo số tiền) | 120.000 | 176.000 | 296.000 | 416.000 | 592.000 |
| 51 tuổi đến 65 tuổi (phí bảo hiểm theo số tiền) | 128.000 | 188.000 | 316.000 | 444.000 | 632.000 |
```
</details>

<details open><summary>[4] BTB_BP_S1_TB1 ★✓</summary>

```text
[Bảo Việt Tâm Bình | Biểu phí | BIỂU PHÍ BẢO HIỂM BẢO VIỆT TÂM BÌNH]
(Ban hành kèm theo Quyết định số 6038/QĐ-BHBV ngày 27/06/2025 của Tổng Giám đốc Tổng Công ty Bảo hiểm Bảo Việt)
| Chương trình bảo hiểm | Cơ bản | Mở rộng | Nâng cao | Toàn diện | Ưu việt |
|---|---|---|---|---|---|
| Quyền lợi bảo hiểm chính - Điều trị nội trú do bệnh. tai nạn. thai sản |  |  |  |  |  |
| Số tiền bảo hiểm Nhóm tuổi | 60.000.000 | 100.000.000 | 160.000.000 | 220.000.000 | 330.000.000 |
| Đến 6 tuổi (phí bảo hiểm theo số tiền) | 863.000 | 1.510.000 | 1.972.000 | 2.414.000 | 3.198.000 |
| 7 tuổi đến 18 tuổi (phí bảo hiểm theo số tiền) | 535.000 | 936.000 | 1.301.000 | 1.593.000 | 2.111.000 |
| 19 tuổi đến 40 tuổi (phí bảo hiểm theo số tiền) | 584.000 | 1.021.000 | 1.420.000 | 1.738.000 | 2.303.000 |
| 41 tuổi đến 50 tuổi (phí bảo hiểm theo số tiền) | 486.000 | 851.000 | 1.183.000 | 1.448.000 | 1.919.000 |
| 51 tuổi đến 65 tuổi (phí bảo hiểm theo số tiền) | 596.000 | 1.042.000 | 1.449.000 | 1.774.000 | 2.350.000 |
```
</details>

<details><summary>[5] BTB_BQL_S2_TB8 </summary>

```text
[Bảo Việt Tâm Bình | Bảng quyền lợi | BẢO VIỆT TÂM BÌNH]
| CHƯƠNG TRÌNH BẢO HIỂM | CƠ BẢN | MỞ RỘNG | NÂNG CAO | TOÀN DIỆN | ƯU VIỆT |
|---|---|---|---|---|---|
| 2.3. Điều trị răng: |  |  |  |  |  |
| • Khám, chụp X.Q; • Viêm nướu (lợi), nha chu; • Trám răng bằng chất liệu thông thường như amalgam, composite, fuji...; • Điều trị tuỷ răng; • Cạo vôi răng (lấy cao răng) giới hạn 400.000/ người/năm; và • Nhổ răng bệnh lý (bao gồm tiểu phẫu, phẫu thuật). | Chi trả theo chi phí thực tế, tối đa 600.000/năm | Chi trả theo chi phí thực tế, tối đa 600.000/năm | Chi trả theo chi phí thực tế, tối đa 900.000/năm | Chi trả theo chi phí thực tế, tối đa 1.200.000/năm | Chi trả theo chi phí thực tế, tối đa 1.500.000/năm |
| 3. Trợ cấp mất giảm thu nhập/trợ cấp lương trong thời gian nghỉ điều trị do tai nạn và/hoặc ốm bệnh (áp dụng với hợp đồng bảo hiểm tổ chức) (QLBS 3) | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương |
```
</details>

---

## v1-0103 · table · easy · FLX

**Câu hỏi:** Trong gói Bảo hiểm Du lịch Flexi, mức quyền lợi tối đa cho chi phí mai táng thuộc Chương trình Vàng (Gold Plan) là bao nhiêu?

**Đáp án chuẩn:** Theo bảng quyền lợi của Bảo hiểm Du lịch Flexi, chi phí mai táng ở Chương trình Vàng (Gold Plan) có hạn mức là 250.000.000.

**Evidence:** `FLX_BQL_S2_TB1`

**Câu trả lời:**

> Mức quyền lợi tối đa cho chi phí mai táng thuộc Chương trình Vàng (Gold Plan) là 2.000.000.000 VNĐ [1].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] FLX_BQL_S2_TB1 ★✓</summary>

```text
[Bảo hiểm Du lịch Flexi | Bảng quyền lợi | DU LỊCH FLEXI]
| MỤC | QUYỀN LỢI | Chương trình Bạc (Silver Plan) | Chương trình Vàng (Gold Plan) | Chương trình Bạch Kim (Platinum Plan) | Chương trình Kim Cương (Diamond Plan) |
|---|---|---|---|---|---|
| MỤC 2 | Chi phí y tế và các chi phí khác |  |  |  |  |
| MỤC 2 | Quyền lợi A - Chi phí y tế (*): Bao gồm các chi phí y tế tiếp theo phát sinh trong vòng 1 tháng kể từ khi trở về Việt Nam | 1.000.000.000 | 2.000.000.000 | 3.000.000.000 | 4.000.000.000 |
| MỤC 2 | Quyền lợi B - Trợ cấp nằm viện: Cung cấp trợ cấp ngày cho mỗi ngày trọn vẹn Người được bảo hiểm nằm viện (tối đa 20 ngày/HĐBH) | Không áp dụng | 500.000/ngày | 750.000/ngày | 1.000.000/ngày |
| MỤC 3 | Chi phí vận chuyển y tế cấp cứu: Bao gồm chi phí cho việc vận chuyển y tế, được đánh giá là cần thiết, đến một địa điểm mới | 1.000.000.000 | 2.000.000.000 | 3.000.000.000 | 4.000.000.000 |
| MỤC 3 | i) Hỗ trợ người đi cùng | 100.000.000 | 100.000.000 | 100.000.000 | 100.000.000 |
| MỤC 3 | ii) Hồi hương thi hài | 1.000.000.000 | 2.000.000.000 | 3.000.000.000 | 4.000.000.000 |
| MỤC 3 | iii) Chi phí mai táng | 200.000.000 | 250.000.000 | 300.000.000 | 400.000.000 |
| MỤC 3 | iv) Hồi hương trẻ em (***) | 100.000.000 | 100.000.000 | 100.000.000 | 100.000.000 |
```
</details>

<details><summary>[2] FLX_QT_C2_M3_C </summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | III. VẬN CHUYỂN CẤP CỨU > C. Chi phí mai táng]
Trong trường hợp Người được bảo hiểm tử vong do tai nạn hoặc bệnh/ốm đau thuộc phạm vi bảo hiểm trong chuyến đi và không thuộc các điểm loại trừ chung, Công ty bảo hiểm sẽ chi trả cho các chi phí mai táng hợp lý (trừ chi phí chôn cất hoặc hỏa táng) ngoài lãnh thổ Việt Nam tại nước mà Người được bảo hiểm tử vong bao gồm chi phí cho dịch vụ mai táng, chi phí quan tài, chi phí vận chuyển thi thể từ nơi qua đời tới nơi tổ chức lễ tang, chi phí dịch vụ tang lễ khác liên quan tới công tác tổ chức tang lễ. Tổng số tiền chi trả tối đa theo hạn mức của chương trình bảo hiểm đã lựa chọn.
Công ty bảo hiểm có thể trực tiếp chi trả các chi phí mai táng cho công ty cung cấp dịch vụ tang lễ (hoặc cơ sở tương tự) hoặc chi trả cho Người thụ hưởng sau khi Người thụ hưởng cung cấp các chứng từ cần thiết và hợp lệ, bao gồm hợp đồng hoặc thỏa thuận sử dụng dịch vụ, hóa đơn/biên lai, chứng từ thanh toán và chứng từ khác (nếu có).
Điều kiện chi trả áp dụng cho Mục 3 – Vận chuyển cấp cứu:
- Các quyền lợi bảo hiểm chỉ được chi trả khi rủi ro do tai nạn, bệnh/ốm đau xảy ra sau thời gian khởi hành thực tế của phương tiện vận chuyển của Người được bảo hiểm để bắt đầu thực hiện Chuyến đi và vẫn trong thời hạn bảo hiểm.
- Công ty bảo hiểm chi trả cho các chi phí phát sinh trong vòng 30 ngày kể từ ngày xảy ra sự kiện bảo hiểm trên.
```
</details>

<details><summary>[3] FLX_QT_C2_M1_B </summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | I. TAI NẠN CÁ NHÂN > B. Tử vong do tai nạn khi tham gia phương tiện giao thông công cộng]
Đơn vị: VNĐ
| QUYỀN LỢI BẢO HIỂM | Chương trình BẠC | Chương trình VÀNG | Chương trình BẠCH KIM | Chương trình KIM CƯƠNG |
|---|---|---|---|---|
| Tử vong tai nạn khi tham gia phương tiện giao thông công cộng | 2.000.000.000 | 4.000.000.000 | 6.000.000.000 | 8.000.000.000 |
Các điều kiện:
1. Quyền lợi bảo hiểm này chỉ được chi trả khi sự kiện bảo hiểm xảy ra sau thời gian khởi hành thực tế của phương tiện vận chuyển của Người được bảo hiểm để thực hiện Chuyến đi và thuộc phạm vi bảo hiểm. Đối với quyền lợi Tử vong do tai nạn, Công ty bảo hiểm chỉ chi trả quyền lợi khi thời điểm tử vong nằm trong thời hạn bảo hiểm.
2. Nếu người được bảo hiểm là trẻ em tại thời điểm tai nạn, số tiền chi trả tối đa sẽ giới hạn ở mức 20% mức trách nhiệm bảo hiểm cho quyền lợi này.
3. Nếu người được bảo hiểm từ 70 tuổi trở lên tại thời điểm xảy ra tai nạn, số tiền chi trả tối đa sẽ giới hạn ở mức 30% mức trách nhiệm bảo hiểm cho quyền lợi này.
```
</details>

<details><summary>[4] FLX_QT_C2_M1_A </summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | I. TAI NẠN CÁ NHÂN > A. Tử vong do tai nạn không bao gồm trường hợp tham gia phương tiện giao thông công cộng:]
Đơn vị: VNĐ
| QUYỀN LỢI BẢO HIỂM | Chương trình BẠC | Chương trình VÀNG | Chương trình BẠCH KIM | Chương trình KIM CƯƠNG |
|---|---|---|---|---|
| Tử Vong do tai nạn không bao gồm trường hợp tham gia phương tiện giao thông công cộng | 1.000.000.000 | 2.000.000.000 | 3.000.000.000 | 4.000.000.000 |
Các điều kiện:
1. Quyền lợi bảo hiểm này chỉ được chi trả khi sự kiện bảo hiểm xảy ra sau thời gian khởi hành thực tế của phương tiện vận chuyển của Người được bảo hiểm để thực hiện Chuyến đi và thuộc phạm vi bảo hiểm. Đối với quyền lợi Tử vong do tai nạn, Công ty bảo hiểm chỉ chi trả quyền lợi khi thời điểm tử vong nằm trong thời hạn bảo hiểm.
2. Nếu người được bảo hiểm là trẻ em tại thời điểm tai nạn, số tiền chi trả tối đa sẽ giới hạn ở mức 20% mức trách nhiệm bảo hiểm cho quyền lợi này.
3. Nếu người được bảo hiểm từ 70 tuổi trở lên tại thời điểm xảy ra tai nạn, số tiền chi trả tối đa sẽ giới hạn ở mức 30% mức trách nhiệm bảo hiểm cho quyền lợi này.
```
</details>

<details><summary>[5] FLX_BQL_S2_TB3 </summary>

```text
[Bảo hiểm Du lịch Flexi | Bảng quyền lợi | DU LỊCH FLEXI]
| MỤC | QUYỀN LỢI | Chương trình Bạc (Silver Plan) | Chương trình Vàng (Gold Plan) | Chương trình Bạch Kim (Platinum Plan) | Chương trình Kim Cương (Diamond Plan) |
|---|---|---|---|---|---|
| MỤC 6 | Tiền mang theo và Giấy tờ thông hành: Cung cấp quyền lợi bảo hiểm trong trường hợp bị mất Tiền và Giấy tờ thông hành mang theo do mất cắp hoặc thiên tai cộng với chi phí ăn ở đi lại phát sinh thêm | Không áp dụng | Tiền mang theo 4.000.000, các chi phí khác 20.000.000 | Tiền mang theo 6.000.000, các chi phí khác 60.000.000 | Tiền mang theo 8.000.000, các chi phí khác 80.000.000 |
| MỤC 7 | Trách nhiệm cá nhân: Cung cấp quyền lợi bảo hiểm trong trường hợp bị khiếu nại về trách nhiệm pháp lý đối với thương tật thân thể hoặc hư hỏng tài sản do một sự kiện xảy ra trong chuyến đi | Không áp dụng | 4.000.000.000 | 4.000.000.000 | 4.000.000.000 |
| MỤC 8 | Chuyến đi bị trì hoãn: Cung cấp quyền lợi bảo hiểm trong trường hợp hãng vận tải công cộng xuất phát chậm ít nhất 8 tiếng | Không áp dụng | 2.000.000 cho mỗi 8 tiếng và 10.000.000 tổng cộng | 2.000.000 cho mỗi 8 tiếng và 20.000.000 tổng cộng | 2.000.000 cho mỗi 8 tiếng và 30.000.000 tổng cộng |
| MỤC 9 | Mất tiền đặt cọc hay hủy bỏ chuyến đi: Cung cấp quyền lợi bảo hiểm đối với các khoản đặt cọc và thanh toán không được hoàn lại do hủy chuyến đi vì các lý do được nêu trong đơn bảo hiểm | Không áp dụng | 100.000.000 | 150.000.000 | 200.000.000 |
```
</details>

---

## v1-0104 · table · easy · BVP

**Câu hỏi:** Trong gói bảo hiểm Bảo Việt An Gia, chi phí nằm viện mỗi ngày đối với chương trình Vàng được chi trả tối đa là bao nhiêu?

**Đáp án chuẩn:** Theo chương trình Vàng của bảo hiểm Bảo Việt An Gia, quyền lợi chi phí nằm viện là 5.000.000/ngày (áp dụng không quá 60 ngày/năm).

**Evidence:** `BVP_BQL_S1_TB1`

**Câu trả lời:**

> Theo tài liệu [1], chi phí nằm viện mỗi ngày đối với chương trình Vàng được chi trả tối đa là 5.000.000 đồng/ngày.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] BVP_BQL_S1_TB1 ★✓</summary>

```text
[Bảo Việt An Gia | Bảng quyền lợi | BẢNG QUYỀN LỢI BẢO HIỂM - BẢO VIỆT AN GIA]
Đơn vị: Việt Nam đồng
| CHƯƠNG TRÌNH BẢO HIỂM | ĐỒNG | BẠC | VÀNG | BẠCH KIM | KIM CƯƠNG |
|---|---|---|---|---|---|
| I. QUYỀN LỢI BẢO HIỂM CHÍNH – ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, BIẾN CHỨNG THAI SẢN |  |  |  |  |  |
| Tổng hạn mức quyền lợi bảo hiểm chính/ng/năm | 94.000.000/người/năm | 138.000.000/người/năm | 230.000.000/người/năm | 342.000.000/người/năm | 454.000.000/người/năm |
| Phạm vi lãnh thổ | Việt Nam | Việt Nam | Việt Nam | Việt Nam | Việt Nam |
| 1. Chi phí nằm viện (không quá 60 ngày/năm) | 2.000.000/ngày | 3.000.000/ngày | 5.000.000/ngày | 7.500.000/ngày | 10.000.000/ngày |
| • Chi phí phòng và giường, suất ăn theo tiêu chuẩn phòng tại bệnh viện • Chi phí phòng chăm sóc đặc biệt, điều trị cấp cứu | Lên đến 40.000.000/năm | Lên đến 60.000.000/năm | Lên đến 100.000.000/năm | Lên đến 150.000.000/năm | Lên đến 200.000.000/năm |
| • Các chi phí bệnh viện tổng hợp | Lên đến 40.000.000/năm | Lên đến 60.000.000/năm | Lên đến 100.000.000/năm | Lên đến 150.000.000/năm | Lên đến 200.000.000/năm |
| 2. Chi phí khám trước khi nhập viện (trong vòng 30 ngày trước khi nhập viện) | 2.000.000/năm | 3.000.000/năm | 5.000.000/năm | 7.500.000/năm | 10.000.000/năm |
```
</details>

<details><summary>[2] BVP_BQL_S1_TB2 </summary>

```text
[Bảo Việt An Gia | Bảng quyền lợi | BẢNG QUYỀN LỢI BẢO HIỂM - BẢO VIỆT AN GIA]
| CHƯƠNG TRÌNH BẢO HIỂM | ĐỒNG | BẠC | VÀNG | BẠCH KIM | KIM CƯƠNG |
|---|---|---|---|---|---|
| I. QUYỀN LỢI BẢO HIỂM CHÍNH – ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, BIẾN CHỨNG THAI SẢN |  |  |  |  |  |
| 3. Chi phí tái khám sau khi xuất viện (trong vòng 30 ngày sau khi xuất viện) | 2.000.000/năm | 3.000.000/năm | 5.000.000/năm | 7.500.000/năm | 10.000.000/năm |
| 4. Dịch vụ xe cứu thương, xe cấp cứu đường bộ | 5.000.000/năm | 5.000.000/năm | 10.000.000/năm | 10.000.000/năm | 10.000.000/năm |
| 5. Chi phí phẫu thuật | 40.000.000/năm | 60.000.000/năm | 100.000.000/năm | 150.000.000/năm | 200.000.000/năm |
| 6. Phục hồi chức năng | 4.000.000/năm | 6.000.000/năm | 10.000.000/năm | 15.000.000/năm | 20.000.000/năm |
| 7. Trợ cấp bệnh viện công (không quá 60 ngày/năm) | 80.000/ngày | 120.000/ngày | 200.000/ngày | 300.000/ngày | 400.000/ngày |
| 8. Trợ cấp mai táng phí trong trường hợp tử vong tại bệnh viện | 1.000.000/vụ | 1.000.000/vụ | 1.000.000/vụ | 1.000.000/vụ | 1.000.000/vụ |
```
</details>

<details><summary>[3] BVP_QT_C2_M1_A_K1 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. QUYỀN LỢI BẢO HIỂM CHÍNH: ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, BIẾN CHỨNG THAI SẢN > A. Quyền lợi bảo hiểm]
1. Chi phí nằm viện
Trường hợp Người được bảo hiểm phải nằm viện điều trị, Bảo hiểm Bảo Việt sẽ thanh toán cho Người được bảo hiểm tối đa không quá giới hạn phụ cho mỗi ngày điều trị quy định trong bảng quyền lợi bảo hiểm đối với những chi phí y tế thực tế theo chỉ định của bác sĩ, phát sinh cần thiết và hợp lý do bệnh, tai nạn, biến chứng thai sản thuộc phạm vi bảo hiểm xảy ra trong thời hạn bảo hiểm trừ những điểm loại trừ quy định tại hợp đồng bảo hiểm/quy tắc bảo hiểm, bao gồm các chi phí sau:
- Chi phí phòng và giường, suất ăn theo tiêu chuẩn phòng tại bệnh viện.
- Chi phí phòng chăm sóc đặc biệt (ICU (Intensive Care Unit), HDU (High Dependency Unit), CCU (Coronary Care Unit)), điều trị cấp cứu.
- Các chi phí bệnh viện tổng hợp:
- Chi phí thuốc điều trị và sử dụng trong khi nằm viện, truyền máu, ô xy, huyết thanh.
- Chi phí băng, nẹp bột.
- Chi phí tiêm truyền tĩnh mạch.
- Chi phí xét nghiệm hoặc chẩn đoán bằng hình ảnh như X-quang, MRI, CT, PET, siêu âm, nội soi. Các xét nghiệm này phải do bác sĩ chỉ định là cần thiết để đánh giá tình trạng bệnh và là một phần của chi phí nằm viện điều trị.
- Chi phí vật tư y tế tiêu hao cần thiết được sử dụng trong quá trình Người được bảo hiểm nằm viện.
- Các chi phí y tế liên quan khác.
Tổng số ngày nằm viện điều trị được trả tiền bảo hiểm không vượt quá 60 ngày/năm và tổng số tiền được trả tiền bảo hiểm không vượt quá số tiền bảo hiểm quy định của quyền lợi Điều trị nội trú do bệnh, tai nạn, biến chứng thai sản.
```
</details>

<details><summary>[4] BVP_BQL_S1_TB3 </summary>

```text
[Bảo Việt An Gia | Bảng quyền lợi | BẢNG QUYỀN LỢI BẢO HIỂM - BẢO VIỆT AN GIA]
| CHƯƠNG TRÌNH BẢO HIỂM | ĐỒNG | BẠC | VÀNG | BẠCH KIM | KIM CƯƠNG |
|---|---|---|---|---|---|
| II. QUYỀN LỢI BẢO HIỂM BỔ SUNG |  |  |  |  |  |
| 1. Điều trị ngoại trú do bệnh, tai nạn, biến chứng thai sản | 6.000.000/năm | 7.000.000/năm | 8.000.000/năm | 10.000.000/năm | 15.000.000/năm |
| Giới hạn/lần khám (không quá 10 lần khám/năm) | 1.200.000/lần | 1.400.000/lần | 1.600.000/lần | 2.000.000/lần | 3.000.000/lần |
| Điều trị vật lý trị liệu (không quá 60 ngày/năm) | 60.000/ngày | 70.000/ngày | 80.000/ngày | 100.000/ngày | 150.000/ngày |
| 2. Bảo hiểm Tai nạn cá nhân | Lựa chọn tham gia từ 20triệu đến 1tỷ đồng | Lựa chọn tham gia từ 20triệu đến 1tỷ đồng | Lựa chọn tham gia từ 20triệu đến 1tỷ đồng | Lựa chọn tham gia từ 20triệu đến 1tỷ đồng | Lựa chọn tham gia từ 20triệu đến 1tỷ đồng |
```
</details>

<details><summary>[5] BVP_QT_C2_M1_A_K5-8 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. QUYỀN LỢI BẢO HIỂM CHÍNH: ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, BIẾN CHỨNG THAI SẢN > A. Quyền lợi bảo hiểm]
5. Chi phí phẫu thuật
Bảo hiểm Bảo Việt sẽ chi trả cho Người được bảo hiểm các chi phí y tế thực tế thuộc phạm vi bảo hiểm phát sinh cho một ca phẫu thuật nội trú như định nghĩa, bao gồm chi phí thuốc, vật tư tiêu hao, các thiết bị cần thiết và hợp lý theo chỉ định của bác sĩ mà không bị loại trừ bảo hiểm, chi phí phòng mổ, phẫu thuật viên, các chi phí gây mê, các chi phí hội chẩn trước khi mổ và hồi sức sau khi mổ, chi phí tái mổ, chi phí cấy ghép nội tạng trừ những điểm loại trừ quy định tại hợp đồng bảo hiểm/quy tắc bảo hiểm. Giới hạn số tiền chi trả cho trường hợp phẫu thuật không vượt mức giới hạn tối
đa do Người được bảo hiểm lựa chọn khi tham gia bảo hiểm và được ghi cụ thể trong hợp đồng bảo hiểm.
Trường hợp phẫu thuật trong ngày và phẫu thuật ngoại trú không được chi trả trong quyền lợi này.
6. Phục hồi chức năng
7. Trợ cấp bệnh viện công (không quá 60 ngày/năm)
Bảo hiểm Bảo Việt chi trả số tiền trợ cấp ghi trên bảng quyền lợi bảo hiểm cho mỗi ngày nằm viện điều trị nội trú do bệnh, tai nạn tại các bệnh viện công lập.
8. Trợ cấp mai táng phí trong trường hợp tử vong tại bệnh viện.
Trường hợp Người được bảo hiểm tử vong khi nằm viện thuộc phạm vi trách nhiệm bảo hiểm, Bảo hiểm Bảo Việt sẽ trả tiền trợ cấp mai táng phí ghi trên hợp đồng bảo hiểm.
```
</details>

---

## v1-0055 · compare · easy · BVP C37

**Câu hỏi:** Độ tuổi nhỏ nhất để bắt đầu tham gia bảo hiểm của Bảo Việt An Gia và Bảo hiểm 37 bệnh hiểm nghèo (CI37) khác nhau như thế nào?

**Đáp án chuẩn:** Tuổi tham gia nhỏ nhất của Bảo Việt An Gia là từ 15 ngày tuổi, trong khi Bảo hiểm 37 bệnh hiểm nghèo (CI37) yêu cầu từ 18 tuổi. Như vậy, Bảo Việt An Gia có độ tuổi nhận bảo hiểm nhỏ hơn so với CI37.

**Evidence:** `BVP_QT_C1_M3 C37_QT_C4_M1`

**Câu trả lời:**

> Độ tuổi nhỏ nhất để bắt đầu tham gia bảo hiểm của Bảo Việt An Gia là 15 ngày tuổi [1], trong khi Bảo hiểm 37 bệnh hiểm nghèo (CI37) yêu cầu là từ 18 tuổi trở lên [2].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] BVP_QT_C1_M3 ★✓</summary>

```text
[Bảo Việt An Gia | Quy tắc | CHƯƠNG I - Quy Định Chung > III. ĐỐI TƯỢNG THAM GIA BẢO HIỂM]
Đối tượng được tham gia bảo hiểm theo quy tắc bảo hiểm này:
1. Người được bảo hiểm là mọi công dân Việt Nam hoặc người nước ngoài cư trú hợp pháp tại Việt Nam từ 15 ngày tuổi đến 65 tuổi tại thời điểm bắt đầu hiệu lực của hợp đồng bảo hiểm. Người được bảo hiểm chỉ được tham gia đến 65 tuổi với điều kiện đã tham gia liên tục trước đó từ năm 60 tuổi.
2. Trường hợp trẻ em dưới 6 tuổi chỉ được nhận bảo hiểm với điều kiện phải tham gia bảo hiểm cùng hợp đồng với bố và/hoặc mẹ hoặc bố/mẹ đã tham gia ít nhất một loại hình Bảo hiểm Sức khỏe, Chi phí y tế còn hiệu lực tại Bảo hiểm Bảo Việt. Quyền lợi bảo hiểm của trẻ em chỉ được áp dụng mức tương đương hoặc thấp hơn quyền lợi của bố/mẹ.
3. Đối tượng trẻ em từ 15 ngày tuổi đến 3 tuổi, quyền lợi Điều trị nội trú và Điều trị ngoại trú áp dụng theo tỷ lệ đồng chi trả được quy định trong bảng quyền lợi bảo hiểm.
4. Đối tượng trẻ em từ 15 ngày tuổi đến 1 tuổi chỉ được tham gia với điều kiện: Cung cấp giấy yêu cầu bảo hiểm trong tình trạng sức khỏe tốt và khi trẻ đã xuất viện, tham gia cùng bố/mẹ như đã đề cập ở trên, chỉ được tham gia chương trình Bạch Kim/Kim Cương.
```
</details>

<details open><summary>[2] C37_QT_C4_M1 ★✓</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG IV - Điều kiện chung > 1. Điều kiện tham gia]
Người được bảo hiểm phải là công dân Việt Nam hoặc người nước ngoài cư trú hợp pháp ở Việt Nam, tức là ở tại Việt Nam ít nhất 6 tháng trong vòng 12 tháng trước ngày bắt đầu hiệu lực bảo hiểm, với giấy phép lao động hoặc giấy phép cư trú hợp lệ.
Tuổi bắt đầu tham gia bảo hiểm: từ 18 đến 60 tuổi. Trong mọi trường hợp, hợp đồng bảo hiểm chỉ được tái tục cho đến khi NĐBH tròn 65 tuổi.
```
</details>

<details><summary>[3] BVP_QT_C1_M1_K3 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 3. Bên mua bảo hiểm/Người yêu cầu bảo hiểm]
Là tổ chức được thành lập và hoạt động hợp pháp tại Việt Nam, hoặc cá nhân tại Việt Nam từ đủ 18 tuổi trở lên có năng lực hành vi dân sự đầy đủ tại thời điểm giao kết hợp đồng bảo hiểm với Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải đáp ứng các điều kiện để mua bảo hiểm theo quy tắc, điều kiện, điều khoản bảo hiểm và đóng phí bảo hiểm cho Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải có quyền lợi có thể được bảo hiểm theo quy định của pháp luật.
Bên mua bảo hiểm có quyền lợi có thể được bảo hiểm đối với những người sau đây:
- Bản thân Bên mua bảo hiểm;
- Bố/mẹ của Bên mua bảo hiểm;
- Vợ/chồng, con của Bên mua bảo hiểm;
- Người có quan hệ nuôi dưỡng và cấp dưỡng hợp pháp với Bên mua bảo hiểm;
- Người khác, nếu người đó đồng ý cho Bên mua bảo hiểm mua bảo hiểm cho mình.
```
</details>

<details><summary>[4] C37_QT_C1_M2 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 2. Bên mua bảo hiểm]
Là tổ chức được thành lập và hoạt động hợp pháp tại Việt Nam, hoặc cá nhân tại Việt Nam từ đủ 18 tuổi trở lên có năng lực hành vi dân sự đầy đủ tại thời điểm giao kết hợp đồng bảo hiểm với Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải đáp ứng các điều kiện để mua bảo hiểm theo quy tắc, điều kiện, điều khoản bảo hiểm và đóng phí bảo hiểm cho Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải có quyền lợi có thể được bảo hiểm theo quy định của pháp luật.
Bên mua bảo hiểm có quyền lợi có thể được bảo hiểm đối với những người sau đây:
- Bản thân Bên mua bảo hiểm;
- Bố/mẹ của Bên mua bảo hiểm;
- Vợ/chồng, con của Bên mua bảo hiểm;
- Người có quan hệ nuôi dưỡng và cấp dưỡng hợp pháp với Bên mua bảo hiểm;
- Người khác, nếu người đó đồng ý cho Bên mua bảo hiểm mua bảo hiểm cho mình.
```
</details>

<details><summary>[5] BVP_BP_S1_P1 </summary>

```text
[Bảo Việt An Gia | Biểu phí | BIỂU PHÍ BẢO HIỂM BẢO VIỆT AN GIA]
(Ban hành theo Quyết định số 6029/QĐ-BHBV ngày 27 tháng 06 năm 2025 củaTổngGiám đốc TổngCông ty Bảohiểm BảoViệt)
Đơn vị: VND/người/năm
| CHƯƠNG TRÌNH BẢO HIỂM | ĐỒNG | BẠC | VÀNG | BẠCH KIM | KIM CƯƠNG |
|---|---|---|---|---|---|
| A. BẢO HIỂM CHÍNH – Điều trị nội trú do ốm bệnh, tai nạn |  |  |  |  |  |
| • Từ 15 ngày tuổi đến dưới 1 tuổi | Không | Không | Không | 13.648.000 | 16.681.000 |
| • Từ 1 đến 3 tuổi | 2.973.000 | 4.264.000 | 6.459.000 | 9.099.000 | 11.121.000 |
| • Trên 4 đến 6 tuổi | 1.914.000 | 2.746.000 | 4.160.000 | 5.616.000 | 6.864.000 |
| • Trên 7 đến 9 tuổi | 1.615.000 | 2.317.000 | 3.510.000 | 4.739.000 | 5.792.000 |
| • Trên 10 đến 30 tuổi | 1.445.000 | 2.073.000 | 3.140.000 | 4.423.000 | 5.406.000 |
| • Trên 31 đến 50 tuổi | 1.582.000 | 2.270.000 | 3.439.000 | 4.844.000 | 5.921.000 |
| • Trên 51 đến 65 tuổi | 1.866.000 | 2.677.000 | 4.056.000 | 5.704.000 | 6.972.000 |
```
</details>

---

## v1-0056 · compare · medium · BVP C37

**Câu hỏi:** Quy định về thời hạn bảo hiểm giữa Bảo Việt An Gia và Bảo hiểm 37 bệnh hiểm nghèo (CI37) có điểm gì khác nhau?

**Đáp án chuẩn:** Bảo Việt An Gia quy định thời hạn bảo hiểm cố định là 01 năm và không chấp nhận trường hợp tham gia ngắn hạn. Trong khi đó, Bảo hiểm 37 bệnh hiểm nghèo có thời hạn bảo hiểm tối đa là 1 năm và cho phép người tham gia yêu cầu gia hạn tối đa 4 lần, mỗi lần 1 năm.

**Evidence:** `BVP_QT_C1_M1_K45 C37_QT_C4_M9`

**Câu trả lời:**

> [1] [2]
> 
> Thời hạn bảo hiểm của Bảo Việt An Gia là 1 năm và không chấp nhận các trường hợp tham gia ngắn hạn hoặc bổ sung quyền lợi giữa kỳ, trong khi Bảo hiểm 37 bệnh hiểm nghèo (CI37) có thể có thời hạn bảo hiểm là 1 năm hoặc ít hơn, tùy thuộc vào hợp đồng bảo hiểm tổ chức.
> 
> Bảo hiểm 37 bệnh hiểm nghèo (CI37) cho phép Bên mua bảo hiểm gia hạn bảo hiểm tối đa 4 lần, mỗi lần 1 năm, trong khi Bảo Việt An Gia không đề cập đến việc gia hạn bảo hiểm.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] BVP_QT_C1_M1_K45 ★✓</summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 45. Thời hạn bảo hiểm]
Thời hạn bảo hiểm được tính từ thời điểm Bảo hiểm Bảo Việt bắt đầu nhận bảo hiểm cho đến khi kết thúc bảo hiểm. Thời hạn bảo hiểm bắt đầu từ 0 giờ 1 phút sáng ngày bắt đầu hiệu lực bảo hiểm và được kết thúc vào 23 giờ 59 phút ngày hết hạn hiệu lực bảo hiểm. Thời hạn bảo hiểm là 01 năm và được quy định cụ thể trong hợp đồng bảo hiểm, không chấp nhận các trường hợp tham gia ngắn hạn hoặc bổ sung quyền lợi giữa kỳ.
```
</details>

<details open><summary>[2] C37_QT_C1_M21 ★</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 21. Thời hạn bảo hiểm]
Thời hạn bảo hiểm được tính từ thời điểm Bảo hiểm Bảo Việt bắt đầu nhận bảo hiểm cho đến khi kết thúc bảo hiểm. Thời hạn bảo hiểm bắt đầu từ 0 giờ 1 phút sáng ngày bắt đầu hiệu lực bảo hiểm và được kết thúc vào 23 giờ 59 phút ngày hết hạn hiệu lực bảo hiểm.
Đối với hợp đồng bảo hiểm cá nhân: Thời hạn bảo hiểm là 01 năm và được quy định cụ thể trong hợp đồng bảo hiểm.
Đối với hợp đồng bảo hiểm tổ chức: Thời hạn bảo hiểm là 01 năm hoặc ít hơn, và được quy định cụ thể trong hợp đồng bảo hiểm.
```
</details>

<details><summary>[3] BVP_QT_C1_M7 </summary>

```text
[Bảo Việt An Gia | Quy tắc | CHƯƠNG I - Quy Định Chung > VII.Kết thúc quyền lợi bảo hiểm]
Tất cả các quyền lợi bảo hiểm theo hợp đồng bảo hiểm sẽ chấm dứt hiệu lực vào 23 giờ 59 phút đêm của ngày cuối cùng của thời hạn bảo hiểm hoặc vào ngày chấm dứt hiệu lực bảo hiểm do Bên mua bảo hiểm/Bảo hiểm Bảo Việt yêu cầu tùy theo thời điểm nào đến trước. Bảo hiểm Bảo Việt không phải chịu trách nhiệm bồi thường bảo hiểm đối với các sự kiện bảo hiểm/rủi ro phát sinh sau các thời điểm nêu trên. Đồng thời, Bảo hiểm Bảo Việt cũng không phải chịu trách nhiệm bồi thường bảo hiểm đối với hậu quả của các rủi ro phát sinh trong thời hạn bảo hiểm nhưng hậu quả xảy ra ngoài thời hạn bảo hiểm hoặc sau thời điểm chấm dứt hiệu lực bảo hiểm.
```
</details>

<details><summary>[4] C37_QT_C4_M9 ✓</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG IV - Điều kiện chung > 9. Thời hạn bảo hiểm]
Thời hạn bảo hiểm tối đa là 1 năm tính từ thời điểm bảo hiểm Bảo Việt bắt đầu nhận bảo hiểm (thời điểm bắt đầu nhận bảo hiểm/ngày bắt đầu thời hạn bảo hiểm) đến khi kết thúc bảo hiểm (thời điểm kết thúc bảo hiểm/ngày kết thúc thời hạn bảo hiểm) và được ghi cụ thể trên Hợp đồng bảo hiểm. Bên mua bảo hiểm có thể yêu cầu gia hạn bảo hiểm tối đa 4 lần, mỗi lần 1 năm. Bảo hiểm Bảo Việt xem xét và được thể hiện trên Hợp đồng bảo hiểm. Trong thời gian gia hạn bảo hiểm, các điều kiện điều khoản và phí bảo hiểm không thay đổi. Sau khi kết thúc thời gian gia hạn tối đa, nếu Bên mua bảo hiểm tiếp tục tham gia bảo hiểm, Bên mua bảo hiểm sẽ phải yêu cầu ký Hợp đồng bảo hiểm mới.
```
</details>

<details><summary>[5] BVP_QT_C1_M6 </summary>

```text
[Bảo Việt An Gia | Quy tắc | CHƯƠNG I - Quy Định Chung > VI. PHÍ BẢO HIỂM, THỜI HẠN THANH TOÁN PHÍ BẢO HIỂM, THAY ĐỔI QUYỀN LỢI BẢO HIỂM]
Phí bảo hiểm: quy định trong Biểu phí đính kèm Quy tắc bảo hiểm này, phí bảo hiểm phụ thuộc vào chương trình bảo hiểm, độ tuổi của Người được bảo hiểm khi tham gia mới/tái tục bảo hiểm.
Thời hạn thanh toán phí bảo hiểm: được quy định cụ thể tại hợp đồng bảo hiểm và phù hợp với quy định của pháp luật. Trong mọi trường hợp, Bên mua bảo hiểm có nghĩa vụ đóng phí bảo hiểm đầy đủ và đúng thời hạn quy định trong hợp đồng bảo hiểm. Bên mua bảo hiểm và Người được bảo hiểm đồng ý rằng, trong quá trình thực hiện hợp đồng bảo hiểm, Công ty bảo hiểm không có nghĩa vụ phải gửi thông báo nhắc đóng phí.
Thay đổi quyền lợi bảo hiểm: Giới hạn trách nhiệm của các quyền lợi không thể thay đổi trong suốt thời hạn hợp đồng bảo hiểm. Những quyền lợi này chỉ có thể được thay đổi vào ngày tái tục của hợp đồng bảo hiểm trên cơ sở có xác nhận của Bảo hiểm Bảo Việt. Trường hợp tái tục với số tiền bảo hiểm/hạn mức phụ cao hơn và/hoặc tham gia thêm quyền lợi mới so với năm trước phải được sự chấp thuận của Bảo hiểm Bảo Việt; phần chênh lệch về số tiền bảo hiểm/hạn mức phụ cũng như quyền lợi tham gia thêm mới sẽ không được coi là tái tục liên tục, và thời gian chờ đối với phần chênh lệch về số tiền bảo hiểm/hạn mức phụ cũng như quyền lợi tham gia thêm mới sẽ được tính từ thời điểm hợp đồng tái tục (có số tiền bảo hiểm/hạn mức phụ cao hơn và/hoặc tham gia thêm quyền lợi mới) có hiệu lực.
```
</details>

---

## v1-0057 · compare · medium · BVP ITC

**Câu hỏi:** Độ tuổi tham gia bảo hiểm tối đa của Bảo Việt An Gia và Bảo Việt Intercare được quy định khác nhau như thế nào?

**Đáp án chuẩn:** Ở Bảo Việt An Gia, người được bảo hiểm chỉ được tham gia tối đa đến 65 tuổi với điều kiện tham gia liên tục từ năm 60 tuổi. Trong khi đó, Bảo Việt Intercare có giới hạn tuổi cao hơn, nhận người tham gia lần đầu đến 69 tuổi và người tham gia tái tục đến 75 tuổi.

**Evidence:** `BVP_QT_C1_M3 ITC_QT_C4_M1_P1`

**Câu trả lời:**

> Độ tuổi tham gia bảo hiểm tối đa của Bảo Việt An Gia và Bảo Việt Intercare được quy định khác nhau như sau:
> 
> - Bảo Việt An Gia: Độ tuổi tham gia bảo hiểm tối đa là 65 tuổi [1].
> 
> - Bảo Việt Intercare: Độ tuổi tham gia bảo hiểm tối đa là 69 tuổi nếu mới tham gia lần đầu hoặc 75 tuổi nếu tham gia tái tục [2].
> 
> Tài liệu sản phẩm hiện có không có thông tin về độ tuổi tham gia bảo hiểm tối đa của Bảo Việt Intercare khi tham gia tái tục.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] BVP_QT_C1_M3 ★✓</summary>

```text
[Bảo Việt An Gia | Quy tắc | CHƯƠNG I - Quy Định Chung > III. ĐỐI TƯỢNG THAM GIA BẢO HIỂM]
Đối tượng được tham gia bảo hiểm theo quy tắc bảo hiểm này:
1. Người được bảo hiểm là mọi công dân Việt Nam hoặc người nước ngoài cư trú hợp pháp tại Việt Nam từ 15 ngày tuổi đến 65 tuổi tại thời điểm bắt đầu hiệu lực của hợp đồng bảo hiểm. Người được bảo hiểm chỉ được tham gia đến 65 tuổi với điều kiện đã tham gia liên tục trước đó từ năm 60 tuổi.
2. Trường hợp trẻ em dưới 6 tuổi chỉ được nhận bảo hiểm với điều kiện phải tham gia bảo hiểm cùng hợp đồng với bố và/hoặc mẹ hoặc bố/mẹ đã tham gia ít nhất một loại hình Bảo hiểm Sức khỏe, Chi phí y tế còn hiệu lực tại Bảo hiểm Bảo Việt. Quyền lợi bảo hiểm của trẻ em chỉ được áp dụng mức tương đương hoặc thấp hơn quyền lợi của bố/mẹ.
3. Đối tượng trẻ em từ 15 ngày tuổi đến 3 tuổi, quyền lợi Điều trị nội trú và Điều trị ngoại trú áp dụng theo tỷ lệ đồng chi trả được quy định trong bảng quyền lợi bảo hiểm.
4. Đối tượng trẻ em từ 15 ngày tuổi đến 1 tuổi chỉ được tham gia với điều kiện: Cung cấp giấy yêu cầu bảo hiểm trong tình trạng sức khỏe tốt và khi trẻ đã xuất viện, tham gia cùng bố/mẹ như đã đề cập ở trên, chỉ được tham gia chương trình Bạch Kim/Kim Cương.
```
</details>

<details open><summary>[2] ITC_QT_C4_M1_P1 ★✓</summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN IV. QUY ĐỊNH CHUNG > 1. Đối tượng và điều kiện tham gia bảo hiểm]
- Từ 15 ngày tuổi đến 69 tuổi nếu mới tham gia lần đầu hoặc đến 75 tuổi nếu tham gia tái tục.
- Không bị các bệnh tâm thần
- Không bị các bệnh ung thư (chỉ áp dụng cho Người được bảo hiểm tham gia năm đầu tiên)
- Không bị thương tật vĩnh viễn từ 80% trở lên
- Không đang trong thời gian điều trị nội trú bệnh đặc biệt (chỉ áp dụng cho Người được bảo hiểm tham gia năm đầu tiên)
- Là người Việt Nam hoặc người nước ngoài cư trú hợp pháp trong lãnh thổ Việt Nam và không rời khỏi Việt Nam liên tiếp hơn 180 ngày (quy định này không áp dụng với du học sinh ở nước ngoài).
Trường hợp Người tham gia không đúng theo đối tượng và điều kiện tham gia như đề cập, Bảo hiểm Bảo Việt có quyền chấm dứt bảo hiểm và không chịu trách nhiệm với quyền lợi bảo hiểm đã đăng ký.
Người phụ thuộc chỉ được bảo hiểm theo chương trình thấp hơn hoặc bằng mức quyền lợi với Người được bảo hiểm chính (bao gồm cả quyền lợi bảo hiểm chính và các quyền lợi bảo hiểm bổ sung) và phải được Bảo hiểm Bảo Việt chấp thuận.
Trẻ em mới sinh đủ điều kiện tham gia bảo hiểm sau 15 ngày tuổi kể từ ngày sinh hay kể từ ngày xuất viện, ngày nào xảy ra sau sẽ được chọn. Người được bảo hiểm phải nộp yêu cầu bảo hiểm cho đứa trẻ đó cùng với giấy chứng nhận đứa trẻ ở trong tình trạng sức khỏe tốt và phải được Bảo hiểm Bảo Việt chấp thuận. Trẻ em dưới 18 tuổi yêu cầu tham gia cùng bố/mẹ.
Áp dụng bổ sung với hợp đồng bảo hiểm tổ chức:
Đối tượng tham gia bảo hiểm trong hợp đồng bảo hiểm tổ chức bao gồm
a. Nhân viên của Bên mua bảo hiểm.
b. Người thân của Nhân viên.
- Nhân viên chỉ được đăng ký bảo hiểm cho người thân của mình một lần vào đầu hiệu lực hợp đồng.
- Đăng ký sau ngày bắt đầu hiệu lực của hợp đồng bảo hiểm chỉ áp dụng đối với các trường hợp sau:
- Người thân của nhân viên mới vào làm việc;
- Vợ hoặc chồng của nhân viên mới kết hôn;
- Con mới sinh đủ tuổi và đủ điều kiện tham gia;
```
</details>

<details><summary>[3] BVP_QT_C2_M2_B5 </summary>

```text
[Bảo Việt An Gia | Quy tắc | II. QUYỀN LỢI BẢO HIỂM BỔ SUNG > QUYỀN LỢI BỔ SUNG 5: BẢO HIỂM THAI SẢN]
- Người được bảo hiểm có độ tuổi từ 18 tuổi đến 45 tuổi.
- Người được bảo hiểm phải tham gia Quyền lợi bảo hiểm chính chương trình Bạc, Vàng, Bạch Kim, Kim Cương.
- Đối với biến chứng thai sản: Ngoài việc được hưởng theo quyền lợi bảo hiểm bổ sung này, Người được bảo hiểm sẽ được hưởng thêm quyền lợi tối đa thuộc phạm vi bảo hiểm theo Quyền lợi bảo hiểm chính và Quyền lợi bổ sung Điều trị ngoại trú với điều kiện cung cấp đầy đủ hồ sơ chứng từ về y tế và hóa đơn theo qui định.
Đơn vị: VNĐ
| Thai sản | BẠC | VÀNG | BẠCH KIM | KIM CƯƠNG |
|---|---|---|---|---|
| Giới hạn trách nhiệm tối đa cho một thời hạn bảo hiểm | 21.000.000 | 21.000.000 | 21.000.000 | 31.500.000 |
```
</details>

<details><summary>[4] ITC_QT_C1_M28 </summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN I - ĐỊNH NGHĨA > 28. Giới hạn cả đời]
Là giới hạn số tiền bảo hiểm tối đa mà Bảo hiểm Bảo Việt có thể chi trả cho Người được bảo hiểm trong suốt cuộc đời Người được bảo hiểm kể từ ngày tham gia bảo hiểm đầu tiên tại Bảo hiểm Bảo Việt đến cuối cuộc đời (Kể cả trường hợp Người được bảo hiểm tham gia bảo hiểm liên tục hay gián đoạn với Bảo hiểm Bảo Việt). Giới hạn cả đời cho một người được bảo hiểm đối với tất cả các bệnh thuộc danh mục bệnh đặc biệt theo định nghĩa, tình trạng bỏng từ độ III trở lên, chấn thương sọ não có thang điểm hôn mê Glasgow dưới 8 (GCS <8): bằng 20% của số tiền bảo hiểm quyền lợi bảo hiểm chính, và được quy định cụ thể trong bảng quyền lợi bảo hiểm.
```
</details>

<details><summary>[5] BVP_QT_C1_M1_K3 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 3. Bên mua bảo hiểm/Người yêu cầu bảo hiểm]
Là tổ chức được thành lập và hoạt động hợp pháp tại Việt Nam, hoặc cá nhân tại Việt Nam từ đủ 18 tuổi trở lên có năng lực hành vi dân sự đầy đủ tại thời điểm giao kết hợp đồng bảo hiểm với Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải đáp ứng các điều kiện để mua bảo hiểm theo quy tắc, điều kiện, điều khoản bảo hiểm và đóng phí bảo hiểm cho Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải có quyền lợi có thể được bảo hiểm theo quy định của pháp luật.
Bên mua bảo hiểm có quyền lợi có thể được bảo hiểm đối với những người sau đây:
- Bản thân Bên mua bảo hiểm;
- Bố/mẹ của Bên mua bảo hiểm;
- Vợ/chồng, con của Bên mua bảo hiểm;
- Người có quan hệ nuôi dưỡng và cấp dưỡng hợp pháp với Bên mua bảo hiểm;
- Người khác, nếu người đó đồng ý cho Bên mua bảo hiểm mua bảo hiểm cho mình.
```
</details>

---

## v1-0121 · compare · hard · BVP FLX

**Câu hỏi:** Độ tuổi tham gia nhỏ nhất của Bảo Việt An Gia và Bảo hiểm Du lịch Flexi khác nhau như thế nào? Để trẻ ở độ tuổi tối thiểu này được tham gia Bảo Việt An Gia, hợp đồng cần đáp ứng các điều kiện gì về sức khỏe, người đi kèm và chương trình bảo hiểm?

**Đáp án chuẩn:** Độ tuổi tham gia nhỏ nhất của Bảo Việt An Gia là từ 15 ngày tuổi, trong khi Bảo hiểm Du lịch Flexi yêu cầu từ 06 tháng tuổi. Với trẻ từ 15 ngày tuổi đến 1 tuổi ở Bảo Việt An Gia, trẻ phải có giấy yêu cầu bảo hiểm trong tình trạng sức khỏe tốt và đã xuất viện, phải tham gia cùng bố/mẹ (hoặc bố/mẹ có bảo hiểm sức khỏe/chi phí y tế còn hiệu lực tại Bảo hiểm Bảo Việt với quyền lợi tương đương hoặc cao hơn), đồng thời chỉ được lựa chọn chương trình Bạch Kim hoặc Kim Cương.

**Evidence:** `BVP_QT_C1_M3 FLX_QT_C1_M1_K15`

**Câu trả lời:**

> Độ tuổi tham gia nhỏ nhất của Bảo Việt An Gia là 15 ngày tuổi [1], trong khi Bảo hiểm Du lịch Flexi là 6 tháng tuổi [2].
> 
> Để trẻ ở độ tuổi tối thiểu này được tham gia Bảo Việt An Gia, hợp đồng cần đáp ứng các điều kiện sau:
> - Trẻ em từ 15 ngày tuổi đến 3 tuổi chỉ được tham gia với điều kiện cung cấp giấy yêu cầu bảo hiểm trong tình trạng sức khỏe tốt và khi trẻ đã xuất viện [1].
> - Trẻ em từ 15 ngày tuổi đến 1 tuổi chỉ được tham gia chương trình Bạch Kim/Kim Cương [1].
> 
> Tài liệu sản phẩm hiện có không có thông tin về điều kiện sức khỏe, người đi kèm cho trẻ em từ 15 ngày tuổi đến 1 tuổi [1].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] BVP_QT_C1_M3 ★✓</summary>

```text
[Bảo Việt An Gia | Quy tắc | CHƯƠNG I - Quy Định Chung > III. ĐỐI TƯỢNG THAM GIA BẢO HIỂM]
Đối tượng được tham gia bảo hiểm theo quy tắc bảo hiểm này:
1. Người được bảo hiểm là mọi công dân Việt Nam hoặc người nước ngoài cư trú hợp pháp tại Việt Nam từ 15 ngày tuổi đến 65 tuổi tại thời điểm bắt đầu hiệu lực của hợp đồng bảo hiểm. Người được bảo hiểm chỉ được tham gia đến 65 tuổi với điều kiện đã tham gia liên tục trước đó từ năm 60 tuổi.
2. Trường hợp trẻ em dưới 6 tuổi chỉ được nhận bảo hiểm với điều kiện phải tham gia bảo hiểm cùng hợp đồng với bố và/hoặc mẹ hoặc bố/mẹ đã tham gia ít nhất một loại hình Bảo hiểm Sức khỏe, Chi phí y tế còn hiệu lực tại Bảo hiểm Bảo Việt. Quyền lợi bảo hiểm của trẻ em chỉ được áp dụng mức tương đương hoặc thấp hơn quyền lợi của bố/mẹ.
3. Đối tượng trẻ em từ 15 ngày tuổi đến 3 tuổi, quyền lợi Điều trị nội trú và Điều trị ngoại trú áp dụng theo tỷ lệ đồng chi trả được quy định trong bảng quyền lợi bảo hiểm.
4. Đối tượng trẻ em từ 15 ngày tuổi đến 1 tuổi chỉ được tham gia với điều kiện: Cung cấp giấy yêu cầu bảo hiểm trong tình trạng sức khỏe tốt và khi trẻ đã xuất viện, tham gia cùng bố/mẹ như đã đề cập ở trên, chỉ được tham gia chương trình Bạch Kim/Kim Cương.
```
</details>

<details open><summary>[2] FLX_QT_C1_M1_K35 ★</summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | I. ĐỊNH NGHĨA > 35. Trẻ em]
Là người có độ tuổi từ 6 (sáu) tháng tuổi đến 16 (mười sáu) tuổi tại ngày bắt đầu hiệu lực của Hợp đồng bảo hiểm/Giấy chứng nhận bảo hiểm, là con hợp pháp của Người được bảo hiểm và/hoặc người được giám hộ bởi Người được bảo hiểm và tham gia chuyến đi cùng với Người được bảo hiểm.
Trẻ em có độ tuổi từ 11 trở xuống phải được một người được bảo hiểm là người lớn đi kèm và được bảo hiểm cùng với người đó.
Trẻ em có độ tuổi từ 12 đến 16 đi du lịch một mình cũng sẽ được chấp nhận bảo hiểm theo Hợp đồng bảo hiểm/Giấy chứng nhận bảo hiểm với điều kiện đóng phí bảo hiểm theo phí chuẩn của người lớn. Với những trường hợp này, các quyền lợi được chi trả theo hạn mức giới hạn của đối tượng Trẻ em.
```
</details>

<details><summary>[3] BVP_QT_C1_M1_K3 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 3. Bên mua bảo hiểm/Người yêu cầu bảo hiểm]
Là tổ chức được thành lập và hoạt động hợp pháp tại Việt Nam, hoặc cá nhân tại Việt Nam từ đủ 18 tuổi trở lên có năng lực hành vi dân sự đầy đủ tại thời điểm giao kết hợp đồng bảo hiểm với Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải đáp ứng các điều kiện để mua bảo hiểm theo quy tắc, điều kiện, điều khoản bảo hiểm và đóng phí bảo hiểm cho Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải có quyền lợi có thể được bảo hiểm theo quy định của pháp luật.
Bên mua bảo hiểm có quyền lợi có thể được bảo hiểm đối với những người sau đây:
- Bản thân Bên mua bảo hiểm;
- Bố/mẹ của Bên mua bảo hiểm;
- Vợ/chồng, con của Bên mua bảo hiểm;
- Người có quan hệ nuôi dưỡng và cấp dưỡng hợp pháp với Bên mua bảo hiểm;
- Người khác, nếu người đó đồng ý cho Bên mua bảo hiểm mua bảo hiểm cho mình.
```
</details>

<details><summary>[4] FLX_QT_C1_M1_K2 </summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | I. ĐỊNH NGHĨA > 2. Bên mua bảo hiểm/Người yêu cầu bảo hiểm]
Là tổ chức được thành lập và hoạt động hợp pháp hoặc cá nhân từ đủ 18 tuổi trở lên có năng lực hành vi dân sự đầy đủ tại thời điểm giao kết hợp đồng bảo hiểm với Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải đáp ứng các điều kiện để mua bảo hiểm theo quy tắc, điều kiện, điều khoản bảo hiểm và đóng phí bảo hiểm cho Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải có quyền lợi có thể được bảo hiểm theo quy định của pháp luật. Bên mua bảo hiểm có quyền lợi có thể được bảo hiểm đối với những người sau đây:
- Bản thân Bên mua bảo hiểm;
- Bố/mẹ của Bên mua bảo hiểm;
- Vợ/chồng, con đẻ/con nuôi hợp pháp của Bên mua bảo hiểm;
- Người có quan hệ nuôi dưỡng và cấp dưỡng hợp pháp với Bên mua bảo hiểm;
- Tổ chức, doanh nghiệp đại diện mua bảo hiểm cho các cá nhân có liên quan.
```
</details>

<details><summary>[5] BVP_QT_C1_M1_K35 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 35. Người phụ thuộc (người thân)]
Là con hợp pháp của Bên mua bảo hiểm/Người được bảo hiểm có độ tuổi từ 15 ngày tuổi đến 18 tuổi hoặc 24 tuổi nếu đang theo học các khóa học dài hạn tại Việt Nam và chưa kết hôn, kể từ ngày có hiệu lực bảo hiểm hoặc ngày tái tục bảo hiểm hàng năm tiếp theo. Tất cả người phụ thuộc phải có tên trong danh sách yêu cầu được bảo hiểm.
```
</details>

---

## v1-0124 · compare · medium · BTB C37

**Câu hỏi:** Mức số tiền bảo hiểm của quyền lợi bảo hiểm chính trong sản phẩm Bảo Việt Tâm Bình khác như thế nào so với sản phẩm Bảo hiểm 37 bệnh hiểm nghèo (CI37)?

**Đáp án chuẩn:** Bảo Việt Tâm Bình quy định số tiền bảo hiểm theo 5 chương trình cố định: Cơ bản (60.000.000), Mở rộng (100.000.000), Nâng cao (160.000.000), Toàn diện (220.000.000) và Ưu việt (330.000.000). Trong khi đó, Bảo hiểm 37 bệnh hiểm nghèo (CI37) áp dụng mức số tiền bảo hiểm trong khoảng từ 200.000.000 đến 1.000.000.000 Việt Nam đồng, với mức trần tối đa cao hơn đáng kể so với Bảo Việt Tâm Bình.

**Evidence:** `BTB_BP_S1_TB1 C37_BQL_S2_P1`

**Câu trả lời:**

> Số tiền bảo hiểm của quyền lợi bảo hiểm chính trong sản phẩm Bảo Việt Tâm Bình và Bảo hiểm 37 bệnh hiểm nghèo (CI37) được quy định như sau:
> 
> - Bảo Việt Tâm Bình: Số tiền bảo hiểm được quy định trong bảng phí, tùy thuộc vào chương trình bảo hiểm và nhóm tuổi của người được bảo hiểm. Ví dụ, cho độ tuổi 19-40, số tiền bảo hiểm trong chương trình Toàn diện là 220.000.000 đồng [3].
> 
> - Bảo hiểm 37 bệnh hiểm nghèo (CI37): Số tiền bảo hiểm được quy định trong quy tắc bảo hiểm, là 100% số tiền bảo hiểm được chẩn đoán mắc bệnh hiểm nghèo và còn sống 30 ngày sau đó [4].
> 
> Tài liệu sản phẩm hiện có không có thông tin để so sánh trực tiếp về mức số tiền bảo hiểm giữa hai sản phẩm này.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details><summary>[1] BTB_QT_C1_M41 </summary>

```text
[Bảo Việt Tâm Bình | Quy tắc | CHƯƠNG I: ĐỊNH NGHĨA > 41. Số tiền bảo hiểm]
Là tổng mức trách nhiệm bảo hiểm tối đa của Bảo hiểm Bảo Việt đối với Người được bảo hiểm trong suốt thời hạn bảo hiểm. Số tiền bảo hiểm được quy định trong hợp đồng bảo hiểm và/hoặc bảng quyền lợi bảo hiểm đính kèm quy tắc bảo hiểm/hợp đồng bảo hiểm.
```
</details>

<details><summary>[2] C37_QT_C1_M19 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 19. Số tiền bảo hiểm]
Là tổng mức trách nhiệm bảo hiểm tối đa của Bảo hiểm Bảo Việt đối với Người được bảo hiểm trong suốt thời hạn bảo hiểm. Số tiền bảo hiểm được quy định trong hợp đồng bảo hiểm và/hoặc bảng quyền lợi bảo hiểm đính kèm quy tắc bảo hiểm/hợp đồng bảo hiểm.
```
</details>

<details open><summary>[3] BTB_BP_S1_TB1 ★✓</summary>

```text
[Bảo Việt Tâm Bình | Biểu phí | BIỂU PHÍ BẢO HIỂM BẢO VIỆT TÂM BÌNH]
(Ban hành kèm theo Quyết định số 6038/QĐ-BHBV ngày 27/06/2025 của Tổng Giám đốc Tổng Công ty Bảo hiểm Bảo Việt)
| Chương trình bảo hiểm | Cơ bản | Mở rộng | Nâng cao | Toàn diện | Ưu việt |
|---|---|---|---|---|---|
| Quyền lợi bảo hiểm chính - Điều trị nội trú do bệnh. tai nạn. thai sản |  |  |  |  |  |
| Số tiền bảo hiểm Nhóm tuổi | 60.000.000 | 100.000.000 | 160.000.000 | 220.000.000 | 330.000.000 |
| Đến 6 tuổi (phí bảo hiểm theo số tiền) | 863.000 | 1.510.000 | 1.972.000 | 2.414.000 | 3.198.000 |
| 7 tuổi đến 18 tuổi (phí bảo hiểm theo số tiền) | 535.000 | 936.000 | 1.301.000 | 1.593.000 | 2.111.000 |
| 19 tuổi đến 40 tuổi (phí bảo hiểm theo số tiền) | 584.000 | 1.021.000 | 1.420.000 | 1.738.000 | 2.303.000 |
| 41 tuổi đến 50 tuổi (phí bảo hiểm theo số tiền) | 486.000 | 851.000 | 1.183.000 | 1.448.000 | 1.919.000 |
| 51 tuổi đến 65 tuổi (phí bảo hiểm theo số tiền) | 596.000 | 1.042.000 | 1.449.000 | 1.774.000 | 2.350.000 |
```
</details>

<details open><summary>[4] C37_QT_C2 ★</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm]
QUYỀN LỢI BẢO HIỂM ĐƯỢC CHI TRẢ THEO QUY TẮC BẢO HIỂM NÀY:
Sau thời gian chờ 90 ngày kể từ ngày bắt đầu hiệu lực bảo hiểm, nếu NĐBH bị chẩn đoán mắc một hoặc nhiều bệnh/tình trạng hiểm nghèo nào (theo danh mục dưới đây) và còn sống 30 ngày sau ngày được chẩn đoán, Bảo hiểm Bảo Việt sẽ thanh toán cho NĐBH 100% số tiền bảo hiểm.
Danh mục bệnh/tình trạng hiểm nghèo được bảo hiểm:
```
</details>

<details><summary>[5] BTB_BP_S1_P4 </summary>

```text
[Bảo Việt Tâm Bình | Biểu phí | BIỂU PHÍ BẢO HIỂM BẢO VIỆT TÂM BÌNH]
| Chương trình bảo hiểm | Cơ bản | Mở rộng | Nâng cao | Toàn diện | Ưu việt |
|---|---|---|---|---|---|
| Quyền lợi bổ sung - Điều trị ngoại trú do bệnh. tai nạn. biến chứng thai sản. điều trị răng |  |  |  |  |  |
| Số tiền bảo hiểm Nhóm tuổi | 3.000.000 | 3.000.000 | 6.000.000 | 8.000.000 | 10.000.000 |
| Đến 6 tuổi (phí bảo hiểm theo số tiền) | 408.000 | 408.000 | 816.000 | 1.084.000 | 1.356.000 |
| 7 tuổi đến 18 tuổi (phí bảo hiểm theo số tiền) | 320.000 | 320.000 | 644.000 | 856.000 | 1.072.000 |
| 19 tuổi đến 40 tuổi (phí bảo hiểm theo số tiền) | 300.000 | 300.000 | 600.000 | 800.000 | 1.000.000 |
| 41 tuổi đến 50 tuổi (phí bảo hiểm theo số tiền) | 344.000 | 344.000 | 684.000 | 916.000 | 1.144.000 |
| 51 tuổi đến 65 tuổi (phí bảo hiểm theo số tiền) | 384.000 | 384.000 | 772.000 | 1.028.000 | 1.284.000 |
Đơn vị: Việt Nam Đồng
```
</details>

---

## v1-0126 · compare · medium · C37 ITC

**Câu hỏi:** Quy định về độ dài thời hạn bảo hiểm của Bảo hiểm 37 bệnh hiểm nghèo (CI37) và Bảo Việt Intercare có điểm gì khác nhau?

**Đáp án chuẩn:** Bảo hiểm CI37 quy định thời hạn bảo hiểm tối đa là 1 năm cho mỗi hợp đồng (có thể gia hạn tối đa 4 lần, mỗi lần 1 năm). Trong khi đó, Bảo Việt Intercare phân loại theo đối tượng: thời hạn là 01 năm đối với hợp đồng cá nhân, và là 01 năm hoặc ít hơn đối với hợp đồng tổ chức.

**Evidence:** `C37_QT_C4_M9 ITC_QT_C1_M53`

**Câu trả lời:**

> [1][2] Thời hạn bảo hiểm của Bảo hiểm 37 bệnh hiểm nghèo (CI37) và Bảo Việt Intercare đều là 1 năm cho hợp đồng bảo hiểm cá nhân. Tuy nhiên, Bảo hiểm 37 bệnh hiểm nghèo (CI37) cho phép gia hạn bảo hiểm tối đa 4 lần, mỗi lần 1 năm, trong khi Bảo Việt Intercare không đề cập đến việc gia hạn bảo hiểm.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] C37_QT_C1_M21 ★</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 21. Thời hạn bảo hiểm]
Thời hạn bảo hiểm được tính từ thời điểm Bảo hiểm Bảo Việt bắt đầu nhận bảo hiểm cho đến khi kết thúc bảo hiểm. Thời hạn bảo hiểm bắt đầu từ 0 giờ 1 phút sáng ngày bắt đầu hiệu lực bảo hiểm và được kết thúc vào 23 giờ 59 phút ngày hết hạn hiệu lực bảo hiểm.
Đối với hợp đồng bảo hiểm cá nhân: Thời hạn bảo hiểm là 01 năm và được quy định cụ thể trong hợp đồng bảo hiểm.
Đối với hợp đồng bảo hiểm tổ chức: Thời hạn bảo hiểm là 01 năm hoặc ít hơn, và được quy định cụ thể trong hợp đồng bảo hiểm.
```
</details>

<details open><summary>[2] ITC_QT_C1_M53 ★✓</summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN I - ĐỊNH NGHĨA > 53. Thời hạn bảo hiểm]
Thời hạn bảo hiểm được tính từ thời điểm Bảo hiểm Bảo Việt bắt đầu nhận bảo hiểm cho đến khi kết thúc bảo hiểm. Thời hạn bảo hiểm bắt đầu từ 0 giờ 1 phút sáng ngày bắt đầu hiệu lực bảo hiểm và được kết thúc vào 23 giờ 59 phút ngày hết hạn hiệu lực bảo hiểm.
Đối với hợp đồng bảo hiểm cá nhân: Thời hạn bảo hiểm là 01 năm và được quy định cụ thể trong hợp đồng bảo hiểm.
Đối với hợp đồng bảo hiểm tổ chức: Thời hạn bảo hiểm là 01 năm hoặc ít hơn, và được quy định cụ thể trong hợp đồng bảo hiểm.
```
</details>

<details><summary>[3] C37_QT_C4_M9 ✓</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG IV - Điều kiện chung > 9. Thời hạn bảo hiểm]
Thời hạn bảo hiểm tối đa là 1 năm tính từ thời điểm bảo hiểm Bảo Việt bắt đầu nhận bảo hiểm (thời điểm bắt đầu nhận bảo hiểm/ngày bắt đầu thời hạn bảo hiểm) đến khi kết thúc bảo hiểm (thời điểm kết thúc bảo hiểm/ngày kết thúc thời hạn bảo hiểm) và được ghi cụ thể trên Hợp đồng bảo hiểm. Bên mua bảo hiểm có thể yêu cầu gia hạn bảo hiểm tối đa 4 lần, mỗi lần 1 năm. Bảo hiểm Bảo Việt xem xét và được thể hiện trên Hợp đồng bảo hiểm. Trong thời gian gia hạn bảo hiểm, các điều kiện điều khoản và phí bảo hiểm không thay đổi. Sau khi kết thúc thời gian gia hạn tối đa, nếu Bên mua bảo hiểm tiếp tục tham gia bảo hiểm, Bên mua bảo hiểm sẽ phải yêu cầu ký Hợp đồng bảo hiểm mới.
```
</details>

<details><summary>[4] ITC_QT_C4_M7 </summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN IV. QUY ĐỊNH CHUNG > 7. Quyền lợi bảo hiểm]
a. Thời hạn bảo hiểm bằng một năm: được sử dụng quyền lợi bảo hiểm một năm.
b. Thời hạn bảo hiểm dưới một năm:
Bên mua bảo hiểm lựa chọn một trong hai trường hợp dưới đây:
1. Phí bảo hiểm tính theo tỷ lệ:
Quyền lợi bảo hiểm: được sử dụng quyền lợi bảo hiểm theo tỷ lệ khoảng thời gian tham gia bảo hiểm trên một năm (áp dụng cho số tiền bảo hiểm và các giới hạn phụ).
Phí bảo hiểm = tỷ lệ khoảng thời gian tham gia bảo hiểm trên một năm nhân với phí bảo hiểm năm
2. Phí bảo hiểm tính theo biểu phí ngắn hạn:
Quyền lợi bảo hiểm: được sử dụng quyền lợi bảo hiểm một năm. Biểu phí ngắn hạn:
- Thời hạn bảo hiểm đến 1 tháng = 1/4 phí bảo hiểm năm
- Thời hạn bảo hiểm đến 2 tháng = 3/8 phí bảo hiểm năm
- Thời hạn bảo hiểm đến 3 tháng = 1/2 phí bảo hiểm năm
- Thời hạn bảo hiểm đến 4 tháng = 5/8 phí bảo hiểm năm
- Thời hạn bảo hiểm đến 6 tháng = 3/4 phí bảo hiểm năm
- Thời hạn bảo hiểm đến 8 tháng = 7/8 phí bảo hiểm năm
- Thời hạn bảo hiểm trên 8 tháng = phí bảo hiểm năm
```
</details>

<details><summary>[5] C37_QT_C1_M22 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 22. Thời gian chờ]
Là khoảng thời gian mà các sự kiện bảo hiểm xảy ra sẽ không được Bảo hiểm Bảo Việt chi trả đối với các quyền lợi bảo hiểm có liên quan, không chi trả cả những trường hợp thời điểm phát sinh rủi ro nằm trong thời gian chờ nhưng chi phí phát sinh hoặc hậu quả của đợt điều trị rủi ro này lại kéo dài quá thời gian chờ quy định. Thời gian chờ được tính kể từ Ngày bắt đầu hiệu lực bảo hiểm. Đối với các hợp đồng bảo hiểm tái tục liên tục hàng năm và không thay đổi quyền lợi bảo hiểm, thời gian chờ được tính từ Ngày bắt đầu hiệu lực bảo hiểm của hợp đồng bảo hiểm năm đầu tiên.
```
</details>

---

## v1-0127 · compare · hard · FLX ITC

**Câu hỏi:** Đối với hợp đồng của khách hàng cá nhân, quy định về mốc thời gian bắt đầu, kết thúc và độ dài thời hạn bảo hiểm giữa Bảo hiểm Du lịch Flexi và Bảo Việt Intercare có điểm gì khác nhau?

**Đáp án chuẩn:** Ở Du lịch Flexi, thời hạn bảo hiểm được tính từ lúc bắt đầu chuyến đi đến khi kết thúc chuyến đi vào ngày hết hạn (theo giờ Việt Nam) với độ dài tối đa 365 ngày/chuyến. Trong khi đó, ở Bảo Việt Intercare cá nhân, thời hạn bảo hiểm được ấn định là 01 năm, tính cụ thể từ 0 giờ 1 phút sáng ngày bắt đầu hiệu lực đến 23 giờ 59 phút ngày hết hạn hiệu lực bảo hiểm.

**Evidence:** `FLX_QT_C1_M1_K32 ITC_QT_C1_M53`

**Câu trả lời:**

> [2] Bảo Việt Intercare quy định thời hạn bảo hiểm là 1 năm cho hợp đồng bảo hiểm cá nhân, được quy định cụ thể trong hợp đồng bảo hiểm.
> 
> [1] Bảo hiểm Du lịch Flexi không nêu rõ thời hạn bảo hiểm cụ thể cho hợp đồng bảo hiểm cá nhân, chỉ quy định tối đa 365 ngày cho một chuyến đi.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] FLX_QT_C1_M1_K32 ★✓</summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | I. ĐỊNH NGHĨA > 32. Thời hạn bảo hiểm]
Là khoảng thời gian từ thời điểm bắt đầu của Chuyến đi và thời điểm kết thúc của Chuyến đi vào Ngày hết hạn trong Giấy chứng nhận bảo hiểm. Thời hạn bảo hiểm được quy định trong Hợp đồng bảo hiểm/Giấy chứng nhận bảo hiểm.
Thời hạn bảo hiểm sẽ được tính theo giờ tại Việt Nam và tối đa 365 ngày cho một chuyến đi.
```
</details>

<details open><summary>[2] ITC_QT_C1_M53 ★✓</summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN I - ĐỊNH NGHĨA > 53. Thời hạn bảo hiểm]
Thời hạn bảo hiểm được tính từ thời điểm Bảo hiểm Bảo Việt bắt đầu nhận bảo hiểm cho đến khi kết thúc bảo hiểm. Thời hạn bảo hiểm bắt đầu từ 0 giờ 1 phút sáng ngày bắt đầu hiệu lực bảo hiểm và được kết thúc vào 23 giờ 59 phút ngày hết hạn hiệu lực bảo hiểm.
Đối với hợp đồng bảo hiểm cá nhân: Thời hạn bảo hiểm là 01 năm và được quy định cụ thể trong hợp đồng bảo hiểm.
Đối với hợp đồng bảo hiểm tổ chức: Thời hạn bảo hiểm là 01 năm hoặc ít hơn, và được quy định cụ thể trong hợp đồng bảo hiểm.
```
</details>

<details><summary>[3] FLX_QT_C1_M1_K10 </summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | I. ĐỊNH NGHĨA > 10. Chuyến đi]
Là hành trình mà Người được bảo hiểm thực hiện và được bảo hiểm bởi Công ty bảo hiểm theo Hợp đồng bảo hiểm này.
Chuyến đi bắt đầu có hiệu lực 03 tiếng đồng hồ trước khi Người được bảo hiểm rời Việt Nam theo lịch trình để đến điểm đến ở nước ngoài và sẽ kết thúc khi một trong những điều kiện sau đây xảy ra, tùy thời điểm nào sớm hơn:
a. Kết thúc 23 giờ 59 phút của ngày cuối cùng của thời hạn bảo hiểm ghi trên hợp đồng bảo hiểm/giấy chứng nhận bảo hiểm; hoặc
b. Thời điểm Người được bảo hiểm hoàn thành thủ tục nhập cảnh quay trở về Việt Nam (căn cứ vào dấu nhập cảnh và/hoặc vé/thẻ lên máy bay, vé phương tiện di chuyển hoặc bất kỳ giấy tờ liên quan chứng minh được Người được bảo hiểm đã hoàn thành thủ tục nhập cảnh)
```
</details>

<details><summary>[4] ITC_QT_C1_M38 </summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN I - ĐỊNH NGHĨA > 38. Ngày bắt đầu hiệu lực bảo hiểm]
Là ngày hiệu lực của hợp đồng bảo hiểm đầu tiên (được tính từ 0 giờ 1 phút của ngày quy định trên hợp đồng) khi Bên mua bảo hiểm tham gia chương trình bảo hiểm này hoặc của hợp đồng bảo hiểm tái tục liên tục hàng năm. Đối với những hợp đồng bảo hiểm không được tái tục liên tục hàng năm, ngày bắt đầu hiệu lực bảo hiểm đầu tiên là ngày hiệu lực của hợp đồng bảo hiểm mới nhất trừ khi có thỏa thuận khác.
```
</details>

<details><summary>[5] FLX_QT_C1_M1_K19 </summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | I. ĐỊNH NGHĨA > 19. Hợp đồng bảo hiểm nguyên tắc/Hợp đồng bao]
Hợp đồng bảo hiểm nguyên tắc/ Hợp đồng bao là thỏa thuận giữa bên mua bảo hiểm và công ty bảo hiểm xác lập các quyền, nghĩa vụ nhất định về việc cung cấp dịch vụ bảo hiểm cho nhiều lượt/chuyến/lần lưu trú phát sinh trong thời hạn hiệu lực bảo hiểm của hợp đồng. Theo đó, công ty bảo hiểm cam kết bồi thường cho người được bảo hiểm trong trường hợp xảy ra sự kiện thuộc phạm vi bảo hiểm được quy định trong hợp đồng. Hợp đồng bảo hiểm nguyên tắc/hợp đồng bao được thực hiện theo dạng khung cho thời hạn 1 năm hoặc theo thỏa thuận để các bên tiếp tục thực hiện các giao dịch phát sinh sau đó.
```
</details>

---

## v1-0131 · compare · hard · BVP ITC

**Câu hỏi:** Trong định nghĩa về 'Các hoạt động thể thao mạo hiểm', quy định đối với hoạt động đua và leo núi có điểm gì khác nhau giữa Bảo Việt An Gia và Bảo Việt Intercare?

**Đáp án chuẩn:** Bảo Việt An Gia áp dụng cho 'bất kỳ hoạt động đua nào' và 'leo núi' nói chung mà không kèm điều kiện. Ngược lại, Bảo Việt Intercare chỉ tính 'leo núi sử dụng dây leo', đồng thời các cuộc đua có loại trừ cuộc đua từ thiện và cuộc đua nội bộ do Bên mua bảo hiểm là doanh nghiệp tổ chức.

**Evidence:** `BVP_QT_C1_M1_K16 ITC_QT_C1_M14`

**Câu trả lời:**

> Theo tài liệu cung cấp:
> 
> - Bảo Việt An Gia quy định: "bất kỳ hoạt động đua nào" không được bảo hiểm [3].
> 
> - Bảo Việt Intercare quy định: "tham gia tập luyện hoặc tham gia thi đấu các hoạt động thể thao chuyên nghiệp, tham gia các hoạt động thể thao mạo hiểm, trừ trường hợp có thỏa thuận khác trong hợp đồng bảo hiểm." [4]
> 
> Do đó, Bảo Việt An Gia không bảo hiểm cho bất kỳ hoạt động đua nào, trong khi Bảo Việt Intercare chỉ không bảo hiểm khi đó là hoạt động đua chuyên nghiệp và có thỏa thuận khác trong hợp đồng bảo hiểm.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details><summary>[1] BVP_QT_C1_M1_K16 ✓</summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 16. Các hoạt động thể thao mạo hiểm]
Là các hoạt động trên không (trừ khi với tư cách là hành khách trên máy bay thương mại có giấy phép chở khách), môn thể thao bay lượn, nhảy dù, các môn thể thao mùa đông, hockey trên băng, đấu vật, quyền anh, môn bóng ngựa, môn lướt ván, lướt sóng, bơi thuyền buồm cách xa bờ 5 km, leo núi, tham gia vào các hoạt động khám phá không gian, các hoạt động khác như săn bắn, thám hiểm trên núi, thám hiểm Nam/Bắc Cực, tham gia lực lượng thám hiểm, bất kỳ hoạt động đua nào.
```
</details>

<details><summary>[2] ITC_QT_C1_M14 ✓</summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN I - ĐỊNH NGHĨA > 14. Các hoạt động thể thao mạo hiểm]
Là các hoạt động trên không (trừ khi đi lại bằng đường hàng không), các môn thể thao mùa đông, môn thể thao bay lượn, săn bắn, hockey trên băng, nhảy dù, đấu vật, môn bóng ngựa, môn lướt ván, bơi thuyền buồm cách xa bờ 5 km, lặn dưới nước có sử dụng thiết bị lặn, phóng lao, đấm bốc, leo núi sử dụng dây leo, các cuộc đua (không bao gồm các cuộc đua mang tính chất từ thiện, các cuộc đua mang tính chất nội bộ do Bên mua bảo hiểm là doanh nghiệp tổ chức).
```
</details>

<details open><summary>[3] BVP_QT_C3_K8-18 ★</summary>

```text
[Bảo Việt An Gia | Quy tắc | CHƯƠNG III - Các điểm loại trừ chung]
8. Tai nạn xảy ra ngoài thời hạn bảo hiểm; chi phí y tế xảy ra ngoài thời hạn bảo hiểm là hậu quả của tai nạn xảy ra trong thời hạn bảo hiểm.
9. Khám và điều trị không theo quy trình của bệnh viện/phòng khám; các chỉ định điều trị không theo quy trình/phác đồ của Bộ y tế.
10. Tham gia vào các hoạt động hàng không (trừ khi với tư cách là hành khách trên các chuyến bay thương mại), tham gia các cuộc diễn tập huấn luyện quân sự, tham gia chiến đấu của lực lượng vũ trang.
11. Những rủi ro mang tính chất thảm họa như động đất, núi lửa, sóng thần; nhiễm phóng xạ; dịch bệnh truyền nhiễm nhóm A,B/đại dịch/tình trạng y tế khẩn cấp theo công bố của WHO hoặc Cơ quan Nhà nước có thẩm quyền.
12. Các rủi ro phát sinh từ hoặc liên quan đến chiến tranh, nội chiến, đình công, khủng bố, bạo động, dân biến, tiến hành bạo động vũ trang làm rối loạn trật tự xã hội, phiến loạn, các hoạt động dân sự hoặc hành động của bất kỳ người cầm đầu của tổ chức nào nhằm lật đổ, đe dọa chính quyền, kiểm soát bằng vũ lực.
13. Tham gia tập luyện hoặc tham gia thi đấu các hoạt động thể thao chuyên nghiệp, tham gia các hoạt động thể thao mạo hiểm, bất kỳ hoạt động đua nào (bao gồm hợp pháp và bất hợp pháp).
14. Bệnh lao các loại, bệnh nghề nghiệp.
15. Bệnh ung thư (tất cả các quyền lợi bảo hiểm); các chi phí y tế liên quan đến khám/điều trị cho phần cơ thể bị ung thư.
16. Người bị bệnh ung thư trước khi tham gia bảo hiểm; Người đang trong thời gian điều trị nội trú thương tật hoặc bệnh tật, người bị thương tật vĩnh viễn trên 50% tại thời điểm tham gia hoặc thời điểm hợp đồng bảo hiểm bắt đầu có hiệu lực.
17. Mọi quyền lợi phát sinh cho người không thuộc đối tượng tham gia bảo hiểm.
18. Các bệnh suy tủy, bạch cầu, điều trị lọc máu, chạy thận nhân tạo, suy thận, và hậu quả hay biến chứng của các bệnh này.
```
</details>

<details open><summary>[4] ITC_QT_C3_K10-15 ★</summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN III. CÁC ĐIỂM LOẠI TRỪ CHUNG]
10. Các chi phí khám và điều trị liên quan đến răng bao gồm cả điều trị nội trú và ngoại trú, trừ điều trị cấp cứu tai nạn răng khẩn cấp và trường hợp có tham gia quyền lợi bổ sung Bảo hiểm nha khoa.
11. Tham gia vào các hoạt động hàng không (trừ khi với tư cách là hành khách trên các chuyến bay thương mại), tham gia các cuộc diễn tập huấn luyện quân sự, tham gia chiến đấu của lực lượng vũ trang.
12. Những rủi ro mang tính chất thảm họa như động đất, núi lửa, sóng thần; nhiễm phóng xạ; dịch bệnh truyền nhiễm nhóm A,B/đại dịch/tình trạng y tế khẩn cấp theo công bố của WHO hoặc Cơ quan Nhà nước có thẩm quyền.
13. Các rủi ro phát sinh từ hoặc liên quan đến chiến tranh, nội chiến, đình công, khủng bố, bạo động, dân biến, tiến hành bạo động vũ trang làm rối loạn trật tự xã hội, phiến loạn, các hoạt động dân sự hoặc hành động của bất kỳ người cầm đầu của tổ chức nào nhằm lật đổ, đe dọa chính quyền, kiểm soát bằng vũ lực.
14. Tham gia tập luyện hoặc tham gia thi đấu các hoạt động thể thao chuyên nghiệp, tham gia các hoạt động thể thao mạo hiểm, trừ trường hợp có thỏa thuận khác trong hợp đồng bảo hiểm.
15. Kiểm tra và điều trị các bệnh lây qua đường tình dục như: hạ cam mềm, u hạt bẹn, lậu, giang mai, herpes sinh dục, sùi mào gà (mồng gà), HPV sinh dục, bệnh do rận mu (chấy cua), chlamydia, trichomonas, trùng roi, bệnh hột xoài (u lympho sinh dục), nhiễm cytomegalo virus, u mềm lây ở người trên 10 tuổi, hội chứng suy giảm miễn dịch mắc phải (AIDS), tình trạng và bệnh liên quan đến virut HIV, các bệnh lây qua đường tình dục khác; và mọi biến chứng/hậu quả liên quan đến những bệnh/hội chứng/tình trạng kể trên.
```
</details>

<details><summary>[5] BVP_QT_C1_M1_K15 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 15. Các hoạt động thể thao chuyên nghiệp]
Là các hoạt động thể thao mang lại nguồn thu nhập chính và thường xuyên cho Người được bảo hiểm.
```
</details>

---

## v1-0041 · scenario · easy · C37

**Câu hỏi:** Bà Mai tham gia sản phẩm Bảo hiểm 37 bệnh hiểm nghèo (CI37). Sau đó, bà được bác sĩ chẩn đoán mắc Hội chứng CREST và làm hồ sơ yêu cầu bồi thường quyền lợi bệnh Xơ cứng bì tiến triển. Trường hợp của bà Mai có được bảo hiểm CI37 chi trả không?

**Đáp án chuẩn:** Bà Mai không được chi trả quyền lợi bảo hiểm. Theo quy tắc sản phẩm CI37, Hội chứng CREST là trường hợp nằm trong danh mục loại trừ của bệnh Xơ cứng bì tiến triển.

**Evidence:** `C37_QT_C2_M32`

**Câu trả lời:**

> [1][5] Trường hợp của bà Mai không được chi trả bởi Bảo hiểm Bảo Việt. Theo quy tắc bảo hiểm, Hội chứng CREST được liệt kê trong các điểm loại trừ, nghĩa là Bảo hiểm Bảo Việt không chịu trách nhiệm chi trả tiền bảo hiểm cho các bệnh/tình trạng phát sinh liên quan hay hậu quả của Hội chứng CREST. [1]

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] C37_QT_C2_M32 ★✓</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > 32. Xơ cứng bì tiến triển]
Bệnh lý mạch máu – chất tạo keo hệ thống gây ra tình trạng xơ cứng lan tỏa và tiến triển ở da, mạch máu và cơ quan nội tạng. Chẩn đoán phải rõ ràng dựa vào sinh thiết và có bằng chứng về huyết thanh học và rối loạn này chắc chắn sẽ ảnh hưởng đến tim, phổi hoặc thận. Loại trừ những trường hợp sau:
• Xơ cứng bì khu trú (xơ cứng bì tuyến tính hoặc morphea);
• Viêm cân mạc tăng bạch cầu ái toan;
• Hội chứng CREST.
```
</details>

<details><summary>[2] C37_QT_C2 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm]
QUYỀN LỢI BẢO HIỂM ĐƯỢC CHI TRẢ THEO QUY TẮC BẢO HIỂM NÀY:
Sau thời gian chờ 90 ngày kể từ ngày bắt đầu hiệu lực bảo hiểm, nếu NĐBH bị chẩn đoán mắc một hoặc nhiều bệnh/tình trạng hiểm nghèo nào (theo danh mục dưới đây) và còn sống 30 ngày sau ngày được chẩn đoán, Bảo hiểm Bảo Việt sẽ thanh toán cho NĐBH 100% số tiền bảo hiểm.
Danh mục bệnh/tình trạng hiểm nghèo được bảo hiểm:
```
</details>

<details><summary>[3] C37_QT_C1_M22 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 22. Thời gian chờ]
Là khoảng thời gian mà các sự kiện bảo hiểm xảy ra sẽ không được Bảo hiểm Bảo Việt chi trả đối với các quyền lợi bảo hiểm có liên quan, không chi trả cả những trường hợp thời điểm phát sinh rủi ro nằm trong thời gian chờ nhưng chi phí phát sinh hoặc hậu quả của đợt điều trị rủi ro này lại kéo dài quá thời gian chờ quy định. Thời gian chờ được tính kể từ Ngày bắt đầu hiệu lực bảo hiểm. Đối với các hợp đồng bảo hiểm tái tục liên tục hàng năm và không thay đổi quyền lợi bảo hiểm, thời gian chờ được tính từ Ngày bắt đầu hiệu lực bảo hiểm của hợp đồng bảo hiểm năm đầu tiên.
```
</details>

<details><summary>[4] C37_QT_C3_K1-4 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG III - CÁC ĐIỂM LOẠI TRỪ CHUNG]
Bảo hiểm Bảo Việt không chịu trách nhiệm chi trả tiền bảo hiểm đối với những rủi ro, điều kiện, hành động, nguyên nhân, phương pháp điều trị, bệnh/tình trạng như được liệt kê sau đây và các bệnh/tình trạng phát sinh liên quan hay hậu quả của chúng:
1. Trường hợp Bên mua bảo hiểm/Người được bảo hiểm kê khai/cung cấp thông tin không trung thực hay không đầy đủ về tình trạng bệnh/thương tật trong giấy yêu cầu bảo hiểm, Bảo hiểm Bảo Việt có quyền giảm trách nhiệm toàn bộ hoặc một phần đối với khiếu nại bồi thường của hợp đồng bảo hiểm.
2. Người được bảo hiểm điều khiển phương tiện tham gia giao thông mà trong máu hoặc hơi thở có nồng độ cồn vượt quá 50 miligam/100 mililít máu hoặc 0,25 miligam/1 lít khí thở; hoặc vi phạm những quy định khác của Luật trật tự, an toàn giao thông đường bộ (và các sửa đổi, bổ sung, thay thế nếu có).
3. Các hành động đánh nhau của Người được bảo hiểm, trừ khi chứng minh được bằng văn bản xác nhận của cơ quan có thẩm quyền về việc hành động đánh nhau đó chỉ với mục đích tự vệ.
4. Tham gia vào các hoạt động hàng không (trừ khi với tư cách là hành khách trên các chuyến bay thương mại), tham gia các cuộc diễn tập huấn luyện quân sự, tham gia chiến đấu của lực lượng vũ trang.
```
</details>

<details open><summary>[5] C37_QT_C5_M1 ★</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG V - Thủ tục bồi thường > 1. Hồ sơ yêu cầu bồi thường]
Thời hạn yêu cầu trả tiền bảo hiểm hoặc bồi thường theo hợp đồng bảo hiểm là một (01) năm, kể từ ngày xảy ra sự kiện bảo hiểm. Thời gian xảy ra sự kiện bất khả kháng hoặc trở ngại khách quan khác không tính vào thời hạn yêu cầu trả tiền bảo hiểm hoặc bồi thường.
Khi yêu cầu bồi thường, BMBH/NĐBH hoặc người thụ hưởng hợp pháp hoặc người được ủy quyền phải gửi các chứng từ sau đây cho CTBH. Các tài liệu bao gồm:
- Giấy yêu cầu bồi thường được kê khai đầy đủ, có chữ ký của NĐBH hoặc người yêu cầu bồi thường (Người thừa kế/người thụ hưởng/người được chỉ định trên HĐBH/người được ủy quyền hợp pháp của NĐBH);
- Các chứng từ y tế liên quan: chứng từ chẩn đoán, kết luận của bác sỹ, bằng chứng lâm sàng, giấy xuất viện, báo cáo y tế, chứng nhận phẫu thuật, xạ trị, bằng chứng mô học và xét nghiệm, kết quả xét nghiệm phóng xạ, tế bào học, và những kết quả xét nghiệm chụp chiếu khác (để làm căn cứ xác định rõ sự kiện bảo hiểm). NĐBH có thể nộp bản sao của các tài liệu gốc được xác nhận bởi CTBH hoặc đại diện của CTBH sau khi đối chứng với bản gốc. Trong mọi trường hợp, CTBH có quyền yêu cầu bản gốc để kiểm tra;
- Chi phí cho việc cung cấp các tài liệu nêu trên sẽ do NĐBH chịu.
- Trong trường hợp có tranh chấp hoặc không đồng ý về kết quả chẩn đoán bệnh/tình trạng hiểm nghèo/thương tật do người yêu cầu bồi thường cung cấp, CTBH có quyền yêu cầu NĐBH tiến hành kiểm tra y tế, bao gồm nhưng không giới hạn việc cung cấp bằng chứng về tiền sử sức khỏe, chẩn đoán lại, tiến hành xét nghiệm và chụp chiếu lại, nếu cần thiết, tại một bệnh viện khác. Chi phí cho việc cung cấp các tài liệu hoặc bằng chứng đó do CTBH chi trả. NĐBH phải tuân thủ các kết quả/bằng chứng cuối cùng này.
```
</details>

---

## v1-0048 · scenario · medium · ITC

**Câu hỏi:** Chị Mai (28 tuổi) đang tham gia bảo hiểm Bảo Việt Intercare. Khi đang mang thai, chị bị tai nạn giao thông dẫn đến chấn thương phải nhập viện cấp cứu. Sau khi xử lý cấp cứu ban đầu, bác sĩ chỉ định chị tiếp tục nằm viện để dưỡng thai nhằm tránh rủi ro do hậu quả tai nạn để lại. Chi phí dưỡng thai này có được Bảo hiểm Bảo Việt chi trả theo quyền lợi điều trị tai nạn thai kỳ khẩn cấp không?

**Đáp án chuẩn:** Chi phí dưỡng thai không được chi trả. Theo quy tắc của Bảo Việt Intercare, quyền lợi điều trị tai nạn thai kỳ khẩn cấp loại trừ toàn bộ chi phí liên quan đến việc sinh nở và hậu quả của tai nạn (như dưỡng thai, nuôi phôi...).

**Evidence:** `ITC_QT_C2_A_M11`

**Câu trả lời:**

> [1] Không được chi trả. Theo quy định tại [1], quyền lợi chi trả chi phí điều trị tai nạn thai kỳ khẩn cấp chỉ áp dụng cho chi phí điều trị cấp cứu ngay sau khi tai nạn xảy ra. Hậu quả của tai nạn như dưỡng thai không được chi trả.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] ITC_QT_C2_A_M11 ★✓</summary>

```text
[Bảo Việt Intercare | Quy tắc | A. Quyền lợi bảo hiểm chính: Điều trị nội trú do bệnh, tai nạn > 11. Chi phí điều trị tai nạn thai kỳ khẩn cấp ngay sau khi tai nạn]
Nếu Người được bảo hiểm bị tai nạn dẫn đến thương tổn đối với bà mẹ hoặc thai nhi cần phải điều trị cấp cứu thì Bảo hiểm Bảo Việt sẽ chi trả những chi phí thực tế phát sinh, hợp lý và cần thiết cho những điều trị đó nhưng tối đa không vượt quá mức giới hạn phụ quy định trong bảng quyền lợi bảo hiểm. Tuy nhiên, quyền lợi này loại trừ mọi chi phí liên quan đến việc sinh nở và hậu quả của tai nạn (như dưỡng thai, nuôi phôi v.v...)
```
</details>

<details><summary>[2] ITC_QT_C2_A_M1 </summary>

```text
[Bảo Việt Intercare | Quy tắc | A. Quyền lợi bảo hiểm chính: Điều trị nội trú do bệnh, tai nạn > 1. Tiền phòng, giường]
Bảo hiểm Bảo Việt sẽ chi trả cho các chi phí tiền phòng, giường trong quá trình điều trị nội trú và điều trị trong ngày, bao gồm tiền ăn theo tiêu chuẩn điều trị (tức là do bệnh viện cung cấp theo tiêu chuẩn phòng nằm của bệnh viện). Bảo hiểm Bảo Việt không chi trả cho các chi phí khác phát sinh như: điện thoại, báo, tiếp khách, mỹ phẩm.
Bảo hiểm Bảo Việt không chi trả quyền lợi bảo hiểm này nếu như về mặt y khoa các điều trị này có thể được điều trị ngoại trú.
```
</details>

<details><summary>[3] ITC_QT_C2_A_M15 </summary>

```text
[Bảo Việt Intercare | Quy tắc | A. Quyền lợi bảo hiểm chính: Điều trị nội trú do bệnh, tai nạn > 15. Chi phí điều trị phòng cấp cứu]
Bảo hiểm Bảo Việt sẽ trả những chi phí điều trị tiến hành trong vòng 24 giờ tại phòng khám cấp cứu của bệnh viện cho việc cấp cứu do tai nạn hoặc ốm bệnh khẩn cấp theo định nghĩa Điều trị cấp cứu. Giới hạn bảo hiểm được ghi rõ trong bảng quyền lợi bảo hiểm.
```
</details>

<details><summary>[4] ITC_QT_C3_K1-9 </summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN III. CÁC ĐIỂM LOẠI TRỪ CHUNG]
Các điểm loại trừ dưới đây áp dụng với tất cả các quyền lợi bảo hiểm bao gồm cả quyền lợi bổ sung.
Bảo hiểm Bảo Việt không chịu trách nhiệm chi trả tiền bảo hiểm đối với những rủi ro, hạng mục được liệt kê sau đây và các chi phí phát sinh liên quan hay hậu quả của chúng:
1. Các chi phí điều trị bất hợp lý, không cần thiết về mặt y tế, không theo thông lệ hợp lý và không theo chỉ định của bác sĩ.
2. Không bảo hiểm trong năm đầu tiên tham gia bảo hiểm đối với: bệnh đặc biệt, bệnh có sẵn như định nghĩa.
3. Hành động cố ý của Người được bảo hiểm hoặc người thừa kế hợp pháp.
4. Người được bảo hiểm từ 14 tuổi trở lên vi phạm pháp luật bị khởi tố hình sự; vi phạm nội quy, quy định của chính quyền địa phương hoặc các tổ chức xã hội, vi phạm nội quy của cơ quan theo Luật lao động.
5. Người được bảo hiểm điều khiển phương tiện tham gia giao thông mà trong máu hoặc hơi thở có nồng độ cồn vượt quá 50 miligam/100 mililít máu hoặc 0,25 miligam/1 lít khí thở; hoặc vi phạm những quy định khác của Luật trật tự, an toàn giao thông đường bộ (và các sửa đổi, bổ sung, thay thế nếu có).
6. Người được bảo hiểm bị tác động bởi chất kích thích, chất gây nghiện, thuốc cai nghiện, thuốc không được bác sĩ chuyên môn kê toa, rượu, bia hoặc các chất có cồn và việc ảnh hưởng này là nguyên nhân gây ra tai nạn.
7. Hậu quả của việc sử dụng ma túy, các chất có cồn; điều trị nghiện.
8. Các chi phí để có cơ quan cấy ghép nội tạng như cho, nhận, mua, vận chuyển, bảo quản nội tạng. Tuy nhiên, hợp đồng bảo hiểm này bảo hiểm cho các chi phí y tế cho việc cấy ghép nội tạng vào cơ thể.
9. Bất kỳ hành động cố ý phạm pháp hoặc ẩu đả của Người được bảo hiểm, trừ khi là hành động cứu người, bảo vệ tài sản hoặc tự vệ có văn bản xác nhận của cơ quan có thẩm quyền.
```
</details>

<details><summary>[5] ITC_QT_C2 </summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN II - PHẠM VI BẢO HIỂM VÀ QUYỀN LỢI BẢO HIỂM]
Bảo hiểm Bảo Việt chi trả quyền lợi thuộc phạm vi bảo hiểm căn cứ theo các giới hạn phụ và số tiền bảo hiểm được ghi trong Hợp đồng bảo hiểm. Trong mọi trường hợp, số tiền chi trả bảo hiểm tối đa không vượt quá Số tiền bảo hiểm. Các khoản chi phí y tế phát sinh được giới hạn theo chi phí thực tế, thông lệ và hợp lý.
```
</details>

---

## v1-0050 · scenario · medium · BVP

**Câu hỏi:** Anh Hoàng (35 tuổi) tham gia bảo hiểm Bảo Việt An Gia được 6 tháng thì phải nhập viện phẫu thuật do bệnh trĩ. Trường hợp của anh Hoàng có được bảo hiểm chi trả chi phí điều trị không?

**Đáp án chuẩn:** Anh Hoàng không được chi trả chi phí điều trị. Theo quy tắc của Bảo Việt An Gia, bệnh trĩ thuộc danh mục các bệnh loại trừ, không được bảo hiểm trong năm đầu tiên tham gia cho dù phát sinh trước hay sau khi hợp đồng có hiệu lực.

**Evidence:** `BVP_QT_C3_K46-47`

**Câu trả lời:**

> [1] Trong trường hợp của anh Hoàng (35 tuổi) tham gia bảo hiểm Bảo Việt An Gia và phải nhập viện phẫu thuật do bệnh trĩ, anh Hoàng có thể được chi trả chi phí điều trị theo quyền lợi bảo hiểm.
> 
> Theo tài liệu [1], Bảo hiểm Bảo Việt sẽ chi trả cho Người được bảo hiểm các chi phí y tế thực tế thuộc phạm vi bảo hiểm phát sinh cho một ca phẫu thuật nội trú, bao gồm chi phí thuốc, vật tư tiêu hao, các thiết bị cần thiết và hợp lý theo chỉ định của bác sĩ, chi phí phòng mổ, phẫu thuật viên, các chi phí gây mê, các chi phí hội chẩn trước khi mổ và hồi sức sau khi mổ, chi phí tái mổ, chi phí cấy ghép nội tạng trừ những điểm loại trừ quy định tại hợp đồng bảo hiểm/quy tắc bảo hiểm.
> 
> Tài liệu sản phẩm hiện có không có thông tin để xác định bệnh trĩ có nằm trong phạm vi bảo hiểm hay không. Do đó, cần kiểm tra thêm thông tin trong hợp đồng bảo hiểm cụ thể của anh Hoàng.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] BVP_QT_C2_M1_A_K5-8 ★</summary>

```text
[Bảo Việt An Gia | Quy tắc | I. QUYỀN LỢI BẢO HIỂM CHÍNH: ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, BIẾN CHỨNG THAI SẢN > A. Quyền lợi bảo hiểm]
5. Chi phí phẫu thuật
Bảo hiểm Bảo Việt sẽ chi trả cho Người được bảo hiểm các chi phí y tế thực tế thuộc phạm vi bảo hiểm phát sinh cho một ca phẫu thuật nội trú như định nghĩa, bao gồm chi phí thuốc, vật tư tiêu hao, các thiết bị cần thiết và hợp lý theo chỉ định của bác sĩ mà không bị loại trừ bảo hiểm, chi phí phòng mổ, phẫu thuật viên, các chi phí gây mê, các chi phí hội chẩn trước khi mổ và hồi sức sau khi mổ, chi phí tái mổ, chi phí cấy ghép nội tạng trừ những điểm loại trừ quy định tại hợp đồng bảo hiểm/quy tắc bảo hiểm. Giới hạn số tiền chi trả cho trường hợp phẫu thuật không vượt mức giới hạn tối
đa do Người được bảo hiểm lựa chọn khi tham gia bảo hiểm và được ghi cụ thể trong hợp đồng bảo hiểm.
Trường hợp phẫu thuật trong ngày và phẫu thuật ngoại trú không được chi trả trong quyền lợi này.
6. Phục hồi chức năng
7. Trợ cấp bệnh viện công (không quá 60 ngày/năm)
Bảo hiểm Bảo Việt chi trả số tiền trợ cấp ghi trên bảng quyền lợi bảo hiểm cho mỗi ngày nằm viện điều trị nội trú do bệnh, tai nạn tại các bệnh viện công lập.
8. Trợ cấp mai táng phí trong trường hợp tử vong tại bệnh viện.
Trường hợp Người được bảo hiểm tử vong khi nằm viện thuộc phạm vi trách nhiệm bảo hiểm, Bảo hiểm Bảo Việt sẽ trả tiền trợ cấp mai táng phí ghi trên hợp đồng bảo hiểm.
```
</details>

<details><summary>[2] BVP_QT_C1_M1_K29 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 29. Hệ thống bảo lãnh viện phí]
Là hệ thống các cơ sở y tế có ký kết thỏa thuận cung cấp dịch vụ bảo lãnh viện phí với Bảo hiểm Bảo Việt. Người được bảo hiểm khi khám và điều trị tại những cơ sở y tế này sẽ được Bảo hiểm Bảo Việt bảo lãnh thanh toán tùy theo chương trình bảo hiểm tham gia đối với các chi phí phát sinh thuộc phạm vi bảo hiểm và theo hạn mức quy định trong hợp đồng bảo hiểm. Người được bảo hiểm phải tự chi trả cho những chi phí không thuộc phạm vi bảo hiểm và/hoặc những chi phí vượt quá mức trách nhiệm đã tham gia trong hợp đồng bảo hiểm tại thời điểm điều trị.
Danh sách các cơ sở y tế trong hệ thống bảo lãnh viện phí có thể thay đổi và được cập nhật thường xuyên trên trang thông tin điện tử chính thức của Bảo hiểm Bảo Việt.
```
</details>

<details><summary>[3] BVP_QT_C3_K1-7 </summary>

```text
[Bảo Việt An Gia | Quy tắc | CHƯƠNG III - Các điểm loại trừ chung]
(Áp dụng cho Quyền lợi bảo hiểm chính và tất cả các Quyền lợi bảo hiểm bổ sung)
Bảo hiểm Bảo Việt không chịu trách nhiệm chi trả tiền bảo hiểm đối với những rủi ro, hạng mục, điều kiện, các hành động, nguyên nhân, bệnh, phương pháp điều trị như được liệt kê sau đây và các chi phí phát sinh liên quan hay hậu quả của chúng:
1. Các chi phí điều trị bất hợp lý, không cần thiết về mặt y tế, không theo thông lệ hợp lý và không theo chỉ định của bác sĩ.
2. Hành động cố ý gây hại cho bản thân hoặc cho đối tượng khác của Người được bảo hiểm hoặc Người thừa kế hợp pháp.
3. Trường hợp Bên mua bảo hiểm/Người được bảo hiểm kê khai/cung cấp thông tin không trung thực hay không đầy đủ về tình trạng bệnh/thương tật trong giấy yêu cầu bảo hiểm, Bảo hiểm Bảo Việt có quyền giảm trách nhiệm toàn bộ hoặc một phần đối với khiếu nại bồi thường của hợp đồng bảo hiểm.
4. Người được bảo hiểm từ 14 tuổi trở lên vi phạm pháp luật bị khởi tố hình sự; vi phạm nội quy, quy định của chính quyền địa phương hoặc các tổ chức xã hội; vi phạm nội quy của cơ quan theo Luật lao động.
5. Người được bảo hiểm điều khiển phương tiện tham gia giao thông mà trong máu hoặc hơi thở có nồng độ cồn vượt quá 50 miligam/100 mililít máu hoặc 0,25 miligam/1 lít khí thở; hoặc vi phạm những quy định khác của Luật trật tự, an toàn giao thông đường bộ (và các sửa đổi, bổ sung, thay thế nếu có).
6. Người được bảo hiểm bị tai nạn/thương tật trong tình trạng sử dụng rượu/bia, ma túy, chất kích thích, chất gây nghiện. Các rủi ro phát sinh trực tiếp hoặc gián tiếp từ việc: Người được bảo hiểm nghiện rượu/bia, ma túy, chất kích thích; hoặc sử dụng, lạm dụng hay nghiện bất cứ chất có cồn/chất kích thích/chất gây nghiện nào.
7. Các hành động đánh nhau của Người được bảo hiểm, trừ khi chứng minh được bằng văn bản xác nhận của cơ quan có thẩm quyền về việc hành động đánh nhau đó chỉ với mục đích tự vệ.
```
</details>

<details><summary>[4] BVP_QT_C2_M1_A_K2-4 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. QUYỀN LỢI BẢO HIỂM CHÍNH: ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, BIẾN CHỨNG THAI SẢN > A. Quyền lợi bảo hiểm]
2. Chi phí khám trước khi nhập viện (trong vòng 30 ngày trước khi nhập viện)
Bảo hiểm Bảo Việt sẽ chi trả cho Người được bảo hiểm các chi phí khám, kiểm tra, siêu âm, chụp chiếu, xét nghiệm cơ bản và tiền thuốc theo chỉ định của bác sĩ, liên quan trực tiếp đến bệnh/thương tật cần phải nhập viện, và là cơ sở trực tiếp để bác sĩ đưa ra chỉ định nhập viện để điều trị. Chi phí khám trước khi nhập viện chỉ được chấp nhận một lần gần nhất được thực hiện trong vòng 30 ngày trước khi nhập viện.
3. Chi phí tái khám sau khi xuất viện (trong vòng 30 ngày sau khi xuất viện)
Bảo hiểm Bảo Việt sẽ chi trả cho Người được bảo hiểm các chi phí y tế
phát sinh theo chỉ định của bác sĩ ngay khi Người được bảo hiểm xuất viện
và có liên quan trực tiếp đến đợt điều trị nội trú trước đó. Các chi phí này
bao gồm chi phí khám, xét nghiệm, chẩn đoán hình ảnh và thuốc phát sinh
trong vòng 30 ngày kể từ ngày Người được bảo hiểm xuất viện.
4. Dịch vụ xe cứu thương, xe cấp cứu đường bộ
Bảo hiểm Bảo Việt sẽ chi trả cho chi phí sử dụng xe cứu thương/xe cấp cứu bằng đường bộ (không phải là dịch vụ vận chuyển bằng đường hàng không) trong trường hợp Người được bảo hiểm trong tình trạng bệnh/tai nạn nguy kịch ảnh hưởng đến tính mạng buộc phải đưa Người được bảo hiểm đến bệnh viện/phòng khám gần nhất hoặc từ bệnh viện này đến bệnh viện khác theo chỉ định của bác sĩ.
```
</details>

<details><summary>[5] BVP_QT_C4_M2_K1 </summary>

```text
[Bảo Việt An Gia | Quy tắc | CHƯƠNG IV: THỦ TỤC YÊU CẦU BỒI THƯỜNG VÀ BẢO LÃNH VIỆN PHÍ > II. THỦ TỤC TRẢ TIỀN BẢO HIỂM VÀ BẢO LÃNH VIỆN PHÍ]
1. Trường hợp ứng tiền trước, nộp hồ sơ yêu cầu bồi thường sau:
Trường hợp Người được bảo hiểm không sử dụng hoặc không được sử dụng dịch vụ bảo lãnh viện phí trực tiếp, hoặc khám và điều trị tại các bệnh viện/phòng khám hợp pháp nhưng không thuộc hệ thống bảo lãnh viện phí của chương trình, Người được bảo hiểm phải thanh toán mọi chi phí khám/điều trị trước, sau đó gửi toàn bộ hồ sơ cho Bảo hiểm Bảo Việt để thanh toán phần chi phí thuộc phạm vi bảo hiểm.
a. Thời hạn bồi thường:
Khi xảy ra sự kiện bảo hiểm, Bảo hiểm Bảo Việt có trách nhiệm giải quyết và chi trả tiền bảo hiểm theo thời hạn đã thoả thuận trong Hợp đồng bảo hiểm; trong trường hợp không có thoả thuận trong hợp đồng thì Bảo hiểm Bảo Việt thông báo kết quả và giải quyết bồi thường cho người được bảo hiểm, người thừa kế, hoặc người đại diện hợp pháp trong thời hạn tối đa 15 ngày làm việc, kể từ ngày nhận được bộ hồ sơ đầy đủ hợp lệ.
b. Thông tin chung về chi trả bảo hiểm:
Tất cả các chứng từ và tài liệu (bao gồm các hóa đơn gốc, giấy chứng nhận, các chiếu chụp X-quang...) mà Bảo hiểm Bảo Việt yêu cầu hỗ trợ cho việc chi trả bảo hiểm (bồi thường), bao gồm cả các kết quả về sức khỏe và bất kỳ các chi tiết nào về các tiền sử sức khỏe của Người được bảo hiểm sẽ phải được cung cấp miễn phí cho Bảo hiểm Bảo Việt, nếu
- Tiền bảo hiểm sẽ được chi trả cho Người được bảo hiểm hoặc Người thừa kế/Người thụ hưởng/Người được ủy quyền hợp pháp của Người được bảo hiểm theo đúng quy định của Pháp luật. Trong trường hợp Người được bảo hiểm không chỉ định Người thụ hưởng, hoặc Người thụ hưởng đã qua đời hoặc mất tích trong một thời gian nhất định, Bảo hiểm Bảo Việt trả tiền bồi thường cho Người thừa kế hợp pháp theo pháp luật về thừa kế.
```
</details>

---

## v1-0051 · scenario · easy · C37

**Câu hỏi:** Anh Nam tham gia gói Bảo hiểm 37 bệnh hiểm nghèo (CI37). Vừa qua, anh gặp tai nạn khi đang điều khiển xe máy và kết quả đo nồng độ cồn trong máu là 65 miligam/100 mililít máu, dẫn đến biến chứng bệnh hiểm nghèo. Trường hợp này anh Nam có được Bảo hiểm Bảo Việt chi trả quyền lợi không?

**Đáp án chuẩn:** Anh Nam không được chi trả quyền lợi bảo hiểm. Theo quy tắc sản phẩm, Bảo hiểm Bảo Việt loại trừ trách nhiệm khi Người được bảo hiểm điều khiển phương tiện tham gia giao thông mà nồng độ cồn trong máu vượt quá 50 miligam/100 mililít máu.

**Evidence:** `C37_QT_C3_K1-4`

**Câu trả lời:**

> [1]
> 
> Trường hợp anh Nam điều khiển phương tiện tham gia giao thông mà trong máu có nồng độ cồn vượt quá 50 miligam/100 mililít máu, Bảo hiểm Bảo Việt có quyền giảm trách nhiệm toàn bộ hoặc một phần đối với khiếu nại bồi thường của hợp đồng bảo hiểm. Do kết quả đo nồng độ cồn của anh Nam là 65 miligam/100 mililít máu, vượt quá ngưỡng cho phép, nên anh Nam không được Bảo hiểm Bảo Việt chi trả quyền lợi trong trường hợp này.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] C37_QT_C3_K1-4 ★✓</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG III - CÁC ĐIỂM LOẠI TRỪ CHUNG]
Bảo hiểm Bảo Việt không chịu trách nhiệm chi trả tiền bảo hiểm đối với những rủi ro, điều kiện, hành động, nguyên nhân, phương pháp điều trị, bệnh/tình trạng như được liệt kê sau đây và các bệnh/tình trạng phát sinh liên quan hay hậu quả của chúng:
1. Trường hợp Bên mua bảo hiểm/Người được bảo hiểm kê khai/cung cấp thông tin không trung thực hay không đầy đủ về tình trạng bệnh/thương tật trong giấy yêu cầu bảo hiểm, Bảo hiểm Bảo Việt có quyền giảm trách nhiệm toàn bộ hoặc một phần đối với khiếu nại bồi thường của hợp đồng bảo hiểm.
2. Người được bảo hiểm điều khiển phương tiện tham gia giao thông mà trong máu hoặc hơi thở có nồng độ cồn vượt quá 50 miligam/100 mililít máu hoặc 0,25 miligam/1 lít khí thở; hoặc vi phạm những quy định khác của Luật trật tự, an toàn giao thông đường bộ (và các sửa đổi, bổ sung, thay thế nếu có).
3. Các hành động đánh nhau của Người được bảo hiểm, trừ khi chứng minh được bằng văn bản xác nhận của cơ quan có thẩm quyền về việc hành động đánh nhau đó chỉ với mục đích tự vệ.
4. Tham gia vào các hoạt động hàng không (trừ khi với tư cách là hành khách trên các chuyến bay thương mại), tham gia các cuộc diễn tập huấn luyện quân sự, tham gia chiến đấu của lực lượng vũ trang.
```
</details>

<details><summary>[2] C37_QT_C1_M22 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 22. Thời gian chờ]
Là khoảng thời gian mà các sự kiện bảo hiểm xảy ra sẽ không được Bảo hiểm Bảo Việt chi trả đối với các quyền lợi bảo hiểm có liên quan, không chi trả cả những trường hợp thời điểm phát sinh rủi ro nằm trong thời gian chờ nhưng chi phí phát sinh hoặc hậu quả của đợt điều trị rủi ro này lại kéo dài quá thời gian chờ quy định. Thời gian chờ được tính kể từ Ngày bắt đầu hiệu lực bảo hiểm. Đối với các hợp đồng bảo hiểm tái tục liên tục hàng năm và không thay đổi quyền lợi bảo hiểm, thời gian chờ được tính từ Ngày bắt đầu hiệu lực bảo hiểm của hợp đồng bảo hiểm năm đầu tiên.
```
</details>

<details><summary>[3] C37_QT_C2 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm]
QUYỀN LỢI BẢO HIỂM ĐƯỢC CHI TRẢ THEO QUY TẮC BẢO HIỂM NÀY:
Sau thời gian chờ 90 ngày kể từ ngày bắt đầu hiệu lực bảo hiểm, nếu NĐBH bị chẩn đoán mắc một hoặc nhiều bệnh/tình trạng hiểm nghèo nào (theo danh mục dưới đây) và còn sống 30 ngày sau ngày được chẩn đoán, Bảo hiểm Bảo Việt sẽ thanh toán cho NĐBH 100% số tiền bảo hiểm.
Danh mục bệnh/tình trạng hiểm nghèo được bảo hiểm:
```
</details>

<details><summary>[4] C37_QT_C1_M2 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 2. Bên mua bảo hiểm]
Là tổ chức được thành lập và hoạt động hợp pháp tại Việt Nam, hoặc cá nhân tại Việt Nam từ đủ 18 tuổi trở lên có năng lực hành vi dân sự đầy đủ tại thời điểm giao kết hợp đồng bảo hiểm với Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải đáp ứng các điều kiện để mua bảo hiểm theo quy tắc, điều kiện, điều khoản bảo hiểm và đóng phí bảo hiểm cho Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải có quyền lợi có thể được bảo hiểm theo quy định của pháp luật.
Bên mua bảo hiểm có quyền lợi có thể được bảo hiểm đối với những người sau đây:
- Bản thân Bên mua bảo hiểm;
- Bố/mẹ của Bên mua bảo hiểm;
- Vợ/chồng, con của Bên mua bảo hiểm;
- Người có quan hệ nuôi dưỡng và cấp dưỡng hợp pháp với Bên mua bảo hiểm;
- Người khác, nếu người đó đồng ý cho Bên mua bảo hiểm mua bảo hiểm cho mình.
```
</details>

<details><summary>[5] C37_QT_C1_M19 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 19. Số tiền bảo hiểm]
Là tổng mức trách nhiệm bảo hiểm tối đa của Bảo hiểm Bảo Việt đối với Người được bảo hiểm trong suốt thời hạn bảo hiểm. Số tiền bảo hiểm được quy định trong hợp đồng bảo hiểm và/hoặc bảng quyền lợi bảo hiểm đính kèm quy tắc bảo hiểm/hợp đồng bảo hiểm.
```
</details>

---

## v1-0107 · scenario · hard · C37

**Câu hỏi:** Chị Lan tham gia Bảo hiểm 37 bệnh hiểm nghèo (CI37). Sau một cú sốc tâm lý nặng nề, chị bị mất hoàn toàn khả năng nói liên tục suốt 14 tháng và được chuyên gia Tai, Mũi, Họng (ENT) kết luận không thể phục hồi khả năng phát âm do ức chế thần kinh. Trường hợp này của chị Lan có được CI37 chi trả quyền lợi Mất khả năng phát âm không?

**Đáp án chuẩn:** Chị Lan không được chi trả quyền lợi Mất khả năng phát âm của CI37. Mặc dù tình trạng mất phát âm đã kéo dài liên tục trên 12 tháng và có xác nhận của chuyên gia Tai, Mũi, Họng (ENT), nhưng nguyên nhân xuất phát từ cú sốc tâm lý nên thuộc trường hợp loại trừ do tất cả các nguyên nhân liên quan đến tâm thần đều bị loại trừ.

**Evidence:** `C37_QT_C2_M12`

**Câu trả lời:**

> Có, trường hợp của chị Lan được chi trả quyền lợi Mất khả năng phát âm theo Bảo hiểm 37 bệnh hiểm nghèo (CI37) [1]. Theo quy định, mất hoàn toàn và không thể phục hồi khả năng phát âm do chấn thương hoặc bệnh tật, tình trạng này phải kéo dài liên tục trong thời gian 12 tháng và phải có chứng từ y tế có kết luận bệnh của chuyên gia Tai, Mũi, Họng (ENT). Trong trường hợp của chị Lan, chị bị mất khả năng phát âm liên tục trong 14 tháng và có chứng từ y tế từ chuyên gia ENT, do đó thỏa mãn điều kiện chi trả quyền lợi này.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] C37_QT_C2_M12 ★✓</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > 12. Mất khả năng phát âm]
Mất hoàn toàn và không thể phục hồi khả năng phát âm do chấn thương hoặc bệnh tật đối với dây thanh âm. Tình trạng này phải kéo dài liên tục trong thời gian 12 tháng, phải có chứng từ y tế có kết luận bệnh của chuyên gia Tai, Mũi, Họng (ENT). Tất cả các nguyên nhân liên quan đến tâm thần bị loại trừ.
```
</details>

<details><summary>[2] C37_QT_C2_M30 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > 30. Tê liệt (mất khả năng sử dụng tay chân)]
Mất hoàn toàn và không thể phục hồi khả năng sử dụng của ít nhất toàn bộ hai chi do chấn thương hoặc bệnh kéo dài trong ít nhất 6 tuần và không có khả năng phục hồi. Tình trạng này phải được chuyên gia thần kinh xác nhận. Thương tích do Người được bảo hiểm tự gây ra sẽ bị loại trừ.
```
</details>

<details><summary>[3] C37_BQL_S2_P2 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Bảng quyền lợi | PHẠM VI QUYỀN LỢI]
| DANH MỤC BỆNH/TÌNH TRẠNG HIỂM NGHÈO | DANH MỤC BỆNH/TÌNH TRẠNG HIỂM NGHÈO | Số tiền bảo hiểm (Việt Nam đồng) |
|---|---|---|
| 11. Phẫu thuật van tim | 30. Tê liệt (mất khả năng sử dụng tay chân) | Từ 200.000.000 đến 1.000.000.000 |
| 12. Mất khả năng phát âm | 31. Bệnh giai đoạn cuối | Từ 200.000.000 đến 1.000.000.000 |
| 13. Bỏng nặng | 32. Xơ cứng bì tiến triển | Từ 200.000.000 đến 1.000.000.000 |
| 14. Cấy ghép cơ quan nội tạng chính/ tủy xương | 33. Hội chứng Apallic | Từ 200.000.000 đến 1.000.000.000 |
| 15. Bệnh đa xơ cứng | 34. Lupus ban đỏ hệ thống có biến chứng viêm thận do lupus | Từ 200.000.000 đến 1.000.000.000 |
| 16. Loạn dưỡng cơ | 35. Bệnh động mạch vành nghiêm trọng khác | Từ 200.000.000 đến 1.000.000.000 |
| 17. Bệnh Parkinson | 36. Bại liệt | Từ 200.000.000 đến 1.000.000.000 |
| 18. Phẫu thuật động mạch chủ | 37. Mất khả năng sống độc lập | Từ 200.000.000 đến 1.000.000.000 |
| 19. Bệnh Alzheimer/Chứng mất trí nhớ nghiêm trọng |  | Từ 200.000.000 đến 1.000.000.000 |
(*) Ghi chú: Mỗi người được bảo hiểm được mua tối đa một Hợp đồng bảo hiểm 37 bệnh/tình trạng hiểm nghèo với Số tiền bảo hiểm không vượt quá 1.000.000.000 đồng
```
</details>

<details><summary>[4] C37_QT_C1_M22 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG I - ĐỊNH NGHĨA > 22. Thời gian chờ]
Là khoảng thời gian mà các sự kiện bảo hiểm xảy ra sẽ không được Bảo hiểm Bảo Việt chi trả đối với các quyền lợi bảo hiểm có liên quan, không chi trả cả những trường hợp thời điểm phát sinh rủi ro nằm trong thời gian chờ nhưng chi phí phát sinh hoặc hậu quả của đợt điều trị rủi ro này lại kéo dài quá thời gian chờ quy định. Thời gian chờ được tính kể từ Ngày bắt đầu hiệu lực bảo hiểm. Đối với các hợp đồng bảo hiểm tái tục liên tục hàng năm và không thay đổi quyền lợi bảo hiểm, thời gian chờ được tính từ Ngày bắt đầu hiệu lực bảo hiểm của hợp đồng bảo hiểm năm đầu tiên.
```
</details>

<details><summary>[5] C37_QT_C2 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm]
QUYỀN LỢI BẢO HIỂM ĐƯỢC CHI TRẢ THEO QUY TẮC BẢO HIỂM NÀY:
Sau thời gian chờ 90 ngày kể từ ngày bắt đầu hiệu lực bảo hiểm, nếu NĐBH bị chẩn đoán mắc một hoặc nhiều bệnh/tình trạng hiểm nghèo nào (theo danh mục dưới đây) và còn sống 30 ngày sau ngày được chẩn đoán, Bảo hiểm Bảo Việt sẽ thanh toán cho NĐBH 100% số tiền bảo hiểm.
Danh mục bệnh/tình trạng hiểm nghèo được bảo hiểm:
```
</details>

---

## v1-0110 · scenario · hard · BVP

**Câu hỏi:** Anh Nam (28 tuổi) tham gia bảo hiểm Bảo Việt An Gia từ ngày 01/03/2023 và tái tục liên tục sang năm thứ hai vào ngày 01/03/2024. Đến tháng 05/2024, anh phải phẫu thuật tái tạo dây chằng và điều trị tổn thương sụn chêm tại một bệnh viện trong phạm vi địa lý được bảo hiểm. Chi phí khám và điều trị này có được Bảo Việt An Gia chi trả không và nếu có thì áp dụng cơ chế bồi thường như thế nào?

**Đáp án chuẩn:** Chi phí của anh Nam được bảo hiểm do sự kiện diễn ra từ năm thứ hai tham gia liên tục. Theo quy tắc, quyền lợi này được bồi thường trên cơ sở đồng chi trả 70/30, trong đó Người được bảo hiểm phải tự chi trả 30% chi phí.

**Evidence:** `BVP_QT_C3_K32-38`

**Câu trả lời:**

> Chi phí khám và điều trị tái tạo dây chằng và điều trị tổn thương sụn chêm của anh Nam có được Bảo Việt An Gia chi trả. Theo quy định tại [35], điều trị dây chằng và sụn chêm được bảo hiểm từ năm thứ hai liên tục, với điều kiện bồi thường trên cơ sở đồng chi trả 70/30. Người được bảo hiểm (anh Nam) sẽ chịu 30% chi phí theo định nghĩa đồng chi trả.
> 
> Tài liệu sản phẩm hiện có không có thông tin để xác định mức chi trả cụ thể, nhưng theo quy định chung, chi phí sẽ được thanh toán theo tỷ lệ 70/30.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details><summary>[1] BVP_QT_C3_K32-38 ✓</summary>

```text
[Bảo Việt An Gia | Quy tắc | CHƯƠNG III - Các điểm loại trừ chung]
32. Kế hoạch hóa gia đình, phá thai/hậu quả của phá thai do nguyên nhân tâm lý hay xã hội; khám, điều trị hay xét nghiệm cho tình trạng vô sinh/hiếm muộn/kiểm tra khả năng sinh sản; điều trị bất lực; rối loạn chức năng sinh dục hay điều trị sinh lý; thụ tinh nhân tạo (bao gồm tất cả các hình thức), biến chứng thai sản trên Người được bảo hiểm có thai qua thụ tinh bằng phương pháp nhân tạo; điều trị các vấn đề về giới tính; và bất kỳ hậu quả hay biến chứng nào từ những điều trị trên.
33. Khám và điều trị kiểm soát trọng lượng cơ thể (tăng hoặc giảm cân); suy dinh dưỡng, còi xương, béo phì.
34. Bệnh rối loạn tâm thần và hành vi, bệnh tâm thần, loạn thần kinh, bệnh về tâm lý, rối loạn dạng cơ thể, bệnh chậm phát triển, bệnh rối loạn thiếu tập trung, bệnh tự kỉ, rối loạn giấc ngủ, mất ngủ, ngủ ngáy không rõ nguyên nhân, suy nhược thần kinh và suy nhược cơ thể không có nguyên nhân bệnh lý, hội chứng căng thẳng (stress) hoặc các bệnh có liên quan từ hội chứng đó.
35. Điều trị bằng thủy lực, các phương pháp thiên nhiên, spa, mát xa, viện điều dưỡng, an dưỡng, viện chăm sóc dài hạn hoặc tại các cơ sở tương tự.
36. Không bảo hiểm trong năm đầu tiên tham gia bảo hiểm đối với: Bệnh đặc biệt, bệnh có sẵn như định nghĩa; các chỉ định điều trị/phẫu thuật có từ trước ngày tham gia bảo hiểm.
37. Khám/điều trị liên quan đến rách/đứt/tái tạo dây chằng và sụn chêm không được bảo hiểm trong năm đầu tiên, và được bảo hiểm từ năm thứ hai liên tục với điều kiện bồi thường trên cơ sở đồng chi trả 70/30. Người được bảo hiểm chịu 30% chi phí theo định nghĩa đồng chi trả.
38. Rủi ro xảy ra hay điều trị y tế ngoài phạm vi địa lý được bảo hiểm.
```
</details>

<details><summary>[2] BVP_QT_C2_M2_B4_A </summary>

```text
[Bảo Việt An Gia | Quy tắc | QUYỀN LỢI BỔ SUNG 4: BẢO HIỂM NHA KHOA > A. Quyền lợi bảo hiểm]
- Bảo hiểm Bảo Việt sẽ thanh toán cho Người được bảo hiểm chi phí y tế điều trị răng bệnh lý bao gồm:
- Khám và chẩn đoán bệnh.
- Lấy cao răng.
- Trám răng bằng các chất liệu thông thường.
- Nhổ răng bệnh lý.
- Lấy u vôi răng (lấy vôi răng sâu dưới nướu).
- Phẫu thuật cắt chóp răng.
- Chữa tủy răng.
- Điều trị viêm nướu, viêm nha chu.
Điều trị răng giới hạn tại các cơ sở y tế theo quy định sau:
- Chuyên khoa Nha tại tất cả các bệnh viện hoạt động hợp pháp trong phạm vi lãnh thổ Việt Nam.
- Tại Thành phố Hà Nội và Thành phố Hồ Chí Minh: ngoài Chuyên khoa Nha tại tất cả các bệnh viện nói trên, Bảo hiểm Bảo Việt chỉ chấp thuận bồi thường cho các chi phí phát sinh tại các Phòng khám/Nha khoa trong hệ thống bảo lãnh viện phí của Bảo hiểm Bảo Việt.
- Đối với các Tỉnh thành khác: ngoài Chuyên khoa Nha tại tất cả các bệnh viện nói trên, Bảo hiểm Bảo Việt chấp thuận bồi thường cho các chi phí phát sinh tại các Phòng khám/Nha khoa có giấy phép đăng ký kinh doanh và giấy phép hành nghề hợp pháp và cấp được hóa đơn hợp lệ theo quy định của Bộ Tài Chính.
- Bảo hiểm Bảo Việt không chi trả cho các chi phí khám và điều trị của Người được bảo hiểm tại cơ sở y tế thuộc Danh sách cơ sở y tế không chi trả bảo hiểm được cập nhật tại trang thông tin điện tử chính thức của Bảo hiểm Bảo Việt.
```
</details>

<details><summary>[3] BVP_QT_C4_M2_K1 </summary>

```text
[Bảo Việt An Gia | Quy tắc | CHƯƠNG IV: THỦ TỤC YÊU CẦU BỒI THƯỜNG VÀ BẢO LÃNH VIỆN PHÍ > II. THỦ TỤC TRẢ TIỀN BẢO HIỂM VÀ BẢO LÃNH VIỆN PHÍ]
1. Trường hợp ứng tiền trước, nộp hồ sơ yêu cầu bồi thường sau:
Trường hợp Người được bảo hiểm không sử dụng hoặc không được sử dụng dịch vụ bảo lãnh viện phí trực tiếp, hoặc khám và điều trị tại các bệnh viện/phòng khám hợp pháp nhưng không thuộc hệ thống bảo lãnh viện phí của chương trình, Người được bảo hiểm phải thanh toán mọi chi phí khám/điều trị trước, sau đó gửi toàn bộ hồ sơ cho Bảo hiểm Bảo Việt để thanh toán phần chi phí thuộc phạm vi bảo hiểm.
a. Thời hạn bồi thường:
Khi xảy ra sự kiện bảo hiểm, Bảo hiểm Bảo Việt có trách nhiệm giải quyết và chi trả tiền bảo hiểm theo thời hạn đã thoả thuận trong Hợp đồng bảo hiểm; trong trường hợp không có thoả thuận trong hợp đồng thì Bảo hiểm Bảo Việt thông báo kết quả và giải quyết bồi thường cho người được bảo hiểm, người thừa kế, hoặc người đại diện hợp pháp trong thời hạn tối đa 15 ngày làm việc, kể từ ngày nhận được bộ hồ sơ đầy đủ hợp lệ.
b. Thông tin chung về chi trả bảo hiểm:
Tất cả các chứng từ và tài liệu (bao gồm các hóa đơn gốc, giấy chứng nhận, các chiếu chụp X-quang...) mà Bảo hiểm Bảo Việt yêu cầu hỗ trợ cho việc chi trả bảo hiểm (bồi thường), bao gồm cả các kết quả về sức khỏe và bất kỳ các chi tiết nào về các tiền sử sức khỏe của Người được bảo hiểm sẽ phải được cung cấp miễn phí cho Bảo hiểm Bảo Việt, nếu
- Tiền bảo hiểm sẽ được chi trả cho Người được bảo hiểm hoặc Người thừa kế/Người thụ hưởng/Người được ủy quyền hợp pháp của Người được bảo hiểm theo đúng quy định của Pháp luật. Trong trường hợp Người được bảo hiểm không chỉ định Người thụ hưởng, hoặc Người thụ hưởng đã qua đời hoặc mất tích trong một thời gian nhất định, Bảo hiểm Bảo Việt trả tiền bồi thường cho Người thừa kế hợp pháp theo pháp luật về thừa kế.
```
</details>

<details><summary>[4] BVP_QT_C1_M1_K29 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. ĐỊNH NGHĨA > 29. Hệ thống bảo lãnh viện phí]
Là hệ thống các cơ sở y tế có ký kết thỏa thuận cung cấp dịch vụ bảo lãnh viện phí với Bảo hiểm Bảo Việt. Người được bảo hiểm khi khám và điều trị tại những cơ sở y tế này sẽ được Bảo hiểm Bảo Việt bảo lãnh thanh toán tùy theo chương trình bảo hiểm tham gia đối với các chi phí phát sinh thuộc phạm vi bảo hiểm và theo hạn mức quy định trong hợp đồng bảo hiểm. Người được bảo hiểm phải tự chi trả cho những chi phí không thuộc phạm vi bảo hiểm và/hoặc những chi phí vượt quá mức trách nhiệm đã tham gia trong hợp đồng bảo hiểm tại thời điểm điều trị.
Danh sách các cơ sở y tế trong hệ thống bảo lãnh viện phí có thể thay đổi và được cập nhật thường xuyên trên trang thông tin điện tử chính thức của Bảo hiểm Bảo Việt.
```
</details>

<details><summary>[5] BVP_QT_C2_M1_A_K5-8 </summary>

```text
[Bảo Việt An Gia | Quy tắc | I. QUYỀN LỢI BẢO HIỂM CHÍNH: ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, BIẾN CHỨNG THAI SẢN > A. Quyền lợi bảo hiểm]
5. Chi phí phẫu thuật
Bảo hiểm Bảo Việt sẽ chi trả cho Người được bảo hiểm các chi phí y tế thực tế thuộc phạm vi bảo hiểm phát sinh cho một ca phẫu thuật nội trú như định nghĩa, bao gồm chi phí thuốc, vật tư tiêu hao, các thiết bị cần thiết và hợp lý theo chỉ định của bác sĩ mà không bị loại trừ bảo hiểm, chi phí phòng mổ, phẫu thuật viên, các chi phí gây mê, các chi phí hội chẩn trước khi mổ và hồi sức sau khi mổ, chi phí tái mổ, chi phí cấy ghép nội tạng trừ những điểm loại trừ quy định tại hợp đồng bảo hiểm/quy tắc bảo hiểm. Giới hạn số tiền chi trả cho trường hợp phẫu thuật không vượt mức giới hạn tối
đa do Người được bảo hiểm lựa chọn khi tham gia bảo hiểm và được ghi cụ thể trong hợp đồng bảo hiểm.
Trường hợp phẫu thuật trong ngày và phẫu thuật ngoại trú không được chi trả trong quyền lợi này.
6. Phục hồi chức năng
7. Trợ cấp bệnh viện công (không quá 60 ngày/năm)
Bảo hiểm Bảo Việt chi trả số tiền trợ cấp ghi trên bảng quyền lợi bảo hiểm cho mỗi ngày nằm viện điều trị nội trú do bệnh, tai nạn tại các bệnh viện công lập.
8. Trợ cấp mai táng phí trong trường hợp tử vong tại bệnh viện.
Trường hợp Người được bảo hiểm tử vong khi nằm viện thuộc phạm vi trách nhiệm bảo hiểm, Bảo hiểm Bảo Việt sẽ trả tiền trợ cấp mai táng phí ghi trên hợp đồng bảo hiểm.
```
</details>

---

## v1-0113 · scenario · medium · ITC

**Câu hỏi:** Bà Mai tham gia bảo hiểm Bảo Việt Intercare và phải nhập viện điều trị nội trú. Trong một ngày nằm viện, do bệnh tình diễn biến phức tạp, bà được 2 bác sĩ chuyên khoa khác nhau đến khám hội chẩn. Chi phí khám chuyên khoa của bà Mai trong ngày hôm đó sẽ được bảo hiểm chi trả như thế nào?

**Đáp án chuẩn:** Bảo hiểm Bảo Việt Intercare chỉ chi trả chi phí khám chuyên khoa trong thời gian điều trị nội trú theo giới hạn tối đa một lần khám một ngày (và không quá 90 ngày/năm theo mức giới hạn phụ). Do đó, bà Mai chỉ được thanh toán chi phí cho 1 lần khám chuyên khoa trong ngày hôm đó.

**Evidence:** `ITC_QT_C2_A_M10`

**Câu trả lời:**

> Chi phí khám chuyên khoa của bà Mai trong ngày hôm đó sẽ được bảo hiểm chi trả một lần, vì theo quy định [5], trường hợp nhiều bác sĩ chuyên khoa cùng hội chẩn trước một người bệnh theo quy chế bệnh viện thì tất cả chỉ được tính là một lần khám/điều trị.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details><summary>[1] ITC_QT_C2_A_M10 ✓</summary>

```text
[Bảo Việt Intercare | Quy tắc | A. Quyền lợi bảo hiểm chính: Điều trị nội trú do bệnh, tai nạn > 10. Chi phí hội chẩn chuyên khoa]
Bảo hiểm Bảo Việt sẽ trả chi phí khám chuyên khoa trong thời gian điều trị nội trú theo giới hạn một lần khám một ngày, 90 ngày/năm theo mức giới hạn phụ được ghi trong bảng quyền lợi bảo hiểm.
```
</details>

<details><summary>[2] ITC_QT_C2_A_M6 </summary>

```text
[Bảo Việt Intercare | Quy tắc | A. Quyền lợi bảo hiểm chính: Điều trị nội trú do bệnh, tai nạn > 6. Chi phí tái khám sau khi xuất viện]
Bảo hiểm Bảo Việt sẽ chi trả các chi phí y tế phát sinh theo chỉ định của bác sĩ ngay khi Người được bảo hiểm xuất viện và có liên quan trực tiếp đến đợt điều trị nội trú trước đó. Các chi phí này bao gồm chi phí khám, xét nghiệm, chẩn đoán hình ảnh và thuốc phát sinh trong vòng 90 ngày kể từ ngày Người được bảo hiểm xuất viện trừ trường hợp có thỏa thuận khác trong hợp đồng bảo hiểm.
```
</details>

<details><summary>[3] ITC_QT_C2_A_M5 </summary>

```text
[Bảo Việt Intercare | Quy tắc | A. Quyền lợi bảo hiểm chính: Điều trị nội trú do bệnh, tai nạn > 5. Chi phí khám trước khi nhập viện]
Bảo hiểm Bảo Việt sẽ chi trả các chi phí khám, kiểm tra, siêu âm, chụp chiếu, xét nghiệm cơ bản và tiền thuốc theo chỉ định của bác sĩ, liên quan trực tiếp đến bệnh/thương tật cần phải nhập viện, và là cơ sở trực tiếp để bác sĩ đưa ra chỉ định nhập viện để điều trị. Chi phí khám trước khi nhập viện chỉ được chấp nhận một lần gần nhất được thực hiện trong vòng 30 ngày trước khi nhập viện trừ trường hợp có thỏa thuận khác trong hợp đồng bảo hiểm.
```
</details>

<details><summary>[4] ITC_QT_C2_A_M1 </summary>

```text
[Bảo Việt Intercare | Quy tắc | A. Quyền lợi bảo hiểm chính: Điều trị nội trú do bệnh, tai nạn > 1. Tiền phòng, giường]
Bảo hiểm Bảo Việt sẽ chi trả cho các chi phí tiền phòng, giường trong quá trình điều trị nội trú và điều trị trong ngày, bao gồm tiền ăn theo tiêu chuẩn điều trị (tức là do bệnh viện cung cấp theo tiêu chuẩn phòng nằm của bệnh viện). Bảo hiểm Bảo Việt không chi trả cho các chi phí khác phát sinh như: điện thoại, báo, tiếp khách, mỹ phẩm.
Bảo hiểm Bảo Việt không chi trả quyền lợi bảo hiểm này nếu như về mặt y khoa các điều trị này có thể được điều trị ngoại trú.
```
</details>

<details open><summary>[5] ITC_QT_C1_M36 ★</summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN I - ĐỊNH NGHĨA > 36. Lần khám/Điều trị]
Là một lần người bệnh được bác sĩ thăm khám lâm sàng, thực hiện các xét nghiệm, chẩn đoán hình ảnh hay các thủ thuật thăm dò khác và/hoặc sử dụng thuốc điều trị theo chỉ định của bác sĩ tại cùng một cơ sở y tế hợp pháp nhằm mục đích chẩn đoán và điều trị rủi ro thuộc phạm vi bảo hiểm.
- Trường hợp nhiều bác sĩ chuyên khoa cùng hội chẩn trước một người bệnh theo quy chế bệnh viện thì tất cả chỉ được tính là một lần khám/điều trị.
- Trường hợp người bệnh khám một chuyên khoa nhiều lần trong ngày thì tất cả chỉ tính là một lần khám/điều trị.
- Trường hợp người bệnh phải khám nhiều chuyên khoa khác dù có chỉ định của bác sĩ trong cùng một cơ sở y tế, trong một ngày thì tất cả vẫn chỉ tính là một lần khám/điều trị.
- Trường hợp người bệnh khám/xét nghiệm ngày đầu tiên nhưng chưa có kết luận bệnh của bác sĩ được bác sĩ chỉ định khám/xét nghiệm thêm một số mục ở ngày sau đó để có cơ sở đưa ra kết luận bệnh, thì chi phí phát sinh trong tất cả các ngày này được tính là một lần khám/điều trị.
- Trường hợp người bệnh khám và điều trị tại một bệnh viện/phòng khám, nhưng được chỉ định làm xét nghiệm/chẩn đoán hình ảnh ở bệnh viện/phòng khám khác thì tất cả chỉ tính là một lần khám/điều trị.
```
</details>

---

## v1-0118 · scenario · hard · C37

**Câu hỏi:** Ông A tham gia sản phẩm Bảo hiểm 37 bệnh hiểm nghèo (CI37). Ông không may gặp tai nạn giao thông dẫn đến chấn thương đầu và xuất hiện các triệu chứng run, khó đi lại. Chuyên gia thần kinh dựa trên kết quả chụp cộng hưởng từ (MRI) đã xác nhận ông bị tổn thương thần kinh vĩnh viễn dự kiến kéo dài suốt đời. Sau 5 tuần kể từ ngày xảy ra tai nạn, ông A nộp hồ sơ yêu cầu chi trả quyền lợi bệnh Chấn thương đầu nghiêm trọng thì có được chấp thuận không? Vì sao?

**Đáp án chuẩn:** Yêu cầu của ông A chưa được chấp thuận chi trả. Theo quy tắc sản phẩm CI37, quyền lợi Chấn thương đầu nghiêm trọng yêu cầu tình trạng tổn thương thần kinh vĩnh viễn phải có các triệu chứng lâm sàng kéo dài ít nhất 6 tuần kể từ ngày xảy ra tai nạn, trong khi trường hợp của ông A mới chỉ theo dõi được 5 tuần.

**Evidence:** `C37_QT_C2_M29`

**Câu trả lời:**

> [1]
> 
> Theo quy định trong tài liệu, chấn thương đầu nghiêm trọng do tai nạn dẫn đến tình trạng tổn thương thần kinh vĩnh viễn với các triệu chứng lâm sàng kéo dài ít nhất 6 tuần kể từ ngày xảy ra tai nạn. Chẩn đoán này phải do chuyên gia thần kinh xác nhận, đi kèm với các kết quả rõ ràng của hình ảnh Chụp cộng hưởng từ, Chụp cắt lớp hoặc các kỹ thuật hình ảnh đáng tin cậy khác.
> 
> Trong trường hợp của ông A, mặc dù đã xuất hiện các triệu chứng run, khó đi lại và chấn thương thần kinh vĩnh viễn đã được chuyên gia thần kinh xác nhận dựa trên kết quả chụp cộng hưởng từ, nhưng thời gian từ khi xảy ra tai nạn đến khi nộp hồ sơ yêu cầu chi trả quyền lợi là 5 tuần, chưa đủ 6 tuần theo quy định.
> 
> Vì vậy, ông A không được chấp thuận chi trả quyền lợi bệnh Chấn thương đầu nghiêm trọng theo sản phẩm Bảo hiểm 37 bệnh hiểm nghèo (CI37).

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] C37_QT_C2_M29 ★✓</summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > 29. Chấn thương đầu nghiêm trọng]
Chấn thương đầu do tai nạn dẫn đến tình trạng tổn thương thần kinh vĩnh viễn với các triệu chứng lâm sàng kéo dài ít nhất 6 tuần kể từ ngày xảy ra tai nạn. Chẩn đoán này phải do chuyên gia thần kinh xác nhận, đi kèm với các kết quả rõ ràng của hình ảnh Chụp cộng hưởng từ, Chụp cắt lớp hoặc các kỹ thuật hình ảnh đáng tin cậy khác. “Tai nạn” có nghĩa là một sự kiện bất ngờ, không lường trước được gây ra bởi một lực mạnh từ bên ngoài và có thể nhìn thấy được độc lập với các nguyên nhân khác và là nguyên nhân duy nhất dẫn đến chấn thương đầu. Vĩnh viễn có nghĩa là có khả năng kéo dài suốt cuộc đời của người được bảo hiểm. Tổn thương thần kinh vĩnh viễn với các triệu chứng lâm sàng kéo dài có nghĩa là các triệu chứng rối loạn chức năng trong hệ thống thần kinh thể hiện qua kết quả chẩn đoán lâm sàng và dự kiến sẽ kéo dài suốt đời của Người được bảo hiểm. Các triệu chứng bao gồm tê, tê liệt, suy nhược cục bộ, rối loạn phát âm (khó phát âm), hội chứng bất lực ngôn ngữ (không có khả năng phát âm), chứng khó nuốt, suy giảm thị lực, khó đi lại, suy giảm khả năng phối hợp, run, co giật, mất trí nhớ, mê sảng và hôn mê. Các chẩn đoán sau đây bị loại trừ:
• Chấn thương tủy sống;
• Chấn thương đầu do các nguyên nhân khác.
```
</details>

<details><summary>[2] C37_QT_C2_M3 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > 3. Đột quỵ nghiêm trọng]
Sự cố mạch máu não bao gồm nhồi máu mô não, xuất huyết não và dưới nhện, thuyên tắc nội sọ và huyết khối não dẫn đến tình trạng tổn thương thần kinh vĩnh viễn (*) với các triệu chứng lâm sàng kéo dài. Chẩn đoán này phải được xác định bởi tất cả các điều kiện sau:
• Bằng chứng lâm sàng về tình trạng tổn thương thần kinh vĩnh viễn được xác nhận bởi một bác sỹ chuyên khoa thần kinh sau ít nhất 6 tuần kể từ khi xảy ra sự kiện; và
• Các kết quả hình ảnh cộng hưởng từ, chụp cắt lớp vi tính, hoặc các kỹ thuật hình ảnh đáng tin cậy khác phù hợp với chẩn đoán về một cơn đột quỵ mới. Tổn thương thần kinh vĩnh viễn với các triệu chứng lâm sàng kéo dài có nghĩa là các triệu chứng rối loạn chức năng trong hệ thống thần kinh thể hiện qua kết quả chẩn đoán lâm sàng và dự kiến sẽ kéo dài suốt đời của NĐBH. Các triệu chứng bao gồm tê, tê liệt, yếu cục bộ, rối loạn phát âm (khó phát âm), hội chứng bất lực ngôn ngữ (không có khả năng nói), chứng khó nuốt, suy giảm thị lực, khó đi lại, suy giảm khả năng phối hợp, run, co giật, mất trí nhớ, mê sảng và hôn mê. Các trường hợp sau đây bị loại trừ:
• Thiếu máu cục bộ thoáng qua;
• Tổn thương não do tai nạn hoặc thương tích, nhiễm trùng, viêm mạch và viêm nhiễm;
• Bệnh mạch máu ảnh hưởng đến mắt hoặc thần kinh thị giác;
• Rối loạn thiếu máu cục bộ của hệ thống tiền đình;
• Xuất huyết thứ phát trong não đã bị tổn thương có sẵn. Vĩnh viễn có nghĩa là có khả năng kéo dài suốt cuộc đời của NĐBH.
```
</details>

<details><summary>[3] C37_QT_C2_GC1 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > Ghi chú:]
(*) Tình trạng tổn thương thần kinh vĩnh viễn: Tổn thương thần kinh vĩnh viễn có nghĩa là các triệu chứng rối loạn chức năng trong hệ thống thần kinh xuất hiện khi khám lâm sàng và dự kiến sẽ kéo dài trong suốt cuộc đời của Người được bảo hiểm.
i. Di động - khả năng di chuyển trong nhà từ phòng này sang phòng khác trên bề mặt bằng phẳng;
ii. Vệ sinh - khả năng sử dụng nhà vệ sinh hoặc kiểm soát các chức năng ruột và bàng quang để duy trì việc vệ sinh cá nhân hợp lý ở mức độ thỏa đáng;
iii. Ăn - khả năng tự ăn khi thức ăn đã được chuẩn bị và sẵn có.
Tình trạng này phải được bác sĩ do CTBH chỉ định xác nhận. Theo quy tắc bảo hiểm này, "được hỗ trợ" có nghĩa là dùng các thiết bị hoặc dụng cụ đặc biệt để hỗ trợ các hoạt động mà không phải sự trợ giúp của con người.
Loại trừ các bệnh lý không phải do thực thể như bệnh loạn thần kinh và các bệnh tâm thần.
```
</details>

<details><summary>[4] C37_QT_C2_M25 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > 25. Viêm não do vi-rút]
Viêm nghiêm trọng của não (bán cầu não, thân não hoặc tiểu não) do nhiễm vi rút (virus) và dẫn đến tổn thương thần kinh vĩnh viễn. Chẩn đoán này phải được chuyên gia thần kinh kết luận và tình trạng tổn thương thần kinh vĩnh viễn phải được kéo dài trong ít nhất 6 tuần. Viêm não do nhiễm HIV bị loại trừ.
```
</details>

<details><summary>[5] C37_QT_C2_M30 </summary>

```text
[Bảo hiểm 37 bệnh hiểm nghèo (CI37) | Quy tắc | CHƯƠNG II - Quyền lợi bảo hiểm > 30. Tê liệt (mất khả năng sử dụng tay chân)]
Mất hoàn toàn và không thể phục hồi khả năng sử dụng của ít nhất toàn bộ hai chi do chấn thương hoặc bệnh kéo dài trong ít nhất 6 tuần và không có khả năng phục hồi. Tình trạng này phải được chuyên gia thần kinh xác nhận. Thương tích do Người được bảo hiểm tự gây ra sẽ bị loại trừ.
```
</details>

---

## v1-0054 · compare · medium · FLX ITC · phụ: B4ng (B4 bị ngưỡng chặn)

**Câu hỏi:** Độ tuổi tối đa để tham gia Bảo hiểm Du lịch Flexi và Bảo Việt Intercare khác nhau như thế nào?

**Đáp án chuẩn:** Bảo hiểm Du lịch Flexi chấp nhận đối tượng bảo hiểm đến hết 85 tuổi, trong khi Bảo Việt Intercare giới hạn tối đa đến 69 tuổi đối với người mới tham gia lần đầu hoặc đến 75 tuổi nếu tham gia tái tục. Như vậy, mức tuổi tối đa được tham gia của Bảo hiểm Du lịch Flexi cao hơn so với Bảo Việt Intercare.

**Evidence:** `FLX_QT_C1_M1_K15 ITC_QT_C4_M1_P1`

**Câu trả lời:**

> Độ tuổi tối đa để tham gia Bảo hiểm Du lịch Flexi là 85 tuổi [5], trong khi Bảo Việt Intercare chỉ áp dụng cho người có độ tuổi từ 15 ngày tuổi đến 69 tuổi nếu mới tham gia lần đầu hoặc đến 75 tuổi nếu tham gia tái tục [2]. Do đó, độ tuổi tối đa để tham gia Bảo hiểm Du lịch Flexi lớn hơn Bảo Việt Intercare 10 tuổi [2][5].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details><summary>[1] FLX_BP_S2_P1 </summary>

```text
[Bảo hiểm Du lịch Flexi | Biểu phí | Biểu phí bảo hiểm dành cho gia đình]
Chương trình bảo hiểm du lịch quốc tế Flexi Bảo Việt cũng được thiết kế với gói bảo hiểm dành riêng cho gia đình, giúp các thành viên cùng tham gia trong một hợp đồng bảo hiểm với mức phí hợp lý và phạm vi bảo vệ đồng bộ. Gói bảo hiểm gia đình được áp dụng cho tối đa 05 thành viên, bao gồm vợ, chồng và các con ruột hoặc con nuôi hợp pháp dưới 16
tuổi, với điều kiện tất cả các thành viên cùng tham gia một hành trình và đăng ký cùng chương trình bảo hiểm.
Việc lựa chọn bảo hiểm du lịch quốc tế Flexi Bảo Việt cho gia đình không chỉ giúp đơn giản hóa thủ tục tham gia mà còn đảm bảo mỗi thành viên đều được bảo vệ trước những rủi ro có thể phát sinh trong suốt chuyến đi quốc tế. Đây là giải pháp phù hợp cho các gia đình có kế hoạch du lịch, thăm thân hoặc công tác nước ngoài cùng nhau, mang lại sự an tâm và chủ động hơn trong việc bảo vệ tài chính cho cả gia đình.
```
</details>

<details open><summary>[2] ITC_QT_C4_M1_P1 ★✓</summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN IV. QUY ĐỊNH CHUNG > 1. Đối tượng và điều kiện tham gia bảo hiểm]
- Từ 15 ngày tuổi đến 69 tuổi nếu mới tham gia lần đầu hoặc đến 75 tuổi nếu tham gia tái tục.
- Không bị các bệnh tâm thần
- Không bị các bệnh ung thư (chỉ áp dụng cho Người được bảo hiểm tham gia năm đầu tiên)
- Không bị thương tật vĩnh viễn từ 80% trở lên
- Không đang trong thời gian điều trị nội trú bệnh đặc biệt (chỉ áp dụng cho Người được bảo hiểm tham gia năm đầu tiên)
- Là người Việt Nam hoặc người nước ngoài cư trú hợp pháp trong lãnh thổ Việt Nam và không rời khỏi Việt Nam liên tiếp hơn 180 ngày (quy định này không áp dụng với du học sinh ở nước ngoài).
Trường hợp Người tham gia không đúng theo đối tượng và điều kiện tham gia như đề cập, Bảo hiểm Bảo Việt có quyền chấm dứt bảo hiểm và không chịu trách nhiệm với quyền lợi bảo hiểm đã đăng ký.
Người phụ thuộc chỉ được bảo hiểm theo chương trình thấp hơn hoặc bằng mức quyền lợi với Người được bảo hiểm chính (bao gồm cả quyền lợi bảo hiểm chính và các quyền lợi bảo hiểm bổ sung) và phải được Bảo hiểm Bảo Việt chấp thuận.
Trẻ em mới sinh đủ điều kiện tham gia bảo hiểm sau 15 ngày tuổi kể từ ngày sinh hay kể từ ngày xuất viện, ngày nào xảy ra sau sẽ được chọn. Người được bảo hiểm phải nộp yêu cầu bảo hiểm cho đứa trẻ đó cùng với giấy chứng nhận đứa trẻ ở trong tình trạng sức khỏe tốt và phải được Bảo hiểm Bảo Việt chấp thuận. Trẻ em dưới 18 tuổi yêu cầu tham gia cùng bố/mẹ.
Áp dụng bổ sung với hợp đồng bảo hiểm tổ chức:
Đối tượng tham gia bảo hiểm trong hợp đồng bảo hiểm tổ chức bao gồm
a. Nhân viên của Bên mua bảo hiểm.
b. Người thân của Nhân viên.
- Nhân viên chỉ được đăng ký bảo hiểm cho người thân của mình một lần vào đầu hiệu lực hợp đồng.
- Đăng ký sau ngày bắt đầu hiệu lực của hợp đồng bảo hiểm chỉ áp dụng đối với các trường hợp sau:
- Người thân của nhân viên mới vào làm việc;
- Vợ hoặc chồng của nhân viên mới kết hôn;
- Con mới sinh đủ tuổi và đủ điều kiện tham gia;
```
</details>

<details><summary>[3] FLX_QT_C1_M1_K35 </summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | I. ĐỊNH NGHĨA > 35. Trẻ em]
Là người có độ tuổi từ 6 (sáu) tháng tuổi đến 16 (mười sáu) tuổi tại ngày bắt đầu hiệu lực của Hợp đồng bảo hiểm/Giấy chứng nhận bảo hiểm, là con hợp pháp của Người được bảo hiểm và/hoặc người được giám hộ bởi Người được bảo hiểm và tham gia chuyến đi cùng với Người được bảo hiểm.
Trẻ em có độ tuổi từ 11 trở xuống phải được một người được bảo hiểm là người lớn đi kèm và được bảo hiểm cùng với người đó.
Trẻ em có độ tuổi từ 12 đến 16 đi du lịch một mình cũng sẽ được chấp nhận bảo hiểm theo Hợp đồng bảo hiểm/Giấy chứng nhận bảo hiểm với điều kiện đóng phí bảo hiểm theo phí chuẩn của người lớn. Với những trường hợp này, các quyền lợi được chi trả theo hạn mức giới hạn của đối tượng Trẻ em.
```
</details>

<details><summary>[4] ITC_QT_C1_M4 </summary>

```text
[Bảo Việt Intercare | Quy tắc | PHẦN I - ĐỊNH NGHĨA > 4. Bên mua bảo hiểm/Người yêu cầu bảo hiểm]
Là tổ chức được thành lập và hoạt động hợp pháp tại Việt Nam, hoặc cá nhân tại Việt Nam từ đủ 18 tuổi trở lên có năng lực hành vi dân sự đầy đủ tại thời điểm giao kết hợp đồng bảo hiểm với Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải đáp ứng các điều kiện để mua bảo hiểm theo quy tắc, điều kiện, điều khoản bảo hiểm và đóng phí bảo hiểm cho Bảo hiểm Bảo Việt. Bên mua bảo hiểm phải có quyền lợi có thể được bảo hiểm theo quy định của pháp luật.
Bên mua bảo hiểm có quyền lợi có thể được bảo hiểm đối với những người sau đây:
- Bản thân Bên mua bảo hiểm;
- Bố/mẹ đẻ, bố/mẹ của vợ/chồng của Bên mua bảo hiểm;
- Vợ/chồng, con của Bên mua bảo hiểm;
- Người có quan hệ nuôi dưỡng và cấp dưỡng hợp pháp với Bên mua bảo hiểm;
- Nhân viên có Hợp đồng lao động/Hợp đồng thử việc/Các thỏa thuận lao động với Bên mua bảo hiểm theo quy định của pháp luật, làm việc cho Bên mua bảo hiểm và có tên trong danh sách Người được bảo hiểm trong suốt thời hạn bảo hiểm, và người thân của nhân viên.
- Người khác, nếu người đó đồng ý cho Bên mua bảo hiểm mua bảo hiểm cho mình
```
</details>

<details open><summary>[5] FLX_QT_C1_M1_K15 ★✓</summary>

```text
[Bảo hiểm Du lịch Flexi | Quy tắc | I. ĐỊNH NGHĨA > 15. Đối tượng tham gia bảo hiểm]
Là người Việt Nam hoặc người nước ngoài đang ở Việt Nam bao gồm (người cư trú hợp pháp tại Việt Nam và/hoặc những người đang du lịch/công tác tại Việt Nam) và có độ tuổi từ 06 (sáu) tháng tuổi đến hết 85 (tám mươi lăm) tuổi tại ngày bắt đầu hiệu lực của hợp đồng bảo hiểm/giấy chứng nhận bảo hiểm.
```
</details>

---

## v1-0119 · compare · hard · BTB FLX · phụ: B4ng (B4 bị ngưỡng chặn)

**Câu hỏi:** Dựa vào bảng quyền lợi được cung cấp, hãy so sánh cơ cấu chương trình của Bảo Việt Tâm Bình và Bảo hiểm Du lịch Flexi về tổng số lượng chương trình bảo hiểm cũng như tên gọi của chương trình ở mức thấp nhất và cao nhất của mỗi bên.

**Đáp án chuẩn:** Bảo Việt Tâm Bình gồm các chương trình Cơ bản, Mở rộng, Nâng cao, Toàn diện, Ưu việt (thấp nhất là Cơ bản, cao nhất là Ưu việt). Bảo hiểm Du lịch Flexi gồm Chương trình Bạc, Vàng, Bạch Kim, Kim Cương (thấp nhất là Bạc, cao nhất là Kim Cương). Tâm Bình nhiều hơn Flexi một chương trình và đặt tên theo mức phạm vi bảo hiểm, còn Flexi đặt tên theo kim loại/đá quý.

**Evidence:** `BTB_BQL_S2_TB9 FLX_BQL_S2_P1`

**Câu trả lời:**

> Bảo Việt Tâm Bình có 5 chương trình bảo hiểm từ cơ bản đến toàn diện: Cơ bản, Mở rộng, Nâng cao, Toàn diện, Ưu việt.
> 
> Bảo hiểm Du lịch Flexi có 4 chương trình bảo hiểm từ thấp đến cao: Chương trình Bạc (Silver Plan), Chương trình Vàng (Gold Plan), Chương trình Bạch Kim (Platinum Plan), Chương trình Kim Cương (Diamond Plan).

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details><summary>[1] BTB_QT_C1_M2 </summary>

```text
[Bảo Việt Tâm Bình | Quy tắc | CHƯƠNG I: ĐỊNH NGHĨA > 2. Bảng quyền lợi bảo hiểm]
Bảng quyền lợi bảo hiểm cung cấp các thông tin tóm tắt về quyền lợi bảo hiểm. Bảng quyền lợi bảo hiểm được cấp cùng và là bộ phận không tách rời của hợp đồng bảo hiểm.
```
</details>

<details><summary>[2] FLX_BQL_S3 </summary>

```text
[Bảo hiểm Du lịch Flexi | Bảng quyền lợi | VD) c CC)]
ASEAN: Brunei, Cam-pu-chia, Indonesia, Lào, Malaysia, Myanmar, Philippines, Singapore và Thái Lan
Châu Á - Thái Bình Dương: bao gồm các nước ở Vùng 1 và các nước sau đây: Australia (Úc), Trung Quốc, đảo Guam, HongKong, Nhật Bản, Hàn Quốc, Macao, New Zealand, Đài Loan và Ấn Độ.
Toàn thế giới (trừ Việt Nam và các quốc gia/khu vực bị cấm vận)
(*) Đối với trẻ em, các quyền lợi được giới hạn ở mức 20% số tiền bảo hiểm. Đối với người từ 70 tuổi trở lên, các quyển lợi được giới hạn ở mức 30% số tiền bảo hiểm..
(**) Quyền lợi bảo hiểm thẻ tín dụng không áp dụng đối với trẻ em.
(***) Quyền lợi không áp dụng đối với trẻ em.
(****) Đối với trẻ em, quyển lợi được giới hạn ở 50% số tiền bảo hiểm
```
</details>

<details><summary>[3] BTB_BQL_S3 </summary>

```text
[Bảo Việt Tâm Bình | Bảng quyền lợi | Lưu ý áp dụng chung với tất cả các quyền lợi bảo hiểm:]
- Đối với phương pháp điều trị Đông y, các mức giới hạn quyền lợi bảo hiểm sẽ được thanh toán tối đa không vượt quá 50% số tiền bảo hiểm của quyền lợi tương ứng.
- Đối với điều trị/trợ cấp/tử vong/thương tật toàn bộ vĩnh viễn do bệnh ung thư và biến chứng/hậu quả liên quan đến bệnh ung thư (Sau thời gian chờ 2 năm, từ năm thứ 3 tham gia liên tục): Chi trả tối đa 50% số tiền bảo hiểm tương ứng với từng quyền lợi.
- Quy định đồng chi trả đối với trẻ em từ 15 ngày tuổi đến 3 tuổi:
- Tỷ lệ áp đồng chi trả: 70/30 (Bảo hiểm Bảo Việt chi trả 70%, Người được bảo hiểm tự chi trả 30%).
- Quy định này không áp dụng trong trường hợp Người được bảo hiểm khám và điều trị tại các Cơ sở y tế/Bệnh viện công lập (trừ các Khoa quốc tế/Khoa điều trị tự nguyện/Khoa điều trị theo yêu cầu của Bệnh viện công lập).
- Lưu ý về điều trị răng:
Hợp đồng bảo hiểm bồi thường cho các chi phí khám chữa răng hợp lý, hợp lệ và được thực hiện tại các cơ sở y tế theo quy định sau:
- Chuyên khoa Nha tại tất cả các bệnh viện hoạt động hợp pháp trong phạm vi lãnh thổ Việt Nam.
- Tại Thành phố Hà Nội và Thành Phố Hồ Chí Minh: ngoài Chuyên khoa nha tại tất cả các bệnh viện nói trên, Công ty bảo hiểm chỉ chấp thuận bồi thường cho các chi phí phát sinh tại các Phòng khám/Nha khoa trong hệ thống bảo lãnh viện phí của Công ty bảo hiểm.
- Đối với các Tỉnh thành khác: ngoài Chuyên khoa Nha tại tất cả các bệnh viện nói trên, chấp thuận bồi thường cho các chi phí phát sinh tại các Phòng khám/Nha khoa có giấy phép đăng ký kinh doanh và giấy phép hành nghề hợp pháp và cấp được hóa đơn hợp lệ theo quy định của Bộ Tài Chính.
- Bảo hiểm Bảo Việt không chi trả cho các chi phí khám và điều trị tại cơ sở y tế thuộc danh sách Cơ sở y tế không chi trả bảo hiểm được cập nhật tại trang thông tin điện tử chính thức của Bảo hiểm Bảo Việt.
```
</details>

<details><summary>[4] FLX_BQL_S2_TB3 </summary>

```text
[Bảo hiểm Du lịch Flexi | Bảng quyền lợi | DU LỊCH FLEXI]
| MỤC | QUYỀN LỢI | Chương trình Bạc (Silver Plan) | Chương trình Vàng (Gold Plan) | Chương trình Bạch Kim (Platinum Plan) | Chương trình Kim Cương (Diamond Plan) |
|---|---|---|---|---|---|
| MỤC 6 | Tiền mang theo và Giấy tờ thông hành: Cung cấp quyền lợi bảo hiểm trong trường hợp bị mất Tiền và Giấy tờ thông hành mang theo do mất cắp hoặc thiên tai cộng với chi phí ăn ở đi lại phát sinh thêm | Không áp dụng | Tiền mang theo 4.000.000, các chi phí khác 20.000.000 | Tiền mang theo 6.000.000, các chi phí khác 60.000.000 | Tiền mang theo 8.000.000, các chi phí khác 80.000.000 |
| MỤC 7 | Trách nhiệm cá nhân: Cung cấp quyền lợi bảo hiểm trong trường hợp bị khiếu nại về trách nhiệm pháp lý đối với thương tật thân thể hoặc hư hỏng tài sản do một sự kiện xảy ra trong chuyến đi | Không áp dụng | 4.000.000.000 | 4.000.000.000 | 4.000.000.000 |
| MỤC 8 | Chuyến đi bị trì hoãn: Cung cấp quyền lợi bảo hiểm trong trường hợp hãng vận tải công cộng xuất phát chậm ít nhất 8 tiếng | Không áp dụng | 2.000.000 cho mỗi 8 tiếng và 10.000.000 tổng cộng | 2.000.000 cho mỗi 8 tiếng và 20.000.000 tổng cộng | 2.000.000 cho mỗi 8 tiếng và 30.000.000 tổng cộng |
| MỤC 9 | Mất tiền đặt cọc hay hủy bỏ chuyến đi: Cung cấp quyền lợi bảo hiểm đối với các khoản đặt cọc và thanh toán không được hoàn lại do hủy chuyến đi vì các lý do được nêu trong đơn bảo hiểm | Không áp dụng | 100.000.000 | 150.000.000 | 200.000.000 |
```
</details>

<details><summary>[5] BTB_BQL_S2_TB3 </summary>

```text
[Bảo Việt Tâm Bình | Bảng quyền lợi | BẢO VIỆT TÂM BÌNH]
| CHƯƠNG TRÌNH BẢO HIỂM | CƠ BẢN | MỞ RỘNG | NÂNG CAO | TOÀN DIỆN | ƯU VIỆT |
|---|---|---|---|---|---|
| • Chi phí phòng và giường, suất ăn theo tiêu chuẩn tại bệnh viện; • Chi phí phòng chăm sóc đặc biệt; điều trị cấp cứu; • Chi phí máu, huyết tương • Chi phí thuốc điều trị và sử dụng trong khi nằm viện; truyền máu, ô xy, huyết thanh, quần áo 1. Nằm viện do bệnh, tai nạn, thai sản (Tối đa 60 ngày/năm) |  |  |  |  |  |
| 4. Chi phí khám trước khi nhập viện và tái khám sau khi xuất viện (Không áp dụng cho thai sản) | Chi trả theo chi phí thực tế, tối đa 500.000/năm | Chi trả theo chi phí thực tế, tối đa 1.000.000/năm | Chi trả theo chi phí thực tế, tối đa 1.500.000/năm | Chi trả theo chi phí thực tế, tối đa 2.000.000/năm | Chi trả theo chi phí thực tế, tối đa 3.000.000/năm |
| 5. Xe cứu thương (Không áp dụng cho thai sản) | Chi trả theo chi phí thực tế, tối đa 1.000.000 | Chi trả theo chi phí thực tế, tối đa 2.000.000 | Chi trả theo chi phí thực tế, tối đa 2.500.000 | Chi trả theo chi phí thực tế, tối đa 3.000.000 | Chi trả theo chi phí thực tế, tối đa 3.500.000 |
| 6. Hỗ trợ giáo dục (Giới hạn tối đa 2 con) | người/năm | /người/năm | /người/năm | /người/năm | /người/năm |
|  | 500.000/con | 1.000.000/con | 2.000.000/con | 2.000.000/con | 2.500.000/con |
| QUYỀN LỢI BẢO HIỂM BỔ SUNG |  |  |  |  |  |
```
</details>

---

## v1-0120 · compare · medium · BTB ITC · phụ: B4ng (B4 bị ngưỡng chặn)

**Câu hỏi:** Hai sản phẩm Bảo Việt Tâm Bình và Bảo Việt Intercare được phân chia thành những chương trình bảo hiểm nào theo các đoạn trích trên?

**Đáp án chuẩn:** Cả hai sản phẩm đều có 5 chương trình bảo hiểm nhưng tên gọi hoàn toàn khác nhau: Bảo Việt Tâm Bình gồm các chương trình Cơ bản, Mở rộng, Nâng cao, Toàn diện, Ưu việt; trong khi Bảo Việt Intercare gồm các chương trình Select, Essential, Classic, Gold, Diamond.

**Evidence:** `BTB_BQL_S2_TB9 ITC_BQL_S1_TB1`

**Câu trả lời:**

> Bảo Việt Tâm Bình được phân chia thành các chương trình bảo hiểm: Cơ bản, Mở rộng, Nâng cao, Toàn diện và Ưu việt [1][3].
> 
> Bảo Việt Intercare được phân chia thành các chương trình bảo hiểm: Select, Essential, Classic, Gold và Diamond [2][4].

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] BTB_BQL_S2_TB8 ★</summary>

```text
[Bảo Việt Tâm Bình | Bảng quyền lợi | BẢO VIỆT TÂM BÌNH]
| CHƯƠNG TRÌNH BẢO HIỂM | CƠ BẢN | MỞ RỘNG | NÂNG CAO | TOÀN DIỆN | ƯU VIỆT |
|---|---|---|---|---|---|
| 2.3. Điều trị răng: |  |  |  |  |  |
| • Khám, chụp X.Q; • Viêm nướu (lợi), nha chu; • Trám răng bằng chất liệu thông thường như amalgam, composite, fuji...; • Điều trị tuỷ răng; • Cạo vôi răng (lấy cao răng) giới hạn 400.000/ người/năm; và • Nhổ răng bệnh lý (bao gồm tiểu phẫu, phẫu thuật). | Chi trả theo chi phí thực tế, tối đa 600.000/năm | Chi trả theo chi phí thực tế, tối đa 600.000/năm | Chi trả theo chi phí thực tế, tối đa 900.000/năm | Chi trả theo chi phí thực tế, tối đa 1.200.000/năm | Chi trả theo chi phí thực tế, tối đa 1.500.000/năm |
| 3. Trợ cấp mất giảm thu nhập/trợ cấp lương trong thời gian nghỉ điều trị do tai nạn và/hoặc ốm bệnh (áp dụng với hợp đồng bảo hiểm tổ chức) (QLBS 3) | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương |
```
</details>

<details open><summary>[2] ITC_BQL_S1_TB1 ★✓</summary>

```text
[Bảo Việt Intercare | Bảng quyền lợi | BẢNG QUYỀN LỢI BẢO HIỂM BẢO VIỆT INTERCARE]
Đơn vị: đồng
| QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN | QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BÊNH, TAI NẠN |
|---|---|---|---|---|---|
| CHƯƠNG TRÌNH | SELECT | ESSENTIAL | CLASSIC | GOLD | DIAMOND |
| Phạm vi lãnh thổ | Vùng 1 | Vùng 2 | Vùng 3 | Vùng 4 | Vùng 5 |
| Số tiền bảo hiểm (STBH) cho một thời hạn bảo hiểm và theo các giới hạn phụ dưới đây | 1.050.000.000 | 2.100.000.000 | 4.200.000.000 | 5.250.000.000 | 10.500.000.000 |
```
</details>

<details open><summary>[3] BTB_BQL_S2_TB3 ★</summary>

```text
[Bảo Việt Tâm Bình | Bảng quyền lợi | BẢO VIỆT TÂM BÌNH]
| CHƯƠNG TRÌNH BẢO HIỂM | CƠ BẢN | MỞ RỘNG | NÂNG CAO | TOÀN DIỆN | ƯU VIỆT |
|---|---|---|---|---|---|
| • Chi phí phòng và giường, suất ăn theo tiêu chuẩn tại bệnh viện; • Chi phí phòng chăm sóc đặc biệt; điều trị cấp cứu; • Chi phí máu, huyết tương • Chi phí thuốc điều trị và sử dụng trong khi nằm viện; truyền máu, ô xy, huyết thanh, quần áo 1. Nằm viện do bệnh, tai nạn, thai sản (Tối đa 60 ngày/năm) |  |  |  |  |  |
| 4. Chi phí khám trước khi nhập viện và tái khám sau khi xuất viện (Không áp dụng cho thai sản) | Chi trả theo chi phí thực tế, tối đa 500.000/năm | Chi trả theo chi phí thực tế, tối đa 1.000.000/năm | Chi trả theo chi phí thực tế, tối đa 1.500.000/năm | Chi trả theo chi phí thực tế, tối đa 2.000.000/năm | Chi trả theo chi phí thực tế, tối đa 3.000.000/năm |
| 5. Xe cứu thương (Không áp dụng cho thai sản) | Chi trả theo chi phí thực tế, tối đa 1.000.000 | Chi trả theo chi phí thực tế, tối đa 2.000.000 | Chi trả theo chi phí thực tế, tối đa 2.500.000 | Chi trả theo chi phí thực tế, tối đa 3.000.000 | Chi trả theo chi phí thực tế, tối đa 3.500.000 |
| 6. Hỗ trợ giáo dục (Giới hạn tối đa 2 con) | người/năm | /người/năm | /người/năm | /người/năm | /người/năm |
|  | 500.000/con | 1.000.000/con | 2.000.000/con | 2.000.000/con | 2.500.000/con |
| QUYỀN LỢI BẢO HIỂM BỔ SUNG |  |  |  |  |  |
```
</details>

<details open><summary>[4] ITC_BP_S6 ★</summary>

```text
[Bảo Việt Intercare | Biểu phí | 3. BẢO HIỂM NHA KHOA]
| Chương trình | Select | Essential | Classic | Gold | Diamond |
|---|---|---|---|---|---|
| Phí bảo hiểm | 6.600.000 | 7.000.000 | 8.300.000 | 8.800.000 | 9.300.000 |
```
</details>

<details><summary>[5] BTB_BQL_S2_TB2 </summary>

```text
[Bảo Việt Tâm Bình | Bảng quyền lợi | BẢO VIỆT TÂM BÌNH]
| CHƯƠNG TRÌNH BẢO HIỂM | CƠ BẢN | MỞ RỘNG | NÂNG CAO | TOÀN DIỆN | ƯU VIỆT |
|---|---|---|---|---|---|
| • Chi phí phòng và giường, suất ăn theo tiêu chuẩn tại bệnh viện; • Chi phí phòng chăm sóc đặc biệt; điều trị cấp cứu; • Chi phí máu, huyết tương • Chi phí thuốc điều trị và sử dụng trong khi nằm viện; truyền máu, ô xy, huyết thanh, quần áo 1. Nằm viện do bệnh, tai nạn, thai sản (Tối đa 60 ngày/năm) |  |  |  |  |  |
| 2.2. Phẫu thuật sinh con và các loại thủ thuật điều trị, tiểu phẫu | Chi trả theo chi phí thực tế, tối đa 3.000.000/năm | Chi trả theo chi phí thực tế, tối đa 5.000.000/năm | Chi trả theo chi phí thực tế, tối đa 12.000.000/năm | Chi trả theo chi phí thực tế, tối đa 14.000.000/năm | Chi trả theo chi phí thực tế, tối đa 20.000.000/năm |
| 2.3. Phẫu thuật khác | Chi trả theo chi phí thực tế, tối đa 10.000.000/năm | Chi trả theo chi phí thực tế, tối đa 16.000.000/năm | Chi trả theo chi phí thực tế, tối đa 30.000.000/năm | Chi trả theo chi phí thực tế, tối đa 40.000.000/năm | Chi trả theo chi phí thực tế, tối đa 60.000.000/năm |
| 3. Trợ cấp nằm viện (Tối đa 60 ngày/năm): Tại bệnh viện công từ tuyến tỉnh trở lên (Loại trừ các Khoa quốc tế/Khoa điều trị tự nguyện/Khoa điều trị theo yêu cầu) (Không áp dụng cho thai sản) | 100.000/ngày | 150.000/ngày | 200.000/ngày | 250.000/ngày | 400.000/ngày |
```
</details>

---

## v1-0125 · compare · medium · BTB BVP · phụ: B4ng (B4 bị ngưỡng chặn)

**Câu hỏi:** Hệ thống các chương trình bảo hiểm của Bảo Việt Tâm Bình và Bảo Việt An Gia được phân chia thành những gói nào và có sự khác nhau ra sao về tên gọi?

**Đáp án chuẩn:** Bảo Việt Tâm Bình gồm các chương trình Cơ bản, Mở rộng, Nâng cao, Toàn diện và Ưu việt; Bảo Việt An Gia gồm Đồng, Bạc, Vàng, Bạch Kim và Kim Cương. Tâm Bình đặt tên theo cấp độ quyền lợi, còn An Gia đặt tên theo kim loại và đá quý tăng dần.

**Evidence:** `BTB_BQL_S2_TB9 BVP_BP_S1_TB1`

**Câu trả lời:**

> Hệ thống các chương trình bảo hiểm của Bảo Việt Tâm Bình được phân chia thành 5 gói: CƠ BẢN, MỞ RỘNG, NÂNG CAO, TOÀN DIỆN, ƯU VIỆT [1].
> 
> Hệ thống các chương trình bảo hiểm của Bảo Việt An Gia được phân chia thành 5 gói: ĐỒNG, BẠC, VÀNG, BẠCH KIM, KIM CƯƠNG [2].
> 
> Sự khác nhau về tên gọi giữa hai hệ thống này là:
> - Bảo Việt Tâm Bình sử dụng tên gọi CƠ BẢN, MỞ RỘNG, NÂNG CAO, TOÀN DIỆN, ƯU VIỆT.
> - Bảo Việt An Gia sử dụng tên gọi ĐỒNG, BẠC, VÀNG, BẠCH KIM, KIM CƯƠNG.

**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):

<details open><summary>[1] BTB_BQL_S2_TB1 ★</summary>

```text
[Bảo Việt Tâm Bình | Bảng quyền lợi | BẢO VIỆT TÂM BÌNH]
| CHƯƠNG TRÌNH BẢO HIỂM | CƠ BẢN | MỞ RỘNG | NÂNG CAO | TOÀN DIỆN | ƯU VIỆT |
|---|---|---|---|---|---|
| • Chi phí phòng và giường, suất ăn theo tiêu chuẩn tại bệnh viện; • Chi phí phòng chăm sóc đặc biệt; điều trị cấp cứu; • Chi phí máu, huyết tương • Chi phí thuốc điều trị và sử dụng trong khi nằm viện; truyền máu, ô xy, huyết thanh, quần áo 1. Nằm viện do bệnh, tai nạn, thai sản (Tối đa 60 ngày/năm) |  |  |  |  |  |
| bệnh viện; • Chi phí băng, nẹp bột; • Chi phí tiêm truyền tĩnh mạch; • Chi phí xét nghiệm hoặc chẩn đoán bằng hình ảnh như X-quang, MRI, CT, PET, siêu âm, nội soi. Các xét nghiệm này phải do bác sĩ chỉ định là cần thiết để đánh giá tình trạng bệnh và là một phần của chi phí điều trị nằm viện; • Chi phí vật tư y tế cần thiết được sử dụng trong quá trình người bệnh nằm viện; • Chi phí sinh thường; • Các chi phí y tế liên quan khác. 2. Phẫu thuật do bệnh, tai nạn, thai sản Trả theo chi phí thực tế, tối đa không vượt quá hạn mức theo phân loại dưới đây: 2.1. Phẫu thuật đặc biệt (theo phụ lục II của Quy tắc bảo hiểm) | Chi trả theo chi phí thực tế, tối đa 400.000/ngày , lên đến 21.000.000/năm Chi trả theo chi phí thực tế, tối đa 18.000.000/năm | Chi trả theo chi phí thực tế, tối đa 600.000/ngày , lên đến 36.000.000/năm Chi trả theo chi phí thực tế, tối đa 30.000.000/năm | Chi trả theo chi phí thực tế, tối đa 1.000.000/ngày , lên đến 60.000.000/năm Chi trả theo chi phí thực tế, tối đa 50.000.000/năm | Chi trả theo chi phí thực tế, tối đa 1.400.000/ngày , lên đến 84.000.000/năm Chi trả theo chi phí thực tế, tối đa 60.000.000/năm | Chi trả theo chi phí thực tế, tối đa 2.000.000/ngày , lên đến 120.000.000/năm Chi trả theo chi phí thực tế, tối đa 97.000.000/năm |
```
</details>

<details open><summary>[2] BVP_BQL_S1_TB4 ★</summary>

```text
[Bảo Việt An Gia | Bảng quyền lợi | BẢNG QUYỀN LỢI BẢO HIỂM - BẢO VIỆT AN GIA]
| CHƯƠNG TRÌNH BẢO HIỂM | ĐỒNG | BẠC | VÀNG | BẠCH KIM | KIM CƯƠNG |
|---|---|---|---|---|---|
| II. QUYỀN LỢI BẢO HIỂM BỔ SUNG |  |  |  |  |  |
| 3. Bảo hiểm Sinh mạng cá nhân | Lựa chọn tham gia từ 20triệu đến 200triệu đồng | Lựa chọn tham gia từ 20triệu đến 300triệu đồng | Lựa chọn tham gia từ 20triệu đến 500triệu đồng | Lựa chọn tham gia từ 20triệu đến 700triệu đồng | Lựa chọn tham gia từ 20triệu đến 1tỷ đồng |
| 4. Bảo hiểm Nha khoa | 2.000.000/năm 1.000.000/lần khám | 2.000.000/năm 1.000.000/lần khám | 5.000.000/năm 2.500.000/lần khám | 10.000.000/năm 5.000.000/lần khám | 15.000.000/năm 7.500.000/lần khám |
| 5. Bảo hiểm Thai sản | Không | 21.000.000/năm | 21.000.000/năm | 21.000.000/năm | 31.500.000/năm |
```
</details>

<details><summary>[3] BTB_BQL_S2_TB8 </summary>

```text
[Bảo Việt Tâm Bình | Bảng quyền lợi | BẢO VIỆT TÂM BÌNH]
| CHƯƠNG TRÌNH BẢO HIỂM | CƠ BẢN | MỞ RỘNG | NÂNG CAO | TOÀN DIỆN | ƯU VIỆT |
|---|---|---|---|---|---|
| 2.3. Điều trị răng: |  |  |  |  |  |
| • Khám, chụp X.Q; • Viêm nướu (lợi), nha chu; • Trám răng bằng chất liệu thông thường như amalgam, composite, fuji...; • Điều trị tuỷ răng; • Cạo vôi răng (lấy cao răng) giới hạn 400.000/ người/năm; và • Nhổ răng bệnh lý (bao gồm tiểu phẫu, phẫu thuật). | Chi trả theo chi phí thực tế, tối đa 600.000/năm | Chi trả theo chi phí thực tế, tối đa 600.000/năm | Chi trả theo chi phí thực tế, tối đa 900.000/năm | Chi trả theo chi phí thực tế, tối đa 1.200.000/năm | Chi trả theo chi phí thực tế, tối đa 1.500.000/năm |
| 3. Trợ cấp mất giảm thu nhập/trợ cấp lương trong thời gian nghỉ điều trị do tai nạn và/hoặc ốm bệnh (áp dụng với hợp đồng bảo hiểm tổ chức) (QLBS 3) | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương | Theo số tiền bảo hiểm lựa chọn tối đa không quá 1.000.000.000/loại/năm, hoặc theo tháng lương |
```
</details>

<details><summary>[4] BVP_BP_S1_P3 </summary>

```text
[Bảo Việt An Gia | Biểu phí | BIỂU PHÍ BẢO HIỂM BẢO VIỆT AN GIA]
| CHƯƠNG TRÌNH BẢO HIỂM | ĐỒNG | BẠC | VÀNG | BẠCH KIM | KIM CƯƠNG |
|---|---|---|---|---|---|
| B. BẢO HIỂM BỔ SUNG TÙY CHỌN THEO NHU CẦU |  |  |  |  |  |
| • Trên 31 đến 50 tuổi | 1.956.000 | 2.282.000 | 2.608.000 | 3.433.000 | 5.301.000 |
| • Trên 51 đến 65 tuổi | 2.272.000 | 2.650.000 | 3.029.000 | 4.006.000 | 6.223.000 |
| 2. BH Tai nạn cá nhân | 0,1% STBH | 0,1% STBH | 0,1% STBH | 0,1% STBH | 0,1% STBH |
| 3. BH Sinh mạng cá nhân | 0,25% STBH | 0,25% STBH | 0,25% STBH | 0,25% STBH | 0,2% STBH |
| 4. BH Nha Khoa | 545.000 | 545.000 | 1.350.000 | 2.300.000 | 3.450.000 |
| 5. Bảo hiểm Thai sản Từ 18 - 45 tuổi | Không | 5.520.000 | 5.520.000 | 5.520.000 | 5.500.000 |
NGUYỄN CẢNH NAM – CÔNG TY BẢO VIỆT ĐÀ NẴNG |
Tel/Zalo: 0976.552.952
Địa chỉ : 257 Đống Đa, 97 Trần Phú, Đà Nẵng
```
</details>

<details><summary>[5] BTB_BQL_S2_TB2 </summary>

```text
[Bảo Việt Tâm Bình | Bảng quyền lợi | BẢO VIỆT TÂM BÌNH]
| CHƯƠNG TRÌNH BẢO HIỂM | CƠ BẢN | MỞ RỘNG | NÂNG CAO | TOÀN DIỆN | ƯU VIỆT |
|---|---|---|---|---|---|
| • Chi phí phòng và giường, suất ăn theo tiêu chuẩn tại bệnh viện; • Chi phí phòng chăm sóc đặc biệt; điều trị cấp cứu; • Chi phí máu, huyết tương • Chi phí thuốc điều trị và sử dụng trong khi nằm viện; truyền máu, ô xy, huyết thanh, quần áo 1. Nằm viện do bệnh, tai nạn, thai sản (Tối đa 60 ngày/năm) |  |  |  |  |  |
| 2.2. Phẫu thuật sinh con và các loại thủ thuật điều trị, tiểu phẫu | Chi trả theo chi phí thực tế, tối đa 3.000.000/năm | Chi trả theo chi phí thực tế, tối đa 5.000.000/năm | Chi trả theo chi phí thực tế, tối đa 12.000.000/năm | Chi trả theo chi phí thực tế, tối đa 14.000.000/năm | Chi trả theo chi phí thực tế, tối đa 20.000.000/năm |
| 2.3. Phẫu thuật khác | Chi trả theo chi phí thực tế, tối đa 10.000.000/năm | Chi trả theo chi phí thực tế, tối đa 16.000.000/năm | Chi trả theo chi phí thực tế, tối đa 30.000.000/năm | Chi trả theo chi phí thực tế, tối đa 40.000.000/năm | Chi trả theo chi phí thực tế, tối đa 60.000.000/năm |
| 3. Trợ cấp nằm viện (Tối đa 60 ngày/năm): Tại bệnh viện công từ tuyến tỉnh trở lên (Loại trừ các Khoa quốc tế/Khoa điều trị tự nguyện/Khoa điều trị theo yêu cầu) (Không áp dụng cho thai sản) | 100.000/ngày | 150.000/ngày | 200.000/ngày | 250.000/ngày | 400.000/ngày |
```
</details>

---
