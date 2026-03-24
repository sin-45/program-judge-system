SET NAMES utf8mb4;

-- 1. 新しい問題テーブル
CREATE TABLE problems (
    problem_id VARCHAR(10) PRIMARY KEY,  -- A001 など
    difficulty VARCHAR(2) NOT NULL,      -- A, B, C, D, E
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE test_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    problem_id VARCHAR(10),
    input_data TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);

-- 2. サンプルデータの挿入
INSERT INTO problems (problem_id, difficulty, title, description) VALUES
('A001', 'A', 'Hello World', '"Hello World" と出力してください。'),
('A002', 'A', 'はじめての足し算', '空白区切りの2つの整数 A, B を受け取り、その和を出力してください。'),
('A003', 'A', '文字列の繰り返し', '文字列 S と整数 N が空白区切りで与えられます。S を N 回繰り返して出力してください。'),
('A004', 'A', '偶数だけ出力', '整数 N が与えられます。N が偶数ならそのまま出力し、奇数なら 0 を出力してください。'),
('A005', 'A', '配列の合計', '1行目に要素数 N、2行目に空白区切りの N 個の整数が与えられます。それらの合計値を出力してください。');

-- 3. テストケースの挿入（問題IDと一致するように修正！）
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
-- A001: Hello World (入力は空っぽでOK)
('A001', '\n', 'Hello World'),

-- A002: 足し算
('A002', '10 20\n', '30'),
('A002', '100 200\n', '300'),
('A002', '-5 5\n', '0'),

-- A003: 文字列の繰り返し
('A003', 'abc 3\n', 'abcabcabc'),
('A003', 'AtCoder 2\n', 'AtCoderAtCoder'),
('A003', 'xyz 0\n', ''),

-- A004: 偶数だけ出力
('A004', '4\n', '4'),
('A004', '7\n', '0'),
('A004', '-2\n', '-2'),

-- A005: 配列の合計
('A005', '3\n1 2 3\n', '6'),
('A005', '5\n10 20 30 40 50\n', '150'),
('A005', '4\n-1 -2 -3 -4\n', '-10');
