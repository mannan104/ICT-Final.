import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. WIDE PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="ICT for Structural Safety",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

plt.style.use('dark_background')

# ==========================================
# 2. HEADER & EXPANDED TEAM CREDITS
# ==========================================
st.title("🏗️ ICT for Structural Safety")
st.subheader("Beam Deflection Analyzer & Risk Monitor")

with st.container(border=True):
    st.write("### 👥 PROJECT DEVELOPED BY TEAM:")
    st.write("") 
    
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
            st.markdown(f"#### {member['name']}")
            st.code(member['reg'], language="text")

st.divider()

# ==========================================
# 3. INTERACTIVE ENGINEERING SIDEBAR
# ==========================================
st.sidebar.header("🔧 Structural Inputs")

L = st.sidebar.slider("Beam Length (L) [m]", 1.0, 20.0, 10.0, step=0.5)
P = st.sidebar.slider("Applied Point Load (P) [N]", 100.0, 10000.0, 2000.0, step=100.0)
E = st.sidebar.slider("Young's Modulus (E) [Pa]", 1e9, 2.5e11, 2.0e11, format="%e")
I = st.sidebar.slider("Moment of Inertia (I) [m4]", 0.000001, 0.01, 0.0005, format="%.6f")

# ==========================================
# 4. STATIC CALCULATIONS & PLOT GENERATION
# ==========================================
delta_max = (P * L**3) / (48 * E * I)

x = np.linspace(0, L, 300)
y = np.zeros_like(x)
half_L = L / 2

for idx, x_val in enumerate(x):
    if x_val <= half_L:
        y[idx] = -(P * x_val * (3 * L**2 - 4 * x_val**2)) / (48 * E * I)
    else:
        x_sym = L - x_val
        y[idx] = -(P * x_sym * (3 * L**2 - 4 * x_sym**2)) / (48 * E * I)

# A. Metrics Row (Simplified text strings to prevent truncation bugs)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Max Displacement", f"{delta_max * 1000:.3f} mm")
c2.metric("Applied Load Force", f"{P:.1f} N")
c3.metric("Total Span Length", f"{L:.1f} m")
c4.metric("Rigidity Factor EI", f"{E*I:.2e} N-m2")

st.write("")

# B. Build Matplotlib Structural Diagram
fig, ax = plt.subplots(figsize=(12, 4))

ax.plot(x, np.zeros_like(x), color='#475569', linestyle='--', alpha=0.6, label='Baseline')
ax.plot(x, y * 1000, color='#38bdf8', linewidth=4.5, label='Deflected Profile')
ax.fill_between(x, y * 1000, 0, color='#38bdf8', alpha=0.1)
ax.scatter([0, L], [0, 0], color='#f59e0b', s=220, marker='^', zorder=5)

ax.annotate(
    f"P = {P:.0f} N", 
    xy=(L/2, np.min(y)*1000), 
    xytext=(L/2, np.min(y)*1000 + (delta_max*1000*0.4) + 5),
    arrowprops=dict(facecolor='#f59e0b', shrink=0.08, width=2, headwidth=8),
    ha='center', color='#f59e0b', weight='bold'
)

ax.set_title("Beam Deflection Shape Elastic Curve", color='white', fontsize=12, pad=12, weight='bold')
ax.set_xlabel("Beam Length Coordinate (meters)", color='#94a3b8')
ax.set_ylabel("Displacement (mm)", color='#94a3b8')
ax.grid(True, linestyle=':', alpha=0.25, color='#cbd5e1')

max_bound = max(delta_max * 1000 * 1.8, 12)
ax.set_ylim(-max_bound, max_bound * 0.4)
ax.set_xlim(-0.5, L + 0.5)

st.pyplot(fig)

# ==========================================
# 5. RISK ASSESSMENT INDICATORS
# ==========================================
st.write("")
st.markdown("### 🚨 Structural Safety Status Evaluation")

if delta_max < 0.005:
    st.success("✅ SAFE: Calculated internal strain deformation parameters are well within allowable design tolerances.")
elif delta_max < 0.02:
    st.warning("⚠️ WARNING STATUS: Structural displacement levels approaching serviceability state limits.")
else:
    st.error("❌ CRITICAL DEFLECTION HAZARD: Severe displacement threshold breached. Immediate design adjustment required.")
