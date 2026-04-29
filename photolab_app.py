import streamlit as st
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import io
from datetime import datetime

# --- Cấu hình giao diện chuẩn PhotoLab ---
st.set_page_config(
    page_title="PhotoLab",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS Tùy chỉnh ---
st.markdown("""
    <style>
    .stApp {
        background-color: #262626;
        color: white;
    }
    .main-header {
        background-color: #c56b20;
        padding: 10px;
        text-align: center;
        margin: -6rem -5rem 2rem -5rem;
    }
    .header-title {
        font-family: 'Brush Script MT', cursive;
        color: white;
        font-size: 70px;
        margin: 0;
    }
    /* Style cho vùng upload giả lập */
    .upload-box {
        border: 3px solid white;
        border-radius: 40px;
        padding: 40px;
        text-align: center;
        margin: 20px auto;
        width: fit-content;
        cursor: pointer;
    }
    .recent-item {
        background-color: #d9d9d9; 
        color: black; 
        padding: 15px; 
        border-radius: 15px; 
        display: flex; 
        align-items: center; 
        margin-bottom: 10px;
    }
    </style>
    <div class="main-header">
        <h1 class="header-title">PhotoLab</h1>
    </div>
    """, unsafe_allow_html=True)

# --- Khởi tạo State ---
if 'img_input' not in st.session_state:
    st.session_state.img_input = None
if 'recent_files' not in st.session_state:
    st.session_state.recent_files = []

# --- GIAO DIỆN CHÍNH ---
if st.session_state.img_input is None:
    # --- TRANG CHỦ ---
    st.markdown("""
        <div class="upload-box">
            <span style="font-size: 80px;">☁️</span><br>
            <b style="font-size: 20px;">Sẵn sàng chỉnh sửa?</b>
        </div>
    """, unsafe_allow_html=True)
    
    # Nút upload thật sự nằm ở đây
    uploaded_file = st.file_uploader("Bấm vào đây để chọn ảnh từ máy tính", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        st.session_state.img_input = Image.open(uploaded_file)
        # Lưu vào danh sách gần đây
        file_info = {"name": uploaded_file.name, "time": datetime.now().strftime("%d/%m/%Y")}
        st.session_state.recent_files.insert(0, file_info)
        st.rerun()

    st.markdown("### Gần đây")
    if not st.session_state.recent_files:
        st.info("Chưa có ảnh nào được xử lý.")
    else:
        for f in st.session_state.recent_files[:3]:
            st.markdown(f"""
                <div class="recent-item">
                    <div style="width: 40px; height: 40px; background: #c56b20; border-radius: 5px; margin-right: 15px;"></div>
                    <div><b>{f['name']}</b><br><small>{f['time']}</small></div>
                </div>
            """, unsafe_allow_html=True)

else:
    # --- TRANG EDITOR ---
    if st.button("⬅️ Quay lại Trang chủ"):
        st.session_state.img_input = None
        st.rerun()

    img = st.session_state.img_input
    col_tools, col_main, col_adjust = st.columns([1, 2, 1])

    with col_tools:
        st.write("🛠️ **Công cụ**")
        angle = st.slider("Xoay ảnh", -180, 180, 0)
        zoom = st.slider("Thu phóng (%)", 10, 200, 100)
        blur = st.slider("Làm mờ", 0, 20, 0)

    with col_adjust:
        st.write("🎨 **Tinh chỉnh**")
        bright = st.slider("Độ sáng", 0.5, 1.5, 1.0)
        cont = st.slider("Tương phản", 0.5, 1.5, 1.0)
        sat = st.slider("Bão hòa", 0.5, 1.5, 1.0)
        
        # Nút Lưu
        buf = io.BytesIO()
        # (Xử lý ảnh sẽ thực hiện ở col_main để hiển thị)
        
    with col_main:
        # Xử lý ảnh pipeline
        proc = img.rotate(angle, expand=True)
        if zoom != 100:
            w, h = proc.size
            proc = proc.resize((int(w*zoom/100), int(h*zoom/100)))
        if blur > 0:
            proc = proc.filter(ImageFilter.GaussianBlur(blur))
        
        proc = ImageEnhance.Brightness(proc).enhance(bright)
        proc = ImageEnhance.Contrast(proc).enhance(cont)
        proc = ImageEnhance.Color(proc).enhance(sat)
        
        st.image(proc, use_container_width=True)
        
        # Download
        proc.save(buf, format="PNG")
        st.download_button("💾 TẢI ẢNH ĐÃ SỬA", buf.getvalue(), file_name="photolab_export.png")