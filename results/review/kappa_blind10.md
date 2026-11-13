## Chấm mù 10 câu manual30

File chấm `results/review/blind10_B4_v1.1_test_scored.xlsx`, khóa `results/review/blind10_key.csv`, điểm chốt `results/review/manual30_B4_v1_test_20261107-1335.csv`. Kappa trống khi cả hai lần chỉ có một nhãn.

### Chấm mù so với điểm chốt manual30 (độ nhất quán của người chấm)

| Cột | n | kappa | CI95 bootstrap | Trùng chính xác | Lệch ≤ 1 |
| --- | --- | --- | --- | --- | --- |
| correct_1_5 (weighted, bậc hai) | 10 | 0,961 | [0,81; 1,00] | 0,80 | 1,00 |
| faithful_1_5 (weighted, bậc hai) | 10 | 0,630 | [0,30; 0,94] | 0,70 | 0,90 |
| cite_ok (Cohen) | 10 | 0,286 | [0,00; 0,78] | 0,70 | – |
| error_code (Cohen) | 10 | 0,324 | [-0,05; 0,70] | 0,50 | – |

### Chấm mù so với đề xuất dx_* (kiểm tra neo theo đề xuất)

| Cột | n | kappa | CI95 bootstrap | Trùng chính xác | Lệch ≤ 1 |
| --- | --- | --- | --- | --- | --- |
| correct_1_5 (weighted, bậc hai) | 10 | 0,961 | [0,81; 1,00] | 0,80 | 1,00 |
| faithful_1_5 (weighted, bậc hai) | 10 | 0,630 | [0,30; 0,94] | 0,70 | 0,90 |
| cite_ok (Cohen) | 10 | 0,286 | [0,00; 0,78] | 0,70 | – |
| error_code (Cohen) | 10 | 0,324 | [-0,05; 0,70] | 0,50 | – |

### Từng câu (chấm mù / manual30)

| Mã | qid | correct | faithful | cite_ok | error_code |
| --- | --- | --- | --- | --- | --- |
| M01 | v1-0080 | 5 / 5 | 5 / 5 | 1 / 1 | OK / OK |
| M02 | v1-0025 | 5 / 5 | 5 / 5 | 1 / 0 | OK / G2 |
| M03 | v1-0057 | 3 / 4 | 5 / 4 | 1 / 1 | G1 / OK |
| M04 | v1-0050 | 1 / 1 | 2 / 4 | 0 / 0 | F2 / R1 |
| M05 | v1-0107 | 1 / 1 | 3 / 3 | 1 / 1 | F2 / G1 |
| M06 | v1-0127 | 3 / 2 | 4 / 4 | 1 / 1 | G1 / G1 |
| M07 | v1-0100 | 5 / 5 | 5 / 5 | 1 / 1 | OK / OK |
| M08 | v1-0124 | 3 / 3 | 4 / 3 | 1 / 0 | R1 / R1 |
| M09 | v1-0110 | 5 / 5 | 5 / 5 | 1 / 0 | OK / G2 |
| M10 | v1-0091 | 5 / 5 | 5 / 5 | 1 / 1 | OK / OK |
