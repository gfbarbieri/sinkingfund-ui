"""
Report Utilities
================

Utility functions for converting report data from the sinkingfund library
into pandas DataFrames for display in Streamlit. Handles conversion of
account balance, contributions, and payouts sections.

Features
--------
- Convert report sections to DataFrames with Date index
- Handle multiple bill IDs as columns
- Extract totals and counts from report structure
- Support for account_balance, contributions, and payouts sections

Examples
--------
.. code-block:: python

   from sinkingfund_ui.utils.report_utils import (
       convert_report_section_to_dataframe
   )
   from sinkingfund import SinkingFund
   from datetime import date, timedelta
   import pandas as pd

   fund = SinkingFund(
       start_date=date.today(),
       end_date=date.today() + timedelta(days=365),
       balance=1000.0
   )
   fund.add_bills(source=[...], contribution_interval=14)
   report = fund.quick_report(
       contribution_interval=14,
       allocation_strategy="sorted",
       scheduler_strategy="independent_scheduler"
   )

   # Convert account balance section to DataFrame.
   balance_df = convert_report_section_to_dataframe(
       report, 'account_balance'
   )

   # Convert contributions section to DataFrame.
   contrib_df = convert_report_section_to_dataframe(
       report, 'contributions'
   )
"""

########################################################################
## IMPORTS
########################################################################

import pandas as pd

########################################################################
## FUNCTIONS
########################################################################

def convert_report_section_to_dataframe(report_data, section_key):
    """
    Convert one section of the report dictionary to a DataFrame.
    
    Parameters
    ----------
    report_data : dict
        The report dictionary from quick_start()
    section_key : str
        The section to convert ('account_balance', 'contributions', or 'payouts')
        
    Returns
    -------
    pd.DataFrame
        DataFrame with Date as index and columns for total, count, and individual bills
    """
    if not report_data:
        return pd.DataFrame()
    
    # Get all unique bill IDs for this section
    all_bill_ids = set()
    for date_data in report_data.values():
        all_bill_ids.update(date_data[section_key]['bills'].keys())
    
    all_bill_ids = sorted(list(all_bill_ids))
    
    # Build the data
    section_data = []
    for date, data in sorted(report_data.items()):
        row = {
            'Date': date,
            'total': float(data[section_key]['total']),
            'count': data[section_key]['count']
        }
        
        # Add columns for each bill
        for bill_id in all_bill_ids:
            row[f'bill_{bill_id}'] = float(data[section_key]['bills'].get(bill_id, 0))
        
        section_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(section_data).set_index('Date')
    
    return df