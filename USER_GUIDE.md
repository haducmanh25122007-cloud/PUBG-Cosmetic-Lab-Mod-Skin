# Hướng dẫn sử dụng — PUBG Cosmetic Lab v0.16

> **Phạm vi tài liệu:** Hướng dẫn tải mã nguồn, khôi phục tệp Lua, kiểm tra cấu trúc và đọc cấu hình. Đây không phải hướng dẫn can thiệp vào tiến trình trò chơi, nạp mã vào PUBG, vượt anti-cheat hoặc sử dụng mod trong môi trường bị cấm.

## 1. Giới thiệu

Kho lưu trữ chứa mã nguồn Lua liên quan đến dữ liệu/giao diện cosmetic của PUBG phiên bản 0.16. Mã gốc được chia thành 8 phần để thuận tiện tải lên GitHub:

- `src/parts/source-01.lua.part` đến `source-08.lua.part`: các đoạn mã theo đúng thứ tự.
- `src/assemble_source.py`: script ghép các phần thành một tệp Lua.
- `src/ManhDuathoi-Skin-0.16-Cosmetic-Refine.lua`: tệp được tạo sau khi chạy script ghép.

Đây là mã nguồn dạng module, không phải ứng dụng độc lập có thể mở trực tiếp bằng cách nhấp đúp.

## 2. Yêu cầu

- Máy tính Windows, macOS hoặc Linux.
- Python 3 đã cài đặt.
- Kết nối Internet để tải repository.
- Trình soạn thảo văn bản/mã nguồn như VS Code hoặc Notepad++ (không bắt buộc).

Kiểm tra Python:

**Windows**
```powershell
py --version
```

**macOS/Linux**
```bash
python3 --version
```

Nếu máy báo không tìm thấy lệnh Python, hãy cài Python 3 từ trang chính thức https://www.python.org/downloads/ rồi mở lại Terminal/PowerShell.

## 3. Tải mã nguồn từ GitHub

1. Mở trang repository: https://github.com/haducmanh25122007-cloud/PUBG-Cosmetic-Lab-Mod-Skin
2. Nhấn nút **Code**.
3. Chọn **Download ZIP**.
4. Giải nén ZIP vào một thư mục dễ tìm, ví dụ `PUBG-Cosmetic-Lab-Mod-Skin`.
5. Mở thư mục vừa giải nén và kiểm tra có thư mục `src` cùng tệp `README.md`.

Không tải riêng lẻ hoặc đổi tên các tệp `.part`, vì script cần đủ 8 phần và ghép theo thứ tự tên tệp.

## 4. Khôi phục tệp Lua gốc

Mở Terminal/PowerShell tại thư mục gốc repository — nơi có `README.md`.

**Windows**
```powershell
py src/assemble_source.py
```

Nếu lệnh `py` không hoạt động nhưng `python` có hoạt động:
```powershell
python src/assemble_source.py
```

**macOS/Linux**
```bash
python3 src/assemble_source.py
```

Khi chạy thành công, chương trình in đường dẫn tệp vừa tạo và dung lượng. Tệp đầu ra nằm tại:

```text
src/ManhDuathoi-Skin-0.16-Cosmetic-Refine.lua
```

Nếu xuất hiện thông báo `Expected 8 source parts`, hãy kiểm tra thư mục `src/parts/` có đủ đúng 8 tệp `source-01.lua.part` đến `source-08.lua.part` hay không. Không tự ý đổi tên hoặc xóa phần nào.

## 5. Mở và đọc mã nguồn

1. Mở tệp `src/ManhDuathoi-Skin-0.16-Cosmetic-Refine.lua` bằng VS Code hoặc Notepad++.
2. Dùng chức năng tìm kiếm để tìm tên biến, tên module hoặc ID cần nghiên cứu.
3. Giữ một bản sao nguyên gốc trước khi chỉnh sửa.
4. Nếu chỉnh sửa các phần `.part`, hãy hiểu rằng việc ghép lại sẽ đưa thay đổi đó vào tệp Lua đầu ra.

Lưu ý: tệp bắt đầu bằng một hàm Lua dạng `return function(controller_class)`. Điều này cho thấy nó được thiết kế để được một chương trình chủ tương thích gọi vào; bản thân tệp không tự cung cấp toàn bộ môi trường chạy. Mã có tham chiếu tới module/API nội bộ của trò chơi, vì vậy chỉ có tệp Lua không đủ để kết luận rằng nó có thể chạy độc lập.

## 6. Một số thiết lập có thể nhận diện trong mã

Các giá trị dưới đây được ghi nhận trong cấu hình nguồn; đây là mô tả giá trị mặc định, không phải cam kết về hành vi thực tế:

| Thiết lập | Giá trị mặc định | Ý nghĩa theo tên cấu hình |
|---|---:|---|
| `enabled_on_start` | `false` | Không bật tính năng ngay khi khởi động |
| `open_menu_on_start` | `false` | Không tự mở menu khi khởi động |
| `persist_selection` | `false` | Không lưu lựa chọn qua phiên theo cấu hình |
| `upgrade_only` | `true` | Cấu hình giới hạn theo hướng nâng cấp |
| `vehicle_dump_on_start` | `false` | Không tự chạy mục dump xe khi khởi động |

Nguồn cũng có danh mục cosmetic cho một số vật phẩm/vũ khí, trong đó phần cấu hình đầu có M416 và AUG. Không nên suy diễn rằng mọi ID đều còn hợp lệ ở phiên bản trò chơi hiện tại.

## 7. Lỗi thường gặp

**Lỗi không tìm thấy Python**
- Thử `py --version`, `python --version` (Windows) hoặc `python3 --version` (macOS/Linux).
- Cài Python 3 nếu chưa có, sau đó mở cửa sổ Terminal/PowerShell mới.

**Báo thiếu source parts**
- Kiểm tra đã giải nén đầy đủ repository.
- Kiểm tra thư mục `src/parts/` có đủ 8 tệp, từ số 01 đến 08.
- Không đổi tên các tệp.

**Không thấy tệp Lua sau khi chạy**
- Đọc thông báo trong Terminal/PowerShell.
- Đảm bảo bạn chạy lệnh từ bản repository đã giải nén và có quyền ghi vào thư mục.

**Mở tệp Lua nhưng không biết chạy thế nào**
- Đây là module cần một môi trường chủ tương thích, không phải chương trình độc lập.
- Repository hiện không cung cấp đầy đủ tài liệu về runtime/controller/API nội bộ hoặc quy trình triển khai được xác minh. Không tự ý nạp mã vào trò chơi hay dùng công cụ không rõ nguồn gốc.

## 8. An toàn, tương thích và trách nhiệm

- Đây là dự án không chính thức, không liên kết, không được PUBG/KRAFTON xác nhận hay hỗ trợ.
- Tính tương thích với bản game khác 0.16 chưa được xác minh.
- Không có bảo đảm về an toàn tài khoản. Việc sửa đổi hoặc can thiệp trò chơi có thể vi phạm điều khoản dịch vụ và dẫn tới hạn chế tài khoản.
- Chỉ nghiên cứu mã hoặc thử nghiệm trong môi trường mà bạn có quyền và việc sửa đổi được cho phép.
- Không tải thêm DLL, injector, executable hoặc công cụ không rõ nguồn gốc chỉ để cố chạy mã.
- Repository không kèm tài sản game/proprietary files và hiện không khai báo giấy phép sử dụng.

## 9. Cấu trúc repository

```text
.
├── README.md
├── USER_GUIDE.md
├── docs/
│   └── RELEASE-v0.16.md
└── src/
    ├── assemble_source.py
    └── parts/
        ├── source-01.lua.part
        ├── source-02.lua.part
        ├── source-03.lua.part
        ├── source-04.lua.part
        ├── source-05.lua.part
        ├── source-06.lua.part
        ├── source-07.lua.part
        └── source-08.lua.part
```

## 10. Kiểm tra nhanh sau khi khôi phục

- [ ] Có đủ 8 tệp trong `src/parts/`.
- [ ] Script chạy không báo lỗi.
- [ ] Tệp `src/ManhDuathoi-Skin-0.16-Cosmetic-Refine.lua` đã được tạo.
- [ ] Tệp Lua mở được bằng trình soạn thảo văn bản.
- [ ] Giữ lại bản gốc trước khi thực hiện bất kỳ chỉnh sửa nào.

---

**Tài liệu có thể được cập nhật khi có thông tin runtime, phiên bản và quy trình kiểm thử hợp lệ được xác minh.**
