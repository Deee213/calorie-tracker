from datetime import datetime
import json
import os
import time
from PIL import Image
import streamlit as st
from google import genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Daily Macro Tracker",
    page_icon="🥗",
    layout="centered"
)

# --- MODERN AESTHETIC CSS & MOBILE OPTIMIZATION ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    html, body, [class*="css"], div, span, p {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Force seamless container sizing for mobile */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 500px !important;
    }

    /* Main Remaining Calories Highlight Box */
    .summary-card {
        background: linear-gradient(135deg, #1e1e24 0%, #2a2a36 100%);
        border: 1px solid #3f3f4e;
        border-radius: 18px;
        padding: 18px 14px;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        margin-bottom: 16px;
    }

    .summary-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #a1a1aa;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .summary-value {
        font-size: 2.8rem;
        font-weight: 800;
        color: #6366f1;
        line-height: 1.1;
    }

    /* Responsive 2x2 Grid Macro Cards for Mobile */
    .macro-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 12px;
    }

    .macro-card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 14px;
        padding: 12px 10px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .macro-label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }

    .cal-text { color: #818cf8; }
    .prot-text { color: #c084fc; }
    .carb-text { color: #34d399; }
    .fat-text { color: #facc15; }

    .macro-value {
        font-size: 1.15rem;
        font-weight: 800;
        color: #f4f4f5;
    }

    .macro-sub {
        font-size: 0.7rem;
        color: #71717a;
        margin-top: 2px;
    }

    /* Tab Customizations */
    button[data-baseweb="tab"] {
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- API KEY INITIALIZATION ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing!")
    st.stop()

api_key = api_key.strip()
client = genai.Client(api_key=api_key)

# --- SESSION STATE & TARGETS ---
TARGETS = {
    "calories": 1650,
    "protein": 110,
    "carbs": 190,
    "fat": 50
}

today_str = datetime.now().strftime("%Y-%m-%d")

if "history" not in st.session_state:
    st.session_state.history = {}

if today_str not in st.session_state.history:
    st.session_state.history[today_str] = []

today_meals = st.session_state.history[today_str]

# Calculate Totals
total_calories = sum(m.get("calories", 0) for m in today_meals)
total_protein = sum(m.get("protein", 0) for m in today_meals)
total_carbs = sum(m.get("carbs", 0) for m in today_meals)
total_fat = sum(m.get("fat", 0) for m in today_meals)

remaining_calories = max(0, TARGETS["calories"] - total_calories)

# --- HEADER & DASHBOARD ---
st.title("🥗 Daily Macro Tracker")

# Summary Dashboard Box
st.markdown(f"""
    <div class="summary-card">
        <div class="summary-title">Remaining Calories</div>
        <div class="summary-value">{remaining_calories}</div>
        <div class="macro-grid">
            <div class="macro-card">
                <div class="macro-label cal-text">Calories</div>
                <div class="macro-value">{total_calories}</div>
                <div class="macro-sub">of {TARGETS['calories']} kcal</div>
            </div>
            <div class="macro-card">
                <div class="macro-label prot-text">Protein</div>
                <div class="macro-value">{total_protein}g</div>
                <div class="macro-sub">of {TARGETS['protein']}g</div>
            </div>
            <div class="macro-card">
                <div class="macro-label carb-text">Carbs</div>
                <div class="macro-value">{total_carbs}g</div>
                <div class="macro-sub">of {TARGETS['carbs']}g</div>
            </div>
            <div class="macro-card">
                <div class="macro-label fat-text">Fat</div>
                <div class="macro-value">{total_fat}g</div>
                <div class="macro-sub">of {TARGETS['fat']}g</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NAVIGATION TABS ---
nav_tab1, nav_tab2, nav_tab3 = st.tabs(["📸 Log Meal", "📋 Today's Log", "📅 History"])

# --- TAB 1: LOG MEAL ---
with nav_tab1:
    method = st.radio("Input Type", ["Text Description", "Camera / Upload"], horizontal=True, label_visibility="collapsed")
    
    meal_image = None
    text_description = ""

    if method == "Text Description":
        text_description = st.text_area(
            "Describe your meal:",
            placeholder="e.g., 2 scrambled eggs with 1 slice of toast...",
            height=100
        )
    else:
        uploaded_file = st.file_uploader("Snap or upload meal picture", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            meal_image = Image.open(uploaded_file)
            st.image(meal_image, caption="Meal Preview", use_container_width=True)

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

        models_to_try = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents
                )
                return response.text
            except Exception:
                time.sleep(1)
                continue
        raise Exception("API server is busy. Please try logging again.")

    if st.button("✨ Analyze & Log Meal", type="primary", use_container_width=True):
        if not meal_image and not text_description:
            st.warning("Please enter a description or upload an image.")
        else:
            with st.spinner("Analyzing macros..."):
                try:
                    result_text = analyze_meal(image=meal_image, text=text_description)
                    clean_json = result_text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(clean_json)
                    data["time"] = datetime.now().strftime("%I:%M %p")

                    st.session_state.history[today_str].append(data)
                    st.success(f"Logged: {data.get('meal_name', 'Meal')} ({data.get('calories', 0)} kcal)")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 2: TODAY'S LOG ---
with nav_tab2:
    if not today_meals:
        st.info("No meals logged today yet.")
    else:
        for idx, item in enumerate(reversed(today_meals)):
            real_idx = len(today_meals) - 1 - idx
            with st.container(border=True):
                col_info, col_del = st.columns([5, 1])
                with col_info:
                    st.markdown(f"**{item.get('meal_name', 'Meal')}** ({item.get('time', '')})")
                    st.caption(
                        f"🔥 {item.get('calories', 0)} kcal | "
                        f"🥩 P: {item.get('protein', 0)}g | "
                        f"🍞 C: {item.get('carbs', 0)}g | "
                        f"🥑 F: {item.get('fat', 0)}g"
                    )
                with col_del:
                    if st.button("🗑️", key=f"del_{real_idx}"):
                        st.session_state.history[today_str].pop(real_idx)
                        st.rerun()

# --- TAB 3: DAILY HISTORY ---
with nav_tab3:
    if not st.session_state.history:
        st.info("No historical data available.")
    else:
        for date_key in sorted(st.session_state.history.keys(), reverse=True):
            day_meals = st.session_state.history[date_key]
            day_calories = sum(m.get("calories", 0) for m in day_meals)
            
            with st.expander(f"📆 **{date_key}** — **{day_calories} kcal**"):
                for m in day_meals:
                    st.write(f"• **{m.get('meal_name', 'Meal')}**: {m.get('calories', 0)} kcal")