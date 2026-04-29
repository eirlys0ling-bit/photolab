import streamlit as st
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import io
import numpy as np
from datetime import datetime

# --- Cấu hình giao diện ---
st.set_page_config(page_title="PhotoLab Pro", page_icon="🎨", layout="wide")

# --- CSS Tùy chỉnh (Đảm bảo giao diện hiện đại & không lỗi) ---
st.markdown("""
    <style>
    .stApp { background-color: #1e1e1e; color: white; }
    .main-header {
        background-color: #c56b20;
        padding: 15px;
        text-align: center;
        margin: -6rem -5rem 2rem -5rem;
    }
    .header-title { font-family: 'Brush Script MT', cursive; font-size: 50px; color: white; margin: 0; }
    .tool-box { background: #2d2d2d; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    .stSlider [data-baseweb="slider"] { margin-bottom: 20px; }
    </style>
    <div class="main-header"><h1 class="header-title">PhotoLab</h1></div>
    """, unsafe_allow_html=True)

# --- Quản lý trạng thái ---
if 'img' not in st.session_state:
    st.session_state.img = None
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Trang chủ ---
if st.session_state.img is None:
    st.markdown("<h2 style='text-align: center;'>☁️ Tải ảnh lên để bắt đầu</h2>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Chọn ảnh", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded:
        st.session_state.img = Image.open(uploaded).convert("RGB")
        st.rerun()
    
    if st.session_state.history:
        st.write("---")
        st.write("🕒 Ảnh vừa chỉnh sửa")
        cols = st.columns(4)
        for i, h in enumerate(st.session_state.history[:4]):
            cols[i].image(h, use_container_width=True)
else:
    # --- Trang Editor ---
    col_l, col_m, col_r = st.columns([1, 2, 1])

    with col_l:
        if st.button("⬅️ Quay lại"):
            st.session_state.img = None
            st.rerun()
        
        st.markdown("### 🛠️ Hình dáng")
        with st.container(border=True):
            angle = st.slider("Xoay tự do", -180, 180, 0)
            zoom = st.slider("Thu phóng (%)", 50, 200, 100)
            st.write("Lật ảnh")
            c1, c2 = st.columns(2)
            flip_h = c1.button("↔️ Ngang")
            flip_v = c2.button("↕️ Dọc")

        st.markdown("### 🌫️ Hiệu ứng mờ")
        with st.container(border=True):
            blur_val = st.slider("Mờ toàn phần", 0, 20, 0)
            st.info("Sử dụng thanh trượt để làm mờ nghệ thuật")

    with col_r:
        st.markdown("### 🎨 Màu sắc")
        with st.container(border=True):
            bright = st.slider("Độ sáng", 0.5, 2.0, 1.0)
            cont = st.slider("Tương phản", 0.5, 2.0, 1.0)
            sat = st.slider("Bão hòa", 0.0, 2.0, 1.0)
        
        st.markdown("### ⚖️ Cân bằng RGB")
        with st.container(border=True):
            r_gain = st.slider("Red (Đỏ)", 0.5, 1.5, 1.0)
            g_gain = st.slider("Green (Xanh lá)", 0.5, 1.5, 1.0)
            b_gain = st.slider("Blue (Xanh dương)", 0.5, 1.5, 1.0)

        preset = st.selectbox("Bộ lọc nhanh", ["Gốc", "Vivid", "Vintage", "B&W", "Cool", "Warm"])

    with col_main := col_m:
        # Xử lý Pipeline
        out = st.session_state.img
        
        # Xoay & Zoom
        if angle != 0: out = out.rotate(angle, expand=True)
        if zoom != 100:
            w, h = out.size
            out = out.resize((int(w*zoom/100), int(h*zoom/100)))
        
        # Filter
        if preset == "B&W": out = ImageOps.grayscale(out).convert("RGB")
        elif preset == "Vintage": out = ImageOps.colorize(ImageOps.grayscale(out), "#704214", "#C0C0C0")
        
        # RGB Balance (Nâng cao)
        if r_gain != 1.0 or g_gain != 1.0 or b_gain != 1.0:
            data = np.array(out).astype(float)
            data[:,:,0] *= r_gain
            data[:,:,1] *= g_gain
            data[:,:,2] *= b_gain
            out = Image.fromarray(np.clip(data, 0, 255).astype('uint8'))

        # Tinh chỉnh
        out = ImageEnhance.Brightness(out).enhance(bright)
        out = ImageEnhance.Contrast(out).enhance(cont)
        out = ImageEnhance.Color(out).enhance(sat)
        if blur_val > 0: out = out.filter(ImageFilter.GaussianBlur(blur_val))

        st.image(out, use_container_width=True, caption="Bản xem trước")

        # Nút hành động chính
        buf = io.BytesIO()
        out.save(buf, format="PNG")
        st.download_button("💾 LƯU VỀ MÁY", buf.getvalue(), "photolab_edit.png", "image/png")
        
        if st.button("✨ Thêm vào lịch sử"):
            st.session_state.history.insert(0, out)
            st.success("Đã lưu vào bộ nhớ tạm!")