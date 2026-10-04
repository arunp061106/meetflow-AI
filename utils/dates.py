from datetime import datetime, date, timedelta
from typing import Optional, Union

def format_date_str(d: Optional[Union[date, str]], default: str = "No deadline") -> str:
    """Format date to human readable string safely."""
    if not d:
        return default
    if isinstance(d, str):
        try:
            d = datetime.strptime(d[:10], "%Y-%m-%d").date()
        except Exception:
            return d
    try:
        return d.strftime("%b %d, %Y")
    except Exception:
        return str(d)

def get_relative_deadline_str(d: Optional[Union[date, str]], status: str = "") -> str:
    """Returns 'Overdue by X days', 'Due today', or 'Due in X days' safely."""
    if not d:
        return "No deadline"
    if isinstance(d, str):
        try:
            d = datetime.strptime(d[:10], "%Y-%m-%d").date()
        except Exception:
            return f"Due {d}"

    if not isinstance(d, (date, datetime)):
        return "No deadline"

    today = date.today()
    if isinstance(d, datetime):
        d = d.date()

    diff = (d - today).days

    if status == "Completed":
        return f"Completed ({d.strftime('%b %d')})"
    if diff < 0:
        return f"⚠️ {abs(diff)} day(s) overdue"
    elif diff == 0:
        return "⚠️ Due today"
    elif diff == 1:
        return "Due tomorrow"
    else:
        return f"Due in {diff} days"
