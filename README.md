# 💬 Talking with Database
### Modern Streamlit UI + Gemini AI + SQLite

This redesigned version uses a modern glassmorphism UI with a moving animated background, hero landing section, polished cards, sidebar schema explorer, sample prompt buttons, and dashboard-style query output.

## Project Structure

```text
talking_with_database/
├── app.py            # Redesigned Streamlit app UI + query workflow
├── db_setup.py       # SQLite database creation + sample data
├── requirements.txt  # Python dependencies
└── README.md
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Optional: Set Gemini API key

Without an API key, the app still opens in demo mode and supports the sample questions.

```bash
# Linux / macOS
export GEMINI_API_KEY="your-gemini-api-key"

# Windows PowerShell
$env:GEMINI_API_KEY="your-gemini-api-key"
```

### 3. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## UI/UX Changes Added

- Animated moving background with glowing gradient layers
- Glassmorphism hero card and dashboard layout
- Custom Google Fonts: Inter + Space Grotesk
- Sidebar schema explorer with modern chips
- AI/SQL/DB visual graphic in the hero section
- Modern rounded buttons, tabs, result cards, and query workspace
- Demo mode fallback when `GEMINI_API_KEY` is not set

## Database Schema

The app creates a local SQLite file named `company.db`.

| Table | Columns |
|---|---|
| `employees` | id, name, department, salary, hire_date, email |
| `departments` | id, name, manager_id, budget, location |
| `projects` | id, title, department_id, start_date, end_date, status |
| `sales` | id, employee_id, amount, product, sale_date, region |

## Sample Questions

- Show all employees in Engineering
- Average salary by department
- Top 5 sales by amount
- Active projects count
- Employees hired after 2022
- Which department has the highest budget?
- Total sales amount per region
