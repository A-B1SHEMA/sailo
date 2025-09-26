import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

# ----------------------------
# Utility Functions
# ----------------------------
def simulate_savings(starting_balance, monthly_contribution, annual_return, months):
    """Simple compound growth simulation"""
    balance = starting_balance
    history = []
    for m in range(months):
        balance += monthly_contribution
        balance *= (1 + annual_return / 12)
        history.append(balance)
    return history

def generate_pdf_report(main_forecast, target_goal, progress, scenario_results, scenario_inputs):
    """Generate PDF report with results"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("💰 Savings Decision Support Report", styles["Title"]))
    story.append(Spacer(1, 12))

    # Personalized Recommendation
    story.append(Paragraph("Personalized Recommendation", styles["Heading2"]))
    final_balance = main_forecast[-1]
    story.append(Paragraph(f"Final Balance: ${final_balance:,.2f}", styles["Normal"]))
    story.append(Paragraph(f"Target Goal: ${target_goal:,.2f}", styles["Normal"]))
    story.append(Paragraph(f"Goal Achievement: {progress*100:.1f}%", styles["Normal"]))
    story.append(Spacer(1, 12))

    # What-If Scenarios
    story.append(Paragraph("What-If Scenarios", styles["Heading2"]))
    table_data = [["Scenario", "Final Balance", "Target Goal", "Achievement %"]]
    for scenario in scenario_results:
        target_goal = scenario_inputs[int(scenario["Scenario"][-1]) - 1]["TargetGoal"]
        progress = scenario["FinalBalance"] / target_goal
        table_data.append([
            scenario["Scenario"],
            f"${scenario['FinalBalance']:,.2f}",
            f"${target_goal:,.2f}",
            f"{progress*100:.1f}%"
        ])

    table = Table(table_data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    return buffer

# ----------------------------
# Streamlit Layout
# ----------------------------
st.set_page_config(page_title="💰 Savings DSS", layout="wide")

st.title("💰 Smart Savings Decision Support System")

# Tabs
tab1, tab2, tab3, tab6 = st.tabs([
    "1️⃣ Inputs",
    "2️⃣ Forecast",
    "3️⃣ Personalized Recommendation",
    "6️⃣ What-If Scenarios"
])

# ----------------------------
# Tab 1: Inputs
# ----------------------------
with tab1:
    st.header("Enter Your Savings Plan")

    starting_balance = st.number_input("Starting Balance ($)", min_value=0.0, value=1000.0, step=100.0)
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=500.0, step=50.0)
    annual_return = st.slider("Expected Annual Return (%)", 0.0, 20.0, 5.0) / 100
    months = st.slider("Time Horizon (Months)", 6, 120, 36)
    target_goal = st.number_input("Target Goal ($)", min_value=1000.0, value=20000.0, step=1000.0)

    st.info("👉 Adjust your savings inputs and move to the Forecast tab.")

# ----------------------------
# Tab 2: Forecast
# ----------------------------
with tab2:
    st.header("Forecasted Growth")

    main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)

    df = pd.DataFrame({
        "Month": np.arange(1, months + 1),
        "Balance": main_forecast
    })

    st.line_chart(df.set_index("Month"))

# ----------------------------
# Tab 3: Personalized Recommendation
# ----------------------------
with tab3:
    st.header("Personalized Recommendation")

    main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)
    progress = main_forecast[-1] / target_goal

    # ✅ Dynamic Message
    if progress >= 1.0:
        st.success(f"🎉 Excellent! Your projected balance (${main_forecast[-1]:.2f}) meets or exceeds your goal of ${target_goal}.")
    elif 0.75 <= progress < 1.0:
        st.warning(f"⚠️ Almost there! Your projected balance (${main_forecast[-1]:.2f}) is {progress*100:.1f}% of your goal.")
    else:
        st.error(f"❌ Below target. Your projected balance (${main_forecast[-1]:.2f}) is only {progress*100:.1f}% of your goal. Consider adjusting contribution or strategy.")

    # ✅ Side-by-side Summary Dashboard
    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric("Final Balance", f"${main_forecast[-1]:.2f}")
        st.metric("Target Goal", f"${target_goal:,.2f}")
        st.metric("Goal Achievement", f"{progress*100:.1f}%")

    with col2:
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progress * 100,
            title={'text': "Goal Achievement (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 75], 'color': "red"},
                    {'range': [75, 100], 'color': "yellow"},
                    {'range': [100, 200], 'color': "green"},
                ],
            }
        ))
        st.plotly_chart(gauge, use_container_width=True)

# ----------------------------
# Tab 6: What-If Scenarios
# ----------------------------
with tab6:
    st.header("What-If Scenarios")

    scenario_inputs = []
    scenario_results = []
    for i in range(1, 4):
        st.subheader(f"Scenario {i}")
        colA, colB, colC, colD = st.columns(4)
        with colA:
            sb = st.number_input(f"Start (${i})", min_value=0.0, value=starting_balance, key=f"sb_{i}")
        with colB:
            mc = st.number_input(f"Monthly (${i})", min_value=0.0, value=monthly_contribution, key=f"mc_{i}")
        with colC:
            ar = st.slider(f"Return % ({i})", 0.0, 20.0, annual_return * 100, key=f"ar_{i}") / 100
        with colD:
            tg = st.number_input(f"Goal (${i})", min_value=1000.0, value=target_goal, key=f"tg_{i}")

        scenario_inputs.append({
            "StartingBalance": sb,
            "MonthlyContribution": mc,
            "AnnualReturn": ar,
            "TargetGoal": tg,
        })

        forecast = simulate_savings(sb, mc, ar, months)
        scenario_results.append({
            "Scenario": f"Scenario {i}",
            "FinalBalance": forecast[-1]
        })

    scenario_df = pd.DataFrame({
        "Scenario": [f"Scenario {i}" for i in range(1, 4)],
        "Final Balance": [r["FinalBalance"] for r in scenario_results],
        "Target Goal": [si["TargetGoal"] for si in scenario_inputs],
        "Achievement %": [r["FinalBalance"] / si["TargetGoal"] * 100 for r, si in zip(scenario_results, scenario_inputs)]
    })
    st.dataframe(scenario_df)

    # Download PDF report
    if st.button("Download PDF Report"):
        pdf = generate_pdf_report(main_forecast, target_goal, progress, scenario_results, scenario_inputs)
        st.download_button("Download report", data=pdf, file_name="savings_report.pdf", mime="application/pdf")
