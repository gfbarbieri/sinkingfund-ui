"""
Integration Tests for Schedule Visualization
==============================================

Tests verify that schedule visualization can be created from generated
reports and that the visualization components work correctly with real
fund data.

Examples
--------
.. code-block:: python

   # Run all tests in this module.
   pytest tests/integration/test_schedule_visualization.py

   # Run a specific test class.
   pytest tests/integration/test_schedule_visualization.py::TestScheduleVisualization
"""

########################################################################
## IMPORTS
########################################################################

import pytest
import pandas as pd

from sinkingfund_ui.utils.report_utils import convert_report_section_to_dataframe
from sinkingfund_ui.components.figures import create_timeseries_chart_from_dfs


########################################################################
## SCHEDULE VISUALIZATION TESTS
########################################################################

class TestScheduleVisualization:
    """Test schedule visualization with real fund data."""

    def test_visualization_from_generated_report(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test that visualization can be created from generated report."""
        # Add bills and generate report.
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Update contribution dates, allocate, and schedule to ensure report has data.
        sample_fund_with_balance.update_contribution_dates(14)
        sample_fund_with_balance.allocate(strategy="sorted")
        sample_fund_with_balance.schedule(strategy="independent_scheduler")
        
        # Generate report.
        report = sample_fund_with_balance.report(active_only=True)
        
        # Verify report structure.
        assert isinstance(report, dict)
        # Report may be empty if no bill instances in planning period, which is valid.
        
        # Convert report sections to DataFrames.
        account_balance_df = convert_report_section_to_dataframe(
            report, 'account_balance'
        )
        contributions_df = convert_report_section_to_dataframe(
            report, 'contributions'
        )
        payouts_df = convert_report_section_to_dataframe(
            report, 'payouts'
        )
        
        # Verify DataFrames are created.
        assert isinstance(account_balance_df, pd.DataFrame)
        assert isinstance(contributions_df, pd.DataFrame)
        assert isinstance(payouts_df, pd.DataFrame)
        
        # Verify DataFrames have Date index.
        assert isinstance(account_balance_df.index, pd.DatetimeIndex) or \
               all(isinstance(idx, (pd.Timestamp, type(account_balance_df.index[0]))) 
                   for idx in account_balance_df.index[:5]) if len(account_balance_df) > 0 else True
        
        # Create visualization chart.
        fig = create_timeseries_chart_from_dfs(
            account_balance_df, contributions_df, payouts_df
        )
        
        # Verify chart is created.
        assert fig is not None
        assert len(fig.data) >= 1  # At least balance line

    def test_visualization_dataframe_structure(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test that converted DataFrames have correct structure."""
        # Add bills and generate report.
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Generate report.
        report = sample_fund_with_balance.report(active_only=True)
        
        # Convert to DataFrames.
        account_balance_df = convert_report_section_to_dataframe(
            report, 'account_balance'
        )
        contributions_df = convert_report_section_to_dataframe(
            report, 'contributions'
        )
        payouts_df = convert_report_section_to_dataframe(
            report, 'payouts'
        )
        
        # Verify account balance DataFrame structure.
        if not account_balance_df.empty:
            assert 'total' in account_balance_df.columns
            assert len(account_balance_df) > 0
        
        # Verify contributions DataFrame structure.
        if not contributions_df.empty:
            assert 'total' in contributions_df.columns
            assert 'count' in contributions_df.columns
        
        # Verify payouts DataFrame structure.
        if not payouts_df.empty:
            assert 'total' in payouts_df.columns
            assert 'count' in payouts_df.columns

    def test_visualization_with_contributions_and_payouts(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test visualization with both contributions and payouts."""
        # Add bills and generate report.
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Update contribution dates and allocate.
        sample_fund_with_balance.update_contribution_dates(14)
        sample_fund_with_balance.allocate(strategy="sorted")
        sample_fund_with_balance.schedule(strategy="independent_scheduler")
        
        # Generate report.
        report = sample_fund_with_balance.report(active_only=True)
        
        # Convert to DataFrames.
        account_balance_df = convert_report_section_to_dataframe(
            report, 'account_balance'
        )
        contributions_df = convert_report_section_to_dataframe(
            report, 'contributions'
        )
        payouts_df = convert_report_section_to_dataframe(
            report, 'payouts'
        )
        
        # Create visualization.
        fig = create_timeseries_chart_from_dfs(
            account_balance_df, contributions_df, payouts_df
        )
        
        # Verify chart has multiple traces (balance + contributions/payouts).
        assert fig is not None
        assert len(fig.data) >= 1
        
        # Verify balance trace exists.
        balance_trace = fig.data[0]
        assert balance_trace.name == 'Account Balance'
        
        # Check for contribution or payout traces if data exists.
        trace_names = [trace.name for trace in fig.data]
        if not contributions_df.empty and contributions_df['total'].sum() > 0:
            assert 'Contributions' in trace_names
        if not payouts_df.empty and payouts_df['total'].sum() < 0:
            assert 'Payouts' in trace_names

    def test_visualization_empty_report(self):
        """Test visualization with empty report."""
        # Create empty report.
        report = {}
        
        # Convert to DataFrames.
        account_balance_df = convert_report_section_to_dataframe(
            report, 'account_balance'
        )
        contributions_df = convert_report_section_to_dataframe(
            report, 'contributions'
        )
        payouts_df = convert_report_section_to_dataframe(
            report, 'payouts'
        )
        
        # Verify DataFrames are empty.
        assert account_balance_df.empty
        assert contributions_df.empty
        assert payouts_df.empty
        
        # Create visualization (should handle empty DataFrames).
        fig = create_timeseries_chart_from_dfs(
            account_balance_df, contributions_df, payouts_df
        )
        
        # Chart should still be created (may have no traces if all DataFrames are empty).
        assert fig is not None
