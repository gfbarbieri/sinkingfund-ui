"""
Figure Components
=================

Components for creating all visualizations in the UI, including interactive
Plotly charts from report DataFrames and workflow/preview displays. Provides
time series visualization of account balance, contributions, and payouts over
time, plus strategy workflow diagrams and allocation/schedule previews.

Features
--------
- Time series chart with account balance line
- Contribution markers with bill breakdowns in hover text
- Payout markers with bill breakdowns in hover text
- Interactive Plotly figures with hover details
- Strategy flow diagram showing workflow steps
- Allocation preview showing balance distribution
- Schedule preview showing contribution scheduling
- Conditional rendering based on fund state

Examples
--------
.. code-block:: python

   from sinkingfund_ui.components.figures import (
       create_timeseries_chart_from_dfs,
       render_strategy_flow_diagram,
       render_allocation_preview,
       render_schedule_preview
   )
   from sinkingfund_ui.utils.report_utils import (
       convert_report_section_to_dataframe
   )
   import streamlit as st

   # Get report from fund.
   report = fund.quick_report(...)

   # Convert report sections to DataFrames.
   balance_df = convert_report_section_to_dataframe(
       report, 'account_balance'
   )
   contrib_df = convert_report_section_to_dataframe(
       report, 'contributions'
   )
   payouts_df = convert_report_section_to_dataframe(
       report, 'payouts'
   )

   # Create and display chart.
   fig = create_timeseries_chart_from_dfs(
       balance_df, contrib_df, payouts_df
   )
   st.plotly_chart(fig, use_container_width=True)

   # Render workflow diagram.
   render_strategy_flow_diagram()

   # Render allocation preview.
   render_allocation_preview(
       fund=fund,
       allocation_strategy="sorted"
   )

   # Render schedule preview.
   render_schedule_preview(
       fund=fund,
       scheduler_strategy="independent_scheduler",
       contribution_interval=14
   )
"""

########################################################################
## IMPORTS
########################################################################

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

########################################################################
## FUNCTIONS
########################################################################

def create_timeseries_chart_from_dfs(account_balance_df, contributions_df, payouts_df):
    """
    Create time series chart using the DataFrame format.
    
    Parameters
    ----------
    account_balance_df : pd.DataFrame
        Account balance data with Date index
    contributions_df : pd.DataFrame  
        Contributions data with Date index
    payouts_df : pd.DataFrame
        Payouts data with Date index
        
    Returns
    -------
    plotly.graph_objects.Figure
        Interactive plotly figure
    """

    # Create the figure.
    fig = go.Figure()
    
    # Add account balance line (only if DataFrame is not empty).
    if not account_balance_df.empty and 'total' in account_balance_df.columns:
        fig.add_trace(go.Scatter(
            x=account_balance_df.index,
            y=account_balance_df['total'],
            mode='lines',
            name='Account Balance',
            line=dict(color='blue', width=2),
            hovertemplate='Date: %{x}<br>Balance: $%{y:.2f}<extra></extra>'
        ))
    
    # Add contribution markers (only for dates with contributions > 0).
    if not contributions_df.empty and 'total' in contributions_df.columns:
        contrib_dates = contributions_df[contributions_df['total'] > 0]
    else:
        contrib_dates = pd.DataFrame()
    
    if not contrib_dates.empty:
        # Create hover text for contributions
        contrib_hover_text = []
        for date, row in contrib_dates.iterrows():
            bill_breakdown = []
            for col in contrib_dates.columns:
                if col.startswith('bill_') and row[col] > 0:
                    bill_id = col.replace('bill_', '')
                    bill_breakdown.append(f"  {bill_id}: ${row[col]:.2f}")
            
            bills_text = "<br>".join(bill_breakdown)
            hover_text = f"Date: {date}<br>Contributions: ${row['total']:.2f}<br>Bills:<br>{bills_text}"
            contrib_hover_text.append(hover_text)
        
        # Get corresponding account balance for marker placement
        contrib_balances = account_balance_df.loc[contrib_dates.index, 'total']
        
        fig.add_trace(go.Scatter(
            x=contrib_dates.index,
            y=contrib_balances,
            mode='markers',
            name='Contributions',
            marker=dict(
                color='green',
                size=8,
                symbol='circle',
                line=dict(color='darkgreen', width=1)
            ),
            hovertemplate='%{text}<extra></extra>',
            text=contrib_hover_text
        ))
    
    # Add payout markers (only for dates with payouts < 0).
    if not payouts_df.empty and 'total' in payouts_df.columns:
        payout_dates = payouts_df[payouts_df['total'] < 0]
    else:
        payout_dates = pd.DataFrame()
    
    if not payout_dates.empty:
        # Create hover text for payouts
        payout_hover_text = []
        for date, row in payout_dates.iterrows():
            bill_breakdown = []
            for col in payout_dates.columns:
                if col.startswith('bill_') and row[col] < 0:
                    bill_id = col.replace('bill_', '')
                    bill_breakdown.append(f"  {bill_id}: ${abs(row[col]):.2f}")
            
            bills_text = "<br>".join(bill_breakdown)
            hover_text = f"Date: {date}<br>Payouts: ${abs(row['total']):.2f}<br>Bills:<br>{bills_text}"
            payout_hover_text.append(hover_text)
        
        # Get corresponding account balance for marker placement
        payout_balances = account_balance_df.loc[payout_dates.index, 'total']
        
        fig.add_trace(go.Scatter(
            x=payout_dates.index,
            y=payout_balances,
            mode='markers',
            name='Payouts',
            marker=dict(
                color='red',
                size=8,
                symbol='triangle-down',
                line=dict(color='darkred', width=1)
            ),
            hovertemplate='%{text}<extra></extra>',
            text=payout_hover_text
        ))
    
    # Update layout
    fig.update_layout(
        title='Sinking Fund Account Balance Over Time',
        xaxis_title='Date',
        yaxis_title='Account Balance ($)',
        hovermode='closest',
        showlegend=True,
        height=500,
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray', tickformat='$,.0f')
    )
    
    return fig

########################################################################
## STRATEGY FLOW DIAGRAM
########################################################################

def render_strategy_flow_diagram():
    """
    Render a text-based flowchart showing the strategy workflow.
    """

    # Render the workflow diagram as a markdown flowchart.
    st.markdown("""
    **Workflow:**
    
    1. **Create Fund** → Set planning range and initial balance
    2. **Load Bills** → Add bills from file or manually
    3. **Select Strategies** → Choose allocation and scheduler strategies
    4. **Configure Report** → Set contribution interval and options
    5. **Generate Report** → Create bill summary and schedules
    6. **View Results** → Review bill summary table
    """)

########################################################################
## ALLOCATION PREVIEW
########################################################################

def render_allocation_preview(fund, allocation_strategy):
    """
    Render a preview of how the balance will be allocated.

    Parameters
    ----------
    fund : SinkingFund
        The sinking fund instance.
    allocation_strategy : str
        Selected allocation strategy.
    """

    # Only show preview if there are bills and a balance.
    if not fund.get_bills() or fund.balance == 0:
        return

    # Render a simple preview message.
    st.info(
        f"With **{allocation_strategy}** allocation strategy, "
        f"the initial balance of ${fund.balance:.2f} will be "
        f"distributed across {len(fund.get_bills())} bill(s)."
    )

########################################################################
## SCHEDULE PREVIEW
########################################################################

def render_schedule_preview(fund, scheduler_strategy, contribution_interval):
    """
    Render a preview of the contribution schedule.

    Parameters
    ----------
    fund : SinkingFund
        The sinking fund instance.
    scheduler_strategy : str
        Selected scheduler strategy.
    contribution_interval : int
        Contribution interval in days.
    """

    # Only show preview if there are bills.
    if not fund.get_bills():
        return

    # Render a simple preview message.
    st.info(
        f"With **{scheduler_strategy}** scheduler strategy, "
        f"contributions will be scheduled every {contribution_interval} "
        f"days for {len(fund.get_bills())} bill(s)."
    )
