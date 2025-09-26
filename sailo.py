import streamlit as st

# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(
    page_title="Sailo",
    page_icon="logo.png",  # small favicon/logo in browser tab
    layout="wide"
)

# -------------------------------
# Sidebar
# -------------------------------
st.sidebar.markdown(
    '<img src="logo.png" width="120">', 
    unsafe_allow_html=True
)
st.sidebar.title("Sailo Dashboard")
st.sidebar.write("Navigate through your financial insights:")

st.sidebar.markdown("### Menu")
menu_options = ["Home", "Goal Tracker", "Analytics", "Recommendations"]
choice = st.sidebar.radio("", menu_options)

# -------------------------------
# Main page header
# -------------------------------
st.markdown(
    '<div style="display:flex; align-items:center;">'
    '<img src="logo.png" width="100" style="margin-right:20px;">'
    '<h1>Sailo</h1>'
    '</div>',
    unsafe_allow_html=True
)

st.write("Your personal financial goal dashboard.")

# -------------------------------
# Page content based on selection
# -------------------------------
if choice == "Home":
    st.subheader("Welcome Home")
    st.write("Here you can see an overview of your progress.")

elif choice == "Goal Tracker":
    st.subheader("Goal Tracker")
    st.write("Track your savings goals and progress here.")

elif choice == "Analytics":
    st.subheader("Analytics")
    st.write("Visualize your financial metrics and trends.")

elif choice == "Recommendations":
    st.subheader("Personalized Recommendations")
    st.write("Get actionable suggestions to reach your goals faster.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("© 2025 Sailo. All rights reserved.")

