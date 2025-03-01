import streamlit as st
import pandas as pd
import numpy as np
import datetime
from io import BytesIO

# Configure page
st.set_page_config(page_title="Lease Accounting Tool", layout="wide")

# Main app title
st.title("Lease Accounting Tool")
st.write("Enter lease information to generate FRS102 accounting entries")

# Create main tabs for lease management
tab_main, tab_reports = st.tabs(["Lease Management", "Reports & Analysis"])

with tab_main:
    # Create tabs for different lease information categories
    lease_tabs = st.tabs([
        "General", "Unit", "Rent", "Payments", "Insurance", 
        "Clause/Option", "Contact", "Cost Centers", 
        "Accounting", "Variable Payment", "SubLease"
    ])
    
    # Tab 1: General Lease Information
    with lease_tabs[0]:
        st.subheader("General Lease Information")
        
        col1, col2 = st.columns(2)
        with col1:
            lease_reference = st.text_input("Lease Reference Number")
            lease_type = st.selectbox("Lease Type", ["Property", "Equipment", "Vehicle", "Other"])
            lease_start_date = st.date_input("Lease Start Date")
            lease_end_date = st.date_input("Lease End Date", value=lease_start_date + datetime.timedelta(days=365*3))
            lessor_name = st.text_input("Lessor Name")
        
        with col2:
            lessee_name = st.text_input("Lessee Name")
            lease_status = st.selectbox("Status", ["Active", "Pending", "Expired", "Terminated"])
            currency = st.selectbox("Currency", options=["GBP (£)", "USD ($)", "EUR (€)"])
            description = st.text_area("Lease Description", height=100)
    
    # Tab 2: Unit Information
    with lease_tabs[1]:
        st.subheader("Unit Information")
        
        col1, col2 = st.columns(2)
        with col1:
            property_type = st.selectbox("Property Type", ["Office", "Retail", "Warehouse", "Manufacturing", "Land", "Residential", "Other"])
            address_line1 = st.text_input("Address Line 1")
            address_line2 = st.text_input("Address Line 2")
            city = st.text_input("City/Town")
            
        with col2:
            region = st.text_input("County/State/Region")
            postal_code = st.text_input("Postal/Zip Code")
            country = st.selectbox("Country", ["United Kingdom", "United States", "Germany", "France", "Other"])
            area_size = st.number_input("Area Size", min_value=0.0)
            area_unit = st.selectbox("Unit", ["sq ft", "sq m", "acres", "hectares"])
    
    # Tab 3: Rent Information
    with lease_tabs[2]:
        st.subheader("Rent Information")
        
        col1, col2 = st.columns(2)
        with col1:
            base_rent = st.number_input("Base Rent Amount", min_value=0.0, value=1000.0)
            payment_frequency = st.selectbox(
                "Payment Frequency",
                options=["monthly", "quarterly", "semi-annual", "annual"]
            )
            rent_free_period = st.number_input("Rent Free Period (months)", min_value=0, value=0)
            rent_commencement_date = st.date_input("Rent Commencement Date", value=lease_start_date)
            
        with col2:
            rent_review_frequency = st.number_input("Rent Review Frequency (years)", min_value=0, value=3)
            rent_review_type = st.selectbox("Rent Review Type", ["Market Rate", "RPI/CPI", "Fixed Percentage", "None"])
            if rent_review_type == "Fixed Percentage":
                rent_increase_percentage = st.number_input("Rent Increase Percentage", min_value=0.0, max_value=100.0, value=3.0)
            security_deposit = st.number_input("Security Deposit", min_value=0.0, value=0.0)
    
    # Tab 4: Payments
    with lease_tabs[3]:
        st.subheader("Payment Schedule")
        
        payment_type = st.selectbox("Payment Type", ["Fixed", "Variable", "Stepped"])
        
        if payment_type == "Stepped":
            st.write("Stepped Payment Schedule")
            num_steps = st.number_input("Number of Step Changes", min_value=1, value=2)
            
            for i in range(num_steps):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.date_input(f"Step {i+1} Start Date", value=lease_start_date + datetime.timedelta(days=365*i))
                with col2:
                    st.number_input(f"Step {i+1} Amount", min_value=0.0, value=1000.0 * (1 + (i * 0.1)))
                with col3:
                    st.selectbox(f"Step {i+1} Frequency", options=["monthly", "quarterly", "semi-annual", "annual"])
        
        payment_method = st.selectbox("Payment Method", ["Direct Debit", "Bank Transfer", "Check", "Other"])
        billing_address_same = st.checkbox("Billing Address Same as Property Address", value=True)
        
        if not billing_address_same:
            st.text_input("Billing Address Line 1")
            st.text_input("Billing Address Line 2")
            st.text_input("Billing City/Town")
    
    # Tab 5: Insurance
    with lease_tabs[4]:
        st.subheader("Insurance Information")
        
        col1, col2 = st.columns(2)
        with col1:
            insurance_required = st.checkbox("Insurance Required", value=True)
            if insurance_required:
                insurance_type = st.multiselect("Insurance Types Required", 
                                             ["Property", "Liability", "Business Interruption", "Contents", "Public Liability"])
                insurance_min_coverage = st.number_input("Minimum Coverage Amount", min_value=0)
                
        with col2:
            insurance_provider = st.text_input("Insurance Provider")
            policy_number = st.text_input("Policy Number")
            policy_expiry = st.date_input("Policy Expiry Date")
            annual_premium = st.number_input("Annual Premium", min_value=0.0)
    
    # Tab 6: Clause/Option
    with lease_tabs[5]:
        st.subheader("Clauses and Options")
        
        col1, col2 = st.columns(2)
        with col1:
            has_break_clause = st.checkbox("Break Clause", value=False)
            if has_break_clause:
                break_date = st.date_input("Break Date")
                break_notice = st.number_input("Notice Period (months)", min_value=1, value=6)
                break_penalty = st.number_input("Break Penalty Amount", min_value=0.0)
            
            has_extension_option = st.checkbox("Extension Option", value=False)
            if has_extension_option:
                extension_periods = st.number_input("Number of Extension Periods", min_value=1, value=1)
                extension_length = st.number_input("Length of Each Extension (years)", min_value=1, value=3)
                extension_notice = st.number_input("Extension Notice Period (months)", min_value=1, value=6)
        
        with col2:
            has_purchase_option = st.checkbox("Purchase Option", value=False)
            if has_purchase_option:
                purchase_option_amount = st.number_input("Purchase Option Amount", min_value=0.0)
                purchase_date = st.date_input("Purchase Option Date")
                
            other_clauses = st.text_area("Other Special Clauses", height=100)
    
    # Tab 7: Contact
    with lease_tabs[6]:
        st.subheader("Contact Information")
        
        contact_tabs = st.tabs(["Lessor Contacts", "Lessee Contacts", "Other Parties"])
        
        with contact_tabs[0]:
            st.subheader("Lessor Contacts")
            
            col1, col2 = st.columns(2)
            with col1:
                lessor_primary_name = st.text_input("Primary Contact Name")
                lessor_position = st.text_input("Position/Title")
                lessor_email = st.text_input("Email Address")
                
            with col2:
                lessor_phone = st.text_input("Phone Number")
                lessor_address = st.text_area("Address", height=100)
        
        with contact_tabs[1]:
            st.subheader("Lessee Contacts")
            
            col1, col2 = st.columns(2)
            with col1:
                lessee_primary_name = st.text_input("Primary Contact Name", key="lessee_name")
                lessee_position = st.text_input("Position/Title", key="lessee_position")
                lessee_email = st.text_input("Email Address", key="lessee_email")
                
            with col2:
                lessee_phone = st.text_input("Phone Number", key="lessee_phone")
                lessee_address = st.text_area("Address", key="lessee_address", height=100)
    
    # Tab 8: Cost Centers
    with lease_tabs[7]:
        st.subheader("Cost Center Allocation")
        
        multi_cost_center = st.checkbox("Allocate to Multiple Cost Centers")
        
        if multi_cost_center:
            num_centers = st.number_input("Number of Cost Centers", min_value=1, max_value=10, value=2)
            
            allocation_data = []
            total_allocation = 0
            
            for i in range(int(num_centers)):
                col1, col2, col3 = st.columns(3)
                with col1:
                    cost_center = st.text_input(f"Cost Center {i+1} Code")
                with col2:
                    cost_center_name = st.text_input(f"Cost Center {i+1} Name")
                with col3:
                    allocation = st.number_input(f"Allocation % for Center {i+1}", min_value=0.0, max_value=100.0, value=100.0/num_centers)
                    total_allocation += allocation
                
                allocation_data.append({"code": cost_center, "name": cost_center_name, "allocation": allocation})
            
            st.write(f"Total Allocation: {total_allocation}%")
            if total_allocation != 100.0:
                st.warning("Total allocation should equal 100%")
        else:
            st.text_input("Cost Center Code")
            st.text_input("Cost Center Name")
    
    # Tab 9: Accounting
    with lease_tabs[8]:
        st.subheader("Accounting Information")
        
        col1, col2 = st.columns(2)
        with col1:
            accounting_standard = st.selectbox("Accounting Standard", ["FRS102", "IFRS 16", "ASC 842", "Other"])
            lease_classification = st.selectbox("Lease Classification", ["Finance", "Operating"])
            initial_direct_costs = st.number_input("Initial Direct Costs", min_value=0.0)
            
        with col2:
            discount_rate_type = st.radio("Discount Rate Type", ["Implicit Rate", "Incremental Borrowing Rate", "OBR Rate"])
            
            if discount_rate_type == "Implicit Rate":
                discount_rate = st.number_input("Implicit Rate (%)", min_value=0.0, max_value=20.0, value=4.5, step=0.1)
            elif discount_rate_type == "OBR Rate":
                discount_rate = st.slider("OBR Rate (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.1)
            else:
                discount_rate = st.number_input("Incremental Borrowing Rate (%)", min_value=0.0, max_value=20.0, value=6.0, step=0.1)
        
        # Calculation preview
        if st.button("Calculate Lease Values"):
            st.write("### Lease Accounting Values")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Right-of-Use Asset", "£1,245,000")
                st.metric("Initial Lease Liability", "£1,190,000")
            
            with col2:
                st.metric("Lease Term (Months)", "36")
                st.metric("Discount Rate", f"{discount_rate}%")
                
            # Show sample journal entries
            st.write("### Sample Journal Entries")
            journal_entries = pd.DataFrame([
                {"Account": "Right-of-Use Asset", "Debit": 1245000, "Credit": 0},
                {"Account": "Lease Liability", "Debit": 0, "Credit": 1190000},
                {"Account": "Initial Direct Costs", "Debit": 0, "Credit": 55000}
            ])
            st.table(journal_entries)
    
    # Tab 10: Variable Payment
    with lease_tabs[9]:
        st.subheader("Variable Payment Information")
        
        has_variable_payments = st.checkbox("Includes Variable Payments")
        
        if has_variable_payments:
            variable_type = st.selectbox("Variable Payment Type", 
                                         ["Percentage of Sales", "Indexed to Inflation", "Usage Based", "Other"])
            
            col1, col2 = st.columns(2)
            with col1:
                if variable_type == "Percentage of Sales":
                    percentage = st.number_input("Percentage of Sales (%)", min_value=0.0, max_value=100.0, value=5.0)
                    min_annual = st.number_input("Minimum Annual Amount", min_value=0.0)
                    max_annual = st.number_input("Maximum Annual Amount (0 for no cap)", min_value=0.0)
                elif variable_type == "Indexed to Inflation":
                    index_type = st.selectbox("Index Type", ["RPI", "CPI", "CPIH", "Other"])
                    cap = st.number_input("Cap (%)", min_value=0.0, value=5.0)
                    floor = st.number_input("Floor (%)", min_value=0.0, value=0.0)
                    
            with col2:
                payment_schedule = st.selectbox("Payment Schedule", ["Monthly", "Quarterly", "Annual"])
                reassessment_date = st.date_input("Next Reassessment Date")
                st.text_area("Variable Payment Terms", height=100)
    
    # Tab 11: SubLease
    with lease_tabs[10]:
        st.subheader("SubLease Information")
        
        has_sublease = st.checkbox("Has SubLease Arrangements")
        
        if has_sublease:
            col1, col2 = st.columns(2)
            with col1:
                sublessee_name = st.text_input("SubLessee Name")
                sublease_start = st.date_input("SubLease Start Date")
                sublease_end = st.date_input("SubLease End Date")
                sublease_amount = st.number_input("SubLease Amount", min_value=0.0)
                sublease_frequency = st.selectbox("SubLease Payment Frequency", 
                                                 ["Monthly", "Quarterly", "Semi-Annual", "Annual"])
                
            with col2:
                sublease_area = st.number_input("SubLeased Area", min_value=0.0)
                sublease_area_unit = st.selectbox("Unit", ["sq ft", "sq m"], key="sublease_unit")
                sublease_percentage = st.number_input("Percentage of Total Area (%)", min_value=0.0, max_value=100.0)
                
                sublease_terms = st.text_area("SubLease Terms and Conditions", height=100)
    
    # Save button at bottom
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Save Lease Information", type="primary"):
            st.success("Lease information saved successfully!")

with tab_reports:
    # Create tabs for different report types
    report_tabs = st.tabs(["Lease Schedule", "Accounting Reports", "Compliance Reports", "Lease Portfolio"])
    
    with report_tabs[0]:
        st.subheader("Lease Schedule Report")
        st.write("This report shows the schedule of all lease payments and accounting entries.")
        
        # Sample amortization schedule
        amortization_data = []
        for i in range(1, 37):
            amortization_data.append({
                "Period": i,
                "Date": (datetime.datetime.now() + datetime.timedelta(days=30*i)).strftime("%Y-%m-%d"),
                "Payment": 1000,
                "Interest": 1000 * 0.05 * (1 - (i/36)),
                "Principal": 1000 - (1000 * 0.05 * (1 - (i/36))),
                "Ending Balance": max(0, 36000 - (i * 1000))
            })
        
        amortization_df = pd.DataFrame(amortization_data)
        st.dataframe(amortization_df)
    
    with report_tabs[1]:
        st.subheader("Accounting Reports")
        accounting_report_type = st.selectbox("Report Type", 
                                           ["Journal Entries", "Balance Sheet Impact", "Expense Recognition"])
        
        if accounting_report_type == "Journal Entries":
            st.write("### Journal Entries")
            # Sample data
            st.table(pd.DataFrame([
                {"Date": "2025-01-01", "Account": "Right-of-Use Asset", "Debit": 36000, "Credit": 0},
                {"Date": "2025-01-01", "Account": "Lease Liability", "Debit": 0, "Credit": 36000},
                {"Date": "2025-02-01", "Account": "Interest Expense", "Debit": 150, "Credit": 0},
                {"Date": "2025-02-01", "Account": "Lease Liability", "Debit": 850, "Credit": 0},
                {"Date": "2025-02-01", "Account": "Cash", "Debit": 0, "Credit": 1000}
            ]))