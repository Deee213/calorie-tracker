from datetime import datetime
import hashlib
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

# --- WARM CREAM AESTHETIC STYLING (FORCED LIGHT MODE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Force global light theme override to prevent dark mode invisibility */
    html, body, [class*="css"], div, span, p, label, h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #1c1917 !important;
    }

    .stApp {
        background-color: #f7f4ee !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 4rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        max-width: 480px !important;
    }

    .warm-card {
        background-color: #ffffff;
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.03);
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

    button[data-baseweb="tab"] p {
        color: #44403c !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #f97316 !important;
    }

    /* Input styling fixes for clean contrast */
    input, textarea, select {
        background-color: #ffffff !important;
        color: #1c1917 !important;
        border: 1px solid #e7e5e4 !important;
        border-radius: 12px !important;
    }
    
    input::placeholder, textarea::placeholder {
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
    st.stop()
client = genai.Client(api_key=api_key.strip())

# --- MULTI-USER STORAGE HELPERS ---
USERS_FILE = "users_data.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_all_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_all_users(users_data):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users_data, f, indent=4)
    except Exception as e:
        st.error(f"Failed to save user database: {e}")

# --- SESSION STATE INITIALIZATION FOR AUTH ---
if "user" not in st.session_state:
    st.session_state.user = None

all_users = load_all_users()

# --- AUTHENTICATION SCREEN ---
if not st.session_state.user:
    st.markdown("<h2 style='text-align: center; color: #1c1917; margin-bottom: 20px;'>🥗 Daily Macro Tracker</h2>", unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    with tab_login:
        with st.form("login_form"):
            username_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password", help="Click the eye icon on the right to toggle password visibility")
            submit_login = st.form_submit_button("Login", use_container_width=True)
            
            if submit_login:
                if username_input in all_users and all_users[username_input]["password"] == hash_password(password_input):
                    st.session_state.user = username_input
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab_register:
        with st.form("register_form"):
            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Choose Password", type="password", help="Click the eye icon on the right to toggle password visibility")
            submit_reg = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit_reg:
                if not new_user or not new_pass:
                    st.warning("Please fill in both fields.")
                elif new_user in all_users:
                    st.error("Username already taken. Please choose another.")
                else:
                    all_users[new_user] = {
                        "password": hash_password(new_pass),
                        "profile": {
                            "age": 25,
                            "gender": "Male",
                            "height": 175,
                            "weight": 75,
                            "target_weight": 68,
                            "activity": "Moderate (3-5 days/week)",
                            "pace": "Normal (~2 kg / month)"
                        },
                        "history": {}
                    }
                    save_all_users(all_users)
                    st.session_state.user = new_user
                    st.success("Account created successfully!")
                    st.rerun()
    st.stop()

# --- LOGGED IN USER DATA SCOPING ---
current_user = st.session_state.user
user_data = all_users[current_user]

p = user_data.get("profile", {
    "age": 25, "gender": "Male", "height": 175, "weight": 75,
    "target_weight": 68, "activity": "Moderate (3-5 days/week)", "pace": "Normal (~2 kg / month)"
})
history = user_data.get("history", {})

today_str = datetime.now().strftime("%Y-%m-%d")
if today_str not in history:
    history[today_str] = []

with st.sidebar:
    st.write(f"Logged in as: **{current_user}**")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.user = None
        st.rerun()

# --- CALCULATE TARGETS BASED ON PROFILE ---
if p["gender"] == "Male":
    bmr = (10 * p["weight"]) + (6.25 * p["height"]) - (5 * p["age"]) + 5
else:
    bmr = (10 * p["weight"]) + (6.25 * p["height"]) - (5 * p["age"]) - 161

activity_multipliers = {
    "Sedentary (little or no exercise)": 1.2,
    "Light (1-3 days/week)": 1.375,
    "Moderate (3-5 days/week)": 1.55,
    "Active (6-7 days/week)": 1.725
}
tdee = bmr * activity_multipliers.get(p["activity"], 1.55)

pace_deficits = {
    "Normal (~2 kg / month)": 500,
    "Aggressive (~3.5 kg / month)": 750,
    "⚡ Rush / Fast (~4.5+ kg / month)": 1000
}
daily_deficit = pace_deficits.get(p["pace"], 500)
target_calories = max(1200, int(tdee - daily_deficit))

target_protein = int((target_calories * 0.30) / 4)
target_carbs = int((target_calories * 0.40) / 4)
target_fat = int((target_calories * 0.30) / 9)

TARGETS = {
    "calories": target_calories,
    "protein": target_protein,
    "carbs": target_carbs,
    "fat": target_fat
}

monthly_loss_kg = round((daily_deficit * 30) / 7700, 1)

# --- TODAY'S METRICS ---
today_meals = history[today_str]
total_calories = sum(m.get("calories", 0) for m in today_meals)
total_protein = sum(m.get("protein", 0) for m in today_meals)
total_carbs = sum(m.get("carbs", 0) for m in today_meals)
total_fat = sum(m.get("fat", 0) for m in today_meals)
remaining_calories = max(0, TARGETS["calories"] - total_calories)

fat_pct = min(100, int((total_fat / TARGETS["fat"]) * 100)) if TARGETS["fat"] else 0
prot_pct = min(100, int((total_protein / TARGETS["protein"]) * 100)) if TARGETS["protein"] else 0
carb_pct = min(100, int((total_carbs / TARGETS["carbs"]) * 100)) if TARGETS["carbs"] else 0

fat_angle = fat_pct * 3.6
prot_angle = fat_angle + (prot_pct * 3.6)
carb_angle = min(360, prot_angle + (carb_pct * 3.6))
conic_bg = f"conic-gradient(#3b82f6 0deg {fat_angle}deg, #eab308 {fat_angle}deg {prot_angle}deg, #22c55e {prot_angle}deg {carb_angle}deg, #f3f0e6 {carb_angle}deg 360deg)"

# --- MAIN NUTRITION SUMMARY CARD ---
st.markdown(f"""
    <div class="warm-card">
        <div class="goal-header">
            <span style="font-size: 1.2rem;">⚡</span>
            <div>
                <div class="goal-title">Calorie Goal: {TARGETS['calories']:,} kcal</div>
                <div class="goal-sub">Remaining only {remaining_calories:,} kcal • Est. Loss: <b>~{monthly_loss_kg} kg/mo</b></div>
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
            ✨ Welcome back, {current_user}! Mode: {p['pace'].split(' ')[0]}
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NAVIGATION TABS ---
nav_tab1, nav_tab2, nav_tab3, nav_tab4 = st.tabs(["👤 Profile", "📸 Log Meal", "📋 Today", "📅 History"])

with nav_tab1:
    st.markdown("### Your Personal Details")
    st.caption("Update your body metrics below. Targets and monthly weight loss estimates will adjust automatically.")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=10, max_value=100, value=int(p["age"]))
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=int(p["height"]))
            weight = st.number_input("Current Weight (kg)", min_value=30.0, max_value=250.0, value=float(p["weight"]))
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female"], index=0 if p["gender"]=="Male" else 1)
            target_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=250.0, value=float(p["target_weight"]))
            activity_options = [
                "Sedentary (little or no exercise)",
                "Light (1-3 days/week)",
                "Moderate (3-5 days/week)",
                "Active (6-7 days/week)"
            ]
            current_act_index = activity_options.index(p["activity"]) if p["activity"] in activity_options else 2
            activity = st.selectbox("Activity Level", activity_options, index=current_act_index)

        st.markdown("---")
        st.markdown("### Weight Loss Speed & Rush Mode")
        pace_options = [
            "Normal (~2 kg / month)", 
            "Aggressive (~3.5 kg / month)", 
            "⚡ Rush / Fast (~4.5+ kg / month)"
        ]
        current_pace_index = pace_options.index(p["pace"]) if p["pace"] in pace_options else 0
        pace = st.selectbox("Select Weight Loss Pace", pace_options, index=current_pace_index)

        submitted = st.form_submit_button("💾 Save Profile & Recalculate", use_container_width=True)
        if submitted:
            all_users[current_user]["profile"] = {
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "target_weight": target_weight,
                "activity": activity,
                "pace": pace
            }
            save_all_users(all_users)
            st.success("Profile updated successfully!")
            st.rerun()

with nav_tab2:
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

        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(model=model_name, contents=contents)
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

                    all_users[current_user]["history"][today_str].append(data)
                    save_all_users(all_users)
                    st.success(f"Logged: {data.get('meal_name', 'Meal')} ({data.get('calories', 0)} kcal)")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

with nav_tab3:
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
                        all_users[current_user]["history"][today_str].pop(real_idx)
                        save_all_users(all_users)
                        st.rerun()

with nav_tab4:
    if not history:
        st.info("No historical logs available.")
    else:
        for date_key in sorted(history.keys(), reverse=True):
            day_meals = history[date_key]
            day_calories = sum(m.get("calories", 0) for m in day_meals)
            
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