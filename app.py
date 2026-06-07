import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Ultimate Beam Analyzer", layout="wide")
plt.style.use('dark_background')

# =========================
# BACKGROUND
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
    elif load_type == "UDL":
        w = st.slider("UDL (N/m)", 10.0, 5000.0, 500.0)
    else:
        w = st.slider("Max Triangular Load (N/m)", 10.0, 5000.0, 500.0)

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
        c = h/2
    else:
        d = st.number_input("Diameter (m)", value=0.5)
        I = (np.pi * d**4) / 64
        c = d/2

# =========================
# CALCULATIONS
# =========================
x = np.linspace(0, L, 200)

if load_type == "Point Load":

