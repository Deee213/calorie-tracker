from datetime import datetime
import json
import os
from PIL import Image
import streamlit as st
from google import genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Daily Macro Tracker",
    page_icon="🥗",
    layout="wide"
)

# --- CUSTOM CSS FOR DASHBOARD LOOK ---
st.markdown("""
    <style>
    /* Dark Card Styling */
    .dashboard-card {
        background-color: #1e1e24;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Custom Ring Containers */
    .ring-container {
        text-align: center;
        padding: 10px;
    }
    
    .ring-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .ring-cal { border: 6px solid #4f46e5; background: #111827; }
    .ring-prot { border: 6px solid #a855f7; background: #111827; }
    .ring-carb { border: 6px solid #10b981; background: #111827; }
    .ring-fat { border: 6px solid #eab308; background: #111827; }

    .ring-val { font-size: 1.3rem; font-weight: bold; color: #ffffff; }
    .ring-sub { font-size: 0.75rem; color: #9ca3af; }
    .ring-label { font-size: 0.85rem; color: #d1d5db; margin-bottom: 4px; font-weight: 600; }
    
    /* Modern Input Area Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2a2a32;
        border-radius: 6px;
        color: #9ca3af;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- API KEY INITIALIZATION ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing!")
    st.info("Please set GEMINI_API_KEY in Streamlit Cloud Secrets or set it in environment variables.")
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

# Initialize historical daily logs dictionary
if "history" not in st.session_state:
    st.session_state.history = {}

# Ensure today's entry exists
if today_str not in st.session_state.history:
    st.session_state.history[today_str] = []

today_meals = st.session_state.history[today_str]

# --- HEADER ---
st.title("🥗 Daily Macro Tracker")

# --- TOP DASHBOARD SECTION ---
top_left, top_right = st.columns([2.5, 1])

# Calculate Current Totals for Today
total_calories = sum(m.get("calories", 0) for m in today_meals)
total_protein = sum(m.get("protein", 0) for m in today_meals)
total_carbs = sum(m.get("carbs", 0) for m in today_meals)
total_fat = sum(m.get("fat", 0) for m in today_meals)

remaining_calories = max(0, TARGETS["calories"] - total_calories)

with top_left:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #9ca3af; margin-bottom: 2px;'>Remaining Calories:</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; font-size: 2.8rem; margin-top: 0;'>{remaining_calories}</h1>", unsafe_allow_html=True)
    
    r1, r2, r3, r4 = st.columns(4)
    
    # Calories Ring
    cal_pct = int((total_calories / TARGETS["calories"]) * 100)
    with r1:
        st.markdown(f"""
            <div class="ring-container">
                <div class="ring-label">Calories</div>
                <div class="ring-circle ring-cal">
                    <div class="ring-val">{total_calories}</div>
                </div>
                <div class="ring-sub">{total_calories} of {TARGETS['calories']} ({cal_pct}%)</div>
            </div>
        """, unsafe_allow_html=True)

    # Protein Ring
    with r2:
        st.markdown(f"""
            <div class="ring-container">
                <div class="ring-label">Protein</div>
                <div class="ring-circle ring-prot">
                    <div class="ring-val">{total_protein}g</div>
                    <div class="ring-sub">of {TARGETS['protein']}g</div>
                </div>
                <div class="ring-sub">{total_protein} of {TARGETS['protein']}g</div>
            </div>
        """, unsafe_allow_html=True)

    # Carbs Ring
    with r3:
        st.markdown(f"""
            <div class="ring-container">
                <div class="ring-label">Carbs</div>
                <div class="ring-circle ring-carb">
                    <div class="ring-val">{total_carbs}g</div>
                    <div class="ring-sub">of {TARGETS['carbs']}g</div>
                </div>
                <div class="ring-sub">{total_carbs} of {TARGETS['carbs']}g</div>
            </div>
        """, unsafe_allow_html=True)

    # Fat Ring
    with r4:
        st.markdown(f"""
            <div class="ring-container">
                <div class="ring-label">Fat</div>
                <div class="ring-circle ring-fat">
                    <div class="ring-val">{total_fat}g</div>
                    <div class="ring-sub">of {TARGETS['fat']}g</div>
                </div>
                <div class="ring-sub">{total_fat} of {TARGETS['fat']}g</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# Right Side Panel: Today's Recent Items Log
with top_right:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### Today's Log (Recent Items)")
    st.divider()
    
    if not today_meals:
        st.caption("No meals logged for today yet.")
    else:
        for idx, item in enumerate(reversed(today_meals[-4:])):
            time_str = item.get("time", "")
            st.markdown(f"**Ate: {item.get('meal_name', 'Meal')}** ({item.get('calories', 0)} cal)")
            st.caption(f"🕒 {time_str} | P:{item.get('protein',0)}g C:{item.get('carbs',0)}g F:{item.get('fat',0)}g")
            st.divider()
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN NAVIGATION TABS ---
nav_tab1, nav_tab2 = st.tabs(["📸 Log a Meal", "📅 Daily Calorie History"])

# --- TAB 1: LOG MEAL ---
with nav_tab1:
    st.subheader("📸 Log a Meal")
    st.write("Analyze & Log Method")
    
    # Input tabs: TEXT and CAMERA (Voice removed)
    method_tab1, method_tab2 = st.tabs(["TEXT", "CAMERA"])
    
    meal_image = None
    text_description = ""

    with method_tab1:
        text_description = st.text_area(
            "Describe what you ate (e.g., '2 scrambled eggs with 1 slice of whole wheat toast'):",
            placeholder="Describe what you ate...",
            height=120,
            max_chars=500
        )

    with method_tab2:
        uploaded_file = st.file_uploader("Snap or upload an image of your meal", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            meal_image = Image.open(uploaded_file)
            st.image(meal_image, caption="Meal Preview", width=300)

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

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents
        )
        return response.text

    if st.button("Analyze & Log Meal 💫", type="primary"):
        if not meal_image and not text_description:
            st.warning("Please upload an image or enter a text description.")
        else:
            with st.spinner("Analyzing macros with Gemini AI..."):
                try:
                    result_text = analyze_meal(image=meal_image, text=text_description)
                    clean_json = result_text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(clean_json)
                    
                    # Add timestamp
                    data["time"] = datetime.now().strftime("%I:%M %p")

                    st.session_state.history[today_str].append(data)
                    st.success(f"Logged: {data.get('meal_name', 'Meal')} ({data.get('calories', 0)} kcal)")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error analyzing meal: {e}")

# --- TAB 2: DAILY CALORIE HISTORY ---
with nav_tab2:
    st.subheader("📅 Daily Intake History")
    
    if not st.session_state.history:
        st.info("No history recorded yet.")
    else:
        # Sort dates descending (newest first)
        for date_key in sorted(st.session_state.history.keys(), reverse=True):
            day_meals = st.session_state.history[date_key]
            day_calories = sum(m.get("calories", 0) for m in day_meals)
            day_protein = sum(m.get("protein", 0) for m in day_meals)
            day_carbs = sum(m.get("carbs", 0) for m in day_meals)
            day_fat = sum(m.get("fat", 0) for m in day_meals)
            
            with st.expander(f"📆 **{date_key}** — Total Intake: **{day_calories} kcal**"):
                h_col1, h_col2, h_col3, h_col4 = st.columns(4)
                h_col1.metric("Calories", f"{day_calories} / {TARGETS['calories']} kcal")
                h_col2.metric("Protein", f"{day_protein}g / {TARGETS['protein']}g")
                h_col3.metric("Carbs", f"{day_carbs}g / {TARGETS['carbs']}g")
                h_col4.metric("Fat", f"{day_fat}g / {TARGETS['fat']}g")
                
                st.divider()
                st.markdown("**Meals Logged:**")
                if not day_meals:
                    st.caption("No meals recorded for this day.")
                else:
                    for m_idx, m in enumerate(day_meals, 1):
                        st.write(
                            f"{m_idx}. **{m.get('meal_name', 'Meal')}** ({m.get('time', '')}) — "
                            f"{m.get('calories', 0)} kcal | P: {m.get('protein', 0)}g | C: {m.get('carbs', 0)}g | F: {m.get('fat', 0)}g"
                        )