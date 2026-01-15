"""
Fund Setup Form
===============

Form for initializing a sinking fund with planning period and initial
balance configuration. This is the first step in the application workflow.

Features
--------
- Planning start date configuration (defaults to today)
- Planning end date configuration (defaults to one year from start)
- Initial account balance input
- Validation to ensure end date is after start date

Examples
--------
.. code-block:: python

   import streamlit as st
   from sinkingfund_ui.components.forms.fund_setup import fund_setup_form

   # Render the fund setup form.
   fund_setup_form()

   # After form submission, the fund is stored in
   # st.session_state.fund.
"""

########################################################################
## IMPORTS
########################################################################

import streamlit as st

from datetime import date, timedelta
from sinkingfund import SinkingFund

########################################################################
## FUND SETUP FORM
########################################################################

def _serialize_bills(fund):
    """
    Convert existing bills into data dictionaries for re-adding to a fund.

    Parameters
    ----------
    fund : SinkingFund
        The fund instance containing bills to serialize.

    Returns
    -------
    list[dict]
        List of bill data dictionaries suitable for passing to
        SinkingFund.add_bills().
    """

    bills = fund.get_bills()
    bill_data_list = []

    for bill in bills:
        bill_data = {
            "bill_id": bill.bill_id,
            "service": bill.service,
            "amount_due": float(bill.amount_due),
            "recurring": bill.recurring
        }

        if bill.recurring:
            bill_data.update({
                "due_date": None,
                "start_date": getattr(bill, "start_date", None),
                "frequency": getattr(bill, "frequency", None),
                "interval": getattr(bill, "interval", None),
                "occurrences": getattr(bill, "occurrences", None),
                "end_date": getattr(bill, "end_date", None)
            })
        else:
            bill_data.update({
                "due_date": getattr(bill, "end_date", None),
                "start_date": None,
                "frequency": None,
                "interval": None,
                "occurrences": None,
                "end_date": None
            })

        bill_data_list.append(bill_data)

    return bill_data_list

def _clear_fund_dependent_state():
    """
    Clear state derived from allocations, schedules, and selections.

    Notes
    -----
    This function modifies st.session_state directly, clearing report,
    allocation_strategy, scheduler_strategy, proportional_method,
    bills_data, selected_bill_id, and any editing_* keys.
    """

    st.session_state.report = None
    st.session_state.allocation_strategy = None
    st.session_state.scheduler_strategy = None
    st.session_state.proportional_method = None

    if "bills_data" in st.session_state:
        st.session_state.bills_data = []

    if "selected_bill_id" in st.session_state:
        del st.session_state["selected_bill_id"]

    keys_to_clear = [
        key for key in st.session_state.keys() if key.startswith("editing_")
    ]
    for key in keys_to_clear:
        del st.session_state[key]

def rebuild_fund_with_bills(
    existing_fund, start_date, end_date, balance, contribution_interval=14
):
    """
    Rebuild a fund while preserving existing bills.

    Parameters
    ----------
    existing_fund : SinkingFund or None
        The current fund to preserve bills from. If None, creates a new
        fund with no bills.
    start_date : date
        The start date for the new fund.
    end_date : date
        The planning end date for the new fund.
    balance : float
        The initial account balance.
    contribution_interval : int, optional
        Days between contributions when re-adding bills. Defaults to 14.

    Returns
    -------
    SinkingFund
        A new fund instance with preserved bills but no allocations or
        schedules.
    """

    preserved_bills = (
        _serialize_bills(existing_fund)
        if existing_fund else []
    )

    new_fund = SinkingFund(
        start_date=start_date,
        end_date=end_date,
        balance=float(balance)
    )

    if preserved_bills:
        new_fund.add_bills(
            source=preserved_bills,
            contribution_interval=contribution_interval
        )

    return new_fund

def fund_setup_form():
    """
    Render the sinking fund initialization form.

    Notes
    -----
    This function renders a Streamlit form for creating or updating a
    fund. On submission, it stores the fund in st.session_state.fund
    and clears dependent state (allocations, schedules, report).
    """

    existing_fund = st.session_state.fund if "fund" in st.session_state else None

    default_start_date = (
        existing_fund.start_date if existing_fund else date.today()
    )
    default_end_date = (
        existing_fund.end_date if existing_fund else date.today() + timedelta(days=365)
    )
    default_balance = (
        float(existing_fund.balance) if existing_fund else 1000.0
    )

    # Render the form.
    with st.form("fund_management"):

        # Planning start date. Defaults to today.
        start_date = st.date_input(
            label="Starting Contribution Date", value=default_start_date,
            help=(
                "The date you want to make the first contribution to "
                "the fund. Think: 'When do you want to start saving?'"
                " Maybe this is when your paycheck hits your bank account?"
            )
        )
        
        # Planning end date. Defaults to one year from the start date.
        # The end date is not the last contribution date, it is just the
        # window of the planning period. It will be used only to
        # set an end date for any reporting periods. Another option
        # would be to use a horizon in months or days, then calculate
        # the end date from the starting date and the horizon.
        end_date = st.date_input(
            label="Planning End Date", 
            value=default_end_date,
            help=(
                "The date you want to end the planning window for "
                "reporting purposes. The end date is not the last "
                "contribution date, it is just the window of the "
                "planning period."
            )
        )
        
        # Initial account balance. The account balance is allocated to
        # any envelopes before the contribution schedule is created. If
        # the user doesn't want to allocate any existing balance, then
        # this needs to be set to 0.0, as there is no way to both have
        # an account balance and skip the allocation step.
        balance = st.number_input(
            label="Account Balance ($)", min_value=0.0, value=default_balance,
            format="%.2f",
            help=(
                "The initial balance of the account. This balance is "
                "allocated to any envelopes before the contribution "
                "schedule is created. To skip the allocation step, "
                "the set the account balance to 0.0."
            )
        )
        
        action_label = "Update Fund" if existing_fund else "Create Fund"
        create_or_update_fund = st.form_submit_button(
            label=action_label, type="primary"
        )
        
        # If the form is submitted, create the fund and add it to the
        # session state.
        if create_or_update_fund:
            
            # DEFENSIVE: Ensure that the end date is after the start
            # date. TODO: Add this check to the SinkingFund class.
            if end_date <= start_date:
                st.error("End date must be after start date.")
            else:

                # Preserve bills for updates, but clear allocations
                # and schedules by recreating the fund.
                new_fund = rebuild_fund_with_bills(
                    existing_fund=existing_fund,
                    start_date=start_date,
                    end_date=end_date,
                    balance=balance,
                    contribution_interval=14
                )

                st.session_state.fund = new_fund
                _clear_fund_dependent_state()

                if existing_fund:
                    st.success(
                        "Fund updated. Allocations and schedules reset."
                    )
                else:
                    st.success("Fund created successfully.")
                st.rerun()

