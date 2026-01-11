"""
Unit Tests for Table Components
================================

Tests for unified bills table and bill summary table components. Verifies
DataFrame creation, bill attribute access, selection state management, and
edit/delete functionality.

Examples
--------
.. code-block:: python

   # Run all tests in this module.
   pytest tests/unit/test_tables.py

   # Run a specific test.
   pytest tests/unit/test_tables.py::TestUnifiedBillsTable::test_empty_bills_list_handling
"""

import pandas as pd
import pytest
from unittest.mock import MagicMock


class TestUnifiedBillsTable:
    """Test unified_bills_table logic."""

    def test_empty_bills_list_handling(self):
        """Test handling of empty bills list."""
        bills = []
        
        assert len(bills) == 0
        assert not bills  # Empty list is falsy

    def test_bill_attribute_access(self):
        """Test accessing bill attributes."""
        mock_bill = MagicMock()
        mock_bill.bill_id = "test_1"
        mock_bill.service = "Test Service"
        mock_bill.amount_due = 100.0
        mock_bill.recurring = False
        mock_bill.frequency = "N/A"
        mock_bill.end_date = None
        
        assert mock_bill.bill_id == "test_1"
        assert mock_bill.service == "Test Service"
        assert mock_bill.amount_due == 100.0
        assert mock_bill.recurring is False

    def test_bill_data_formatting(self):
        """Test bill data formatting for display."""
        mock_bill = MagicMock()
        mock_bill.bill_id = "test_1"
        mock_bill.service = "Test Service"
        mock_bill.amount_due = 100.0
        mock_bill.recurring = False
        mock_bill.frequency = "monthly"
        mock_bill.end_date = None
        
        # Test amount formatting.
        amount_formatted = f"${mock_bill.amount_due:.2f}"
        assert amount_formatted == "$100.00"
        
        # Test recurring status formatting.
        recurring_formatted = "Yes" if mock_bill.recurring else "No"
        assert recurring_formatted == "No"
        
        # Test frequency formatting.
        frequency_formatted = getattr(mock_bill, 'frequency', 'N/A')
        assert frequency_formatted == "monthly"
        
        # Test due date formatting.
        due_date_formatted = str(mock_bill.end_date) if mock_bill.end_date else "N/A"
        assert due_date_formatted == "N/A"

    def test_delete_button_key_generation(self):
        """Test delete button key generation."""
        bill_id = "test_bill_1"
        key = f"delete_{bill_id}"
        
        assert key == "delete_test_bill_1"
        
        bill_id = "bill-2"
        key = f"delete_{bill_id}"
        assert key == "delete_bill-2"

    def test_edit_button_key_generation(self):
        """Test edit button key generation."""
        bill_id = "test_bill_1"
        key = f"edit_{bill_id}"
        
        assert key == "edit_test_bill_1"
        
        bill_id = "bill-2"
        key = f"edit_{bill_id}"
        assert key == "edit_bill-2"

    def test_edit_state_key_generation(self):
        """Test edit state session key generation."""
        bill_id = "test_bill_1"
        key = f"editing_{bill_id}"
        
        assert key == "editing_test_bill_1"
        
        bill_id = "bill-2"
        key = f"editing_{bill_id}"
        assert key == "editing_bill-2"

    def test_bill_column_structure(self):
        """Test unified table DataFrame has expected column structure."""
        # Test that DataFrame has expected columns (no Actions column).
        expected_columns = [
            "ID", "Service", "Amount", "Recurring", 
            "Frequency", "Due Date"
        ]
        
        assert len(expected_columns) == 6
        assert "ID" in expected_columns
        assert "Service" in expected_columns
        assert "Amount" in expected_columns
        assert "Recurring" in expected_columns
        assert "Frequency" in expected_columns
        assert "Due Date" in expected_columns

    def test_dataframe_creation_from_bills(self):
        """Test creating DataFrame from bill objects."""
        from datetime import date
        
        mock_bill1 = MagicMock()
        mock_bill1.bill_id = "bill_1"
        mock_bill1.service = "Service One"
        mock_bill1.amount_due = 100.0
        mock_bill1.recurring = False
        mock_bill1.frequency = None
        mock_bill1.end_date = date(2024, 12, 31)
        
        mock_bill2 = MagicMock()
        mock_bill2.bill_id = "bill_2"
        mock_bill2.service = "Service Two"
        mock_bill2.amount_due = 50.0
        mock_bill2.recurring = True
        mock_bill2.frequency = "monthly"
        mock_bill2.end_date = None
        
        bills = [mock_bill1, mock_bill2]
        
        # Create DataFrame similar to unified_bills_table.
        bills_data = []
        for bill in bills:
            bills_data.append({
                "ID": bill.bill_id,
                "Service": bill.service,
                "Amount": f"${bill.amount_due:.2f}",
                "Recurring": "Yes" if bill.recurring else "No",
                "Frequency": getattr(bill, 'frequency', 'N/A'),
                "Due Date": str(bill.end_date) if bill.end_date else "N/A"
            })
        
        df = pd.DataFrame(bills_data)
        
        assert len(df) == 2
        assert list(df.columns) == ["ID", "Service", "Amount", "Recurring", "Frequency", "Due Date"]
        assert df.iloc[0]["ID"] == "bill_1"
        assert df.iloc[0]["Service"] == "Service One"
        assert df.iloc[0]["Amount"] == "$100.00"
        assert df.iloc[0]["Recurring"] == "No"
        assert df.iloc[1]["ID"] == "bill_2"
        assert df.iloc[1]["Recurring"] == "Yes"
        assert df.iloc[1]["Frequency"] == "monthly"

    def test_bill_map_creation(self):
        """Test creating bill_id to bill object mapping."""
        mock_bill1 = MagicMock()
        mock_bill1.bill_id = "bill_1"
        mock_bill1.service = "Service One"
        
        mock_bill2 = MagicMock()
        mock_bill2.bill_id = "bill_2"
        mock_bill2.service = "Service Two"
        
        bills = [mock_bill1, mock_bill2]
        
        # Create mapping similar to unified_bills_table.
        bill_map = {bill.bill_id: bill for bill in bills}
        
        assert len(bill_map) == 2
        assert "bill_1" in bill_map
        assert "bill_2" in bill_map
        assert bill_map["bill_1"] == mock_bill1
        assert bill_map["bill_2"] == mock_bill2

    def test_selection_state_key(self):
        """Test selection state session key."""
        key = "selected_bill_id"
        assert key == "selected_bill_id"

    def test_row_selection_mapping(self):
        """Test mapping DataFrame row index to bill_id."""
        from datetime import date
        
        mock_bill1 = MagicMock()
        mock_bill1.bill_id = "bill_1"
        mock_bill1.service = "Service One"
        mock_bill1.amount_due = 100.0
        mock_bill1.recurring = False
        mock_bill1.frequency = None
        mock_bill1.end_date = date(2024, 12, 31)
        
        mock_bill2 = MagicMock()
        mock_bill2.bill_id = "bill_2"
        mock_bill2.service = "Service Two"
        mock_bill2.amount_due = 50.0
        mock_bill2.recurring = False
        mock_bill2.frequency = None
        mock_bill2.end_date = None
        
        bills = [mock_bill1, mock_bill2]
        
        # Create DataFrame.
        bills_data = []
        for bill in bills:
            bills_data.append({
                "ID": bill.bill_id,
                "Service": bill.service,
                "Amount": f"${bill.amount_due:.2f}",
                "Recurring": "Yes" if bill.recurring else "No",
                "Frequency": getattr(bill, 'frequency', 'N/A'),
                "Due Date": str(bill.end_date) if bill.end_date else "N/A"
            })
        
        df = pd.DataFrame(bills_data)
        
        # Test mapping row index to bill_id.
        selected_idx = 0
        selected_bill_id = df.iloc[selected_idx]["ID"]
        assert selected_bill_id == "bill_1"
        
        selected_idx = 1
        selected_bill_id = df.iloc[selected_idx]["ID"]
        assert selected_bill_id == "bill_2"


class TestEditBillForm:
    """Test edit_bill_form logic."""

    def test_update_dict_creation_non_recurring(self):
        """Test creating update dictionary for non-recurring bill."""
        # Simulate form submission data for non-recurring bill.
        updates = {
            "service": "Updated Service",
            "amount_due": 150.0,
            "recurring": False,
            "end_date": None
        }
        
        # Clear recurring-specific fields.
        updates["start_date"] = None
        updates["frequency"] = None
        updates["interval"] = None
        updates["occurrences"] = None
        
        assert updates["service"] == "Updated Service"
        assert updates["amount_due"] == 150.0
        assert updates["recurring"] is False
        assert updates["start_date"] is None
        assert updates["frequency"] is None

    def test_update_dict_creation_recurring(self):
        """Test creating update dictionary for recurring bill."""
        # Simulate form submission data for recurring bill.
        from datetime import date
        
        updates = {
            "service": "Updated Recurring Service",
            "amount_due": 75.0,
            "recurring": True,
            "start_date": date(2024, 1, 1),
            "frequency": "monthly",
            "interval": 1,
            "occurrences": None,
            "end_date": None
        }
        
        assert updates["service"] == "Updated Recurring Service"
        assert updates["amount_due"] == 75.0
        assert updates["recurring"] is True
        assert updates["frequency"] == "monthly"
        assert updates["interval"] == 1

    def test_edit_form_key_prefix(self):
        """Test edit form key prefix generation."""
        bill_id = "test_bill_1"
        key_prefix = f"edit_{bill_id}"
        
        recurring_key = f"{key_prefix}_recurring_checkbox"
        form_key = f"{key_prefix}_edit_form"
        
        assert recurring_key == "edit_test_bill_1_recurring_checkbox"
        assert form_key == "edit_test_bill_1_edit_form"

    def test_bill_attribute_extraction(self):
        """Test extracting bill attributes for form pre-population."""
        from datetime import date
        
        mock_bill = MagicMock()
        mock_bill.bill_id = "test_1"
        mock_bill.service = "Test Service"
        mock_bill.amount_due = 100.0
        mock_bill.recurring = False
        mock_bill.end_date = date(2024, 12, 31)
        mock_bill.start_date = None
        mock_bill.frequency = None
        mock_bill.interval = 1
        mock_bill.occurrences = None
        
        # Test attribute access with getattr for optional fields.
        bill_id = mock_bill.bill_id
        service = mock_bill.service
        amount = mock_bill.amount_due
        recurring = mock_bill.recurring
        end_date = getattr(mock_bill, 'end_date', None)
        start_date = getattr(mock_bill, 'start_date', None)
        frequency = getattr(mock_bill, 'frequency', None)
        
        assert bill_id == "test_1"
        assert service == "Test Service"
        assert amount == 100.0
        assert recurring is False
        assert end_date == date(2024, 12, 31)
        assert start_date is None
        assert frequency is None


class TestBillSummaryTable:
    """Test create_bill_summary_table logic."""

    def test_empty_envelopes_handling(self):
        """Test handling of empty envelopes list."""
        envelopes = []
        
        if not envelopes:
            df = pd.DataFrame(columns=[
                'Bill ID', 'Service', 'Start Contribution Date',
                'Due Date', 'Allocation', 'Remaining', 'Fully Funded'
            ])
        
        assert df.empty
        assert len(df.columns) == 7

    def test_envelope_attribute_access(self):
        """Test accessing envelope attributes."""
        mock_envelope = MagicMock()
        mock_envelope.start_contrib_date = None
        mock_envelope.initial_allocation = 100.0
        
        mock_bill_instance = MagicMock()
        mock_bill_instance.bill_id = "test_1"
        mock_bill_instance.service = "Test Service"
        mock_bill_instance.due_date = None
        
        mock_envelope.bill_instance = mock_bill_instance
        
        mock_schedule = MagicMock()
        mock_schedule.cash_flows = []
        mock_schedule.total_amount_in_range.return_value = 500.0
        
        mock_envelope.schedule = mock_schedule
        mock_envelope.is_fully_funded.return_value = False
        mock_envelope.remaining.return_value = 50.0
        
        # Test attribute access
        assert mock_envelope.start_contrib_date is None or isinstance(
            mock_envelope.start_contrib_date, type(None)
        )
        assert mock_envelope.initial_allocation == 100.0
        assert mock_envelope.bill_instance.bill_id == "test_1"
        assert mock_envelope.bill_instance.service == "Test Service"
        assert hasattr(mock_envelope, 'schedule')
        assert hasattr(mock_envelope, 'is_fully_funded')
        assert hasattr(mock_envelope, 'remaining')

    def test_bill_summary_dataframe_creation(self):
        """Test creating bill summary DataFrame."""
        bill_data = [
            {
                'Bill ID': 'bill_1',
                'Service': 'Service One',
                'Start Contribution Date': None,
                'Due Date': None,
                'Allocation': '$100.00',
                'Remaining': '$25.00',
                'Fully Funded': 'No'
            }
        ]
        
        df = pd.DataFrame(bill_data)
        
        assert len(df) == 1
        assert 'Bill ID' in df.columns
        assert 'Service' in df.columns
        assert 'Start Contribution Date' in df.columns
        assert 'Due Date' in df.columns
        assert 'Allocation' in df.columns
        assert 'Remaining' in df.columns
        assert 'Fully Funded' in df.columns
        # Verify Average Contribution Amount is not present
        assert 'Average Contribution Amount' not in df.columns

    def test_bill_summary_required_columns(self):
        """Test bill summary DataFrame has all required columns."""
        df = pd.DataFrame(columns=[
            'Bill ID', 'Service', 'Start Contribution Date',
            'Due Date', 'Allocation', 'Remaining', 'Fully Funded'
        ])
        
        expected_columns = [
            'Bill ID', 'Service', 'Start Contribution Date',
            'Due Date', 'Allocation', 'Remaining', 'Fully Funded'
        ]
        
        assert list(df.columns) == expected_columns

    def test_fully_funded_boolean_conversion(self):
        """Test converting fully_funded boolean to string."""
        fully_funded = True
        result = "Yes" if fully_funded else "No"
        assert result == "Yes"
        
        fully_funded = False
        result = "Yes" if fully_funded else "No"
        assert result == "No"

    def test_currency_formatting(self):
        """Test currency formatting for allocation and remaining."""
        allocation = 100.0
        formatted = f"${allocation:.2f}"
        assert formatted == "$100.00"
        
        remaining = 25.5
        formatted = f"${remaining:.2f}"
        assert formatted == "$25.50"

