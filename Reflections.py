import google.generativeai as genai
import streamlit as st
import json
import os
#from dotenv import load_dotenv
#from datetime import datetime


# For production
api_key = st.secrets["GEMINI_API_KEY"]

# Configure the generative AI model
genai.configure(api_key=api_key)


thought_generation_prompt = """
You are a supportive friend creating an inspirational message.

Task: Generate a short, positive, and encouraging thought that:
- Acknowledges the user's current emotions (based on the selected moods)
- Offers gentle comfort
- Provides hope and motivation
- Is easy to understand
- Fits in one to three sentences (max 100 words)
- Avoids very complex language

Guidelines:
1. Create a reflection that is COMPLETELY DIFFERENT from these key phrases:
{previous_key_phrases}

2. Mood Themes: {themes}

Requirements:
- Concise (under 80 words)
- Deeply personal
- Use simple, understandable language
- Unique emotional perspective

Guidelines 2:
- Keep it simple and hopeful
- Use warm, encouraging language
- Make it relatable and uplifting
"""

# Configuration for thought generation
generation_config = {
    "temperature": 0.7,
    "max_output_tokens": 60,
    "top_p": 0.9,
}

# Initialize Gemini model
thought_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash"
)


class SoulfulReflectionsApp:
    def __init__(self):
        # Initialize session state for tracking thoughts
        if 'generated_thoughts' not in st.session_state:
            st.session_state.generated_thoughts = []

        # Initialize key phrases to prevent duplication
        if 'key_phrases' not in st.session_state:
            st.session_state.key_phrases = []

        # Initialize selected moods
        if 'selected_moods' not in st.session_state:
            st.session_state.selected_moods = []

    def _extract_key_phrases(self, thought):
        """
        Extract key phrases more efficiently

        Args:
            thought (str): The original thought

        Returns:
            list: Key phrases to prevent duplication
        """
        # Split the thought into words
        words = thought.split()
        if len(words) > 4:
            # Take start, middle, and end phrases
            key_phrases = [
                ' '.join(words[:3]),  # First 3 words
                ' '.join(words[len(words)//2-1:len(words)//2+2]),  # Middle 3 words
                ' '.join(words[-3:])  # Last 3 words
            ]
            return key_phrases
        return [thought]

    def is_unique_thought(self, new_thought):
        """
        Check if thought is unique more efficiently

        Args:
            new_thought (str): The new generated thought

        Returns:
            bool: Whether the thought is considered unique
        """
        # Reduce comparison complexity
        return not any(
            new_thought.lower() in existing.lower() or
            existing.lower() in new_thought.lower()
            for existing in st.session_state.generated_thoughts[-5:]  # Check only recent thoughts
        )

    def render_mood_selector(self):
        """Render mood selection interface"""
        st.write("Select your current mood(s) to receive today's inspirational message.")

        # Mood options with emojis
        mood_options = [
            {"name": "Joy", "emoji": "😄"},
            {"name": "Sadness", "emoji": "😢"},
            {"name": "Fear", "emoji": "😨"},
            {"name": "Disgust", "emoji": "🤢"},
            {"name": "Anger", "emoji": "😠"}
        ]

        # Create columns for mood selection
        cols = st.columns(len(mood_options))
        selected_moods = []

        for i, mood in enumerate(mood_options):
            with cols[i]:
                if st.checkbox(f"{mood['emoji']} {mood['name']}",
                               key=f"mood_{mood['name'].lower()}"):
                    selected_moods.append(mood['name'])

        # Update session state with selected moods
        st.session_state.selected_moods = selected_moods
        return selected_moods

    def generate_unique_thought(self, moods):
        """
        Generate a unique, uplifting thought

        Args:
            moods (list): List of selected mood themes

        Returns:
            str: A unique, inspirational reflection
        """
        # Prepare previous key phrases context
        previous_key_phrases = "\n".join(st.session_state.key_phrases[-10:]) \
            if st.session_state.key_phrases else "No previous phrases"

        # Construct full prompt
        full_prompt = thought_generation_prompt.format(
            themes=', '.join(moods),
            previous_key_phrases=previous_key_phrases
        )

        # Attempt to generate a unique thought
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                # Generate response
                response = thought_model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                new_thought = response.text.strip()

                # Check uniqueness more efficiently
                if self.is_unique_thought(new_thought):
                    # Extract and store key phrases
                    new_key_phrases = self._extract_key_phrases(new_thought)

                    # Update session state with new thought and phrases
                    st.session_state.generated_thoughts.append(new_thought)
                    st.session_state.key_phrases.extend(new_key_phrases)

                    # Limit stored thoughts and phrases
                    st.session_state.generated_thoughts = st.session_state.generated_thoughts[-7:]
                    st.session_state.key_phrases = st.session_state.key_phrases[-20:]

                    return new_thought

            except Exception as e:
                st.error(f"Attempt {attempt + 1} failed: {e}")

        # Fallback if unique thought cannot be generated
        return "Today is a new opportunity. Your strength is always greater than your challenges."

    def render_app(self):
        """Main app rendering method"""
        # App Title and Introduction
        st.title("Soulful Reflections")

        st.subheader("Hey! I'm here to brighten your day. Share how you're feeling, and I'll provide personalized reflections based on your mood."
        )

        # Mood Selection
        selected_moods = self.render_mood_selector()

        # Thought Display Placeholder
        thought_placeholder = st.empty()

        # Initial or Current Thought
        if 'current_thought' not in st.session_state or not selected_moods:
            # Default thought if no mood selected
            default_thought = "Every moment is a chance to begin again. You are stronger than you know."
            st.session_state.current_thought = default_thought

        # Display Current Thought
        thought_placeholder.markdown(
            f"<h3 style='text-align: center;'>{st.session_state.current_thought}</h3>",
            unsafe_allow_html=True
        )

        # New Inspiration Button
        if st.button("Get New Inspiration"):
            # Ensure moods are selected
            if selected_moods:
                with st.spinner('Generating new inspiration...'):
                    new_thought = self.generate_unique_thought(selected_moods)
                    st.session_state.current_thought = new_thought

                # Update thought display
                thought_placeholder.markdown(
                    f"<h3 style='text-align: center;'>{new_thought}</h3>",
                    unsafe_allow_html=True
                )
            else:
                st.warning("Please select at least one mood to generate an inspiration.")


# Run the app
if __name__ == "__main__":
    app = SoulfulReflectionsApp()
    app.render_app()