import streamlit as st
import pdfplumber
import re
import pandas as pd

st.set_page_config(page_title="Robby's Multi-Scanner", layout="wide")
st.title("🏗️ Robby's Factuur & PDF Scanner")

# Upload sectie
uploaded_file = st.file_uploader("Upload je factuur (PDF of Foto)", type=['pdf', 'png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    tekst = ""
    
    # PDF verwerking (vlijmscherp voor digitale facturen)
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                tekst += page.extract_text() or ""
    else:
        # Foto verwerking via EasyOCR (zoals we eerder deden)
        import easyocr
        import numpy as np
        from PIL import Image
        reader = easyocr.Reader(['nl'])
        img = Image.open(uploaded_file)
        result = reader.readtext(np.array(img), detail=0)
        tekst = " ".join(result)

    tekst = tekst.lower()

    # --- SLIMMERE ZOEKLOGICA VOOR MEERDERE BEDRAGEN ---
    # We zoeken naar alles wat op een bedrag lijkt: getallen met een komma en 2 decimalen
    bedrag_patroon = r'\d+[.,]\d{2}'
    gevonden_tekst_bedragen = re.findall(bedrag_patroon, tekst)
    
    # Omzetten naar echte getallen en uniek maken (tegen dubbelingen)
    unieke_bedragen = []
    for b in gevonden_tekst_bedragen:
        getal = float(b.replace('.', '').replace(',', '.'))
        if getal > 1.0 and getal not in unieke_bedragen: # Filter heel kleine bedragen en dubbelen
            unieke_bedragen.append(getal)

    st.divider()
    
    if unieke_bedragen:
        st.subheader("Gevonden bedragen op de factuur:")
        st.write("De AI heeft de volgende bedragen herkend. Selecteer de juiste:")
        
        # Laat de gebruiker de bedragen kiezen die hij wil opslaan
        geselecteerde_bedragen = st.multiselect("Welke bedragen wil je opslaan?", 
                                                options=sorted(unieke_bedragen, reverse=True),
                                                default=[max(unieke_bedragen)])
        
        # Categorie toevoegen
        categorie = st.selectbox("Categorie voor deze uitgave(n):", ["MATERIALEN", "TECHNIEKEN", "ELEKTRICITEIT", "OVERIG"])

        if st.button("Sla geselecteerde bedragen op"):
            # Hier kun je de logica toevoegen om het naar een lijst te schrijven
            for bedrag in geselecteerde_bedragen:
                st.write(f"✅ Opgeslagen: €{bedrag:.2f} in categorie {categorie}")
            st.balloons()
    else:
        st.warning("Geen bedragen gevonden. Probeer een duidelijkere scan of typ het bedrag handmatig.")
        handmatig = st.number_input("Handmatig bedrag invoeren:", value=0.0)
        if st.button("Handmatig opslaan"):
            st.success(f"€{handmatig} opgeslagen!")

    # Voor debug: wat ziet de AI?
    with st.expander("Bekijk de volledige tekst uit de PDF/Foto"):
        st.text(tekst)

