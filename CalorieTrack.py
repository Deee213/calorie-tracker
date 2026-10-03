import json
import os
from PIL import Image
import streamlit as st
from google import genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Calorie Tracker",
    page_icon="🥗",
    layout="centered"
)

# --- API KEY INITIALIZATION ---
# Checks Streamlit Cloud Secrets first, then falls back to local environment variables
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing!")
    st.info("Please set GEMINI_API_KEY in Streamlit Cloud Secrets or set it in environment variables.")
    st.stop()

# Clean key string and initialize Gemini Client explicitly
api_key = api_key.strip()
client = genai.Client(api_key=api_key)

# --- SESSION STATE (DAILY MACROS) ---
# Default targets: 1,650 kcal, 110g Protein, 190g Carbs, 50g Fat
if "logged_meals" not in st.session_state:
    st.session_state.logged_meals = []

TARGETS = {
    "calories": 1650,
    "protein": 110,
    "carbs": 190,
    "fat": 50
}

# --- HEADER & PROGRESS ---
st.title("🥗 Daily Macro Tracker")

# Calculate current totals
total_calories = sum(m.get("calories", 0) for m in st.session_state.logged_meals)
total_protein = sum(m.get("protein", 0) for m in st.session_state.logged_meals)
total_carbs = sum(m.get("carbs", 0) for m in st.session_state.logged_meals)
total_fat = sum(m.get("fat", 0) for m in st.session_state.logged_meals)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Calories", f"{total_calories} / {TARGETS['calories']} kcal")
col2.metric("Protein", f"{total_protein} / {TARGETS['protein']}g")
col3.metric("Carbs", f"{total_carbs} / {TARGETS['carbs']}g")
col4.metric("Fat", f"{total_fat} / {TARGETS['fat']}g")

st.progress(min(total_calories / TARGETS["calories"], 1.0))

st.divider()

# --- INPUT SECTION ---
st.subheader("📸 Log a Meal")

input_method = st.radio("Choose input method:", ["Camera / Upload", "Text Description"], horizontal=True)

meal_image = None
text_description = ""

if input_method == "Camera / Upload":
    uploaded_file = st.file_uploader("Take a photo or upload an image of your food", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        meal_image = Image.open(uploaded_file)
        st.image(meal_image, caption="Uploaded Meal", use_container_width=True)
else:
    text_description = st.text_area("Describe what you ate (e.g., '2 scrambled eggs with 1 slice of whole wheat toast'):")

# --- GEMINI ANALYSIS FUNCTION ---
def analyze_meal(image=None, text=""):
    prompt = """
    Analyze this food item and provide an estimated breakdown of macros in JSON format ONLY.
    Return exact key-value pairs without markdown formatting:
    {
      "meal_name": "Short descriptive name",
      "calories": integer,
      "protein": integer_in_grams,
      "carbs": integer_in_grams,
      "fat": integer_in_grams
    }
    """
    
    contents = [prompt]
    if image:
        contents.append(image)
    if text:
        contents.append(f"Description: {text}")

    # Explicitly using gemini-3.8-flash model endpoint
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=contents
    )
    return response.text

if st.button("Analyze & Log Meal", type="primary"):
    if not meal_image and not text_description:
        st.warning("Please upload an image or enter a text description.")
    else:
        with st.spinner("Analyzing macros with Gemini AI..."):
            try:
                result_text = analyze_meal(image=meal_image, text=text_description)
                
                # Strip markdown code fencing if returned
                clean_json = result_text.strip().replace("```json", "").replace("```", "")
                data = json.loads(clean_json)

                st.session_state.logged_meals.append(data)
                st.success(f"Logged: {data.get('meal_name', 'Meal')} ({data.get('calories', 0)} kcal)")
                st.rerun()

            except Exception as e:
                st.error(f"Error analyzing meal: {e}")

# --- LOGGED MEALS HISTORY ---
if st.session_state.logged_meals:
    st.divider()
    st.subheader("📋 Today's Meals")
    for idx, meal in enumerate(st.session_state.logged_meals, 1):
        st.write(
            f"**{idx}. {meal.get('meal_name', 'Meal')}** — "
            f"{meal.get('calories', 0)} kcal | "
            f"P: {meal.get('protein', 0)}g | "
            f"C: {meal.get('carbs', 0)}g | "
            f"F: {meal.get('fat', 0)}g"
        )
    
    if st.button("Reset Daily Tracker"):
        st.session_state.logged_meals = []
        st.rerun()