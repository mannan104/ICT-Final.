import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import io

# Safe import for automated PDF reports
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    PDF_OK = True
except ImportError:
    PDF_OK = False

# ==========================================
# 1. PAGE ARCHITECTURE & UI THEMING
# ==========================================
st.set_page_config(
    page_title="Beam Deflection Visualizer",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom injection of Tailwind-inspired styling matching Streamlit Dark Theme
st.markdown("""
<style>
    .stApp {
        background-color: #020617;
        color: #f8fafc;
    }
    .block-container {
        max-width: 1200px;
        margin: auto;
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    .metric-card {
        background-color: #0f172a;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1e293b;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        text-align: center;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.75rem;
        font-weight: 600;
    }
    .project-footer {
        text-align: center;
        color: #64748b;
        padding: 2rem 0;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. APP HEADER & TEAM MATRIX
# ==========================================
st.title("🏗️ Structural Beam Deflection Visualizer")
st.markdown("<p style='text-align:center; color: #94a3b8; font-size: 1.15rem; margin-bottom: 2rem;'>ICT for Structural Safety — Simply Supported Beam Engineering Lab</p>", unsafe_allow_html=True)

# Clean, professional metadata grid for the project team
with st.container():
    st.markdown("### 👥 Project Investigation Team")
    tm1, tm2, tm3, tm4, tm5 = st.columns(5)
    with tm1: st.markdown("<div style='background-color:#0f172a; padding:10px; border-radius:8px; border:1px solid #1e293b;'><b>Abdul Mannan</b><br><code style='color:#38bdf8;'>25-ME-55</code></div>", unsafe_allow_html=True)
    with tm2: st.markdown("<div style='background-color:#0f172a; padding:10px; border-radius:8px; border:1px solid #1e293b;'><b>M. bin Akarma</b><br><code style='color:#38bdf8;'>25-ME-59</code></div>", unsafe_allow_html=True)
    with tm3: st.markdown("<div style='background-color:#0f172a; padding:10px; border-radius:8px; border:1px solid #1e293b;'><b>Muneeb Azhar</b><br><code style='color:#38bdf8;'>25-ME-27</code></div>", unsafe_allow_html=True)
    with tm4: st.markdown("<div style='background-color:#0f172a; padding:10px; border-radius:8px; border:1px solid #1e293b;'><b>Ahmed Ali</b><br><code style='color:#38bdf8;'>25-ME-115</code></div>", unsafe_allow_html=True)
    with tm5: st.markdown("<div style='background-color:#0f172a; padding:10px; border-radius:8px; border:1px solid #1e293b;'><b>Hammad Fida</b><br><code style='color:#38bdf8;'>25-ME-03</code></div>", unsafe_allow_html=True)

st.divider()

# ==========================================
# 3. SIDEBAR PARAMETER CONTROL PANEL
# ==========================================
with st.sidebar:
    st.header("⚙️ Design Parameters")
    st.markdown("---")
    
    st.subheader("📏 Geometry")
    L = st.slider("Beam Span Length (L)", 1.0, 20.0, 10.0, step=0.5, help="Total length of the simply supported beam in meters.")
    
    st.subheader("🔌 Load Configuration")
    load_type = st.selectbox(
        "Load Distribution Profile", 
        ["Point Load (Mid-Span)", "Uniformly Distributed Load (UDL)", "Symmetric Triangular Load"]
    )
    
    if load_type == "Point Load (Mid-Span)":
        P = st.slider("Concentrated Load P (N)", 100.0, 50000.0, 12000.0, step=100.0)
        w = 0.0
    elif load_type == "Uniformly Distributed Load (UDL)":
        w = st.slider("Distributed Load w (N/m)", 10.0, 10000.0, 1500.0, step=50.0)
        P = 0.0
    else: # Triangular load
        w = st.slider("Peak Central Load w_max (N/m)", 10.0, 10000.0, 2000.0, step=50.0)
        P = 0.0

    st.subheader("🪵 Material Classification")
    material = st.selectbox("Structural Material", ["Structural Steel", "Aluminum (6061-T6)", "M25 Concrete"])
    
    if material == "Structural Steel":
        E = 200e9      # Elastic Modulus (Pa)
        allow = 250e6  # Allowable Yield Stress (Pa)
    elif material == "Aluminum (6061-T6)":
        E = 70e9
        allow = 150e6
    else:
        E = 30e9
        allow = 25e6

    st.subheader("📐 Rectangular Profile Cross-Section")
    b = st.number_input("Section Width b (m)", min_value=0.01, max_value=2.0, value=0.25, step=0.01)
    h = st.number_input("Section Height h (m)", min_value=0.01, max_value=2.0, value=0.50, step=0.01)
    
    # Structural Properties Calculations
    I = (b * h**3) / 12  # Second Area Moment of Inertia
    c = h / 2            # Distance to extreme fiber

# ==========================================
# 4. STRUCTURAL MECHANICS ENGINE
# ==========================================
x = np.linspace(0, L, 250)

if load_type == "Point Load (Mid-Span)":
    # Max deflection at midspan
    delta_max = (P * L**3) / (48 * E * I)
    # Piecewise function handled via symmetry to prevent right-side curve distortion
    x_symmetric = np.minimum(x, L - x)
    y = (P * x_symmetric * (3 * L**2 - 4 * x_symmetric**2)) / (48 * E * I)
    M_max = (P * L) / 4

elif load_type == "Uniformly Distributed Load (UDL)":
    delta_max = (5 * w * L**4) / (384 * E * I)
    y = (w * x * (L**3 - 2 * L * x**2 + x**3)) / (24 * E * I)
    M_max = (w * L**2) / 8

else: # Symmetric Triangular Load peaking at center span
    delta_max = (w * L**4) / (120 * E * I)
    x_symmetric = np.minimum(x, L - x)
    y = (w * x_symmetric * (25 * L**4 - 40 * L**2 * x_symmetric**2 + 16 * x_symmetric**4)) / (960 * E * I)
    M_max = (w * L**2) / 12

# Vector adjustments: map down deflection visually
y_deflected = -y
max_bending_stress = (M_max * c) / I
fos = allow / max_bending_stress if max_bending_stress > 0 else float('inf')

# ==========================================
# 5. HIGH-FIDELITY DASHBOARD METRICS
# ==========================================
st.markdown("### 📊 Engineering Limit State Performance")
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>📉 Max Deflection</div>
        <div class='metric-value'>{delta_max*
