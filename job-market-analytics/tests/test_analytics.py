import sqlite3
import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.analytics import create_database, QUERIES, SAMPLE_JOBS


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    create_database(c)
    yield c
    c.close()


def test_database_seeded(conn):
    count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    assert count == len(SAMPLE_JOBS)


def test_skills_table_populated(conn):
    count = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
    assert count > 0


def test_summary_query(conn):
    df = pd.read_sql_query(QUERIES["summary"], conn)
    assert int(df["total_jobs"].iloc[0]) == len(SAMPLE_JOBS)
    assert float(df["avg_salary"].iloc[0]) > 0
    assert int(df["remote_count"].iloc[0]) > 0
    assert int(df["visa_sponsor_count"].iloc[0]) > 0


def test_top_skills_query(conn):
    df = pd.read_sql_query(QUERIES["top_skills"], conn)
    assert len(df) <= 15
    assert "skill" in df.columns
    assert "demand_count" in df.columns
    counts = df["demand_count"].tolist()
    assert counts == sorted(counts, reverse=True)


def test_python_is_top_skill(conn):
    df = pd.read_sql_query(QUERIES["top_skills"], conn)
    top_skills = df["skill"].tolist()
    assert "Python" in top_skills[:5]


def test_remote_vs_onsite(conn):
    df = pd.read_sql_query(QUERIES["remote_vs_onsite"], conn)
    assert len(df) == 2
    work_types = df["work_type"].tolist()
    assert "Remote" in work_types
    assert "On-site" in work_types


def test_visa_friendly_query(conn):
    df = pd.read_sql_query(QUERIES["visa_friendly"], conn)
    assert len(df) == 2
    sponsors = df["sponsorship"].tolist()
    assert "Sponsors Visa" in sponsors


def test_entry_level_remote_visa(conn):
    df = pd.read_sql_query(QUERIES["entry_level_remote_visa"], conn)
    assert len(df) > 0
    for _, row in df.iterrows():
        # Verify all returned jobs match our criteria
        job = conn.execute(
            "SELECT experience_years, remote, visa_sponsor FROM jobs WHERE title=? AND company=?",
            (row["title"], row["company"])
        ).fetchone()
        assert job[0] <= 1   # entry level
        assert job[1] == 1   # remote
        assert job[2] == 1   # visa sponsor


def test_salary_by_role(conn):
    df = pd.read_sql_query(QUERIES["salary_by_role"], conn)
    assert len(df) > 0
    assert "avg_salary" in df.columns
    assert "role_level" in df.columns


def test_salary_by_location(conn):
    df = pd.read_sql_query(QUERIES["salary_by_location"], conn)
    assert len(df) > 0
    assert "region" in df.columns
    assert "avg_salary" in df.columns


def test_all_salaries_positive(conn):
    df = pd.read_sql_query("SELECT salary_min, salary_max FROM jobs", conn)
    assert (df["salary_min"] > 0).all()
    assert (df["salary_max"] > 0).all()
    assert (df["salary_max"] >= df["salary_min"]).all()
