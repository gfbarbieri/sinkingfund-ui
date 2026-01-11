"""
Integration Tests for Bill Management Operations
=================================================

Tests adding, deleting, and retrieving bills using the SinkingFund API
with real instances. Verifies that bills are correctly created, managed,
and retrieved with proper attributes and validation.

Examples
--------
.. code-block:: python

   # Run all tests in this module.
   pytest tests/integration/test_bill_management.py

   # Run a specific test class.
   pytest tests/integration/test_bill_management.py::TestAddBills
"""

########################################################################
## IMPORTS
########################################################################

from datetime import date, timedelta

import pytest


########################################################################
## ADD BILLS TESTS
########################################################################

class TestAddBills:
    """Test adding bills to a fund."""

    def test_add_single_non_recurring_bill(
        self, sample_fund, sample_non_recurring_bill_data
    ):
        """Test adding a single non-recurring bill."""
        initial_count = len(sample_fund.get_bills())

        sample_fund.add_bills(
            source=[sample_non_recurring_bill_data],
            contribution_interval=14
        )

        bills = sample_fund.get_bills()
        assert len(bills) == initial_count + 1
        assert bills[0].bill_id == "test_bill_1"
        assert bills[0].service == "Test Service"
        assert bills[0].amount_due == 100.0
        assert bills[0].recurring is False

    def test_add_single_recurring_bill(
        self, sample_fund, sample_recurring_bill_data
    ):
        """Test adding a single recurring bill."""
        initial_count = len(sample_fund.get_bills())

        sample_fund.add_bills(
            source=[sample_recurring_bill_data],
            contribution_interval=14
        )

        bills = sample_fund.get_bills()
        assert len(bills) == initial_count + 1
        assert bills[0].bill_id == "test_recurring_1"
        assert bills[0].recurring is True
        assert bills[0].frequency == "monthly"

    @pytest.mark.parametrize("frequency", [
        "monthly", "quarterly", "annual", "weekly", "daily"
    ])
    def test_add_recurring_bills_different_frequencies(
        self, sample_fund, frequency
    ):
        """Test adding recurring bills with all frequency types."""
        from tests.integration.conftest import create_bill_with_frequency

        bill_data = create_bill_with_frequency(frequency)
        sample_fund.add_bills(source=[bill_data], contribution_interval=14)

        bills = sample_fund.get_bills()
        assert len(bills) == 1
        assert bills[0].frequency == frequency

    def test_add_multiple_bills(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test adding multiple bills in one call."""
        initial_count = len(sample_fund.get_bills())

        sample_fund.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )

        bills = sample_fund.get_bills()
        assert len(bills) == initial_count + 3
        assert bills[0].bill_id == "bill_1"
        assert bills[1].bill_id == "bill_2"
        assert bills[2].bill_id == "bill_3"

    def test_add_bills_contribution_interval(
        self, sample_fund, sample_non_recurring_bill_data
    ):
        """Test that contribution_interval parameter is accepted."""
        # Should not raise an error with contribution_interval.
        sample_fund.add_bills(
            source=[sample_non_recurring_bill_data],
            contribution_interval=7  # Weekly contributions.
        )

        bills = sample_fund.get_bills()
        assert len(bills) == 1


########################################################################
## DELETE BILLS TESTS
########################################################################

class TestDeleteBills:
    """Test deleting bills from a fund."""

    def test_delete_single_bill(
        self, sample_fund, sample_non_recurring_bill_data
    ):
        """Test deleting a single bill by ID."""
        sample_fund.add_bills(
            source=[sample_non_recurring_bill_data],
            contribution_interval=14
        )

        initial_count = len(sample_fund.get_bills())
        assert initial_count == 1

        sample_fund.delete_bills(["test_bill_1"])

        bills = sample_fund.get_bills()
        assert len(bills) == 0

    def test_delete_multiple_bills(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test deleting multiple bills at once."""
        sample_fund.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )

        initial_count = len(sample_fund.get_bills())
        assert initial_count == 3

        sample_fund.delete_bills(["bill_1", "bill_3"])

        bills = sample_fund.get_bills()
        assert len(bills) == 1
        assert bills[0].bill_id == "bill_2"

    def test_delete_nonexistent_bill(self, sample_fund):
        """Test attempting to delete a non-existent bill."""
        # The API raises ValueError when deleting non-existent bill.
        initial_count = len(sample_fund.get_bills())

        with pytest.raises(ValueError):
            sample_fund.delete_bills(["nonexistent_bill"])

        bills = sample_fund.get_bills()
        assert len(bills) == initial_count


########################################################################
## GET BILLS TESTS
########################################################################

class TestGetBills:
    """Test retrieving bills from a fund."""

    def test_get_bills_empty_fund(self, sample_fund):
        """Test getting bills from an empty fund."""
        bills = sample_fund.get_bills()
        assert isinstance(bills, list)
        assert len(bills) == 0

    def test_get_bills_after_adding(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test getting bills after adding them."""
        sample_fund.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )

        bills = sample_fund.get_bills()
        assert len(bills) == 3
        assert all(hasattr(bill, 'bill_id') for bill in bills)
        assert all(hasattr(bill, 'service') for bill in bills)
        assert all(hasattr(bill, 'amount_due') for bill in bills)
        assert all(hasattr(bill, 'recurring') for bill in bills)

    def test_get_bills_bill_attributes(
        self, sample_fund, sample_non_recurring_bill_data
    ):
        """Test that bill objects have expected attributes."""
        sample_fund.add_bills(
            source=[sample_non_recurring_bill_data],
            contribution_interval=14
        )

        bills = sample_fund.get_bills()
        bill = bills[0]

        assert hasattr(bill, 'bill_id')
        assert hasattr(bill, 'service')
        assert hasattr(bill, 'amount_due')
        assert hasattr(bill, 'recurring')
        # Non-recurring bills may have start_date instead of due_date.
        assert hasattr(bill, 'start_date') or hasattr(bill, 'due_date')
