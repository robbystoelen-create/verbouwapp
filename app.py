import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re
import os

st.set_page_config(page_title="Verbouw Scanner", page_icon="🏗️")
st.title("🏗️ Robby's Verbouw Scanner")

# AI Laden
@st.cache_resource
def load_reader():
    return easyocr.Reader(['nl'])

reader = load_reader()

# De Camera/Upload knop
uploaded_file = st.camera_input("Maak een foto van je factuur")

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Gescande foto", use_container_width=True)
    
    with st.spinner('De AI leest je factuur...'):
        img_np = np.array(img)
        result = reader.readtext(img_np, detail=0)
        tekst = " ".join(result).lower()

        # Bedrag zoeken
        bedragen = re.findall(r'\d+[.,]\d{2}', tekst)
        # We pakken het hoogste bedrag (vaak het totaal)
        totaal = max([float(b.replace('.', '').replace(',', '.')) for b in bedragen]) if bedragen else 0.0

        # Categorie bepalen
        cat = "OVERIG"
        if any(w in tekst for w in ["elektra", "kabel", "watt", "niko"]): cat = "ELEKTRICITEIT"
        elif any(w in tekst for w in ["water", "kraan", "pvc", "sanitair"]): cat = "TECHNIEKEN"
        elif any(w in tekst for w in ["gamma", "praxis", "hout", "verf"]): cat = "MATERIALEN"

    st.subheader(f"Gevonden bedrag: € {totaal:.2f}")
    st.write(f"Voorgestelde categorie: **{cat}**")

    if st.button("Sla deze uitgave op"):
        with open("mijn_uitgaven.txt", "a") as f:
            f.write(f"Categorie: {cat} | Bedrag: €{totaal:.2f}\n")
        st.balloons()
        st.success("Opgeslagen in mijn_uitgaven.txt!")