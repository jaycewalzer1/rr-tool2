"""Tests for the lease-term heuristics.

These cover the part of the system with no ground truth to fall back on: OCR
gives unlabelled tokens in an unpredictable order, so every field is inferred.
"""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar

import pytest

from cre.tenant_parser.fields import (
    MAX_SQUARE_FEET,
    MIN_ANCHOR_PSF,
    MIN_INLINE_PSF,
    MIN_SQUARE_FEET,
    build_tenant_row,
    calculate_annual_rent,
    determine_begin_date,
    determine_end_date,
    extract_dates,
    extract_psf_candidates,
    extract_square_feet,
)


def tokens(line: str) -> list[str]:
    return line.split()


class TestExtractSquareFeet:
    def test_joins_a_thousands_group_ocr_split_apart(self):
        assert extract_square_feet(tokens("Starbucks 101 1 800 03/01/2019")) == 1800

    def test_joins_five_and_six_digit_sizes(self):
        assert extract_square_feet(tokens("29 000 $4.50")) == 29000
        assert extract_square_feet(tokens("101 035 $4.50")) == 101035

    def test_treats_a_zero_prefixed_pair_as_a_suite_number(self):
        # "05" is suite 5, so the size is the group that follows it.
        assert extract_square_feet(tokens("05 2400 $12.00")) == 2400

    def test_falls_back_to_a_standalone_value(self):
        assert extract_square_feet(tokens("Subway 1450 $24.00")) == 1450

    @pytest.mark.parametrize("size", [MIN_SQUARE_FEET - 1, MAX_SQUARE_FEET + 1])
    def test_rejects_sizes_outside_the_retail_range(self, size: int):
        assert extract_square_feet([str(size)]) is None

    def test_returns_none_when_there_are_no_numbers(self):
        assert extract_square_feet(tokens("Starbucks Option Current")) is None


class TestExtractPsfCandidates:
    def test_keeps_amounts_at_or_above_the_inline_floor(self):
        assert extract_psf_candidates(["$24.00", "$4.60"], "Subway") == [24.00, 4.60]

    def test_discards_recovery_charges_below_the_floor(self):
        # $2.10 is a CAM charge, not base rent.
        assert extract_psf_candidates(["$24.00", "$2.10"], "Subway") == [24.00]

    def test_anchors_get_a_lower_floor_than_inline_tenants(self):
        between = f"${(MIN_ANCHOR_PSF + MIN_INLINE_PSF) / 2:.2f}"
        assert extract_psf_candidates([between], "Target") != []
        assert extract_psf_candidates([between], "Subway") == []

    def test_ignores_whole_dollar_amounts(self):
        assert extract_psf_candidates(["$58", "500"], "Subway") == []


class TestCalculateAnnualRent:
    def test_rejoins_a_rent_ocr_split_at_the_comma(self):
        assert calculate_annual_rent(tokens("$58 500"), 1800, [32.50]) == "$58,500"

    def test_picks_the_candidate_closest_to_size_times_psf(self):
        # 1,800 sq ft at $32.50 is ~$58.5k, so the $120k figure is another column.
        parts = tokens("$58 500 $120 000")
        assert calculate_annual_rent(parts, 1800, [32.50]) == "$58,500"

    def test_computes_the_rent_when_none_is_printed(self):
        assert calculate_annual_rent(tokens("Subway"), 2000, [30.00]) == "$60,000"

    def test_returns_none_without_enough_information(self):
        assert calculate_annual_rent(tokens("Subway"), None, []) is None

    def test_ignores_amounts_too_small_to_be_annual_rent(self):
        assert calculate_annual_rent(tokens("$1 200"), None, []) is None


class TestDates:
    def test_reads_standard_and_month_year_formats(self):
        dates, found_current = extract_dates(tokens("03/01/2019 Jan 2009 02/28/2024"))
        assert datetime(2019, 3, 1) in dates
        assert datetime(2009, 1, 1) in dates
        assert not found_current

    def test_detects_a_current_term(self):
        _, found_current = extract_dates(["Current"])
        assert found_current

    def test_expands_two_digit_years(self):
        dates, _ = extract_dates(["03/01/19"])
        assert dates == [datetime(2019, 3, 1)]

    def test_begin_date_is_the_earliest(self):
        dates, current = extract_dates(tokens("02/28/2024 03/01/2019"))
        assert determine_begin_date(dates, current, []) == "03/01/2019"

    def test_begin_date_falls_back_to_current(self):
        assert determine_begin_date([], True, []) == "Current"

    def test_begin_date_returns_none_when_nothing_is_datelike(self):
        assert determine_begin_date([], False, ["Subway"]) is None

    def test_end_date_prefers_a_common_lease_term(self):
        begin = datetime(2019, 3, 1)
        # 2029 is ten years out but 2024 is five, which is the likelier expiry.
        dates = [begin, datetime(2029, 6, 1), datetime(2024, 2, 28)]
        assert determine_end_date(dates, begin, False) == "02/28/2024"

    def test_end_date_uses_the_second_date_when_no_term_matches(self):
        begin = datetime(2019, 3, 1)
        assert determine_end_date([begin, datetime(2022, 1, 1)], begin, False) == "01/01/2022"

    def test_end_date_without_a_start_is_unknown(self):
        assert determine_end_date([], None, False) is None


class TestBuildTenantRow:
    location: ClassVar[dict[str, str]] = {
        "pdf_name": "centre.pdf",
        "address": "123 Main St",
        "city": "Austin",
        "state": "TX",
        "zip_code": "78701",
    }

    def test_builds_a_full_row(self):
        row = build_tenant_row(
            "Starbucks 101 1 800 03/01/2019 02/28/2024 $32.50 $58 500",
            seen_tenants={},
            **self.location,
        )
        assert row is not None
        pdf, tenant, square_feet, begin, end, psf, rent, city, state, zip_code, address = row
        assert (pdf, tenant, square_feet) == ("centre.pdf", "Starbucks", 1800)
        assert (begin, end, psf, rent) == ("03/01/2019", "02/28/2024", "$32.50", "$58,500")
        assert (city, state, zip_code, address) == ("Austin", "TX", "78701", "123 Main St")

    def test_labels_repeat_rows_for_the_same_tenant_as_options(self):
        seen: dict = {}
        first = build_tenant_row("Subway 1450 $24.00", seen_tenants=seen, **self.location)
        second = build_tenant_row("Subway 1450 $26.00", seen_tenants=seen, **self.location)
        assert first is not None and second is not None
        assert first[1] == "Subway"
        assert second[1] == "Subway Option 1"

    def test_attributes_a_continuation_line_to_the_previous_tenant(self):
        seen: dict = {}
        build_tenant_row("Subway 1450 $24.00", seen_tenants=seen, **self.location)
        row = build_tenant_row("2200 $26.00", seen_tenants=seen, **self.location)
        assert row is not None
        assert row[1] == "Subway Option 1"

    def test_skips_a_segment_with_no_tenant_context(self):
        assert build_tenant_row("2200 $26.00", seen_tenants={}, **self.location) is None
