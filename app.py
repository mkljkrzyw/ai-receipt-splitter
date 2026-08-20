import os
import base64
import json
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. Funkcja do zamiany zdjęcia na format czytelny dla internetu (Base64)
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 3. Główne zapytanie do AI
def analizuj_paragon(sciezka_do_zdjecia):
    base64_image = encode_image(sciezka_do_zdjecia)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={ "type": "json_object" }, # Zmuszamy AI do wyplucia czystego JSONa
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Jesteś kasjerem. Odczytaj ten paragon. Zwróć plik JSON, który zawiera listę 'produkty', gdzie każdy produkt ma 'nazwa' i 'cena'. Nic więcej."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
    )
    
    return json.loads(response.choices[0].message.content)

# 4. Odpalenie skryptu
if __name__ == "__main__":
    dane_z_paragonu = analizuj_paragon("moj_paragon.jpg")
    print(json.dumps(dane_z_paragonu, indent=4, ensure_ascii=False))