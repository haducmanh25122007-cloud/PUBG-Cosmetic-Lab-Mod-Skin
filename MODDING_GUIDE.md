# Hướng dẫn phát triển mod cosmetic Lua — PUBG 0.16

> Tài liệu dành cho người muốn **nghiên cứu và tự xây dựng một dự án mod cosmetic**, không chỉ tải và khôi phục tệp có sẵn. Phạm vi ở đây là kiến trúc mã nguồn, dữ liệu cấu hình, tổ chức dự án và quy trình kiểm thử an toàn. Tài liệu không hướng dẫn inject DLL, can thiệp bộ nhớ, bypass anti-cheat, né phát hiện hoặc nạp mã trái phép vào trò chơi trực tuyến.

## 1. Bạn sẽ học được gì?

Sau khi đọc tài liệu, bạn có thể:

- Hiểu cấu trúc tổng thể của repository mẫu.
- Nhận diện phần cấu hình, danh mục cosmetic và adapter.
- Tổ chức một dự án Lua riêng có phiên bản, README và dữ liệu tách biệt.
- Chỉnh sửa dữ liệu mẫu theo cách có thể kiểm tra, soát lỗi và quản lý bằng Git.
- Phân biệt phần nào đã được xác nhận trong mã nguồn và phần nào cần runtime/API hợp lệ để triển khai.

**Lưu ý quan trọng:** mã nguồn v0.16 hiện có là một module Lua phụ thuộc vào môi trường chủ và API nội bộ. Repository chưa cung cấp tài liệu runtime/controller đầy đủ hoặc môi trường kiểm thử độc lập. Vì vậy không thể cam kết rằng chỉ sửa các bảng ID là tạo được một mod chạy được.

## 2. Kiến thức cần chuẩn bị

### Lua cơ bản

Nên nắm các nội dung:
- Biến: `local name = value`
- Bảng (table): `{ ... }`
- Hàm: `function name(...) ... end`
- Điều kiện: `if / elseif / else`
- Vòng lặp: `for`, `pairs`, `ipairs`
- Module: `return ...`

Ví dụ bảng dữ liệu Lua độc lập:

```lua
local cosmetic = {
    name = "Example Cosmetic",
    item_type = "weapon",
    base_id = 100001,
    skin_ids = {
        10000101,
        10000102,
    },
}

return cosmetic
```

Đây chỉ là ví dụ cấu trúc dữ liệu Lua để học tập; các ID trên là số minh họa, không phải ID PUBG hợp lệ.

### Công cụ

- Python 3: dùng script hiện có để ghép các phần mã.
- VS Code hoặc editor Lua: đọc, tìm kiếm và chỉnh sửa.
- Git: lưu lịch sử thay đổi, tạo nhánh và quay lại phiên bản trước.
- Lua interpreter phù hợp: chỉ để kiểm tra cú pháp Lua độc lập; cú pháp hợp lệ không đồng nghĩa module tương thích với runtime trò chơi.

## 3. Đọc kiến trúc của mã nguồn v0.16

Phần đầu mã nguồn cho thấy module có dạng:

```lua
return function(controller_class)
    local config = {
        -- configuration
    }
    -- module implementation
end
```

Có thể rút ra các điểm sau:

1. Tệp trả về một hàm nhận `controller_class`, thay vì chạy như một script độc lập.
2. Cấu hình được khai báo trong bảng `config`.
3. Cấu hình có adapter tham chiếu tới module avatar nội bộ.
4. Danh mục vũ khí được tổ chức thành các bảng có `base_id`, `name` và `skin_ids`.
5. Một số cờ điều khiển trạng thái khởi động và chế độ hoạt động.

Đây là nhận xét từ cấu trúc mã đang có. Chưa thể khẳng định đầy đủ cách controller được khởi tạo, cách API nội bộ được gọi hoặc quy trình nạp module vì repository chưa có tài liệu runtime tương ứng.

## 4. Các nhóm cấu hình đã nhận diện

Trong cấu hình đầu nguồn có các trường:

| Trường | Giá trị mẫu | Vai trò theo tên |
|---|---|---|
| `owner` | `@manhduathoi` | Tác giả/định danh dự án |
| `version` | `manhduathoi-skin-0.16` | Phiên bản module |
| `persist_selection` | `false` | Cờ lưu lựa chọn |
| `enabled_on_start` | `false` | Cờ bật khi khởi động |
| `open_menu_on_start` | `false` | Cờ mở menu khi khởi động |
| `default_selection` | `{}` | Lựa chọn mặc định |
| `adapter.avatar_module` | tên module nội bộ | Điểm tham chiếu adapter avatar |
| `weapon_catalogs` | danh sách bảng | Danh mục vũ khí/cosmetic |
| `upgrade_only` | `true` | Cờ giới hạn chế độ theo tên |
| `vehicle_catalog` | danh sách bảng | Danh mục phương tiện |

Không thay đổi các trường adapter/controller nếu chưa hiểu hợp đồng API mà runtime yêu cầu. Các tên trường cho biết ý định cấu hình, nhưng không thay thế tài liệu API.

## 5. Cách tổ chức một dự án mod mới

Không nên chỉnh thẳng bản duy nhất đang hoạt động. Hãy tạo bản sao dự án và tổ chức rõ ràng:

```text
my-cosmetic-project/
├── README.md
├── CHANGELOG.md
├── docs/
│   ├── DESIGN.md
│   └── TESTING.md
├── src/
│   ├── config.lua
│   ├── catalogs/
│   │   └── weapons.lua
│   └── main.lua
└── tests/
    └── validate_catalog.lua
```

Ý nghĩa:
- `config.lua`: metadata và các tùy chọn dự án.
- `catalogs/`: dữ liệu được chia theo loại vật phẩm.
- `main.lua`: điểm tổ chức module; chỉ tích hợp runtime khi có API hợp lệ và tài liệu chính thức.
- `tests/`: kiểm tra dữ liệu, ID trùng và cấu trúc bảng.
- `docs/`: ghi lại thiết kế, giả định và kết quả thử nghiệm.

Đây là cấu trúc đề xuất cho dự án mới, không phải cấu trúc bắt buộc của module v0.16.

## 6. Quy trình phát triển từng bước

### Bước 1 — Tạo bản sao và nhánh riêng

Giữ nguyên repository gốc. Tạo một repository mới hoặc branch riêng để thử nghiệm. Đặt tên phiên bản rõ ràng, ví dụ `0.1.0-dev`.

### Bước 2 — Viết mục tiêu và phạm vi

Ghi rõ dự án chỉ xử lý loại dữ liệu nào: ví dụ danh mục cosmetic minh họa, công cụ tra cứu ID từ dữ liệu bạn có quyền sử dụng, hoặc giao diện quản lý dữ liệu offline. Tránh tuyên bố hỗ trợ những phiên bản chưa được kiểm thử.

### Bước 3 — Tách dữ liệu khỏi logic

Đưa danh sách vật phẩm vào các bảng Lua riêng. Dùng tên trường nhất quán; mỗi mục nên có loại vật phẩm, mã định danh và ghi chú nguồn dữ liệu. Không tự đoán ID hoặc sao chép dữ liệu không rõ quyền sử dụng.

### Bước 4 — Kiểm tra dữ liệu

Tạo kiểm tra cho:
- Trường bắt buộc không bị thiếu.
- ID có kiểu số và nằm trong phạm vi hợp lệ do nguồn dữ liệu của bạn quy định.
- Không có ID trùng ngoài ý muốn.
- Tên và loại vật phẩm không để trống.
- Dữ liệu có nguồn gốc và phiên bản rõ ràng.

### Bước 5 — Tích hợp trong môi trường được phép

Chỉ kết nối module với một runtime/API mà bạn có quyền sử dụng và có tài liệu hợp lệ. Trước khi tích hợp cần biết rõ:
- Cách runtime nạp module.
- Định dạng controller được truyền vào.
- API nào được phép gọi.
- Cách đăng ký và dọn dẹp tài nguyên.
- Cách xử lý lỗi và tương thích phiên bản.

Các thông tin trên chưa được xác nhận trong repository này. Không tự suy đoán tên hàm hoặc quy trình nạp.

### Bước 6 — Kiểm thử và ghi nhận

Kiểm tra cú pháp Lua, dữ liệu, lỗi đầu vào và khả năng khôi phục. Ghi rõ môi trường, phiên bản, kết quả và giới hạn trong `docs/TESTING.md`. Không thử trên tài khoản chính hoặc môi trường trực tuyến nếu việc sửa đổi không được cho phép.

### Bước 7 — Phát hành

- Tăng phiên bản.
- Cập nhật CHANGELOG.
- Viết hướng dẫn cài đặt đúng với runtime đã xác minh.
- Ghi checksum cho tệp phát hành.
- Nêu rõ giới hạn, giấy phép và nguồn dữ liệu.

## 7. Quản lý dự án bằng Git

Một quy trình cơ bản:

```bash
git init
git add .
git commit -m "chore: initial project structure"
git switch -c feature/catalog-data
# chỉnh sửa và kiểm tra dữ liệu
git add .
git commit -m "feat: add cosmetic catalog data"
git switch main
git merge feature/catalog-data
```

Nên commit theo từng thay đổi nhỏ. Không đưa mật khẩu, token, cookie, tệp tài khoản hoặc dữ liệu riêng tư vào repository.

## 8. Checklist trước khi gọi là một mod hoàn chỉnh

- [ ] Mục tiêu và phạm vi dự án được mô tả rõ.
- [ ] Cấu trúc Lua được tách thành module dễ bảo trì.
- [ ] Dữ liệu có nguồn gốc, phiên bản và kiểm tra hợp lệ.
- [ ] Không có ID tự đoán hoặc dữ liệu không rõ quyền sử dụng.
- [ ] Runtime/API tích hợp có tài liệu và được phép sử dụng.
- [ ] Đã kiểm thử trong môi trường hợp lệ.
- [ ] Có hướng dẫn cài đặt/loại bỏ đã xác minh.
- [ ] README, CHANGELOG và giấy phép được cập nhật.

## 9. Giới hạn của hướng dẫn này

Tài liệu này dạy cách tổ chức và phát triển dự án Lua dựa trên cấu trúc quan sát được trong source v0.16. Nó **không phải công thức hoàn chỉnh để tạo mod PUBG có thể chạy ngay**. Muốn viết hướng dẫn triển khai cụ thể cần có tài liệu runtime/API hợp pháp, phiên bản mục tiêu và môi trường thử nghiệm được phép.

Không hướng dẫn hoặc hỗ trợ:
- Inject mã/DLL vào tiến trình trò chơi.
- Sửa bộ nhớ hoặc gói tin của trò chơi trực tuyến.
- Vô hiệu hóa, né tránh hoặc bypass anti-cheat.
- Vượt cơ chế bảo vệ tài khoản hoặc truy cập trái phép.

## 10. Tài liệu liên quan

- [README — tổng quan repository](README.md)
- [USER_GUIDE — tải và khôi phục source](USER_GUIDE.md)
- [Release notes v0.16](docs/RELEASE-v0.16.md)
