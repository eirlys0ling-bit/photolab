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

# --- CSS Tùy chỉnh (Giao diện tối & Header cam) ---
st.markdown("""
    <style>
    /* Nền tối chủ đạo */
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
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
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
    div[data-testid="stDownloadButton"] > button {
        background-color: #c56b20 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
    }

    /* Thanh trượt (Sliders) */
    .stSlider label {
        color: white !important;
        font-weight: bold !important;
    }
    
    /* Giao diện trang chủ (Cloud upload) */
    .upload-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 50px;
    }
    .cloud-icon {
        border: 3px solid white;
        border-radius: 40px;
        padding: 50px;
        text-align: center;
    }
    
    /* Mục gần đây */
    .recent-item {
        background-color: #d9d9d9; 
        color: black; 
        padding: 15px; 
        border-radius: 15px; 
        display: flex; 
        align-items: center; 
        justify-content: space-between;
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

# --- XỬ LÝ TẢI FILE ---
with st.sidebar:
    st.markdown("### 📥 TẢI ẢNH LÊN")
    uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.session_state.img_input = Image.open(uploaded_file)
        # Lưu vào danh sách gần đây nếu chưa có
        file_info = {
            "name": uploaded_file.name,
            "time": datetime.now().strftime("%d/%m/%Y")
        }
        if file_info["name"] not in [f["name"] for f in st.session_state.recent_files]:
            st.session_state.recent_files.insert(0, file_info)

# --- GIAO DIỆN CHÍNH ---
if st.session_state.img_input:
    img = st.session_state.img_input
    
    # Chia layout: [Công cụ | Ảnh chính | Tinh chỉnh]
    col_tools, col_main, col_adjust = st.columns([1, 2, 1])

    # --- CỘT TRÁI: CÔNG CỤ (Tools) ---
    with col_tools:
        st.write("↩️ ↪️ 🔄") 
        t_cols = st.columns(5)
        icons = ["✂️", "↺", "↻", "↔️", "↕️"]
        for i, icon in enumerate(icons):
            with t_cols[i]: st.button(icon, key=f"tool_{i}")
        
        st.markdown("---")
        angle = st.slider("Xoay", -180, 180, 0)
        zoom = st.slider("Phóng to, thu nhỏ", 10, 200, 100)
        
        st.markdown("---")
        st.write("**Làm mờ**")
        brush_size = st.slider("Bút", 1, 100, 20)
        blur_val = st.slider("Cường độ", 0, 20, 0)

    # --- CỘT GIỮA: HIỂN THỊ ẢNH ---
    with col_main:
        # 1. Xoay & Zoom
        processed = img.rotate(angle, expand=True)
        if zoom != 100:
            w, h = processed.size
            new_size = (int(w * zoom / 100), int(h * zoom / 100))
            processed = processed.resize(new_size)
            
        # 2. Làm mờ
        if blur_val > 0:
            processed = processed.filter(ImageFilter.GaussianBlur(radius=blur_val))
        
        # Hiển thị ảnh chính
        st.image(processed, use_container_width=True)
        
        # Hàng bộ lọc dưới ảnh
        st.markdown("---")
        filters = ["normal", "vivid", "warm", "cool", "vintage", "greyscale"]
        f_cols = st.columns(len(filters))
        selected_filter = "normal"
        for i, f in enumerate(filters):
            with f_cols[i]:
                thumb = img.resize((100, 100))
                if f == "greyscale": thumb = ImageOps.grayscale(thumb)
                st.image(thumb, use_container_width=True)
                if st.button(f, key=f"filter_btn_{f}"):
                    selected_filter = f

    # --- CỘT PHẢI: TINH CHỈNH (Adjustments) ---
    with col_adjust:
        # Tinh chỉnh màu sắc trực tiếp trên ảnh 'processed'
        st.markdown('<div style="text-align:right">', unsafe_allow_html=True)
        buf = io.BytesIO()
        processed.save(buf, format="PNG")
        st.download_button("Lưu", buf.getvalue(), file_name="photolab_edited.png")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        bright = st.slider("Độ sáng", 0.0, 2.0, 1.0)
        contrast = st.slider("Độ tương phản", 0.0, 2.0, 1.0)
        sat = st.slider("Độ bão hòa", 0.0, 2.0, 1.0)
        
        # Áp dụng Enhancers
        enhancer_b = ImageEnhance.Brightness(processed)
        processed = enhancer_b.enhance(bright)
        enhancer_c = ImageEnhance.Contrast(processed)
        processed = enhancer_c.enhance(contrast)
        enhancer_s = ImageEnhance.Color(processed)
        processed = enhancer_s.enhance(sat)
        
        st.markdown("---")
        st.write("**Cân bằng màu**")
        st.slider("🔴 Red", -100, 100, 0)
        st.slider("🟢 Green", -100, 100, 0)
        st.slider("🟡 Blue", -100, 100, 0)

else:
    # --- GIAO DIỆN TRANG CHỦ (Trangchu.png) ---
    st.markdown("""
        <div class="upload-container">
            <div class="cloud-icon">
                <span style="font-size: 80px;">🐱🐱</span><br>
                <div style="margin-top: 15px;">
                    <span style="color: #c56b20; font-size: 40px;">⬆️</span><br>
                    <b style="font-size: 20px;">Tải ảnh lên ở thanh bên trái</b>
                </div>
            </div>
        </div>
        <div style="margin-top: 50px; padding: 0 10%;">
            <h3>Gần đây</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Hiển thị danh sách gần đây
    if not st.session_state.recent_files:
        st.info("Không có tệp nào gần đây.")
    else:
        for f in st.session_state.recent_files[:3]: # Hiển thị tối đa 3 file mới nhất
            st.markdown(f"""
                <div class="recent-item">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 50px; height: 50px; background-color: #888; border-radius: 8px; margin-right: 15px; display: flex; align-items: center; justify-content: center; color: white;">🖼️</div>
                        <div>
                            <b style="font-size: 18px;">{f['name']}</b><br>
                            <small style="color: #555;">{f['time']}</small>
                        </div>
                    </div>
                    <span style="font-size: 24px; cursor: pointer;">🗑️</span>
                </div>
            """, unsafe_allow_html=True)