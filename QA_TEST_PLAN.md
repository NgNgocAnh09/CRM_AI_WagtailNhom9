# QA Test Plan - Smart CRM

## 1. Mục tiêu

Kiểm tra luồng từ tạo khách hàng trong Wagtail Admin, tạo ghi chú, gọi Gemini AI, lưu kết quả phân tích và hiển thị dữ liệu trên Dashboard.

## 2. Tài khoản và dữ liệu chuẩn bị

- Tài khoản superuser đã tạo bằng `python manage.py createsuperuser`.
- Server chạy bằng `python manage.py runserver`.
- `.env` có `GEMINI_API_KEY` hợp lệ cho nhóm test AI thật.
- Một trang `CRMDashboardPage` được tạo dưới root page và đã publish.
- Không dùng email trùng nhau giữa các lần test vì `Customer.email` là duy nhất.

## 3. Kịch bản use case

### UC-01: Tạo khách hàng mới

**Thao tác**

1. Đăng nhập `/admin/`.
2. Mở Snippets > Customer > Add.
3. Nhập tên, email, số điện thoại và công ty.
4. Lưu.

**Kết quả mong đợi**

- Bản ghi được tạo một lần.
- Email không hợp lệ hoặc trùng bị báo lỗi tại form.
- Khách hàng xuất hiện trong danh sách và có thể được chọn khi tạo Note.

### UC-02: Tạo ghi chú và phân tích AI

**Thao tác**

1. Mở Snippets > Note > Add.
2. Chọn khách hàng.
3. Nhập một nội dung mẫu ở mục 4.
4. Lưu và mở lại bản ghi.

**Kết quả mong đợi**

- `ai_summary` có nội dung ngắn gọn.
- `ai_category` thuộc một trong ba nhóm: `Tiềm năng`, `Đang cân nhắc`, `Không quan tâm`.
- Nội dung HTML trong RichText không làm hỏng prompt phân tích.
- Nội dung gốc, khách hàng và thời gian tạo vẫn được giữ nguyên.

### UC-03: Kiểm tra Dashboard

**Thao tác**

1. Mở URL trang Dashboard đã publish.
2. Tìm khách hàng vừa tạo.
3. Đối chiếu ghi chú, tóm tắt và phân loại với bản ghi trong Admin.

**Kết quả mong đợi**

- Khách hàng xuất hiện đúng một lần.
- Các ghi chú được gắn đúng khách hàng.
- Tóm tắt và nhãn phân loại hiển thị đúng dữ liệu mới nhất.
- Refresh trang không làm mất dữ liệu hoặc tạo thêm ghi chú.

## 4. Dữ liệu hội thoại/ghi chú mẫu

| Mã | Loại | Nội dung test | Phân loại mong đợi |
|---|---|---|---|
| AI-01 | Tích cực | Khách hàng đã xem báo giá, xác nhận ngân sách và muốn đặt lịch demo vào thứ Sáu. Đề nghị gửi hợp đồng mẫu trước buổi demo. | Tiềm năng |
| AI-02 | Đang hỏi đáp | Khách hàng hỏi giá gói doanh nghiệp, thời gian triển khai, cách tích hợp CRM và có hỗ trợ nhập dữ liệu cũ hay không. Chưa xác nhận ngân sách. | Đang cân nhắc |
| AI-03 | Tiêu cực | Khách hàng cho biết hiện chưa có nhu cầu, đã ký với nhà cung cấp khác và đề nghị không gọi lại trong quý này. | Không quan tâm |
| AI-04 | Tích cực nhưng ngắn | Đồng ý nhận bản dùng thử và muốn trao đổi thêm với trưởng phòng kinh doanh vào tuần sau. | Tiềm năng |
| AI-05 | Không rõ | Đã gọi điện, khách hàng nghe máy nhưng nói đang bận. Nhân viên sẽ liên hệ lại sau. | Đang cân nhắc hoặc Không xác định |
| AI-06 | Có HTML | `<p>Khách hàng quan tâm <strong>gói Premium</strong>, yêu cầu gửi bảng giá.</p>` | Tiềm năng |
| AI-07 | Ký tự đặc biệt | Khách hàng Nguyễn An hỏi: “Có hỗ trợ SSO, API và dữ liệu tiếng Việt không?” | Đang cân nhắc |
| AI-08 | Dài | Ghi lại toàn bộ lịch sử trao đổi, các yêu cầu kỹ thuật, người phê duyệt, ngân sách dự kiến, mốc triển khai và rủi ro. Kiểm tra tóm tắt có giữ lại quyết định và bước tiếp theo quan trọng hay không. | Phù hợp nội dung, tối đa 1-2 câu |

Phân loại của AI có thể thay đổi theo ngữ cảnh. QA nên đánh giá theo ý nghĩa nội dung, không chỉ so sánh chuỗi tuyệt đối.

## 5. Kiểm thử lỗi và biên

| Mã | Tình huống | Kết quả mong đợi |
|---|---|---|
| ER-01 | Không có `GEMINI_API_KEY` | Không làm server crash; Note lưu với `Thiếu API Key` và `Không xác định`. |
| ER-02 | API key sai hoặc Gemini timeout | Note vẫn lưu; kết quả là `Lỗi khi phân tích AI` và `Lỗi`; lỗi được ghi log để dev điều tra. |
| ER-03 | Email trùng | Form từ chối bản ghi, không tạo Customer thứ hai. |
| ER-04 | Bỏ trống nội dung Note | Form yêu cầu nội dung hoặc không gọi AI; không tạo bản ghi rác. |
| ER-05 | Nhiều Note cho một Customer | Dashboard nhóm đúng tất cả Note dưới cùng Customer. |
| ER-06 | Người dùng chưa đăng nhập mở `/admin/` | Được chuyển đến trang đăng nhập, không xem được dữ liệu quản trị. |
| ER-07 | Xóa Customer có Note | Theo `on_delete=CASCADE`, Note liên quan bị xóa; cần xác nhận đây là chính sách nghiệp vụ mong muốn. |
| ER-08 | AI trả sai format | Ứng dụng không crash; cần hiển thị trạng thái `Không xác định` và báo log. |

## 6. Checklist smoke test

- [ ] `python manage.py check` không có lỗi.
- [ ] `python manage.py migrate` chạy thành công.
- [ ] Tạo được superuser và đăng nhập `/admin/`.
- [ ] Tạo được Customer hợp lệ.
- [ ] Không tạo được Customer với email trùng.
- [ ] Tạo Note thành công khi có API key.
- [ ] AI summary và category được lưu.
- [ ] Dashboard hiển thị Customer và Note.
- [ ] Chạy lại trang không tạo bản ghi mới.
- [ ] Luồng không có API key vẫn lưu Note và báo trạng thái phù hợp.
- [ ] `python manage.py test` hoàn tất thành công.

## 7. Bug/blocker phát hiện khi viết test

### BUG-001 - Test và model dùng hai tên Page khác nhau

- **Mức độ:** Blocker
- **Hiện trạng:** `home/tests.py` import `HomePage`, nhưng `home/models.py` chỉ khai báo `CRMDashboardPage`. Migration `0003` cũng chuyển từ `HomePage` sang `CRMDashboardPage`.
- **Ảnh hưởng:** Test hiện có không thể import model đúng; luồng tạo/render homepage có thể không chạy được.
- **Đề xuất:** Dev chọn một tên model chính, sau đó đồng bộ `models.py`, migration, `tests.py`, template và dữ liệu Wagtail.

### BUG-002 - Bộ dependency không cài được trên Python 3.14

- **Mức độ:** High
- **Hiện trạng:** `google-api-core==2.33.0` yêu cầu `grpcio-status>=1.75.1` trên Python 3.14, trong khi requirements pin `grpcio-status==1.71.2`.
- **Ảnh hưởng:** Không dựng được môi trường bằng `pip install -r requirements.txt` trên Python 3.14.
- **Workaround:** Dùng Python 3.13 theo README hoặc dev đồng bộ lại các pin package và Dockerfile.

## 8. Báo cáo lỗi

Mỗi bug nên có:

- Mã test và môi trường (`Windows`, phiên bản Python, trình duyệt).
- Bước tái hiện.
- Kết quả thực tế và kết quả mong đợi.
- Ảnh chụp hoặc log đã che API key và dữ liệu nhạy cảm.
- Mức độ ảnh hưởng và tần suất tái hiện.
