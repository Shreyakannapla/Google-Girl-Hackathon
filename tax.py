import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import sqlite3
from fpdf import FPDF

# Streamlit UI
st.set_page_config(page_title="AI Tax Assistant", page_icon="💰", layout="wide")

# Sidebar Navigation
st.sidebar.title("💰 AI-Powered Tax Assistant")
option = st.sidebar.radio("Choose an Option", ["Calculate Tax", "OCR Invoice Scanner"])

# Database Connection
conn = sqlite3.connect('tax_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tax_history (name TEXT, income INTEGER, deductions INTEGER, tax INTEGER)''')
conn.commit()

# Tax Calculator
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

if option == "Calculate Tax":
    st.title("📊 Income Tax Calculator")
    
    income = st.number_input("Enter Your Annual Income (₹)", min_value=0, step=1000)
    investments = st.number_input("Investments (₹)", min_value=0, step=1000)
    other_deductions = st.number_input("Other Deductions (₹)", min_value=0, step=1000)
    
    if st.button("Calculate Tax"):
        taxable_income = max(0, income - (investments + other_deductions))  # Ensure it's non-negative

        # Old Regime Tax Calculation
        if taxable_income <= 250000:
            tax_old = 0
        elif taxable_income <= 500000:
            tax_old = (taxable_income - 250000) * 0.05
        elif taxable_income <= 1000000:
            tax_old = (taxable_income - 500000) * 0.2 + 12500
        else:
            tax_old = (taxable_income - 1000000) * 0.3 + 112500

        # New Regime Tax Calculation
        tax_new = calculate_tax_new_regime(taxable_income)

        # 🔍 Debug Statements
        st.write(f"**Debug Info:**")
        st.write(f"Taxable Income: ₹{taxable_income:,.2f}")
        st.write(f"Tax (Old Regime): ₹{tax_old:,.2f}")
        st.write(f"Tax (New Regime): ₹{tax_new:,.2f}")

        best_option = "Old Regime" if tax_old < tax_new else "New Regime"

        st.write(f"📌 **Tax Under Old Regime:** ₹ {tax_old:,.2f}")
        st.write(f"📌 **Tax Under New Regime:** ₹ {tax_new:,.2f}")
        st.success(f"💡 Best Option for You: **{best_option}** (Lower tax)")

        st.session_state["final_tax"] = min(tax_old, tax_new)

# OCR Invoice Scanner
elif option == "OCR Invoice Scanner":
    st.title("📝 Upload Invoice / Salary Slip for Tax Extraction")
    uploaded_file = st.file_uploader("Upload an image or PDF", type=["png", "jpg", "jpeg", "pdf"])
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            images = convert_from_path(uploaded_file)
            img = images[0]
        else:
            img = Image.open(uploaded_file)

        st.image(img, caption="Uploaded File", use_column_width=True)
        text = pytesseract.image_to_string(img)
        st.subheader("Extracted Text:")
        st.write(text)
        
        extracted_amounts = [int(s) for s in text.split() if s.isdigit()]
        if extracted_amounts:
            estimated_income = max(extracted_amounts)
            st.success(f"Estimated Income from Document: ₹ {estimated_income:,.2f}")
