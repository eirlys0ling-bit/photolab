import streamlit as st
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import io

# --- Cấu hình giao diện chuẩn PhotoLab ---
st.set_page_config(
    page_title="PhotoLab",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS Tùy chỉnh theo bản thiết kế Trangchu.png và edit.png ---
st.markdown("""
    <style>
    /* Nền tối chủ đạo và font chữ */
    .stApp {
        background-color: #262626;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header màu cam đặc trưng */
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
    
    /* Các nút chức năng (Undo, Redo, Tools) */
    .stButton > button {
        background-color: #444;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 5px 10px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #c56b20;
        color: white;
    }
    
    /* Nút LƯU màu cam */
    .save-btn > div > button {
        background-color: #c56b20 !important;
        width: 80px;
    }

    /* Thanh trượt (Sliders) */
    .stSlider label {
        color: white !important;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 0px;
    }
    div[data-baseweb="slider"] > div > div {
        background: white !important;
    }
    div[role="slider"] {
        background-color: #c56b20 !important;
    }

    /* Khung chứa ảnh preview bộ lọc */
    .filter-box {
        text-align: center;
        margin-top: 10px;
    }
    .filter-label {
        font-size: 12px;
        margin-top: 5px;
    }
    
    /* Giao diện trang chủ (Cloud upload) */
    .upload-area {
        border: 2px dashed white;
        border-radius: 40px;
        padding: 40px;
        text-align: center;
        margin: 50px auto;
        width: 300px;
    }
    </style>
    <div class="main-header">
        <h1 class="header-title">PhotoLab</h1>
    </div>
    """, unsafe_allow_headers=True)

# --- Khởi tạo State ---
if 'img_input' not in st.session_state:
    st.session_state.img_input = None

# --- GIAO DIỆN CHÍNH ---
with st.sidebar:
    st.markdown("### 📥 TẢI ẢNH LÊN")
    uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.session_state.img_input = Image.open(uploaded_file)

if st.session_state.img_input:
    img = st.session_state.img_input
    
    # Chia layout: [Công cụ | Ảnh chính | Tinh chỉnh]
    col_tools, col_main, col_adjust = st.columns([1, 2, 1])

    # --- CỘT TRÁI: CÔNG CỤ (Dựa trên edit.png) ---
    with col_tools:
        st.write("↩️ ↪️ 🔄") # Giả lập các nút Undo, Redo, Reset
        t1, t2, t3, t4, t5 = st.columns(5)
        with t1: st.button("✂️")
        with t2: st.button("↺")
        with t3: st.button("↻")
        with t4: st.button("↔️")
        with t5: st.button("↕️")
        
        st.markdown("---")
        st.write("**Xoay**")
        angle = st.slider("Xoay", -180, 180, 0, label_visibility="collapsed")
        
        st.write("**Phóng to, thu nhỏ**")
        zoom = st.slider("Phóng to", 10, 200, 100, label_visibility="collapsed")
        
        st.markdown("---")
        st.write("**Làm mờ**")
        st.slider("Kích thước Bút", 1, 100, 20)
        blur_val = st.slider("Cường độ mờ", 0, 20, 0)

    # --- CỘT GIỮA: ẢNH & BỘ LỌC ---
    with col_main:
        # Xử lý ảnh cơ bản
        processed = img.rotate(angle, expand=True)
        if blur_val > 0:
            processed = processed.filter(ImageFilter.GaussianBlur(radius=blur_val))
        
        # Hiển thị ảnh chính
        st.image(processed, use_container_width=True)
        
        # Hàng bộ lọc (Dựa trên chọn bộ lọc.png)
        st.markdown("---")
        filters = ["normal", "vivid", "warm", "cool", "vintage", "greyscale"]
        f_cols = st.columns(len(filters))
        for i, f in enumerate(filters):
            with f_cols[i]:
                # Tạo bản xem trước nhỏ (thumbnail)
                thumb = img.resize((100, 100))
                if f == "greyscale": thumb = ImageOps.grayscale(thumb)
                st.image(thumb, use_container_width=True)
                st.caption(f)

    # --- CỘT PHẢI: TINH CHỈNH (Dựa trên edit.png) ---
    with col_adjust:
        st.markdown('<div class="save-btn">', unsafe_allow_headers=True)
        # Nút lưu ảnh
        buf = io.BytesIO()
        processed.save(buf, format="PNG")
        st.download_button("Lưu", buf.getvalue(), file_name="photolab_edit.png")
        st.markdown('</div>', unsafe_allow_headers=True)
        
        st.write("**Độ sáng**")
        bright = st.slider("Độ sáng", 0.0, 2.0, 1.0, key="br", label_visibility="collapsed")
        
        st.write("**Độ tương phản**")
        contrast = st.slider("Độ tương phản", 0.0, 2.0, 1.0, key="ct", label_visibility="collapsed")
        
        st.write("**Độ bão hòa**")
        sat = st.slider("Độ bão hòa", 0.0, 2.0, 1.0, key="st", label_visibility="collapsed")
        
        st.markdown("---")
        st.write("**Cân bằng màu**")
        st.slider("🔴 Red - Cyan", -100, 100, 0)
        st.slider("🟢 Green - Magenta", -100, 100, 0)
        st.slider("🟡 Blue - Yellow", -100, 100, 0)

else:
    # --- GIAO DIỆN TRANG CHỦ (Trangchu.png) ---
    st.markdown("""
        <div style="text-align: center; margin-top: 30px;">
            <div style="display: inline-block; border: 3px solid white; border-radius: 40px; padding: 40px;">
                <span style="font-size: 80px;">🐱🐱</span><br>
                <div style="margin-top: 10px;">
                    <span style="color: #c56b20; font-size: 40px;">⬆️</span><br>
                    <b style="font-size: 24px;">Tải ảnh lên</b>
                </div>
            </div>
            <h3 style="margin-top: 40px; text-align: left; margin-left: 10%;">Gần đây</h3>
        </div>
    """, unsafe_allow_headers=True)
    
    # Hiển thị demo ảnh gần đây
    c_left, c_mid, c_right = st.columns([1, 4, 1])
    with c_mid:
        st.markdown("""
            <div style="background-color: #d9d9d9; color: black; padding: 15px; border-radius: 15px; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 50px; height: 50px; background-color: #888; border-radius: 8px; margin-right: 15px;"></div>
                    <div>
                        <b>meo.jpeg</b><br>
                        <small style="color: #555;">29/04/2026</small>
                    </div>
                </div>
                <span>🗑️</span>
            </div>
        """, unsafe_allow_headers=True)