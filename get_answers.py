import google.generativeai as genai
import os
import json
from PIL import Image
from multiprocessing import Pool, cpu_count
import dotenv

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")


def load_image_as_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def process_scenario_file(args):
    filename, input_dir, output_dir, image_base_dir, lang = args
    scenario_name = filename.replace(".json", "")
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)

    print(f"Przetwarzam scenariusz: {filename}")

    with open(input_path, "r", encoding="utf-8") as f:
        questions_data = json.load(f)

    results = {}

    for key, q_data in questions_data.items():
        case_id = key
        print(f"Pytanie {key} w {filename}")

        case_results = {}
        prompts = {
            "question": q_data.get("Question", ""),
            "changed_question": q_data.get("Changed Question", ""),
            "rephrased_question": q_data.get("Rephrased Question", ""),
            "rephrased_question_sd": q_data.get("Rephrased Question(SD)", ""),
        }

        for label, prompt_text in prompts.items():
            prompt = prompt_text
            input_data = prompt

            if label in ["rephrased_question", "rephrased_question_sd"]:
                dirname = "TYPO" if label == "rephrased_question_sd" else "SD_TYPO"
                if lang == "pl":
                    dirname = (
                        "TYPO_PL" if label == "rephrased_question_sd" else "SD_TYPO_PL"
                    )
                image_path = os.path.join(
                    image_base_dir, scenario_name, dirname, f"{case_id}.jpg"
                )
                if os.path.exists(image_path):
                    image_bytes = load_image_as_bytes(image_path)
                    input_data = [
                        prompt,
                        {"mime_type": "image/jpeg", "data": image_bytes},
                    ]
                else:
                    input_data = [f"{prompt} (UWAGA: obraz nie znaleziony)"]

            try:
                response = model.generate_content(input_data)
                answer = response.text
            except Exception as e:
                answer = f"[ERROR] {e}"

            case_results[label] = {"prompt": prompt, "answer": answer}

        results[key] = case_results

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"Zapisano wyniki do {output_path}")


def generate_answers_parallel(
    output_dir="results", input_dir="data/processed_questions", lang="en"
):
    INPUT_DIR = input_dir
    OUTPUT_DIR = output_dir
    IMAGE_BASE_DIR = "data/images"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    scenario_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]

    args_list = [
        (filename, INPUT_DIR, OUTPUT_DIR, IMAGE_BASE_DIR, lang)
        for filename in scenario_files
    ]

    with Pool(processes=cpu_count()) as pool:
        pool.map(process_scenario_file, args_list)


if __name__ == "__main__":
    generate_answers_parallel()
    generate_answers_parallel(
        output_dir="results_polish",
        input_dir="data/processed_questions_polish",
        lang="pl",
    )
    print("Przetwarzanie zakończone.")
