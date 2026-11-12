# Hướng dẫn toàn bộ quy trình phát triển công cụ và mod PUBG Cosmetic

> **Phạm vi:** Tài liệu này hướng dẫn xây dựng quy trình phát triển trong môi trường offline/thử nghiệm được cho phép hoặc thông qua giao diện mod/plugin chính thức. Tài liệu không hướng dẫn gắn vào tiến trình PUBG đang chạy, đọc/ghi bộ nhớ game, chèn mã, vượt anti-cheat, can thiệp lưu lượng mạng được bảo vệ hoặc tạo overlay trái phép. PUBG/KRAFTON có thể không cho phép việc chỉnh sửa game. Chỉ sử dụng dữ liệu và giao diện mà bạn có quyền truy cập, kiểm tra và chỉnh sửa.

Quy trình được chia thành ba dự án:
1. **Phân tích SDK và xuất metadata.**
2. **Skin ID Dumper:** quét nguồn dữ liệu được phép và tạo catalog có thể tìm kiếm.
3. **Cosmetic Mod:** sử dụng catalog trong môi trường thử nghiệm thông qua adapter có tài liệu.

Source Lua 0.16 trong repository hiện tham chiếu đến các module nội bộ của game. Điều đó không chứng minh rằng có SDK công khai, runtime hook an toàn hoặc API UI trong game được hỗ trợ. Cần xác minh từng thành phần; không tự đoán offset, tên class, địa chỉ hàm hay API không có tài liệu.

---

# 0. Xác định nguồn dữ liệu được phép sử dụng

Trước khi viết code, cần xác định chính xác dumper được phép đọc dữ liệu từ đâu:

- SDK chính thức hoặc bản metadata export được cung cấp cho mục đích phát triển mod.
- Bản game developer/test mà bạn sở hữu hoặc được cấp quyền kiểm tra.
- Các tệp catalog JSON, CSV, XML hoặc định dạng export khác.
- Plugin API có tài liệu và cho phép truy cập metadata cosmetic.

Nếu không có plugin API được tài liệu hóa, phiên bản dumper đầu tiên phải là ứng dụng desktop/offline để đọc các tệp export hợp lệ. Chỉ có thể thêm bảng điều khiển bên trong game khi có giao diện plugin/modding chính thức hoặc được cấp quyền, hỗ trợ tạo UI và truy cập dữ liệu.

Tạo file `docs/DATA_SOURCE.md` và ghi lại:

| Trường | Nội dung cần ghi |
|---|---|
| Nguồn dữ liệu | SDK, bản test, file export hoặc plugin |
| Quyền sử dụng | Chủ sở hữu và phạm vi được phép |
| Phiên bản | Phiên bản SDK/build/catalog |
| Định dạng | JSON, CSV, XML, metadata đã sinh |
| Cách truy cập | API có tài liệu hoặc đọc file |
| Giới hạn | Dữ liệu nào không được đọc, sửa hoặc phát hành |

Không tiếp tục nếu chưa xác định rõ nguồn và quyền sử dụng.

# PHẦN I — Phân tích SDK và xuất metadata

## 1. Chuẩn bị môi trường

Môi trường đề xuất trên Windows:

- Windows 10/11.
- Git.
- Visual Studio Code.
- Python 3.11 trở lên.
- Lua 5.4 để chạy các ví dụ Lua độc lập.
- Bộ công cụ SDK chính thức, nếu chủ sở hữu SDK cung cấp.
- Thư mục dữ liệu thử nghiệm riêng; không thử nghiệm trên tài khoản đang chơi.

Tạo cấu trúc dự án:

~~~text
pubg-cosmetic-lab/
├── docs/
├── sdk/
│   ├── input/          # file export được phép; không commit dữ liệu hạn chế
│   └── reports/
├── dumper/
├── catalog/
├── mod/
├── tests/
└── README.md
~~~

Khởi tạo Git:

~~~bash
git init
git branch -M main
~~~

Tạo file `.gitignore`:

~~~gitignore
.venv/
__pycache__/
*.log
sdk/input/
*.pak
*.ucas
*.utoc
*.uasset
*.umap
.env
~~~

Chỉ thêm các phần mở rộng đúng với gói SDK thực tế. Không đưa dữ liệu độc quyền hoặc bị hạn chế lên GitHub.

## 2. Tìm hiểu metadata trong SDK

Một bản SDK export có thể mô tả class, struct, enum, property, function, tên asset và mã định danh. Nội dung chính xác phụ thuộc SDK. Hãy bắt đầu từ tài liệu và metadata được sinh chính thức; không lấy tên hoặc offset từ phiên bản khác rồi mặc định chúng đúng.

Với mỗi kiểu dữ liệu tìm được, ghi lại:

- Tên kiểu đầy đủ.
- Lớp cha nếu có tài liệu.
- Các thuộc tính và kiểu dữ liệu.
- Tên enum và giá trị.
- Chữ ký hàm nếu SDK công bố.
- Phiên bản SDK/build.
- Mức độ liên quan đến cosmetic.

Không tự tạo offset bộ nhớ, object pointer, địa chỉ hàm hoặc quy ước gọi hàm không được tài liệu hóa. Những thông tin đó không phải API ổn định.

## 3. Chuẩn hóa danh sách metadata

Tạo file `sdk/inventory.schema.json`. Ví dụ dưới đây chỉ minh họa cấu trúc, không khẳng định đây là class thật của PUBG:

~~~json
{
  "schema_version": 1,
  "source": {
    "name": "authorized-sdk-export",
    "version": "REPLACE_WITH_REAL_VERSION"
  },
  "types": [
    {
      "name": "Example.CosmeticRecord",
      "kind": "class",
      "properties": [
        { "name": "Id", "type": "integer" },
        { "name": "DisplayName", "type": "string" }
      ]
    }
  ]
}
~~~

## 4. Xây dựng bộ đọc file export

Ở phiên bản đầu, nên hỗ trợ JSON và CSV. Tách phần đọc dữ liệu khỏi giao diện:

- `sdk/parser.py`: đọc file export được phép.
- `sdk/normalize.py`: chuyển trường dữ liệu nguồn về schema thống nhất.
- `sdk/validate.py`: kiểm tra trường bắt buộc và kiểu dữ liệu.
- `sdk/report.py`: tạo báo cáo inventory dễ đọc.

Nguyên tắc: gặp định dạng lạ, file lỗi hoặc thiếu trường bắt buộc thì phải báo lỗi rõ ràng, không tự đoán dữ liệu.

### Tiêu chí hoàn thành giai đoạn SDK

- [ ] Đã ghi rõ nguồn dữ liệu và quyền sử dụng.
- [ ] Đã ghi phiên bản SDK/build.
- [ ] Parser đọc được một file mẫu nhỏ.
- [ ] Trường lạ được giữ lại hoặc báo cáo.
- [ ] Dữ liệu lỗi tạo thông báo dễ hiểu.
- [ ] Không cần truy cập tiến trình game hoặc dùng offset không có tài liệu.
- [ ] Có thể tạo lại báo cáo inventory với kết quả nhất quán.

---

# PHẦN II — Xây dựng Skin ID Dumper

## 5. Xác định chức năng của dumper

Dumper có nhiệm vụ chuyển nguồn metadata được phép thành catalog thống nhất. Nó không thay đổi game và không mở khóa vật phẩm.

Các chức năng mong muốn:

- Chọn file hoặc thư mục export hợp lệ.
- Quét các file có định dạng được hỗ trợ.
- Hiển thị tiến trình và file đang xử lý.
- Tạm dừng/hủy quá trình quét dài.
- Hiển thị kết quả trong bảng.
- Tìm kiếm theo ID hoặc tên.
- Lọc theo loại vật phẩm, súng, phương tiện hoặc phiên bản nguồn nếu có dữ liệu.
- Phát hiện ID trùng và bản ghi sai định dạng.
- Xuất JSON, CSV và TXT.
- Lưu báo cáo kèm phiên bản nguồn và thời gian quét.

### Về nút tự quét bên trong game

Một bảng điều khiển xuất hiện bên trong PUBG cần API plugin/modding chính thức hoặc được cấp quyền, có chức năng tạo UI và truy cập dữ liệu. Repository hiện chưa có tài liệu xác minh API đó. Vì vậy, hãy làm bản desktop GUI trước. Sau này có thể thêm adapter giao diện cho runtime thử nghiệm được phép mà không phải viết lại lõi scanner.

## 6. Cấu trúc thư mục đề xuất

~~~text
dumper/
├── app.py
├── ui/
│   ├── main_window.py
│   └── progress_view.py
├── sources/
│   ├── base.py
│   ├── json_source.py
│   └── csv_source.py
├── scanner/
│   ├── scan_service.py
│   ├── normalize.py
│   └── validate.py
├── exporters/
│   ├── json_exporter.py
│   ├── csv_exporter.py
│   └── txt_exporter.py
└── models/
    └── cosmetic.py
~~~

Tách thành các lớp độc lập:

1. **Source reader:** mở file dữ liệu được phép.
2. **Scanner:** tìm các bản ghi phù hợp.
3. **Normalizer:** chuyển bản ghi về schema chung.
4. **Validator:** kiểm tra chất lượng dữ liệu.
5. **UI:** hiển thị trạng thái và kết quả.
6. **Exporter:** ghi dữ liệu ra file.

Cách tổ chức này giúp thay nguồn JSON bằng nguồn khác được phép mà không phải viết lại giao diện.

## 7. Thiết kế cấu trúc một bản ghi skin

Có thể dùng schema sau:

~~~json
{
  "schema_version": 1,
  "source_version": "example-export-1",
  "generated_at": "2026-01-01T00:00:00Z",
  "items": [
    {
      "id": "REPLACE_WITH_VERIFIED_ID",
      "name": "Example item",
      "category": "weapon_skin",
      "weapon": "REPLACE_WITH_VERIFIED_WEAPON",
      "rarity": null,
      "source": "authorized-json-export"
    }
  ]
}
~~~

Các giá trị trên chỉ là ví dụ/placeholder, không phải ID PUBG thật. Nên lưu ID dưới dạng chuỗi để tránh mất số 0 ở đầu hoặc làm hỏng mã định danh không thuần số.

Các nhóm có thể dùng nếu nguồn dữ liệu hỗ trợ:

- `weapon_skin`: skin súng.
- `character_outfit`: trang phục nhân vật.
- `helmet`: mũ.
- `backpack`: ba lô.
- `vehicle_skin`: skin phương tiện.
- `melee`: vũ khí cận chiến.
- `other`: nhóm khác.

## 8. Quy trình quét dữ liệu

1. Người dùng chọn file/thư mục export.
2. Kiểm tra đường dẫn có thể đọc và nằm trong phạm vi đã chọn.
3. Chỉ liệt kê các phần mở rộng được hỗ trợ.
4. Đọc từng file với giới hạn kích thước và xử lý lỗi.
5. Chuẩn hóa các bản ghi tìm được.
6. Kiểm tra trường bắt buộc.
7. Loại trùng theo nhóm, ID và phiên bản nguồn.
8. Ghi lại bản ghi bị từ chối cùng lý do.
9. Hiển thị bảng kết quả.
10. Chỉ xuất file sau khi người dùng xác nhận.

Không được âm thầm xóa ID trùng. Hãy hiển thị bản ghi trùng và vị trí nguồn để người dùng xử lý.

## 9. Thiết kế giao diện GUI

Gợi ý bố cục:

~~~text
┌─────────────────────────────────────────────────────────────┐
│ Cosmetic ID Dumper                                          │
├─────────────────────────────────────────────────────────────┤
│ Nguồn: [Chọn thư mục export...] [Tải dữ liệu]               │
│ [Bắt đầu quét] [Hủy] [Xuất JSON] [Xuất CSV] [Xuất TXT]      │
│ Tiến trình: [====================          ] 65%             │
│ Tìm kiếm: [____________________] Loại: [Tất cả v]            │
├────────────┬───────────────────┬──────────────┬──────────────┤
│ ID         │ Tên               │ Loại         │ Nguồn        │
├────────────┼───────────────────┼──────────────┼──────────────┤
│ ...        │ ...               │ ...          │ ...          │
└────────────┴───────────────────┴──────────────┴──────────────┘
│ Tìm thấy: N | Trùng: N | Lỗi: N                              │
└─────────────────────────────────────────────────────────────┘
~~~

Có thể dùng PySide6 hoặc một thư viện GUI desktop được duy trì tốt. Chạy scanner trong worker thread để cửa sổ không bị treo. Nút Hủy phải dừng worker an toàn. Không báo thành công trước khi đọc, kiểm tra và xuất dữ liệu hoàn tất.

## 10. Định dạng xuất dữ liệu

JSON nên là định dạng chính vì lưu được metadata. CSV tiện mở bằng bảng tính. TXT có thể dùng một ID trên mỗi dòng.

Nếu định dạng cho phép, mỗi bản export nên có:

- Phiên bản schema.
- Phiên bản nguồn/build.
- Thời gian tạo.
- Tổng số bản ghi.
- Số bản ghi trùng.
- Số bản ghi lỗi.
- Phiên bản dumper.

Ví dụ tiêu đề CSV:

~~~csv
id,name,category,weapon,source_version
~~~

## 11. Kiểm thử dumper

Tạo dữ liệu kiểm thử giả lập; không dùng ID PUBG tự đoán. Tối thiểu phải kiểm tra:

- Bản ghi hợp lệ.
- Thiếu ID.
- Tên rỗng.
- ID trùng.
- Loại không xác định.
- JSON sai cú pháp.
- File đầu vào rất lớn.
- Tên có ký tự Unicode.
- Hủy quét giữa chừng.
- Xuất rồi nhập lại dữ liệu.

### Tiêu chí hoàn thành giai đoạn Dumper

- [ ] GUI đọc được JSON/CSV được phép.
- [ ] Hiển thị tiến trình quét.
- [ ] Nút Hủy hoạt động.
- [ ] Tìm kiếm và lọc theo loại hoạt động.
- [ ] Báo cáo ID trùng và bản ghi lỗi.
- [ ] Xuất JSON/CSV/TXT hợp lệ.
- [ ] JSON đã xuất có thể nạp lại.
- [ ] Không tương tác với tiến trình được bảo vệ hoặc anti-cheat.

---

# PHẦN III — Xây dựng Skin Catalog

## 12. Tách dữ liệu thô và dữ liệu đã chuẩn hóa

~~~text
catalog/
├── raw/                  # dữ liệu dump; thường không đưa lên Git
├── curated/
│   ├── weapons.json
│   ├── outfits.json
│   ├── vehicles.json
│   └── other.json
├── schemas/
│   └── cosmetic.schema.json
└── reports/
~~~

Raw dump là dữ liệu gốc lấy từ nguồn. Curated catalog là dữ liệu đã làm sạch để mod sử dụng. Không chỉnh sửa trực tiếp file raw.

## 13. Kiểm tra và quản lý phiên bản catalog

Mỗi lần phát hành catalog cần lưu:

- Phiên bản game/bản test.
- Phiên bản SDK/export nguồn.
- Phiên bản schema catalog.
- Phiên bản dumper.
- Ngày tạo.
- Số bản ghi theo từng nhóm.
- Số bản ghi trùng và lỗi.
- Hash/checksum của file export.

Khi có nguồn phiên bản mới, tạo báo cáo so sánh gồm ID mới, ID bị xóa, tên thay đổi, nhóm thay đổi và dữ liệu xung đột. Không mặc định một ID luôn mang cùng ý nghĩa ở mọi phiên bản game.

---

# PHẦN IV — Xây dựng Cosmetic Mod

## 14. Tách dữ liệu catalog khỏi logic mod

~~~text
mod/
├── main.lua
├── config.lua
├── adapters/
│   └── supported_runtime.lua
├── catalog/
│   ├── weapons.lua
│   └── vehicles.lua
├── presets/
├── ui/
├── tests/
└── README.md
~~~

Adapter là lớp duy nhất giao tiếp với runtime. Adapter phải sử dụng API có tài liệu và được phép. Nếu chưa có runtime được hỗ trợ, chạy logic mod trong simulator cục bộ và không kết nối vào bản game chính thức.

## 15. Khai báo cấu hình

Ví dụ cấu hình cho môi trường test cục bộ:

~~~lua
return {
    enabled_on_start = false,
    open_menu_on_start = false,
    persist_selection = false,
    default_selection = {},
    catalog_schema_version = 1
}
~~~

Đặt mặc định an toàn. Mod nên khởi động ở trạng thái tắt trong test harness cho đến khi người dùng bật.

## 16. Xây dựng hệ thống chọn skin và preset

Triển khai từng chức năng riêng:

1. Nạp catalog.
2. Kiểm tra schema catalog.
3. Hiển thị các nhóm vật phẩm.
4. Tìm theo tên hoặc ID.
5. Chọn vật phẩm.
6. Lưu lựa chọn thành preset.
7. Nạp/xóa preset.
8. Khôi phục mặc định.
9. Xuất/nhập preset người dùng.

Preset nên tham chiếu ID trong catalog thay vì sao chép toàn bộ bản ghi. Nếu ID không còn tồn tại trong catalog mới, hiển thị cảnh báo và bỏ qua lựa chọn đó an toàn.

## 17. Định nghĩa hợp đồng runtime adapter

Không tự bịa tên hàm PUBG. Có thể định nghĩa giao diện cho simulator của dự án:

~~~lua
local Adapter = {}

function Adapter:get_capabilities()
    return {
        catalog_read = true,
        cosmetic_preview = false,
        apply_cosmetic = false
    }
end

function Adapter:preview(item)
    return false, "Preview is not supported by this test adapter"
end

return Adapter
~~~

Đây là adapter mẫu cho test harness của bạn, không phải API PUBG. Adapter thật chỉ được viết dựa trên SDK/plugin có tài liệu và trong phạm vi được phép.

## 18. Kiểm thử khi không chạy game thật

Xây dựng simulator với nhân vật, súng và vị trí cosmetic giả lập. Kiểm tra:

- Catalog nạp thành công.
- Catalog sai bị từ chối.
- Tìm kiếm và lựa chọn hoạt động.
- Preset lưu và nạp lại được.
- ID không còn tồn tại được xử lý đúng.
- UI vô hiệu hóa chức năng adapter không hỗ trợ.
- Không ghi dữ liệu ra ngoài thư mục dự án/test.

### Tiêu chí hoàn thành giai đoạn Mod

- [ ] Schema catalog được kiểm tra.
- [ ] UI độc lập với runtime.
- [ ] Preset sử dụng ID ổn định.
- [ ] ID bị thiếu tạo cảnh báo.
- [ ] Test adapter không truy cập game thật.
- [ ] Tích hợp runtime chỉ được làm khi có API được phép và tài liệu rõ ràng.

---

# PHẦN V — Đóng gói và bảo trì

## 19. Quản lý phiên bản riêng cho từng thành phần

Dùng phiên bản riêng cho:

- Định dạng SDK inventory: `schema_version`.
- Dumper: semantic version, ví dụ `1.0.0`.
- Catalog: phiên bản theo nguồn/build.
- Mod: semantic version kèm schema catalog tương thích.

Không gọi catalog là “mới nhất” nếu chưa ghi phiên bản nguồn và ngày tạo.

## 20. Checklist phát hành

- [ ] Loại bỏ SDK riêng tư hoặc dữ liệu bị hạn chế.
- [ ] Ghi nguồn và quyền sử dụng.
- [ ] Có dữ liệu mẫu giả lập.
- [ ] Có hướng dẫn cài đặt và build.
- [ ] Ghi các giới hạn đã biết.
- [ ] Chạy test từ bản clone sạch.
- [ ] Tạo checksum cho file phát hành.
- [ ] Ghi rõ dự án không chính thức và không liên kết với PUBG/KRAFTON.

## 21. Cần bổ sung gì để hướng dẫn sát PUBG hơn?

Repository hiện có source Lua tham chiếu module nội bộ của game, nhưng chưa có tài liệu về định dạng export SDK PUBG được hỗ trợ, plugin API runtime được cấp quyền hoặc hợp đồng UI extension trong game đã xác minh.

Để chuyển lộ trình này thành hướng dẫn triển khai cụ thể theo phiên bản, cần bổ sung:

1. Định dạng SDK/export mà bạn được phép sử dụng.
2. Các file source hoặc đoạn code chính xác thực hiện UI dump và scanner trong các bản 0.1–0.16.
3. Tài liệu plugin/runtime API cho phép tạo UI và truy cập metadata.
4. Một file export mẫu đã loại bỏ dữ liệu nhạy cảm hoặc độc quyền.

Nếu thiếu các thông tin này, mọi offset, tên class, tên hàm, cách quét trực tiếp hoặc cách tạo nút bên trong PUBG đều chỉ là suy đoán.

## Thứ tự triển khai đề xuất

| Mốc | Kết quả cần đạt |
|---|---|
| M1 — SDK inventory | Báo cáo metadata đã phân tích và có phiên bản |
| M2 — Dumper core | Scanner, kiểm tra dữ liệu và exporter |
| M3 — Dumper GUI | Bảng kết quả, tiến trình và nút hủy |
| M4 — Catalog | Cơ sở dữ liệu cosmetic sạch, có phiên bản |
| M5 — Mod core | Cấu hình, lựa chọn skin và preset |
| M6 — Test UI | Simulator cục bộ hoạt động |
| M7 — Adapter được hỗ trợ | Chỉ triển khai khi có hợp đồng API hợp lệ |
| M8 — Phát hành | Gói có thể build lại và tài liệu đầy đủ |

**Nguyên tắc quan trọng:** kiểm chứng từng lớp bằng test trước khi nối sang lớp tiếp theo. Dumper phải hoạt động độc lập với mod; logic catalog và preset của mod cũng phải chạy được khi PUBG không mở.
