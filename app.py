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

# Team Members Display Box using pure Markdown (No HTML)
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
# SIDEBAR CONTROLS (Live Inputs)
# ==========================================
st.sidebar.header("🏗️ Structural Parameters")

beam_type = st.sidebar.selectbox(
    "Beam Configuration", 
    ["Cantilever (Fixed-Free)", "Simply Supported (Pinned-Pinned)"]
)

length = st.sidebar.slider("Beam Length (L) [meters]", 2.0, 15.0, 8.0, 0.5)
elasticity = st.sidebar.slider("Elastic Modulus (E) [GPa]", 10, 210, 200, step=10)
inertia = st.sidebar.slider("Moment of Inertia (I) [10⁻⁶ m⁴]", 10, 500, 150, step=10)

st.sidebar.header("⚖️ Dynamic Loading")
load_type = st.sidebar.radio("Load Condition", ["Point Load at Center/Tip", "Oscillating Dynamic Load"])
base_load = st.sidebar.slider("Load Magnitude (P) [kN]", 5.0, 150.0, 50.0, 5.0)

# Real-time animation control toggle
run_live_feed = st.sidebar.toggle("🟢 Activate Live Sensor Feed", value=True)

# ==========================================
# PHYSICS & CALCULATIONS ENGINE
# ==========================================
E_Pa = elasticity * 1e9
I_m4 = inertia * 1e-6
L_m = length

def get_deflection_curve(x, P_N, beam_type):
    y = np.zeros_like(x)
    EI = E_Pa * I_m4
    
    if beam_type == "Cantilever (Fixed-Free)":
        # y = (P * x^2 * (3L - x)) / (6EI)
        y = (P_N * (x**2) * (3 * L_m - x)) / (6 * EI)
    else: 
        # Pinned-pinned mid-span loading
        half_L = L_m / 2
        for idx, x_val in enumerate(x):
            if x_val <= half_L:
                y[idx] = (P_N * x_val * (3 * L_m**2 - 4 * x_val**2)) / (48 * EI)
            else:
                x_sym = L_m - x_val
                y[idx] = (P_N * x_sym * (3 * L_m**2 - 4 * x_sym**2)) / (48 * EI)
    return y * 1000 # Convert to mm

# ==========================================
# LIVE DASHBOARD APP LOOP
# ==========================================
x_points = np.linspace(0, L_m, 200)

# Layout slots for real-time updates
metric_slot = st.empty()
chart_slot = st.empty()

SAFETY_LIMIT_MM = (L_m * 1000) / 250

iteration = 0
while True:
    if run_live_feed:
        iteration += 1
        if load_type == "Oscillating Dynamic Load":
            dynamic_load = base_load * (1 + 0.6 * np.sin(iteration * 0.2))
        else:
            dynamic_load = base_load + np.random.uniform(-2.5, 2.5)
    else:
        dynamic_load = base_load

    load_N = dynamic_load * 1000
    deflection = get_
