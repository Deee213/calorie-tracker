import os
import re
import json
import streamlit as st
from google import genai
from PIL import Image

# Page Configuration
st.set_page_config(page_title="Running & Calorie Tracker", page_icon="🏃", layout="centered")

# Daily Targets
DAILY_TARGET_KCAL = 1650
TARGET_PROTEIN = 110
TARGET_CARBS = 190
TARGET_FAT = 50

# Check API Key
api_key = os.environ.get("AQ.Ab8RN6JGWnJMPkmo42vxRItg5-8HTINXHfm57HgJndonTK53RQ")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing!")
    st.info("Please set it in PowerShell before running Streamlit:")
    st.code('$env:GEMINI_API_KEY="your_api_key_here"', language="powershell")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# Initialize Session State
if "total_kcal" not in st.session_state:
    st.session_state.total_kcal = 0
if "total_protein" not in st.session_state:
    st.session_state.total_protein = 0
if "total_carbs" not in st.session_state:
    st.session_state.total_carbs = 0
if "total_fat" not in st.session_state:
    st.session_state.total_fat = 0
if "logged_meals" not in st.session_state:
    st.session_state.logged_meals = []

# Header
st.title("🏃 AI Calorie & Macro Tracker")
st.caption("Upload your meal image to estimate calories and macros toward your 1,650 kcal target.")

# Sidebar Progress
st.sidebar.header("📊 Daily Progress")
remaining_kcal = DAILY_TARGET_KCAL - st.session_state.total_kcal

st.sidebar.metric(
    label="Calories Remaining", 
    value=f"{remaining_kcal} kcal", 
    delta=f"Target: {DAILY_TARGET_KCAL} kcal"
)
st.sidebar.progress(min(max(st.session_state.total_kcal / DAILY_TARGET_KCAL, 0.0), 1.0))

st.sidebar.subheader("Macro Totals")
st.sidebar.write(f"🥩 **Protein:** {st.session_state.total_protein}g / {TARGET_PROTEIN}g")
st.sidebar.write(f"🍞 **Carbs:** {st.session_state.total_carbs}g / {TARGET_CARBS}g")
st.sidebar.write(f"🥑 **Fat:** {st.session_state.total_fat}g / {TARGET_FAT}g")

if st.sidebar.button("Reset Daily Tracker"):
    st.session_state.total_kcal = 0
    st.session_state.total_protein = 0
    st.session_state.total_carbs = 0
    st.session_state.total_fat = 0
    st.session_state.logged_meals = []
    st.rerun()

# Meal Upload Section
uploaded_file = st.file_uploader("Upload a picture of your meal", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Meal", use_container_width=True)

    if st.button("Estimate & Log Meal"):
        with st.spinner("Analyzing meal ingredients and calculating macros..."):
            prompt = """
            Analyze this food image. Provide:
            1. An itemized breakdown of food items with portion estimates.
            2. Estimated total Calories (kcal), Protein (g), Carbohydrates (g), and Fat (g).
            
            End your response strictly with a JSON block in this format:
            ```json
            {
                "meal_name": "Short summary of meal",
                "calories": 500,
                "protein": 30,
                "carbs": 60,
                "fat": 15
            }
            ```
            """
            
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[image, prompt]
                )
                
                analysis_text = response.text
                st.markdown("### Analysis Breakdown")
                st.write(analysis_text)

                # Extract JSON
                json_match = re.search(r"```json\n(.*?)\n```", analysis_text, re.DOTALL)
                if json_match:
                    meal_data = json.loads(json_match.group(1))
                    
                    st.session_state.total_kcal += meal_data.get("calories", 0)
                    st.session_state.total_protein += meal_data.get("protein", 0)
                    st.session_state.total_carbs += meal_data.get("carbs", 0)
                    st.session_state.total_fat += meal_data.get("fat", 0)
                    st.session_state.logged_meals.append(meal_data)
                    
                    st.success(f"Logged {meal_data.get('meal_name')}! ({meal_data.get('calories')} kcal)")
                    st.rerun()

            except Exception as e:
                st.error(f"Error processing image: {e}")

# Display Logged Meals
if st.session_state.logged_meals:
    st.markdown("---")
    st.subheader("📝 Today's Logged Meals")
    for idx, meal in enumerate(st.session_state.logged_meals, 1):
        st.write(
            f"**{idx}. {meal.get('meal_name')}** — "
            f"{meal.get('calories')} kcal | P: {meal.get('protein')}g | "
            f"C: {meal.get('carbs')}g | F: {meal.get('fat')}g"
        )