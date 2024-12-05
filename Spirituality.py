import google.generativeai as genai
import streamlit as st
import json
import os
from dotenv import load_dotenv

# Load environment variables for local
# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")

#for prod
api_key = st.secrets["GEMINI_API_KEY"]
# Configure the generative AI model
genai.configure(api_key=api_key)

# Prompts
thought_of_the_day_prompt = """
You are an expert in creating inspirational and motivational content. Your task is to generate a "Thought of the Day" that is concise, impactful, and resonates deeply with users.

Guidelines:
- The thought should be less than 100 words.
- Ensure the content is meaningful and can inspire or uplift the user.
- Avoid using special characters like "\\" to maintain format integrity.
- Do not include any sensitive or controversial topics.

Output:
- Return a single string containing the "Thought of the Day".

Sample Format:
"Your thought of the day content here."
"""

base_prompt = """
You are an expert in creating personalized spiritual content for users. 
You will be given information about the user's religious affiliation, denomination, and preferred themes.
Your task is to generate daily devotionals less than 150 words, prayer guides which is less than 150 words, inspirational quotes which is less than 100 words and Religious Insight(Information about that specific day/week/month for that specific religion)tailored to their preferences.

Avoid:
- Generating content that is too generic or not specific to the user's inputs.
- Mentioning sensitive information or controversial topics.
- Repeating the same structure for each response.
- Special characters like "\\" to avoid breaking the JSON

Output:
- Return a dictionary with keys: daily_devotional, inspirational_quote, and prayer_guide.

Sample Format:
{
  "daily_devotional": "Your daily devotional content here.",
  "prayer_guide": "Your prayer guide content here.",
  "inspirational_quote": "Your inspirational quote here.",
  "religious_insight":"Your religious insight here."
}
"""

generation_config = {
    "temperature": 0.5,  # Set temperature for deterministic responses
}

# Initialize separate models for each task
thought_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", system_instruction=thought_of_the_day_prompt
)

spiritual_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", system_instruction=base_prompt
)


# Function to generate a random thought of the day
def get_thought_of_day():
    response = thought_model.generate_content(thought_of_the_day_prompt)
    return response.parts[0].text.strip()


# Function to generate a thought based on a specific theme
def get_thought_by_theme(themes):
    theme_prompt = f"Generate a 'Thought of the Day' focusing on the themes: {', '.join(themes)}."
    response = thought_model.generate_content(theme_prompt)
    return response.parts[0].text.strip()


# Function to generate personalized spiritual content
def get_spiritual_content(religion, denomination, themes):
    prompt = f"Generate spiritual content for a {religion} of the {denomination} denomination focusing on {', '.join(themes)}."
    response = spiritual_model.generate_content(prompt)
    return json.loads(response.parts[0].text[7:-4])


# Streamlit app
st.title("Soulful Reflections")

# Welcome Section
st.write(
    "Welcome to Soulful Reflections! Discover daily inspiration and spiritual guidance tailored to your beliefs and emotions.")

# Part 1: Random Thought of the Day
st.header("Thought of the Day")
random_thought = get_thought_of_day()
thought_placeholder = st.empty()
thought_placeholder.write(random_thought)

# Part 2 Get Inspired
# st.header("Get Inspired")
# st.write("Select a theme to receive a new inspirational message.")
inspiration_themes = st.selectbox("Select a theme to receive a new inspirational message.",
                                  ["Strength", "Gratitude", "Forgiveness", "Love", "Hope", "Peace", "Courage", "Wisdom",
                                   "Joy", "Patience", "Humility", "Compassion", "Faith", "Mindfulness", "Purpose",
                                   "Healing", "Unity", "Growth", "Generosity", "Resilience"])
if st.button("Get Inspired"):
    if inspiration_themes:
        inspired_thought = get_thought_by_theme(inspiration_themes)
        thought_placeholder.write(inspired_thought)

# Part 3: Religious Beliefs Specific Content
st.header("Personalized Spiritual Content")
st.write(
    "Discover personalized spiritual content tailored to your beliefs, religion, denomination and themes to receive daily devotionals, prayer guides, and inspirational quotes that resonate with your faith and emotions.")
religion = st.selectbox("Religion", ["Christianity", "Islam", "Judaism", "Hinduism", "Buddhism", "Other"])
denomination = st.text_input("Denomination or Sect")
themes = st.multiselect("Preferred Themes and Topics",
                        ["Strength", "Gratitude", "Forgiveness", "Love", "Hope", "Peace", "Courage", "Wisdom", "Joy",
                         "Patience", "Humility", "Compassion", "Faith", "Mindfulness", "Purpose", "Healing", "Unity",
                         "Growth", "Generosity", "Resilience"])

if st.button("Generate Spiritual Content"):
    with st.spinner('Generating spiritual content...'):
        spiritual_content = get_spiritual_content(religion, denomination, themes)
    st.header("Daily Devotional")
    st.write(spiritual_content["daily_devotional"])

    st.header("Prayer Guide")
    st.write(spiritual_content["prayer_guide"])

    st.header("Inspirational Quote")
    st.write(spiritual_content["inspirational_quote"])

    # st.header("Religious Insight")
    # st.write(spiritual_content.get("religious_insight", "No specific insight available for today."))

    # st.header("Daily Challenge")
    # st.write("Engage with today's challenge to deepen your spiritual practice and apply the themes in your daily life.")