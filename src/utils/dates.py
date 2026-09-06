from datetime import datetime, date
from typing import Optional, Union


def parse_date(date_str: Optional[Union[str, datetime, date]]) -> Optional[date]:
    """Safely converts string or datetime objects into date instances."""
    if date_str is None:
        return None
    if hasattr(date_str, "date"):
        return date_str.date()
    if isinstance(date_str, date):
        return date_str

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except ValueError:
            pass
    return None


def calculate_age(dob: Optional[Union[str, datetime, date]], reference_date: Optional[Union[str, datetime, date]] = None) -> Optional[int]:
    """Calculates age in years relative to a reference date (defaults to today)."""
    parsed_dob = parse_date(dob)
    if not parsed_dob:
        return None

    ref_date = parse_date(reference_date) if reference_date else date.today()
    if ref_date < parsed_dob:
        return None

    age = ref_date.year - parsed_dob.year - ((ref_date.month, ref_date.day) < (parsed_dob.month, parsed_dob.day))
    return age
