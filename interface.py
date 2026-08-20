import streamlit as st
import pandas as pd

# 1. Konfiguracja i ustawienia
st.set_page_config(page_title="Paragonator 3000", layout="centered")
osoby = ["Mikołaj", "Zuzia", "Rudy", "Pawko"]

st.title("💸 Paragonator 3000")
st.write("Rozliczaj paragony bez wstawania z łóżka.")
st.markdown("---")

# 2. Symulacja danych, które docelowo wypluje API OpenAI
# (Gdy podepniemy AI, to to zniknie, a dane będą zczytywane ze zdjęcia)
mock_paragony = [
    {
        "id_paragonu": "Biedronka - 01.08.2026",
        "produkty": [
            {"nazwa": "Wódka (wspólna)", "cena": 50.00},
            {"nazwa": "Laysy Paprykowe", "cena": 8.00},
            {"nazwa": "Sushi box", "cena": 20.00}
        ]
    }
]

# 3. Zmienna do trzymania naszych obliczeń
rozliczenia = []

# 4. Generowanie interfejsu (Jedna długa strona)
for p_idx, paragon in enumerate(mock_paragony):
    st.subheader(f"🧾 Paragon: {paragon['id_paragonu']}")
    
    # Wybór osoby płacącej za cały paragon (radiobutton poziomy)
    kto_placil = st.radio(
        "Kto zapłacił za ten paragon?", 
        osoby, 
        key=f"placi_{p_idx}", 
        horizontal=True
    )
    
    st.write("### Lista produktów:")
    
    # Generowanie każdego produktu z checkboksem dla lokatorów
    for prod_idx, produkt in enumerate(paragon["produkty"]):
        # Graficzny podział na kolumny: z lewej nazwa i cena, z prawej checkboxy
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"**{produkt['nazwa']}**")
            st.markdown(f"*{produkt['cena']:.2f} zł*")
            
        with col2:
            st.write("Dla kogo?")
            # Tworzymy 4 kolumny na checkboxy, żeby były ładnie w jednym rzędzie na telefonie
            chk_cols = st.columns(4)
            zaznaczeni = []
            
            for i, osoba in enumerate(osoby):
                # Klucz (key) musi być unikalny dla każdego checkboxa!
                if chk_cols[i].checkbox(osoba, key=f"chk_{p_idx}_{prod_idx}_{osoba}"):
                    zaznaczeni.append(osoba)
                    
        # Logika matematyczna na bieżąco
        if zaznaczeni:
            kwota_na_glowe = produkt['cena'] / len(zaznaczeni)
            for dłużnik in zaznaczeni:
                if dłużnik != kto_placil: # Nie ma sensu, żeby ktoś wisiał kasę samemu sobie
                    rozliczenia.append({
                        "Kto wisi": dłużnik,
                        "Komu wisi": kto_placil,
                        "Za co": produkt['nazwa'],
                        "Kwota": kwota_na_glowe
                    })
        st.markdown("---") # Linia oddzielająca produkty

# 5. Ostateczne podsumowanie
st.write("### 📊 Finał")
if st.button("Podsumuj i Zapisz (Gotowe do Excela)", type="primary"):
    if rozliczenia:
        # Zamieniamy naszą listę na tabelę z biblioteki Pandas
        df = pd.DataFrame(rozliczenia)
        
        # Grupujemy długi (żeby wiedzieć ogółem kto komu ile)
        podsumowanie = df.groupby(["Kto wisi", "Komu wisi"])['Kwota'].sum().reset_index()
        
        st.success("Matematyka zrobiona! Oto wyniki:")
        st.dataframe(podsumowanie, use_container_width=True)
    else:
        st.warning("Nikogo nie zaznaczono przy żadnym produkcie. Nikt nikomu nic nie wisi!")