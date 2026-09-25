import streamlit as st
from google import genai
from PIL import Image
from dotenv import load_dotenv
import os
import re

load_dotenv()

st.set_page_config(
    page_title="AI chấm đoạn văn nghị luận",
    page_icon="📚",
    layout="centered"
)

# =========================
# KẾT NỐI GEMINI
# =========================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

st.title("📚 AI chấm đoạn văn nghị luận")
st.caption("Nghị luận xã hội • Nghị luận văn học")

if not api_key:
    st.error("Chưa tìm thấy GEMINI_API_KEY.")
    st.info("Hãy thiết lập API key trước khi sử dụng.")
    st.stop()

client = genai.Client(api_key=api_key)


# =========================
# GIAO DIỆN
# =========================

loai_bai = st.selectbox(
    "1. Chọn loại đoạn văn",
    [
        "Nghị luận xã hội",
        "Nghị luận văn học"
    ]
)

de_bai = st.text_input(
    "2. Tên đề bài",
    placeholder="Nhập hoặc dán đề bài tại đây..."
)

st.write("3. Nhập bài làm")

phuong_thuc = st.radio(
    "Chọn cách nộp bài:",
    [
        "Sao chép và dán đoạn văn",
        "Tải ảnh đoạn văn"
    ],
    horizontal=True
)

bai_viet = ""
def dem_so_chu(text):
    return len(re.findall(r"\S+", text))
anh_bai = None

if phuong_thuc == "Sao chép và dán đoạn văn":
    bai_viet = st.text_area(
        "Dán đoạn văn của bạn vào đây",
        height=300,
        placeholder="Dán đoạn văn khoảng 200 chữ vào đây..."
    )
else:
    anh_bai = st.file_uploader(
        "Tải ảnh đoạn văn",
        type=["png", "jpg", "jpeg"]
    )

st.divider()

if st.button("🔎 CHẤM BÀI", use_container_width=True):

    if not de_bai.strip():
        st.warning("Bạn chưa nhập tên đề bài.")
        st.stop()

    if phuong_thuc == "Sao chép và dán đoạn văn":
        if not bai_viet.strip():
            st.warning("Bạn chưa nhập đoạn văn.")
            st.stop()
    so_chu = dem_so_chu(bai_viet)
    st.info(f"📏 Bài làm của bạn có khoảng **{so_chu} chữ**.")
    
    if so_chu < 130:
        st.warning("⚠️ Đoạn văn đang khá ngắn so với yêu cầu khoảng 200 chữ.")
    elif so_chu > 300:
        st.warning("⚠️ Đoạn văn đang khá dài so với yêu cầu khoảng 200 chữ.")

    if phuong_thuc == "Tải ảnh đoạn văn":
        if anh_bai is None:
            st.warning("Bạn chưa tải ảnh đoạn văn.")
            st.stop()

    # =========================
    # PROMPT
    # =========================

    if loai_bai == "Nghị luận xã hội":

        tieu_chi = """
        ĐOẠN VĂN NGHỊ LUẬN XÃ HỘI - THANG 2,00 ĐIỂM

        1. Hình thức và dung lượng: 0,25 điểm
        - Đảm bảo đúng cấu trúc một đoạn văn.
        - Không xuống dòng tùy tiện.
        - Chữ cái đầu đoạn viết hoa.
        - Có lùi đầu dòng khi viết trên giấy.
        - Dung lượng khoảng 200 chữ.

        2. Xác định vấn đề nghị luận: 0,25 điểm
        - Nêu rõ và chính xác vấn đề cần bàn luận.
        - Vấn đề có thể là hiện tượng xã hội hoặc tư tưởng, đạo lý.

        3. Triển khai vấn đề nghị luận: 1,00 điểm
        - Giải thích khái niệm hoặc từ ngữ cốt lõi nếu cần.
        - Bàn luận bằng lý lẽ rõ ràng.
        - Trả lời được vì sao, như thế nào.
        - Có dẫn chứng thực tế, tiêu biểu, xác thực.
        - Có quan điểm cá nhân rõ ràng.
        - Có mở rộng/phản biện hoặc bài học nhận thức và hành động.
        - Lập luận chặt chẽ, không sáo rỗng.

        4. Chính tả, ngữ pháp và sáng tạo: 0,50 điểm
        - Chính tả.
        - Ngữ pháp.
        - Dùng từ.
        - Đặt câu.
        - Diễn đạt mạch lạc.
        - Có góc nhìn mới mẻ, cảm xúc hoặc cách diễn đạt sáng tạo.
        """

    else:

        tieu_chi = """
        ĐOẠN VĂN NGHỊ LUẬN VĂN HỌC - THANG 2,00 ĐIỂM

        1. Hình thức và dung lượng: 0,25 điểm
        - Đảm bảo đúng cấu trúc một đoạn văn.
        - Không xuống dòng tùy tiện.
        - Viết hoa chữ cái đầu.
        - Có lùi đầu dòng khi viết trên giấy.
        - Dung lượng khoảng 200 chữ.

        2. Xác định vấn đề nghị luận: 0,25 điểm
        - Xác định đúng nét đặc sắc về nội dung hoặc nghệ thuật cần phân tích.
        - Có thể liên quan đến văn bản trong sách giáo khoa hoặc ngữ liệu ngoài sách giáo khoa.

        3. Triển khai vấn đề nghị luận: 1,00 điểm
        - Phân tích từ ngữ, hình ảnh, chi tiết, biện pháp tu từ hoặc đặc trưng thể loại.
        - Có trích dẫn ngữ liệu phù hợp.
        - Kết hợp phân tích với nhận xét, đánh giá.
        - Làm rõ giá trị nội dung và nghệ thuật.
        - Thể hiện hiểu biết về tư tưởng, tình cảm và giá trị nhân văn của tác giả.
        - Lập luận chặt chẽ.

        4. Chính tả, ngữ pháp và sáng tạo: 0,50 điểm
        - Chính tả.
        - Ngữ pháp.
        - Dùng từ.
        - Đặt câu.
        - Có phát hiện mới mẻ, sâu sắc.
        - Văn phong có cảm xúc, hình ảnh hoặc liên tưởng hợp lý.
        """


    prompt = f"""
Bạn là AI hỗ trợ chấm đoạn văn Ngữ văn THPT.

QUY TẮC XƯNG HÔ BẮT BUỘC:
- AI phải xưng là "mình".
- Gọi người làm bài là "bạn".
- TUYỆT ĐỐI KHÔNG gọi người làm bài là "thầy", "cô" hoặc "giáo viên".

Loại bài:
{loai_bai}

Đề bài:
{de_bai}

{tieu_chi}

YÊU CẦU CHẤM:

1. Hãy đếm số chữ của bài làm.
2. Báo chính xác số chữ mà bạn nhận được.
3. Mốc tham khảo là khoảng 200 chữ.
4. Nếu bài quá ngắn hoặc quá dài so với khoảng 200 chữ, phải cảnh báo rõ.
5. Không được tự ý tính điểm chỉ vì bài dài.
6. Chấm từng tiêu chí riêng.
7. Tổng điểm tối đa là 2,00 điểm.
8. Không được cho điểm vượt quá điểm tối đa của từng tiêu chí.
9. Phải giải thích vì sao bài được số điểm đó.
10. Phải chỉ ra những lỗi cụ thể.
11. Với mỗi lỗi quan trọng, phải đưa ra cách sửa.
12. Nếu bài làm tốt, vẫn phải chỉ ra điểm có thể cải thiện.
13. Không được bịa dẫn chứng, nội dung tác phẩm hoặc chi tiết không có trong bài.
14. Nếu không đủ thông tin để xác định một chi tiết, hãy nói rõ.
15. Nhận xét phải dễ hiểu, không quá chung chung.

Hãy trả kết quả theo đúng cấu trúc sau:

# KẾT QUẢ CHẤM

## 1. Số chữ
- Số chữ: ... chữ
- Mức độ phù hợp với yêu cầu khoảng 200 chữ: ...
- Cảnh báo dung lượng: ...

## 2. Bảng điểm

| Tiêu chí | Điểm tối đa | Điểm đạt | Nhận xét |
|---|---:|---:|---|
| Hình thức và dung lượng | 0,25 | ... | ... |
| Xác định vấn đề nghị luận | 0,25 | ... | ... |
| Triển khai vấn đề nghị luận | 1,00 | ... | ... |
| Chính tả, ngữ pháp và sáng tạo | 0,50 | ... | ... |
| **TỔNG** | **2,00** | **...** | |

## 3. Nhận xét chi tiết

### Điểm mạnh
- ...

### Những điểm cần cải thiện
- ...

## 4. Lỗi cụ thể và cách sửa

| Lỗi trong bài | Vấn đề | Gợi ý sửa |
|---|---|---|
| ... | ... | ... |

Nếu không phát hiện lỗi cụ thể ở một mục, ghi rõ "Chưa phát hiện lỗi đáng kể".

## 5. Gợi ý cải thiện đoạn văn
Đưa ra các gợi ý cụ thể để bạn có thể nâng chất lượng bài viết.

## 6. Nhận xét cuối
Viết một đoạn ngắn, thân thiện, trực tiếp nói với "bạn".
Không gọi "thầy/cô".
"""


    # =========================
    # GỌI GEMINI
    # =========================

    with st.spinner("Mình đang đọc và chấm bài..."):

        try:

            if phuong_thuc == "Sao chép và dán đoạn văn":

                response = client.models.generate_content(
                  model="gemini-3.5-flash-lite",
                    contents=[
                        prompt,
                        f"""
                        BÀI LÀM CỦA BẠN:

                        {bai_viet}
                        """
                    ]
                )

            else:

                image = Image.open(anh_bai)

                response = client.models.generate_content(
               model="gemini-3.5-flash-lite",
                    contents=[
                        prompt,
                        """
                        Đây là ảnh bài làm của bạn.
                        Hãy đọc chính xác nội dung trong ảnh.

                        Nếu chữ trong ảnh không rõ, KHÔNG được tự bịa nội dung.
                        Hãy nói rõ phần nào không thể đọc chính xác.

                        Sau khi đọc được bài, hãy đếm số chữ và chấm theo tiêu chí.
                        """,
                        image
                    ]
                )

            st.success("Đã chấm xong!")

            st.markdown(response.text)

        except Exception as e:

            st.error("Có lỗi khi chấm bài.")
            st.code(str(e))


  
