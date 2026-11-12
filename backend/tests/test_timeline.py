import pytest
from app.services.timeline import (
    parse_date_to_month_index,
    normalize_date_string,
    calculate_employment_duration,
    calculate_total_experience_years
)

def test_parse_date_to_month_index():
    assert parse_date_to_month_index("Jan 2021") == 2021 * 12 + 1
    assert parse_date_to_month_index("December 2022") == 2022 * 12 + 12
    assert parse_date_to_month_index("03/2020") == 2020 * 12 + 3
    assert parse_date_to_month_index("2019-06") == 2019 * 12 + 6
    assert parse_date_to_month_index("2018", is_end=False) == 2018 * 12 + 1
    assert parse_date_to_month_index("2018", is_end=True) == 2018 * 12 + 12

def test_normalize_date_string():
    assert normalize_date_string("March 2021") == "2021-03"
    assert normalize_date_string("08/2019") == "2019-08"
    assert normalize_date_string("Present") == "Present"
    assert normalize_date_string("Current") == "Present"

def test_calculate_employment_duration():
    months, is_curr = calculate_employment_duration("2021-01", "2021-12")
    assert months == 12
    assert is_curr is False

    months, is_curr = calculate_employment_duration("2023-01", "Present")
    assert months >= 12
    assert is_curr is True

def test_calculate_total_experience_years_non_overlapping():
    # Two distinct non-overlapping jobs
    # Job 1: 2020-01 to 2020-12 (12 months = 1 year)
    # Job 2: 2021-01 to 2021-12 (12 months = 1 year)
    jobs = [
        {"start_date": "2020-01", "end_date": "2020-12"},
        {"start_date": "2021-01", "end_date": "2021-12"}
    ]
    total = calculate_total_experience_years(jobs)
    assert total == 2.0

def test_calculate_total_experience_years_overlapping():
    # Overlapping jobs:
    # Job 1: 2020-01 to 2021-06 (18 months)
    # Job 2: 2020-06 to 2021-12 (19 months)
    # Total elapsed interval is 2020-01 to 2021-12 = 24 months = 2.0 years
    # (NOT 18 + 19 = 37 months = 3.1 years!)
    jobs = [
        {"start_date": "2020-01", "end_date": "2021-06"},
        {"start_date": "2020-06", "end_date": "2021-12"}
    ]
    total = calculate_total_experience_years(jobs)
    assert total == 2.0

