"""Integration test fixtures for sinkingfund-ui.

Provides fixtures and helper functions for integration tests that
require actual SinkingFund instances and bill data.
"""

########################################################################
## IMPORTS
########################################################################

from datetime import date, timedelta

import pytest
from sinkingfund import SinkingFund


########################################################################
## DATE FIXTURES
########################################################################

@pytest.fixture
def test_start_date():
    """
    Return a test start date (today).

    Returns
    -------
    datetime.date
        Today's date.
    """
    return date.today()


@pytest.fixture
def test_end_date(test_start_date):
    """
    Return a test end date (one year from start).

    Parameters
    ----------
    test_start_date : datetime.date
        Start date fixture.

    Returns
    -------
    datetime.date
        Date one year from start date.
    """
    return test_start_date + timedelta(days=365)


########################################################################
## FUND FIXTURES
########################################################################

@pytest.fixture
def sample_fund(test_start_date, test_end_date):
    """
    Create a test SinkingFund instance with default dates and zero balance.
    
    Parameters
    ----------
    test_start_date : datetime.date
        Start date for the fund.
    test_end_date : datetime.date
        End date for the fund.
        
    Returns
    -------
    SinkingFund
        A new SinkingFund instance for testing.
    """
    return SinkingFund(
        start_date=test_start_date,
        end_date=test_end_date,
        balance=0.0
    )


@pytest.fixture
def sample_fund_with_balance(test_start_date, test_end_date):
    """
    Create a test SinkingFund instance with default dates and $1000 balance.
    
    Parameters
    ----------
    test_start_date : datetime.date
        Start date for the fund.
    test_end_date : datetime.date
        End date for the fund.
        
    Returns
    -------
    SinkingFund
        A new SinkingFund instance with initial balance.
    """
    return SinkingFund(
        start_date=test_start_date,
        end_date=test_end_date,
        balance=1000.0
    )


########################################################################
## BILL DATA FIXTURES
########################################################################

@pytest.fixture
def sample_non_recurring_bill_data():
    """
    Return sample bill data for a non-recurring bill.
    
    Returns
    -------
    dict
        Bill data dictionary with required fields.
    """
    return {
        "bill_id": "test_bill_1",
        "service": "Test Service",
        "amount_due": 100.0,
        "recurring": False,
        "due_date": date.today() + timedelta(days=30)
    }


@pytest.fixture
def sample_recurring_bill_data():
    """
    Return sample bill data for a recurring monthly bill.
    
    Returns
    -------
    dict
        Bill data dictionary for recurring bill.
    """
    return {
        "bill_id": "test_recurring_1",
        "service": "Monthly Service",
        "amount_due": 50.0,
        "recurring": True,
        "start_date": date.today(),
        "frequency": "monthly",
        "interval": 1
    }


@pytest.fixture
def sample_multiple_bills_data():
    """
    Return a list of multiple sample bills (recurring and non-recurring).
    
    Returns
    -------
    list[dict]
        List of bill data dictionaries.
    """
    return [
        {
            "bill_id": "bill_1",
            "service": "Service One",
            "amount_due": 100.0,
            "recurring": False,
            "due_date": date.today() + timedelta(days=30)
        },
        {
            "bill_id": "bill_2",
            "service": "Service Two",
            "amount_due": 75.0,
            "recurring": True,
            "start_date": date.today(),
            "frequency": "monthly",
            "interval": 1
        },
        {
            "bill_id": "bill_3",
            "service": "Service Three",
            "amount_due": 200.0,
            "recurring": True,
            "start_date": date.today(),
            "frequency": "quarterly",
            "interval": 1
        }
    ]


########################################################################
## HELPER FUNCTIONS
########################################################################

def create_bill_with_frequency(frequency: str):
    """
    Create a bill with a specific frequency.

    Parameters
    ----------
    frequency : str
        Frequency type: monthly, quarterly, annual, weekly, daily.

    Returns
    -------
    dict
        Bill data dictionary with specified frequency.
    """
    return {
        "bill_id": f"test_{frequency}_bill",
        "service": f"{frequency.title()} Service",
        "amount_due": 50.0,
        "recurring": True,
        "start_date": date.today(),
        "frequency": frequency,
        "interval": 1
    }

