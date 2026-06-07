import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. EXPANDED PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="ICT for Structural Safety: Advanced Beam Analyzer",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed" # Collapsed to maximize widescreen layout
)

# Enforce clean dark layout presets for presentation graphics
plt.style.use('dark_background')

# ==========================================
# 2. HERO HEADER & HIGH-WIDE TEAM BOARD
# ==========================================
st.title("🏗️ ICT for Structural Safety")
st.subheader("Widescreen Live Beam Deflection Visualizer & Analytical Engine")

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
# 3. INITIAL SELECTION & MEMORY STATE
# ==========================================
# Hidden or default values initialized cleanly to avoid string parsing dropouts
if 'dummy' not in st.session_state:
    st.session_state['dummy'] = True

# ==========================================
# 4. PHYSICS ENGINE PRE-PROCESSING
# ==========================================
# Setup default or layout placeholder properties prior to lower input cards
x_len = 10.0
P_force = 5000.0
E_mod = 2.0e11
I_inertia = 0.0005

# ==========================================
# 5. DUAL-ZONE RENDER: TOP VISUALIZER REGION
# ==========================================
# Create dynamic tracking vectors
x_coord = np.linspace(0, x_len, 300)
y_disp = np.zeros_like(x_coord)
half_span = x_len / 2

# Calculate exact elastic line curve deflection points
delta_calc = (P_force * x_len**3) / (48 * E_mod * I_inertia)

for idx, current_x in enumerate(x_coord):
    if current_x <= half_span:
        y_disp[idx] = -(P_force * current_x * (3 * x_len**2 - 4 * current_x**2)) / (48 * E_mod * I_inertia)
    else:
        symmetric_x = x_len - current_x
        y_disp[idx] = -(P_force * symmetric_x * (3 * x_len**2 - 4 * symmetric_x**2)) / (48 * E_mod * I_inertia)

# Display real-time telemetry panels up top
m1, m2, m3, m4 = st.columns(4)
m1.metric("Max Deflection", f"{delta_calc * 1000:.3f} mm")
m2.metric("Total Span (L)", f"{x_len:.1f} meters")
m3.metric("Applied Load Force", f"{P_force:.0f} N")
m4.metric("Flexural Rigidity (EI)", f"{E_mod * I_inertia:.2e} N-m2")

st.write("")

# Construct scientific matplotlib workspace
fig, ax = plt.subplots(figsize=(14, 4.5))

# Plot undeflected baseline and structural deflection curves
ax.plot(x_coord, np.zeros_like(x_coord), color='#475569', linestyle='--', alpha=0.5, label='Undeflected Axis')
ax.plot(x_coord, y_disp * 1000, color='#38bdf8', linewidth=5, label='Elastic Line Curvature')
ax.fill_between(x_coord, y_disp * 1000, 0, color='#38bdf8', alpha=0.08)

# Render pinning reactions visually using heavy triangular markers
ax.scatter([0, x_len], [0, 0], color='#f59e0b', s=250, marker='^', choose_zorder=5)

# Generate custom vector arrow force overlay
ax.annotate(
    f"Force Vector P: {P_force:.0f} N", 
    xy=(x_len/2, np.min(y_disp)*1000), 
    xytext=(x_len/2, np.min(y_disp)*1000 + (delta_calc*1000*0.4) + 6),
    arrowprops=dict(facecolor='#f59e0b', shrink=0.08, width=
