# Tech Job Market Analytics 📊

A data analytics pipeline that analyzes **2026 tech job posting data** to surface insights about in-demand skills, salary trends, remote work patterns, and visa sponsorship availability — with a special focus on **OPT/international candidate opportunities**.

Built with **Python**, **SQL (SQLite)**, **pandas**, and **matplotlib**.

---

## Why This Project

As an international CS graduate navigating the tech job market on F-1 OPT, I built this project to answer real questions:
- Which skills are employers actually hiring for?
- What's the salary range for entry-level roles?
- How many companies offer visa sponsorship?
- Where are the best remote + visa-friendly opportunities?

---

## Features

- Relational SQLite database with `jobs` and `skills` tables
- 30 realistic tech job postings across companies (Salesforce, Microsoft, Amazon, Runpod, etc.)
- 8 analytical SQL queries (aggregations, JOINs, CASE expressions, subqueries)
- 5 data visualizations (skills demand, salary ranges, remote/on-site, visa sponsorship, regional salary)
- OPT/visa-friendly job filter — entry level + remote + sponsorship
- Formatted console report
- 11 pytest tests
- GitHub Actions CI

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.12 | Core language |
| SQLite | Embedded relational database |
| pandas | Data manipulation and SQL query results |
| matplotlib | Data visualizations |
| pytest | Testing |
| GitHub Actions | CI/CD |

---

## Getting Started

```bash
git clone https://github.com/DianaM12-2/job-market-analytics.git
cd job-market-analytics
pip install -r requirements.txt
python src/analytics.py
```

Charts saved to `/outputs/`. Console report prints automatically.

### Run tests
```bash
pytest tests/ -v
```

---

## Sample Output

```
============================================================
  TECH JOB MARKET ANALYTICS REPORT — 2026
============================================================

📊 MARKET OVERVIEW
  Total Jobs Analyzed:     30
  Average Salary:          $113,567
  Salary Range:            $55,000 — $200,000
  Remote Positions:        22 (73%)
  Visa Sponsors:           24 (80%)
  Entry-Level Positions:   10

🎯 BEST JOBS FOR OPT/INTERNATIONAL CANDIDATES
  ✅ Junior Software Engineer @ Visa Inc.
  ✅ Junior Frontend Developer @ HubSpot
  ✅ Junior Backend Developer @ Twilio
  ...

🔧 TOP 10 IN-DEMAND SKILLS
   1. Python               ████████████████████ (20)
   2. SQL                  ████████████████████ (20)
   3. Git                  ███████████████████  (19)
   4. Docker               ████████████         (12)
   ...
```

---

## Charts Generated

- `top_skills.png` — Top 15 most in-demand tech skills
- `salary_by_role.png` — Salary ranges by role level (Junior/Mid/Senior/Data/ML)
- `remote_vs_onsite.png` — Remote vs on-site distribution + salary comparison
- `visa_sponsorship.png` — Visa sponsorship availability and salary impact
- `salary_by_region.png` — Average salary by geographic region

---

## Author

**Diana Martinez** — CS Graduate (Magna Cum Laude), University of the District of Columbia
[GitHub](https://github.com/DianaM12-2) · [LinkedIn](https://linkedin.com/in/diana-martinez-s) · [Portfolio](https://dianam12-2.github.io)
