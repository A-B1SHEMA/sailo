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
    story.append(Paragraph("💰 Sailo Decision Support Report", styles["Title"]))
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
st.set_page_config(page_title="💰 Sailo DSS", layout="wide")
st.title("💰 Sailo Decision Support System")

# Default simulation values
starting_balance = 1000.0
monthly_contribution = 200.0
annual_return = 0.05
months = 12
target_goal = 10000
main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)

formatted_balance = f"{main_forecast[-1]:,.2f}"
formatted_goal = f"{target_goal:,.2f}"
progress = main_forecast[-1] / target_goal

# ----------------------------
# Tabs
# ----------------------------
tab_inputs, tab_forecast, tab_whatif, tab_recommendation = st.tabs([
    "1️⃣ Inputs",
    "2️⃣ Forecast",
    "3️⃣ What-If Scenario",
    "4️⃣ Personalized Recommendation"
])

# ----------------------------
# Tab 1: Inputs
# ----------------------------
with tab_inputs:
    st.header("1️⃣ Inputs")
    starting_balance = st.number_input("Starting Balance ($)", min_value=0.0, value=starting_balance)
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=monthly_contribution)
    annual_return = st.slider("Expected Annual Return (%)", 0.0, 20.0, annual_return * 100) / 100
    target_goal = st.number_input("Target Goal ($)", min_value=1000.0, value=target_goal)
    months = st.number_input("Months to Simulate", min_value=1, value=months, step=1)
    main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)
    formatted_balance = f"{main_forecast[-1]:,.2f}"
    formatted_goal = f"{target_goal:,.2f}"
    progress = main_forecast[-1] / target_goal
    st.success(f"Inputs updated! Projected final balance: ${formatted_balance}")

# ----------------------------
# Tab 2: Forecast
# ----------------------------
with tab_forecast:
    st.header("2️⃣ Forecast")
    df_forecast = pd.DataFrame({
        "Period": list(range(1, len(main_forecast) + 1)),
        "Projected Balance": main_forecast
    }).set_index("Period")
    st.line_chart(df_forecast)

# ----------------------------
# Tab 3: What-If Scenario
# ----------------------------
with tab_whatif:
    st.header("3️⃣ What-If Scenarios")

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

    for r, si in zip(scenario_results, scenario_inputs):
        st.subheader(f"{r['Scenario']} Progress")
        progress_value = min(r["FinalBalance"] / si["TargetGoal"], 1.0)
        st.progress(progress_value)
        st.write(f"Final Balance: ${r['FinalBalance']:,.2f} / Goal: ${si['TargetGoal']:,.2f} ({progress_value*100:.1f}%)")

    # Download PDF report
    if st.button("Download PDF Report"):
        pdf = generate_pdf_report(main_forecast, target_goal, progress, scenario_results, scenario_inputs)
        st.download_button("Download report", data=pdf, file_name="sailo_report.pdf", mime="application/pdf")

# ----------------------------
# Tab 4: Personalized Recommendation
# ----------------------------
with tab_recommendation:
    st.header("4️⃣ Personalized Recommendation")
    if progress >= 1.0:
        st.success(f"🎉 Excellent! Your projected balance (${formatted_balance}) meets or exceeds your goal of ${formatted_goal}.")
    elif progress >= 0.5:
        st.warning(f"Your projected balance is ${formatted_balance}, which is {progress*100:.1f}% of your goal (${formatted_goal}). Keep going!")
    else:
        st.error(f"Your projected balance is ${formatted_balance}, which is only {progress*100:.1f}% of your goal (${formatted_goal}). Consider adjusting your plan.")

    st.subheader("📈 Progress toward your goal")
    st.progress(min(progress, 1.0))
    st.write(f"Final Balance: ${formatted_balance} / Goal: ${formatted_goal} ({progress*100:.1f}%)")



