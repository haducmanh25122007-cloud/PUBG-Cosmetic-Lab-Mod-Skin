# PUBG 0.16 Cosmetic Lab

Kho lưu trữ mã nguồn mod cosmetic PUBG 0.16 do cộng đồng quản lý, không chính thức.

> **Tuyên bố miễn trừ:** Dự án không liên kết, không được PUBG hoặc KRAFTON xác nhận hay hỗ trợ. Chỉ sử dụng trong môi trường cho phép chỉnh sửa. Không đảm bảo tương thích hoặc an toàn tài khoản.

## Tài liệu hướng dẫn — Tiếng Việt

- [HUONG_DAN_TOAN_BO_QUY_TRINH.md](HUONG_DAN_TOAN_BO_QUY_TRINH.md) — hướng dẫn quy trình từ phân tích SDK, xây dựng Skin ID Dumper, chuẩn hóa catalog đến phát triển mod và đóng gói.
- [MODDING_GUIDE.md](MODDING_GUIDE.md) — hướng dẫn phát triển dự án mod Lua: kiến trúc, cấu hình, tổ chức dữ liệu, kiểm thử và quản lý Git.
- [USER_GUIDE.md](USER_GUIDE.md) — hướng dẫn tải repository, khôi phục mã nguồn Lua và đọc cấu hình hiện có.

## Documentation — English

- [END_TO_END_TOOLCHAIN_GUIDE.md](END_TO_END_TOOLCHAIN_GUIDE.md) — end-to-end roadmap for SDK analysis, Skin ID Dumper, catalog development, mod architecture, testing, and release.

## Mã nguồn

Mã nguồn Lua gốc được chia thành tám phần liên tiếp trong `src/parts/` do giới hạn kích thước khi tải file lên GitHub.

### Ghép lại file Lua gốc

Yêu cầu: Python 3.

Mở terminal tại thư mục gốc repository và chạy:

~~~bash
python src/assemble_source.py
~~~

Script sẽ ghép tám phần theo đúng thứ tự và tạo file:

~~~text
src/ManhDuathoi-Skin-0.16-Cosmetic-Refine.lua
~~~

Không đổi thứ tự, chỉnh sửa hoặc bỏ thiếu các file part trước khi ghép.

## Cấu trúc repository

- `src/parts/` — các phần mã nguồn liên tiếp.
- `src/assemble_source.py` — script ghép mã nguồn.
- `README.md` — thông tin dự án và hướng dẫn.

## Ghi chú

- Source tham chiếu các module và API nội bộ của game; có thể không hoạt động ở phiên bản game khác.
- Repository không chứa asset game hoặc tệp PUBG độc quyền.
- Repository chưa khai báo giấy phép. Mọi quyền vẫn thuộc chủ sở hữu tương ứng.
