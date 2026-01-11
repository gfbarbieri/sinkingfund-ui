"""
Unit Tests for Visualization Components
========================================

Tests for strategy flow diagram, allocation preview, and schedule preview
rendering. Verifies correct Streamlit component calls and message content
based on fund state.

Examples
--------
.. code-block:: python

   # Run all tests in this module.
   pytest tests/unit/test_visualizations.py

   # Run a specific test class.
   pytest tests/unit/test_visualizations.py::TestStrategyFlowDiagram
"""

import pytest
from datetime import date
from unittest.mock import MagicMock, patch

from sinkingfund_ui.components.figures import (
    render_strategy_flow_diagram,
    render_allocation_preview,
    render_schedule_preview
)

from sinkingfund_ui.main import render_schedule_visualization


class TestStrategyFlowDiagram:
    """Test strategy flow diagram rendering."""

    @patch('sinkingfund_ui.components.figures.st')
    def test_render_strategy_flow_diagram(self, mock_st):
        """Test that strategy flow diagram renders correctly."""
        render_strategy_flow_diagram()
        
        mock_st.markdown.assert_called_once()
        call_args = mock_st.markdown.call_args[0][0]
        assert "Workflow:" in call_args
        assert "Create Fund" in call_args
        assert "Load Bills" in call_args
        assert "Select Strategies" in call_args


class TestAllocationPreview:
    """Test allocation preview rendering."""

    @patch('sinkingfund_ui.components.figures.st')
    def test_render_allocation_preview_with_bills_and_balance(self, mock_st):
        """Test allocation preview with bills and balance."""
        mock_fund = MagicMock()
        mock_fund.get_bills.return_value = [MagicMock(), MagicMock()]
        mock_fund.balance = 1000.0
        
        render_allocation_preview(mock_fund, "sorted")
        
        mock_st.info.assert_called_once()
        call_args = mock_st.info.call_args[0][0]
        assert "sorted" in call_args
        assert "1000.00" in call_args
        assert "2" in call_args

    @patch('sinkingfund_ui.components.figures.st')
    def test_render_allocation_preview_no_bills(self, mock_st):
        """Test allocation preview with no bills."""
        mock_fund = MagicMock()
        mock_fund.get_bills.return_value = []
        mock_fund.balance = 1000.0
        
        render_allocation_preview(mock_fund, "sorted")
        
        mock_st.info.assert_not_called()

    @patch('sinkingfund_ui.components.figures.st')
    def test_render_allocation_preview_zero_balance(self, mock_st):
        """Test allocation preview with zero balance."""
        mock_fund = MagicMock()
        mock_fund.get_bills.return_value = [MagicMock()]
        mock_fund.balance = 0.0
        
        render_allocation_preview(mock_fund, "sorted")
        
        mock_st.info.assert_not_called()


class TestSchedulePreview:
    """Test schedule preview rendering."""

    @patch('sinkingfund_ui.components.figures.st')
    def test_render_schedule_preview_with_bills(self, mock_st):
        """Test schedule preview with bills."""
        mock_fund = MagicMock()
        mock_fund.get_bills.return_value = [MagicMock(), MagicMock()]
        
        render_schedule_preview(mock_fund, "independent_scheduler", 14)
        
        mock_st.info.assert_called_once()
        call_args = mock_st.info.call_args[0][0]
        assert "independent_scheduler" in call_args
        assert "14" in call_args
        assert "2" in call_args

    @patch('sinkingfund_ui.components.figures.st')
    def test_render_schedule_preview_no_bills(self, mock_st):
        """Test schedule preview with no bills."""
        mock_fund = MagicMock()
        mock_fund.get_bills.return_value = []
        
        render_schedule_preview(mock_fund, "independent_scheduler", 14)
        
        mock_st.info.assert_not_called()


class TestScheduleVisualization:
    """Test schedule visualization rendering."""

    @patch('sinkingfund_ui.main.st')
    @patch('sinkingfund_ui.main.create_timeseries_chart_from_dfs')
    @patch('sinkingfund_ui.main.convert_report_section_to_dataframe')
    def test_render_schedule_visualization_with_report(
        self, mock_convert, mock_create_chart, mock_st
    ):
        """Test schedule visualization with report exists."""
        # Setup mocks.
        test_date = date(2025, 1, 1)
        mock_st.session_state.report = {
            test_date: {
                'account_balance': {'total': 1000.0, 'count': 1, 'bills': {}},
                'contributions': {'total': 100.0, 'count': 1, 'bills': {'bill_1': 100.0}},
                'payouts': {'total': 0.0, 'count': 0, 'bills': {}}
            }
        }
        
        mock_balance_df = MagicMock()
        mock_contrib_df = MagicMock()
        mock_payout_df = MagicMock()
        mock_convert.side_effect = [mock_balance_df, mock_contrib_df, mock_payout_df]
        
        mock_fig = MagicMock()
        mock_create_chart.return_value = mock_fig
        
        # Call function.
        render_schedule_visualization()
        
        # Verify convert_report_section_to_dataframe called 3 times.
        assert mock_convert.call_count == 3
        assert mock_convert.call_args_list[0][0][1] == 'account_balance'
        assert mock_convert.call_args_list[1][0][1] == 'contributions'
        assert mock_convert.call_args_list[2][0][1] == 'payouts'
        
        # Verify chart creation.
        mock_create_chart.assert_called_once_with(
            mock_balance_df, mock_contrib_df, mock_payout_df
        )
        
        # Verify chart display.
        mock_st.plotly_chart.assert_called_once_with(
            mock_fig, use_container_width=True
        )

    @patch('sinkingfund_ui.main.st')
    def test_render_schedule_visualization_no_report(self, mock_st):
        """Test schedule visualization with no report."""
        # Setup mocks.
        mock_st.session_state.report = None
        
        # Call function.
        render_schedule_visualization()
        
        # Verify info message displayed.
        mock_st.info.assert_called_once()
        call_args = mock_st.info.call_args[0][0]
        assert "Generate a schedule" in call_args

    @patch('sinkingfund_ui.main.st')
    def test_render_schedule_visualization_empty_report(self, mock_st):
        """Test schedule visualization with empty report."""
        # Setup mocks.
        mock_st.session_state.report = {}
        
        # Call function.
        render_schedule_visualization()
        
        # Verify info message displayed.
        mock_st.info.assert_called_once()
        call_args = mock_st.info.call_args[0][0]
        assert "Generate a schedule" in call_args

    @patch('sinkingfund_ui.main.st')
    @patch('sinkingfund_ui.main.create_timeseries_chart_from_dfs')
    @patch('sinkingfund_ui.main.convert_report_section_to_dataframe')
    def test_render_schedule_visualization_error_handling(
        self, mock_convert, mock_create_chart, mock_st
    ):
        """Test schedule visualization error handling."""
        # Setup mocks.
        test_date = date(2025, 1, 1)
        mock_st.session_state.report = {
            test_date: {
                'account_balance': {'total': 1000.0, 'count': 1, 'bills': {}},
                'contributions': {'total': 100.0, 'count': 1, 'bills': {}},
                'payouts': {'total': 0.0, 'count': 0, 'bills': {}}
            }
        }
        
        # Simulate error in conversion.
        mock_convert.side_effect = ValueError("Conversion error")
        
        # Call function.
        render_schedule_visualization()
        
        # Verify error displayed.
        mock_st.error.assert_called_once()
        call_args = mock_st.error.call_args[0][0]
        assert "Error displaying schedule visualization" in call_args
        
        # Verify traceback displayed.
        mock_st.code.assert_called_once()

