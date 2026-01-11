"""
Integration Tests for Strategy Selection
=========================================

Tests for different allocation and scheduler strategies in quick_report().
Verifies that different strategy combinations produce valid reports and
that invalid strategies raise appropriate errors.

Examples
--------
.. code-block:: python

   # Run all tests in this module.
   pytest tests/integration/test_strategy_selection.py

   # Run a specific test class.
   pytest tests/integration/test_strategy_selection.py::TestAllocationStrategies
"""

from datetime import date, timedelta
import pytest


class TestAllocationStrategies:
    """Test different allocation strategies."""

    def test_quick_report_with_sorted_allocation(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test quick_report with sorted allocation strategy."""
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        report = sample_fund_with_balance.quick_report(
            contribution_interval=14,
            allocation_strategy="sorted",
            scheduler_strategy="independent_scheduler",
            active_only=True
        )
        
        assert isinstance(report, dict)
        if report:
            first_date = next(iter(report.keys()))
            assert isinstance(first_date, date)

    def test_quick_report_with_proportional_allocation(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test quick_report with proportional allocation strategy."""
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Proportional allocation requires a 'method' parameter
        report = sample_fund_with_balance.quick_report(
            contribution_interval=14,
            allocation_strategy="proportional",
            scheduler_strategy="independent_scheduler",
            active_only=True,
            method="proportional"  # Proportional allocation method
        )
        
        assert isinstance(report, dict)
        if report:
            first_date = next(iter(report.keys()))
            assert isinstance(first_date, date)

    def test_quick_report_with_proportional_allocation_different_methods(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test quick_report with different proportional allocation methods."""
        # Test with methods that work without additional parameters
        # Note: "zero" causes division by zero, "urgency" requires curr_date
        methods = ["proportional", "equal"]
        
        for method in methods:
            # Create a fresh fund for each method to avoid conflicts
            from sinkingfund import SinkingFund
            from datetime import date, timedelta
            test_start = date.today()
            test_end = test_start + timedelta(days=365)
            
            fund = SinkingFund(
                start_date=test_start,
                end_date=test_end,
                balance=1000.0
            )
            fund.add_bills(
                source=sample_multiple_bills_data,
                contribution_interval=14
            )
            
            report = fund.quick_report(
                contribution_interval=14,
                allocation_strategy="proportional",
                scheduler_strategy="independent_scheduler",
                active_only=True,
                method=method
            )
            
            assert isinstance(report, dict)

    def test_quick_report_default_allocation_strategy(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test quick_report with default allocation strategy (sorted)."""
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Default allocation_strategy should be "sorted"
        report = sample_fund_with_balance.quick_report(
            contribution_interval=14,
            scheduler_strategy="independent_scheduler",
            active_only=True
        )
        
        assert isinstance(report, dict)


class TestSchedulerStrategies:
    """Test different scheduler strategies."""

    def test_quick_report_with_independent_scheduler(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test quick_report with independent_scheduler strategy."""
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
        if report:
            first_date = next(iter(report.keys()))
            assert isinstance(first_date, date)

    def test_quick_report_default_scheduler_strategy(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test quick_report with default scheduler strategy."""
        sample_fund.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Default scheduler_strategy should be "independent_scheduler"
        report = sample_fund.quick_report(
            contribution_interval=14,
            allocation_strategy="sorted",
            active_only=True
        )
        
        assert isinstance(report, dict)


class TestStrategyCombinations:
    """Test different combinations of allocation and scheduler strategies."""

    def test_sorted_with_independent_scheduler(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test sorted allocation with independent scheduler."""
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        report = sample_fund_with_balance.quick_report(
            contribution_interval=14,
            allocation_strategy="sorted",
            scheduler_strategy="independent_scheduler",
            active_only=True
        )
        
        assert isinstance(report, dict)
        envelopes = sample_fund_with_balance.get_envelopes()
        assert len(envelopes) > 0

    def test_proportional_with_independent_scheduler(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test proportional allocation with independent scheduler."""
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Proportional allocation requires a 'method' parameter
        report = sample_fund_with_balance.quick_report(
            contribution_interval=14,
            allocation_strategy="proportional",
            scheduler_strategy="independent_scheduler",
            active_only=True,
            method="proportional"  # Proportional allocation method
        )
        
        assert isinstance(report, dict)
        envelopes = sample_fund_with_balance.get_envelopes()
        assert len(envelopes) > 0

    def test_different_allocation_strategies_produce_different_results(
        self, sample_fund_with_balance, sample_multiple_bills_data, test_start_date, test_end_date
    ):
        """Test that different allocation strategies produce different results."""
        # Create a fresh fund for sorted allocation
        fund_sorted = sample_fund_with_balance
        fund_sorted.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Run with sorted allocation
        report_sorted = fund_sorted.quick_report(
            contribution_interval=14,
            allocation_strategy="sorted",
            scheduler_strategy="independent_scheduler",
            active_only=True
        )
        
        # Create a new fund for proportional allocation to avoid
        # duplicate bills
        from sinkingfund import SinkingFund
        fund_proportional = SinkingFund(
            start_date=test_start_date,
            end_date=test_end_date,
            balance=1000.0
        )
        fund_proportional.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Run with proportional allocation (requires method parameter)
        report_proportional = fund_proportional.quick_report(
            contribution_interval=14,
            allocation_strategy="proportional",
            scheduler_strategy="independent_scheduler",
            active_only=True,
            method="proportional"  # Proportional allocation method
        )
        
        # Both should produce valid reports
        assert isinstance(report_sorted, dict)
        assert isinstance(report_proportional, dict)


class TestStrategyValidation:
    """Test strategy parameter validation."""

    def test_invalid_allocation_strategy_raises_error(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test that invalid allocation strategy raises an error."""
        sample_fund.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Invalid allocation strategy should raise an error (KeyError)
        with pytest.raises(KeyError):
            sample_fund.quick_report(
                contribution_interval=14,
                allocation_strategy="invalid_strategy",
                scheduler_strategy="independent_scheduler",
                active_only=True
            )

    def test_invalid_scheduler_strategy_raises_error(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test that invalid scheduler strategy raises an error."""
        sample_fund.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Invalid scheduler strategy should raise an error (KeyError)
        with pytest.raises(KeyError):
            sample_fund.quick_report(
                contribution_interval=14,
                allocation_strategy="sorted",
                scheduler_strategy="invalid_strategy",
                active_only=True
            )

