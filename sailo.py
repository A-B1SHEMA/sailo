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
    for i, scenario in enumerate(scenario_results):
        tg = scenario_inputs[i]["TargetGoal"]
        prog = scenario["FinalBalance"] / tg
        table_data.append([
            scenario["Scenario"],
            f"${scenario['FinalBalance']:,.2f}",
            f"${tg:,.2f}",
            f"{prog*100:.1f}%"
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
st.set_page_config(page_title="💰 Sailo", layout="wide")
st.title("💰 Sailo Decision Support System")

# ----------------------------
# Default Values
# ----------------------------
starting_balance = 2000.0
monthly_contribution = 500.0
annual_return = 0.05
target_goal = 10000.0
months = 12

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Inputs",
    "2️⃣ Forecast",
    "3️⃣ What-If Scenario",
    "4️⃣ Personalized Recommendation"
])

# ----------------------------
# Tab 1: Inputs
# ----------------------------
with tab1:
    st.header("📥 Enter Your Financial Data")
    starting_balance = st.number_input("Starting Balance ($)", min_value=0.0, value=float(starting_balance))
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=float(monthly_contribution))
    annual_return = st.slider("Expected Annual Return (%)", 0.0, 20.0, float(annual_return * 100)) / 100
    target_goal = st.number_input("Target Goal ($)", min_value=1000.0, value=float(target_goal))
    months = st.number_input("Months to Simulate", min_value=1, value=int(months), step=1)

# ----------------------------
# Forecast Data
# ----------------------------
main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)
progress = main_forecast[-1] / target_goal

# ----------------------------
# Tab 2: Forecast
# ----------------------------
with tab2:
    st.header("📈 Forecast")
    df_forecast = pd.DataFrame({
        "Period": list(range(1, months + 1)),
        "Projected Balance": main_forecast
    }).set_index("Period")
    st.line_chart(df_forecast)

# ----------------------------
# Tab 3: What-If Scenario
# ----------------------------
with tab3:
    st.header("🔍 What-If Scenario")
    multiplier = st.slider("Adjust Forecast Multiplier", 0.5, 1.5, 1.0)
    scenario_forecast = [x * multiplier for x in main_forecast]
    df_scenario = pd.DataFrame({
        "Period": list(range(1, months + 1)),
        "Projected Balance": scenario_forecast
    }).set_index("Period")
    st.line_chart(df_scenario)

# ----------------------------
# Tab 4: Personalized Recommendation
# ----------------------------
with tab4:
    st.header("💡 Recommendations")

    # Recommendation Message
    if progress >= 1.0:
        st.success(f"🎉 Excellent! Your projected balance (${main_forecast[-1]:,.2f}) meets or exceeds your goal of ${target_goal:,.2f}.")
    elif progress >= 0.5:
        st.warning(f"Your projected balance is ${main_forecast[-1]:,.2f}, which is {progress*100:.1f}% of your goal (${target_goal:,.2f}). Keep going!")
    else:
        st.error(f"Your projected balance is ${main_forecast[-1]:,.2f}, which is only {progress*100:.1f}% of your goal (${target_goal:,.2f}). Consider adjusting your plan.")

    # Progress bar with numeric value
    st.subheader("📊 Progress toward your goal")
    st.progress(min(progress, 1.0))
    st.write(f"Current Balance: ${main_forecast[-1]:,.2f}")
    st.write(f"Target Goal: ${target_goal:,.2f}")
    st.write(f"Progress: {progress*100:.1f}%")

# ----------------------------
# Optional: Download PDF
# ----------------------------
scenario_inputs = [{"StartingBalance": starting_balance,
                    "MonthlyContribution": monthly_contribution,
                    "AnnualReturn": annual_return,
                    "TargetGoal": target_goal}]
scenario_results = [{"Scenario": "Base Case", "FinalBalance": main_forecast[-1]}]

if st.button("Download PDF Report"):
    pdf = generate_pdf_report(main_forecast, target_goal, progress, scenario_results, scenario_inputs)
    st.download_button("Download Report", data=pdf, file_name="sailo_report.pdf", mime="application/pdf")
