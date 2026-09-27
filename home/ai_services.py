import os
import google.generativeai as genai
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy API key từ biến môi trường
API_KEY = os.getenv("GEMINI_API_KEY")

# Cấu hình API key cho thư viện genai
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found in .env file")

# Khởi tạo model Gemini
model = genai.GenerativeModel('gemini-flash-latest')

def analyze_note_content(text: str) -> dict:
    """
    Hàm này nhận vào nội dung ghi chú (text), gọi Gemini AI để tóm tắt 
    và phân loại khách hàng (Tiềm năng, Bình thường, Hủy chốt...).
    Trả về định dạng dict.
    """
    if not API_KEY:
        return {"summary": "Thiếu API Key", "category": "Không xác định"}

    prompt = f"""
Bạn là một trợ lý AI phân tích dữ liệu CRM chuyên nghiệp.
Dưới đây là một ghi chú của nhân viên sale về khách hàng. 
Nhiệm vụ của bạn là:
1. Tóm tắt nội dung ghi chú (ngắn gọn trong 1-2 câu).
2. Phân loại khách hàng vào 1 trong 3 nhóm sau: "Tiềm năng", "Đang cân nhắc", "Không quan tâm".

Định dạng trả về duy nhất (KHÔNG giải thích thêm, KHÔNG dùng markdown):
Tóm tắt: <Nội dung tóm tắt>
Phân loại: <Nhóm>

Nội dung ghi chú:
"{text}"
    """

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Bóc tách dữ liệu từ text trả về
        summary = ""
        category = "Không xác định"
        
        for line in result_text.split('\n'):
            if line.startswith("Tóm tắt:"):
                summary = line.replace("Tóm tắt:", "").strip()
            elif line.startswith("Phân loại:"):
                category = line.replace("Phân loại:", "").strip()
                
        return {
            "summary": summary,
            "category": category
        }
    except Exception as e:
        print(f"Error when calling AI: {e}")
        return {
            "summary": "Lỗi khi phân tích AI",
            "category": "Lỗi"
        }
