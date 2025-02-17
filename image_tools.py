import streamlit as st
from rembg import remove, new_session
from PIL import Image, ImageEnhance
import io
import base64
from streamlit_image_comparison import image_comparison
from streamlit_option_menu import option_menu
import requests
from streamlit_lottie import st_lottie
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai
# from dotenv import load_dotenv
import os


# load_dotenv()
# Cấu hình trang
st.set_page_config(page_title="AI Background Remover", page_icon="🎭", layout="wide")

# Khởi tạo Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Hàm tiện ích
def load_lottieurl(url: str):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

def get_image_download_link(img, filename, text):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}" class="download-btn">{text}</a>'
    return href

@st.cache_data
def remove_background(image):
    return remove(image, session=new_session())

def get_ai_response(user_message):
    prompt = f"""
    Bạn là trợ lý AI chuyên nghiệp của dịch vụ "AI Background Remover", công cụ hàng đầu trong lĩnh vực xóa phông nền ảnh bằng trí tuệ nhân tạo. Nhiệm vụ của bạn là cung cấp thông tin, hỗ trợ và giải đáp thắc mắc cho người dùng một cách chuyên nghiệp, đồng thời quảng bá giá trị của dịch vụ.

    Khi tạo nội dung chăm sóc khách hàng, hãy tuân thủ các nguyên tắc sau:

    1. 🎯 Tập trung vào vấn đề cốt lõi: Xác định và giải quyết trực tiếp các thắc mắc phổ biến
    2. 💡 Cung cấp giải pháp toàn diện: Đưa ra hướng dẫn chi tiết, dễ hiểu và áp dụng được
    3. 🔍 Dự đoán nhu cầu: Cung cấp thông tin phụ trợ có thể hữu ích cho người dùng
    4. 🛠️ Chia sẻ mẹo và thủ thuật: Giới thiệu các cách sử dụng hiệu quả và sáng tạo
    5. 📊 Sử dụng dữ liệu và ví dụ: Minh họa lợi ích bằng số liệu thống kê hoặc trường hợp cụ thể
    6. 🔄 Cập nhật thông tin: Đề cập đến tính năng mới hoặc cải tiến gần đây
    7. 🤝 Khuyến khích tương tác: Mời gọi phản hồi và chia sẻ trải nghiệm từ cộng đồng người dùng
    8. 🌟 Nhấn mạnh giá trị độc đáo: Làm nổi bật điểm mạnh của AI Background Remover
    9. 🔒 Đảm bảo an toàn: Nhấn mạnh cam kết về bảo mật và quyền riêng tư của người dùng
    10. 📚 Cung cấp tài nguyên: Giới thiệu hướng dẫn sử dụng, FAQ, hoặc video tutorial liên quan

    Lưu ý quan trọng:
    - Sử dụng ngôn ngữ chuyên nghiệp, dễ hiểu và thân thiện
    - Tránh sử dụng từ ngữ quá kỹ thuật, giải thích các thuật ngữ phức tạp nếu cần
    - Cấu trúc nội dung rõ ràng, sử dụng đoạn ngắn và gạch đầu dòng để dễ đọc
    - Tạo sự cân bằng giữa thông tin hữu ích và quảng bá dịch vụ một cách tinh tế
    - Thể hiện sự thấu hiểu về nhu cầu đa dạng của người dùng
    - Sử dụng giọng điệu tích cực, khuyến khích và hỗ trợ
    - Cung cấp thông tin về hỗ trợ bổ sung nếu cần (ví dụ: kênh hỗ trợ trực tiếp)

    Chủ đề cần phản hồi: {user_message}

    Hãy tạo một bài viết hỗ trợ khách hàng toàn diện với cấu trúc sau:
    1. Giới thiệu ngắn gọn về chủ đề
    2. Giải thích chi tiết vấn đề và giải pháp
    3. Mẹo và thủ thuật hữu ích
    4. Câu hỏi thường gặp liên quan
    5. Tài nguyên bổ sung và hướng dẫn nâng cao, đây là trang chủ của dự án và không có trang phụ nào khác https://
    6. Lời kết và khuyến khích sử dụng dịch vụ

    Hãy đảm bảo nội dung được trình bày một cách chuyên nghiệp, dễ hiểu và hấp dẫn, phù hợp để đăng trên trang hỗ trợ hoặc blog của dịch vụ.
    """
    response = model.generate_content(prompt)
    return response.text

# Khởi tạo session state
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None
if 'input_image' not in st.session_state:
    st.session_state.input_image = None

# CSS tùy chỉnh
st.markdown("""
<style>
    :root {
        --primary-color: #3498db;
        --secondary-color: #2c3e50;
        --accent-color: #e74c3c;
        --background-color: #ecf0f1;
        --text-color: #34495e;
        --success-color: #2ecc71;
        --warning-color: #f39c12;
        --error-color: #e74c3c;
    }
    body {
        color: var(--text-color);
        background-color: var(--background-color);
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header {
        font-size: 2.8rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        animation: fadeInDown 1s ease-in-out;
    }
    .sub-header {
        font-size: 1.8rem;
        color: var(--secondary-color);
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--accent-color);
        padding-bottom: 0.5rem;
        animation: fadeInLeft 0.5s ease-in-out;
    }
    .info-box {
        background-color: var(--background-color);
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--accent-color);
        transition: all 0.3s ease;
    }
    .info-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        width: 100%;
        background-color: var(--primary-color);
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        margin-top: 1rem;
    }
    .stButton>button:hover {
        background-color: var(--accent-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .download-btn {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: var(--success-color);
        color: white;
        text-align: center;
        text-decoration: none;
        font-size: 16px;
        border-radius: 5px;
        transition: all 0.3s ease;
        margin-top: 1rem;
    }
    .download-btn:hover {
        background-color: #27ae60;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stAlert {
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.5s ease-in-out;
    }
    .stAlert.success {
        background-color: var(--success-color);
        color: white;
    }
    .stAlert.warning {
        background-color: var(--warning-color);
        color: white;
    }
    .stAlert.error {
        background-color: var(--error-color);
        color: white;
    }
    .stSelectbox {
        margin-bottom: 1rem;
    }
    .stSelectbox > div > div {
        background-color: var(--background-color);
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stSelectbox > div > div:hover {
        background-color: #d6dbdf;
    }
    .image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1rem;
        perspective: 1000px;
    }
    .image-container img {
        max-width: 100%;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .image-container img:hover {
        transform: rotateY(10deg);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    }
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .sidebar .stSelectbox {
        background-color: var(--background-color);
        border-radius: 5px;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    .sidebar .stSelectbox > div > div {
        background-color: white;
    }
    .sidebar .stSelectbox label {
        color: var(--secondary-color);
        font-weight: bold;
    }
    .sidebar .info-box {
        background-color: var(--primary-color);
        color: white;
        border-left: 4px solid var(--accent-color);
    }
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 120px;
        background-color: var(--secondary-color);
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px 0;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    .email-form {
        background-color: var(--background-color);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .email-form textarea {
        width: 100%;
        border-radius: 5px;
        border: 1px solid var(--primary-color);
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    .email-form button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .email-form button:hover {
        background-color: var(--accent-color);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Nội dung chính
st.markdown('<h1 class="main-header">🎭 AI Background Remover</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<h2 class="sub-header">Options</h2>', unsafe_allow_html=True)
    
    model_type = st.selectbox(
        "Select AI Model",
        ["u2net", "u2netp", "u2net_human_seg", "u2net_cloth_seg"],
        help="Choose the AI model for background removal"
    )
    
    st.markdown('<div class="info-box">💡 Tip: Close the app when not in use to free up memory</div>', unsafe_allow_html=True)
    
    st.markdown("### About")
    st.markdown("""
    This app uses state-of-the-art AI to remove backgrounds from images with precision and ease.
    - Upload an image from your device or via URL
    - Process it to remove the background seamlessly
    - Edit and enhance the result as needed
    - Download your masterpiece!
    """)
    
    st.markdown("### Support")
    if 'show_email_form' not in st.session_state:
        st.session_state.show_email_form = False
    
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""

    st.session_state.user_email = st.text_input("Your Email Address", value=st.session_state.user_email)

    if st.button("📧 Contact Support"):
        st.session_state.show_email_form = not st.session_state.show_email_form

    if st.session_state.show_email_form:
        st.markdown('<div class="email-form">', unsafe_allow_html=True)
        user_message = st.text_area("Câu hỏi của bạn?", height=150)
        if st.button("Send Email"):
            if st.session_state.user_email and user_message:
                try:
                    ai_response = get_ai_response(user_message)
                    sender_email = os.getenv('SENDER_EMAIL')
                    password = os.getenv('SENDER_PASSWORD')
                    receiver_email = st.session_state.user_email
                   

                    message = MIMEMultipart()
                    message["From"] = sender_email
                    message["To"] = receiver_email
                    message["Subject"] = "Response to Your Inquiry - AI Background Remover"
                    message.attach(MIMEText(ai_response, "plain"))

                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(sender_email, password)
                        server.sendmail(sender_email, receiver_email, message.as_string())

                    st.success("Your message has been processed and a response has been sent to your email. Please check your inbox.")
                    st.session_state.show_email_form = False
                except Exception as e:
                    st.error(f"An error occurred while processing your request: {str(e)}")
            else:
                st.warning("Please fill in both your email address and message.")
        st.markdown('</div>', unsafe_allow_html=True)

# Menu chính
selected = option_menu(
    menu_title=None,
    options=["Upload", "Process", "Edit"],
    icons=["cloud-upload", "gear", "pencil-square"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#ecf0f1"},
        "icon": {"color": "#3498db", "font-size": "25px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#d6dbdf"},
        "nav-link-selected": {"background-color": "#3498db"},
    }
)

# Tải animation Lottie
lottie_upload = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_urbk83vw.json")
lottie_process = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_4kx2q32n.json")
lottie_edit = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_khrclx93.json")

if selected == "Upload":
    st.markdown('<h2 class="sub-header">Upload Image</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st_lottie(lottie_upload, height=200, key="upload_animation")
    
    with col2:
        upload_method = st.radio("Choose upload method:", ("File Upload", "Image URL"))
        
        if upload_method == "File Upload":
            uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                try:
                    st.session_state.input_image = Image.open(uploaded_file)
                    st.image(st.session_state.input_image, caption="Uploaded Image", use_container_width=True)
                    st.success("Image uploaded successfully! 🎉")
                except Exception as e:
                    st.error(f"Error uploading image: {str(e)} 😕")
        else:
            image_url = st.text_input("Enter the URL of the image:")
            if image_url:
                try:
                    response = requests.get(image_url)
                    st.session_state.input_image = Image.open(io.BytesIO(response.content))
                    st.image(st.session_state.input_image, caption="Image from URL", use_container_width=True)
                    st.success("Image loaded successfully from URL! 🌐")
                except Exception as e:
                    st.error(f"Error loading image from URL: {str(e)} 😕")

elif selected == "Process":
    st.markdown('<h2 class="sub-header">Process Image</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st_lottie(lottie_process, height=200, key="process_animation")
    
    with col2:
        if st.session_state.input_image is not None:
            if st.button("Remove Background", key="remove_bg"):
                try:
                    with st.spinner('AI is working its magic... ✨'):
                        st.session_state.processed_image = remove_background(st.session_state.input_image)
                    st.success("Background removed successfully! 🎉")
                except Exception as e:
                    st.error(f"Error processing image: {str(e)} 😕")
            
            if st.session_state.processed_image is not None:
                col1, col2 = st.columns(2)
                with col1:
                    st.image(st.session_state.input_image, caption="Original Image", use_container_width=True)
                with col2:
                    st.image(st.session_state.processed_image, caption="Processed Image", use_container_width=True)
                
                st.markdown(get_image_download_link(st.session_state.processed_image, "background_removed.png", "📥 Download Processed Image"), unsafe_allow_html=True)
                
                st.markdown('<h3 class="sub-header">Image Comparison</h3>', unsafe_allow_html=True)
                image_comparison(
                    img1=st.session_state.input_image,
                    img2=st.session_state.processed_image,
                    label1="Original",
                    label2="Processed",
                )
        else:
            st.warning("Please upload an image first in the 'Upload' tab. 🖼️")

elif selected == "Edit":
    st.markdown('<h2 class="sub-header">Edit Processed Image</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st_lottie(lottie_edit, height=200, key="edit_animation")
    
    with col2:
        if st.session_state.processed_image is not None:
            edit_option = st.selectbox("Choose edit option:", ["Grayscale", "Resize", "Rotate", "Adjust Brightness"])
            
            if edit_option == "Grayscale":
                if st.button("Apply Grayscale"):
                    try:
                        gray_image = st.session_state.processed_image.convert('L')
                        st.image(gray_image, caption="Grayscale Image", use_container_width=True)
                        st.markdown(get_image_download_link(gray_image, "grayscale.png", "📥 Download Grayscale Image"), unsafe_allow_html=True)
                        st.success("Grayscale effect applied successfully! 🎨")
                    except Exception as e:
                        st.error(f"Error applying grayscale effect: {str(e)} 😕")
            
            elif edit_option == "Resize":
                resize_factor = st.slider("Resize factor", min_value=0.1, max_value=2.0, value=1.0, step=0.1)
                if st.button("Apply Resize"):
                    try:
                        width, height = st.session_state.processed_image.size
                        resized_image = st.session_state.processed_image.resize((int(width * resize_factor), int(height * resize_factor)))
                        st.image(resized_image, caption=f"Resized Image ({resize_factor}x)", use_container_width=True)
                        st.markdown(get_image_download_link(resized_image, "resized.png", "📥 Download Resized Image"), unsafe_allow_html=True)
                        st.success("Image resized successfully! 🔍")
                    except Exception as e:
                        st.error(f"Error resizing image: {str(e)} 😕")
            
            elif edit_option == "Rotate":
                rotation_angle = st.slider("Rotation angle", min_value=0, max_value=360, value=0, step=90)
                if st.button("Apply Rotation"):
                    try:
                        rotated_image = st.session_state.processed_image.rotate(rotation_angle)
                        st.image(rotated_image, caption=f"Rotated Image ({rotation_angle}°)", use_container_width=True)
                        st.markdown(get_image_download_link(rotated_image, "rotated.png", "📥 Download Rotated Image"), unsafe_allow_html=True)
                        st.success("Image rotated successfully! 🔄")
                    except Exception as e:
                        st.error(f"Error rotating image: {str(e)} 😕")
            
            elif edit_option == "Adjust Brightness":
                brightness_factor = st.slider("Brightness factor", min_value=0.1, max_value=2.0, value=1.0, step=0.1)
                if st.button("Apply Brightness Adjustment"):
                    try:
                        enhancer = ImageEnhance.Brightness(st.session_state.processed_image)
                        brightened_image = enhancer.enhance(brightness_factor)
                        st.image(brightened_image, caption=f"Adjusted Brightness Image ({brightness_factor}x)", use_container_width=True)
                        st.markdown(get_image_download_link(brightened_image, "brightened.png", "📥 Download Brightened Image"), unsafe_allow_html=True)
                        st.success("Brightness adjusted successfully! ☀️")
                    except Exception as e:
                        st.error(f"Error adjusting brightness: {str(e)} 😕")
        else:
            st.warning("Please process an image first in the 'Process' tab. 🖼️")

# Footer
st.markdown("---")
st.markdown('<p style="text-align: center; color: var(--secondary-color);">Developed with ❤️ using Streamlit and rembg</p>', unsafe_allow_html=True)

# Add a back-to-top button
st.markdown("""
<script>
    var mybutton = document.createElement("button");
    mybutton.innerHTML = "⬆️ Back to Top";
    mybutton.style.display = "none";
    mybutton.style.position = "fixed";
    mybutton.style.bottom = "20px";
    mybutton.style.right = "30px";
    mybutton.style.zIndex = "99";
    mybutton.style.border = "none";
    mybutton.style.outline = "none";
    mybutton.style.backgroundColor = "#3498db";
    mybutton.style.color = "white";
    mybutton.style.cursor = "pointer";
    mybutton.style.padding = "15px";
    mybutton.style.borderRadius = "10px";
    mybutton.style.fontSize = "18px";
    mybutton.style.transition = "all 0.3s ease";

    mybutton.onmouseover = function() {
        this.style.backgroundColor = "#2980b9";
    }
    mybutton.onmouseout = function() {
        this.style.backgroundColor = "#3498db";
    }

    document.body.appendChild(mybutton);

    window.onscroll = function() {scrollFunction()};

    function scrollFunction() {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            mybutton.style.display = "block";
        } else {
            mybutton.style.display = "none";
        }
    }

    mybutton.addEventListener("click", function() {
        document.body.scrollTop = 0;
        document.documentElement.scrollTop = 0;
    });
</script>
""", unsafe_allow_html=True)

# Add tooltips
st.markdown("""
<script>
    var tooltips = document.getElementsByClassName('tooltip');
    for (var i = 0; i < tooltips.length; i++) {
        tooltips[i].addEventListener('mouseover', function() {
            var tooltiptext = this.getElementsByClassName('tooltiptext')[0];
            tooltiptext.style.visibility = 'visible';
            tooltiptext.style.opacity = '1';
        });
        tooltips[i].addEventListener('mouseout', function() {
            var tooltiptext = this.getElementsByClassName('tooltiptext')[0];
            tooltiptext.style.visibility = 'hidden';
            tooltiptext.style.opacity = '0';
        });
    }
</script>
""", unsafe_allow_html=True)