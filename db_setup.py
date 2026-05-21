import sqlite3
import os

DB_PATH = "company.db"

TABLES = {
    "employees": ["id", "name", "department", "salary", "hire_date", "email"],
    "departments": ["id", "name", "manager_id", "budget", "location"],
    "projects": ["id", "title", "department_id", "start_date", "end_date", "status"],
    "sales": ["id", "employee_id", "amount", "product", "sale_date", "region"],
}


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    _seed(conn)
    return conn


def _seed(conn):
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            manager_id INTEGER,
            budget REAL,
            location TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            salary REAL NOT NULL,
            hire_date TEXT NOT NULL,
            email TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            department_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'active'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            amount REAL,
            product TEXT,
            sale_date TEXT,
            region TEXT
        )
    """)

    # Seed only if empty
    if cur.execute("SELECT COUNT(*) FROM employees").fetchone()[0] == 0:
        departments = [
            (1, "Engineering",  None,  850000, "Bangalore"),
            (2, "Sales",        None,  620000, "Mumbai"),
            (3, "Marketing",    None,  430000, "Delhi"),
            (4, "HR",           None,  280000, "Hyderabad"),
            (5, "Data Science", None,  540000, "Pune"),
        ]
        cur.executemany("INSERT INTO departments VALUES (?,?,?,?,?)", departments)

        employees = [
            (1,  "Arjun Sharma",   "Engineering",  95000, "2021-03-15", "arjun@company.com"),
            (2,  "Priya Nair",     "Engineering",  88000, "2020-07-01", "priya@company.com"),
            (3,  "Rahul Gupta",    "Sales",        72000, "2022-01-10", "rahul@company.com"),
            (4,  "Sneha Pillai",   "Sales",        68000, "2022-05-20", "sneha@company.com"),
            (5,  "Vikram Singh",   "Marketing",    61000, "2019-11-03", "vikram@company.com"),
            (6,  "Anita Desai",    "HR",           55000, "2021-08-17", "anita@company.com"),
            (7,  "Karan Mehta",    "Data Science", 92000, "2023-02-28", "karan@company.com"),
            (8,  "Divya Rao",      "Data Science", 87000, "2022-09-12", "divya@company.com"),
            (9,  "Suresh Kumar",   "Engineering",  78000, "2020-04-22", "suresh@company.com"),
            (10, "Meera Joshi",    "Marketing",    59000, "2023-06-05", "meera@company.com"),
            (11, "Aakash Verma",   "Sales",        74000, "2021-12-01", "aakash@company.com"),
            (12, "Pooja Iyer",     "Data Science", 96000, "2022-03-14", "pooja@company.com"),
        ]
        cur.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?)", employees)

        projects = [
            (1, "Cloud Migration",       1, "2024-01-01", "2024-06-30", "completed"),
            (2, "CRM Revamp",            2, "2024-03-01", None,         "active"),
            (3, "AI Hiring Assistant",   5, "2024-04-01", None,         "active"),
            (4, "Brand Refresh",         3, "2023-10-01", "2024-02-28", "completed"),
            (5, "Data Warehouse Build",  5, "2024-05-01", None,         "active"),
            (6, "Mobile App v2",         1, "2024-02-15", None,         "active"),
            (7, "Sales Analytics Dashboard", 5, "2024-06-01", None,    "active"),
        ]
        cur.executemany("INSERT INTO projects VALUES (?,?,?,?,?,?)", projects)

        sales = [
            (1,  3,  145000, "Enterprise License", "2024-01-15", "North"),
            (2,  4,   87000, "SaaS Subscription",  "2024-02-10", "South"),
            (3,  3,  210000, "Enterprise License", "2024-02-28", "West"),
            (4,  11, 320000, "Consulting Package", "2024-03-05", "North"),
            (5,  4,   55000, "SaaS Subscription",  "2024-03-18", "East"),
            (6,  3,  175000, "Enterprise License", "2024-04-02", "West"),
            (7,  11, 430000, "Enterprise License", "2024-04-20", "North"),
            (8,  4,   98000, "Consulting Package", "2024-05-01", "South"),
            (9,  3,  260000, "Enterprise License", "2024-05-15", "East"),
            (10, 11, 510000, "Enterprise License", "2024-06-10", "North"),
        ]
        cur.executemany("INSERT INTO sales VALUES (?,?,?,?,?,?)", sales)

        conn.commit()


def get_schema_description(conn):
    cur = conn.cursor()
    lines = []
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    for tbl in tables:
        cur.execute(f"PRAGMA table_info({tbl})")
        cols = cur.fetchall()
        col_str = ", ".join(f"{c[1]} ({c[2]})" for c in cols)
        lines.append(f"- {tbl}({col_str})")
    return "\n".join(lines)
