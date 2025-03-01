import streamlit as st
import pandas as pd
import numpy as np
import datetime
from io import BytesIO

# Configure page
st.set_page_config(page_title="Lease Accounting Tool", layout="wide")

# Main app interface
st.title("Lease Accounting Tool")
st.write("Enter lease information to generate FRS102 accounting entries")

# Form for manual entry
with st.form("lease_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        lease_start_date = st.date_input("Lease Start Date")
        lease_end_date = st.date_input("Lease End Date", value=lease_start_date + datetime.timedelta(days=365*3))
        payment_amount = st.number_input("Payment Amount (£)", min_value=0.0, value=1000.0)
        payment_frequency = st.selectbox(
            "Payment Frequency",
            options=["monthly", "quarterly", "semi-annual", "annual"]
        )
    
    with col2:
        initial_direct_costs = st.number_input("Initial Direct Costs (£)", min_value=0.0, value=0.0)
        has_purchase_option = st.checkbox("Has Purchase Option")
        purchase_option_amount = st.number_input("Purchase Option Amount (£)", min_value=0.0, value=0.0, disabled=not has_purchase_option)
        asset_description = st.text_input("Asset Description", value="Equipment")
    
    # OBR Rate input
    obr_rate = st.slider(
        "OBR Rate (%)",
        min_value=0.0,
        max_value=15.0,
        value=5.0,
        step=0.1
    )
    
    submitted = st.form_submit_button("Calculate Lease Accounting")

if submitted:
    # Collect lease data
    lease_data = {
        'lease_start_date': lease_start_date.strftime('%Y-%m-%d'),
        'lease_end_date': lease_end_date.strftime('%Y-%m-%d'),
        'payment_amount': payment_amount,
        'payment_frequency': payment_frequency,
        'initial_direct_costs': initial_direct_costs,
        'has_purchase_option': has_purchase_option,
        'purchase_option_amount': purchase_option_amount if has_purchase_option else 0,
        'asset_description': asset_description
    }
    
    # Calculate lease accounting values
    def calculate_lease_accounting(lease_data, obr_rate):
        # Parse dates
        start_date = datetime.datetime.strptime(lease_data['lease_start_date'], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(lease_data['lease_end_date'], '%Y-%m-%d')
        
        # Calculate lease term in months
        lease_term_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        
        # Set payment frequency multiplier
        freq_map = {
            'monthly': 1,
            'quarterly': 3,
            'semi-annual': 6,
            'annual': 12
        }
        payment_multiplier = freq_map.get(lease_data['payment_frequency'].lower(), 1)
        
        # Calculate number of payments
        num_payments = max(1, lease_term_months // payment_multiplier)
        
        # Convert annual rate to payment period rate
        period_rate = obr_rate / 100 / (12 / payment_multiplier)
        
        # Calculate present value of lease payments
        payment_amount = float(lease_data['payment_amount'])
        if period_rate > 0:
            pv_lease_payments = payment_amount * ((1 - (1 + period_rate) ** -num_payments) / period_rate)
        else:
            pv_lease_payments = payment_amount * num_payments
        
        # Add present value of purchase option if applicable
        if lease_data.get('has_purchase_option', False) and lease_data.get('purchase_option_amount'):
            pv_purchase_option = float(lease_data['purchase_option_amount']) / ((1 + period_rate) ** num_payments)
            pv_lease_payments += pv_purchase_option
        
        # Add initial direct costs
        if lease_data.get('initial_direct_costs'):
            initial_direct_costs = float(lease_data['initial_direct_costs'])
        else:
            initial_direct_costs = 0
        
        # Calculate right-of-use asset
        rou_asset = pv_lease_payments + initial_direct_costs
        
        # Calculate amortization schedule
        schedule = []
        remaining_liability = pv_lease_payments
        
        for period in range(1, num_payments + 1):
            interest_expense = remaining_liability * period_rate
            principal_payment = payment_amount - interest_expense
            remaining_liability -= principal_payment
            
            schedule.append({
                'period': period,
                'payment': payment_amount,
                'interest': interest_expense,
                'principal': principal_payment,
                'ending_balance': remaining_liability if remaining_liability > 0 else 0
            })
        
        # Return calculation results
        return {
            'lease_term_months': lease_term_months,
            'number_of_payments': num_payments,
            'payment_frequency': payment_multiplier,
            'period_interest_rate': period_rate,
            'present_value_lease_payments': pv_lease_payments,
            'right_of_use_asset': rou_asset,
            'initial_lease_liability': pv_lease_payments,
            'amortization_schedule': schedule
        }
    
    accounting_results = calculate_lease_accounting(lease_data, obr_rate)
    
    # Display results
    st.subheader("Accounting Results")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Right-of-Use Asset", f"£{accounting_results['right_of_use_asset']:,.2f}")
        st.metric("Initial Lease Liability", f"£{accounting_results['initial_lease_liability']:,.2f}")
    
    with col2:
        st.metric("Lease Term (Months)", accounting_results['lease_term_months'])
        st.metric("Discount Rate", f"{obr_rate}%")
    
    # Show amortization schedule
    st.subheader("Amortization Schedule")
    schedule_df = pd.DataFrame(accounting_results['amortization_schedule'])
    st.dataframe(schedule_df)
    
    # Journal entries tab
    st.subheader("Journal Entries")
    
    # Initial recognition entry
    st.write("**Initial Recognition**")
    initial_entry = pd.DataFrame([
        {"Account": "Right-of-Use Asset", "Debit": accounting_results['right_of_use_asset'], "Credit": 0},
        {"Account": "Lease Liability", "Debit": 0, "Credit": accounting_results['initial_lease_liability']}
    ])
    st.table(initial_entry)
    
    # First month entry
    st.write("**First Period Journal Entry**")
    first_period = accounting_results['amortization_schedule'][0]
    monthly_depreciation = accounting_results['right_of_use_asset'] / accounting_results['lease_term_months']
    
    first_month_entry = pd.DataFrame([
        {"Account": "Interest Expense", "Debit": first_period['interest'], "Credit": 0},
        {"Account": "Lease Liability", "Debit": first_period['principal'], "Credit": 0},
        {"Account": "Cash", "Debit": 0, "Credit": first_period['payment']},
        {"Account": "Depreciation Expense", "Debit": monthly_depreciation, "Credit": 0},
        {"Account": "Right-of-Use Asset", "Debit": 0, "Credit": monthly_depreciation}
    ])
    st.table(first_month_entry)
    
    # Technical memo
    st.subheader("Technical Accounting Memo")
    
    memo = f"""
    # Technical Accounting Memo: Lease Accounting under FRS102
    
    ## 1. Lease Identification and Key Terms
    
    - **Asset Description**: {lease_data['asset_description']}
    - **Lease Start Date**: {lease_data['lease_start_date']}
    - **Lease End Date**: {lease_data['lease_end_date']}
    - **Lease Term**: {accounting_results['lease_term_months']} months
    - **Payment Amount**: £{lease_data['payment_amount']:,.2f} {lease_data['payment_frequency']}
    - **Purchase Option**: {'Yes - £' + str(lease_data['purchase_option_amount']) if lease_data['has_purchase_option'] else 'No'}
    - **Initial Direct Costs**: £{lease_data['initial_direct_costs']:,.2f}
    
    ## 2. Recognition Criteria Analysis
    
    This lease meets the recognition criteria under FRS102 Section 20 as:
    
    - It conveys the right to control the use of the identified asset for a period of time
    - The lease term is significant relative to the economic life of the asset
    - The present value of the lease payments is significant
    
    ## 3. Initial Measurement
    
    - **Right-of-Use Asset**: £{accounting_results['right_of_use_asset']:,.2f}
    - **Lease Liability**: £{accounting_results['initial_lease_liability']:,.2f}
    - **Discount Rate (OBR)**: {obr_rate}%
    
    The lease liability has been calculated as the present value of future lease payments, discounted at the OBR rate of {obr_rate}%.
    
    The right-of-use asset includes the lease liability plus initial direct costs of £{lease_data['initial_direct_costs']:,.2f}.
    
    ## 4. Subsequent Measurement Approach
    
    - The lease liability will be measured at amortized cost using the effective interest method
    - The right-of-use asset will be depreciated on a straight-line basis over the lease term of {accounting_results['lease_term_months']} months
    - Interest expense will be recognized based on the OBR rate of {obr_rate}% applied to the outstanding lease liability
    
    ## 5. Journal Entries
    
    ### Initial Recognition
    
    | Account | Debit | Credit |
    |---------|-------|--------|
    | Right-of-Use Asset | £{accounting_results['right_of_use_asset']:,.2f} | |
    | Lease Liability | | £{accounting_results['initial_lease_liability']:,.2f} |
    
    ### First Period Entry
    
    | Account | Debit | Credit |
    |---------|-------|--------|
    | Interest Expense | £{first_period['interest']:,.2f} | |
    | Lease Liability | £{first_period['principal']:,.2f} | |
    | Cash | | £{first_period['payment']:,.2f} |
    | Depreciation Expense | £{monthly_depreciation:,.2f} | |
    | Right-of-Use Asset | | £{monthly_depreciation:,.2f} |
    """
    
    st.markdown(memo)
    
    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        memo_download = memo.encode()
        st.download_button(
            label="Download Memo",
            data=BytesIO(memo_download),
            file_name="lease_accounting_memo.txt",
            mime="text/plain"
        )
    
    with col2:
        # Create Excel file in memory
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer) as writer:
            # Amortization schedule
            schedule_df = pd.DataFrame(accounting_results['amortization_schedule'])
            schedule_df.to_excel(writer, sheet_name="Amortization", index=False)
            
            # Summary information
            summary_data = {
                "Metric": ["Right-of-Use Asset", "Initial Lease Liability", "Lease Term (Months)", "Discount Rate"],
                "Value": [
                    f"£{accounting_results['right_of_use_asset']:,.2f}",
                    f"£{accounting_results['initial_lease_liability']:,.2f}",
                    accounting_results['lease_term_months'],
                    f"{obr_rate}%"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
        
        excel_buffer.seek(0)
        st.download_button(
            label="Download Calculations (Excel)",
            data=excel_buffer,
            file_name="lease_calculations.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
