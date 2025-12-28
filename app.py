import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Verbouw Scanner PRO", page_icon="🏗️")
st.title("🏗️ Robby's Verbouw Scanner")

# AI Laden met Cache (zodat het sneller gaat)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['nl', 'en'])

reader = load_reader()

uploaded_file = st.camera_input("Scan een factuur of bonnetje")

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Gescande foto", use_container_width=True)
    
    with st.spinner('De AI analyseert de tekst...'):
        # Omzetten naar tekst
        img_np = np.array(img)
        result = reader.readtext(img_np, detail=0)
        tekst = " ".join(result).lower()

        # Laat zien wat de AI ziet (voor troubleshooting)
        with st.expander("Bekijk wat de AI heeft gelezen"):
            st.write(tekst)

        # Zoek bedragen (zoekt naar patronen als 10,50 of 1.250,99)
        # We zoeken naar getallen met 2 decimalen achter een komma of punt
        bedrag_patroon = r'\d+[.,]\d{2}'
        gevonden_bedragen = re.findall(bedrag_patroon, tekst)
        
        # Bedragen omzetten naar bruikbare getallen
        getallen = []
        for b in gevonden_bedragen:
            # Haal punten weg (duizendtallen) en vervang komma door punt
            schoon = b.replace('.', '').replace(',', '.')
            getallen.append(float(schoon))

        totaal = max(getallen) if getallen else 0.0

        # Categorie bepalen op basis van trefwoorden
        cat = "OVERIG"
        if any(w in tekst for w in ["elektra", "kabel", "watt", "niko", "lamp"]): cat = "ELEKTRICITEIT"
        elif any(w in tekst for w in ["water", "kraan", "pvc", "sanitair", "buis"]): cat = "TECHNIEKEN"
        elif any(w in tekst for w in ["gamma", "praxis", "hout", "verf", "schroef"]): cat = "MATERIALen"

    st.divider()
    st.subheader(f"Gevonden Totaalbedrag: € {totaal:.2f}")
    st.info(f"Voorgestelde categorie: **{cat}**")

    if st.button("Sla deze uitgave op"):
        # Op Streamlit Cloud wordt dit tijdelijk opgeslagen
        with open("uitgaven_log.txt", "a") as f:
            f.write(f"{cat};{totaal:.2f}\n")
        st.balloons()
        st.success("Opgeslagen!")
