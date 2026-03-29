from pathlib import Path
import glob
import subprocess
import pymysql
import json
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
PROBLEMS_DIR = Path("problems")

def get_db_connection():
    return pymysql.connect(
        host='db',
        user='user',
        password='password',
        database='judge_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 1. トップページ：難易度（A〜E）を選ばせる
@app.route("/")
def home():
    # 難易度のリストをHTMLに渡す
    difficulties = ["A", "B", "C", "D", "E"]
    return render_template("index.html", difficulties=difficulties)

# 2. 難易度別の問題一覧ページ（例：/difficulty/A にアクセスした時）
@app.route("/difficulty/<level>")
def show_difficulty(level):
    problems = []
    if PROBLEMS_DIR.exists():
        for p_dir in PROBLEMS_DIR.iterdir():
            if p_dir.is_dir():
                json_file = p_dir / "problem.json"
                if json_file.exists():
                    try:
                        with open(json_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if data.get("difficulty") == level:
                                problems.append(data)
                    except Exception as e:
                        print(f"Error reading {json_file}: {e}")
    
    problems.sort(key=lambda x: x.get("problem_id", ""))

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT problem_id FROM submissions WHERE status = 'AC'")
            ac_records = cursor.fetchall()
            ac_set = {record['problem_if'] for record in ac_records}
        conn.close()

        for p in problems:
            p["is_ac"] = p["problem_id"] in ac_set
    except Exception as e:
        print("DB Error:", e)

    return render_template("list.html", level=level, problems=problems)


# 3. 提出ページ
@app.route("/problem/<problem_id>")
def show_problem(problem_id):
    json_file = PROBLEMS_DIR / problem_id / "problem.json"
    if not json_file.exists():
        return "問題が見つかりません", 404
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            problem= json.load(f)
    except Exception as e:
        print(f"Error reading {json_file}: {e}")
        return "問題の読み込みに失敗しました", 500
           
    return render_template("problem.html", problem=problem)

@app.route("/submit", methods=["POST"])
def submit_code():
    data = request.get_json()
    language = data.get("language")
    source_code = data.get("code")
    problem_id = data.get("problem_id")

    test_case_dir = Path("test_cases") / problem_id
    in_dir = test_case_dir / "in"
    out_dir = test_case_dir / "out"

    if not (in_dir.exists() and out_dir.exists()):
        return jsonify({
            "status": "Error",
            "output": "Test cases not found for problem_id: {}".format(problem_id)
        })
    
    test_cases = []
    for in_path in sorted(in_dir.glob("*.txt")):
        out_oath = out_dir / in_path.name
        if out_oath.exists():
            test_cases.append({
                "name": in_path.name,
                "input_data": in_path.read_text(encoding="utf-8"),
                "expected_output": out_oath.read_text(encoding="utf-8")
            })

    if language == "python":
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(source_code)
        exec_command = ["python3", "main.py"]

    elif language == "rust":
        with open("main.rs", "w", encoding="utf-8") as f:
            f.write(source_code)
        # Rustコードをコンパイル
        compile_result = subprocess.run(
            ["/root/.cargo/bin/rustc", "main.rs", "-o", "main"],
            capture_output=True,
            text=True
            )
        
        if compile_result.returncode != 0:
            return jsonify({
                "status": "CE",
                "output": compile_result.stderr,
            })
        exec_command = ["./main"]

    else:
        return jsonify({
            "status": "Error",
            "output": "Unsupported language"
        })
    
    status = "AC"
    output = "Accepted"

    for i, tc in enumerate(test_cases):
        try:
            result = subprocess.run(
                exec_command,
                input = tc["input_data"],
                capture_output = True,
                text = True,
                timeout = 2.0
            )

            if result.returncode == 0:
                if result.stdout.strip() == tc["expected_output"].strip():
                    continue
                else:
                    status = "WA"
                    output = "Not Output"
                    break
            else:
                status = "RE"
                output = result.stderr
                break

        except subprocess.TimeoutExpired:
            status = "TLE"
            output = "Time Limit Exceeded"
            break
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO submissions (problem_id, status) VALUES (%s, %s)",
                (problem_id, status)
            )
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB Error:", e)

    return jsonify({
        "status": status,
        "output": output,
        "received_language": language
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

