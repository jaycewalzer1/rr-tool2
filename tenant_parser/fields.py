"""Recovering structured lease terms from a single OCR'd tenant segment.

A segment looks roughly like::

    Starbucks 101 1,800 03/01/2019 02/28/2024 $32.50 $58,500

but OCR splits numbers unpredictably ("1" "800", "$58" "500"), drops commas and
reorders columns, so each field is recovered heuristically and sanity-checked
against the others rather than read positionally.
"""

from __future__ import annotations

import itertools
import logging
import re
from datetime import datetime
from typing import Any

from tenant_parser.constants import anchor_tenants, months_map
from tenant_parser.lines import extract_tenant_name

logger = logging.getLogger(__name__)

DATE_FORMAT = "%m/%d/%Y"

# Retail suites below 800 sq ft are effectively kiosks and above 250,000 are
# whole centres; both indicate a misread rather than a real unit.
MIN_SQUARE_FEET = 800
MAX_SQUARE_FEET = 250_000

# Below these rents per square foot the figure is a CAM or tax recovery, not
# base rent. Anchors negotiate lower rents, so they get a lower floor.
MIN_ANCHOR_PSF = 4.20
MIN_INLINE_PSF = 4.60

# Annual rent for any leasable retail space clears this, so smaller candidates
# are suite numbers or monthly figures.
MIN_ANNUAL_RENT = 10_000

# Lease terms cluster on these lengths, so an end date landing on one of them
# is almost certainly the real expiry rather than an option or notice date.
COMMON_LEASE_TERMS_YEARS = (3, 5, 10)

_STANDARD_DATE = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}")
_MONTH_YEAR = re.compile(r"([A-Za-z]{3,9})[-\s]*(\d{2,4})")
_TERM_IN_YEARS = re.compile(r"Years?\s+(\d+)", re.IGNORECASE)
_PSF = re.compile(r"^\$\d+\.\d{2}$")
_WHOLE_DOLLARS = re.compile(r"^\$\d+$")
_DIGITS = re.compile(r"^\d+$")

_ANCHOR_NAMES = {name.lower() for name in anchor_tenants}

TenantRow = list[Any]


def build_tenant_row(
    segment: str,
    *,
    pdf_name: str,
    address: str,
    city: str,
    state: str,
    zip_code: str,
    seen_tenants: dict[str, Any],
) -> TenantRow | None:
    """Convert one tenant segment into a data-sheet row, or ``None`` if unusable.

    ``seen_tenants`` carries state across calls for a single PDF: it remembers
    the tenant a continuation line belongs to, and how many rows that tenant has
    already produced so repeat rows can be labelled as options.
    """
    parts = re.split(r"[,\s]+", segment.strip())

    tenant_name = extract_tenant_name(parts)
    if not tenant_name and "current_tenant" not in seen_tenants:
        return None

    if tenant_name:
        seen_tenants.setdefault(tenant_name, {"option_number": 0})
        seen_tenants["current_tenant"] = tenant_name

    tenant_name = seen_tenants["current_tenant"]
    option_number = seen_tenants[tenant_name]["option_number"]
    seen_tenants[tenant_name]["option_number"] += 1
    labelled_name = f"{tenant_name} Option {option_number}" if option_number else tenant_name

    square_feet = extract_square_feet(parts)
    dates, found_current = extract_dates(parts)
    begin_date = determine_begin_date(dates, found_current, parts)
    end_date = determine_end_date(dates, _parse_date(begin_date), found_current)
    psf_candidates = extract_psf_candidates(parts, tenant_name)

    return [
        pdf_name,
        labelled_name,
        square_feet,
        begin_date,
        end_date,
        f"${min(psf_candidates):.2f}" if psf_candidates else None,
        calculate_annual_rent(parts, square_feet, psf_candidates),
        city,
        state,
        zip_code,
        address,
    ]


def extract_dates(parts: list[str]) -> tuple[list[datetime], bool]:
    """Every date in ``parts``, plus whether a literal "Current" term was seen."""
    dates: list[datetime] = []
    found_current = False

    for index, raw in enumerate(parts):
        part = raw.strip()
        following = parts[index + 1].strip() if index + 1 < len(parts) else ""

        if match := _STANDARD_DATE.match(part):
            parsed = _parse_date(match.group())
            if parsed:
                dates.append(parsed)
        # "Jan-2009" survives the split as one token but "Jan 2009" becomes two,
        # so the token and the token pair are both tried.
        elif parsed := _month_year(part, following):
            dates.append(parsed)
        elif "years" in part.lower():
            dates.extend(_dates_from_term(parts))
        elif part.lower() == "current":
            found_current = True

    return dates, found_current


def determine_begin_date(
    dates: list[datetime], found_current: bool, parts: list[str]
) -> str | None:
    """Earliest date on the row, falling back to a stated term length."""
    if dates:
        return min(dates).strftime(DATE_FORMAT)
    if found_current:
        return "Current"

    for part in parts:
        match = _TERM_IN_YEARS.search(part)
        if match:
            return datetime(2000 + int(match.group(1)), 1, 1).strftime(DATE_FORMAT)

    return None


def determine_end_date(
    dates: list[datetime], begin_date: datetime | None, found_current: bool
) -> str | None:
    """Pick the expiry date, preferring one a common lease term after the start."""
    if not begin_date:
        return "Current" if found_current else None

    for term in COMMON_LEASE_TERMS_YEARS:
        matching = [date for date in dates if date.year == begin_date.year + term]
        if matching:
            return min(matching, key=lambda date: (date.month, date.day)).strftime(DATE_FORMAT)

    ordered = sorted(dates)
    if len(ordered) > 1:
        return ordered[1].strftime(DATE_FORMAT)

    return "Current" if found_current else None


def extract_square_feet(parts: list[str]) -> int | None:
    """Reassemble the unit size from digit groups OCR split apart.

    "1,800" is frequently read as the two tokens "1" and "800", so adjacent
    numeric tokens are joined before any single token is considered.
    """
    for left, right in itertools.pairwise(parts):
        if not (_DIGITS.match(left) and _DIGITS.match(right)):
            continue

        joined = _in_range(left + right) if _is_split_number(left, right) else None
        if joined is not None:
            return joined

        # "05" is a suite prefix, not a thousands digit: use the group after it.
        if len(left) == 2 and left.startswith("0"):
            standalone = _in_range(right)
            if standalone is not None:
                return standalone

        if len(left) == 3 and len(right) == 1:
            standalone = _in_range(left)
            if standalone is not None:
                return standalone

    for part in parts:
        if _DIGITS.match(part) and len(part) <= 4:
            standalone = _in_range(part)
            if standalone is not None:
                return standalone

    return None


def extract_psf_candidates(parts: list[str], tenant_name: str) -> list[float]:
    """Dollar-and-cents amounts large enough to be base rent per square foot."""
    floor = MIN_ANCHOR_PSF if tenant_name.lower() in _ANCHOR_NAMES else MIN_INLINE_PSF
    values = (float(part.replace("$", "")) for part in parts if _PSF.match(part))
    return [value for value in values if value >= floor]


def calculate_annual_rent(
    parts: list[str], square_feet: int | None, psf_candidates: list[float]
) -> str | None:
    """Recover annual rent, cross-checking it against size times rent PSF."""
    expected = square_feet * min(psf_candidates) if square_feet and psf_candidates else None
    candidates = _rent_candidates(parts)

    if len(candidates) > 1 and expected:
        return f"${min(candidates, key=lambda rent: abs(rent - expected)):,}"
    if len(candidates) == 1:
        return f"${candidates[0]:,}"
    if expected and expected > MIN_ANNUAL_RENT:
        return f"${int(expected):,}"
    return None


def _rent_candidates(parts: list[str]) -> list[int]:
    """Whole-dollar amounts, rejoining the thousands group OCR split off."""
    candidates: list[int] = []

    for index, part in enumerate(parts[:-1]):
        if not _WHOLE_DOLLARS.match(part):
            continue

        tail = parts[index + 1]
        if not (tail.isdigit() or "." in tail):
            continue

        try:
            combined = int(float(f"{part.removeprefix('$')}{tail}"))
        except ValueError:
            continue

        if combined > MIN_ANNUAL_RENT:
            candidates.append(combined)

    return candidates


def _is_split_number(left: str, right: str) -> bool:
    """Whether two numeric tokens are one thousands-separated number."""
    if len(right) == 3:
        return len(left) in (1, 3) or (len(left) == 2 and not left.startswith("0"))
    return False


def _in_range(digits: str) -> int | None:
    value = int(digits)
    return value if MIN_SQUARE_FEET <= value <= MAX_SQUARE_FEET else None


def _parse_date(value: str | None) -> datetime | None:
    if not value or value == "Current":
        return None
    for fmt in (DATE_FORMAT, "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    logger.debug("unparseable date skipped: %s", value)
    return None


def _month_year(part: str, following: str) -> datetime | None:
    """Parse a month-and-year date written as one token or split across two."""
    if match := _MONTH_YEAR.fullmatch(part):
        return _parse_month_year(*match.groups())
    if part.lower() in months_map:
        return _parse_month_year(part, following)
    return None


def _parse_month_year(month_name: str, year_text: str) -> datetime | None:
    month = months_map.get(month_name.lower())
    if not month or not year_text.isdigit():
        return None

    year = int(year_text)
    if len(year_text) == 2:
        year += 2000 if year < 70 else 1900

    try:
        return datetime(year, month, 1)
    except ValueError:
        logger.debug("unparseable month-year skipped: %s %s", month_name, year_text)
        return None


def _dates_from_term(parts: list[str]) -> list[datetime]:
    """Interpret "10 Years" as a year, which is how these rows are laid out."""
    return [
        datetime(2000 + int(parts[index - 1]), 1, 1)
        for index, word in enumerate(parts)
        if word.lower() == "years" and index > 0 and parts[index - 1].isdigit()
    ]
