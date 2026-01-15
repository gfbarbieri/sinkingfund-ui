"""
Main Application
================

Streamlit application for managing sinking funds. Provides a user interface
for creating funds, managing bills, allocating balances, and scheduling
contributions.

Features
--------
- Fund setup with planning period and initial balance configuration
- Bill management via file upload or manual entry (supports recurring bills)
- Allocation strategies: sorted, proportional, or none
- Scheduler strategies for contribution planning
- Interactive bills table with edit/delete functionality
- Bill summary table showing envelope status and allocations

Examples
--------
.. code-block:: python

   # Run the application.
   streamlit run sinkingfund_ui/main.py

   # The application will launch in a web browser. Users can:
   # 1. Create a fund with start/end dates and initial balance.
   # 2. Add bills (recurring or one-time).
   # 3. Select allocation and scheduler strategies.
   # 4. Generate contribution schedules and view reports.
"""

########################################################################
## IMPORTS
########################################################################

import streamlit as st
import traceback

from decimal import Decimal

from sinkingfund_ui.components.forms import (
    fund_setup_form, manual_bill_form, upload_bills_from_file,
    allocation_strategy_form, proportional_method_form, scheduler_strategy_form
)

from sinkingfund_ui.components.tables import (
    unified_bills_table, create_bill_summary_table, fund_info_table
)

from sinkingfund_ui.utils.report_utils import convert_report_section_to_dataframe
from sinkingfund_ui.components.figures import create_timeseries_chart_from_dfs

########################################################################
## PAGE CONFIGURATION
########################################################################

def configure_page():
    """
    Configure Streamlit page settings.
    """

    # Configure the page when launched.
    st.set_page_config(
        page_title="Sinking Fund Manager",
        layout="wide",
        initial_sidebar_state="expanded"
    )

########################################################################
## SESSION STATE MANAGEMENT
########################################################################

def initialize_session_state():
    """
    Initialize session state variables.
    """

    # Store the sinking fund object.
    if 'fund' not in st.session_state:
        st.session_state.fund = None

    # Store the bills data.
    if 'bills_data' not in st.session_state:
        st.session_state.bills_data = []

    # Store the quick report.
    if 'report' not in st.session_state:
        st.session_state.report = None

    # Store the allocation strategy.
    if 'allocation_strategy' not in st.session_state:
        st.session_state.allocation_strategy = None

    # Store the scheduler strategy.
    if 'scheduler_strategy' not in st.session_state:
        st.session_state.scheduler_strategy = None

    # Store the proportional method (only used when allocation_strategy
    # is "proportional").
    if 'proportional_method' not in st.session_state:
        st.session_state.proportional_method = None

########################################################################
## RENDER FUND MANAGEMENT SECTION
########################################################################

def render_fund_management_sidebar():
    """
    Render the fund management form in the sidebar.
    """

    st.header("Fund Management")
    fund_setup_form()

########################################################################
## RENDER BILL MANAGEMENT SECTION
########################################################################

def render_bill_management_sidebar():
    """Render the sidebar with bill management options."""

    st.header("Manage Bills")
    
    if st.session_state.fund is None:
        st.info("Set up a fund in Fund Management to manage bills.")
        return
    
    # File upload section
    st.subheader("Upload Bills from File")
    upload_bills_from_file()
        
    # Manual bill entry section
    st.subheader("Add Bill Manually")
    manual_bill_form(fund=st.session_state.fund)

########################################################################
## RENDER SCHEDULE CONTRIBUTIONS SIDEBAR
########################################################################

def render_schedule_contributions_sidebar():
    """
    Render the sidebar section for scheduling contributions with
    allocation strategy, contribution interval, and scheduler strategy.
    """

    st.header("Schedule Contributions")
    
    if st.session_state.fund is None:
        st.info("Set up a fund in Fund Management to schedule contributions.")
        return
    
    # Render allocation strategy selection.
    allocation_strategy = allocation_strategy_form()
    
    # If proportional allocation is selected, show method selection.
    proportional_method = None

    if allocation_strategy == "proportional":
        proportional_method = proportional_method_form()
    else:
        # Clear proportional method when not using proportional
        # allocation.
        if 'proportional_method' in st.session_state:
            del st.session_state.proportional_method
    
    # Render contribution interval input.
    contribution_interval = st.number_input(
        "Contribution Interval (days)", min_value=1, value=14,
        help="Days between contribution payments."
    )
    
    # Render scheduler strategy selection.
    scheduler_strategy = scheduler_strategy_form()
    
    # Render the generate schedule button. Disable if no bills exist.
    bills_exist = len(st.session_state.fund.get_bills()) > 0
    generate_button = st.button(
        "Generate Schedule",
        type="primary",
        disabled=not bills_exist,
        use_container_width=True
    )
    
    if not bills_exist:
        st.info("Add bills first before generating schedule.")
    
    # If the generate button was clicked, execute the full workflow.
    if generate_button:
        
        try:
            # Get bill instances for the planning period.
            bill_instances = st.session_state.fund.get_bill_instances()
            
            if not bill_instances:
                st.error("No bill instances found in the planning period.")
            else:
                # Check if envelopes already exist. If they do, sync them
                # with bills instead of creating new ones.
                existing_envelopes = st.session_state.fund.get_envelopes()
                if existing_envelopes:
                    # Sync existing envelopes with current bills.
                    st.session_state.fund.sync_envelopes_with_bills()
                else:
                    # Create new envelopes from bill instances.
                    st.session_state.fund.create_envelopes(bill_instances)
                
                # If strategy is "none", clear allocations before
                # updating dates. This must happen before
                # update_contribution_dates because that method uses
                # allocations and expects Decimal type.
                if allocation_strategy == "none":
                    envelopes = st.session_state.fund.get_envelopes()
                    if envelopes:
                        for envelope in envelopes:
                            envelope.initial_allocation = Decimal(0)
                
                # Update contribution dates.
                st.session_state.fund.update_contribution_dates(
                    contribution_interval
                )
                
                # Allocate balance if strategy is not "none" and balance > 0.
                if (
                    allocation_strategy != "none" and
                    st.session_state.fund.balance > 0
                ):
                    # Build allocation_kwargs for proportional strategy.
                    allocation_kwargs = {}
                    if (
                        allocation_strategy == "proportional" and
                        proportional_method
                    ):
                        allocation_kwargs["method"] = proportional_method
                    
                    # Perform allocation.
                    st.session_state.fund.allocate(
                        strategy=allocation_strategy,
                        **allocation_kwargs
                    )
                elif allocation_strategy == "none":
                    st.info("Allocation cleared (none strategy selected).")
                
                # Schedule cashflows using the selected strategy.
                st.session_state.fund.schedule(strategy=scheduler_strategy)
                
                # Generate report and store in session state for bill summary.
                report = st.session_state.fund.report(active_only=True)
                st.session_state.report = report
                
                st.success("Schedule generated successfully!")
                st.rerun()
        
        except Exception as e:
            st.error(f"Error generating schedule: {str(e)}")
            st.code(traceback.format_exc())

########################################################################
## RENDER SCHEDULE VISUALIZATION SECTION
########################################################################

def render_schedule_visualization():
    """
    Render the schedule visualization chart showing account balance,
    contributions, and payouts over time.
    """

    # Check if report exists in session state.
    if st.session_state.report is None or not st.session_state.report:
        st.info(
            "Use the sidebar to generate a schedule before viewing the "
            "visualization."
        )
        return
    
    try:
        # Convert report sections to DataFrames.
        account_balance_df = convert_report_section_to_dataframe(
            st.session_state.report, 'account_balance'
        )
        contributions_df = convert_report_section_to_dataframe(
            st.session_state.report, 'contributions'
        )
        payouts_df = convert_report_section_to_dataframe(
            st.session_state.report, 'payouts'
        )
        
        # Create the time series chart.
        fig = create_timeseries_chart_from_dfs(
            account_balance_df, contributions_df, payouts_df
        )
        
        # Display the chart.
        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error displaying schedule visualization: {str(e)}")
        st.code(traceback.format_exc())

########################################################################
## RENDER BILLS SECTION
########################################################################

def render_bills_section():
    """
    Render the bills section with unified bills table that includes
    display and deletion functionality, and bill summary table.
    """

    # Render the main header.
    st.header("Bills")

    if st.session_state.fund is None:
        st.info("Set up a fund in the sidebar to manage bills.")
        return

    # Render the unified bills table.
    try:
        unified_bills_table(fund=st.session_state.fund)
    except Exception as e:
        st.error(f"Error displaying bills: {str(e)}")
    
    # Render bill summary table if envelopes exist.
    envelopes = st.session_state.fund.get_envelopes()
    if envelopes:
        st.subheader("Envelopes")
        try:
            df_summary = create_bill_summary_table(
                fund=st.session_state.fund
            )
            if not df_summary.empty:
                st.dataframe(df_summary, use_container_width=True)
            else:
                st.info("No bill summary data available.")
        except Exception as e:
            st.error(f"Error creating bill summary: {str(e)}")

########################################################################
## MAIN APPLICATION
########################################################################

def main():
    """
    Main application function.
    """

    # Configure the page and initialize the session state. The session
    # state is used to store the sinking fund instance and the quick
    # report.
    configure_page()
    initialize_session_state()
    
    # Render the title and description.
    st.title("Sinking Fund Manager")

    # Render the sidebar.
    with st.sidebar:
        render_fund_management_sidebar()
        st.divider()
        render_bill_management_sidebar()
        st.divider()
        render_schedule_contributions_sidebar()

    # Main panel fund information (or placeholder).
    st.header("Fund Information")
    if st.session_state.fund is None:
        st.info("No fund has been set up. Use the sidebar to start one.")
        return

    fund_info_table(st.session_state.fund)
    
    # Render the main content.
    # Bills section (unified table with display and deletion,
    # plus summary).
    render_bills_section()
    
    # Schedule visualization section (chart showing account balance,
    # contributions, and payouts over time).
    st.header("Schedule Visualization")
    render_schedule_visualization()

if __name__ == "__main__":
    main()