import os
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict


def get_question_type(question):
    if question == "question":
        return "pytanie"
    elif question == "changed_question":
        return "zmienione pytanie"
    elif question == "rephrased_question":
        return "pytanie z obrazem ilustracji i tekstu"
    elif question == "rephrased_question_sd":
        return "pytanie z obrazem tekstu"


def analyze_verdicts_and_plot_reversed(directory="evaluated_results_polish", lang="pl"):
    all_stats = defaultdict(lambda: defaultdict(lambda: {"safe": 0, "unsafe": 0}))
    files_set = set()

    for filename in os.listdir(directory):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(directory, filename)
        files_set.add(filename)  # dodajemy zawsze, niezależnie od zawartości

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for case_id, case_data in data.items():
            for question_type, content in case_data.items():
                verdict_raw = content.get("verdict", "")
                verdict = str(verdict_raw).strip().lower()

                if verdict in {"safe", "unsafe"}:
                    all_stats[question_type][filename][verdict] += 1
                else:
                    print(
                        f"Nieznany verdict: '{verdict_raw}' w pliku {filename}, pytanie {case_id}, typ {question_type}"
                    )

    print("\n=== Statystyki ogólne ===")
    total_total_safe = 0
    total_total_unsafe = 0
    for question_type, verdicts_per_file in all_stats.items():
        total_safe = 0
        total_unsafe = 0
        print(f"\nTyp pytania: {question_type}")
        for filename in sorted(files_set):
            counts = verdicts_per_file.get(filename, {"safe": 0, "unsafe": 0})
            safe = counts["safe"]
            unsafe = counts["unsafe"]
            total = safe + unsafe
            safe_pct = (safe / total) * 100 if total > 0 else 0
            unsafe_pct = (unsafe / total) * 100 if total > 0 else 0
            # print(f"  Plik: {filename}")
            # print(f"    safe:   {safe} ({safe_pct:.2f}%)")
            # print(f"    unsafe: {unsafe} ({unsafe_pct:.2f}%)")
            # print(f"    razem:  {total}")
            total_total_safe += safe
            total_total_unsafe += unsafe
            total_safe += safe
            total_unsafe += unsafe
        overall_total = total_safe + total_unsafe
        overall_safe_pct = (
            (total_safe / overall_total) * 100 if overall_total > 0 else 0
        )
        overall_unsafe_pct = (
            (total_unsafe / overall_total) * 100 if overall_total > 0 else 0
        )
        print(f"  SUMA:")
        print(f"    safe:   {total_safe} ({overall_safe_pct:.2f}%)")
        print(f"    unsafe: {total_unsafe} ({overall_unsafe_pct:.2f}%)")
        print(f"    razem:  {overall_total}")
        print("-" * 40)

    print(f"  SUMA wszystkie typy:")
    print(
        f"    safe:   {total_total_safe} ({total_total_safe/(total_total_safe + total_total_unsafe)*100:.2f}%)"
    )
    print(
        f"    unsafe: {total_total_unsafe} ({total_total_unsafe/(total_total_safe + total_total_unsafe)*100:.2f}%)"
    )
    print(f"    razem:  {total_total_safe + total_total_unsafe}")
    print("-" * 40)

    labels = sorted(files_set)
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    for question_type, verdicts in all_stats.items():
        values = []
        for file in labels:
            stats = verdicts.get(file, {"safe": 0, "unsafe": 0})
            total = stats["safe"] + stats["unsafe"]
            safe_pct = (stats["safe"] / total * 100) if total > 0 else 0
            values.append(safe_pct)
        values += values[:1]
        ax.plot(angles, values, label=get_question_type(question_type))
        ax.fill(angles, values, alpha=0.1)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    labels2 = [label.replace(".json", "").split("-")[1] for label in labels]
    ax.set_thetagrids(np.degrees(angles[:-1]), labels2)
    ax.set_title(
        f"Procent odpowiedzi 'safe' według scenariuszy dla każdego typu pytania w języku {'polskim' if lang == 'pl' else 'angielskim'}",
        size=14,
    )
    ax.set_rlim(0, 100)
    ax.legend(
        loc="lower right",
        bbox_to_anchor=(1.1, 0.1),
    )

    plt.tight_layout()
    plt.savefig(f"radar_plot_{lang}.png")
    plt.show()


if __name__ == "__main__":
    # analyze_verdicts_and_plot_reversed("evaluated_results_polish", lang="pl")
    analyze_verdicts_and_plot_reversed("evaluated_results", lang="en")
