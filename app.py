import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# Safe optional import for PDF
try:
    from reportlab.pdfgen import canvas
    pdf_available = True
except:
    pdf_available = False

# =========================
# PAGE SETUP
# =========================
st.set_page_config(page_title="Ultimate Beam Analyzer", layout="wide")
plt.style.use('dark_background')

# =========================
# BACKGROUND STYLE
# =========================
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1503387762-592deb58ef4e");
    background-size: cover;
}
.block-container {
    background: rgba(0,0,0,0.75);
    padding: 2rem;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏗️ Ultimate Structural Beam Analyzer")

# =========================
# SIDEBAR INPUTS
# =========================
with st.sidebar:
    st.header("⚙ Inputs")

    L = st.slider("Length (m)", 1.0, 20.0, 10.0)

    load_type = st.selectbox("Load Type", ["Point Load", "UDL", "Triangular"])

    if load_type == "Point Load":
        P = st.slider("Point Load (N)", 100.0, 15000.0, 5000.0)
        w = 0
    else:
        w = st.slider("Load (N/m)", 10.0, 5000.0, 500.0)
        P = 0

    material = st.selectbox("Material", ["Steel", "Aluminum", "Concrete"])

    if material == "Steel":
        E = 2e11
        allowable = 250e6
    elif material == "Aluminum":
        E = 7e10
        allowable = 150e6
    else:
        E = 3e10
        allowable = 40e6

    st.subheader("📐 Cross Section")

    shape = st.selectbox("Shape", ["Rectangular", "Circular"])

    if shape == "Rectangular":
        b = st.number_input("Width (m)", value=0.3)
        h = st.number_input("Height (m)", value=0.6)
        I = (b * h**3) / 12
        c = h / 2
    else:
        d = st.number_input("Diameter (m)", value=0.5)
        I = (np.pi * d**4) / 64
        c = d / 2

# =========================
# CALCULATIONS
# =========================
x = np.linspace(0, L, 200)

if load_type == "Point Load":
    delta_max = (P * L**3) / (48 * E * I)
    y = (P * x * (3 * L**2 - 4 * x**2)) / (48 * E * I)
    M_max = (P * L) / 4

elif load_type == "UDL":
    delta_max = (5 * w * L**4) / (384 * E * I)
    y = (w * x * (L**3 - 2 * L * x**2 + x**3)) / (24 * E * I)
    M_max = (w * L**2) / 8

else:  # Triangular
    delta_max = (w * L**4) / (30 * E * I)
    y = (w * x * (L - x)**3) / (30 * E * I)
    M_max = (w * L**2) / 6

y = -y  # downward deflection

sigma = (M_max * c) / I
FS = allowable / sigma if sigma != 0 else 0

# =========================
# RESULTS
# =========================
st.markdown("### 📊 Results")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Max Deflection (mm)", f"{delta_max*1000:.2f}")
c2.metric("Max Moment (Nm)", f"{M_max:.2f}")
c3.metric("Stress (MPa)", f"{sigma/1e6:.2f}")
c4.metric("Factor of Safety", f"{FS:.2f}")

# =========================
# DEFLECTION PLOT
# =========================
st.markdown("### 📉 Deflection")

fig, ax = plt.subplots()
ax.plot(x, y * 1000, linewidth=3)
ax.axhline(0, linestyle='--')
ax.set_xlabel("Length (m)")
ax.set_ylabel("Deflection (mm)")
ax.grid(True)

st.pyplot(fig)
plt.close(fig)

# =========================
# 3D STYLE VIEW
# =========================
st.markdown("### 🧊 Beam Visualization")

fig2, ax2 = plt.subplots()
ax2.plot(x, np.zeros_like(x), linewidth=8)
ax2.plot(x, y * 200, linewidth=2)
ax2.set_title("3D Style")
ax2.axis('off')

st.pyplot(fig2)
plt.close(fig2)

# =========================
# ANIMATION
# =========================
st.markdown("### 🎬 Animation")

if st.checkbox("Play Animation"):
    placeholder = st.empty()
    for scale in np.linspace(0, 1, 15):
        fig_anim, ax_anim = plt.subplots()
        ax_anim.plot(x, y * scale * 1000)
        ax_anim.set_ylim(min(y)*1000, 10)
        placeholder.pyplot(fig_anim)
        plt.close(fig_anim)
        time.sleep(0.05)

# =========================
# SAFETY
# =========================
st.markdown("### ⚠ Safety Check")

if FS > 2:
    st.success("✅ SAFE DESIGN")
elif FS > 1:
    st.warning("⚠ Moderate Safety")
else:
    st.error("❌ FAILURE RISK")

# =========================
# PDF EXPORT (SAFE)
# =========================
st.markdown("### 📄 Export Report")

if pdf_available:
    def create_pdf():
        file_path = "report.pdf"
        c_pdf = canvas.Canvas(file_path)
        c_pdf.drawString(100, 800, "Beam Report")
        c_pdf.drawString(100, 770, f"Length: {L} m")
        c_pdf.drawString(100, 750, f"Deflection: {delta_max:.6f} m")
        c_pdf.drawString(100, 730, f"Stress: {sigma:.2f} Pa")
        c_pdf.drawString(100, 710, f"FOS: {FS:.2f}")
        c_pdf.save()
        return file_path

    if st.button("Generate PDF"):
        pdf_path = create_pdf()
        with open(pdf_path, "rb") as f:
            st.download_button("⬇ Download PDF", f, "beam_report.pdf")

else:
    st.warning("Install 'reportlab' to enable PDF export.")



