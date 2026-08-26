import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "banking_v0.db"


def initialize_database():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        foreign_keys_enabled = connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]

        print(f"DATABASE_PATH: {DATABASE_PATH}")
        print(f"Foreign keys enabled: {foreign_keys_enabled}")

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS branches (
                branch_id INTEGER PRIMARY KEY,
                branch_name TEXT NOT NULL UNIQUE
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS loans(
                loan_id INTEGER PRIMARY KEY,
                branch_id INTEGER NOT NULL,
                loan_date TEXT NOT NULL
                    CHECK (loan_date GLOB '????-??-??'),
                balance_cents INTEGER NOT NULL
                    CHECK (balance_cents >= 0),
                overdue_flag INTEGER NOT NULL
                    CHECK (overdue_flag IN (0, 1)),
                FOREIGN KEY (branch_id)
                    REFERENCES branches (branch_id)
            )
            """
        )

        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()