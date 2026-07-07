"""
Tech Job Market Analytics
Analyzes tech job posting data to surface insights about:
- Most in-demand skills
- Salary ranges by role and location
- Remote vs on-site trends
- OPT/visa-friendly employer patterns

Author: Diana Martinez
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from datetime import datetime


# ──────────────────────────────────────────────
# Sample Dataset — realistic tech job postings
# ──────────────────────────────────────────────

SAMPLE_JOBS = [
    # (title, company, location, remote, salary_min, salary_max, skills, visa_sponsor, date_posted, experience_years)
    ("Junior Software Engineer",     "Salesforce",       "San Francisco, CA", True,  95000,  130000, "Python,Java,SQL,REST APIs,Git",              True,  "2026-05-01", 0),
    ("Software Engineer",            "Microsoft",        "Seattle, WA",       True,  110000, 160000, "Python,C#,Azure,SQL,Git,Docker",             True,  "2026-05-03", 2),
    ("Junior Data Analyst",          "Capital One",      "McLean, VA",        False, 70000,  95000,  "SQL,Python,Tableau,Excel,Git",               True,  "2026-05-05", 0),
    ("Full Stack Developer",         "Shopify",          "Remote",            True,  100000, 140000, "JavaScript,React,Node.js,SQL,Docker",        True,  "2026-05-06", 2),
    ("Backend Engineer",             "Stripe",           "New York, NY",      True,  120000, 170000, "Python,Go,PostgreSQL,Docker,Kubernetes",     True,  "2026-05-07", 3),
    ("Junior Frontend Developer",    "HubSpot",          "Remote",            True,  75000,  100000, "JavaScript,React,TypeScript,CSS,HTML",       True,  "2026-05-08", 0),
    ("Data Engineer",                "Airbnb",           "San Francisco, CA", True,  130000, 175000, "Python,SQL,Spark,Airflow,AWS",               True,  "2026-05-09", 3),
    ("Software Engineer I",          "Amazon",           "Seattle, WA",       False, 115000, 155000, "Java,Python,AWS,SQL,Git",                    True,  "2026-05-10", 1),
    ("Junior Python Developer",      "EagleForce",       "Herndon, VA",       False, 55000,  75000,  "Python,Flask,SQL,REST APIs,Git",             False, "2026-05-11", 0),
    ("Data Analyst",                 "Deloitte",         "Washington, DC",    False, 65000,  90000,  "SQL,Python,Tableau,Excel,PowerBI",           True,  "2026-05-12", 1),
    ("Software Engineer",            "GitHub",           "Remote",            True,  110000, 150000, "Python,Ruby,JavaScript,Docker,Git",          True,  "2026-05-13", 2),
    ("Junior Backend Developer",     "Twilio",           "Remote",            True,  85000,  110000, "Python,Node.js,REST APIs,SQL,Git",           True,  "2026-05-14", 0),
    ("ML Engineer",                  "OpenAI",           "San Francisco, CA", True,  150000, 200000, "Python,PyTorch,SQL,Docker,AWS",              True,  "2026-05-15", 3),
    ("Software Engineer",            "Pivotly",          "Remote",            True,  90000,  130000, "JavaScript,TypeScript,React,Python,SQL",     False, "2026-05-16", 1),
    ("Junior Data Engineer",         "Snowflake",        "Remote",            True,  95000,  125000, "Python,SQL,Spark,dbt,Git",                   True,  "2026-05-17", 0),
    ("Full Stack Engineer",          "Runpod",           "Remote",            True,  130000, 200000, "Python,TypeScript,Go,Docker,SQL",            False, "2026-05-18", 1),
    ("Software Engineer",            "IBM",              "Austin, TX",        True,  95000,  135000, "Java,Python,SQL,Docker,Git",                 True,  "2026-05-19", 2),
    ("Junior Software Engineer",     "Visa Inc.",        "Bellevue, WA",      False, 85000,  115000, "Python,JavaScript,SQL,REST APIs,Git",        True,  "2026-05-20", 0),
    ("Data Scientist",               "Netflix",          "Los Gatos, CA",     True,  140000, 190000, "Python,R,SQL,Spark,TensorFlow",              True,  "2026-05-21", 3),
    ("Backend Developer",            "Cloudflare",       "Remote",            True,  110000, 150000, "Go,Python,Rust,Docker,SQL",                  True,  "2026-05-22", 2),
    ("Junior Software Developer",    "MobileIT",         "Remote",            True,  60000,  80000,  "JavaScript,React,SQL,Node.js,Git",           False, "2026-05-23", 0),
    ("Software Engineer",            "Figma",            "San Francisco, CA", True,  120000, 165000, "TypeScript,React,Python,SQL,Docker",         True,  "2026-05-24", 2),
    ("Data Analyst",                 "Spotify",          "New York, NY",      True,  80000,  110000, "SQL,Python,Tableau,Git,Excel",               True,  "2026-05-25", 1),
    ("Junior DevOps Engineer",       "HashiCorp",        "Remote",            True,  90000,  120000, "Docker,Kubernetes,Python,Terraform,Git",     True,  "2026-05-26", 0),
    ("Software Engineer",            "Anthropic",        "San Francisco, CA", True,  140000, 200000, "Python,C++,SQL,Docker,Git",                  True,  "2026-05-27", 2),
    ("Junior Full Stack Developer",  "Delta Dental",     "Remote",            True,  70000,  95000,  "JavaScript,TypeScript,Python,SQL,Git",       True,  "2026-05-28", 0),
    ("Analytics Engineer",           "HelioCampus",      "Bethesda, MD",      True,  85000,  115000, "SQL,Python,dbt,Tableau,Git",                 False, "2026-05-29", 2),
    ("Software Engineer",            "Palantir",         "Denver, CO",        False, 120000, 160000, "Java,Python,SQL,Docker,Git",                 True,  "2026-05-30", 2),
    ("Junior Software Engineer",     "ServiceNow",       "Santa Clara, CA",   False, 95000,  130000, "Java,JavaScript,SQL,REST APIs,Git",          True,  "2026-06-01", 0),
    ("Data Engineer",                "Databricks",       "Remote",            True,  130000, 175000, "Python,Spark,SQL,dbt,Docker",                True,  "2026-06-02", 2),
]


# ──────────────────────────────────────────────
# Database Setup
# ──────────────────────────────────────────────

def create_database(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id              INTEGER PRIMARY KEY,
            title           TEXT NOT NULL,
            company         TEXT NOT NULL,
            location        TEXT NOT NULL,
            remote          INTEGER DEFAULT 0,
            salary_min      INTEGER,
            salary_max      INTEGER,
            salary_avg      INTEGER,
            skills          TEXT,
            visa_sponsor    INTEGER DEFAULT 0,
            date_posted     TEXT,
            experience_years INTEGER DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id       INTEGER PRIMARY KEY,
            job_id   INTEGER REFERENCES jobs(id),
            skill    TEXT NOT NULL
        )
    """)

    for job in SAMPLE_JOBS:
        title, company, location, remote, sal_min, sal_max, skills, visa, date, exp = job
        sal_avg = (sal_min + sal_max) // 2
        cursor = conn.execute("""
            INSERT INTO jobs (title, company, location, remote, salary_min, salary_max,
                              salary_avg, skills, visa_sponsor, date_posted, experience_years)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, company, location, int(remote), sal_min, sal_max,
              sal_avg, skills, int(visa), date, exp))

        job_id = cursor.lastrowid
        for skill in skills.split(","):
            conn.execute("INSERT INTO skills (job_id, skill) VALUES (?, ?)",
                         (job_id, skill.strip()))

    conn.commit()


# ──────────────────────────────────────────────
# SQL Queries
# ──────────────────────────────────────────────

QUERIES = {
    "summary": """
        SELECT
            COUNT(*)                                            AS total_jobs,
            ROUND(AVG(salary_avg), 0)                           AS avg_salary,
            ROUND(AVG(salary_min), 0)                           AS avg_salary_min,
            ROUND(AVG(salary_max), 0)                           AS avg_salary_max,
            SUM(CASE WHEN remote = 1 THEN 1 ELSE 0 END)        AS remote_count,
            SUM(CASE WHEN visa_sponsor = 1 THEN 1 ELSE 0 END)  AS visa_sponsor_count,
            SUM(CASE WHEN experience_years = 0 THEN 1 ELSE 0 END) AS entry_level_count
        FROM jobs
    """,

    "salary_by_role": """
        SELECT
            CASE
                WHEN title LIKE '%Junior%' OR title LIKE '%Jr%' THEN 'Junior'
                WHEN title LIKE '%Senior%' OR title LIKE '%Sr%' THEN 'Senior'
                WHEN title LIKE '%Data%'  THEN 'Data'
                WHEN title LIKE '%ML%' OR title LIKE '%Machine%' THEN 'ML/AI'
                ELSE 'Mid-level'
            END AS role_level,
            COUNT(*) AS count,
            ROUND(AVG(salary_avg), 0) AS avg_salary,
            ROUND(MIN(salary_min), 0) AS min_salary,
            ROUND(MAX(salary_max), 0) AS max_salary
        FROM jobs
        GROUP BY role_level
        ORDER BY avg_salary DESC
    """,

    "top_skills": """
        SELECT skill, COUNT(*) AS demand_count
        FROM skills
        GROUP BY skill
        ORDER BY demand_count DESC
        LIMIT 15
    """,

    "remote_vs_onsite": """
        SELECT
            CASE WHEN remote = 1 THEN 'Remote' ELSE 'On-site' END AS work_type,
            COUNT(*) AS count,
            ROUND(AVG(salary_avg), 0) AS avg_salary
        FROM jobs
        GROUP BY remote
    """,

    "visa_friendly": """
        SELECT
            CASE WHEN visa_sponsor = 1 THEN 'Sponsors Visa' ELSE 'No Sponsorship' END AS sponsorship,
            COUNT(*) AS count,
            ROUND(AVG(salary_avg), 0) AS avg_salary
        FROM jobs
        GROUP BY visa_sponsor
        ORDER BY visa_sponsor DESC
    """,

    "top_companies": """
        SELECT company, salary_avg, remote, visa_sponsor, title
        FROM jobs
        WHERE experience_years <= 1
        ORDER BY salary_avg DESC
        LIMIT 10
    """,

    "entry_level_remote_visa": """
        SELECT title, company, location, salary_min, salary_max, skills
        FROM jobs
        WHERE experience_years <= 1
          AND remote = 1
          AND visa_sponsor = 1
        ORDER BY salary_avg DESC
    """,

    "salary_by_location": """
        SELECT
            CASE
                WHEN location = 'Remote' OR remote = 1 THEN 'Remote'
                WHEN location LIKE '%CA%' THEN 'California'
                WHEN location LIKE '%WA%' THEN 'Washington'
                WHEN location LIKE '%NY%' THEN 'New York'
                WHEN location LIKE '%VA%' OR location LIKE '%DC%' OR location LIKE '%MD%' THEN 'DMV Area'
                ELSE 'Other'
            END AS region,
            COUNT(*) AS jobs,
            ROUND(AVG(salary_avg), 0) AS avg_salary
        FROM jobs
        GROUP BY region
        ORDER BY avg_salary DESC
    """
}


# ──────────────────────────────────────────────
# Visualizations
# ──────────────────────────────────────────────

def generate_charts(conn: sqlite3.Connection, output_dir: Path) -> None:
    output_dir.mkdir(exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    # 1. Top 15 most in-demand skills
    df = pd.read_sql_query(QUERIES["top_skills"], conn)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#e74c3c" if i < 3 else "#3498db" if i < 8 else "#95a5a6"
              for i in range(len(df))]
    ax.barh(df["skill"][::-1], df["demand_count"][::-1], color=colors[::-1], edgecolor="white")
    ax.set_title("Top 15 Most In-Demand Tech Skills (2026)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Number of Job Postings Requiring This Skill")
    for i, (_, row) in enumerate(df[::-1].iterrows()):
        ax.text(row["demand_count"] + 0.1, i, str(row["demand_count"]), va="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_dir / "top_skills.png", dpi=150)
    plt.close()

    # 2. Salary ranges by role level
    df = pd.read_sql_query(QUERIES["salary_by_role"], conn)
    fig, ax = plt.subplots(figsize=(9, 5))
    x = range(len(df))
    ax.bar(x, df["max_salary"], color="#3498db", alpha=0.4, label="Max Salary")
    ax.bar(x, df["avg_salary"], color="#2980b9", label="Avg Salary")
    ax.bar(x, df["min_salary"], color="#1a5276", alpha=0.7, label="Min Salary")
    ax.set_xticks(list(x))
    ax.set_xticklabels(df["role_level"], fontsize=11)
    ax.set_title("Salary Ranges by Role Level", fontsize=14, fontweight="bold")
    ax.set_ylabel("Salary (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "salary_by_role.png", dpi=150)
    plt.close()

    # 3. Remote vs On-site
    df = pd.read_sql_query(QUERIES["remote_vs_onsite"], conn)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    ax1.pie(df["count"], labels=df["work_type"],
            colors=["#2ecc71", "#e74c3c"], autopct="%1.0f%%",
            startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 2})
    ax1.set_title("Remote vs On-site Distribution", fontweight="bold")
    ax2.bar(df["work_type"], df["avg_salary"],
            color=["#2ecc71", "#e74c3c"], edgecolor="white", width=0.4)
    ax2.set_title("Avg Salary: Remote vs On-site", fontweight="bold")
    ax2.set_ylabel("Avg Salary (USD)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    for i, (_, row) in enumerate(df.iterrows()):
        ax2.text(i, row["avg_salary"] + 1000, f"${row['avg_salary']:,.0f}",
                 ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(output_dir / "remote_vs_onsite.png", dpi=150)
    plt.close()

    # 4. Visa sponsorship analysis
    df = pd.read_sql_query(QUERIES["visa_friendly"], conn)
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["#27ae60", "#e74c3c"]
    bars = ax.bar(df["sponsorship"], df["count"], color=colors, edgecolor="white", width=0.4)
    ax.set_title("Visa Sponsorship Availability in Tech Jobs", fontsize=13, fontweight="bold")
    ax.set_ylabel("Number of Job Postings")
    for bar, (_, row) in zip(bars, df.iterrows()):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.2,
                f"{row['count']} jobs\nAvg: ${row['avg_salary']:,.0f}",
                ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(output_dir / "visa_sponsorship.png", dpi=150)
    plt.close()

    # 5. Salary by region
    df = pd.read_sql_query(QUERIES["salary_by_location"], conn)
    fig, ax = plt.subplots(figsize=(9, 5))
    bar_colors = ["#e74c3c" if r == "Remote" else "#3498db" for r in df["region"]]
    ax.bar(df["region"], df["avg_salary"], color=bar_colors, edgecolor="white")
    ax.set_title("Average Tech Salary by Region", fontsize=14, fontweight="bold")
    ax.set_ylabel("Average Salary (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(i, row["avg_salary"] + 500, f"${row['avg_salary']:,.0f}\n({row['jobs']} jobs)",
                ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_dir / "salary_by_region.png", dpi=150)
    plt.close()

    print(f"✅ 5 charts saved to {output_dir}/")


# ──────────────────────────────────────────────
# Console Report
# ──────────────────────────────────────────────

def print_report(conn: sqlite3.Connection) -> None:
    print("\n" + "=" * 60)
    print("  TECH JOB MARKET ANALYTICS REPORT — 2026")
    print("=" * 60)

    s = pd.read_sql_query(QUERIES["summary"], conn).iloc[0]
    print(f"\n📊 MARKET OVERVIEW")
    print(f"  Total Jobs Analyzed:     {int(s['total_jobs'])}")
    print(f"  Average Salary:          ${int(s['avg_salary']):,}")
    print(f"  Salary Range:            ${int(s['avg_salary_min']):,} — ${int(s['avg_salary_max']):,}")
    print(f"  Remote Positions:        {int(s['remote_count'])} ({int(s['remote_count'])/int(s['total_jobs'])*100:.0f}%)")
    print(f"  Visa Sponsors:           {int(s['visa_sponsor_count'])} ({int(s['visa_sponsor_count'])/int(s['total_jobs'])*100:.0f}%)")
    print(f"  Entry-Level Positions:   {int(s['entry_level_count'])}")

    print(f"\n🎯 BEST JOBS FOR OPT/INTERNATIONAL CANDIDATES (Entry-Level + Remote + Visa)")
    df = pd.read_sql_query(QUERIES["entry_level_remote_visa"], conn)
    for _, row in df.iterrows():
        print(f"  ✅ {row['title']} @ {row['company']}")
        print(f"     ${row['salary_min']:,}–${row['salary_max']:,} | Skills: {row['skills'][:50]}...")

    print(f"\n💰 SALARY BY ROLE LEVEL")
    df = pd.read_sql_query(QUERIES["salary_by_role"], conn)
    for _, row in df.iterrows():
        print(f"  {row['role_level']:<12} Avg: ${int(row['avg_salary']):>9,}  "
              f"(${int(row['min_salary']):,}–${int(row['max_salary']):,})")

    print(f"\n🔧 TOP 10 IN-DEMAND SKILLS")
    df = pd.read_sql_query(QUERIES["top_skills"], conn)
    for i, (_, row) in enumerate(df.head(10).iterrows(), 1):
        bar = "█" * row["demand_count"]
        print(f"  {i:>2}. {row['skill']:<20} {bar} ({row['demand_count']})")

    print("\n" + "=" * 60)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    create_database(conn)
    print_report(conn)
    generate_charts(conn, Path("outputs"))
    conn.close()
