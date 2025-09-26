import streamlit as st
import pandas as pd
import numpy as np
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ----------------------------
# Utility Functions
# ----------------------------
def simulate_savings(starting_balance, monthly_contribution, annual_return, months):
    balance = starting_balance
    history = []
    for _ in range(months):
        balance += monthly_contribution
        balance *= (1 + annual_return / 12)
        history.append(balance)
    return history

def actionable_suggestions(starting_balance, monthly_contribution, annual_return, target_goal, months):
    """Generate suggestions for 1,2,3,5 features"""
    forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)
    final_balance = forecast[-1]
    suggestions = []

    # 1️⃣ Contribution adjustment
    if final_balance < target_goal:
        required_contribution = (target_goal / ((1 + annual_return / 12) ** months) - starting_balance) * (12 / months)
        suggestions.append(f"Increase monthly contribution to ${required_contribution:,.2f} to reach your goal.")

    # 2️⃣ Timeline adjustment
    elif final_balance > target_goal:
        extra_months = 0
        temp_balance = starting_balance
        while temp_balance < target_goal:
            temp_balance += monthly_contribution
            temp_balance *= (1 + annual_return / 12)
            extra_months += 1
        suggestions.append(f"You can reach your goal in {extra_months} months with current plan.")

    # 3️⃣ Shortfall/Surplus
    difference = final_balance - target_goal
    if difference < 0:
        suggestions.append(f"You are short by ${abs(difference):,.2f} at the end of the period.")
    else:
        suggestions.append(f"You will have a surplus of ${difference:,.2f} at the end of the period.")

    # 5️⃣ Milestones
    milestones = [0.25, 0.5, 0.75, 1.0]
    milestone_texts = []
    for m in milestones:
        target = target_goal * m
        achieved = next((i+1 for i, b in enumerate(forecast) if b >= target), None)
        if achieved:
            milestone_texts.append(f"Reach {int(m*100)}% of your goal by month {achieved}")
    suggestions.append(" • ".join(milestone_texts))

    return suggestions

# ----------------------------
# Streamlit Layout
# ----------------------------
st.set_page_config(page_title="💰 Sailo DSS", layout="wide")
st.title("💰 Sailo Decision Support System")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Inputs",
    "2️⃣ Forecast",
    "3️⃣ What-If Scenario",
    "4️⃣ What You Can Do"
])

# ----------------------------
# Tab 1: Inputs
# ----------------------------
with tab1:
    st.header("Input your financial plan")
    starting_balance = st.number_input("Starting Balance ($)", min_value=0.0, value=2000.0)
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=500.0)
    annual_return = st.slider("Expected Annual Return (%)", 0.0, 20.0, 5.0) / 100
    target_goal = st.number_input("Target Goal ($)", min_value=1000.0, value=10000.0)
    months = st.number_input("Time Horizon (Months)", min_value=1, value=12)

# ----------------------------
# Tab 2: Forecast
