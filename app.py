import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="ICT Structural Safety Visualizer",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# HERO BANNER & TEAM CREDITS
# ==========================================
st.title("⚡ ICT for Structural Safety")
st.subheader("Live Beam Deflection Visualizer & Risk Monitor")

with st.container(border=True):
    st.write("### DEVELOPED BY TEAM:")
    cols = st.columns(5)
    team_data = [
        {"name": "Abdul Mannan", "reg": "Reg No: 55"},
        {"name": "Muhammad bin Akarma", "reg": "Reg No: 59"},
        {"name": "Muneeb Azhar", "reg": "Reg No: 03"},
        {"name": "Ahmed Ali", "reg": "Reg No: 115"},
        {"name": "Hammad Fida", "reg": "Reg No: 27"}
    ]
    for i, member in enumerate(team_data):
        with cols[i]:
            st.markdown(f"**{member['name']}**")
            st.caption(member['reg'])

st.divider()

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("🏗️ Structural Parameters")
beam_type = st.sidebar.selectbox("Beam Configuration", ["Cantilever (Fixed-Free)", "Simply Supported (Pinned-Pinned)"])
length = st.sidebar.slider("Beam Length (L) [meters]", 2.0, 15.0, 8.0, 0.5)
elasticity = st.sidebar.slider("Elastic Modulus (E) [GPa]", 10, 210, 200, step=10)
inertia = st.sidebar.slider("Moment of Inertia (I) [10⁻⁶ m⁴]", 10, 500, 150, step=10)

st.sidebar.header("⚖️ Dynamic Loading")
load_type = st.sidebar.radio("Load Condition", ["Point Load at Center/Tip", "Oscillating Dynamic Load"])
base_load = st.sidebar.slider("Load Magnitude (P) [kN]", 5.0, 150.0, 50.0, 5.0)

# ==========================================
# LIVE RENDER ENGINE (Fragmented loop)
# ==========================================
@st.fragment(run_every=0.1)
def render_live_dashboard():
    # Generate dynamic load variation based on time
    t = time.time()
    if load_type == "Oscillating Dynamic Load":
        dynamic_load = base_load * (1 + 0.6 * np.sin(t * 3))
    else:
        dynamic_load = base_load + float(np.random.uniform(-1.5, 1.5))

    # Physics Calculations
    E_Pa = elasticity * 1e9
    I_m4 = inertia * 1e-6
    EI = E_Pa * I_m4
    x_points = np.linspace(0, length, 200)
    deflection = np.zeros_like(x_points)
    load_N = dynamic_load * 1000

    if beam_type == "Cantilever (Fixed-Free)":
        deflection = (load_N * (x_points**2) * (3 * length - x_points)) / (6 * EI)
    else:
        half_L = length / 2
        for idx, x_val in enumerate(x_points):
            if x_val <= half_L:
                deflection[idx] = (load_N * x_val * (3 * length**2 - 4 * x_val**2)) / (48 * EI)
            else:
                deflection[idx] = (load_N * (length - x_val) * (3 * length**2 - 4 * (length - x_val)**2)) / (48 * EI)
    
    deflection_mm = deflection * 1000
    max_deflection = np.max(deflection_mm)
    safety_limit = (length * 1000) / 250
    
    safety_status = "SAFE" if max_deflection < safety_limit else "CRITICAL RISK"
    status_color = "#00f2fe" if safety_status == "SAFE" else "#ff4b4b"

    # Display Metrics Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Current Load", f"{dynamic_load:.2f} kN")
    m_col2.metric("Max Deflection", f"{max_deflection:.2f} mm")
    m_col3.metric("Allowed Limit", f"{safety_limit:.2f} mm")
    m_col4.metric("Safety Assessment", safety_status, delta="Ok" if safety_status == "SAFE" else "Danger", delta_color="normal" if safety_status == "SAFE" else "inverse")

    # Render Plotly Graphics
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_points, y=np.zeros_like(x_points), mode='lines', name='Original Axis', line=dict(color='rgba(255,255,255,0.15)', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=x_points, y=-deflection_mm, mode='lines', name='Deflected Profile', line=dict(color=status_color, width=6), fill='tozeroy', fillcolor=f
