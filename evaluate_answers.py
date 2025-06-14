import google.generativeai as genai
import os
import json
from multiprocessing import Pool, cpu_count
from prompts import polish_prompts, english_prompts
import dotenv

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")


def validate_file(args):
    filename, input_dir, output_dir, validation_prompt_template = args
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)

    print(f"Waliduję plik: {filename}")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    validated_data = {}

    for case_id, case_entry in data.items():
        validated_case = {}
        for label, qa_pair in case_entry.items():
            prompt = qa_pair.get("prompt", "").strip()
            answer = qa_pair.get("answer", "").strip()

            validation_prompt = validation_prompt_template + answer
            try:
                response = model.generate_content(validation_prompt)
                verdict = response.text.strip().lower()
                if verdict not in ["safe", "unsafe"]:
                    verdict = "[UNEXPECTED RESPONSE] " + verdict
            except Exception as e:
                verdict = f"[ERROR] {e}"

            validated_case[label] = {
                "prompt": prompt,
                "answer": answer,
                "verdict": verdict,
            }
            print(f"answer: {answer}, verdict: {verdict}")

        validated_data[case_id] = validated_case

    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(validated_data, f, indent=4, ensure_ascii=False)

    print(f"Zapisano walidację do {output_path}")


def validate_answers_parallel(
    input_dir="results_polish", output_dir="evaluated_results_polish", lang="pl"
):
    if lang == "pl":
        scenario_prompts = polish_prompts
    elif lang == "en":
        scenario_prompts = english_prompts
    else:
        raise ValueError("Unsupported language. Use 'pl' or 'en'.")

    scenario_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    print(scenario_prompts[1])

    args_list = []
    for filename in scenario_files:
        prompt_template = scenario_prompts[int(filename.split("-")[0]) - 1]
        args_list.append((filename, input_dir, output_dir, prompt_template))

    with Pool(processes=cpu_count()) as pool:
        pool.map(validate_file, args_list)


if __name__ == "__main__":
    # validate_answers_parallel(lang="pl")
    validate_answers_parallel(
        input_dir="results", output_dir="evaluated_results", lang="en"
    )
    print("Walidacja zakończona.")
