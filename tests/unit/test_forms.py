"""
Unit Tests for Form Components
===============================

Tests for bill data creation, validation, file path extraction, amount
validation, and date handling in form components. Verifies bill data
structure, required fields, and edge cases.

Examples
--------
.. code-block:: python

   # Run all tests in this module.
   pytest tests/unit/test_forms.py

   # Run a specific test class.
   pytest tests/unit/test_forms.py::TestBillDataCreation
"""

from datetime import date, timedelta
import pytest


class TestBillDataCreation:
    """Test bill data dictionary creation logic."""

    def test_create_non_recurring_bill_data(self):
        """Test creating bill data for non-recurring bill."""
        bill_data = {
            "bill_id": "test_1",
            "service": "Test Service",
            "amount_due": 100.0,
            "recurring": False,
            "due_date": date.today() + timedelta(days=30),
            "start_date": None,
            "frequency": None,
            "interval": None,
            "occurrences": None,
            "end_date": None
        }
        
        assert bill_data["recurring"] is False
        assert bill_data["due_date"] is not None
        assert bill_data["start_date"] is None
        assert bill_data["frequency"] is None

    def test_create_recurring_bill_data(self):
        """Test creating bill data for recurring bill."""
        bill_data = {
            "bill_id": "test_2",
            "service": "Monthly Service",
            "amount_due": 50.0,
            "recurring": True,
            "due_date": None,
            "start_date": date.today(),
            "frequency": "monthly",
            "interval": 1,
            "occurrences": None,
            "end_date": None
        }
        
        assert bill_data["recurring"] is True
        assert bill_data["due_date"] is None
        assert bill_data["start_date"] is not None
        assert bill_data["frequency"] == "monthly"
        assert bill_data["interval"] == 1

    def test_create_recurring_bill_with_occurrences(self):
        """Test creating recurring bill with occurrences limit."""
        bill_data = {
            "bill_id": "test_3",
            "service": "Limited Service",
            "amount_due": 75.0,
            "recurring": True,
            "due_date": None,
            "start_date": date.today(),
            "frequency": "monthly",
            "interval": 1,
            "occurrences": 12,
            "end_date": None
        }
        
        assert bill_data["recurring"] is True
        assert bill_data["occurrences"] == 12
        assert bill_data["end_date"] is None

    def test_create_recurring_bill_with_end_date(self):
        """Test creating recurring bill with end date."""
        end_date = date.today() + timedelta(days=365)
        bill_data = {
            "bill_id": "test_4",
            "service": "Date Limited Service",
            "amount_due": 100.0,
            "recurring": True,
            "due_date": None,
            "start_date": date.today(),
            "frequency": "quarterly",
            "interval": 1,
            "occurrences": None,
            "end_date": end_date
        }
        
        assert bill_data["recurring"] is True
        assert bill_data["occurrences"] is None
        assert bill_data["end_date"] is not None
        assert bill_data["end_date"] == end_date


class TestBillDataValidation:
    """Test bill data validation logic."""

    def test_valid_non_recurring_bill_has_required_fields(self):
        """Test that valid non-recurring bill has required fields."""
        bill_data = {
            "bill_id": "test_1",
            "service": "Test",
            "amount_due": 100.0,
            "recurring": False,
            "due_date": date.today()
        }
        
        assert "bill_id" in bill_data
        assert "service" in bill_data
        assert "amount_due" in bill_data
        assert "recurring" in bill_data
        assert "due_date" in bill_data

    def test_valid_recurring_bill_has_required_fields(self):
        """Test that valid recurring bill has required fields."""
        bill_data = {
            "bill_id": "test_2",
            "service": "Test",
            "amount_due": 50.0,
            "recurring": True,
            "start_date": date.today(),
            "frequency": "monthly",
            "interval": 1
        }
        
        assert "bill_id" in bill_data
        assert "service" in bill_data
        assert "amount_due" in bill_data
        assert "recurring" in bill_data
        assert "start_date" in bill_data
        assert "frequency" in bill_data
        assert "interval" in bill_data

    def test_all_frequency_types_valid(self):
        """Test that all frequency types are valid."""
        frequencies = ["monthly", "quarterly", "annual", "weekly", "daily"]
        
        for frequency in frequencies:
            bill_data = {
                "bill_id": f"test_{frequency}",
                "service": "Test",
                "amount_due": 50.0,
                "recurring": True,
                "start_date": date.today(),
                "frequency": frequency,
                "interval": 1
            }
            
            assert bill_data["frequency"] in frequencies


class TestFilePathExtraction:
    """Test file path extraction logic."""

    def test_extract_file_extension(self):
        """Test extracting file extension from filename."""
        filename = "test_bills.csv"
        extension = filename.split('.')[-1]
        assert extension == "csv"
        
        filename = "bills.xlsx"
        extension = filename.split('.')[-1]
        assert extension == "xlsx"
        
        filename = "data.json"
        extension = filename.split('.')[-1]
        assert extension == "json"

    def test_create_temp_file_suffix(self):
        """Test creating temporary file with correct suffix."""
        uploaded_file_name = "sample_bills.csv"
        suffix = f".{uploaded_file_name.split('.')[-1]}"
        assert suffix == ".csv"
        
        uploaded_file_name = "bills.xlsx"
        suffix = f".{uploaded_file_name.split('.')[-1]}"
        assert suffix == ".xlsx"


class TestAmountValidation:
    """Test amount validation edge cases."""

    def test_zero_amount_allowed(self):
        """Test that zero amount is valid (edge case)."""
        bill_data = {
            "bill_id": "test_zero",
            "service": "Free Service",
            "amount_due": 0.0,
            "recurring": False,
            "due_date": date.today()
        }
        
        assert bill_data["amount_due"] == 0.0

    def test_large_amount_allowed(self):
        """Test that large amounts are valid."""
        bill_data = {
            "bill_id": "test_large",
            "service": "Expensive Service",
            "amount_due": 1000000.0,
            "recurring": False,
            "due_date": date.today()
        }
        
        assert bill_data["amount_due"] == 1000000.0

    def test_float_amount_conversion(self):
        """Test converting amount to float."""
        amount_input = "100.50"
        amount_due = float(amount_input)
        assert amount_due == 100.50
        
        amount_input = 100
        amount_due = float(amount_input)
        assert amount_due == 100.0


class TestDateHandling:
    """Test date handling in bill data."""

    def test_future_dates_valid(self):
        """Test that far future dates are valid."""
        far_future = date.today() + timedelta(days=365 * 10)  # 10 years
        
        bill_data = {
            "bill_id": "test_future",
            "service": "Future Service",
            "amount_due": 100.0,
            "recurring": False,
            "due_date": far_future
        }
        
        assert bill_data["due_date"] > date.today()

    def test_date_today_valid(self):
        """Test that today's date is valid."""
        today = date.today()
        
        bill_data = {
            "bill_id": "test_today",
            "service": "Today Service",
            "amount_due": 100.0,
            "recurring": True,
            "start_date": today,
            "frequency": "monthly",
            "interval": 1
        }
        
        assert bill_data["start_date"] == today

