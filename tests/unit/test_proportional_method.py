"""
Unit Tests for Proportional Method Selection
=============================================

Tests for proportional method form component. Verifies form rendering,
session state management, and proportional method constant definitions.

Examples
--------
.. code-block:: python

   # Run all tests in this module.
   pytest tests/unit/test_proportional_method.py

   # Run a specific test class.
   pytest tests/unit/test_proportional_method.py::TestProportionalMethodForm
"""

import pytest
from unittest.mock import MagicMock, patch

from sinkingfund_ui.components.forms.strategy import (
    proportional_method_form,
    PROPORTIONAL_METHODS
)


class TestProportionalMethodForm:
    """Test proportional method form component."""

    @patch('sinkingfund_ui.components.forms.strategy.st')
    def test_proportional_method_form_default(self, mock_st):
        """Test proportional method form with default selection."""
        mock_st.session_state = {}
        mock_st.selectbox.return_value = "proportional"
        
        result = proportional_method_form()
        
        assert result == "proportional"
        mock_st.selectbox.assert_called_once()
        call_args = mock_st.selectbox.call_args
        assert call_args[1]['label'] == "Proportional Method"
        assert call_args[1]['options'] == PROPORTIONAL_METHODS

    @patch('sinkingfund_ui.components.forms.strategy.st')
    def test_proportional_method_form_with_session_state(self, mock_st):
        """Test proportional method form with existing session state."""
        mock_st.session_state = {'proportional_method': 'urgency'}
        mock_st.selectbox.return_value = "urgency"
        
        result = proportional_method_form()
        
        assert result == "urgency"
        mock_st.selectbox.assert_called_once()
        call_args = mock_st.selectbox.call_args
        # With key parameter, Streamlit handles session state
        # automatically. We always pass index=0 as default.
        assert call_args[1]['index'] == 0
        assert call_args[1]['key'] == 'proportional_method'

    @patch('sinkingfund_ui.components.forms.strategy.st')
    def test_proportional_method_form_invalid_session_state(self, mock_st):
        """Test proportional method form with invalid session state value."""
        mock_st.session_state = {'proportional_method': 'invalid'}
        mock_st.selectbox.return_value = "proportional"
        
        result = proportional_method_form()
        
        assert result == "proportional"
        mock_st.selectbox.assert_called_once()
        call_args = mock_st.selectbox.call_args
        assert call_args[1]['index'] == 0  # Falls back to default index


class TestProportionalMethodConstants:
    """Test proportional method constant definitions."""

    def test_proportional_methods_defined(self):
        """Test that proportional methods are properly defined."""
        assert isinstance(PROPORTIONAL_METHODS, list)
        assert len(PROPORTIONAL_METHODS) > 0
        assert "proportional" in PROPORTIONAL_METHODS
        assert "urgency" in PROPORTIONAL_METHODS
        assert "equal" in PROPORTIONAL_METHODS
        assert "zero" in PROPORTIONAL_METHODS

