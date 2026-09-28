# Smart CRM Wagtail

Smart CRM là ứng dụng CRM xây dựng trên Django và Wagtail. Nhân viên tạo khách hàng và ghi chú trong Wagtail Admin. Khi ghi chú được lưu, Gemini AI sẽ tóm tắt nội dung và phân loại khách hàng thành `Tiềm năng`, `Đang cân nhắc` hoặc `Không quan tâm`.

## 1. Yêu cầu

- Git
- Python 3.13 khuyến nghị
- Quyền truy cập internet để cài package và gọi Gemini API
- Gemini API key nếu muốn chạy phân tích AI thật

> Python 3.14 hiện chưa tương thích với bộ pin package trong `requirements.txt`: `grpcio-status==1.71.2` không có bản phù hợp cho Python 3.14. Dùng Python 3.13 để cài đặt ổn định.

## 2. Clone mã nguồn

```powershell
git clone <URL_REPOSITORY>
cd CRM_AI_WagtailNhom9
```

## 3. Tạo và kích hoạt môi trường ảo trên Windows PowerShell

```powershell
py -3.13 -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
python --version
```

Khi thành công, đầu dòng lệnh sẽ có tiền tố `(venv)`.

Nếu đã có sẵn môi trường ảo được tạo bằng Python 3.13, chỉ cần chạy:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Trên Git Bash dùng:

```bash
source venv/Scripts/activate
```

## 4. Cài thư viện

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Nếu pip báo lỗi `ResolutionImpossible` liên quan đến `grpcio-status`, kiểm tra phiên bản bằng `python --version`. Hãy xóa môi trường ảo Python 3.14 và tạo lại bằng Python 3.13:

```powershell
deactivate
Remove-Item -Recurse -Force venv
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 5. Cấu hình Gemini API key

Tạo file `.env` từ file mẫu:

```powershell
Copy-Item .env.example .env
```

Mở `.env` và thay giá trị mẫu:

```env
GEMINI_API_KEY=your_real_gemini_api_key
```

Có thể tạo key tại Google AI Studio: <https://aistudio.google.com/app/apikey>.

Không commit `.env`, không đưa API key vào `README.md`, log, screenshot hoặc mã nguồn. Nếu key đã bị chia sẻ, hãy thu hồi và tạo key mới ngay.

Khi chưa có key, ứng dụng vẫn có thể khởi động nhưng ghi chú sẽ nhận kết quả dự phòng:

- Tóm tắt: `Thiếu API Key`
- Phân loại: `Không xác định`

## 6. Khởi tạo database

```powershell
python manage.py migrate
```

Tạo tài khoản quản trị Wagtail:

```powershell
python manage.py createsuperuser
```

Nhập username, email và password theo hướng dẫn trên màn hình. Đây là tài khoản dùng để đăng nhập `/admin/`.

## 7. Chạy ứng dụng

```powershell
python manage.py runserver
```

Các địa chỉ chính:

- Website: <http://127.0.0.1:8000/>
- Wagtail Admin: <http://127.0.0.1:8000/admin/>
- Django Admin: <http://127.0.0.1:8000/django-admin/>
- Tìm kiếm: <http://127.0.0.1:8000/search/>

## 8. Luồng sử dụng CRM

1. Đăng nhập Wagtail Admin tại `/admin/`.
2. Mở Snippets và tạo `Customer` với tên, email, số điện thoại và công ty.
3. Tạo `Note`, chọn khách hàng và nhập nội dung trao đổi.
4. Lưu ghi chú. `Note.save()` gọi Gemini, sau đó ghi `ai_summary` và `ai_category` vào database.
5. Mở trang Dashboard đã xuất bản để kiểm tra khách hàng, ghi chú, tóm tắt và nhãn phân loại.

Bộ kịch bản chi tiết và dữ liệu mẫu nằm trong [QA_TEST_PLAN.md](QA_TEST_PLAN.md).

## 9. Chạy kiểm tra

Kiểm tra cấu hình Django:

```powershell
python manage.py check
```

Chạy test:

```powershell
python manage.py test
```

Kiểm tra migration còn thiếu:

```powershell
python manage.py makemigrations --check --dry-run
```

Các test AI nên mock lời gọi Gemini để không phụ thuộc mạng, quota hoặc API key thật.

## 10. Cấu trúc chính

```text
home/models.py          Customer, Note và CRMDashboardPage
home/ai_services.py     Gọi Gemini và phân tích ghi chú
home/tests.py           Test Wagtail hiện có
search/views.py         Tìm kiếm trang Wagtail
smart_crm/settings/     Cấu hình dev và production
QA_TEST_PLAN.md         Kịch bản QA và dữ liệu test
```

## 11. Lưu ý hiện tại

- `requirements.txt` và Dockerfile đang dùng các phiên bản thư viện cần được đồng bộ nếu muốn chạy Python 3.14.
- `home/tests.py` hiện import `HomePage`, trong khi model hiện tại khai báo `CRMDashboardPage`. Cần dev thống nhất tên model và cập nhật migration/test/template trước khi xem toàn bộ test suite là đạt.
- `Note.save()` gọi AI mỗi lần ghi bản ghi. Việc sửa một ghi chú có thể tạo thêm request Gemini và phát sinh quota.
- Dashboard phải được tạo và publish trong Wagtail trước khi kiểm thử hiển thị dữ liệu CRM.
