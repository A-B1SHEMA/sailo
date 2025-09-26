import streamlit as st
import pandas as pd
import numpy as np

# ----------------------------
# Sample Data & Forecast Logic
# ----------------------------
target_goal = 10000
main_forecast = [2000, 4000, 6000, 8500, 10500]

formatted_balance = f"{main_forecast[-1]:,.2f}"
formatted_goal = f"{target_goal:,.2f}"
progress = main_forecast[-1] / target_goal

# ----------------------------
# Streamlit App Layout
# ----------------------------
st.set_page_config(page_title="💰 Savings DSS", layout="wide")
st.title("💰 Smart Savings Decision Support System")

# Tabs
tab1, tab2, tab3 = st.tabs(["Forecast", "Quick What-If", "Personalized Recommendation"])

# ----------------------------
# Tab 1: Forecast
# ----------------------------
with tab1:
    st.header("📈 Forecast")
    df = pd.DataFrame({
        "Period": list(range(1, len(main_forecast)+1)),
        "Projected Balance": main_forecast
    }).set_index("Period")
    st.line_chart(df)

# ----------------------------
# Tab 2: Quick What-If Scenario
# ----------------------------
with tab2:
    st.header("🔍 Quick What-If Scenario")
    multiplier = st.slider("Adjust Forecast Multiplier", 0.5, 1.5, 1.0)
    scenario_forecast = [x * multiplier for x in main_forecast]
    df_scenario = pd.DataFrame({
        "Period": list(range(1, len(scenario_forecast)+1)),
        "Projected Balance": scenario_forecast
    }).set_index("Period")
    st.line_chart(df_scenario)

# ----------------------------
# Tab 3: Personalized Recommendation
# ----------------------------
with tab3:
    st.header("💡 Recommendations")
    if progress >= 1.0:
        st.success(f"🎉 Excellent! Your projected balance (${formatted_balance}) meets or exceeds your goal of ${formatted_goal}.")
    elif progress >= 0.5:
        st.warning(f"Your projected balance is ${formatted_balance}, which is {progress*100:.1f}% of your goal (${formatted_goal}). Keep going!")
    else:
        st.error(f"Your projected balance is ${formatted_balance}, which is only {progress*100:.1f}% of your goal (${formatted_goal}). Consider adjusting your plan.")

    st.subheader("📈 Progress toward your goal")
    st.progress(min(progress, 1.0))


