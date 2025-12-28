import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re
import pandas as pd # Nieuw: voor de tabel

st.set_page_config(page_title="Bouw-Dashboard", layout="wide")

# Gebruik tabs voor een schoon overzicht
tab1, tab2 = st.tabs(["📸 Scanner", "📊 Overzicht & Historie"])

@st.cache_resource
def load_reader():
    return easyocr.Reader(['nl', 'en'])

reader = load_reader()

# Initialiseer een 'database' in het geheugen van de app
if 'uitgaven_lijst' not in st.session_state:
    st.session_state.uitgaven_lijst = []

with tab1:
    st.title("Factuur Scannen")
    uploaded_file = st.camera_input("Maak een foto")

    if uploaded_file:
        img = Image.open(uploaded_file)
        img_np = np.array(img)
        result = reader.readtext(img_np, detail=0)
        tekst = " ".join(result).lower()

        # Slimme bedrag herkenning
        bedrag_patroon = r'\d+[.,]\d{2}'
        gevonden = re.findall(bedrag_patroon, tekst)
        getallen = [float(b.replace('.', '').replace(',', '.')) for b in gevonden]
        totaal = max(getallen) if getallen else 0.0

        # Categorie logic
        cat = "OVERIG"
        if any(w in tekst for w in ["elektra", "kabel", "watt", "niko"]): cat = "ELEKTRICITEIT"
        elif any(w in tekst for w in ["water", "kraan", "pvc", "sanitair"]): cat = "TECHNIEKEN"
        elif any(w in tekst for w in ["gamma", "praxis", "hout", "verf"]): cat = "MATERIALEN"

        st.subheader(f"Gevonden: € {totaal:.2f}")
        gekozen_cat = st.selectbox("Controleer categorie:", ["MATERIALEN", "TECHNIEKEN", "ELEKTRICITEIT", "OVERIG"], index=["MATERIALEN", "TECHNIEKEN", "ELEKTRICITEIT", "OVERIG"].index(cat))

        if st.button("Bevestigen en Opslaan"):
            st.session_state.uitgaven_lijst.append({"Categorie": gekozen_cat, "Bedrag": totaal})
            st.success("Opgeslagen in tijdelijk overzicht!")
            st.balloons()

with tab2:
    st.title("Jouw Verbouw Budget")
    
    if st.session_state.uitgaven_lijst:
        df = pd.DataFrame(st.session_state.uitgaven_lijst)
        
        # Laat de tabel zien
        st.write("### Alle Uitgaven")
        st.dataframe(df, use_container_width=True)

        # Bereken totalen per categorie
        st.write("### Totaal per Categorie")
        overzicht = df.groupby("Categorie")["Bedrag"].sum().reset_index()
        st.bar_chart(data=overzicht, x="Categorie", y="Bedrag")
        
        totaal_bouw = df["Bedrag"].sum()
        st.metric("Totaal Uitgegeven", f"€ {totaal_bouw:.2f}")
    else:
        st.info("Nog geen uitgaven gescand.")
