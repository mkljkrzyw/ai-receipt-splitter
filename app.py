import streamlit as st
import pandas as pd
import base64
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Ładowanie klucza z sejfu (.env)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. Ustawienia interfejsu
st.set_page_config(page_title="Paragonator 3000", layout="centered")
osoby = ["Mikołaj", "Zuzia", "Rudy", "Pawko"]

st.title("💸 Paragonator 3000")
st.write("Rozliczaj paragony bez wstawania z łóżka.")
st.markdown("---")

# 3. Pamięć podręczna (OCHRONA TWOJEGO PORTFELA)
# Dzięki temu kod wyśle zapytanie do AI tylko raz dla danego paragonu
if 'produkty_z_ai' not in st.session_state:
    st.session_state['produkty_z_ai'] = None

# 4. Wgrywanie zdjęcia paragonu prosto z telefonu/komputera
plik_paragonu = st.file_uploader("Wgraj zdjęcie paragonu", type=['jpg', 'jpeg', 'png'])

if plik_paragonu is not None:
    # Wyświetlamy zdjęcie, żebyś widział co wrzuciłeśgpt-4o-mini
    st.image(plik_paragonu, caption="Twój paragon", use_container_width=True)
    
    if st.button("Odczytaj AI 🤖", type="primary"):
        with st.spinner("Szef kuchni czyta dane... to potrwa kilka sekund."):
            # Zamiana wgranego pliku na format dla AI (Base64)
            base64_image = base64.b64encode(plik_paragonu.getvalue()).decode('utf-8')
            
            # Zapytanie do modelu - WERSJA PRO
            response = client.chat.completions.create(
                model="gpt-4o", # ZMIANA: Używamy pełnego, inteligentnego modelu
                response_format={ "type": "json_object" },
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": """Jesteś głównym księgowym analizującym polskie paragony sklepowe (Biedronka, Lidl, Auchan). 
                                    Zwróć plik JSON, który zawiera listę 'produkty', gdzie każdy produkt ma 'nazwa' i 'cena'.
                                    
                                    ZASADY KRYTYCZNE, KTÓRYCH MUSISZ PRZESTRZEGAĆ:
                                    1. Odczytuj nazwy precyzyjnie, omijając śmieciowe ciągi znaków.
                                    2. RABATY I OPUSTY: Jeśli pod produktem widzisz pozycję typu "Rabat", "Opust" lub ujemną kwotę, MUSISZ odjąć tę wartość od ceny głównej produktu nad nim. Zwróć tylko JEDNĄ, ostateczną cenę po rabacie.
                                    3. Nigdy nie dodawaj opustu jako osobnego produktu na liście!
                                    4. Ignoruj sumy końcowe (np. "SUMA PLN", "Gotówka", "Reszta", "Kwota VAT").
                                    5. Cena musi być dokładną liczbą zmiennoprzecinkową (np. 14.99)."""
                            },
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ]
            )
            
            wynik = json.loads(response.choices[0].message.content)
            # Zapisujemy do pamięci Streamlit!
            st.session_state['produkty_z_ai'] = wynik.get('produkty', [])
            st.success("Odczytano paragon!")

# 5. Moduł klikania i rozliczeń (Aktywuje się dopiero, gdy AI zwróci dane)
if st.session_state['produkty_z_ai'] is not None:
    st.subheader("🧾 Rozliczenie")
    rozliczenia = []
    
    # Kto założył kasę w Biedrze?
    kto_placil = st.radio("Kto zapłacił za ten paragon?", osoby, horizontal=True)
    st.write("### Lista produktów:")
    
    # Lecimy z produktami
    for prod_idx, produkt in enumerate(st.session_state['produkty_z_ai']):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"**{produkt['nazwa']}**")
            st.markdown(f"*{produkt['cena']} zł*")
            
        with col2:
            st.write("Dla kogo?")
            chk_cols = st.columns(4)
            zaznaczeni = []
            
            for i, osoba in enumerate(osoby):
                # Unikalny klucz dla każdego checkboxa
                if chk_cols[i].checkbox(osoba, key=f"chk_{prod_idx}_{osoba}"):
                    zaznaczeni.append(osoba)
                    
        # Matematyka w tle
        if zaznaczeni:
            kwota_na_glowe = produkt['cena'] / len(zaznaczeni)
            for dluznik in zaznaczeni:
                if dluznik != kto_placil: 
                    rozliczenia.append({
                        "Kto wisi": dluznik,
                        "Komu wisi": kto_placil,
                        "Za co": produkt['nazwa'],
                        "Kwota": kwota_na_glowe
                    })
        st.markdown("---")

    st.write("### 📊 Finał")
    if st.button("Podsumuj i Zapisz (Gotowe do Excela)", type="primary"):
        if rozliczenia:
            df = pd.DataFrame(rozliczenia)
            # Grupujemy długi
            podsumowanie = df.groupby(["Kto wisi", "Komu wisi"])['Kwota'].sum().reset_index()
            # Zaokrąglamy grosze
            podsumowanie['Kwota'] = podsumowanie['Kwota'].round(2)
            
            st.success("Matematyka zrobiona! Oto wyniki:")
            st.dataframe(podsumowanie, use_container_width=True)
        else:
            st.warning("Nikogo nie zaznaczono przy żadnym produkcie. Nikt nikomu nic nie wisi!")