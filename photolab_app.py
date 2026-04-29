import streamlit as st
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import io
import numpy as np
from datetime import datetime

# --- Cấu hình giao diện ---
st.set_page_config(page_title="PhotoLab Pro", page_icon="🎨", layout="wide")

# --- CSS Tùy chỉnh (Sửa lỗi icon và giao diện) ---
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
    .stSlider [data-baseweb="slider"] { margin-bottom: 20px; }
    /* Fix cho các nút bấm hiển thị đẹp hơn */
    .stButton > button {
        width: 100%;
        background-color: #383838;
        color: white;
        border: 1px solid #444;
    }
    .stButton > button:hover {
        border-color: #c56b20;
        color: #c56b20;
    }
    </style>
    <div class="main-header"><h1 class="header-title">PhotoLab</h1></div>
    """, unsafe_allow_html=True)

# --- Khởi tạo State ---
if 'img' not in st.session_state:
    st.session_state.img = None
if 'history' not in st.session_state:
    st.session_state.history = []

# --- GIAO DIỆN ---
if st.session_state.img is None:
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>☁️ Tải ảnh lên để bắt đầu</h2>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Chọn ảnh", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded:
        st.session_state.img = Image.open(uploaded).convert("RGB")
        st.rerun()
    
    if st.session_state.history:
        st.write("---")
        st.write("🕒 Ảnh trong phiên làm việc này")
        cols = st.columns(4)
        for i, h in enumerate(st.session_state.history[:4]):
            cols[i].image(h, use_container_width=True)
else:
    # Cấu hình Layout
    col_l, col_m, col_r = st.columns([1.2, 2.5, 1.2])

    with col_l:
        if st.button("⬅️ QUAY LẠI TRANG CHỦ"):
            st.session_state.img = None
            st.rerun()
        
        st.markdown("### 🛠️ Hình dáng")
        angle = st.slider("Xoay ảnh (độ)", -180, 180, 0)
        zoom = st.slider("Thu phóng (%)", 10, 200, 100)
        
        st.write("Lật ảnh")
        cl1, cl2 = st.columns(2)
        flip_h = cl1.checkbox("Ngang")
        flip_v = cl2.checkbox("Dọc")

        st.markdown("### 🌫️ Hiệu ứng")
        blur_val = st.slider("Độ mờ (Blur)", 0, 20, 0)

    with col_r:
        st.markdown("### 🎨 Màu sắc")
        bright = st.slider("Độ sáng", 0.1, 2.0, 1.0)
        cont = st.slider("Tương phản", 0.1, 2.0, 1.0)
        sat = st.slider("Bão hòa", 0.0, 2.0, 1.0)
        
        st.markdown("### ⚖️ Cân bằng RGB")
        r_gain = st.slider("Red (Đỏ)", 0.0, 2.0, 1.0)
        g_gain = st.slider("Green (Xanh lá)", 0.0, 2.0, 1.0)
        b_gain = st.slider("Blue (Xanh dương)", 0.0, 2.0, 1.0)

        preset = st.selectbox("Bộ lọc nhanh", ["Gốc", "Sắc nét", "Trắng đen", "Hoài cổ", "Lạnh", "Ấm"])

    with col_m:
        # --- PIPELINE XỬ LÝ ẢNH ---
        proc = st.session_state.img
        
        # 1. Xoay & Lật & Zoom
        if angle != 0: proc = proc.rotate(angle, expand=True)
        if flip_h: proc = ImageOps.mirror(proc)
        if flip_v: proc = ImageOps.flip(proc)
        if zoom != 100:
            w, h = proc.size
            proc = proc.resize((int(w*zoom/100), int(h*zoom/100)))
        
        # 2. Bộ lọc (Presets)
        if preset == "Trắng đen":
            proc = ImageOps.grayscale(proc).convert("RGB")
        elif preset == "Hoài cổ":
            proc = ImageOps.colorize(ImageOps.grayscale(proc), "#704214", "#C0C0C0")
        elif preset == "Sắc nét":
            proc = proc.filter(ImageFilter.SHARPEN)
        
        # 3. Cân bằng RGB (Sử dụng Numpy để đảm bảo tốc độ)
        if r_gain != 1.0 or g_gain != 1.0 or b_gain != 1.0:
            arr = np.array(proc).astype(float)
            arr[:,:,0] *= r_gain
            arr[:,:,1] *= g_gain
            arr[:,:,2] *= b_gain
            proc = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))

        # 4. Tinh chỉnh cơ bản
        proc = ImageEnhance.Brightness(proc).enhance(bright)
        proc = ImageEnhance.Contrast(proc).enhance(cont)
        proc = ImageEnhance.Color(proc).enhance(sat)
        if blur_val > 0:
            proc = proc.filter(ImageFilter.GaussianBlur(blur_val))

        # Hiển thị ảnh kết quả
        st.image(proc, use_container_width=True)

        # 5. Xuất bản
        st.markdown("---")
        buf = io.BytesIO()
        proc.save(buf, format="PNG")
        
        c_save, c_hist = st.columns(2)
        c_save.download_button(
            label="💾 TẢI ẢNH VỀ MÁY",
            data=buf.getvalue(),
            file_name="photolab_pro.png",
            mime="image/png"
        )
        if c_hist.button("✨ LƯU VÀO LỊCH SỬ"):
            st.session_state.history.insert(0, proc)
            st.toast("Đã thêm vào danh sách phía dưới!")
