"""Property address extraction from rent roll PDF text.

Rent rolls rarely state the property address in a structured field, so it is
recovered from the surrounding marketing text. Anything that merely *looks*
like an address is then validated against the GeoNames ZIP/city/state table so
that headings such as "Market Overview" never make it into the workbook.
"""

from __future__ import annotations

import logging
import re

import pandas as pd

from cre.tenant_parser.reference import (
    CITY_COLUMN,
    STATE_ABBREVIATION_COLUMN,
    STATE_NAME_COLUMN,
    ZIP_COLUMN,
    reference_data,
)

logger = logging.getLogger(__name__)

Address = tuple[str, str, str, str]

UNKNOWN_ADDRESS: Address = ("N/A", "N/A", "N/A", "N/A")

_STREET_SUFFIXES = r"Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr"

_ADDRESS_PATTERNS: tuple[str, ...] = (
    rf"\d{{3,5}}\s[\w\s]+\s(?:{_STREET_SUFFIXES})\s*,?\s*[\w\s]*,\s*[A-Za-z]{{2}}\s*\d{{5}}",
    rf"\d{{3,5}}\s[\w\s]+\s(?:{_STREET_SUFFIXES})\s+[\w\s]+,\s*[A-Za-z]{{2}}\s*\d{{5}}",
    rf"\d{{3,5}},?\s*[\d,\s]+(?:{_STREET_SUFFIXES})\s*,?\s*[\w\s]*,\s*[A-Za-z]{{2}}",
    r"\d{4,6}\s*-\s*\d{4,6}\s[\w\s]+\s*,?\s*[\w\s]*,\s*[A-Za-z]{2}\s*\d{5}",
    r"\d{3,5}\s[\w\s]+\s[\w\s]+,\s*[A-Za-z][a-z]+\s[A-Za-z]{2}\s*\d{5}",
    r"[\w\s]+,\s*[A-Za-z]{2}\s*\d{5}",
    r"\d+\s[\w\s]+,?\s*[\w\s]+\s\|\s*[\w\s]+,\s*[A-Za-z]{2}\s*\d{5}",
)

_PHONE = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
# Broker contact blocks sit next to the property address and produce false
# positives, so any candidate within this many lines of one is discarded.
_BROKER = re.compile(r"\bNewmark\b|@nmrk\.com", re.IGNORECASE)
_BROKER_LINE_WINDOW = 17

_INVALID_LINE_KEYWORDS = re.compile(
    r"\b(stores|summary|overview|market|job|students|kay|zale)\b", re.IGNORECASE
)
_INVALID_ADDRESS_KEYWORDS = re.compile(
    r"\b(stores|summary|overview|market|phase|job|students|suite|700|800|kay|zale)\b",
    re.IGNORECASE,
)

_TRAILING_ZIP = re.compile(r"\b\d{5}\b$")
_STATE_BEFORE_ZIP = re.compile(r"\b[A-Za-z]{2}\b(?=\s*\d{5})")


def extract_addresses(text: str, csv_data: pd.DataFrame | None = None) -> list[Address]:
    """Return the single most complete ``(address, city, state, zip)`` in ``text``.

    A list is returned (rather than a bare tuple) because the caller iterates
    over addresses when expanding tenant rows.
    """
    data = reference_data() if csv_data is None else csv_data
    lines = text.splitlines()
    candidates: dict[tuple[str, str, str], Address] = {}

    for index, line in enumerate(lines):
        if _INVALID_LINE_KEYWORDS.search(line):
            continue
        if _has_nearby_phone(lines, index) or _has_nearby_broker(lines, index):
            continue

        for pattern in _ADDRESS_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if not match:
                continue

            address = match.group(0).strip()
            city, state, zip_code = _split_components(address)
            if not is_real_address(address, city, state, zip_code, data):
                continue

            key = (city, state, zip_code)
            # Longer matches carry more of the street line, so prefer them.
            if key not in candidates or len(address) > len(candidates[key][0]):
                candidates[key] = (address, city, state, zip_code)

    if not candidates:
        return [_fallback_address(text, data)]

    return [max(candidates.values(), key=lambda entry: len(entry[0]))]


def is_real_address(
    address: str, city: str, state: str, zip_code: str, csv_data: pd.DataFrame | None = None
) -> bool:
    """Validate the city/state (and ZIP, when present) against the reference table."""
    data = reference_data() if csv_data is None else csv_data

    if _INVALID_ADDRESS_KEYWORDS.search(address):
        return False

    city_valid = bool(data[CITY_COLUMN].eq(city.lower()).any())
    state_valid = bool(
        data[STATE_NAME_COLUMN].eq(state.lower()).any()
        or data[STATE_ABBREVIATION_COLUMN].eq(state.upper()).any()
    )

    if zip_code.isdigit():
        for_zip = data[data[ZIP_COLUMN] == zip_code]
        if not for_zip.empty:
            matches_zip = bool(for_zip[CITY_COLUMN].eq(city.lower()).any()) and bool(
                for_zip[STATE_NAME_COLUMN].eq(state.lower()).any()
                or for_zip[STATE_ABBREVIATION_COLUMN].eq(state.upper()).any()
            )
            if not matches_zip:
                return False

    return city_valid and state_valid


def _split_components(address: str) -> tuple[str, str, str]:
    """Pull city, state and ZIP out of a matched address string."""
    zip_match = _TRAILING_ZIP.search(address)
    zip_code = zip_match.group(0) if zip_match else "N/A"

    state_match = _STATE_BEFORE_ZIP.search(address)
    state = state_match.group(0).upper() if state_match else ""

    city = "UNKNOWN"
    if state:
        city_match = re.search(rf"([\w\s]+)\s*,?\s*{state}", address, re.IGNORECASE)
        if city_match:
            city = city_match.group(1).strip().title()

    return city, state, zip_code


def _has_nearby_phone(lines: list[str], index: int) -> bool:
    before = index > 0 and _PHONE.search(lines[index - 1]) is not None
    after = index + 1 < len(lines) and _PHONE.search(lines[index + 1]) is not None
    return before or after


def _has_nearby_broker(lines: list[str], index: int) -> bool:
    window = lines[max(0, index - _BROKER_LINE_WINDOW) : index + _BROKER_LINE_WINDOW]
    return any(_BROKER.search(line) for line in window)


def _fallback_address(text: str, csv_data: pd.DataFrame) -> Address:
    """Recover a city/state pair when no full street address could be matched."""
    abbreviations = csv_data[STATE_ABBREVIATION_COLUMN].unique()
    state_pattern = re.compile(r"\b(?:" + "|".join(abbreviations) + r")\b", re.IGNORECASE)
    state_match = state_pattern.search(text)
    if not state_match:
        return UNKNOWN_ADDRESS

    state = state_match.group(0).upper()
    city_match = re.search(r"((?:\b\w+\b\s*){1,3}),?\s*" + re.escape(state), text, re.IGNORECASE)
    city = city_match.group(1).strip().title() if city_match else "UNKNOWN"

    if city == "UNKNOWN" or not is_real_address("N/A", city, state, "N/A", csv_data):
        logger.debug("no address could be recovered from the document text")
        return UNKNOWN_ADDRESS

    return ("N/A", city, state, "N/A")
