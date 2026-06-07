import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# ------------------------------------------
# 1. PAGE CONFIGURATION
# ------------------------------------------
st.set_page_config(
    page_title="ICT for Structural Safety: Live Beam Deflection Visualizer",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set high-end dark background theme for engineering plots
plt.style.use('dark_background')

# ------------------------------------------
# 2. HERO HEADER & TEAM CREDITS
# ------------------------------------------
st.title("🏗️ ICT for Structural Safety")
st.subheader("Live Beam Deflection Visualizer & Risk Monitor")

# Team Members Panel - Pure Markdown & Native Containers
with st.container(border=True):
    st.markdown("### 👥 PROJECT DEVELOPED BY TEAM:")
    
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

# ------------------------------------------
# 3. SIDEBAR CONTROLS
# ------------------------------------------
st.sidebar.header("🔧 Structural Parameters")

L = st.sidebar.slider("Beam Length (L) [m]", 1.0, 20.0, 10.0, step=0.5)
P_base = st.sidebar.slider("Static Point Load (P) [N]", 100.0, 10000.0, 2000.0, step=100.0)
E = st.sidebar.slider("Young's Modulus (E) [Pa]", 1e9, 2.5e11, 2.0e11, format="%e")
I = st.sidebar.slider("Moment of Inertia (I) [m⁴]", 0.000001, 0.01, 0.0005, format="%.6f")

st.sidebar.header("⚡ Live Simulation Settings")
run_vibration = st.sidebar.toggle("Deformation Vibration Loop", value=True)

# ------------------------------------------
# 4. ENGINEERING THEORY
# ------------------------------------------
with st.container(border=True):
    st.markdown("### 📘 Structural Engineering Theory")
    st.markdown(
        "For a **Simply Supported Beam** subjected to a concentrated central point load, "
        "the exact structural deflection curve can be mapped using Euler-Bernoulli beam theory equations."
    )
    
    col_theory_1, col_theory_2 = st.columns(2)
    with col_theory_1:
        st.latex(r"\delta_{max} = \frac{P \cdot L^3}{48 \cdot E \cdot I}")
    with col_theory_2:
        st.markdown(
            "- **P** = Applied Concentrated Force $(N)$\n"
            "- **L** = Total Span Length $(m)$\n"
            "- **E** = Material Modulus of Elasticity $(Pa)$\n"
            "- **I** = Cross-Sectional Area Moment of Inertia $(m^4)$"
        )

st.write("")

# ------------------------------------------
# 5. LIVE CALCULATIONS & GRAPHICS ANIMATION
# ------------------------------------------
x = np.linspace(0, L, 300)

# Layout structural placeholders for high-speed dynamic execution
metric_slot = st.empty()
plot_slot = st.empty()
safety_slot = st.empty()

# Run rendering sequence loop
iteration = 0
while True:
    # Introduce real-time harmonic environmental oscillation (e.g., wind/traffic)
    if run_vibration:
        iteration += 1
        vibration_factor = 1 + 0.15 * np.sin(iteration * 0.4)
        P_dynamic = P_base * vibration_factor
    else:
        P_dynamic = P_base

    # Accurate Physics Deflection Calculations
    delta_max = (P_dynamic * L**3) / (48 * E * I)
    
    # Exact elastic deflection profile modeling curve
    # Using structural elastic boundary function: (P*x / 48*E*I) * (3*L^2 - 4*x^2) for half span
    y = np.zeros_like(x)
    half_L = L / 2
    for idx, x_val in enumerate(x):
        if x_val <= half_L:
            y[idx] = -(P_dynamic * x_val * (3 * L**2 - 4 * x_val**2)) / (48 * E * I)
        else:
            x_sym = L - x_val
            y[idx] = -(P_dynamic * x_sym * (3 * L**2 - 4 * x_sym**2)) / (48 * E * I)

    # 1. Output Live Metrics Row
    with metric_slot.container():
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Max Deflection", f"{delta_max * 1000:.3f} mm")
        c2.metric("Dynamic Load Force", f"{P_dynamic:.1f} N")
        c3.metric("Beam Total Span", f"{L:.1f} m")
        c4.metric("Stiffness Factor (EI)", f"{E*I:.2e} N·m²")

    # 2. Output High-Contrast Cyberpunk Graphic Plot
    fig, ax = plt.subplots(figsize=(11, 4))
    
    # Draw reference ground axis line
    ax.plot(x, np.zeros_like(x), color='gray', linestyle='--', alpha=0.5, label='Undeflected Axis')
    
    # Plot live deformation line
    ax.plot(x, y * 1000, color='#38bdf8', linewidth=4, label='Deformed Profile')
    ax.fill_between(x, y * 1000, 0, color='#38bdf8', alpha=0.12)
    
    # Add pinning structural indicators at ends
    ax.scatter([0, L], [0, 0], color='#f59e0b', s=180, marker='^', zorder=5, label='Pin Support')
    
    # Add dynamic force vector vector graphic
    ax.annotate(
        f"P = {P_dynamic:.0f} N", 
        xy=(L/2, np.min(y)*1000), 
        xytext=(L/2, np.min(y)*1000 + (delta_max*1000*0.4) + 5),
        arrowprops=dict(facecolor='#f59e0b', shrink=0.08, width=2, headwidth=8),
        ha='center', color='#f59e0b', weight='bold'
    )
    
    ax.set_title("Live Structural Deflection Elastic Curve Profile", color='white', fontsize=12, pad=12)
    ax.set_xlabel("Beam Length Coordinate (meters)", color='#94a3b8')
    ax.set_ylabel("Displacement (mm)", color='#94a3b8')
    ax.grid(True, linestyle=':', alpha=0.2, color='white')
    
    # Dynamic constraint adjustments to lock scales smoothly during cycles
    max_bound = max(delta_max * 1000 * 1.8, 10)
    ax.set_ylim(-max_bound, max_bound * 0.4)
    ax.set_xlim(-0.5, L + 0.5)

    with plot_slot.container():
        st.pyplot(fig)
        plt.close(fig) # Prevent server RAM leaks

    # 3. Output Real-Time Structural Assessment System
    with safety_slot.container():
        st.markdown("### 🚨 Structural Safety Status Evaluation")
        if delta_max < 0.005:
            st.success("✅ SAFE: Calculated internal strain deformation parameters are well within allowable design tolerances.")
        elif delta_max < 0.02:
            st.warning("⚠️ WARNING STATUS: Structural displacement levels approaching serviceability state criteria limit. Continuous health check monitoring required.")
        else:
            st.error("❌ CRITICAL DEFLECTION HAZARD: Severe displacement threshold breached. Immediate threat to structure load bearing path.")

    # Control timing interval loop sequence
    if run_vibration:
        time.sleep(0.05)
    else:
        st.stop()
