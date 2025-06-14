import os
from PIL import Image


def merge_images_vertically(image1_path, image2_path):
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    width = max(image1.width, image2.width)
    total_height = image1.height + image2.height

    combined = Image.new("RGB", (width, total_height), color="white")
    combined.paste(image1, (0, 0))
    combined.paste(image2, (0, image1.height))

    return combined


def merge_all_images():
    IMAGE_BASE = "data/images"

    for scenario_name in os.listdir(IMAGE_BASE):
        scenario_path = os.path.join(IMAGE_BASE, scenario_name)
        sd_path = os.path.join(scenario_path, "SD")
        typo_path = os.path.join(scenario_path, "TYPO_PL")
        output_path = os.path.join(scenario_path, "SD_TYPO_PL")

        if not os.path.isdir(sd_path) or not os.path.isdir(typo_path):
            continue

        os.makedirs(output_path, exist_ok=True)
        print(f"Przetwarzanie scenariusza: {scenario_name}")

        for filename in os.listdir(sd_path):
            if not filename.endswith(".jpg"):
                continue

            number = os.path.splitext(filename)[0]
            img_sd_path = os.path.join(sd_path, filename)
            img_typo_path = os.path.join(typo_path, f"{number}.jpg")
            out_path = os.path.join(output_path, f"{number}.jpg")

            if not os.path.exists(img_typo_path):
                print(f"Brak TYPO_PL dla: {filename}")
                continue

            try:
                combined_image = merge_images_vertically(img_sd_path, img_typo_path)
                combined_image.save(out_path)
                print(f"Zapisano: {out_path}")
            except Exception as e:
                print(f"Błąd przy łączeniu {filename}: {e}")


if __name__ == "__main__":
    merge_all_images()
