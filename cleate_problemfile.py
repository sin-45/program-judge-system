import json
from pathlib import Path

prom = ["A", "B", "C", "D", "E"]
num = 10

for p in prom:
    for i in range(1, num + 1):
        problem_id = f"{p}{i:03d}"
        problem_dir = Path("problems") / p / problem_id
        in_dir = problem_dir / "in"
        out_dir = problem_dir / "out"
        problem_dir.mkdir(parents=True, exist_ok=True)
        in_dir.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)

        problem_data = {
            "problem_id": problem_id,
            "title": "",
            "difficulty": p,
            "description": "",
            "input_format": "",
            "output_format": "",
            "sample_input": "",
            "sample_output": "",
        }

        with open(problem_dir / "cleate_in-out_format.py", "w", encoding="utf-8") as f:
            f.write("")

        with open(problem_dir / "problem.json", "w", encoding="utf-8") as f:
            json.dump(problem_data, f, ensure_ascii=False, indent=4)


