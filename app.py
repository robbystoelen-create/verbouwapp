import streamlit as st
import pdfplumber
import re
import pandas as pd
import numpy as np
from PIL import Image

st.set_page_config(page_title="Robby's Bouw App", layout="wide")

# Initialiseer de database in het geheugen
if 'uitgaven_lijst' not in st.session_state:
    st.session_state.uitgaven_lijst = []

# Maak de mappen (Tabs) weer aan
tab1, tab2 = st.tabs(["📸 Scanner", "📊 Overzicht"])

with tab1:
    st.title("Scanner")
    uploaded_file = st.file_uploader("Upload PDF of Foto", type=['pdf', 'png', 'jpg', 'jpeg'])
    
    # Camera als backup
    if not uploaded_file:
        uploaded_file = st.camera_input("Of maak een foto")

    if uploaded_file is not None:
        tekst = ""
        # PDF tekst eruit halen
        if uploaded_file.type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    tekst += page.extract_text() or ""
        else:
            # Foto tekst eruit halen (hiervoor moet easyocr in je requirements staan)
            import easyocr
            reader = easyocr.Reader(['nl'])
            img = Image.open(uploaded_file)
            result = reader.readtext(np.array(img), detail=0)
            tekst = " ".join(result)

        tekst = tekst.lower()

        # Zoek alle mogelijke bedragen (getal met , of . en 2 decimalen)
        bedrag_patroon = r'\d+[.,]\d{2}'
        gevonden = re.findall(bedrag_patroon, tekst)
        
        # Maak getallen schoon en uniek
        unieke_bedragen = []
        for b in gevonden:
            g = float(b.replace('.', '').replace(',', '.'))
            if g > 1.0 and g not in unieke_bedragen and not (2020 <= g <= 2030):
                unieke_bedragen.append(g)

        if unieke_bedragen:
            st.write("### Kies de juiste bedragen:")
            geselecteerd = st.multiselect("Welke bedragen horen bij de factuur?", 
                                          options=sorted(unieke_bedragen, reverse=True),
                                          default=[max(unieke_bedragen)])
            
            cat = st.selectbox("Categorie:", ["MATERIALEN", "TECHNIEKEN", "ELEKTRICITEIT", "OVERIG"])
            
            if st.button("Sla deze uitgaven op"):
                for b in geselecteerd:
                    st.session_state.uitgaven_lijst.append({"Categorie": cat, "Bedrag": b})
                st.success(f"Opgeslagen in Overzicht!")
                st.balloons()
        else:
            st.warning("Geen bedrag herkend.")
            handmatig = st.number_input("Handmatig bedrag:", value=0.0)
            if st.button("Handmatig opslaan"):
                st.session_state.uitgaven_lijst.append({"Categorie": "OVERIG", "Bedrag": handmatig})

with tab2:
    st.title("Totaal Overzicht")
    
    if st.session_state.uitgaven_lijst:
        df = pd.DataFrame(st.session_state.uitgaven_lijst)
        
        # Tabel laten zien
        st.dataframe(df, use_container_width=True)
        
        # Totaal berekenen
        totaal_generaal = df["Bedrag"].sum()
        st.metric("Totaal Uitgegeven", f"€ {totaal_generaal:.2f}")
        
        # Grafiekje
        st.bar_chart(df.groupby("Categorie")["Bedrag"].sum())
        
        # Download knop voor Excel (CSV)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download lijst voor Excel", data=csv, file_name="verbouw_kosten.csv", mime="text/csv")
    else:
        st.info("De lijst is nog leeg. Scan eerst een factuur.")
