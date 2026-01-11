"""
Strategy Selection Forms
========================

Forms for selecting allocation and scheduler strategies. Provides dropdowns
for choosing how to allocate initial balance and how to schedule
contributions over time.

Features
--------
- Allocation strategy selection (sorted, proportional, none)
- Proportional method selection (when using proportional allocation)
- Scheduler strategy selection (independent_scheduler)
- Strategy preview section
- Automatic session state management

Examples
--------
.. code-block:: python

   import streamlit as st
   from sinkingfund_ui.components.forms.strategy import (
       allocation_strategy_form,
       scheduler_strategy_form,
       proportional_method_form
   )

   # Select allocation strategy.
   allocation_strategy = allocation_strategy_form()

   # If proportional, select method.
   if allocation_strategy == "proportional":
       method = proportional_method_form()

   # Select scheduler strategy.
   scheduler_strategy = scheduler_strategy_form()
"""

########################################################################
## IMPORTS
########################################################################

import streamlit as st

########################################################################
## STRATEGY OPTIONS
########################################################################

# Allocation strategies available in the sinkingfund library.
# Options: "sorted" (default), "proportional", "none" (skip allocation).
ALLOCATION_STRATEGIES = [
    "sorted",
    "proportional",
    "none"
]

# Scheduler strategies available in the sinkingfund library.
# Options: "independent_scheduler" (default).
SCHEDULER_STRATEGIES = [
    "independent_scheduler"
]

# Proportional allocation methods available in the sinkingfund library.
# Options: "urgency", "equal", "proportional", "zero".
PROPORTIONAL_METHODS = [
    "proportional",
    "urgency",
    "equal",
    "zero"
]

########################################################################
## ALLOCATION STRATEGY FORM
########################################################################

def allocation_strategy_form():
    """
    Render the allocation strategy selection dropdown.

    Returns
    -------
    str | None
        Selected allocation strategy, or None if not selected.
    """

    # Render the allocation strategy dropdown with key for automatic
    # state management. Streamlit will store the value in
    # st.session_state['allocation_strategy'] automatically.
    selected_strategy = st.selectbox(
        label="Allocation Strategy",
        options=ALLOCATION_STRATEGIES,
        index=0,  # Default to first option if not in session state
        key="allocation_strategy",
        help=(
            "Select how to distribute the initial account balance "
            "across envelopes."
        )
    )

    return selected_strategy

########################################################################
## SCHEDULER STRATEGY FORM
########################################################################

def scheduler_strategy_form():
    """
    Render the scheduler strategy selection dropdown.

    Returns
    -------
    str | None
        Selected scheduler strategy, or None if not selected.
    """

    # Render the scheduler strategy dropdown with key for automatic
    # state management. Streamlit will store the value in
    # st.session_state['scheduler_strategy'] automatically.
    selected_strategy = st.selectbox(
        label="Scheduler Strategy",
        options=SCHEDULER_STRATEGIES,
        index=0,  # Default to first option if not in session state
        key="scheduler_strategy",
        help=(
            "Select how to schedule contributions over time for "
            "each envelope."
        )
    )

    return selected_strategy

########################################################################
## PROPORTIONAL METHOD FORM
########################################################################

def proportional_method_form():
    """
    Render the proportional allocation method selection dropdown.
    This is only shown when "proportional" allocation strategy is selected.

    Returns
    -------
    str | None
        Selected proportional method, or None if not selected.
    """

    # Render the proportional method dropdown with key for automatic
    # state management. Streamlit will store the value in
    # st.session_state['proportional_method'] automatically.
    selected_method = st.selectbox(
        label="Proportional Method",
        options=PROPORTIONAL_METHODS,
        index=0,  # Default to first option if not in session state
        key="proportional_method",
        help=(
            "Select the method for proportional allocation: "
            "'proportional' (by amount), 'urgency' (by due date), "
            "'equal' (equal distribution), or 'zero' (no allocation)."
        )
    )

    return selected_method


