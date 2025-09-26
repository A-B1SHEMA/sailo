import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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
    for m in range(months):
        balance += monthly_contribution
        balance *= (1 + annual_return / 12)
        history.append(balance)
    return history

def generate_actionable_suggestions(starting_balance, monthly_contribution, annual_return, target_goal, months):
    forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)
    final_balance = forecast[-1]
    shortfall = target_goal - final_balance
    suggestions = []

    # 1️⃣ Contribution Adjustments
    if shortfall > 0:
        required_monthly = (target_goal - starting_balance * (1 + annual_return/12)**months) / months
        suggestions.append(f"Increase contribution to ${required_monthly:,.2f} per month to meet your goal in {months} months.")
    else:
        suggestions.append("Your current plan meets or exceeds your goal. Consider keeping your contribution stable or adjusting for other goals.")

    # 2️⃣ Timeline Adjustments
    if shortfall > 0:
        reduced_months = months
        while simulate_savings(starting_balance, monthly_contribution, annual_return, reduced_months)[-1] < target_goal:
            reduced_months += 1
        suggestions.append(f"Extend your timeline to {reduced_months} months to reach your goal with current contributions.")

    # 3️⃣ Shortfall/Surplus
    if shortfall > 0:
        suggestions.append(f"You are short by ${shortfall:,.2f}. Consider adjusting contributions or timeline.")
    else:
        suggestions.append(f"You have a surplus of ${-shortfall:,.2f}. You can save less or allocate extra to other goals.")

    # 5️⃣ Milestone Suggestions
    milestones = [0.25, 0.5, 0.75, 1.0]
    for milestone in milestones:
        milestone_balance = target_goal * milestone
        month_reached = next((i+1 for i, b in enumerate(forecast) if b >= milestone_balance), None)
        if month_reached:
            suggestions.append(f"Milestone {int(milestone*100)}% of your goal (${milestone_balance:,.2f}) will be reached in month {month_reached}.")

    return suggestions

# ----------------------------
# Streamlit Layout
# ----------------------------
st.set_page_config(page_title="Sailo DSS", layout="wide")
st.title("💰 Sailo Decision Support System")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Inputs",
    "2️⃣ What You Can Do",
    "3️⃣ Forecast",
    "4️⃣ What-If Scenario"
])

# ----------------------------
# Default Input Values
# ----------------------------
starting_balance = 2000.0
monthly_contribution = 500.0
annual_return = 0.05
target_goal = 10000.0
months = 12

# ----------------------------
# Tab 1: Inputs
# ----------------------------
with tab1:
    st.header("🔧 Inputs")
    starting_balance = st.number_input("Starting Balance ($)", min_value=0.0, value=starting_balance)
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=monthly_contribution)
    annual_return = st.slider("Expected Annual Return (%)", 0.0, 20.0, int(annual_return*100)) / 100
    target_goal = st.number_input("Target Goal ($)", min_value=1000.0, value=target_goal)
    months = st.number_input("Time Horizon (months)", min_value=1, value=months)

# ----------------------------
# Tab 2: What You Can Do
# ----------------------------
with tab2:
    st.header("💡 What You Can Do")
    suggestions = generate_actionable_suggestions(starting_balance, monthly_contribution, annual_return, target_goal, months)
    for s in suggestions:
        st.markdown(f"- {s}")

# ----------------------------
# Tab 3: Forecast
# ----------------------------
with tab3:
    st.header("📈 Forecast")
    forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)
    df_forecast = pd.DataFrame({
        "Month": list(range(1, months+1)),
        "Projected Balance": forecast
    }).set_index("Month")
    st.line_chart(df_forecast)

# Progress Bar
    progress = forecast[-1]/target_goal
    st.subheader("📊 Progress Toward Your Goal")
    st.progress(min(progress, 1.0))
    st.write(f"Projected Balance: ${forecast[-1]:,.2f} / Goal: ${target_goal:,.2f} ({progress*100:.1f}%)")

# ----------------------------
# Tab 4: What-If Scenario
# ----------------------------
with tab4:
    st.header("🔍 What-If Scenarios")
    multiplier = st.slider("Adjust Forecast Multiplier", 0.5, 1.5, 1.0)
    scenario_forecast = [x * multiplier for x in forecast]
    df_scenario = pd.DataFrame({
        "Month": list(range(1, months+1)),
        "Projected Balance": scenario_forecast
    }).set_index("Month")
    st.line_chart(df_scenario)

