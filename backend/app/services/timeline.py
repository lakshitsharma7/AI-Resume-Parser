import re
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

MONTH_NAME_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

def parse_date_to_month_index(date_str: Optional[str], is_end: bool = False) -> Optional[int]:
    """
    Parses various date representations into an absolute integer month index (year * 12 + month).
    Returns None if date cannot be parsed.
    """
    if not date_str:
        return None
    
    clean_str = date_str.strip().lower()
    now = datetime.now()
    
    # Check for Present / Current
    if any(p in clean_str for p in ["present", "current", "now", "ongoing", "till date", "today"]):
        return now.year * 12 + now.month
    
    # Check Month Year: "Jan 2021", "January 2021", "Jan-2021", "Jan. 2021"
    match_my = re.search(r'([a-zA-Z]{3,9})[\s,./\-_]+(\d{4})', clean_str)
    if match_my:
        month_name = match_my.group(1).lower()
        year = int(match_my.group(2))
        month = MONTH_NAME_MAP.get(month_name, 1 if not is_end else 12)
        return year * 12 + month

    # Check MM/YYYY or MM-YYYY or YYYY/MM:
    match_num_my = re.search(r'(\d{1,2})[\s,./\-_](\d{4})', clean_str)
    if match_num_my:
        month = int(match_num_my.group(1))
        year = int(match_num_my.group(2))
        if 1 <= month <= 12:
            return year * 12 + month
            
    match_num_ym = re.search(r'(\d{4})[\s,./\-_](\d{1,2})', clean_str)
    if match_num_ym:
        year = int(match_num_ym.group(1))
        month = int(match_num_ym.group(2))
        if 1 <= month <= 12:
            return year * 12 + month

    # Check Year only: "2021"
    match_y = re.search(r'\b(19\d{2}|20\d{2})\b', clean_str)
    if match_y:
        year = int(match_y.group(1))
        month = 12 if is_end else 1
        return year * 12 + month

    return None

def normalize_date_string(date_str: Optional[str]) -> Optional[str]:
    """
    Normalizes a date string to YYYY-MM or 'Present'.
    """
    if not date_str:
        return None
    
    clean_str = date_str.strip()
    if any(p in clean_str.lower() for p in ["present", "current", "now", "ongoing", "till date"]):
        return "Present"
        
    month_idx = parse_date_to_month_index(date_str)
    if month_idx is None:
        # Return cleaned original string if it contains at least 4 digits
        if re.search(r'\d{4}', clean_str):
            return clean_str
        return None
        
    year = month_idx // 12
    month = month_idx % 12
    if month == 0:
        year -= 1
        month = 12
    return f"{year:04d}-{month:02d}"

def calculate_employment_duration(start_str: Optional[str], end_str: Optional[str]) -> Tuple[int, bool]:
    """
    Calculates duration in months between start and end date, and whether the job is current.
    """
    is_current = False
    if end_str and any(p in end_str.lower() for p in ["present", "current", "now", "ongoing", "till date"]):
        is_current = True
        
    start_idx = parse_date_to_month_index(start_str, is_end=False)
    end_idx = parse_date_to_month_index(end_str, is_end=True)
    
    if not start_idx and not end_idx:
        return 0, is_current
        
    if start_idx and not end_idx:
        now = datetime.now()
        end_idx = now.year * 12 + now.month
        is_current = True

    if not start_idx and end_idx:
        # If start is missing but end is present, assume at least 1 month
        return 1, is_current

    if start_idx and end_idx:
        if end_idx < start_idx:
            # Handle reverse order error
            start_idx, end_idx = end_idx, start_idx
        months = (end_idx - start_idx) + 1
        return max(1, months), is_current

    return 0, is_current

def calculate_total_experience_months(jobs: List[Dict[str, Any]]) -> int:
    """
    Calculates non-overlapping total experience in months.
    Merges overlapping intervals so that concurrent roles are not double-counted.
    """
    intervals: List[List[int]] = []
    
    for job in jobs:
        start_str = job.get("start_date")
        end_str = job.get("end_date")
        
        start_idx = parse_date_to_month_index(start_str, is_end=False)
        end_idx = parse_date_to_month_index(end_str, is_end=True)
        
        if not start_idx and not end_idx:
            continue
            
        if start_idx and not end_idx:
            now = datetime.now()
            end_idx = now.year * 12 + now.month
            
        if not start_idx and end_idx:
            start_idx = end_idx
            
        if start_idx and end_idx:
            if end_idx < start_idx:
                start_idx, end_idx = end_idx, start_idx
            intervals.append([start_idx, end_idx])
            
    if not intervals:
        return 0
        
    intervals.sort(key=lambda x: x[0])
    
    merged: List[List[int]] = []
    for start, end in intervals:
        if not merged:
            merged.append([start, end])
        else:
            prev_start, prev_end = merged[-1]
            if start <= prev_end + 1:
                merged[-1][1] = max(prev_end, end)
            else:
                merged.append([start, end])
                
    total_months = sum((end - start + 1) for start, end in merged)
    return total_months

def calculate_total_experience_years(jobs: List[Dict[str, Any]]) -> float:
    """
    Calculates non-overlapping total experience in years.
    """
    total_months = calculate_total_experience_months(jobs)
    return round(total_months / 12.0, 1)

