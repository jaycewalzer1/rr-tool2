"""Tests for turning raw OCR output into per-tenant segments."""

from __future__ import annotations

from cre.tenant_parser.lines import (
    clean_lines,
    extract_tenant_name,
    split_tenants,
    starts_new_tenant,
)


class TestCleanLines:
    def test_keeps_a_tenant_row(self):
        row = "Starbucks 101 1,800 03/01/2019 02/28/2024 $32.50"
        assert clean_lines([row]) == [row]

    def test_drops_lines_with_no_rent(self):
        assert clean_lines(["Property Overview", "Anchored by a regional grocer"]) == []

    def test_drops_footnotes_and_notes(self):
        assert clean_lines(["[1] Analysis excludes $24.00 CAM", "NOTE: rents are $24.00 net"]) == []

    def test_normalises_runs_of_whitespace(self):
        assert clean_lines(["Subway    1450     $24.00"]) == ["Subway 1450 $24.00"]

    def test_truncates_a_trailing_admin_fee_clause(self):
        cleaned = clean_lines(["Subway 1450 $24.00 NNN + 15% Admin"])
        assert cleaned == ["Subway 1450 $24.00"]

    def test_keeps_the_option_marker_when_dropping_a_cam_clause(self):
        cleaned = clean_lines(["Subway 1450 $24.00 Fixed CAM 3% annual Option"])
        assert "Option" in cleaned[0]
        assert "Fixed CAM" not in cleaned[0]


class TestSplitTenants:
    def test_separates_two_rows_ocr_ran_together(self):
        segments = split_tenants("Starbucks 1800 $32.50 Subway 1450 $24.00")
        assert segments == ["Starbucks 1800 $32.50", "Subway 1450 $24.00"]

    def test_discards_the_vacant_unit_trailing_a_tenant(self):
        assert split_tenants("Subway 1450 $24.00 VACANT 2200") == ["Subway 1450 $24.00"]

    def test_returns_nothing_when_no_tenant_is_recognised(self):
        assert split_tenants("Unit 4 2200 $18.00") == []

    def test_matches_a_tenant_regardless_of_ocr_casing(self):
        assert split_tenants("STARBUCKS 1800 $32.50") == ["STARBUCKS 1800 $32.50"]


class TestStartsNewTenant:
    def test_a_row_beginning_with_a_name_starts_a_tenant(self):
        assert starts_new_tenant("Starbucks 1800 $32.50")

    def test_a_row_beginning_with_a_figure_is_a_continuation(self):
        assert not starts_new_tenant("2200 $26.00")


class TestExtractTenantName:
    def test_returns_the_canonical_spelling(self):
        # The summary sheet groups on exact names, so OCR casing is normalised.
        assert extract_tenant_name(["starbucks", "1800"]) == "Starbucks"

    def test_matches_a_multi_word_name(self):
        assert extract_tenant_name(["Panda", "Express", "2400"]) == "Panda Express"

    def test_prefers_an_inline_tenant_over_an_anchor(self):
        # Anchors are often named in centre descriptions rather than being the row.
        assert extract_tenant_name(["Target", "Center", "Subway", "1450"]) == "Subway"

    def test_returns_empty_for_an_unknown_tenant(self):
        assert extract_tenant_name(["Acme", "Holdings", "LLC"]) == ""
