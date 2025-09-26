import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

# ----------------------------
# Helper Functions
# ----------------------------
def simulate_savings(starting_balance, monthly_contribution, annual_return, months):
    balances = [starting_balance]
    for _ in range(months):
        new_balance = balances[-1] * (1 + annual_return / 12) + monthly_contribution
        balances.append(new_balance)
    return balances

def simulate_debt_payoff(debt_amount, min_payment, extra_cash, debt_apr, months):
    balances = []
    debt_balance = debt_amount
    for month in range(months):
        if debt_balance > 0:
            interest = debt_balance * debt_apr / 12
            debt_balance = max(debt_balance + interest - (min_payment + extra_cash), 0)
        balances.append(debt_balance)
    return balances

def generate_pdf_report(main_forecast, target_goal, debt_amount, min_debt_payment, debt_apr, extra_cash, months, monthly_contribution):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("💰 Sailo Decision Support Report", styles["Title"]))
    story.append(Spacer(1, 12))

    # Personalized Recommendation Metrics
    final_balance = main_forecast[-1]
    progress = final_balance / target_goal
    deficit_or_surplus = final_balance - target_goal
    debt_to_asset_ratio = debt_amount / final_balance if final_balance > 0 else 0

    story.append(Paragraph("🎯 Personalized Recommendation", styles["Heading2"]))
    story.append(Paragraph(f"Projected Balance: ${final_balance:,.2f}", styles["Normal"]))
    story.append(Paragraph(f"Target Goal: ${target_goal:,.2f}", styles["Normal"]))
    story.append(Paragraph(f"Goal Achievement: {progress*100:.1f}%", styles["Normal"]))
    story.append(Paragraph(f"Deficit/Surplus: ${deficit_or_surplus:,.2f}", styles["Normal"]))
    story.append(Paragraph(f"Debt-to-Asset Ratio: {debt_to_asset_ratio*100:.1f}%", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Debt Metrics
    debt_forecast = simulate_debt_payoff(debt_amount, min_debt_payment, extra_cash, debt_apr, months)
    debt_free_month = next((i for i, v in enumerate(debt_forecast) if v <= 0), months)
    total_interest = sum([debt_forecast[i] * debt_apr / 12 for i in range(debt_free_month)])
    story.append(Paragraph("💳 Debt Metrics & Payoff Simulation", styles["Heading2"]))
    story.append(Paragraph(f"Estimated months to debt-free: {debt_free_month}", styles["Normal"]))
    story.append(Paragraph(f"Estimated interest paid: ${total_interest:,.2f}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Quick Wins & Deep Optimization
    story.append(Paragraph("⚡ Quick Wins", styles["Heading2"]))
    story.append(Paragraph("- Add a one-time boost to reduce timeline", styles["Normal"]))
    story.append(Paragraph("- Cut expenses and redirect to savings", styles["Normal"]))
    story.append(Paragraph("- Enable micro-savings (round-ups)", styles["Normal"]))
    story.append(Paragraph("- Track progress vs peers", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("🧠 Deep Optimization", styles["Heading2"]))
    story.append(Paragraph("- Rebalance portfolio (10–15% to growth assets)", styles["Normal"]))
    story.append(Paragraph("- Use Roth IRA/HSA for tax efficiency", styles["Normal"]))
    story.append(Paragraph(f"- Debt Strategy: Current debt ${debt_amount:,.2f}, min payment ${min_debt_payment:,.2f}/month, APR {debt_apr*100:.1f}%", styles["Normal"]))
    story.append(Paragraph("- Review fund expense ratios for better returns", styles["Normal"]))
    story.append(Spacer(1, 12))

    # What-If Scenario
    story.append(Paragraph("🔮 What-If Analysis", styles["Heading2"]))
    story.append(Paragraph(f"Extra ${extra_cash}/month could improve goal achievement.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ----------------------------
# Streamlit App Layout
# ----------------------------
st.set_page_config(page_title="💰 Sailo", layout="wide")

# ----------------------------
# Sidebar Inputs with Logo
# ----------------------------
st.sidebar.image("logo.png", width=120)  # Sidebar logo
st.sidebar.header("Your Inputs")
starting_balance = st.sidebar.number_input("Starting Balance ($)", value=5000, step=500)
monthly_contribution = st.sidebar.number_input("Monthly Contribution ($)", value=500, step=50)
annual_return = st.sidebar.number_input("Expected Annual Return (%)", value=5.0, step=0.5) / 100
months = st.sidebar.number_input("Investment Horizon (Months)", value=120, step=12)
target_goal = st.sidebar.number_input("Target Goal ($)", value=50000, step=1000)

st.sidebar.subheader("Debt Information")
debt_amount = st.sidebar.number_input("Debt Balance ($)", value=10000, step=500)
debt_apr = st.sidebar.number_input("Debt APR (%)", value=18.0, step=0.5) / 100
min_debt_payment = st.sidebar.number_input("Minimum Monthly Debt Payment ($)", value=200, step=50)
extra_cash = st.sidebar.number_input("Extra Cash Available ($/month)", value=100, step=50)

# ----------------------------
# Main page logo and title
# ----------------------------
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo.png", width=100)  # Main page logo
with col2:
    st.markdown("<h1>💰 Sailo Decision Support System</h1>", unsafe_allow_html=True)
    st.markdown("Plan, optimize, and accelerate your savings goals with debt & investment insights.")

# ----------------------------
# Tabs
# ----------------------------
tab1, tab2 = st.tabs(["💡 Dashboard", "🎯 Personalized Recommendation"])

# ----------------------------
# Tab 1: Dashboard
# ----------------------------
with tab1:
    st.header("📊 Sailo Dashboard")
    main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)
    debt_forecast = simulate_debt_payoff(debt_amount, min_debt_payment, extra_cash, debt_apr, months)
    invest_forecast = simulate_savings(starting_balance, monthly_contribution + extra_cash, annual_return, months)

    df_compare = pd.DataFrame({
        "Month": range(months),
        "Debt Remaining": debt_forecast,
        "Invest Extra": invest_forecast[1:]
    })

    debt_free_month = next((i for i, v in enumerate(debt_forecast) if v <= 0), months)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_compare["Month"], y=df_compare["Debt Remaining"],
                             mode='lines', name='Debt Remaining', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df_compare["Month"], y=df_compare["Invest Extra"],
                             mode='lines', name='Invest Extra', line=dict(color='green')))
    fig.add_vline(x=debt_free_month, line_dash="dash", line_color="blue",
                  annotation_text="Debt-Free", annotation_position="top right")
    fig.update_layout(title="Debt vs Invest Comparison",
                      xaxis_title="Month",
                      yaxis_title="Amount ($)",
                      template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⚡ Quick Wins")
    st.markdown("""
    - 🪙 One-Time Boost
    - ✂️ Cut Expenses
    - 🔄 Round-Up Auto-Save
    - 📊 Peer Benchmark
    """)

    st.subheader("🧠 Deep Optimization")
    st.markdown(f"""
    - 📈 Rebalance Portfolio
    - 🧾 Tax Efficiency (Roth IRA/HSA)
    - 💳 Debt Strategy: Current debt ${debt_amount:,.2f}, min payment ${min_debt_payment:,.2f}/month, APR {debt_apr*100:.1f}%
    - 💸 Fee Scan
    """)

    months_to_payoff = debt_free_month
    total_interest = sum([debt_forecast[i] * debt_apr / 12 for i in range(months_to_payoff)])
    st.subheader("💳 Debt Metrics & Payoff Simulation")
    st.markdown(f"""
    - Estimated months to debt-free: **{months_to_payoff} months**
    - Estimated interest paid: **${total_interest:,.2f}**
    """)

# ----------------------------
# Tab 2: Personalized Recommendation
# ----------------------------
with tab2:
    st.header("🎯 Sailo Personalized Recommendation & Analytics")
    final_balance = main_forecast[-1]
    total_contributions = monthly_contribution * months + starting_balance
    total_interest = final_balance - total_contributions
    progress = final_balance / target_goal
    deficit_or_surplus = final_balance - target_goal
    debt_to_asset_ratio = debt_amount / final_balance if final_balance > 0 else 0

    month_counter = 0
    balance_sim = starting_balance
    while balance_sim < target_goal and month_counter < 600:
        balance_sim = balance_sim * (1 + annual_return / 12) + monthly_contribution
        month_counter += 1
    months_to_goal_current = month_counter

    month_counter_extra = 0
    balance_sim_extra = starting_balance
    while balance_sim_extra < target_goal and month_counter_extra < 600:
        balance_sim_extra = balance_sim_extra * (1 + annual_return / 12) + monthly_contribution + extra_cash
        month_counter_extra += 1
    months_to_goal_extra = month_counter_extra

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Projected Balance", f"${final_balance:,.2f}")
    col2.metric("Goal Progress", f"{progress*100:.1f}%")
    col3.metric("Deficit/Surplus", f"${deficit_or_surplus:,.2f}")
    col4.metric("Debt-to-Asset Ratio", f"{debt_to_asset_ratio*100:.1f}%")
    col5.metric("Months to Goal", f"{months_to_goal_current} (current)")

    st.subheader("🔮 What-If: Extra Contributions")
    st.info(f"Adding extra ${extra_cash}/month could reach your goal in **{months_to_goal_extra} months** instead of {months_to_goal_current} months.")

    st.subheader("💹 Contributions vs Interest")
    df_analytics = pd.DataFrame({
        "Type": ["Contributions", "Interest Earned"],
        "Amount": [total_contributions, total_interest]
    })
    fig_analytics = px.bar(df_analytics, x="Type", y="Amount", text="Amount",
                           color="Type", color_discrete_map={"Contributions":"blue", "Interest Earned":"green"})
    st.plotly_chart(fig_analytics, use_container_width=True)

    if st.button("📄 Download PDF Report"):
        pdf_buffer = generate_pdf_report(main_forecast, target_goal, debt_amount, min_debt_payment, debt_apr, extra_cash, months, monthly_contribution)
        st.download_button("Download Sailo Report", data=pdf_buffer, file_name="Sailo_Report.pdf", mime="application/pdf")
