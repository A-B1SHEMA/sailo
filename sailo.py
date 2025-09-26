import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
        # Pay debt first
        if debt_balance > 0:
            interest = debt_balance * debt_apr / 12
            debt_balance = max(debt_balance + interest - (min_payment + extra_cash), 0)
        balances.append(debt_balance)
    return balances

# ----------------------------
# Streamlit App Layout
# ----------------------------
st.set_page_config(page_title="Smart Savings Dashboard", layout="wide")
st.title("📊 Smart Savings Dashboard")
st.markdown("Plan, optimize, and accelerate your savings goals with debt & investment insights.")

# ----------------------------
# Sidebar Inputs
# ----------------------------
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
# Tabs
# ----------------------------
tab1, tab2 = st.tabs(["💡 Dashboard", "🎯 Personalized Recommendation"])

# ----------------------------
# Tab 1: Dashboard
# ----------------------------
with tab1:
    st.header("📊 Savings & Debt Dashboard")

    # Forecast savings
    main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)

    # Debt payoff simulation
    debt_forecast = simulate_debt_payoff(debt_amount, min_debt_payment, extra_cash, debt_apr, months)

    # Extra cash invested scenario
    invest_forecast = simulate_savings(starting_balance, monthly_contribution + extra_cash, annual_return, months)

    # Prepare comparison DataFrame
    df_compare = pd.DataFrame({
        "Month": range(months),
        "Debt Remaining": debt_forecast,
        "Invest Extra": invest_forecast[1:]  # skip month 0 to align lengths
    })

    # Find debt-free milestone
    debt_free_month = next((i for i, v in enumerate(debt_forecast) if v <= 0), months)

    # Plot Debt vs Invest comparison chart with debt-free marker
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_compare["Month"], y=df_compare["Debt Remaining"],
                             mode='lines', name='Debt Remaining', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df_compare["Month"], y=df_compare["Invest Extra"],
                             mode='lines', name='Invest Extra', line=dict(color='green')))

    # Add vertical line for debt-free milestone
    fig.add_vline(x=debt_free_month, line_dash="dash", line_color="blue",
                  annotation_text="Debt-Free", annotation_position="top right")

    fig.update_layout(title="Debt vs Invest Comparison",
                      xaxis_title="Month",
                      yaxis_title="Amount ($)",
                      template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # Quick Wins & Deep Optimization
    # ----------------------------
    st.subheader("⚡ Quick Wins")
    st.markdown("""
    - 🪙 **One-Time Boost**: Add a lump sum now to reduce timeline.
    - ✂️ **Cut Expenses**: Redirect discretionary spending to savings.
    - 🔄 **Round-Up Auto-Save**: Enable micro-savings from daily purchases.
    - 📊 **Peer Benchmark**: Track progress relative to similar users.
    """)

    st.subheader("🧠 Deep Optimization")
    st.markdown(f"""
    - 📈 **Rebalance Portfolio**: Shift 10–15% to growth assets.
    - 🧾 **Tax Efficiency**: Use Roth IRA/HSA for future tax savings.
    - 💳 **Debt Strategy**: Current debt: **${debt_amount:,.2f}**, min payment: **${min_debt_payment:,.2f}/month**, APR: **{debt_apr*100:.1f}%**
    - 💸 **Fee Scan**: Review investment fees to improve returns.
    """)

    # Debt metrics
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
    st.header("🎯 Personalized Recommendation")
    final_balance = main_forecast[-1]
    progress = final_balance / target_goal

    if progress >= 1.0:
        st.success(f"🎉 Your projected balance **${final_balance:,.2f}** meets your goal of **${target_goal:,.2f}**.")
    else:
        deficit = target_goal - final_balance
        st.warning(f"⚠️ You are projected to fall short by **${deficit:,.2f}**.")
        st.info(f"Increase monthly contribution by **${deficit/months:,.2f}** or extend your investment horizon.")
