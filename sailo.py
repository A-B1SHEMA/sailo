import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io
import random

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

    table = Table(table_data, hAlign="LEFT", colWidths=[100, 120, 120, 100])
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

# ----------------------------
# Default Inputs
# ----------------------------
months = 12
starting_balance = 1000.0
monthly_contribution = 500.0
annual_return = 0.05
target_goal = 10000.0

# ----------------------------
# Tabs
# ----------------------------
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
    st.header("📥 Inputs")
    starting_balance = st.number_input("Starting Balance ($)", min_value=0.0, value=starting_balance)
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=monthly_contribution)
    annual_return = st.slider("Expected Annual Return (%)", 0.0, 20.0, float(annual_return*100)) / 100
    target_goal = st.number_input("Target Goal ($)", min_value=1000.0, value=target_goal)
    months = st.number_input("Months", min_value=1, value=months)

# ----------------------------
# Tab 2: What You Can Do
# ----------------------------
with tab2:
    st.header("💡 What You Can Do")
    main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)
    final_balance = main_forecast[-1]
    progress = final_balance / target_goal
    gap = max(target_goal - final_balance, 0)

    if progress < 1.0:
        needed_balance = target_goal - final_balance
        suggested_contribution = needed_balance / months
        st.info(f"Increase your monthly contribution by ${suggested_contribution:,.2f} to reach your goal in {months} months.")
    else:
        st.success("🎉 You are on track to meet or exceed your goal!")

    # Quick Wins Module
    st.markdown("### ⚡ Quick Wins")
    boost = min(1000, gap * 0.2) if gap > 0 else 0
    months_saved = int(boost / monthly_contribution) if monthly_contribution > 0 else 0
    benchmark = random.randint(60, 90)

    st.markdown(f"""
    - 🪙 **One-Time Boost**: Add a lump sum of **${boost:,.0f}** now to reduce your timeline by ~{months_saved} months.
    - ✂️ **Cut Expenses**: Redirect **$50/month** from discretionary spending to savings.
    - 🔄 **Round-Up Auto-Save**: Enable micro-savings from daily purchases.
    - 📊 **Peer Benchmark**: You're ahead of **{benchmark}%** of users in your bracket.
    """)

    # Deep Optimization Module
    st.markdown("### 🧠 Deep Optimization")
    debt_balance = st.number_input("Debt Balance ($)", min_value=0.0, value=0.0, key="debt_balance")

    st.markdown("""
    - 📈 **Rebalance Portfolio**: Consider shifting **10–15%** to growth assets.
    - 🧾 **Tax Efficiency**: Use **Roth IRA** or **HSA** to reduce future tax burden.
    - 💸 **Fee Scan**: Review fund expense ratios—switching could improve returns.
    """)

    if debt_balance > 0:
        st.markdown("- 💳 **Debt Strategy**: Pay off high-interest loans first to save big on interest.")

    # Visual Gauge for Quick Wins Impact
    quick_win_gain = boost + (50 * months)
    if gap > 0:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=min(quick_win_gain / gap * 100, 100),
            title={"text": "Gap Closed with Quick Wins (%)"},
            gauge={"axis": {"range": [0, 100]}}
        ))
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Tab 3: Forecast
# ----------------------------
with tab3:
    st.header("📈 Forecast: Growth Over Time")
    main_forecast = simulate_savings(starting_balance, monthly_contribution, annual_return, months)

    months_list = list(range(1, months+1))
    contributions = np.cumsum([monthly_contribution]*months) + starting_balance
    interest = [balance - contrib for balance, contrib in zip(main_forecast, contributions)]

    df_forecast = pd.DataFrame({
        "Month": months_list,
        "Contributions": contributions,
        "Interest": interest,
        "Total Balance": main_forecast
    }).set_index("Month")

    st.subheader("Balance Breakdown")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_forecast.index, y=df_forecast["Contributions"],
                             mode='lines', name='Contributions', fill='tonexty'))
    fig.add_trace(go.Scatter(x=df_forecast.index, y=df_forecast["Total Balance"],
                             mode='lines', name='Total Balance', fill='tonexty'))
    fig.update_layout(yaxis_title="Balance ($)", xaxis_title="Month", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Progress toward your goal")
    st.progress(min(final_balance/target_goal, 1.0))
    st.write(f"Your final projected balance: ${final_balance:,.2f}")
    st.write(f"Target goal: ${target_goal:,.2f}")
    st.write(f"Goal achievement: {progress*100:.1f}%")

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
            ar = st.slider(f"Return % ({i})", 0.0, 20.0, float(annual_return*100), key=f"ar_{i}") / 100
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

    # Direct download button for PDF report
    pdf = generate_pdf_report(main_forecast, target_goal, progress, scenario_results, scenario_inputs)
    st.download_button("📄 Download PDF Report", data=pdf, file_name="sailo_report.pdf", mime="application/pdf")
