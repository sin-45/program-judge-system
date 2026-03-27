import subprocess
import pymysql
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host='db',
        user='judge_user',
        password='judge_password',
        database='online_judge_db',
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
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # 選ばれた難易度（Aなど）の問題だけをDBから取得
        cursor.execute("SELECT * FROM problems WHERE difficulty=%s ORDER BY problem_id", (level,))
        problems = cursor.fetchall()
    conn.close()
    return render_template("list.html", level=level, problems=problems)

# 3. 提出ページ
@app.route("/problem/<problem_id>")
def show_problem(problem_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM problems WHERE problem_id=%s", (problem_id,))
        problem = cursor.fetchone()
    conn.close()
    
    if not problem:
        return "問題が見つかりません", 404
        
    return render_template("problem.html", problem=problem)

@app.route("/submit", methods=["POST"])
def submit_code():
    data = request.get_json()
    language = data.get("language")
    source_code = data.get("code")
    problem_id = data.get("problem_id")

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select input_data, expected_output from test_cases where problem_id=%s", (problem_id,))
            test_cases = cursor.fetchall()
    finally:
        conn.close()


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
        
    return jsonify({
        "status": status,
        "output": output,
        "received_language": language
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

