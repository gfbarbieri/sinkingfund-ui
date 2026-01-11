"""
Bill Management Forms
=====================

Forms for uploading bills from files (CSV, Excel, JSON) and manually
creating bills. Supports both one-time and recurring bills with various
frequency options.

Features
--------
- File upload for bulk bill creation (CSV, Excel, JSON)
- Manual bill entry form with validation
- Edit existing bills with pre-populated values
- Support for recurring bills with frequency, interval, and end date
- Session state management for form reactivity

Examples
--------
.. code-block:: python

   import streamlit as st
   from sinkingfund_ui.components.forms.bill_management import (
       upload_bills_from_file, manual_bill_form
   )
   from sinkingfund import SinkingFund
   from datetime import date

   # Initialize fund.
   fund = SinkingFund(
       start_date=date.today(),
       end_date=date.today() + timedelta(days=365),
       balance=1000.0
   )
   st.session_state.fund = fund

   # Upload bills from file.
   upload_bills_from_file()

   # Or manually add a bill.
   manual_bill_form(fund=fund)
"""

########################################################################
## IMPORTS
########################################################################

import streamlit as st
import os
import tempfile

########################################################################
## BILL MANAGEMENT FORMS
########################################################################

def upload_bills_from_file():
    """
    Render the file uploader for bills.
    """

    # Render the file uploader.
    uploaded_file = st.file_uploader(
        "Choose a CSV, Excel, or JSON file.",
        type=['csv', 'xlsx', 'xls', 'json']
    )
    
    # If the user selects a file to upload, then Streamlit stores it as
    # an UploadedFile object. From there, we can choose to render a load
    # button, which we will use to set off the create bill process.
    if uploaded_file is not None:

        # If the load button is clicked, then read the temporary file
        # and attempt to create bills from the loaded data.
        if st.button("Create Bills from File"):

            # Try to load the bills.
            try:

                # Create temporary file.
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}"
                ) as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    temp_path = tmp_file.name
                
                # Load bills using SinkingFund API. This will load the
                # bills from the path, create the bill objects, and then
                # add them to the fund's bill manager.
                st.session_state.fund.add_bills(source=temp_path, contribution_interval=14)
                
                # Clean up temp file.
                os.unlink(temp_path)
                
                st.success("Bills created successfully.")
                st.rerun()
                
            except Exception as e:
                st.error(
                    f"Error loading and creating bills from file: {str(e)}"
                )

def manual_bill_form(fund):
    """
    Render the manual bill entry form.
    """

    # Render the recurring checkbox outside the form for reactivity.
    recurring = st.checkbox(label="Recurring Bill", key="recurring_checkbox")

    # The number of occurrences of the recurring bill. This is optional.
    use_occurrences = st.checkbox(
        label="Limit number of occurrences", key="use_occurrences"
    )

    # The end date of the recurring bill. This is optional.
    use_end_date = st.checkbox(
        label="Set end date", key="use_end_date"
    )

    # Render the form for manual bill entry.
    with st.form(key="add_bill_form"):

        # Render the bill ID input.
        bill_id = st.text_input(label="Bill ID")

        # Render the service name input.
        service = st.text_input(label="Service Name")

        # Render the amount due input.
        amount_due = st.number_input(
            label="Amount Due ($)", min_value=0.01, format="%.2f"
        )
        
        # Render the due date input for non-recurring bills.
        if not recurring:
            due_date = st.date_input(label="Due Date")
            start_date = None
            frequency = None
            interval = None
            occurrences = None
            end_date = None
        
        # If the bill is recurring, then render the start date,
        # frequency, interval, occurrences, and end date inputs.
        else:

            # Due date is not used for recurring bills.
            due_date = None

            # Render the start date input.
            start_date = st.date_input(label="Start Date")

            # Render the frequency selectbox.
            frequency = st.selectbox(
                label="Frequency", 
                options=["monthly", "quarterly", "annual", "weekly", "daily"]
            )

            # Render the interval input.
            interval = st.number_input(label="Interval", min_value=1, value=1)
            
            # Render the occurrences radio button. This is optional.
            if use_occurrences:
                occurrences = st.number_input(
                    label="Number of Occurrences", min_value=1
                )
            else:
                occurrences = None
            
            # Render the end date input. This is optional as well.
            # TODO: If the user offers a number of occurrences, then
            # the end date should be calculated from the start date and
            # the number of occurrences.
            if use_end_date:
                end_date = st.date_input(label="End Date")
            else:
                end_date = None
        
        # Render the submit button.
        submitted = st.form_submit_button(label="Add Bill")
        
        # If the form is submitted, then create the bill and add it to
        # the bill manager.
        if submitted:

            try:
                
                # Create bill data dictionary.
                bill_data = {
                    "bill_id": bill_id,
                    "service": service,
                    "amount_due": float(amount_due),
                    "recurring": recurring,
                    "due_date": due_date,
                    "start_date": start_date,
                    "frequency": frequency,
                    "interval": interval,
                    "occurrences": occurrences,
                    "end_date": end_date
                }
                    
                # Add bill using SinkingFund API.
                fund.add_bills(source=[bill_data], contribution_interval=14)
                st.success(f"Added bill: {service}")
                st.rerun()
                    
            except Exception as e:
                st.error(f"Error creating bill: {str(e)}")

def edit_bill_form(fund, bill):
    """
    Render the edit bill form with pre-populated values.
    
    Parameters
    ----------
    fund : SinkingFund
        The sinking fund instance
    bill : Bill
        The bill object to edit
        
    Returns
    -------
    bool
        True if the form was submitted and update was successful, False otherwise
    """
    
    # Get existing bill values. Note: For non-recurring bills, end_date
    # is used to store the due date. For recurring bills, end_date is
    # the end date of the recurrence.
    bill_id = bill.bill_id
    existing_recurring = bill.recurring
    existing_service = bill.service
    existing_amount = bill.amount_due
    existing_end_date = getattr(bill, 'end_date', None)
    existing_start_date = getattr(bill, 'start_date', None)
    existing_frequency = getattr(bill, 'frequency', None)
    existing_interval = getattr(bill, 'interval', 1)
    existing_occurrences = getattr(bill, 'occurrences', None)
    
    # Create unique keys based on bill_id to avoid conflicts.
    key_prefix = f"edit_{bill_id}"
    
    # Render the recurring checkbox outside the form for reactivity.
    recurring = st.checkbox(
        label="Recurring Bill", 
        value=existing_recurring,
        key=f"{key_prefix}_recurring_checkbox"
    )
    
    # The number of occurrences of the recurring bill. This is optional.
    use_occurrences = st.checkbox(
        label="Limit number of occurrences",
        value=existing_occurrences is not None,
        key=f"{key_prefix}_use_occurrences"
    )
    
    # The end date of the recurring bill. This is optional.
    use_end_date = st.checkbox(
        label="Set end date",
        value=existing_end_date is not None,
        key=f"{key_prefix}_use_end_date"
    )
    
    # Render the form for editing the bill.
    with st.form(key=f"{key_prefix}_edit_form"):
        
        # Render the bill ID as text (read-only, cannot be changed).
        st.text_input(label="Bill ID", value=bill_id, disabled=True)
        
        # Render the service name input.
        service = st.text_input(label="Service Name", value=existing_service)
        
        # Render the amount due input.
        amount_due = st.number_input(
            label="Amount Due ($)",
            min_value=0.01,
            value=float(existing_amount),
            format="%.2f"
        )
        
        # Render the due date input for non-recurring bills. For
        # non-recurring bills, end_date stores the due date.
        if not recurring:
            due_date = st.date_input(
                label="Due Date",
                value=existing_end_date if existing_end_date else None
            )
            start_date = None
            frequency = None
            interval = None
            occurrences = None
            end_date = None
        
        # If the bill is recurring, then render the start date,
        # frequency, interval, occurrences, and end date inputs.
        else:
            
            # Due date is not used for recurring bills.
            due_date = None
            
            # Render the start date input.
            start_date = st.date_input(
                label="Start Date",
                value=existing_start_date if existing_start_date else None
            )
            
            # Render the frequency selectbox.
            frequency = st.selectbox(
                label="Frequency",
                options=["monthly", "quarterly", "annual", "weekly", "daily"],
                index=(["monthly", "quarterly", "annual", "weekly", "daily"].index(existing_frequency)
                       if existing_frequency in ["monthly", "quarterly", "annual", "weekly", "daily"]
                       else 0)
            )
            
            # Render the interval input.
            interval = st.number_input(
                label="Interval",
                min_value=1,
                value=int(existing_interval)
            )
            
            # Render the occurrences input. This is optional.
            if use_occurrences:
                occurrences = st.number_input(
                    label="Number of Occurrences",
                    min_value=1,
                    value=int(existing_occurrences) if existing_occurrences else 1
                )
            else:
                occurrences = None
            
            # Render the end date input. This is optional as well.
            if use_end_date:
                end_date = st.date_input(
                    label="End Date",
                    value=existing_end_date if existing_end_date else None
                )
            else:
                end_date = None
        
        # Create two columns for Save and Cancel buttons.
        col1, col2 = st.columns(2)
        
        with col1:
            # Render the submit button.
            submitted = st.form_submit_button(label="Save Changes", use_container_width=True)
        
        with col2:
            # Render the cancel button.
            cancel = st.form_submit_button(label="Cancel", use_container_width=True)
        
        # If cancel is clicked, clear edit state and selection,
        # then return.
        if cancel:
            if f"editing_{bill_id}" in st.session_state:
                del st.session_state[f"editing_{bill_id}"]
            # Also clear selection state if it exists.
            if 'selected_bill_id' in st.session_state:
                del st.session_state['selected_bill_id']
            st.rerun()
            return False
        
        # If the form is submitted, update the bill.
        if submitted:
            
            try:
                
                # Build the updates dictionary with only fields that can be updated.
                # Note: bill_id cannot be changed, so it's not included.
                updates = {
                    "service": service,
                    "amount_due": float(amount_due),
                    "recurring": recurring
                }
                
                # Add fields based on whether bill is recurring or not.
                # For non-recurring bills, end_date stores the due date.
                if not recurring:
                    if due_date:
                        updates["end_date"] = due_date
                    # Clear recurring-specific fields if switching from recurring.
                    updates["start_date"] = None
                    updates["frequency"] = None
                    updates["interval"] = None
                    updates["occurrences"] = None
                    # Note: For non-recurring, end_date is the due date.
                else:
                    if start_date:
                        updates["start_date"] = start_date
                    if frequency:
                        updates["frequency"] = frequency
                    if interval:
                        updates["interval"] = interval
                    if occurrences:
                        updates["occurrences"] = occurrences
                    if end_date:
                        updates["end_date"] = end_date
                    # For recurring bills, end_date is the recurrence end date.
                
                # Update bill using SinkingFund API.
                fund.update_bill(bill_id, updates)
                
                # Clear edit state and selection.
                if f"editing_{bill_id}" in st.session_state:
                    del st.session_state[f"editing_{bill_id}"]
                if 'selected_bill_id' in st.session_state:
                    del st.session_state['selected_bill_id']
                
                st.success(f"Updated bill: {service}")
                st.rerun()
                return True
                    
            except Exception as e:
                st.error(f"Error updating bill: {str(e)}")
                return False
    
    return False

