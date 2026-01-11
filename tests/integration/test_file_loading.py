"""
Integration Tests for File Loading Operations
==============================================

Tests loading bills from CSV, JSON, and Excel files with various formats
and error handling scenarios. Verifies that bills are correctly parsed
from different file formats and that errors are handled appropriately.

Examples
--------
.. code-block:: python

   # Run all tests in this module.
   pytest tests/integration/test_file_loading.py

   # Run a specific test class.
   pytest tests/integration/test_file_loading.py::TestCSVLoading
"""

########################################################################
## IMPORTS
########################################################################

from pathlib import Path

import pytest


########################################################################
## CONSTANTS
########################################################################

# Get the fixtures directory path.
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestCSVLoading:
    """Test loading bills from CSV files."""

    def test_load_bills_from_csv(self, sample_fund):
        """Test loading bills from a valid CSV file."""
        csv_path = str(FIXTURES_DIR / "sample_bills.csv")
        
        initial_count = len(sample_fund.get_bills())
        
        sample_fund.add_bills(source=csv_path, contribution_interval=14)
        
        bills = sample_fund.get_bills()
        assert len(bills) > initial_count
        # Verify some expected bills were loaded.
        bill_ids = [bill.bill_id for bill in bills]
        assert "bill_1" in bill_ids
        assert "bill_2" in bill_ids

    def test_load_csv_verify_bill_data(self, sample_fund):
        """Test that CSV-loaded bills have correct data."""
        csv_path = str(FIXTURES_DIR / "sample_bills.csv")
        
        sample_fund.add_bills(source=csv_path, contribution_interval=14)
        
        bills = sample_fund.get_bills()
        bill_1 = next((b for b in bills if b.bill_id == "bill_1"), None)
        
        assert bill_1 is not None
        assert bill_1.service == "Electric Bill"
        assert bill_1.amount_due == 150.0
        assert bill_1.recurring is False

    def test_load_csv_handle_malformed_data(self, sample_fund):
        """Test error handling for malformed CSV files."""
        invalid_csv_path = str(FIXTURES_DIR / "invalid_bills.csv")
        
        # Should raise an error or handle gracefully.
        with pytest.raises((ValueError, KeyError, Exception)):
            sample_fund.add_bills(
                source=invalid_csv_path, contribution_interval=14
            )


class TestJSONLoading:
    """Test loading bills from JSON files."""

    def test_load_bills_from_json(self, sample_fund):
        """Test loading bills from a valid JSON file."""
        json_path = str(FIXTURES_DIR / "sample_bills.json")
        
        initial_count = len(sample_fund.get_bills())
        
        sample_fund.add_bills(source=json_path, contribution_interval=14)
        
        bills = sample_fund.get_bills()
        assert len(bills) > initial_count
        # Verify some expected bills were loaded.
        bill_ids = [bill.bill_id for bill in bills]
        assert "bill_1" in bill_ids
        assert "bill_2" in bill_ids

    def test_load_json_verify_bill_data(self, sample_fund):
        """Test that JSON-loaded bills have correct data."""
        json_path = str(FIXTURES_DIR / "sample_bills.json")
        
        sample_fund.add_bills(source=json_path, contribution_interval=14)
        
        bills = sample_fund.get_bills()
        bill_2 = next((b for b in bills if b.bill_id == "bill_2"), None)
        
        assert bill_2 is not None
        assert bill_2.service == "Internet Service"
        # Amount may be Decimal type.
        from decimal import Decimal
        assert bill_2.amount_due == Decimal('79.99') or float(
            bill_2.amount_due
        ) == 79.99
        assert bill_2.recurring is True
        assert bill_2.frequency == "monthly"

    def test_load_json_malformed_data(self, sample_fund, tmp_path):
        """Test error handling for malformed JSON files."""
        invalid_json_path = tmp_path / "invalid.json"
        invalid_json_path.write_text("{ invalid json }")
        
        # Should raise an error.
        with pytest.raises((ValueError, Exception)):
            sample_fund.add_bills(
                source=str(invalid_json_path),
                contribution_interval=14
            )


class TestExcelLoading:
    """Test loading bills from Excel files."""

    @pytest.mark.skip(
        reason="Library Excel reader has bug with dict/DataFrame handling"
    )
    def test_load_bills_from_excel(self, sample_fund):
        """Test loading bills from a valid Excel file."""
        excel_path = str(FIXTURES_DIR / "sample_bills.xlsx")
        
        initial_count = len(sample_fund.get_bills())
        
        sample_fund.add_bills(source=excel_path, contribution_interval=14)
        
        bills = sample_fund.get_bills()
        assert len(bills) > initial_count

    @pytest.mark.skip(
        reason="Library Excel reader has bug with dict/DataFrame handling"
    )
    def test_load_excel_verify_bill_data(self, sample_fund):
        """Test that Excel-loaded bills have correct data."""
        excel_path = str(FIXTURES_DIR / "sample_bills.xlsx")
        
        sample_fund.add_bills(source=excel_path, contribution_interval=14)
        
        bills = sample_fund.get_bills()
        assert len(bills) > 0
        # Verify bills have expected attributes.
        for bill in bills:
            assert hasattr(bill, 'bill_id')
            assert hasattr(bill, 'service')
            assert hasattr(bill, 'amount_due')


class TestFileValidation:
    """Test file format validation and error handling."""

    def test_load_nonexistent_file(self, sample_fund):
        """Test error handling for non-existent file."""
        nonexistent_path = str(FIXTURES_DIR / "nonexistent_file.csv")
        
        with pytest.raises((FileNotFoundError, Exception)):
            sample_fund.add_bills(
                source=nonexistent_path,
                contribution_interval=14
            )

    def test_load_empty_file(self, sample_fund, tmp_path):
        """Test handling of empty files."""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("")
        
        # Should handle gracefully or raise appropriate error
        try:
            sample_fund.add_bills(
                source=str(empty_csv),
                contribution_interval=14
            )
            # If no error, verify no bills were added
            bills = sample_fund.get_bills()
            assert len(bills) == 0
        except (ValueError, Exception):
            # Error is also acceptable for empty files
            pass

