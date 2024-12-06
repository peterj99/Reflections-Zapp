import google.generativeai as genai
import streamlit as st
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables for local
#

# For production
api_key = st.secrets["GEMINI_API_KEY"]

# Configure the generative AI model
genai.configure(api_key=api_key)

# Prompts
thought_of_the_day_prompt = """
You are an expert in creating inspirational and motivational content. Your task is to generate a “Reflection the Day" that is concise, impactful, and resonates deeply with users.

Guidelines:
- The thought should be less than 80 words.
- Ensure the content is meaningful and can inspire or uplift the user.
- Avoid using special characters like "\\" to maintain format integrity.
- Do not include any sensitive or controversial topics.

Output:
- Return a single string containing the "Thought of the Day".

Sample Format:
"Your thought of the day content here."
"""

generation_config = {
    "temperature": 0.5,  # Set temperature for deterministic responses
}

# Initialize separate models for each task
thought_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", system_instruction=thought_of_the_day_prompt
)

# Function to generate a random thought of the day
def get_thought_of_day():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt = f"{thought_of_the_day_prompt}\nCurrent Date and Time: {current_time}"
    response = thought_model.generate_content(prompt)
    return response.parts[0].text.strip()

# Function to generate a thought based on a specific theme
def get_thought_by_theme(themes):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    theme_prompt = f"Generate a 'Thought of the Day' focusing on the themes: {', '.join(themes)}.\nCurrent Date and Time: {current_time}"
    response = thought_model.generate_content(theme_prompt)
    return response.parts[0].text.strip()

# Streamlit app
st.title("Soulful Reflections")

# Welcome Section
st.write(
    "Welcome to Soulful Reflections! We help make your day better by providing personalized inspiration and guidance. Here's a small reflection for you"
)

# Part 1: Random Thought of the Day

random_thought = get_thought_of_day()
thought_placeholder = st.empty()
thought_placeholder.markdown(f"<h3>{random_thought}</h3>", unsafe_allow_html=True)

# Part 2: Get Inspired
inspiration_themes = st.selectbox(
    "Select a theme to receive a new inspirational message.(this can be changed to user's moods)",
    ["Strength", "Gratitude", "Forgiveness", "Love", "Hope", "Peace", "Courage", "Wisdom", "Joy",
     "Patience", "Humility", "Compassion", "Faith", "Mindfulness", "Purpose", "Healing", "Unity",
     "Growth", "Generosity", "Resilience"],
    key="inspiration_theme_selector"  # Add a unique key to prevent rerunning
)

# Display current thought
if 'current_thought' not in st.session_state:
    st.session_state.current_thought = random_thought

thought_placeholder.markdown(f"<h3>{st.session_state.current_thought}</h3>", unsafe_allow_html=True)

if st.button("Get New Reflection"):
    # Clear the existing thought
    thought_placeholder.empty()

    # Show spinner
    with st.spinner('Generating new thought...'):
        # Generate new thought based on selected theme
        st.session_state.current_thought = get_thought_by_theme([inspiration_themes])

    # Update with new thought
    thought_placeholder.markdown(f"<h3>{st.session_state.current_thought}</h3>", unsafe_allow_html=True)