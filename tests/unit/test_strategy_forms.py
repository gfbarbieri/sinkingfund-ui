"""
Unit Tests for Strategy Selection Forms
========================================

Tests for allocation strategy and scheduler strategy form components.
Verifies form rendering, session state management, and strategy constant
definitions.

Examples
--------
.. code-block:: python

   # Run all tests in this module.
   pytest tests/unit/test_strategy_forms.py

   # Run a specific test class.
   pytest tests/unit/test_strategy_forms.py::TestAllocationStrategyForm
"""

import pytest
from unittest.mock import MagicMock, patch

from sinkingfund_ui.components.forms.strategy import (
    allocation_strategy_form,
    scheduler_strategy_form,
    ALLOCATION_STRATEGIES,
    SCHEDULER_STRATEGIES
)


class TestAllocationStrategyForm:
    """Test allocation strategy form component."""

    @patch('sinkingfund_ui.components.forms.strategy.st')
    def test_allocation_strategy_form_default(self, mock_st):
        """Test allocation strategy form with default selection."""
        mock_st.session_state = {}
        mock_st.selectbox.return_value = "sorted"
        
        result = allocation_strategy_form()
        
        assert result == "sorted"
        mock_st.selectbox.assert_called_once()
        call_args = mock_st.selectbox.call_args
        assert call_args[1]['label'] == "Allocation Strategy"
        assert call_args[1]['options'] == ALLOCATION_STRATEGIES

    @patch('sinkingfund_ui.components.forms.strategy.st')
    def test_allocation_strategy_form_with_session_state(self, mock_st):
        """Test allocation strategy form with existing session state."""
        mock_st.session_state = {'allocation_strategy': 'proportional'}
        mock_st.selectbox.return_value = "proportional"
        
        result = allocation_strategy_form()
        
        assert result == "proportional"
        mock_st.selectbox.assert_called_once()
        call_args = mock_st.selectbox.call_args
        # With key parameter, Streamlit handles session state
        # automatically. We always pass index=0 as default.
        assert call_args[1]['index'] == 0
        assert call_args[1]['key'] == 'allocation_strategy'

    @patch('sinkingfund_ui.components.forms.strategy.st')
    def test_allocation_strategy_form_invalid_session_state(self, mock_st):
        """Test allocation strategy form with invalid session state value."""
        mock_st.session_state = {'allocation_strategy': 'invalid'}
        mock_st.selectbox.return_value = "sorted"
        
        result = allocation_strategy_form()
        
        assert result == "sorted"
        mock_st.selectbox.assert_called_once()
        call_args = mock_st.selectbox.call_args
        assert call_args[1]['index'] == 0  # Falls back to default index


class TestSchedulerStrategyForm:
    """Test scheduler strategy form component."""

    @patch('sinkingfund_ui.components.forms.strategy.st')
    def test_scheduler_strategy_form_default(self, mock_st):
        """Test scheduler strategy form with default selection."""
        mock_st.session_state = {}
        mock_st.selectbox.return_value = "independent_scheduler"
        
        result = scheduler_strategy_form()
        
        assert result == "independent_scheduler"
        mock_st.selectbox.assert_called_once()
        call_args = mock_st.selectbox.call_args
        assert call_args[1]['label'] == "Scheduler Strategy"
        assert call_args[1]['options'] == SCHEDULER_STRATEGIES

    @patch('sinkingfund_ui.components.forms.strategy.st')
    def test_scheduler_strategy_form_with_session_state(self, mock_st):
        """Test scheduler strategy form with existing session state."""
        mock_st.session_state = {'scheduler_strategy': 'independent_scheduler'}
        mock_st.selectbox.return_value = "independent_scheduler"
        
        result = scheduler_strategy_form()
        
        assert result == "independent_scheduler"
        mock_st.selectbox.assert_called_once()
        call_args = mock_st.selectbox.call_args
        assert call_args[1]['index'] == 0


class TestStrategyConstants:
    """Test strategy constant definitions."""

    def test_allocation_strategies_defined(self):
        """Test that allocation strategies are properly defined."""
        assert isinstance(ALLOCATION_STRATEGIES, list)
        assert len(ALLOCATION_STRATEGIES) > 0
        assert "sorted" in ALLOCATION_STRATEGIES
        assert "proportional" in ALLOCATION_STRATEGIES

    def test_scheduler_strategies_defined(self):
        """Test that scheduler strategies are properly defined."""
        assert isinstance(SCHEDULER_STRATEGIES, list)
        assert len(SCHEDULER_STRATEGIES) > 0
        assert "independent_scheduler" in SCHEDULER_STRATEGIES

