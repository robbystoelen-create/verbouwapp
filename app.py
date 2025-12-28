# AI de tekst laten lezen
        img_np = np.array(img)
        result = reader.readtext(img_np, detail=0)
        tekst = " ".join(result).lower()
        
        # Verbeterde zoekfunctie voor bedragen
        # Zoekt naar patronen zoals 10,50 of 1.250,00 of 15.00
        bedrag_patroon = r'\d+(?:[.,]\d+)*[.,]\d{2}'
        gevonden = re.findall(bedrag_patroon, tekst)
        
        # Schoon de getallen op en kies de hoogste
        schoon_bedragen = []
        for b in gevonden:
            schoon = b.replace('.', '').replace(',', '.')
            schoon_bedragen.append(float(schoon))
        
        totaal = max(schoon_bedragen) if schoon_bedragen else 0.0
