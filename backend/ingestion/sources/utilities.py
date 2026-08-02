"""
utilities.py

Utility functions to help scrape functions.
"""

#Standard modules
import re
from datetime import datetime
from zoneinfo import ZoneInfo

#Third-party libraries
from bs4 import BeautifulSoup
import html

# ==========================================
# 1. SCRAPING FUNCTIONS
# ==========================================
#Helper function
def clean(raw_html: str) -> str:
        # Parse HTML
        soup = BeautifulSoup(raw_html, "html.parser")

        # Extract text (preserves spacing between blocks)
        text = soup.get_text(separator="\n")

        # Decode HTML entities (&nbsp;, etc.)
        text = html.unescape(text)

        # Normalize whitespace
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

        return text

def extract_date_hour(date:str)->str:

    # UTC -> Perú
    dt = datetime.fromisoformat(date.replace("Z", "+00:00")).astimezone(
        ZoneInfo("America/Lima")
    )

    date_ = dt.date()
    hour_ = dt.time()

    return (date_.isoformat(),hour_.strftime("%H:%M:%S"))

MONTHS_ES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

def parse_spanish_date(date_str: str) -> str | None:
    """
    Converts:
        'Mar, julio 14, 2026'
    into:
        '2026-07-14'
    """

    if not date_str:
        return None

    date_str = date_str.strip()

    match = re.search(
        r"^[^,]+,\s*([a-záéíóúñ]+)\s+(\d{1,2}),\s*(\d{4})$",
        date_str,
        re.IGNORECASE,
    )

    if not match:
        return None

    month_name, day, year = match.groups()

    month = MONTHS_ES.get(month_name.lower())

    if month is None:
        return None

    dt = datetime(int(year), month, int(day))

    return dt.date().isoformat()

def parse_time_range(time_str: str):
    """
    Returns:
        ("10:00:00", "20:00:00")

    or

        ("10:00:00", None)
    """

    if not time_str:
        return None, None

    time_str = (
        time_str.strip()
        .replace("(", "")
        .replace(")", "")
    )

    parts = [p.strip() for p in time_str.split("-")]

    def convert(value):

        return datetime.strptime(
            value.lower(),
            "%I:%M %p"
        ).strftime("%H:%M:%S")

    start = convert(parts[0])

    end = convert(parts[1]) if len(parts) > 1 else None

    return start, end

def parse_location(location: str):
    """
    Assumes format:

    Place Name,
    Exact Address,
    District,
    City,
    Country
    """

    if not location:
        return {
            "address": None,
            "district": None,
            "city": None,
            "country": None,
        }

    parts = [p.strip() for p in location.split(",")]

    if len(parts) < 5:
        return {
            "address": None,
            "district": None,
            "city": None,
            "country": None,
        }

    return {
        "address": parts[-4],
        "district": parts[-3],
        "city": parts[-2],
        "country": parts[-1],
    }