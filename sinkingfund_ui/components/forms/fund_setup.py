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

def fund_setup_form():
    """
    Render the sinking fund initialization form.
    """

    # Render the form.
    with st.form("fund_setup"):

        # Render the form fields.
        col1, col2, col3 = st.columns(3)

        # Planning start date. Defaults to today.
        with col1:
            start_date = st.date_input(
                label="Starting Contribution Date", value=date.today(),
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
        with col2:
            end_date = st.date_input(
                label="Planning End Date", 
                value=date.today() + timedelta(days=365),
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
        with col3:
            balance = st.number_input(
                label="Account Balance ($)", min_value=0.0, value=1000.0,
                format="%.2f",
                help=(
                    "The initial balance of the account. This balance is "
                    "allocated to any envelopes before the contribution "
                    "schedule is created. To skip the allocation step, "
                    "the set the account balance to 0.0."
                )
            )
        
        # Create fund button.
        create_fund = st.form_submit_button(
            label="Create Fund", type="primary"
        )
        
        # If the form is submitted, create the fund and add it to the
        # session state.
        if create_fund:
            
            # DEFNESIVE: Ensure that the end date is after the start
            # date. TODO: Add this check to the SinkingFund class.
            if end_date <= start_date:
                st.error("End date must be after start date.")
            else:

                # Initialize the fund.
                st.session_state.fund = SinkingFund(
                    start_date=start_date,
                    end_date=end_date,
                    balance=float(balance)
                )
                st.success("Fund created successfully.")
                st.rerun()

