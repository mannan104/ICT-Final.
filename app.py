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
    delta_max = (P * L**3) / (48 * E * I)
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
        <div class='metric-value'>{delta_max*1000:.2f} mm</div>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>⚡ Max Bending Moment</div>
        <div class='metric-value'>{M_max/1000:.2f} kN·m</div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>💥 Max Flexural Stress</div>
        <div class='metric-value'>{max_bending_stress/1e6:.2f} MPa</div>
    </div>""", unsafe_allow_html=True)
with m4:
    fos_color = "#4ade80" if fos >= 2.0 else "#fbbf24" if fos >= 1.0 else "#f87171"
    fos_display = f"{fos:.2f}" if fos != float('inf') else "N/A"
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>🛡️ Factor of Safety</div>
        <div class='metric-value' style='color:{fos_color};'>{fos_display}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if fos >= 2.0:
    st.success(f"✅ **STRUCTURALLY VALID SIGNATURE**: Bending stress stays safely below limit constraints for {material}. System meets industrial code margins.")
elif 1.0 <= fos < 2.0:
    st.warning("⚠️ **MARGINAL REGIME**: The layout is functional but dangerous under fluctuating loading conditions. Recommendation: Increase cross-section depth ($h$).")
else:
    st.error("🚨 **STRUCTURAL PLASTIC COLLAPSE**: Allowable material parameters breached. Immediate elastic structural catastrophic failure indicated.")

# ==========================================
# 6. GRAPHICS & CURVE PLOTS
# ==========================================
st.markdown("### 📉 Elastic Curve Simulation")

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 4.5))
fig.patch.set_facecolor('#020617')
ax.set_facecolor('#0f172a')

ax.plot(x, y_deflected * 1000, color="#38bdf8", linewidth=3.5, label="Deformed Beam Axis")
ax.fill_between(x, y_deflected * 1000, 0, color="#38bdf8", alpha=0.08)
ax.axhline(0, color="#64748b", linestyle='--', linewidth=1.2, label="Undeformed Structural Horizon")

ax.set_xlabel("Linear Position along Beam Span (x, meters)", color="#94a3b8", fontsize=10)
ax.set_ylabel("Deflection Delta (y, millimeters)", color="#94a3b8", fontsize=10)
ax.grid(True, color="#1e293b", linestyle=':', alpha=0.6)
ax.tick_params(colors='#94a3b8', labelsize=9)
ax.legend(loc="lower left", framealpha=0.9, facecolor="#0f172a", edgecolor="#1e293b")
ax.set_title(f"Elastic Response Profile under {load_type}", color="#38bdf8", fontsize=11, pad=12)

st.pyplot(fig)
plt.close(fig)

# ==========================================
# 7. LOAD STEP PROGRESSION ANIMATION
# ==========================================
with st.expander("🎬 Execute Dynamic Load Application Sequence"):
    if st.button("Initiate Progressive Strain Simulation"):
        frame_slot = st.empty()
        time_steps = np.sin(np.linspace(0, np.pi/2, 16))
        
        for scalar in time_steps:
            fig_dyn, ax_dyn = plt.subplots(figsize=(12, 4.5))
            fig_dyn.patch.set_facecolor('#020617')
            ax_dyn.set_facecolor('#0f172a')
            
            ax_dyn.plot(x, y_deflected * scalar * 1000, color="#f43f5e", linewidth=3.5, label="Transient Elastic Deformation")
            ax_dyn.fill_between(x, y_deflected * scalar * 1000, 0, color="#f43f5e", alpha=0.06)
            ax_dyn.axhline(0, color="#64748b", linestyle='--', linewidth=1.2)
            
            ax_dyn.set_ylim(min(y_deflected) * 1150 - 2, 5)
            ax_dyn.set_xlabel("Linear Position along Beam Span (m)", color="#94a3b8")
            ax_dyn.set_ylabel("Deflection (mm)", color="#94a3b8")
            ax_dyn.grid(True, color="#1e293b", linestyle=':')
            ax_dyn.tick_params(colors='#94a3b8')
            ax_dyn.legend(loc="lower left", facecolor="#0f172a", edgecolor="#1e293b")
            
            frame_slot.pyplot(fig_dyn)
            plt.close(fig_dyn)
            time.sleep(0.05)

# ==========================================
# 8. AUTOMATED ENGINEERING REPORT EXPORT
# ==========================================
st.markdown("### 📄 Quality Management Reporting")

if PDF_OK:
    def build_pdf_document():
        pdf_buffer = io.BytesIO()
        pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)
        
        pdf_canvas.setFont("Helvetica-Bold", 18)
        pdf_canvas.drawString(50, 750, "Structural Verification & Stress Audit Report")
        pdf_canvas.setFont("Helvetica", 9)
        pdf_canvas.setFillColorRGB(0.4, 0.4, 0.4)
        pdf_canvas.drawString(50, 735, f"Automated Engineering Run System Trace • Generated: {time.strftime('%b %d, %Y | %H:%M:%S')}")
        pdf_canvas.line(50, 725, 560, 725)
        
        pdf_canvas.setFillColorRGB(0.1, 0.1, 0.1)
        pdf_canvas.setFont("Helvetica-Bold", 12)
        pdf_canvas.drawString(50, 695, "1. Design Space Boundaries")
        pdf_canvas.setFont("Helvetica", 10)
        pdf_canvas.drawString(70, 675, f"Structural Target Span Length (L): {L:.2f} meters")
        pdf_canvas.drawString(70, 655, f"Material Specification: {material} (E = {E/1e9:.1f} GPa)")
        pdf_canvas.drawString(70, 635, f"Geometric Cross-Section Profile: {b*1000:.0f}mm wide × {h*1000:.0f}mm high")
        pdf_canvas.drawString(70, 615, f"Calculated Moment of Inertia (I): {I:.6e} m⁴")
        
        pdf_canvas.setFont("Helvetica-Bold", 12)
        pdf_canvas.drawString(50, 575, "2. Analytical Mechanics Calculations")
        pdf_canvas.setFont("Helvetica", 10)
        pdf_canvas.drawString(70, 555, f"Load Profile Layout Configured: {load_type}")
        pdf_canvas.drawString(70, 535, f"Calculated Max Elastic Deflection Boundary: {delta_max*1000:.3f} mm")
        pdf_canvas.drawString(70, 515, f"Induced Internal Bending Moment Vector (M_max): {M_max/1000:.2f} kN·m")
        pdf_canvas.drawString(70, 495, f"Calculated Extreme Fiber Bending Stress: {max_bending_stress/1e6:.2f} MPa")
        
        pdf_canvas.setFont("Helvetica-Bold", 12)
        pdf_canvas.drawString(50, 455, "3. Safety & Compliance Verdict")
        pdf_canvas.setFont("Helvetica-Bold", 11)
        if fos >= 2.0:
            pdf_canvas.setFillColorRGB(0.0, 0.5, 0.0)
            pdf_canvas.drawString(70, 435, f"VERDICT: PASSED (Design Margin Factor FOS = {fos:.2f})")
        elif fos >= 1.0:
            pdf_canvas.setFillColorRGB(0.6, 0.4, 0.0)
            pdf_canvas.drawString(70, 435, f"VERDICT: MARGINAL COMPLIANCE (Design Margin Factor FOS = {fos:.2f})")
        else:
            pdf_canvas.setFillColorRGB(0.8, 0.0, 0.0)
            pdf_canvas.drawString(70, 435, f"VERDICT: CRITICAL INSIGNIA STRUCTURAL FAILURE (FOS = {fos:.2f})")
            
        pdf_canvas.showPage()
        pdf_canvas.save()
        pdf_buffer.seek(0)
        return pdf_buffer

    report_stream = build_pdf_document()
    st.download_button(
        label="📥 Export Certified Engineering Report (PDF)",
        data=report_stream,
        file_name=f"Beam_Deflection_Report_{int(time.time())}.pdf",
        mime="application/pdf"
    )
else:
    st.info("💡 Reportlab generation suite uninitialized. Add `reportlab` to requirements workspace dependencies setup to build automation print exports.")

st.markdown("<div class='project-footer'>💡 Design built with Streamlit Cloud Server Workspace Framework. Project version 2.1.0</div>", unsafe_allow_html=True)
