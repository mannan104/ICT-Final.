import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# Optional PDF
try:
    from reportlab.pdfgen import canvas
    PDF_OK = True
except:
    PDF_OK = False

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Beam Deflection", layout="wide")

# =========================
# SIMPLE CLEAN STYLE
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #020617;
    color: white;
}

.block-container {
    max-width: 1100px;
    margin: auto;
}

h1 {
    text-align: center;
    color: #38bdf8;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.title("🏗️ Beam Deflection Visualizer")
st.markdown("<p style='text-align:center;'>ICT for Structural Safety</p>", unsafe_allow_html=True)

# =========================
# TEAM SECTION
# =========================
st.markdown("### 👥 Project Team")

col1, col2, col3, col4, col5 = st.columns(5)

col1.markdown("**Abdul Mannan**  \n25-ME-55")
col2.markdown("**Muhammad bin Akarma**  \n25-ME-59")
col3.markdown("**Muneeb Azhar**  \n25-ME-27")
col4.markdown("**Ahmed Ali**  \n25-ME-115")
col5.markdown("**Hammad Fida**  \n25-ME-03")

st.divider()

# =========================
# SIDEBAR INPUT
# =========================
with st.sidebar:
    st.header("⚙️ Inputs")

    L = st.slider("Length (m)", 1.0, 20.0, 10.0)

    load = st.selectbox("Load Type", ["Point", "UDL", "Triangular"])

    if load == "Point":
        P = st.slider("Load (N)", 100.0, 15000.0, 5000.0)
        w = 0
    else:
        w = st.slider("Load (N/m)", 10.0, 5000.0, 500.0)
        P = 0

    material = st.selectbox("Material", ["Steel", "Aluminum", "Concrete"])

    if material == "Steel":
        E = 2e11
        allow = 250e6
    elif material == "Aluminum":
        E = 7e10
        allow = 150e6
    else:
        E = 3e10
        allow = 40e6

    st.markdown("### Section")

    b = st.number_input("Width (m)", 0.1, 2.0, 0.3)
    h = st.number_input("Height (m)", 0.1, 2.0, 0.6)

    I = (b * h**3) / 12
    c = h / 2

# =========================
# CALCULATIONS
# =========================
x = np.linspace(0, L, 200)

if load == "Point":
    delta = (P * L**3) / (48 * E * I)
    y = (P * x * (3*L**2 - 4*x**2)) / (48 * E * I)
    M = (P * L) / 4

elif load == "UDL":
    delta = (5*w*L**4) / (384 * E * I)
    y = (w * x * (L**3 - 2*L*x**2 + x**3)) / (24 * E * I)
    M = (w * L**2) / 8

else:
    delta = (w * L**4) / (30 * E * I)
    y = (w * x * (L - x)**3) / (30 * E * I)
    M = (w * L**2) / 6

y = -y
stress = (M * c) / I
FS = allow / stress if stress != 0 else 0

# =========================
# RESULTS
# =========================
st.markdown("### 📊 Results")

r1, r2, r3, r4 = st.columns(4)
r1.metric("Deflection (mm)", f"{delta*1000:.2f}")
r2.metric("Moment (Nm)", f"{M:.2f}")
r3.metric("Stress (MPa)", f"{stress/1e6:.2f}")
r4.metric("FOS", f"{FS:.2f}")

# =========================
# GRAPH
# =========================
st.markdown("### 📉 Deflection Curve")

fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(x, y*1000, color="#38bdf8", linewidth=3)
ax.fill_between(x, y*1000, 0, alpha=0.1)
ax.axhline(0, linestyle='--')

ax.set_xlabel("Length (m)")
ax.set_ylabel("Deflection (mm)")
ax.grid(True)

st.pyplot(fig)
plt.close(fig)

# =========================
# ANIMATION
# =========================
with st.expander("🎬 Animation"):
    if st.button("Play"):
        placeholder = st.empty()
        for s in np.linspace(0, 1, 10):
            fig2, ax2 = plt.subplots()
            ax2.plot(x, y*s*1000)
            ax2.set_ylim(min(y)*1000, 10)
            placeholder.pyplot(fig2)
            plt.close(fig2)
            time.sleep(0.05)

# =========================
# SAFETY
# =========================
st.markdown("### ⚠️ Safety")

if FS > 2:
    st.success("SAFE")
elif FS > 1:
    st.warning("MODERATE")
else:
    st.error("UNSAFE")

# =========================
# PDF REPORT
# =========================
st.markdown("### 📄 Report")

if PDF_OK:
    def make_pdf():
        file = "report.pdf"
        c_pdf = canvas.Canvas(file)
        c_pdf.drawString(100, 800, "Beam Report")
        c_pdf.drawString(100, 770, f"Length: {L}")
        c_pdf.drawString(100, 750, f"Deflection: {delta}")
        c_pdf.drawString(100, 730, f"Stress: {stress}")
        c_pdf.save()
        return file

    if st.button("Generate PDF"):
        pdf = make_pdf()
        with open(pdf, "rb") as f:
            st.download_button("Download PDF", f, "report.pdf")
else:
    st.info("Install reportlab for PDF feature")


