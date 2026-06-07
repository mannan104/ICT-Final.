import streamlit as stimport stream numpy as np
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
st.set_page_config(
    page_title="Beam Deflection Visualizer",
    layout="wide"
)

# =========================
# CLEAN MODERN STYLE
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0b1220, #020617);
    color: white;
}

/* Center content width */
.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

/* Metrics */
[data-testid="metric-container"] {
    background: #0f172a;
    border-radius: 10px;
    padding: 15px;
    border-left: 4px solid #38bdf8;
}

/* Titles */
h1 {
    text-align: center;
    color: #38bdf8;
}

h2, h3 {
    color: #e2e8f0;
}

/* Divider spacing */
hr {
    margin-top: 20px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER (CENTERED CLEAN)
# =========================
st.title("🏗️ Beam Deflection Visualizer")
st.markdown(
    "<p style='text-align:center;'>ICT for Structural Safety</p>",
    unsafe_allow_html=True
)

# =========================
# TEAM (SIMPLE + CLEAN)
# =========================
st.markdown("### 👥 Project Team")

team_cols = st.columns(5)
team = [
    ("Abdul Mannan", "25-ME-55"),
    ("Muhammad bin Akarma", "25-ME-59"),
    ("Muneeb Azhar", "25-ME-27"),
    ("Ahmed Ali", "25-ME-115"),
    ("Hammad Fida", "25-ME-03")
]

for i, (name, reg) in enumerate(team):
    with team_cols[i]:
        st.markdown(f"""
        <div style="text-align:center; 
                    border:1px solid #1e293b; 
                    padding:10px; 
                    border-radius:8px;">
        <b>{name}</b><br>
        <small>{reg}</small>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# =========================
# SIDEBAR INPUTS (CLEAN)
# =========================
with st.sidebar:
    st.header("⚙️ Inputs")

    L = st.slider("Length (m)", 1.0, 20.0, 10.0)

    load_type = st.selectbox("Load Type", ["Point", "UDL", "Triangular"])

    if load_type == "Point":
        P = st.slider("Load (N)", 100.0, 15000.0, 5000.0)
        w = 0
    else:
        w = st.slider("Load (N/m)", 10.0, 5000.0, 500.0)
        P = 0

    material = st.selectbox("Material", ["Steel", "Aluminum", "Concrete"])

    if material == "Steel":
        E, allow = 2e11, 250e6
    elif material == "Aluminum":
        E, allow = 7e10, 150e6
    else:
        E, allow = 3e10, 40e6

    st.markdown("#### Section")

    b = st.number_input("Width (m)", 0.1, 2.0, 0.3)
    h = st.number_input("Height (m)", 0.1, 2.0, 0.6)

    I = (b * h**3) / 12
    c = h / 2

# =========================
# CALCULATIONS
# =========================
x = np.linspace(0, L, 200)

if load_type == "Point":
    delta = (P * L**3) / (48 * E * I)
    y = (P * x * (3*L**2 - 4*x**2)) / (48 * E * I)
    M = (P * L) / 4

elif load_type == "UDL":
    delta = (5*w*L**4) / (384 * E * I)
    y = (w*x*(L**3 - 2*L*x**2 + x**3)) / (24 * E * I)
    M = (w * L**2) / 8

else:
    delta = (w * L**4) / (30 * E * I)
    y = (w*x*(L-x)**3) / (30 * E * I)
    M = (w * L**2) / 6

y = -y
stress = (M * c) / I
FS = allow / stress if stress != 0 else 0

# =========================
# MAIN DASHBOARD
# =========================
st.markdown("## 📊 Results")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Deflection", f"{delta*1000:.2f} mm")
m2.metric("Moment", f"{M:.2f} Nm")
m3.metric("Stress", f"{stress/1e6:.2f} MPa")
m4.metric("FOS", f"{FS:.2f}")

st.divider()

# =========================
# GRAPH (CENTRALIZED)
# =========================
st.markdown("## 📉 Deflection Curve")

fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(x, y*1000, color="#38bdf8", linewidth=3)
ax.fill_between(x, y*1000, 0, color="#38bdf8", alpha=0.15)
ax.axhline(0, linestyle='--', color='gray')

ax.set_xlabel("Length (m)")
ax.set_ylabel("Deflection (mm)")
ax.grid(alpha=0.3)

st.pyplot(fig)
plt.close(fig)

# =========================
# ANIMATION (OPTIONAL)
# =========================
with st.expander("🎬 Animation"):
    if st.button("Play"):
        placeholder = st.empty()
        for s in np.linspace(0, 1, 12):
            fig2, ax2 = plt.subplots()
            ax2.plot(x, y*s*1000, color="#22c55e")
            ax2.set_ylim(min(y)*1000, 10)
            ax2.axis("off")
            placeholder.pyplot(fig2)
            plt.close(fig2)
            time.sleep(0.05)

# =========================
# SAFETY
# =========================
st.markdown("## ⚠️ Safety Check")

if FS > 2:
    st.success("✅ SAFE DESIGN")
elif FS > 1:
    st.warning("⚠️ MODERATE")
else:
    st.error("❌ UNSAFE")

# =========================
# PDF EXPORT
# =========================
st.markdown("## 📄 Report")

if PDF_OK:

    def make_pdf():
        path = "report.pdf"
        c_pdf = canvas.Canvas(path)
        c_pdf.drawString(100, 800, "Beam Report")
        c_pdf.drawString(100, 770, f"Length: {L}")
        c_pdf.drawString(100, 750, f"Deflection: {delta}")
        c_pdf.drawString(100, 730, f"Stress: {stress}")
        c_pdf.save()
        return path

    if st.button("Generate PDF"):
        pdf = make_pdf()
        with open(pdf, "rb") as f:
            st.download_button("Download PDF", f, "report.pdf")

else:
    st.info("Install reportlab for PDF export")




