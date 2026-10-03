from datetime import datetime, timedelta
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

# --- WARM CREAM AESTHETIC STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Global Typography & Light Background */
    html, body, [class*="css"], div, span, p, label {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #1c1917 !important;
    }

    .stApp {
        background-color: #f7f4ee !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 4rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 480px !important;
    }

    /* Top Date Calendar Selector Pill Box */
    div[data-testid="stColumn"] {
        background-color: #efeae1;
        border-radius: 20px;
        padding: 8px 0px;
        text-align: center;
    }

    .day-pill-name {
        font-size: 0.7rem;
        font-weight: 600;
        color: #78716c !important;
    }

    .day-pill-num {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1c1917 !important;
    }

    /* Active Day Pill (Orange) */
    .day-pill-active {
        background-color: #f97316 !important;
        border-radius: 16px;
        padding: 4px 0px;
        box-shadow: 0 4px 10px rgba(249, 115, 22, 0.3);
    }

    .day-pill-active .day-pill-name, 
    .day-pill-active .day-pill-num {
        color: #ffffff !important;
    }

    /* Main Summary Card Wrapper */
    .warm-card {
        background-color: #ffffff;
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.03);
        margin-top: 10px;
        margin-bottom: 16px;
        border: 1px solid #f0ece1;
    }

    .goal-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 14px;
    }

    .goal-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1c1917 !important;
    }

    .goal-sub {
        font-size: 0.8rem;
        color: #78716c !important;
    }

    /* Donut Ring & Macro Progress Layout */
    .donut-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
    }

    .donut-circle {
        position: relative;
        width: 130px;
        height: 130px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .donut-inner {
        position: absolute;
        width: 96px;
        height: 96px;
        background: #ffffff;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .donut-val {
        font-size: 1.3rem;
        font-weight: 800;
        color: #1c1917 !important;
        line-height: 1;
    }

    .donut-lbl {
        font-size: 0.65rem;
        color: #a8a29e !important;
        margin-top: 2px;
    }

    /* Macro Progress Bars */
    .macro-bar-group {
        flex-grow: 1;
    }

    .macro-bar-item {
        margin-bottom: 10px;
    }

    .macro-bar-header {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #44403c !important;
        margin-bottom: 3px;
    }

    .bar-bg {
        width: 100%;
        height: 6px;
        background-color: #f3f0e6;
        border-radius: 3px;
        overflow: hidden;
    }

    .bar-fill {
        height: 100%;
        border-radius: 3px;
    }

    .bar-fat { background-color: #3b82f6; }
    .bar-protein { background-color: #eab308; }
    .bar-carbs { background-color: #22c55e; }

    .macro-value-sub {
        font-size: 0.72rem;
        color: #78716c !important;
        margin-top: 2px;
    }

    /* Motivation Pill */
    .motivation-pill {
        display: flex;
        align-items: center;
        gap: 6px;
        background-color: #fff7ed;
        padding: 8px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #c2410c !important;
        margin-top: 14px;
    }

    /* Navigation Tabs Contrast Overrides */
    button[data-baseweb="tab"] p {
        color: #44403c !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #f97316 !important;
    }

    /* Form Visibility Overrides */
    textarea, input[type="text"] {
        background-color: #ffffff !important;
        color: #1c1917 !important;
        border: 1px solid #e7e5e4 !important;
        border-radius: 12px !important;
    }

    textarea::placeholder, input::placeholder {
        color: #a8a29e !important;
    }

    header[data-testid="stHeader"] {
        background-color: transparent !important;
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

# --- LOCAL FILE PERSISTENCE HELPERS ---
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_history(history_data):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history_data, f, indent=4)
    except Exception as e:
        st.error(f"Failed to save history: {e}")

# --- SESSION STATE & TARGETS ---
TARGETS = {
    "calories": 2500,
    "protein": 66,
    "carbs": 136,
    "fat": 77
}

today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")

if "history" not in st.session_state:
    st.session_state.history = load_history()

if today_str not in st.session_state.history:
    st.session_state.history[today_str] = []

today_meals = st.session_state.history[today_str]

# Calculate Totals
total_calories = sum(m.get("calories", 0) for m in today_meals)
total_protein = sum(m.get("protein", 0) for m in today_meals)
total_carbs = sum(m.get("carbs", 0) for m in today_meals)
total_fat = sum(m.get("fat", 0) for m in today_meals)

remaining_calories = max(0, TARGETS["calories"] - total_calories)

# Donut Segment Calculations
fat_pct = min(100, int((total_fat / TARGETS["fat"]) * 100)) if TARGETS["fat"] else 0
prot_pct = min(100, int((total_protein / TARGETS["protein"]) * 100)) if TARGETS["protein"] else 0
carb_pct = min(100, int((total_carbs / TARGETS["carbs"]) * 100)) if TARGETS["carbs"] else 0

fat_angle = fat_pct * 3.6
prot_angle = fat_angle + (prot_pct * 3.6)
carb_angle = min(360, prot_angle + (carb_pct * 3.6))

conic_bg = f"conic-gradient(#3b82f6 0deg {fat_angle}deg, #eab308 {fat_angle}deg {prot_angle}deg, #22c55e {prot_angle}deg {carb_angle}deg, #f3f0e6 {carb_angle}deg 360deg)"

# --- TOP DATE CALENDAR STRIP (NATIVE STREAMLIT COLUMNS) ---
cols = st.columns(7)
for idx, i in enumerate(range(-3, 4)):
    dt = today_dt + timedelta(days=i)
    is_today = (i == 0)
    
    with cols[idx]:
        if is_today:
            st.markdown(f"""
                <div class="day-pill-active">
                    <div class="day-pill-name">{dt.strftime('%a')}</div>
                    <div class="day-pill-num">{dt.strftime('%d')}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div>
                    <div class="day-pill-name">{dt.strftime('%a')}</div>
                    <div class="day-pill-num">{dt.strftime('%d')}</div>
                </div>
            """, unsafe_allow_html=True)

# --- MAIN NUTRITION SUMMARY CARD ---
st.markdown(f"""
    <div class="warm-card">
        <div class="goal-header">
            <span style="font-size: 1.2rem;">⚡</span>
            <div>
                <div class="goal-title">Calorie Goal: {TARGETS['calories']:,} kcal</div>
                <div class="goal-sub">Remaining only {remaining_calories:,} kcal</div>
            </div>
        </div>
        <div class="donut-container">
            <div class="donut-circle" style="background: {conic_bg};">
                <div class="donut-inner">
                    <div class="donut-lbl">Consumed</div>
                    <div class="donut-val">{total_calories}</div>
                    <div class="donut-lbl">kcal</div>
                </div>
            </div>
            <div class="macro-bar-group">
                <div class="macro-bar-item">
                    <div class="macro-bar-header">🌀 Fat</div>
                    <div class="bar-bg"><div class="bar-fill bar-fat" style="width: {fat_pct}%;"></div></div>
                    <div class="macro-value-sub"><b>{total_fat}g</b> / {TARGETS['fat']}g</div>
                </div>
                <div class="macro-bar-item">
                    <div class="macro-bar-header">🌽 Protein</div>
                    <div class="bar-bg"><div class="bar-fill bar-protein" style="width: {prot_pct}%;"></div></div>
                    <div class="macro-value-sub"><b>{total_protein}g</b> / {TARGETS['protein']}g</div>
                </div>
                <div class="macro-bar-item">
                    <div class="macro-bar-header">🌾 Carbs</div>
                    <div class="bar-bg"><div class="bar-fill bar-carbs" style="width: {carb_pct}%;"></div></div>
                    <div class="macro-value-sub"><b>{total_carbs}g</b> / {TARGETS['carbs']}g</div>
                </div>
            </div>
        </div>
        <div class="motivation-pill">
            ✨ You are doing great!
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NAVIGATION TABS ---
nav_tab1, nav_tab2, nav_tab3 = st.tabs(["📸 Log Meal", "📋 Today's Meals", "📅 History"])

# --- TAB 1: LOG MEAL ---
with nav_tab1:
    method = st.radio("Input Method", ["Text Description", "Camera / Upload"], horizontal=True, label_visibility="collapsed")
    
    meal_image = None
    text_description = ""

    if method == "Text Description":
        text_description = st.text_area(
            "Describe your meal:",
            placeholder="e.g., Oatmeal with whole milk and berries...",
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
        raise Exception("API server busy. Please try logging again.")

    if st.button("✨ Analyze & Log Meal", type="primary", use_container_width=True):
        if not meal_image and not text_description:
            st.warning("Please describe or upload an image of your meal.")
        else:
            with st.spinner("Analyzing macros..."):
                try:
                    result_text = analyze_meal(image=meal_image, text=text_description)
                    clean_json = result_text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(clean_json)
                    data["time"] = datetime.now().strftime("%I:%M %p")

                    st.session_state.history[today_str].append(data)
                    save_history(st.session_state.history)
                    st.success(f"Logged: {data.get('meal_name', 'Meal')} ({data.get('calories', 0)} kcal)")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 2: TODAY'S MEALS ---
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
                        f"🌀 Fat: {item.get('fat', 0)}g | "
                        f"🌽 Protein: {item.get('protein', 0)}g | "
                        f"🌾 Carbs: {item.get('carbs', 0)}g"
                    )
                with col_del:
                    if st.button("🗑️", key=f"del_{real_idx}"):
                        st.session_state.history[today_str].pop(real_idx)
                        save_history(st.session_state.history)
                        st.rerun()

# --- TAB 3: DAILY HISTORY (CLEAN CARD DISPLAY) ---
with nav_tab3:
    if not st.session_state.history:
        st.info("No historical logs available.")
    else:
        for date_key in sorted(st.session_state.history.keys(), reverse=True):
            day_meals = st.session_state.history[date_key]
            day_calories = sum(m.get("calories", 0) for m in day_meals)
            
            # Format date to display day name (e.g., "Saturday, Oct 03, 2026")
            try:
                formatted_date = datetime.strptime(date_key, "%Y-%m-%d").strftime("%A, %b %d, %Y")
            except Exception:
                formatted_date = date_key

            with st.container(border=True):
                st.markdown(f"🗓️ **{formatted_date}** — **{day_calories:,} kcal**")
                
                if not day_meals:
                    st.caption("No items recorded for this date.")
                else:
                    for m in day_meals:
                        st.markdown(
                            f"• **{m.get('meal_name', 'Meal')}**: {m.get('calories', 0)} kcal "
                            f"(🌀 {m.get('fat', 0)}g Fat | 🌽 {m.get('protein', 0)}g Prot | 🌾 {m.get('carbs', 0)}g Carbs)"
                        )