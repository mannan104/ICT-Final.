import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. PAGE SETUP & THEME
# ==========================================
st.set_page_config(
    page_title="Structural Safety Engine",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
plt.style.use('dark_background')

# ==========================================
# 2. HERO HEADER & SPARKING TEAM BOARD
# ==========================================
st.title("🏗️ ICT for Structural Safety")
st.subheader("Advanced Beam Deflection & Cross-Section Analyzer")

with st.container(border=True):
    st.write("### 👥 PROJECT DEVELOPED BY TEAM:")
    st.write("") 
    cols = st.columns(5)
    t_data = [
        {"n": "Abdul Mannan", "r": "Reg No: 25-ME-55"},
        {"n": "Muhammad bin Akarma", "r": "Reg No: 25-ME-59"},
        {"n": "Muneeb Azhar", "r": "Reg No: 25-ME-03"},
        {"n": "Ahmed Ali", "r": "Reg No: 25-ME-115"},
        {"n": "Hammad Fida", "r": "Reg No: 25-ME-27"}
    ]
    for idx, member in enumerate(t_data):
        with cols[idx]:
            st.markdown(f"#### {member['n']}")
            st.code(member['r'], language="text")

st.divider()

# ==========================================
# 3. GLOBAL FALLBACK PARAMETERS
# ==========================================
L = 10.0
P = 5000.0
E = 2.0e11
I_val = 0.0005

# ==========================================
# 4. BOTTOM SEPARATED CONFIGURATION DECKS
# ==========================================
st.markdown("### 🛠️ Structural Parameter Settings")

# Creating 3 wide configuration layout cards at the very bottom
p1, p2, p3 = st.columns(3)

with p1:
    with st.container(border=True):
        st.markdown("#### 📏 Span Geometry & Load")
        L = st.slider("Beam Length (L) [meters]", 1.0, 20.0, 10.0, step=0.5)
        P = st.slider("Point Force Load (P) [N]", 100.0, 15000.0, 5000.0, step=100.0)

with p2:
    with st.container(border=True):
        st.markdown("#### 🔬 Material Selector")
        mat = st.selectbox("Alloy Core", ["Steel (200 GPa)", "Aluminum (70 GPa)", "Concrete (30 GPa)"])
        E = 2.0e11 if "Steel" in mat else (7.0e10 if "Aluminum" in mat else 3.0e10)
        st.caption(f"Active Modulus E: {E:e} Pa")

with p3:
    with st.container(border=True):
        st.markdown("#### 📐 Profile Shape Definition")
        profile = st.selectbox("Cross-Section Shape", ["Rectangular Solid Beam", "Heavy I-Beam Profile", "Hollow Structural Tube"])
        default_I = 0.0005 if "Rectangular" in profile else (0.0012 if "I-Beam" in profile else 0.0002)
        I_val = st.number_input("Moment of Inertia (I) [m4]", value=default_I, format="%.6f")

# ==========================================
# 5. PHYSICS EQUATIONS & MODEL GENERATION
# ==========================================
delta_max = (P * L**3) / (48 * E * I_val)

x = np.linspace(0, L, 200)
y = np.zeros_like(x)
half_L = L / 2

for idx, x_val in enumerate(x):
    if x_val <= half_L:
        y[idx] = -(P * x_val * (3 * L**2 - 4 * x_val**2)) / (48 * E * I_val)
    else:
        y[idx] = -(P * (L - x_val) * (3 * L**2 - 4 * (L - x_val)**2)) / (48 * E * I_val)

# ==========================================
# 6. GRAPHICS RENDERING (TOP PLACEMENT VIEW)
# ==========================================
st.markdown("### 📊 Live Deflection Telemetry Display")

# Live Metrics Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Max Displacement", f"{delta_max * 1000:.3f} mm")
m2.metric("Total Span Range", f"{L:.1f} m")
m3.metric("Applied Load force", f"{P:.0f} N")
m4.metric("Rigidity Factor (EI)", f"{E*I_val:.2e} N-m2")
