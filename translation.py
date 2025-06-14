import os
import json
import time
import requests
import dotenv

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")

API_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"

input_dir = "data/processed_questions"
output_dir = "data/processed_questions_polish"
os.makedirs(output_dir, exist_ok=True)


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


def translate_dict(d: dict) -> dict:
    new_dict = {}
    for key, value in d.items():
        if key == "GPT-Pred" or key == "Phrase Type":
            next
        elif isinstance(value, str):
            print(f"Tłumaczenie: {value}")
            translation = translate(value)
            print("Przetłumaczono na polski:")
            print(translation)
            new_dict[key] = translation
            time.sleep(0.5)
        elif isinstance(value, dict):
            new_dict[key] = translate_dict(value)
        else:
            new_dict[key] = value
    return new_dict


for filename in os.listdir(input_dir):
    if filename.endswith(".json"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        translated_data = translate_dict(data)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=4)

        print(f"Przetłumaczono: {filename}")
