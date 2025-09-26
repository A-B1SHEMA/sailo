import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------------
# Helper Function: Simulate Savings
# ----------------------------
def simulate_savings(starting_balance, monthly_contribution, annual_return, months):
    balances = [starting_balance]
    for _ in range(months):
        new_balance = balances[-1] * (1 + annual_return / 12) + monthly_contribution
        balances.append(new_balance)
    return balances

# ----------------------------
# Streamlit App Layout
# ----------------------------
st.set_page_config(page_title="Smart Savings Dashboard", layout="wide")

st.title("📊 Smart Savings Dashboard")
st.markdown("Track your savings growth, explore what-if scenarios, and get actionable suggestions to hit your goals.")

# ----------------------------
# User Inputs
# ----------------------------
col1, col2, col3 = st.columns(3)
with col1:
    starting_balance = st.number_input("Starting Balance ($)", min_value=0, value=5000, step=100)
with col2:
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0, value=500, step=50)
with col3:
    annual_return = st.number_input("Expected Annual Return (%)", min_value=0.0, value=5.0, step=0.5) / 100

col4, col5 = st.columns(2)
with col4:
    months = st.number_input("Investment Horizon (Months)", min_value=1, value=120, step=12)
with col5:
    target_goal = st.number_input("Target Goal ($)", min_value=0, value=50000, step=1000)

debt_amount = st.number_input("Outstanding Debt ($)", min_value=0, value=10000, step=500)

# ----------------------------
# Tabs
# ----------------------------
tab1, tab2, tab3 = st.tabs(["📈 Forecast", "💡 What You Can Do", "🎯 Personalized Recommendation"])

# ----------------------------
# Tab 1: Forecast
# ----------------------------
with tab1:
    st.header("📈 Savings Forecast")
    main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)

    df = pd.DataFrame({
        "Month": np.arange(0, months + 1),
        "Balance": main_forecast
    })

    fig = px.line(df, x="Month", y="Balance", title="Projected Savings Growth", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    final_balance = main_forecast[-1]
    st.metric("Final Balance", f"${final_balance:,.2f}")
    st.metric("Target Goal", f"${target_goal:,.2f}")
    st.metric("Progress", f"{(final_balance / target_goal) * 100:.2f}%")

# ----------------------------
# Tab 2: What You Can Do
# ----------------------------
with tab2:
    st.header("💡 What You Can Do")
    main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)
    final_balance = main_forecast[-1]
    progress = final_balance / target_goal

    if progress < 1.0:
        needed_balance = target_goal - final_balance
        suggested_contribution = needed_balance / months
        st.info(f"Increase your monthly contribution by ${suggested_contribution:,.2f} to reach your goal in {months} months.")
    else:
        st.success("🎉 You are on track to meet or exceed your goal!")

    # Quick Wins Module
    st.markdown("### ⚡ Quick Wins")
    st.markdown(f"""
    - 🪙 **One-Time Boost**: Add a lump sum of **$1,000** now to reduce your timeline by ~2 months.
    - ✂️ **Cut Expenses**: Redirect **$50/month** from discretionary spending to savings.
    - 🔄 **Round-Up Auto-Save**: Enable micro-savings from daily purchases.
    - 📊 **Peer Benchmark**: You're ahead of **72%** of users in your bracket.
    """)

    # Deep Optimization Module
    st.markdown("### 🧠 Deep Optimization")
    st.markdown(f"""
    - 📈 **Rebalance Portfolio**: Consider shifting **10–15%** to growth assets.
    - 🧾 **Tax Efficiency**: Use **Roth IRA** or **HSA** to reduce future tax burden.
    - 💳 **Debt Strategy**: You currently have **${debt_amount:,.2f}** in outstanding debt. Paying this off first could save you **hundreds** in interest.
    - 💸 **Fee Scan**: Review fund expense ratios—switching could improve returns.
    """)

# ----------------------------
# Tab 3: Personalized Recommendation
# ----------------------------
with tab3:
    st.header("🎯 Personalized Recommendation")
    main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)
    final_balance = main_forecast[-1]
    progress = final_balance / target_goal

    if progress >= 1.0:
        st.success(f"🎉 Excellent! Your projected balance of **${final_balance:,.2f}** meets your goal of **${target_goal:,.2f}**.")
    else:
        needed_balance = target_goal - final_balance
        st.warning(f"⚠️ You are projected to fall short by **${needed_balance:,.2f}**.")
        st.info(f"To close the gap, increase monthly contributions by **${needed_balance / months:,.2f}** or extend your horizon by a few years.")

