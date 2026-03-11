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
    
    # Collect dates with cashflow activity.
    if not contributions_df.empty and 'total' in contributions_df.columns:
        contrib_active = contributions_df[contributions_df['total'] > 0]
    else:
        contrib_active = pd.DataFrame()

    if not payouts_df.empty and 'total' in payouts_df.columns:
        payout_active = payouts_df[payouts_df['total'] < 0]
    else:
        payout_active = pd.DataFrame()

    cashflow_dates = set(contrib_active.index) | set(payout_active.index)

    # Classify each cashflow date and build hover text.
    green_dates, green_hovers = [], []    # contribution-only
    red_dates, red_hovers = [], []        # payout-only
    purple_dates, purple_hovers = [], []  # both

    for dt in sorted(cashflow_dates):
        contrib_total = contrib_active.loc[dt, 'total'] if dt in contrib_active.index else 0.0
        payout_total = payout_active.loc[dt, 'total'] if dt in payout_active.index else 0.0

        # Build combined hover text.
        hover_parts = [f"Date: {dt}"]

        if contrib_total > 0:
            hover_parts.append(f"Contributions: ${contrib_total:.2f}")
            bill_lines = []
            for col in contrib_active.columns:
                if col.startswith('bill_') and dt in contrib_active.index and contrib_active.loc[dt, col] > 0:
                    bill_id = col.replace('bill_', '')
                    bill_lines.append(f"  {bill_id}: ${contrib_active.loc[dt, col]:.2f}")
            if bill_lines:
                hover_parts.append("Bills:<br>" + "<br>".join(bill_lines))

        if payout_total < 0:
            hover_parts.append(f"Payouts: ${abs(payout_total):.2f}")
            bill_lines = []
            for col in payout_active.columns:
                if col.startswith('bill_') and dt in payout_active.index and payout_active.loc[dt, col] < 0:
                    bill_id = col.replace('bill_', '')
                    bill_lines.append(f"  {bill_id}: ${abs(payout_active.loc[dt, col]):.2f}")
            if bill_lines:
                hover_parts.append("Bills:<br>" + "<br>".join(bill_lines))

        hover_text = "<br>".join(hover_parts)

        # Classify by presence: contribution-only, payout-only, or both.
        has_contrib = contrib_total > 0
        has_payout = payout_total < 0

        if has_contrib and has_payout:
            purple_dates.append(dt)
            purple_hovers.append(hover_text)
        elif has_contrib:
            green_dates.append(dt)
            green_hovers.append(hover_text)
        else:
            red_dates.append(dt)
            red_hovers.append(hover_text)

    # Add contribution-only markers (green circles).
    if green_dates:
        green_balances = account_balance_df.loc[green_dates, 'total']
        fig.add_trace(go.Scatter(
            x=green_dates,
            y=green_balances,
            mode='markers',
            name='Contributions',
            marker=dict(
                color='green',
                size=8,
                symbol='circle',
                line=dict(color='darkgreen', width=1)
            ),
            hovertemplate='%{text}<extra></extra>',
            text=green_hovers
        ))

    # Add payout-only markers (red triangle-down).
    if red_dates:
        red_balances = account_balance_df.loc[red_dates, 'total']
        fig.add_trace(go.Scatter(
            x=red_dates,
            y=red_balances,
            mode='markers',
            name='Payouts',
            marker=dict(
                color='red',
                size=8,
                symbol='triangle-down',
                line=dict(color='darkred', width=1)
            ),
            hovertemplate='%{text}<extra></extra>',
            text=red_hovers
        ))

    # Add both-present markers (purple circles).
    if purple_dates:
        purple_balances = account_balance_df.loc[purple_dates, 'total']
        fig.add_trace(go.Scatter(
            x=purple_dates,
            y=purple_balances,
            mode='markers',
            name='Both',
            marker=dict(
                color='purple',
                size=8,
                symbol='circle',
                line=dict(color='indigo', width=1)
            ),
            hovertemplate='%{text}<extra></extra>',
            text=purple_hovers
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

def create_cashflow_chart_from_dfs(contributions_df, payouts_df):
    """
    Create line chart showing contribution and payout amounts per date.

    Parameters
    ----------
    contributions_df : pd.DataFrame
        Contributions data with Date index
    payouts_df : pd.DataFrame
        Payouts data with Date index

    Returns
    -------
    plotly.graph_objects.Figure
        Interactive plotly line chart
    """

    fig = go.Figure()

    # Filter to active contribution dates.
    if not contributions_df.empty and 'total' in contributions_df.columns:
        contrib_active = contributions_df[contributions_df['total'] > 0]
    else:
        contrib_active = pd.DataFrame()

    # Filter to active payout dates.
    if not payouts_df.empty and 'total' in payouts_df.columns:
        payout_active = payouts_df[payouts_df['total'] < 0]
    else:
        payout_active = pd.DataFrame()

    # Build contribution line.
    if not contrib_active.empty:
        hover_texts = []
        for dt in contrib_active.index:
            parts = [f"Date: {dt}", f"Contributions: ${contrib_active.loc[dt, 'total']:.2f}"]
            bill_lines = []
            for col in contrib_active.columns:
                if col.startswith('bill_') and contrib_active.loc[dt, col] > 0:
                    bill_id = col.replace('bill_', '')
                    bill_lines.append(f"  {bill_id}: ${contrib_active.loc[dt, col]:.2f}")
            if bill_lines:
                parts.append("Bills:<br>" + "<br>".join(bill_lines))
            hover_texts.append("<br>".join(parts))

        fig.add_trace(go.Scatter(
            x=contrib_active.index.tolist(),
            y=contrib_active['total'].tolist(),
            name='Contributions',
            mode='lines+markers',
            line=dict(color='green'),
            marker=dict(color='green', symbol='circle', size=10),
            hovertemplate='%{text}<extra></extra>',
            text=hover_texts,
        ))

    # Build payout line (values are already negative).
    if not payout_active.empty:
        hover_texts = []
        for dt in payout_active.index:
            parts = [f"Date: {dt}", f"Payouts: ${abs(payout_active.loc[dt, 'total']):.2f}"]
            bill_lines = []
            for col in payout_active.columns:
                if col.startswith('bill_') and payout_active.loc[dt, col] < 0:
                    bill_id = col.replace('bill_', '')
                    bill_lines.append(f"  {bill_id}: ${abs(payout_active.loc[dt, col]):.2f}")
            if bill_lines:
                parts.append("Bills:<br>" + "<br>".join(bill_lines))
            hover_texts.append("<br>".join(parts))

        fig.add_trace(go.Scatter(
            x=payout_active.index.tolist(),
            y=payout_active['total'].tolist(),
            name='Payouts',
            mode='lines+markers',
            line=dict(color='red'),
            marker=dict(color='red', symbol='triangle-down', size=10),
            hovertemplate='%{text}<extra></extra>',
            text=hover_texts,
        ))

    fig.update_layout(
        title='Contributions & Payouts Over Time',
        xaxis_title='Date',
        yaxis_title='Amount ($)',
        hovermode='closest',
        showlegend=True,
        height=350,
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray', tickformat='$,.0f'),
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
