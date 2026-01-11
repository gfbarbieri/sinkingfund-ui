"""
Unit Tests for Figure Components
=================================

Tests for time series chart creation from DataFrames. Verifies chart
structure, traces, hover text, and handling of edge cases.

Examples
--------
.. code-block:: python

   # Run all tests in this module.
   pytest tests/unit/test_figures.py

   # Run a specific test class.
   pytest tests/unit/test_figures.py::TestTimeSeriesChart
"""

import pytest
import pandas as pd
from datetime import date, timedelta

from sinkingfund_ui.components.figures import create_timeseries_chart_from_dfs


class TestTimeSeriesChart:
    """Test time series chart creation."""

    def test_create_timeseries_chart_structure(self):
        """Test that chart has correct structure with 3 traces."""
        # Create sample DataFrames.
        dates = [date.today() + timedelta(days=i) for i in range(5)]
        balance_df = pd.DataFrame({
            'total': [1000.0, 1100.0, 1200.0, 1150.0, 1300.0]
        }, index=dates)
        
        contrib_df = pd.DataFrame({
            'total': [100.0, 100.0, 0.0, 0.0, 150.0],
            'count': [1, 1, 0, 0, 1],
            'bill_1': [100.0, 100.0, 0.0, 0.0, 150.0]
        }, index=dates)
        
        payouts_df = pd.DataFrame({
            'total': [0.0, 0.0, 0.0, -50.0, 0.0],
            'count': [0, 0, 0, 1, 0],
            'bill_1': [0.0, 0.0, 0.0, -50.0, 0.0]
        }, index=dates)
        
        # Create chart.
        fig = create_timeseries_chart_from_dfs(
            balance_df, contrib_df, payouts_df
        )
        
        # Verify figure structure.
        assert fig is not None
        # Should have 3 traces: balance line, contributions, payouts.
        assert len(fig.data) == 3

    def test_create_timeseries_chart_balance_line(self):
        """Test account balance line trace properties."""
        # Create sample DataFrames.
        dates = [date.today() + timedelta(days=i) for i in range(3)]
        balance_df = pd.DataFrame({
            'total': [1000.0, 1100.0, 1200.0]
        }, index=dates)
        
        contrib_df = pd.DataFrame({
            'total': [0.0, 0.0, 0.0],
            'count': [0, 0, 0]
        }, index=dates)
        
        payouts_df = pd.DataFrame({
            'total': [0.0, 0.0, 0.0],
            'count': [0, 0, 0]
        }, index=dates)
        
        # Create chart.
        fig = create_timeseries_chart_from_dfs(
            balance_df, contrib_df, payouts_df
        )
        
        # Verify balance line trace (first trace).
        balance_trace = fig.data[0]
        assert balance_trace.name == 'Account Balance'
        assert balance_trace.mode == 'lines'
        assert balance_trace.line.color == 'blue'
        assert len(balance_trace.x) == 3
        assert len(balance_trace.y) == 3

    def test_create_timeseries_chart_contribution_markers(self):
        """Test contribution markers with hover text."""
        # Create sample DataFrames.
        dates = [date.today() + timedelta(days=i) for i in range(3)]
        balance_df = pd.DataFrame({
            'total': [1000.0, 1100.0, 1200.0]
        }, index=dates)
        
        contrib_df = pd.DataFrame({
            'total': [100.0, 0.0, 100.0],
            'count': [1, 0, 1],
            'bill_1': [50.0, 0.0, 50.0],
            'bill_2': [50.0, 0.0, 50.0]
        }, index=dates)
        
        payouts_df = pd.DataFrame({
            'total': [0.0, 0.0, 0.0],
            'count': [0, 0, 0]
        }, index=dates)
        
        # Create chart.
        fig = create_timeseries_chart_from_dfs(
            balance_df, contrib_df, payouts_df
        )
        
        # Verify contribution markers trace (second trace).
        contrib_trace = fig.data[1]
        assert contrib_trace.name == 'Contributions'
        assert contrib_trace.mode == 'markers'
        assert contrib_trace.marker.color == 'green'
        # Should only have markers for dates with contributions > 0.
        assert len(contrib_trace.x) == 2  # Two dates with contributions
        # Verify hover text contains bill breakdown.
        # Note: bill IDs are stripped of 'bill_' prefix in hover text.
        assert len(contrib_trace.text) == 2
        assert '1' in contrib_trace.text[0] or '2' in contrib_trace.text[0]

    def test_create_timeseries_chart_payout_markers(self):
        """Test payout markers with hover text."""
        # Create sample DataFrames.
        dates = [date.today() + timedelta(days=i) for i in range(3)]
        balance_df = pd.DataFrame({
            'total': [1000.0, 950.0, 900.0]
        }, index=dates)
        
        contrib_df = pd.DataFrame({
            'total': [0.0, 0.0, 0.0],
            'count': [0, 0, 0]
        }, index=dates)
        
        payouts_df = pd.DataFrame({
            'total': [0.0, -50.0, -50.0],
            'count': [0, 1, 1],
            'bill_1': [0.0, -30.0, -30.0],
            'bill_2': [0.0, -20.0, -20.0]
        }, index=dates)
        
        # Create chart.
        fig = create_timeseries_chart_from_dfs(
            balance_df, contrib_df, payouts_df
        )
        
        # Verify payout markers trace (should be third trace if balance exists).
        # Find payout trace by name.
        payout_trace = None
        for trace in fig.data:
            if trace.name == 'Payouts':
                payout_trace = trace
                break
        
        assert payout_trace is not None
        assert payout_trace.mode == 'markers'
        assert payout_trace.marker.color == 'red'
        # Should only have markers for dates with payouts < 0.
        assert len(payout_trace.x) == 2  # Two dates with payouts
        # Verify hover text contains bill breakdown.
        # Note: bill IDs are stripped of 'bill_' prefix in hover text.
        assert len(payout_trace.text) == 2
        assert '1' in payout_trace.text[0] or '2' in payout_trace.text[0]

    def test_create_timeseries_chart_empty_dataframes(self):
        """Test handling of empty DataFrames."""
        # Create empty DataFrames.
        balance_df = pd.DataFrame(columns=['total'])
        contrib_df = pd.DataFrame(columns=['total', 'count'])
        payouts_df = pd.DataFrame(columns=['total', 'count'])
        
        # Create chart.
        fig = create_timeseries_chart_from_dfs(
            balance_df, contrib_df, payouts_df
        )
        
        # Should still create figure (may have no traces if all DataFrames are empty).
        assert fig is not None
        # Empty DataFrames result in no traces, which is acceptable.

    def test_create_timeseries_chart_hover_text_format(self):
        """Test bill breakdown format in hover text."""
        # Create sample DataFrames with specific bill amounts.
        dates = [date.today()]
        balance_df = pd.DataFrame({
            'total': [1000.0]
        }, index=dates)
        
        contrib_df = pd.DataFrame({
            'total': [150.0],
            'count': [2],
            'bill_1': [100.0],
            'bill_2': [50.0]
        }, index=dates)
        
        payouts_df = pd.DataFrame({
            'total': [0.0],
            'count': [0]
        }, index=dates)
        
        # Create chart.
        fig = create_timeseries_chart_from_dfs(
            balance_df, contrib_df, payouts_df
        )
        
        # Verify hover text format.
        contrib_trace = fig.data[1]
        hover_text = contrib_trace.text[0]
        # Should contain date, contributions total, and bill breakdown.
        assert 'Date:' in hover_text
        assert 'Contributions:' in hover_text
        assert 'Bills:' in hover_text
        # Note: bill IDs are stripped of 'bill_' prefix in hover text.
        assert '1' in hover_text
        assert '2' in hover_text
        # Should contain dollar amounts.
        assert '$100.00' in hover_text or '$100.0' in hover_text
        assert '$50.00' in hover_text or '$50.0' in hover_text

    def test_create_timeseries_chart_no_contributions(self):
        """Test chart with no contributions."""
        # Create sample DataFrames with no contributions.
        dates = [date.today() + timedelta(days=i) for i in range(3)]
        balance_df = pd.DataFrame({
            'total': [1000.0, 1000.0, 1000.0]
        }, index=dates)
        
        contrib_df = pd.DataFrame({
            'total': [0.0, 0.0, 0.0],
            'count': [0, 0, 0]
        }, index=dates)
        
        payouts_df = pd.DataFrame({
            'total': [0.0, 0.0, 0.0],
            'count': [0, 0, 0]
        }, index=dates)
        
        # Create chart.
        fig = create_timeseries_chart_from_dfs(
            balance_df, contrib_df, payouts_df
        )
        
        # Should have balance line and possibly empty contribution/payout traces.
        assert fig is not None
        assert len(fig.data) >= 1
        # Balance trace should exist.
        assert fig.data[0].name == 'Account Balance'

    def test_create_timeseries_chart_no_payouts(self):
        """Test chart with no payouts."""
        # Create sample DataFrames with no payouts.
        dates = [date.today() + timedelta(days=i) for i in range(3)]
        balance_df = pd.DataFrame({
            'total': [1000.0, 1100.0, 1200.0]
        }, index=dates)
        
        contrib_df = pd.DataFrame({
            'total': [100.0, 100.0, 100.0],
            'count': [1, 1, 1],
            'bill_1': [100.0, 100.0, 100.0]
        }, index=dates)
        
        payouts_df = pd.DataFrame({
            'total': [0.0, 0.0, 0.0],
            'count': [0, 0, 0]
        }, index=dates)
        
        # Create chart.
        fig = create_timeseries_chart_from_dfs(
            balance_df, contrib_df, payouts_df
        )
        
        # Should have balance and contribution traces.
        assert fig is not None
        assert len(fig.data) >= 2
        # Payout trace may or may not be added (only if payouts < 0).
