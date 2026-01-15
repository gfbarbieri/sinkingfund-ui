"""
Bills Table Components
======================

Components for displaying and managing bills in tabular format. Provides
unified bills table with native sorting, filtering, and edit/delete
functionality, plus bill summary tables for envelope status.

Features
--------
- Interactive bills table with row selection
- Edit and delete bill functionality
- Bill summary table showing allocation status
- Session state management for selection persistence

Examples
--------
.. code-block:: python

   import streamlit as st
   from sinkingfund_ui.components.tables import (
       unified_bills_table, create_bill_summary_table
   )
   from sinkingfund import SinkingFund
   from datetime import date, timedelta

   # Create fund and add bills.
   fund = SinkingFund(
       start_date=date.today(),
       end_date=date.today() + timedelta(days=365),
       balance=1000.0
   )
   fund.add_bills(source=[...], contribution_interval=14)

   # Display unified bills table.
   unified_bills_table(fund=fund)

   # Display bill summary after envelopes are created.
   if fund.get_envelopes():
       df_summary = create_bill_summary_table(fund=fund)
       st.dataframe(df_summary)
"""

########################################################################
## IMPORTS
########################################################################

import pandas as pd
import streamlit as st

from sinkingfund_ui.components.forms.bill_management import edit_bill_form

########################################################################
## FUND INFO TABLE
########################################################################

def fund_info_table(fund):
    """
    Render a compact, tabular summary of fund information.

    Parameters
    ----------
    fund : SinkingFund
        The fund instance to display information for.
    """

    data = [{
        "Start Date": fund.start_date,
        "Planning End Date": fund.end_date,
        "Balance": f"${fund.balance:.2f}"
    }]

    df = pd.DataFrame(data)
    st.table(df)

########################################################################
## UNIFIED BILLS TABLE FUNCTION
########################################################################

def unified_bills_table(fund):
    """
    Render a unified bills table with native sorting, filtering, and
    edit/delete functionality via row selection.

    Parameters
    ----------
    fund : SinkingFund
        The fund instance containing bills to display.

    Notes
    -----
    This function renders an interactive Streamlit dataframe with
    single-row selection. When a row is selected, edit and delete
    buttons appear. Selection state is persisted in st.session_state.
    """

    # Get the bills from the fund's bill manager.
    bills = fund.get_bills()
    
    # If there are no bills, display an info message and exit.
    if not bills:
        st.info("No bills added yet. Use the sidebar to add bills.")
        return
    
    # Create DataFrame from bills with columns: ID, Service, Amount,
    # Recurring, Frequency, Due Date.
    bills_data = []
    for bill in bills:
        bills_data.append({
            "ID": bill.bill_id,
            "Service": bill.service,
            "Amount": f"${bill.amount_due:.2f}",
            "Recurring": "Yes" if bill.recurring else "No",
            "Frequency": getattr(bill, 'frequency', 'N/A'),
            "Due Date": str(bill.end_date) if bill.end_date else "N/A"
        })
    
    df = pd.DataFrame(bills_data)
    
    # Create mapping from bill_id to bill object for quick lookup.
    bill_map = {bill.bill_id: bill for bill in bills}
    
    # Display interactive dataframe with single-row selection enabled.
    # This provides native sorting and filtering capabilities.
    selected_rows = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="bills_table"
    )
    
    # Get selected bill ID if a row is selected.
    # Streamlit stores selection state via the dataframe key.
    selected_bill_id = None
    
    # Check selection from the dataframe return value.
    if selected_rows and 'selection' in selected_rows:
        selected_indices = selected_rows['selection'].get('rows', [])
        if selected_indices:
            selected_idx = selected_indices[0]
            if selected_idx < len(df):
                selected_bill_id = df.iloc[selected_idx]['ID']
                # Store in session state for persistence across reruns.
                st.session_state['selected_bill_id'] = selected_bill_id
            else:
                # Invalid index, clear selection.
                if 'selected_bill_id' in st.session_state:
                    del st.session_state['selected_bill_id']
        else:
            # No rows selected - user deselected. Clear session state.
            if 'selected_bill_id' in st.session_state:
                del st.session_state['selected_bill_id']
    else:
        # No selection data in return value - user deselected.
        # Clear session state.
        if 'selected_bill_id' in st.session_state:
            del st.session_state['selected_bill_id']
    
    # Fall back to session state only if we don't have a current
    # selection and the session state exists (handles edge cases
    # where selection might not be in return value but user hasn't
    # explicitly deselected).
    if selected_bill_id is None and 'selected_bill_id' in st.session_state:
        candidate_id = st.session_state['selected_bill_id']
        # Verify the bill still exists (might have been deleted).
        if candidate_id in bill_map:
            selected_bill_id = candidate_id
        else:
            # Clear invalid selection (bill was deleted).
            del st.session_state['selected_bill_id']
    
    # Display action buttons only when a row is selected.
    if selected_bill_id and selected_bill_id in bill_map:
        selected_bill = bill_map[selected_bill_id]
        
        # Action buttons section.
        st.markdown("**Actions**")
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            # Edit button.
            if st.button("✏️ Edit", key="edit_selected_bill", use_container_width=True):
                st.session_state[f"editing_{selected_bill_id}"] = True
                st.rerun()
        
        with col2:
            # Delete button.
            if st.button("🗑️ Delete", key="delete_selected_bill", use_container_width=True):
                fund.delete_bills([selected_bill_id])
                # Clear selection and edit state.
                if 'selected_bill_id' in st.session_state:
                    del st.session_state['selected_bill_id']
                if f"editing_{selected_bill_id}" in st.session_state:
                    del st.session_state[f"editing_{selected_bill_id}"]
                st.rerun()
        
        # Show edit form if editing.
        if st.session_state.get(f"editing_{selected_bill_id}", False):
            with st.expander("✏️ Edit Bill", expanded=True):
                # Render the edit form.
                success = edit_bill_form(fund, selected_bill)
                # If form was successfully submitted, clear edit state
                # and selection.
                if success:
                    if f"editing_{selected_bill_id}" in st.session_state:
                        del st.session_state[f"editing_{selected_bill_id}"]
                    if 'selected_bill_id' in st.session_state:
                        del st.session_state['selected_bill_id']
    else:
        # Show instruction when no row is selected.
        None
        # st.info("👆 Select a row above to edit or delete a bill.")

def create_bill_summary_table(fund):
    """
    Create a summary table showing bill details and allocation information.
    This table displays allocation/envelope-driven fields and is used in the
    envelopes section.
    
    Parameters
    ----------
    fund : SinkingFund
        The sinking fund instance with envelopes and allocation
        
    Returns
    -------
    pd.DataFrame
        DataFrame with columns: Bill ID, Service, Start Contribution Date, 
        Due Date, Allocation, Remaining, Fully Funded
    """

    # Get envelopes from the fund.
    envelopes = fund.get_envelopes()
    
    # If there are no envelopes, then return an empty DataFrame.
    # Otherwise, build the data frame.
    if not envelopes:
        return pd.DataFrame(columns=[
            'Bill ID', 'Service', 'Start Contribution Date', 
            'Due Date', 'Allocation', 'Remaining', 'Fully Funded'
        ])
    
    # Initialize the bill data list.
    bill_data = []
    
    # For each envelope, extract the bill instance information and
    # allocation information.
    for envelope in envelopes:

        # Extract bill instance information.
        start_contrib_date = envelope.start_contrib_date
        allocation = envelope.initial_allocation
        bill_id = envelope.bill_instance.bill_id
        service = envelope.bill_instance.service
        due_date = envelope.bill_instance.due_date
        
        # Determine if the envelope is fully funded by the end of the
        # planning period.
        fully_funded = envelope.is_fully_funded(as_of_date=fund.end_date)

        # Determine how much is remaining as of the end of the planning
        # period.
        remaining = envelope.remaining(as_of_date=fund.end_date)
        
        bill_data.append({
            'Bill ID': bill_id,
            'Service': service,
            'Start Contribution Date': start_contrib_date,
            'Due Date': due_date,
            'Allocation': f"${allocation:.2f}",
            'Remaining': f"${remaining:.2f}",
            'Fully Funded': "Yes" if fully_funded else "No"
        })
    
    df = pd.DataFrame(bill_data)
    
    return df