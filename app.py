import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# Optional PDF
try:
    from reportlab.pdfgen import canvas
    pdf_available = True
except:
    pdf_available = False

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Beam Deflection Visualizer", layout="wide")

# =========================
# MODERN STYLE
# =========================
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}

/* Glass cards */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 15px;
    backdrop-filter: blur(10px);
}

/* Team cards */
.team-card {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    transition: 0.3s;
}
.team-card:hover {
    background: rgba(56,189,248,0.2);
    transform: scale(1.05);
}

/* Titles */
h1, h2, h3 {
    color: #38bdf8;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.title("🏗️ Beam Deflection Visualizer")
st.subheader("📘 ICT for Structural Safety")

# =========================
# TEAM SECTION
# =========================
st.markdown("### 👥 Project Team")

cols = st.columns(5)

team = [
    ("Abdul Mannan", "25-ME-55"),
    ("Muhammad bin Akarma", "25-ME-59"),
    ("Muneeb Azhar", "25-ME-27"),
    ("Ahmed Ali", "25-ME-115"),
    ("Hammad Fida", "25-ME-03"),
]

for i, (name, reg) in enumerate(team):
    with cols[i]:
        st.markdown(f"""
        <div class="team-card">
        <h4>{name}</h4>
        <p>{reg}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# =========================
# SIDEBAR INPUTS
# =========================
with st.sidebar:
    st.header("⚙️ Input Parameters")

    L = st.slider("Beam Length (m)", 1.0, 20.0, 10.0)

    load_type = st.selectbox("Load Type", ["Point Load", "UDL", "Triangular"])

    if load_type == "Point Load":
        P = st.slider("Load (N)", 100.0, 15000.0, 5000.0)
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

    b = st.number_input("Width (m)", 0.1, 2.0, 0.3)
    h = st.number_input("Height (m)", 0.1, 2.0, 0.6)

    I = (b * h**3) / 12
    c = h / 2

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

else:
    delta_max = (w * L**4) / (30 * E * I)
    y = (w * x * (L - x)**3) / (30 * E * I)
    M_max = (w * L**2) / 6

# Downward deflection
y = -y

sigma = (M_max * c) / I
FS = allowable / sigma if sigma != 0 else 0

# =========================
# RESULTS
# =========================
st.markdown("### 📊 Structural Results")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Deflection", f"{delta_max*1000:.2f} mm")
c2.metric("Moment", f"{M_max:.2f} Nm")
c3.metric("Stress", f"{sigma/1e6:.2f} MPa")
c4.metric("Factor of Safety", f"{FS:.2f}")

# =========================
# GRAPH
# =========================
st.markdown("### 📉 Deflection Curve")

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(x, y * 1000, color='#38bdf8', linewidth=3)
ax.fill_between(x, y * 1000, 0, color='#38bdf8', alpha=0.15)
ax.axhline(0, linestyle='--', color='gray')

ax.set_xlabel("Beam Length (m)")
ax.set_ylabel("Deflection (mm)")
ax.set_title("Beam Deflection Profile")
ax.grid(True, alpha=0.3)

st.pyplot(fig)
plt.close(fig)

# =========================
# ANIMATION
# =========================
st.markdown("### 🎬 Deformation Animation")

if st.checkbox("Start Animation"):
    placeholder = st.empty()
    for scale in np.linspace(0, 1, 15):
        fig2, ax2 = plt.subplots()
        ax2.plot(x, y * scale * 1000, color='cyan')
        ax2.set_ylim(min(y)*1000, 10)
        ax2.set_title("Dynamic Deflection")
        placeholder.pyplot(fig2)
        plt.close(fig2)
        time.sleep(0.05)

# =========================
# SAFETY CHECK
# =========================
st.markdown("### ⚠️ Safety Status")

if FS > 2:
    st.success("✅ SAFE STRUCTURE")
elif FS > 1:
    st.warning("⚠️ NEEDS OPTIMIZATION")
else:
    st.error("❌ FAILURE RISK")

# =========================
# PDF EXPORT
# =========================
st.markdown("### 📄 Generate Report")

if pdf_available:

    def create_pdf():
        path = "beam_report.pdf"
        c_pdf = canvas.Canvas(path)

        c_pdf.drawString(100, 800, "Beam Deflection Report")
        c_pdf.drawString(100, 770, f"Length: {L} m")
        c_pdf.drawString(100, 750, f"Deflection: {delta_max:.6f} m")
        c_pdf.drawString(100, 730, f"Stress: {sigma:.2f} Pa")
        c_pdf.drawString(100, 710, f"Factor of Safety: {FS:.2f}")

        c_pdf.save()
        return path

    if st.button("📥 Generate PDF Report"):
        pdf = create_pdf()

        with open(pdf, "rb") as f:
            st.download_button("⬇ Download PDF", f, "beam_report.pdf")

else:
    st.warning("Install 'reportlab' to enable PDF export")



