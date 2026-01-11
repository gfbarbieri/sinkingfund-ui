"""
Integration Tests for Quick Report Generation
==============================================

Tests for the quick_report() method functionality, including different
contribution intervals, allocation strategies, and envelope creation.
Verifies that reports are generated correctly and envelopes are created
with proper attributes.

Examples
--------
.. code-block:: python

   # Run all tests in this module.
   pytest tests/integration/test_quick_report.py

   # Run a specific test class.
   pytest tests/integration/test_quick_report.py::TestQuickReportGeneration
"""

from datetime import date, timedelta
import pytest


class TestQuickReportGeneration:
    """Test quick_report() method functionality."""

    def test_quick_report_with_bills(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test running quick_report() with bills present."""
        sample_fund.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        report = sample_fund.quick_report(
            contribution_interval=14,
            allocation_strategy="sorted",
            scheduler_strategy="independent_scheduler",
            active_only=True
        )
        
        assert isinstance(report, dict)
        # Verify report structure: dict[date, dict]
        if report:
            first_date = next(iter(report.keys()))
            assert isinstance(first_date, date)
            assert isinstance(report[first_date], dict)

    def test_quick_report_return_type(self, sample_fund, sample_non_recurring_bill_data):
        """Test that quick_report returns correct type."""
        sample_fund.add_bills(
            source=[sample_non_recurring_bill_data],
            contribution_interval=14
        )
        
        report = sample_fund.quick_report(
            contribution_interval=14,
            allocation_strategy="sorted",
            scheduler_strategy="independent_scheduler",
            active_only=True
        )
        
        assert isinstance(report, dict)

    def test_quick_report_different_contribution_interval(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test quick_report with different contribution_interval values."""
        sample_fund.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Test weekly contributions
        report_weekly = sample_fund.quick_report(
            contribution_interval=7,
            allocation_strategy="sorted",
            scheduler_strategy="independent_scheduler",
            active_only=True
        )
        
        # Test monthly contributions
        report_monthly = sample_fund.quick_report(
            contribution_interval=30,
            allocation_strategy="sorted",
            scheduler_strategy="independent_scheduler",
            active_only=True
        )
        
        assert isinstance(report_weekly, dict)
        assert isinstance(report_monthly, dict)

    def test_quick_report_active_only_true(self, sample_fund, sample_non_recurring_bill_data):
        """Test quick_report with active_only=True."""
        sample_fund.add_bills(
            source=[sample_non_recurring_bill_data],
            contribution_interval=14
        )
        
        report = sample_fund.quick_report(
            contribution_interval=14,
            allocation_strategy="sorted",
            scheduler_strategy="independent_scheduler",
            active_only=True
        )
        
        assert isinstance(report, dict)

    def test_quick_report_active_only_false(
        self, sample_fund, sample_non_recurring_bill_data
    ):
        """Test quick_report with active_only=False."""
        sample_fund.add_bills(
            source=[sample_non_recurring_bill_data],
            contribution_interval=14
        )
        
        report = sample_fund.quick_report(
            contribution_interval=14,
            allocation_strategy="sorted",
            scheduler_strategy="independent_scheduler",
            active_only=False
        )
        
        assert isinstance(report, dict)

    def test_quick_report_default_parameters(
        self, sample_fund, sample_recurring_bill_data
    ):
        """Test quick_report with default allocation_strategy and scheduler_strategy."""
        sample_fund.add_bills(
            source=[sample_recurring_bill_data],
            contribution_interval=14
        )
        
        # Use default parameters (should work with new API)
        # Defaults: allocation_strategy="sorted",
        # scheduler_strategy="independent_scheduler"
        report = sample_fund.quick_report(
            contribution_interval=14,
            active_only=True
        )
        
        assert isinstance(report, dict)


class TestEnvelopeCreation:
    """Test envelope creation after quick_report."""

    def test_envelopes_created_after_report(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test that envelopes are created after running quick_report()."""
        sample_fund.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Run quick report to create envelopes
        sample_fund.quick_report(
            contribution_interval=14,
            allocation_strategy="sorted",
            scheduler_strategy="independent_scheduler",
            active_only=True
        )
        
        envelopes = sample_fund.get_envelopes()
        assert isinstance(envelopes, list)
        assert len(envelopes) > 0

    def test_get_envelopes_returns_list(
        self, sample_fund, sample_recurring_bill_data
    ):
        """Test that get_envelopes() returns a list."""
        sample_fund.add_bills(
            source=[sample_recurring_bill_data],
            contribution_interval=14
        )
        
        sample_fund.quick_report(
            contribution_interval=14,
            active_only=True
        )
        
        envelopes = sample_fund.get_envelopes()
        assert isinstance(envelopes, list)

    def test_envelope_attributes_accessible(
        self, sample_fund, sample_recurring_bill_data, test_end_date
    ):
        """Test that envelope attributes are accessible."""
        sample_fund.add_bills(
            source=[sample_recurring_bill_data],
            contribution_interval=14
        )
        
        sample_fund.quick_report(
            contribution_interval=14,
            active_only=True
        )
        
        envelopes = sample_fund.get_envelopes()
        assert len(envelopes) > 0
        
        envelope = envelopes[0]
        
        # Verify envelope has expected attributes
        assert hasattr(envelope, 'start_contrib_date')
        assert hasattr(envelope, 'initial_allocation')
        assert hasattr(envelope, 'bill_instance')
        assert hasattr(envelope, 'schedule')
        
        # Verify bill_instance attributes
        assert hasattr(envelope.bill_instance, 'bill_id')
        assert hasattr(envelope.bill_instance, 'service')
        assert hasattr(envelope.bill_instance, 'due_date')
        
        # Verify schedule attributes
        assert hasattr(envelope.schedule, 'cash_flows')
        assert hasattr(envelope.schedule, 'total_amount_in_range')
        
        # Test methods
        assert hasattr(envelope, 'is_fully_funded')
        assert hasattr(envelope, 'remaining')

    def test_envelope_bill_summary_integration(
        self, sample_fund, sample_recurring_bill_data, test_end_date
    ):
        """Test creating bill summary data from envelopes."""
        sample_fund.add_bills(
            source=[sample_recurring_bill_data],
            contribution_interval=14
        )
        
        sample_fund.quick_report(
            contribution_interval=14,
            active_only=True
        )
        
        envelopes = sample_fund.get_envelopes()
        assert len(envelopes) > 0
        
        envelope = envelopes[0]
        
        # Extract data similar to create_bill_summary_table
        start_contrib_date = envelope.start_contrib_date
        allocation = envelope.initial_allocation
        bill_id = envelope.bill_instance.bill_id
        service = envelope.bill_instance.service
        due_date = envelope.bill_instance.due_date
        
        # Calculate average contribution
        if len(envelope.schedule.cash_flows) > 0:
            avg_contrib = (
                envelope.schedule.total_amount_in_range(exclude='payouts') /
                len(envelope.schedule.cash_flows)
            )
        else:
            avg_contrib = 0.0
        
        # Test methods
        fully_funded = envelope.is_fully_funded(as_of_date=test_end_date)
        remaining = envelope.remaining(as_of_date=test_end_date)
        
        # Verify all values are accessible and reasonable
        assert isinstance(start_contrib_date, date)
        # Allocation may be Decimal type.
        from decimal import Decimal
        assert isinstance(allocation, (int, float, Decimal))
        assert isinstance(bill_id, str)
        assert isinstance(service, str)
        assert isinstance(fully_funded, bool)
        assert isinstance(remaining, (int, float, Decimal))

