import base64
import json
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
people = ["Mikołaj", "Zuzia", "Rudy", "Pawko"]

st.set_page_config(page_title="Paragonator", page_icon="💸", layout="centered")
st.title("💸 Paragonator")
st.write("A simple way to split shared expenses.")
st.markdown("---")

if "products_from_ai" not in st.session_state:
    st.session_state["products_from_ai"] = None

receipt_file = st.file_uploader(
    "Upload a receipt photo",
    type=["jpg", "jpeg", "png"],
    help="Supported formats: JPG, JPEG and PNG.",
)

if receipt_file is not None:
    st.image(receipt_file, caption="Your receipt", use_container_width=True)

    if st.button("Read products", type="primary"):
        with st.spinner("Analyzing the receipt. This may take a few seconds."):
            base64_image = base64.b64encode(receipt_file.getvalue()).decode("utf-8")
            response = client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """You are an accountant analyzing Polish supermarket receipts (Biedronka, Lidl, Auchan).
                                    Return a JSON object containing a list called 'products', where each product has a 'name' and a 'price'.
                                    
                                    CRITICAL RULES:
                                    1. Read product names precisely and ignore garbage text.
                                    2. DISCOUNTS AND REBATES: If you see a line such as "Discount", "Rebate", or a negative amount below a product, subtract it from the product's main price. Return only one final price after the discount.
                                    3. Never include a discount or rebate as a separate product.
                                    4. Ignore final totals such as "TOTAL PLN", "Cash", "Change", or "VAT amount".
                                    5. Each price must be an exact floating-point number, for example 14.99.""",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
            )
            result = json.loads(response.choices[0].message.content)
            st.session_state["products_from_ai"] = result.get("products", [])
            st.success("Products have been read.")

if st.session_state["products_from_ai"] is not None:
    st.subheader("🧾 Expense split")
    settlements = []
    payer = st.radio("Who paid for the receipt?", people, horizontal=True)
    st.write("### Products")

    for product_index, product in enumerate(st.session_state["products_from_ai"]):
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(f"**{product['name']}**")
            st.markdown(f"*{product['price']:.2f} PLN*")

        with col2:
            st.write("Who shared it?")
            chk_cols = st.columns(4)
            selected_people = []

            for i, person in enumerate(people):
                if chk_cols[i].checkbox(person, key=f"check_{product_index}_{person}"):
                    selected_people.append(person)

        if selected_people:
            share = product["price"] / len(selected_people)
            for debtor in selected_people:
                if debtor != payer:
                    settlements.append(
                        {
                            "Debtor": debtor,
                            "Paid by": payer,
                            "Item": product["name"],
                            "Amount": share,
                        }
                    )
        st.markdown("---")

    st.write("### 📊 Summary")
    if st.button("Calculate settlement", type="primary"):
        if settlements:
            df = pd.DataFrame(settlements)
            summary = (
                df.groupby(["Debtor", "Paid by"])["Amount"]
                .sum()
                .reset_index()
            )
            summary["Amount"] = summary["Amount"].round(2)

            st.success("The settlement is ready.")
            st.dataframe(summary, use_container_width=True)
        else:
            st.warning("Assign at least one product to someone to calculate the settlement.")
