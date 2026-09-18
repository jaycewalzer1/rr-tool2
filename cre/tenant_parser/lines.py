"""Turning raw OCR lines into one text segment per tenant.

OCR of a rent roll page returns everything on the page: table rows, column
headers, footnotes and paragraphs of marketing prose. This module discards the
noise and then splits what remains on known tenant names, because OCR routinely
runs several table rows together into a single line.
"""

from __future__ import annotations

import functools
import logging
import re

from cre.tenant_parser.constants import anchor_tenants, popular_tenants

logger = logging.getLogger(__name__)

# Every genuine tenant row quotes a rent, so a line without a dollar amount is
# prose or a header and can be dropped outright.
_RENT_PSF = re.compile(r"\$\d+(\.\d{1,2})?", re.IGNORECASE)

_BRACKET_ANALYSIS = r"\[\d+\]\s?.*"
_NOTE_OR_DENOMINATOR = (
    r"^(NOTE:|Denominator:|Notes:|Note:|Per\s.*|Exclusive Use:|Percentage Rent:"
    r"|Renewal History:|Recovery:|CAM:)\s+.*"
)
_ALPHABETIC_SENTENCE = r"^[A-Z][^\.]*[\.,;!?]*\s*\.$"
_FULL_SENTENCE = r"^(?:Additionally|Moreover|Furthermore|Also|However|Tenant|Tenant\'s)\s+.*\.$"
_TIME_TERM = r"\b\d{1,3}-\d{1,3}\s+year\s+term\b"
_INDUSTRY_PROSE = r"\b(?:e-commerce|retail|demographics|development|industry|threats)\b"
_TABLE_HEADER = (
    r"^(?:Tenant|Suite|Feet|Property|Begin|End|Monthly|Annually|PSF|Rent|Improvements).*"
)
_TENANT_RECOVERY = r"^Tenant recovery denominator[^\.]*\.$"
_PROSE_KEYWORDS = (
    r"\b(?:averaging|over|their|size|pay|paid|summary|is|a|are|less|than|area"
    r"|contributions|total|based|and|has|leased|agrees|of|agree)\b.*"
)

_NOISE = re.compile(
    "|".join(
        (
            _BRACKET_ANALYSIS,
            _NOTE_OR_DENOMINATOR,
            _ALPHABETIC_SENTENCE,
            _FULL_SENTENCE,
            _TIME_TERM,
            _INDUSTRY_PROSE,
            _TABLE_HEADER,
            _TENANT_RECOVERY,
            _PROSE_KEYWORDS,
        )
    ),
    re.IGNORECASE,
)

_DROP_LINE = re.compile(f"{_BRACKET_ANALYSIS}|{_NOTE_OR_DENOMINATOR}", re.IGNORECASE)

# Recovery-clause fragments that trail the rent columns. They are truncated
# rather than dropped so the tenant and rent stay intact.
_ADMIN_FEE = re.compile(r"\b\w+\s+\+\s*\d{1,3}%\s+(?:Admin|Fee)\b", re.IGNORECASE)
_CAPPED_PLUS = re.compile(r"\b\w+\s+Capped\s+\+\s*\d{1,3}%\b", re.IGNORECASE)
_PRS_OR_CAM = re.compile(r"(PRS|Fixed CAM).*?(Option|Options)", re.IGNORECASE)

_VACANCY = re.compile(r"\b(VACANT|AVAILABLE)\b", re.IGNORECASE)

_MAX_TENANT_NAME_WORDS = 4


def clean_lines(ocr_lines: list[str]) -> list[str]:
    """Drop headers, footnotes and prose, leaving candidate tenant rows."""
    cleaned: list[str] = []

    for raw in ocr_lines:
        line = re.sub(r"\s+", " ", raw).strip()
        if not _RENT_PSF.search(line) or _DROP_LINE.search(line):
            continue

        line = _strip_recovery_clauses(line)
        line = _strip_noise(line)

        if line:
            cleaned.append(line)

    return cleaned


def _strip_recovery_clauses(line: str) -> str:
    prs = _PRS_OR_CAM.search(line)
    if prs:
        start, end = prs.span()
        # Keep the trailing "Option" so option rows stay detectable.
        line = line[:start] + prs.group(2) + line[end:]

    for pattern in (_ADMIN_FEE, _CAPPED_PLUS):
        match = pattern.search(line)
        if match:
            line = line[: line.rfind(" ", 0, match.start())].strip()

    return line


def _strip_noise(line: str) -> str:
    while match := _NOISE.search(line):
        line = line[: match.start()] + line[match.end() :].strip()
    return line


@functools.lru_cache(maxsize=1)
def _tenant_pattern() -> re.Pattern[str]:
    names = sorted(popular_tenants | anchor_tenants, key=len, reverse=True)
    return re.compile(r"\b(" + "|".join(re.escape(name) for name in names) + r")\b", re.IGNORECASE)


def split_tenants(line: str) -> list[str]:
    """Split a cleaned line into one segment per recognised tenant.

    Each segment is the tenant name followed by the raw figures that trail it.
    Anything after a VACANT/AVAILABLE marker belongs to the next (empty) unit
    and is discarded.
    """
    segments = re.split(_tenant_pattern(), line)
    tenants: list[str] = []
    current: str | None = None

    for raw_segment in segments:
        segment = raw_segment.strip()
        if not segment:
            continue

        if _tenant_pattern().match(segment):
            current = segment
            continue

        if current:
            vacancy = _VACANCY.search(segment)
            if vacancy:
                segment = segment[: vacancy.start()].strip()
            if segment:
                tenants.append(f"{current} {segment}")
            current = None

    logger.debug("detected %d tenant segment(s)", len(tenants))
    return tenants


def starts_new_tenant(line: str) -> bool:
    """A row beginning with a letter starts a new tenant; continuations do not."""
    return bool(re.match(r"^[A-Za-z]", line))


def extract_tenant_name(parts: list[str]) -> str:
    """Match a 1-4 word window of ``parts`` against the known tenant names.

    Popular tenants win over anchor tenants: an anchor name is often part of a
    longer shopping-centre description, whereas a popular tenant is the row.
    """
    detected_popular = ""
    detected_anchor = ""

    for index in range(len(parts)):
        windows = [
            " ".join(filter(None, parts[index : index + size])).strip().lower()
            for size in range(1, _MAX_TENANT_NAME_WORDS + 1)
        ]

        match = _lookup(windows, _POPULAR_BY_KEY)
        if match:
            detected_popular = match
        elif not detected_popular:
            detected_anchor = _lookup(windows, _ANCHOR_BY_KEY) or detected_anchor

    return detected_popular or detected_anchor


def _lookup(windows: list[str], names: dict[str, str]) -> str:
    """First window that names a tenant, returned in its canonical spelling."""
    return next((names[window] for window in windows if window in names), "")


# Canonical spelling by lower-cased name. Returning the canonical form rather
# than the OCR'd text is what lets the summary sheet categorise tenants.
_POPULAR_BY_KEY = {name.lower(): name for name in popular_tenants}
_ANCHOR_BY_KEY = {name.lower(): name for name in anchor_tenants}
