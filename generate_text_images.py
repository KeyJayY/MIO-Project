import os
import json
from PIL import Image, ImageDraw, ImageFont
import textwrap


def create_image_with_text(
    text, font_size=32, image_width=1024, padding=40, line_spacing=10
):
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    temp_img = Image.new("RGB", (image_width, 1))
    draw = ImageDraw.Draw(temp_img)

    avg_char_width = (
        sum(
            draw.textlength(char, font=font)
            for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )
        / 52
    )
    max_chars_per_line = int(image_width / avg_char_width)

    wrapped_lines = textwrap.wrap(text, width=max_chars_per_line)

    line_heights = []
    for line in wrapped_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])

    total_height = (
        sum(line_heights) + (len(wrapped_lines) - 1) * line_spacing + 2 * padding
    )

    image = Image.new("RGB", (image_width, total_height), color="white")
    draw = ImageDraw.Draw(image)

    y = padding
    for line, line_height in zip(wrapped_lines, line_heights):
        line_width = draw.textlength(line, font=font)
        x = (image_width - line_width) // 2
        draw.text((x, y), line, font=font, fill="black")
        y += line_height + line_spacing

    return image


def generate_images_from_key_phrases():
    INPUT_DIR = "data/processed_questions_polish"
    BASE_OUTPUT_DIR = "data/images"

    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith(".json"):
            continue

        scenario_name = filename.replace(".json", "")
        input_path = os.path.join(INPUT_DIR, filename)
        output_dir = os.path.join(BASE_OUTPUT_DIR, scenario_name, "TYPO_PL")
        os.makedirs(output_dir, exist_ok=True)

        print(f"\nPrzetwarzam plik: {filename}")

        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for key, entry in data.items():
            key_phrase = entry.get("Key Phrase", "").strip()

            if not key_phrase:
                print(f"- Pominięto przypadek {key} (brak Key Phrase)")
                continue

            image = create_image_with_text(key_phrase)
            output_path = os.path.join(output_dir, f"{key}.jpg")
            image.save(output_path)

            print(f"Zapisano obraz: {output_path}")


if __name__ == "__main__":
    generate_images_from_key_phrases()
