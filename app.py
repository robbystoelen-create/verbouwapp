import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re
import pdfplumber # Voor het direct lezen van tekst uit PDF

st.set_page_config(page_title="Bouw Scanner PDF & Foto", page_icon="🏗️")
st.title("🏗️ Robby's Factuur Scanner")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['nl', 'en'])

reader = load_reader()

# Aangepaste knop: accepteert nu afbeeldingen EN PDF
uploaded_file = st.file_uploader("Upload een factuur (PDF of Foto)", type=['pdf', 'png', 'jpg', 'jpeg'])

# Als er geen bestand is geüpload, tonen we de camera optie als alternatief
if not uploaded_file:
    uploaded_file = st.camera_input("Of maak direct een foto")

if uploaded_file is not None:
    tekst = ""
    
    # CHECK: Is het een PDF?
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            # Lees de tekst van alle pagina's
            for page in pdf.pages:
                tekst += page.extract_text() or ""
    
    # Anders is het een foto
    else:
        img = Image.open(uploaded_file)
        img_np = np.array(img)
        result = reader.readtext(img_np, detail=0)
        tekst = " ".join(result)

    tekst = tekst.lower()

    # --- DEZELFDE SLIMME ZOEKLOGICA ---
    with st.expander("Bekijk gevonden tekst"):
        st.write(tekst)

    bedrag_patroon = r'\d+[.,]\d{2}'
    gevonden = re.findall(bedrag_patroon, tekst)
    getallen = [float(b.replace('.', '').replace(',', '.')) for b in gevonden]
    
    # Filter jaartallen en kies laatste bedrag (vaak het totaal)
    getallen = [g for g in getallen if not (2020 <= g <= 2030)]
    totaal = getallen[-1] if getallen else 0.0

    st.divider()
    st.subheader(f"Gevonden bedrag: € {totaal:.2f}")
    
    gekozen_totaal = st.number_input("Klop het bedrag?", value=totaal)
    
    if st.button("Opslaan"):
        st.success(f"€{gekozen_totaal} is verwerkt!")
        
