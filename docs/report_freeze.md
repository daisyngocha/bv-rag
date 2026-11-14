# Đóng băng số liệu báo cáo ĐA1 (`da1-report-v1`)

Ngày 14/11/2026. Mọi số trong báo cáo, slide ĐA1 lấy từ trạng thái dưới đây; muốn đổi số phải tạo bản đóng băng mới.

## 1. Mã nguồn và dữ liệu

| Mục | Giá trị |
| --- | --- |
| Commit `main` khi tái lập | `42ea7da1674e339a98314ca8a27a666a7655ddbb` (Merge PR #50, 14/11 11:41) |
| Tag | `da1-report-v1` (gắn vào commit thêm file này) |
| `benchmark/benchmark_v1.1.jsonl` | sha256 `474d28fe4625c37c3e63da18a4a8616746e069f1d1bca3b77a3eee970960d8f2` |
| `data/manifests/v1.json` | sha256 `d112dcd46db35186d1e68ed980720d234f7764a6c92daf492e8f2afec3f985f5` |
| Lưu trữ run | Drive `MyDrive/bv-rag/freeze/da1-report-v1/`: `da1-report-v1_runs.tar.gz` (21 run, `log.jsonl` + `meta.json`) và `SHA256SUMS` |
| `da1-report-v1_runs.tar.gz` | sha256 `7971c2e9385a15afeb08d7613dd742e51a4b053bcb0bfd87f8ae7bca5e85bc5e`, 671.139 byte |

Kiểm lại bản trên Drive: `rclone copy gdrive:bv-rag/freeze/da1-report-v1 <thư mục>`, `sha256sum -c SHA256SUMS` (dòng tarball),
giải nén rồi `sha256sum -c SHA256SUMS` cho các dòng `runs/`.

## 2. Tái lập (14/11, laptop WSL CPU, chỉ tính từ log, không chạy GPU, không gọi judge)

```bash
export PYTHONPATH=.
.venv/bin/python -m eval.metrics $(cat configs/test_runs_official.txt) --align-threshold 0.3 --bench benchmark/benchmark_v1.1.jsonl
for j in j1 c2 j1x; do
  .venv/bin/python -m eval.ragas_summary --judge $j --bench benchmark/benchmark_v1.1.jsonl $(ls results/*_v1.1_test_*.csv)
done
.venv/bin/python scripts/build_results_summary.py
.venv/bin/python -m pytest tests/ -q
```

Kết quả: `git status` trống ở `results/` và `docs/results_summary.md` (số sinh lại trùng bản đã commit);
pytest 74 passed, 4 skipped (2 test cần `fastapi`, không cài trong `.venv`; 2 test cần `BV_TEST_PG` + psql).

## 3. Run

Run test chính thức (`configs/test_runs_official.txt`), dev dùng chọn ngưỡng/prompt (decision-log 07/11), demo 09/11.
Không gồm: dev B0–B2 0832/0814, B3/B3hyb 1012 (đo dao động), B4 1325 (chạy lại cấu hình 1259), các run demo khác
(`B4_demo_20261109-0208` không có trong tài liệu).

| run_id | Vai trò | Số dòng log | sha256 `log.jsonl` | sha256 `meta.json` |
| --- | --- | --- | --- | --- |
| `B0_v1_test_20261107-0904` | test chính thức | 120 | `635e33919a617c257cd35507055f05e90b6bfbe85a6f1d665a2ab5ff787f96fc` | `13e7ef2e6b4767452156101e06aa0451237093aa2f37f800b50b599e64fcd202` |
| `B1_v1_test_20261107-0904` | test chính thức | 120 | `82f47f3325dfad706c56e9d1eeb917bad1f10a1d9e740a4d2814b968ef382cc8` | `a5dbd5823f9eb22837454a2910b635f20e0f28311383b3e137012e85b0a9dd2e` |
| `B2_v1_test_20261107-0904` | test chính thức | 120 | `9475ad327e2b73710c59eaaa0875a34efd1e6aa1639d541c615b373c2d03b12b` | `3ef9c6b747d07c2b4bd02812969623934f1ba64af9b12071e6ec15d69411dde5` |
| `B3hyb_v1_test_20261107-1020` | test chính thức | 120 | `0504df21df13feb24a94112debf2136e602836bd821dc0be5093ccbed80f43b7` | `2eb8e32314bee7d4cf14fd8cb3ca9e81b3e8b70991db64b7e17769e0bb249568` |
| `B3_v1_test_20261107-1020` | test chính thức | 120 | `c339eaaaa035c2988e580896ad5f90de7a888286153b4012b5e1338de0e1660d` | `edcbd751e59b953b3c87ed7904a742d3df991b0c4c6e747876b226fc80699566` |
| `B4rr_v1_test_20261107-1335` | test chính thức | 120 | `3239f6e76c4a557cbe5d2539bd2dc3d98a5818d96abd6bb3e478ec54bc73728e` | `631d2805d814489580072af4e0bf79db15416e59c5717841b47a28449e5cac84` |
| `B4ng_v1_test_20261107-1335` | test chính thức | 120 | `be50870055b3e77794f94d58fb81985c2605ec351334181b69cfc5bc8c838009` | `4bec23deb22e4f39ba4a3789de24e326a2c98cfb9c0bd067f71ad93c604ad468` |
| `B4_v1_test_20261107-1335` | test chính thức | 120 | `91610a2b3755f5c9a7a4acc0f75f403082656c28cd3070709ce41aadf4a20c91` | `7b6e9a7d73e2ae35952ccbd7f1df0ca1ad18c7c7a06c0bd4d122faae1b8320b6` |
| `B1_v1_dev_20261107-0832_r0` | dev: ngưỡng căn chỉnh B1 (0,3) | 30 | `bbbb8fd58aff28473f7db2fca9d8bee4ff1e7bb93d0f63de11febe03c23f605a` | `977939ce06aa0af06db1de1491bf3da42af5c46d1d22f03710d634c0ef2222e6` |
| `B1_v1_dev_20261107-0832_r1` | dev: ngưỡng căn chỉnh B1 (0,3) | 30 | `c1167c57308089f5b8620b447ce891a70c601f462e8bf773f664f5ac6feb3489` | `148ad63ab47b91c11da58faad0f266d01a56057060695b1c7ad75fe27415cdae` |
| `B1_v1_dev_20261107-0832_r2` | dev: ngưỡng căn chỉnh B1 (0,3) | 30 | `5377118272f4d8cb714fbdf86d949c8d9f5d4dad260010e14f837bcd9f98ae39` | `5bc499b38983dbbfa36798d2223e9523a0199b9b0508d7443380b647f1b54b22` |
| `B4_v1_dev_20261107-1131_r0` | dev: rag_v2, quét ngưỡng min_score | 30 | `79911b16edd6f9426c902e7e49bae74918c312f242e490bac1423b592a5e6306` | `cf9dc2b0f45ea9734f517af687c5ebfed4ea721db6859fc68ef247cdcb41ee9a` |
| `B4_v1_dev_20261107-1131_r1` | dev: rag_v2, quét ngưỡng min_score | 30 | `71e93e80d0d0e92affd009555fbcf4f8580e0a66e0f391418eab34ec8f102dd1` | `ba3be1c3c1f5e9bd46985c679e6cbbb8af2839169507f39fb26fe2552bde99c6` |
| `B4_v1_dev_20261107-1131_r2` | dev: rag_v2, quét ngưỡng min_score | 30 | `04908d7cb5d77c935797ae526ae4bba5d7b58789d9d910df7b4f8e767be51bb5` | `134d5c08edca2ae60fae379fc092742a338fdca241d99d9306c0774406724f15` |
| `B4rr_v1_dev_20261107-1131_r0` | dev: ablation B4rr (rag_v1) | 30 | `2cfba44ed9ba9cad0e2dbb018343b55dae88ada29a75cb0db8da8ad88eae8a1f` | `21eb49945bcb3eb64800452b96f6640f4b76338fbd911d66ece20614691016f8` |
| `B4rr_v1_dev_20261107-1131_r1` | dev: ablation B4rr (rag_v1) | 30 | `a26d6d6a47d750a378fe6f32f3c94ebe43ad451c3e74e8ef5be8ec1075f2ed2b` | `5b35a7132feb0438c9f530f180b0c170b72f4aca1300a2188126dd9dd936457d` |
| `B4rr_v1_dev_20261107-1131_r2` | dev: ablation B4rr (rag_v1) | 30 | `82a0d0c6da8f85a4c54e8b2733fe98b8567fec1c1394b44cdf238361d14d0bbf` | `d86ac43845a1bd6784ade8a659a781bed12e90067b61ecd46ef8c7cbf802f271` |
| `B4_v1_dev_20261107-1259_r0` | dev: nhận rag_v3 (min_score 0,90) | 30 | `a3532af1456bb785a5b47501f3ac004509d299630dd4abb852faf830a65df3da` | `7b45f3bec0266a6fcfeba0da30d9f6950d54557bc427b225f64e91e300253ffb` |
| `B4_v1_dev_20261107-1259_r1` | dev: nhận rag_v3 (min_score 0,90) | 30 | `efd5d93119d972d47bcc770bd716becbd6dc71b9c8dcb81425aa27f87f4b1913` | `2890b473a8e3075e05bd2f151a6f200901c475bedd063cf42286787f5eeb0812` |
| `B4_v1_dev_20261107-1259_r2` | dev: nhận rag_v3 (min_score 0,90) | 30 | `eb765d9bdc284f02960a97b2d12462e65bd4b0eea48b19427ee215e871d99c2d` | `5a6af3604cc898500267ae3c4e74b4718436e457359ebeb7163105c464f8fb7a` |
| `B4_demo_20261109-0843` | demo 09/11 (kịch bản 6 câu) | 12 | `72e12c194833c92c434fb1696320ef1beada20a1439cd5f0b3338cf0009ca9e8` | `71a4b962ec6a935054bc428ae9cc51042dbd6ace690001514f9c2695759c0bdd` |

## 4. Điểm Ragas chính thức (`results/ragas/`)

j1 = Gemini (chính), c2 = Claude Haiku 5.5 (phụ), j1x = LLM j1 + embedding Gemini (bổ sung, results_w8 mục 7).
Mỗi CSV có `.usage.jsonl` cùng tên (token). Không thuộc bản đóng băng: `*__c1*`, `*__c1b*`, `*__c2b*`, `*__j1b*`
(hiệu chỉnh judge, chỉ B4/B4ng), `_unofficial/`, `run_full_*.log`.

| File | sha256 |
| --- | --- |
| `B0_v1_test_20261107-0904__j1.csv` | `c1869bca18a118a337f31a6b60140216a8c7eca588f3625bf9ec962d7e932f03` |
| `B1_v1_test_20261107-0904__j1.csv` | `b666c973f6c120eb3abfc96a74dd6b9ceb106e53b309df27a5762961a5f27264` |
| `B2_v1_test_20261107-0904__j1.csv` | `fa7cf189c76cc663aeacbe2ba6707f1d3c73b781dc1e5062ccd6c1e900d29aa0` |
| `B3_v1_test_20261107-1020__j1.csv` | `1982f7198f65aa91fa84de356dc5e82c1c6d9eb1a561a3a15c98ad36dacc6f8b` |
| `B3hyb_v1_test_20261107-1020__j1.csv` | `a80005a2a0766ef3a67c9440fc39f013f5e4e7b0d9c6e16a90bcac60c885a7be` |
| `B4_v1_test_20261107-1335__j1.csv` | `d0221b8d58f9c4d7b491d44215d8658a735ddb90682334c333a70c2047b44e1e` |
| `B4ng_v1_test_20261107-1335__j1.csv` | `afad6137963331e61b3ccbcae9f2c5333dc72623841821d104a9776dc9e75d0b` |
| `B4rr_v1_test_20261107-1335__j1.csv` | `0d1874b9332d42873db39eee64056c4eea493402dd58785ffc2c8d831011f4ab` |
| `B0_v1_test_20261107-0904__c2.csv` | `cf8c8fca92cfaa78d7c09e4873fc17b72085a3726d674f2acc24e29ed0c6ab19` |
| `B1_v1_test_20261107-0904__c2.csv` | `976dc829f8dfbea204928335209ca48d159dcecc8ae3f947ed2c3e2289366adb` |
| `B2_v1_test_20261107-0904__c2.csv` | `20613a3f848799f826d51f520e7b90ed74827d51dcb7493df2010af4474f0a8f` |
| `B3_v1_test_20261107-1020__c2.csv` | `9db34341354988b04f2f33a07dea21b740377d019802ca43201b4d3d10c73c2a` |
| `B3hyb_v1_test_20261107-1020__c2.csv` | `5d046afd3a7c8a91d87f7558321a7a5aa0956ca7b2e08c5768dc4eba7e30fe14` |
| `B4_v1_test_20261107-1335__c2.csv` | `a8b362ff9cd4034363299cd675d57f8c6b785b9b818ec0c929428126cdca0c86` |
| `B4ng_v1_test_20261107-1335__c2.csv` | `188be33dddffacd4f827848f7a6ba7a3e61607c60885db2b9c4b2f8bd507a24e` |
| `B4rr_v1_test_20261107-1335__c2.csv` | `ae8bcc047e5951592ce256ef5fcea592cabc16896d995546422cba2cab58e68b` |
| `B0_v1_test_20261107-0904__j1x.csv` | `d8f9ecb55e42afe03592962c9e7b075510956f608e72d6915fd85f07c971b006` |
| `B1_v1_test_20261107-0904__j1x.csv` | `ca26ba7038246dfb3318c017cfddf8359af39bc81ba6dc39babfa81e4e85b0e6` |
| `B2_v1_test_20261107-0904__j1x.csv` | `1e3e3ace7111203bf40ea06457c20074b7359fc54361382dece59acc84803ec3` |
| `B3_v1_test_20261107-1020__j1x.csv` | `e7f01dc0fef55f959c87f361960e454bf27dfbae391f9254615a401802a36fe3` |
| `B3hyb_v1_test_20261107-1020__j1x.csv` | `1329351a7670eeb3e9928353a3a35661a82634c2772ece0e311d7345676359ea` |
| `B4_v1_test_20261107-1335__j1x.csv` | `28f51b7cc14bd4c50da7737725ad8adfdf42072a56b0c303201e89e1df4e5b47` |
| `B4ng_v1_test_20261107-1335__j1x.csv` | `aa061c85fd881e9aef427990c0e56e78a11847a6b9f17d1286ffbff1e7cca834` |
| `B4rr_v1_test_20261107-1335__j1x.csv` | `dedef8f1df6dd05d98f36bc274669f3799326795802648935c6489dc408e689d` |

Bảng metric sinh lại (đầu ra bước 2):

| File | sha256 |
| --- | --- |
| `results/B0_v1.1_test_20261107-0904.csv` | `68f9ac97422c3409ae8d541516b7f2de110994d8cf3b48f973e5fcd43ea27a6e` |
| `results/B1_v1.1_test_20261107-0904.csv` | `c75ac60f9f75c5272e245088e173946455b60f3db6f5680d9d109330ccd6ca6c` |
| `results/B2_v1.1_test_20261107-0904.csv` | `50cbaa76fe21b575e10a004a3a0962e2977a6000d024d09c54602e4b173c0feb` |
| `results/B3_v1.1_test_20261107-1020.csv` | `0cd8e55394658e28770c99266f481a6b53f5b0402ae05f3f198c6e6fb9b0a071` |
| `results/B3hyb_v1.1_test_20261107-1020.csv` | `2b4db1944770fc7c837c6859d19d9c8e350eb516d53f1f420a5c670546111fd5` |
| `results/B4_v1.1_test_20261107-1335.csv` | `a27781bb8160261259427a6dbab0c425acc71fb7c6907d5e6683176fa378ba55` |
| `results/B4ng_v1.1_test_20261107-1335.csv` | `fdfddb7eb298756ce9d03ef9cf16d1a5ee2995d9c5516adb78bca3a9cc545f01` |
| `results/B4rr_v1.1_test_20261107-1335.csv` | `924c208e19b3319031daac68c60e8e5a1576de94ff35bded1418ea90a85b1e80` |
| `docs/results_summary.md` | `aaa768303fb4d4dba06689e178929ff92d4b09d33fcc4e5f08f0cc194a6a2058` |

## 5. Môi trường judge (`.venv-judge`, Python 3.10.12)

```
anthropic==2.8.0
langchain==0.3.30
langchain-community==0.3.31
langchain-core==0.3.86
langchain-google-genai==2.1.12
langchain-openai==0.3.35
langchain-text-splitters==0.3.11
ragas==0.4.3
```

`google-genai` không cài trong `.venv-judge`; j1/j1x gọi Gemini qua `langchain-google-genai` (kèm `google-ai-generativelanguage==0.12.1`).
