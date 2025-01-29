import openai
import streamlit as st
import os
from datetime import datetime, timedelta


def init_openai():
    api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set it in .streamlit/secrets.toml or as an environment variable.")
    openai.api_key = api_key


def get_ai_response(message, user_profile, sleep_data, daily_summaries):
    try:
        # Prepare context from user data
        sleep_context = format_sleep_data(sleep_data)
        summary_context = format_daily_summaries(daily_summaries)

        system_message = f"""
        You are an empathetic and supportive AI mental health assistant named MindfulChat, with expertise in psychology and cognitive behavioral therapy. Your role is to provide mental health support, guidance, and analysis based on the user's data and interactions.

        User Profile:
        {user_profile}

        Recent Sleep Data:
        {sleep_context}

        Recent Daily Summaries:
        {summary_context}

        As a psychologist, remember to:
        1. Be empathetic, understanding, and non-judgmental
        2. Ask open-ended questions to encourage the user to express themselves
        3. Provide supportive and constructive feedback
        4. Suggest evidence-based coping strategies and mindfulness techniques when appropriate
        5. Encourage professional help for serious concerns
        6. Use a warm and friendly tone
        7. Offer encouragement and positive reinforcement
        8. Respect the user's privacy and maintain confidentiality
        9. Analyze patterns in the user's sleep, mood, and activities to provide insights
        10. Highlight potential correlations between behaviors and mental states
        11. Suggest small, achievable goals to improve mental well-being
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "I apologize, but I'm having trouble responding right now. Please try again in a moment."


def get_initial_questions():
    return [
        "How would you describe your overall mood lately?",
        "Have you been experiencing any significant stress or anxiety? If so, what seems to trigger it?",
        "How would you rate your sleep quality, and has it changed recently?",
        "Are there any specific mental health concerns or issues you'd like to discuss?",
        "What are your main goals for using MindfulChat?",
        "Have you practiced any relaxation or mindfulness techniques before? If so, which ones?"
    ]


def format_sleep_data(sleep_data):
    if not sleep_data:
        return "No recent sleep data available."

    formatted_data = []
    for date, data in sleep_data.items():
        formatted_data.append(
            f"Date: {date}, Duration: {data['hours']}h {data['minutes']}m, Quality: {data['quality']}")

    return "\n".join(formatted_data)


def format_daily_summaries(daily_summaries):
    if not daily_summaries:
        return "No recent daily summaries available."

    formatted_summaries = []
    for date, data in daily_summaries.items():
        formatted_summaries.append(
            f"Date: {date}\nMood: {data['mood']}\nActivities: {', '.join(data['activities'])}\nSummary: {data['summary']}")

    return "\n\n".join(formatted_summaries)


def analyze_mental_health(sleep_data, daily_summaries):
    # Calculate average sleep duration and quality
    sleep_durations = [data['hours'] * 60 + data['minutes'] for data in sleep_data.values()]
    avg_sleep_duration = sum(sleep_durations) / len(sleep_durations) if sleep_durations else 0
    sleep_qualities = [data['quality'] for data in sleep_data.values()]
    avg_sleep_quality = sum(
        ({"Poor": 1, "Fair": 2, "Good": 3, "Very Good": 4, "Excellent": 5}[q] for q in sleep_qualities)) / len(
        sleep_qualities) if sleep_qualities else 0

    # Analyze mood trends
    mood_scores = []
    for summary in daily_summaries.values():
        mood = summary['mood']
        mood_scores.append({"Very Bad": 1, "Bad": 2, "Neutral": 3, "Good": 4, "Very Good": 5}[mood])
    avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 0

    # Count activities
    activity_counts = {}
    for summary in daily_summaries.values():
        for activity in summary['activities']:
            activity_counts[activity] = activity_counts.get(activity, 0) + 1

    # Generate insights
    insights = []
    if avg_sleep_duration < 420:  # Less than 7 hours
        insights.append(
            "Your average sleep duration is below the recommended 7-9 hours. Consider adjusting your sleep schedule to improve your mental well-being.")
    elif avg_sleep_duration > 540:  # More than 9 hours
        insights.append(
            "Your average sleep duration is above the recommended 7-9 hours. While individual needs vary, excessive sleep can sometimes be associated with mood disorders. Monitor how you feel and consult a professional if concerned.")

    if avg_sleep_quality < 3:
        insights.append(
            "Your average sleep quality is lower than ideal. Try implementing a consistent bedtime routine and creating a sleep-friendly environment to improve your sleep quality.")

    if avg_mood < 3:
        insights.append(
            "Your mood has been trending lower recently. Consider incorporating more mood-boosting activities into your routine, such as exercise or socializing with friends.")
    elif avg_mood > 4:
        insights.append(
            "Your mood has been consistently positive lately. Keep up the good work and continue with the activities that seem to be benefiting your mental health.")

    most_common_activity = max(activity_counts, key=activity_counts.get) if activity_counts else None
    if most_common_activity:
        insights.append(
            f"Your most frequent activity is {most_common_activity}. Consider how this activity affects your mood and energy levels.")

    if "Exercise" not in activity_counts:
        insights.append(
            "You haven't reported any exercise recently. Regular physical activity can significantly improve mood and reduce stress. Try incorporating some form of exercise into your routine.")

    return {
        "avg_sleep_duration": avg_sleep_duration,
        "avg_sleep_quality": avg_sleep_quality,
        "avg_mood": avg_mood,
        "activity_counts": activity_counts,
        "insights": insights
    }