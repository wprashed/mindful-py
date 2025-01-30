# MindfulTracker

MindfulTracker is a web application built using Streamlit, designed to help users track their mental health and wellness by logging daily activities, sleep patterns, meals, and mood. The app also provides analytics and insights based on the logged data, including mood trends, sleep quality, and activity frequency. The application includes AI-powered mental health support via an integrated chatbot.

## Features

- **User Authentication:**
  - User login and registration system with validation.
  
- **Daily Logging:**
  - Log sleep data, mood, meals, activities, and additional notes.
  - Rate sleep quality and mood from predefined scales.
  
- **Data Analytics:**
  - View insightful analytics based on your daily logs.
  - Track average sleep hours, sleep quality, mood trends, and activity frequencies.
  - Visualize trends using interactive charts (Plotly).
  
- **AI Mental Health Assistant:**
  - Powered by OpenAI's GPT-4, the MindfulChat assistant provides empathetic support and mental health guidance based on your personal data.
  - Offers personalized insights, coping strategies, and mindfulness techniques.

## Setup Instructions

### 1. Install Dependencies

You need Python 3.7+ installed to run this project. First, clone the repository and install the necessary dependencies.

```bash
git clone <repo-url>
cd mindfultracker
pip install -r requirements.txt
```

### 2. Database Configuration

The app requires a database to store user information and logs. Set up your database by configuring the following in `database.py`:

- `init_db()`: Initializes the database.
- `check_user()`: Validates users during login.
- `add_user()`: Adds new users to the database.
- `add_daily_log()`: Saves daily logs to the database.
- `get_daily_logs()`: Retrieves daily logs for a specific user.
- `get_date_range()`: Returns date ranges based on user selection.

### 3. Set OpenAI API Key

The app integrates with OpenAI to provide the mental health assistant feature. Set up your OpenAI API key:

- Add the following to your `.streamlit/secrets.toml`:

```toml
[openai]
api_key = "<your-api-key>"
```

Alternatively, you can set the `OPENAI_API_KEY` as an environment variable.

### 4. Run the Application

Once everything is set up, you can run the app locally:

```bash
streamlit run app.py
```

## Usage

1. **Login/Registration**: Users can either log in with their existing account or create a new account.
2. **Daily Log**: After logging in, users can input daily logs about their sleep, mood, meals, activities, and additional notes.
3. **Analytics**: Users can view analytics for the selected time period (week, month, year, all time). The app will generate visual reports on sleep patterns, mood trends, activity frequencies, and meal habits.
4. **AI Chatbot**: The MindfulChat assistant will provide personalized mental health insights based on the user's logs and data. It can suggest relaxation techniques, mindfulness practices, and coping strategies.

## Contributing

Feel free to contribute to the project by opening issues, submitting pull requests, or suggesting features. Contributions are welcome!

## License

This project is open-source and available under the MIT License.

---

**MindfulTracker** - Empowering you to track and improve your mental well-being!

### Key Sections:
- **Features**: Lists the main features of your application.
- **Setup Instructions**: Guides users through the steps to install dependencies, set up the database, and configure the OpenAI API key.
- **Usage**: Details how to use the application once it's set up.
- **Contributing**: Encourages users to contribute to the project.
- **License**: States the project's open-source license.
