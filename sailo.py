import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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
    for _ in range(months):
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

    # Personalized Suggestions
    story.append(Paragraph("What You Can Do", styles["Heading2"]))
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

# Tabs: 1=Inputs, 2=What You Can Do, 3=Forecast, 4=What-If Scenario
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Inputs",
    "2️⃣ What You Can Do",
    "3️⃣ Forecast",
    "4️⃣ What-If Scenario"
])

# ----------------------------
# Tab 1: Inputs
# ----------------------------
with tab1:
    st.header("📥 Input Your Data")
    starting_balance = st.number_input("Starting Balance ($)", min_value=0.0, value=2000.0)
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=500.0)
    annual_return = st.slider("Expected Annual Return (%)", 0.0, 20.0, 5.0) / 100
    target_goal = st.number_input("Target Goal ($)", min_value=1000.0, value=10000.0)
    months = st.number_input("Months to Forecast", min_value=1, value=12)

# ----------------------------
# Tab 2: What You Can Do
# ----------------------------
with tab2:
    st.header("💡 Actionable Suggestions")
    main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)
    final_balance = main_forecast[-1]
    progress = final_balance / target_goal

    # Suggest contributions adjustment
    if progress < 1.0:
        required_monthly = (target_goal / ((1 + annual_return/12)**months) - starting_balance) / months
        st.info(f"Increase contribution to **${required_monthly:,.2f} per month** to meet your goal in {months} months.")
    else:
        st.success("You're on track! No changes needed to meet your goal.")

    # Show summary
    st.write(f"Your projected balance: **${final_balance:,.2f}**")
    st.write(f"Target goal: **${target_goal:,.2f}**")
    st.progress(min(progress, 1.0))

# ----------------------------
# Tab 3: Forecast
# ----------------------------
with tab3:
    st.header("📈 Forecast")
    df_forecast = pd.DataFrame({
        "Month": list(range(1, months+1)),
        "Projected Balance": main_forecast
    }).set_index("Month")
    st.line_chart(df_forecast)

# ----------------------------
# Tab 4: What-If Scenario
# ----------------------------
with tab4:
    st.header("🔍 What-If Scenarios")
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
            ar = st.slider(f"Return % ({i})", 0.0, 20.0, annual_return*100, key=f"ar_{i}") / 100
        with colD:
            tg = st.number_input(f"Goal (${i})", min_value=1000.0, value=target_goal, key=f"tg_{i}")

        scenario_inputs.append({"StartingBalance": sb, "MonthlyContribution": mc, "AnnualReturn": ar, "TargetGoal": tg})
        forecast = simulate_savings(sb, mc, ar, months)
        scenario_results.append({"Scenario": f"Scenario {i}", "FinalBalance": forecast[-1]})

    scenario_df = pd.DataFrame({
        "Scenario": [f"Scenario {i}" for i in range(1, 4)],
        "Final Balance": [r["FinalBalance"] for r in scenario_results],
        "Target Goal": [si["TargetGoal"] for si in scenario_inputs],
        "Achievement %": [r["FinalBalance"] / si["TargetGoal"] * 100 for r, si in zip(scenario_results, scenario_inputs)]
    })
    st.dataframe(scenario_df)

    if st.button("Download PDF Report"):
        pdf = generate_pdf_report(main_forecast, target_goal, progress, scenario_results, scenario_inputs)
        st.download_button("Download report", data=pdf, file_name="sailo_report.pdf", mime="application/pdf")

