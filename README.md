# Paragonator

Paragonator is a Streamlit application for splitting shared expenses. It reads products from a receipt photo using OpenAI and calculates who owes money and to whom.

## Features

- Read products and prices from receipt photos.
- Account for discounts during analysis.
- Assign products to multiple people.
- Split costs automatically.
- View a clear settlement summary.

## Requirements

- Python 3.10 or newer.
- An OpenAI API key.
- A receipt photo in JPG, JPEG, or PNG format.

## Setup

1. Create and activate a virtual environment:

	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	```

2. Install the dependencies:

	```powershell
	pip install -r requirements.txt
	```

3. Create a `.env` file in the project directory:

	```text
	OPENAI_API_KEY=your_openai_api_key
	```

4. Start the application:

	```powershell
	streamlit run app.py
	```

## Usage

1. Upload a receipt photo.
2. Select `Read products`.
3. Choose the person who paid.
4. Select everyone who shared each product.
5. Select `Calculate settlement`.

## Limitations

Recognition quality depends on the photo and receipt layout. Receipts with small text, low contrast, or unusual formatting may require manual verification. Each image analysis uses the OpenAI API and may incur a cost based on the provider's current pricing.

## Technologies

Python, Streamlit, OpenAI API, Pandas, and python-dotenv.