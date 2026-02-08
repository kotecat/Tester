import sqlite3

from config import DB_NAME


def get_connection(db_path: str = DB_NAME) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            questions INTEGER NOT NULL,
            time_limit INTEGER NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            q_text TEXT NOT NULL,
            FOREIGN KEY (test_id)
                REFERENCES tests(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            a_text TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            FOREIGN KEY (question_id)
                REFERENCES questions(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            group_name TEXT,
            score INTEGER NOT NULL,
            max_score INTEGER NOT NULL,
            time_taken INTEGER NOT NULL,
            taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (test_id)
                REFERENCES tests(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
        """
    )
    conn.commit()
