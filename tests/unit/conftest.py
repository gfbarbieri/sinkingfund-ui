"""Unit test fixtures for sinkingfund-ui."""

from unittest.mock import MagicMock
import pytest


@pytest.fixture
def mock_streamlit():
    """
    Create a mock Streamlit module with commonly used functions.
    
    Returns
    -------
    MagicMock
        Mock streamlit module with st.session_state, st.write, st.error, etc.
    """
    mock_st = MagicMock()
    
    # Mock session_state as a dictionary
    mock_st.session_state = {}
    
    # Mock common streamlit functions
    mock_st.write = MagicMock()
    mock_st.error = MagicMock()
    mock_st.success = MagicMock()
    mock_st.info = MagicMock()
    mock_st.warning = MagicMock()
    mock_st.dataframe = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.header = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.form_submit_button = MagicMock(return_value=False)
    mock_st.file_uploader = MagicMock(return_value=None)
    mock_st.number_input = MagicMock(return_value=14)
    mock_st.checkbox = MagicMock(return_value=False)
    mock_st.text_input = MagicMock(return_value="")
    mock_st.date_input = MagicMock(return_value=None)
    mock_st.selectbox = MagicMock(return_value="monthly")
    mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock()))
    mock_st.form = MagicMock()
    mock_st.rerun = MagicMock()
    mock_st.code = MagicMock()
    
    # Mock form context manager
    mock_st.form.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
    
    # Mock columns context manager
    mock_col = MagicMock()
    mock_st.columns.return_value = (mock_col, mock_col)
    mock_col.__enter__ = MagicMock(return_value=mock_col)
    mock_col.__exit__ = MagicMock(return_value=False)
    
    return mock_st


@pytest.fixture
def mock_session_state():
    """
    Create a mock session state dictionary.
    
    Returns
    -------
    dict
        Mock session state with common keys.
    """
    return {
        'fund': None,
        'bills_data': [],
        'report': None
    }


@pytest.fixture
def mock_uploaded_file():
    """
    Create a mock Streamlit UploadedFile object.
    
    Returns
    -------
    MagicMock
        Mock uploaded file with name, getbuffer, and type methods.
    """
    mock_file = MagicMock()
    mock_file.name = "test_bills.csv"
    mock_file.getbuffer.return_value = b"test,data,here"
    mock_file.type = "text/csv"
    return mock_file

