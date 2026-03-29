DROP TABLE IF EXISTS submissions;

-- 提出履歴を記録するテーブル
CREATE TABLE submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    problem_id VARCHAR(10) NOT NULL,
    status VARCHAR(5) NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
