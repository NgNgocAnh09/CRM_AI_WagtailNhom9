import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy API key từ biến môi trường
API_KEY = os.getenv("GEMINI_API_KEY")

# Cấu hình API key sử dụng transport='rest' để tránh treo gRPC channel trên Windows
if API_KEY:
    try:
        genai.configure(api_key=API_KEY, transport='rest')
    except Exception:
        pass
else:
    print("WARNING: GEMINI_API_KEY not found in .env file")


def heuristic_fallback_analysis(text: str) -> dict:
    """
    Phân tích thông minh dựa trên từ khóa trong trường hợp API AI gặp sự cố,
    hết hạn ngạch (Rate Limit 429) hoặc bị quá thời gian phản hồi (Timeout).
    Đảm bảo thời gian phản hồi siêu tốc (< 0.01 giây).
    """
    text_lower = text.lower()

    if any(k in text_lower for k in ["chốt", "muốn mua", "báo giá", "ký hợp đồng", "chuyển khoản", "tiềm năng", "cần gấp", "demo", "tư vấn"]):
        category = "Tiềm năng"
        summary = "Khách hàng thể hiện sự quan tâm lớn và nhu cầu chốt dịch vụ/sản phẩm."
        next_action = "Gửi báo giá chính thức, đặt lịch họp demo và chốt hợp đồng trong 24 giờ."
    elif any(k in text_lower for k in ["lỗi", "hỏng", "không được", "khiếu nại", "tệ", "chậm", "phản đối", "sự cố"]):
        category = "Khiếu nại / Hỗ trợ"
        summary = "Khách hàng phản ánh sự cố hoặc chưa hài lòng về sản phẩm/dịch vụ."
        next_action = "Chuyển thông tin cho bộ phận Kỹ thuật/CSKH xử lý ưu tiên và phản hồi khách hàng ngay."
    elif any(k in text_lower for k in ["không nhu cầu", "từ chối", "đắt quá", "hủy", "không nghe máy", "không mua"]):
        category = "Không quan tâm"
        summary = "Khách hàng hiện chưa có nhu cầu hoặc từ chối hợp tác."
        next_action = "Lưu hồ sơ khách hàng, phân loại theo dõi và cập nhật lại sau 3 tháng."
    else:
        category = "Đang cân nhắc"
        summary = "Khách hàng cần tìm hiểu thêm thông tin trước khi đưa ra quyết định."
        next_action = "Gửi tài liệu tham khảo chi tiết và lên lịch gọi lại tư vấn sau 3 ngày."

    if len(text.strip()) > 0:
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        if len(clean_text) > 10:
            summary = clean_text[:130] + ("..." if len(clean_text) > 130 else "")

    return {
        "summary": summary,
        "category": category,
        "next_action": next_action
    }


def analyze_note_content(text: str) -> dict:
    """
    Nhận vào nội dung ghi chú (text), gọi Google Gemini AI để:
    1. Tóm tắt nội dung ghi chú (1-2 câu).
    2. Phân loại khách hàng: "Tiềm năng", "Đang cân nhắc", "Khiếu nại / Hỗ trợ", "Không quan tâm".
    3. Đề xuất hành động tiếp theo (Next Action) cho nhân viên kinh doanh/CSKH.

    Sử dụng Timeout 2.0 giây và lập tức kích hoạt Heuristic Fallback nếu gặp lỗi/Rate Limit 429
    để không bao giờ làm xoay trang (hang/load mãi) trên giao diện Web.
    """
    if not text or not text.strip():
        return {
            "summary": "Không có nội dung ghi chú.",
            "category": "Chưa xác định",
            "next_action": "Cập nhật bổ sung ghi chú thông tin trao đổi."
        }

    if not API_KEY:
        fallback = heuristic_fallback_analysis(text)
        fallback["summary"] = f"[Offline Mode] {fallback['summary']}"
        return fallback

    prompt = f"""
Bạn là một trợ lý AI phân tích dữ liệu CRM chuyên nghiệp cho doanh nghiệp.
Dưới đây là một ghi chú của nhân viên kinh doanh/CSKH về tương tác với khách hàng:

"{text}"

Nhiệm vụ của bạn:
1. Tóm tắt nội dung chính của ghi chú (ngắn gọn 1-2 câu).
2. Phân loại ghi chú vào ĐÚNG 1 trong 4 nhóm sau:
   - "Tiềm năng"
   - "Đang cân nhắc"
   - "Khiếu nại / Hỗ trợ"
   - "Không quan tâm"
3. Gợi ý 1 hành động tiếp theo cụ thể, khả thi cho nhân viên kinh doanh/CSKH (Next Action).

Trả về ĐÚNG định dạng sau (KHÔNG giải thích thêm, KHÔNG dùng markdown bold/italic):
Tóm tắt: <Nội dung tóm tắt>
Phân loại: <Tên 1 nhóm duy nhất>
Đề xuất hành động: <Hành động tiếp theo>
"""

    # Chỉ thử 1 model duy nhất với timeout cực ngắn 2.0s để không làm chậm request HTTP của Web
    try:
        model = genai.GenerativeModel('gemini-3.8-flash')
        response = model.generate_content(
            prompt,
            request_options={"timeout": 2.0}
        )
        result_text = response.text.strip() if response and response.text else ""

        if result_text:
            summary = ""
            category = ""
            next_action = ""

            for line in result_text.split('\n'):
                line_str = line.strip()
                if line_str.startswith("Tóm tắt:"):
                    summary = line_str.replace("Tóm tắt:", "").strip()
                elif line_str.startswith("Phân loại:"):
                    category = line_str.replace("Phân loại:", "").strip()
                elif line_str.startswith("Đề xuất hành động:"):
                    next_action = line_str.replace("Đề xuất hành động:", "").strip()

            valid_categories = ["Tiềm năng", "Đang cân nhắc", "Khiếu nại / Hỗ trợ", "Không quan tâm"]
            matched_cat = None
            for vc in valid_categories:
                if vc.lower() in category.lower():
                    matched_cat = vc
                    break

            if not matched_cat:
                matched_cat = category if category else "Đang cân nhắc"

            if not summary:
                summary = result_text[:150]

            if not next_action:
                next_action = "Liên hệ lại với khách hàng để theo dõi tiến độ."

            return {
                "summary": summary,
                "category": matched_cat,
                "next_action": next_action
            }
    except Exception:
        # Lập tức ngắt và chuyển sang Heuristic Fallback khi gặp bất kỳ lỗi API/Rate Limit 429/Timeout nào
        pass

    return heuristic_fallback_analysis(text)
