import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# ==========================================
# 1. PAGE CONFIGURATION & LAYOUT WIDENING
# ==========================================
st.set_page_config(
    page_title="ICT for Structural Safety: Live Beam Deflection Visualizer",
    page_icon="🏗️",
    layout="wide", # Spreads content across the full viewport width
    initial_sidebar_state="expanded"
)

# Apply sleek high-contrast dark theme presets for engineering graphics
plt.style.use('dark_background')

# ==========================================
# 2. HERO HEADER & HIGH-WIDE TEAM CREDITS
# ==========================================
st.title("🏗️ ICT for Structural Safety")
st.subheader("Live Beam Deflection Visualizer & Risk Monitor")

# Spaced out Team Board to solve congestion
with st.container(border=True):
    st.write("### 👥 PROJECT DEVELOPED BY TEAM:")
    st.write("") # Extra padding spacing
    
    # Using 5 distinct wider layout columns
    cols = st.columns(5)
    team_data = [
        {"name": "Abdul Mannan", "reg": "Reg No: 25-ME-55"},
        {"name": "Muhammad bin Akarma", "reg": "Reg No: 25-ME-59"},
        {"name": "Muneeb Azhar", "reg": "Reg No: 25-ME-03"},
        {"name": "Ahmed Ali", "reg": "Reg No: 25-ME-115"},
        {"name": "Hammad Fida", "reg": "Reg No: 25-ME-27"}
    ]

    for i, member in enumerate(team_data):
        with cols[i]:
            # Clean structured card arrangement
            st.markdown(f"#### {member['name']}")
            st.code(member['reg'], language="text")

st.divider()

# ==========================================
# 3. SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("🔧 Structural Parameters")

L = st.sidebar.slider("Beam Length (L) [m]", 1.0, 20.0, 10.0, step=0.5)
P_base = st.sidebar.slider("Static Point Load (P) [N]", 100.0, 10000.0, 2000.0, step=100.0)
E = st.sidebar.slider("Young's Modulus (E) [Pa]", 1e9, 2.5e11, 2.0e11, format="%e")
I = st.sidebar.slider("Moment of Inertia (I) [m⁴]", 0.000001, 0.01, 0.0005, format="%.6f")

st.sidebar.header("⚡ Live Simulation Settings")
run_vibration = st.sidebar.toggle("Activate Dynamic Load Oscillation", value=True)

# ==========================================
# 4. ENGINEERING THEORY VISUAL PANEL
# ==========================================
with st.container(border=True):
    st.markdown("### 📘 Structural Engineering Theory")
    
    col_theory_1, col_theory_2 = st.columns([3, 2])
    with col_theory_1:
        st.markdown(
            "For a **Simply Supported Beam** subjected to a concentrated central point load, "
            "the elastic line curve modeling deformation profile can be calculated using the Euler-Bernoulli beam equation system."
        )
        st.latex(r"\delta_{max} = \frac{P \cdot L^3}{48 \cdot E \cdot I}")
    with col_theory_2:
        st.markdown(
            "- **P** = Applied Dynamic Force $(N)$\n"
            "- **L** = Total Span Length $(m)$\n"
            "- **E** = Material Modulus of Elasticity $(Pa)$\n"
            "- **I** = Cross-Sectional Area Moment of Inertia $(m^4)$"
        )

st.write("")

# ==========================================
# 5. DYNAMIC PROCESSING GRAPHICS ENGINE
# ==========================================
x = np.linspace(0, L, 300)

# Clean rendering slot boxes for screen optimization updates
metric_slot = st.empty()
plot_slot = st.empty()
safety_slot = st.empty()

iteration = 0
while True:
    # Simulate cyclical physical vibration (traffic, machinery, or wind forces)
    if run_vibration:
        iteration += 1
        vibration_factor = 1 + 0.18 * np.sin(iteration * 0.4)
        P_dynamic = P_base * vibration_factor
    else:
        P_dynamic = P_base

    # Accurate Physics Calculations
    delta_max = (P_dynamic * L**3) / (48 * E * I)
    
    # Map out the deflection shape across length space coordinates
    y = np.zeros_like(x)
    half_L = L / 2
    for idx, x_val in enumerate(x):
        if x_val <= half_L:
            y[idx] = -(P_dynamic * x_val * (3 * L**2 - 4 * x_val**2)) / (48 * E * I)
        else:
            x_sym = L - x_val
            y[idx] = -(P_dynamic * x_sym * (3 * L**2 - 4 * x_sym**2)) / (48 * E * I)

    # A. Render Spaced Metric Panels
    with metric_slot.container():
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Max Displacement", f"{delta_max * 1000:.3f} mm")
        c2.metric("Dynamic Sensor Load", f"{P_dynamic:.1f} N")
        c3.metric("Total Span (L)", f"{L:.1f} m")
        c4.metric("Flexural Rigidity (
