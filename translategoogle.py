import requests
import json
import os
import dotenv

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")

API_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"


def translate(text: str) -> str:
    headers = {"Content-Type": "application/json"}

    payload = {
        "q": text,
        "target": "pl",
        "source": "en",
    }

    response = requests.post(
        f"{API_ENDPOINT}?key={API_KEY}", headers=headers, data=json.dumps(payload)
    )
    response.raise_for_status()

    data = response.json()

    if (
        "data" in data
        and "translations" in data["data"]
        and data["data"]["translations"]
    ):
        return data["data"]["translations"][0]["translatedText"]
    else:
        raise ValueError(
            f"Brak tłumaczenia w odpowiedzi API lub nieprawidłowa struktura: {data}"
        )


if __name__ == "__main__":

    english_text_1 = "Hello, how are you doing today?"
    try:
        polish_translation_1 = translate(english_text_1)
        print(f"Oryginał: '{english_text_1}'")
        print(f"Tłumaczenie: '{polish_translation_1}'")
    except Exception as e:
        print(f"Wystąpił błąd podczas tłumaczenia: {e}")

    english_text_2 = "The capital of Poland is Warsaw."
    try:
        polish_translation_2 = translate(english_text_2)
        print(f"\nOryginał: '{english_text_2}'")
        print(f"Tłumaczenie: '{polish_translation_2}'")
    except Exception as e:
        print(f"Wystąpił błąd podczas tłumaczenia: {e}")
