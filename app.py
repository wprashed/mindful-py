import streamlit as st
import database as db
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Initialize the database
db.init_db()

# Set page config
st.set_page_config(page_title="MindfulTracker", page_icon="🧠", layout="wide")

# Initialize session state
if 'username' not in st.session_state:
    st.session_state.username = None

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: #2c2c2c;
        color: #ffffff;
    }
    .stButton > button {
        background-color: #ff9eaa;
        color: #1a1a1a;
    }
    .stTab > button {
        color: #ffffff;
    }
    .stTab > button[data-baseweb="tab"][aria-selected="true"] {
        color: #ff9eaa;
    }
    .stDateInput > div > div > input {
        background-color: #2c2c2c;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)


def login():
    with st.form("login_form"):
        st.subheader("Welcome Back!")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submit_button = st.form_submit_button("Login")

    if submit_button:
        if db.check_user(username, password):
            st.session_state.username = username
            st.success("Logged in successfully!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")


def register():
    with st.form("register_form"):
        st.subheader("Join MindfulTracker")
        new_user = st.text_input("Choose a Username", key="register_username")
        new_password = st.text_input("Create a Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        submit_button = st.form_submit_button("Create Account")

    if submit_button:
        if new_password != confirm_password:
            st.error("Passwords do not match")
        elif db.add_user(new_user, new_password):
            st.success("You have successfully registered!")
            st.info("Please login with your new account")
        else:
            st.error("Username already exists")


def logout():
    st.session_state.username = None
    st.success("Logged out successfully")
    st.experimental_rerun()


def daily_input():
    st.subheader("Daily Log")

    with st.form("daily_log"):
        date = st.date_input("Date", value=datetime.now())
        sleep_hours = st.number_input("Hours of Sleep", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
        sleep_quality = st.select_slider("Sleep Quality", options=["Poor", "Fair", "Good", "Very Good", "Excellent"],
                                         value="Good")
        mood = st.select_slider("Mood", options=["Very Bad", "Bad", "Neutral", "Good", "Very Good"], value="Neutral")

        meals = st.text_area("Meals (one per line)")
        activities = st.text_area("Activities (one per line)")
        notes = st.text_area("Additional Notes")

        submit_button = st.form_submit_button("Save Daily Log")

    if submit_button:
        meals_list = [meal.strip() for meal in meals.split("\n") if meal.strip()]
        activities_list = [activity.strip() for activity in activities.split("\n") if activity.strip()]

        if db.add_daily_log(st.session_state.username, date.strftime('%Y-%m-%d'), sleep_hours, sleep_quality, mood,
                            meals_list, activities_list, notes):
            st.success("Daily log saved successfully!")
        else:
            st.error("Failed to save daily log")


def analyze_data(logs):
    df = pd.DataFrame(logs)
    df['date'] = pd.to_datetime(df['date'])
    df['sleep_quality_numeric'] = df['sleep_quality'].map(
        {"Poor": 1, "Fair": 2, "Good": 3, "Very Good": 4, "Excellent": 5})
    df['mood_numeric'] = df['mood'].map({"Very Bad": 1, "Bad": 2, "Neutral": 3, "Good": 4, "Very Good": 5})

    # Sleep analysis
    avg_sleep = df['sleep_hours'].mean()
    avg_sleep_quality = df['sleep_quality_numeric'].mean()

    # Mood analysis
    avg_mood = df['mood_numeric'].mean()

    # Activity analysis
    all_activities = [activity for activities in df['activities'] for activity in activities]
    activity_counts = pd.Series(all_activities).value_counts()

    # Meal analysis
    all_meals = [meal for meals in df['meals'] for meal in meals]
    meal_counts = pd.Series(all_meals).value_counts()

    return {
        'avg_sleep': avg_sleep,
        'avg_sleep_quality': avg_sleep_quality,
        'avg_mood': avg_mood,
        'activity_counts': activity_counts,
        'meal_counts': meal_counts,
        'df': df
    }


def display_analytics(logs):
    st.subheader("Mental Health Analytics")

    if not logs:
        st.warning("No data available for the selected period.")
        return

    analysis = analyze_data(logs)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Sleep Duration", f"{analysis['avg_sleep']:.2f} hours")
    with col2:
        st.metric("Average Sleep Quality", f"{analysis['avg_sleep_quality']:.2f}/5")
    with col3:
        st.metric("Average Mood", f"{analysis['avg_mood']:.2f}/5")

    # Sleep and Mood Trends
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=analysis['df']['date'], y=analysis['df']['sleep_hours'], name='Sleep Hours'))
    fig.add_trace(go.Scatter(x=analysis['df']['date'], y=analysis['df']['mood_numeric'], name='Mood', yaxis='y2'))
    fig.update_layout(
        title='Sleep and Mood Trends',
        xaxis_title='Date',
        yaxis_title='Sleep Hours',
        yaxis2=dict(title='Mood', overlaying='y', side='right')
    )
    st.plotly_chart(fig, use_container_width=True)

    # Activity Frequency
    st.subheader("Activity Frequency")
    fig = px.bar(analysis['activity_counts'], x=analysis['activity_counts'].index, y=analysis['activity_counts'].values)
    fig.update_layout(xaxis_title="Activity", yaxis_title="Frequency")
    st.plotly_chart(fig, use_container_width=True)

    # Meal Frequency
    st.subheader("Meal Frequency")
    fig = px.bar(analysis['meal_counts'], x=analysis['meal_counts'].index, y=analysis['meal_counts'].values)
    fig.update_layout(xaxis_title="Meal", yaxis_title="Frequency")
    st.plotly_chart(fig, use_container_width=True)


def main():
    if not st.session_state.username:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            login()
        with tab2:
            register()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}!")
        menu = st.sidebar.selectbox("Menu", ["Daily Input", "Analytics"])

        if menu == "Daily Input":
            daily_input()
        elif menu == "Analytics":
            st.title("Mental Health Analytics")
            date_range = st.selectbox("Select Date Range", ["Week", "Month", "Year", "All Time"])

            start_date, end_date = db.get_date_range(st.session_state.username, date_range.lower())
            if start_date and end_date:
                logs = db.get_daily_logs(st.session_state.username, start_date, end_date)
                display_analytics(logs)
            else:
                st.warning("No data available for the selected period.")

        if st.sidebar.button("Logout"):
            logout()


if __name__ == "__main__":
    main()