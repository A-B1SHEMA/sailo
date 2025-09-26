import streamlit as st
import pandas as pd
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

def generate_pdf_report(main_forecast, target_goal, progress, scenario_results, scenario_inputs):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("💰 Savings Decision Support Report", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Personalized Recommendation", styles["Heading2"]))
    final_balance = main_forecast[-1]
    story.append(Paragraph(f"Final Balance: ${final_balance:,.2f}", styles["Normal"]))
    story.append(Paragraph(f"Target Goal: ${target_goal:,.2f}", styles["Normal"]))
    story.append(Paragraph(f"Goal Achievement: {progress*100:.1f}%", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("What-If Scenarios", styles["Heading2"]))
    table_data = [["Scenario", "Final Balance", "Target Goal", "Achievement %"]]
    for scenario in scenario_results:
        tg = scenario_inputs[int(scenario["Scenario"][-1]) - 1]["TargetGoal"]
        prg = scenario["FinalBalance"] / tg
        table_data.append([
            scenario["Scenario"],
            f"${scenario['FinalBalance']:,.2f}",
            f"${tg:,.2f}",
            f"{prg*100:.1f}%"
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

# Tabs: Inputs, Forecast, What-If Scenario, Personalized Recommendation
tab_inputs, tab_forecast, tab_whatif, tab_recommendations = st.tabs([
    "1️⃣ Inputs",
    "2️⃣ Forecast",
    "3️⃣ What-If Scenario",
    "4️⃣ Personalized Recommendation"
])

# ----------------------------
# Tab 1: Inputs
# ----------------------------
with tab_inputs:
    st.header("📝 Enter Your Financial Details")
    starting_balance = st.number_input("Starting Balance ($)", min_value=0.0, value=2000.0)
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=500.0)
    annual_return = st.slider("Annual Return (%)", 0.0, 20.0, 5.0) / 100
    target_goal = st.number_input("Target Goal ($)", min_value=1000.0, value=10000.0)
    months = st.number_input("Time Horizon (Months)", min_value=1, value=12)

# ----------------------------
# Main Forecast Calculation
# ----------------------------
main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)
formatted_balance = f"{main_forecast[-1]:,.2f}"
formatted_goal = f"{target_goal:,.2f}"
progress = main_forecast[-1] / target_goal

# ----------------------------
# Tab 2: Forecast
# ----------------------------
with tab_forecast:
    st.header("📈 Forecast")
    df = pd.DataFrame({
        "Period": list(range(1, len(main_forecast)+1)),
        "Projected Balance": main_forecast
    }).set_index("Period")
    st.line_chart(df)

# ----------------------------
# Tab 3: What-If Scenario
# ----------------------------
with tab_whatif:
    st.header("🔍 What-If Scenario")
    multiplier = st.slider("Adjust Forecast Multiplier", 0.5, 1.5, 1.0)
    scenario_forecast = [x * multiplier for x in main_forecast]
    df_scenario = pd.DataFrame({
        "Period": list(range(1, len(scenario_forecast)+1)),
        "Projected Balance": scenario_forecast
    }).set_index("Period")
    st.line_chart(df_scenario)

    # Additional 3 scenarios
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
            ar = st.slider(f"Return % ({i})", 0.0, 20.0, annual_return*100, key=f"ar_{i})") / 100
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
        "Achievement %": [r["FinalBalance"]/si["TargetGoal"]*100 for r, si in zip(scenario_results, scenario_inputs)]
    })
    st.dataframe(scenario_df)

    if st.button("Download PDF Report"):
        pdf = generate_pdf_report(main_forecast, target_goal, progress, scenario_results, scenario_inputs)
        st.download_button("Download report", data=pdf, file_name="savings_report.pdf", mime="application/pdf")

# ----------------------------
# Tab 4: Personalized Recommendations
# ----------------------------
with tab_recommendations:
    st.header("💡 Recommendations")
    if progress >= 1.0:
        st.success(f"🎉 Excellent! Your projected balance (${formatted_balance}) meets or exceeds your goal of ${formatted_goal}.")
    elif progress >= 0.5:
        st.warning(f"Your projected balance is ${formatted_balance}, which is {progress*100:.1f}% of your goal (${formatted_goal}). Keep going!")
    else:
        st.error(f"Your projected balance is ${formatted_balance}, which is only {progress*100:.1f}% of your goal (${formatted_goal}). Consider adjusting your plan.")

    st.subheader("📈 Progress toward your goal")
    st.progress(min(progress, 1.0))



