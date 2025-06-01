import streamlit as st
import sqlite3
import pandas as pd

# Streamlit Page Config
st.set_page_config(page_title="Income Tax Assistant", page_icon="💰", layout="centered")

# Database Connection
conn = sqlite3.connect('tax_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tax_history (
    name TEXT,
    income INTEGER,
    deductions INTEGER,
    tax INTEGER
)''')
conn.commit()

# Tax Calculation Function (New Regime)
def calculate_tax_new_regime(taxable_income):
    if taxable_income <= 250000:
        return 0
    elif taxable_income <= 500000:
        return (taxable_income - 250000) * 0.05
    elif taxable_income <= 750000:
        return (taxable_income - 500000) * 0.1 + 12500
    elif taxable_income <= 1000000:
        return (taxable_income - 750000) * 0.15 + 37500
    elif taxable_income <= 1250000:
        return (taxable_income - 1000000) * 0.2 + 75000
    elif taxable_income <= 1500000:
        return (taxable_income - 1250000) * 0.25 + 125000
    else:
        return (taxable_income - 1500000) * 0.3 + 187500

# Sidebar Navigation
option = st.sidebar.selectbox("Navigate", ["Calculate Tax", "View Saved Records", "About"])

# 📊 Tax Calculator
if option == "Calculate Tax":
    st.title("📊 Income Tax Calculator")

    name = st.text_input("Enter Your Name")
    income = st.number_input("Annual Income (₹)", min_value=0, step=1000)
    investments = st.number_input("Investments (₹)", min_value=0, step=1000)
    other_deductions = st.number_input("Other Deductions (₹)", min_value=0, step=1000)

    if st.button("Calculate Tax"):
        taxable_income = max(0, income - (investments + other_deductions))

        # Old Regime Calculation
        if taxable_income <= 250000:
            tax_old = 0
        elif taxable_income <= 500000:
            tax_old = (taxable_income - 250000) * 0.05
        elif taxable_income <= 1000000:
            tax_old = (taxable_income - 500000) * 0.2 + 12500
        else:
            tax_old = (taxable_income - 1000000) * 0.3 + 112500

        # New Regime Calculation
        tax_new = calculate_tax_new_regime(taxable_income)
        best_option = "Old Regime" if tax_old < tax_new else "New Regime"
        final_tax = min(tax_old, tax_new)

        st.write(f"📌 **Taxable Income:** ₹{taxable_income:,.2f}")
        st.write(f"💼 **Old Regime Tax:** ₹{tax_old:,.2f}")
        st.write(f"🆕 **New Regime Tax:** ₹{tax_new:,.2f}")
        st.success(f"✅ Best Option: **{best_option}** — ₹{final_tax:,.2f}")

        if name:
            c.execute("INSERT INTO tax_history (name, income, deductions, tax) VALUES (?, ?, ?, ?)",
                      (name, income, investments + other_deductions, final_tax))
            conn.commit()
            st.info("🗂️ Tax record saved.")
        else:
            st.warning("Please enter your name to save the record.")

# 📋 View Records
elif option == "View Saved Records":
    st.title("📋 Saved Tax Records")
    df = pd.read_sql_query("SELECT rowid AS ID, name, income, deductions, tax FROM tax_history", conn)
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No records found.")

# ℹ️ About Page
elif option == "About":
    st.title("ℹ️ About Tax Calculation")

    st.markdown("""
    ### 🧾 How Tax is Calculated:
    
    This app calculates tax based on **two regimes**:
    
    ---
    #### 🧮 **Old Tax Regime** (With Deductions):
    - Basic Exemption: ₹2,50,000
    - 5% tax on income from ₹2.5L to ₹5L  
    - 20% tax on income from ₹5L to ₹10L  
    - 30% tax on income above ₹10L  
    - Allows deductions like:
        - **Section 80C**: up to ₹1.5L (e.g., LIC, PPF, ELSS, etc.)
        - **Section 80D**: Medical insurance
        - **Standard Deduction**: ₹50,000 for salaried individuals

    ---
    #### 🆕 **New Tax Regime** (Without Deductions):
    | Income Slab (₹) | Tax Rate |
    |-----------------|----------|
    | 0 – 2.5 L       | 0%       |
    | 2.5 – 5 L       | 5%       |
    | 5 – 7.5 L       | 10%      |
    | 7.5 – 10 L      | 15%      |
    | 10 – 12.5 L     | 20%      |
    | 12.5 – 15 L     | 25%      |
    | Above 15 L      | 30%      |

    ---
    The app calculates taxes under both regimes and suggests the better one for you automatically.
    """)

    st.info("💡 Tip: Use the calculator to compare regimes based on your deductions.")
