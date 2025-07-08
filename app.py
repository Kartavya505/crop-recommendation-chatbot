import streamlit as st
from streamlit_chat import message
import joblib
import re
import random
import matplotlib.pyplot as plt

# Load model and label encoder
model = joblib.load('crop_recommendation_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')

# Crop explanation database
crop_info = {
    "rice": "Rice grows well in areas with high rainfall, high humidity, and warm temperatures.",
    "maize": "Maize requires moderate rainfall and warm temperatures.",
    "cotton": "Cotton thrives in black soil with high temperature and moderate rainfall.",
    "jute": "Jute grows best in hot and humid climates with high rainfall.",
    "lentil": "Lentils prefer cool growing seasons and loamy soil with good drainage.",
    "banana": "Bananas grow well in hot, humid areas with high rainfall.",
    "mango": "Mango trees require warm, frost-free climate and well-drained soil.",
    "apple": "Apples need a temperate climate with cold winters and well-drained loamy soil."
}

# Fertilizer database
fertilizer_info = {
    "rice": "Apply urea (N), DAP (P), and MOP (K) in 3 split doses.",
    "maize": "Use NPK 20-20-0 at sowing and top dress with urea after 20 days.",
    "cotton": "Apply 100 kg urea, 50 kg DAP, and 50 kg potash per acre.",
    "jute": "Use compost, urea (40–60 kg/ha), and super phosphate.",
    "lentil": "Apply DAP and potash during sowing; avoid waterlogging.",
    "banana": "Use well-rotted manure, urea, and NPK 2:1:1 ratio monthly.",
    "mango": "Apply FYM, urea, and NPK mix before flowering season.",
    "apple": "Use compost + NPK 10:10:10 before flowering and during fruit setting."
}

# Season info
season_info = {
    "rice": "June to August (Kharif season)",
    "maize": "June to July or October to November",
    "cotton": "April to May (hot season)",
    "jute": "March to May (just before monsoon)",
    "lentil": "October to November (Rabi season)",
    "banana": "Any month with irrigation (preferably Feb–Mar)",
    "mango": "June to August or February to March for grafting",
    "apple": "December to February (cold regions)"
}

# Water requirement
water_info = {
    "rice": "1200-1600 mm. Needs standing water.",
    "maize": "500-800 mm. Moderate irrigation.",
    "cotton": "700-1200 mm. Dry at maturity.",
    "jute": "1500-2000 mm. Avoid waterlogging.",
    "lentil": "350-450 mm. Semi-arid conditions.",
    "banana": "2000-2500 mm. Frequent irrigation.",
    "mango": "900-1200 mm. Needs dry spell before flowering.",
    "apple": "1000-1200 mm. Avoid waterlogging."
}

# Similar crops
similar_crops = {
    "rice": ["sugarcane", "wheat"],
    "maize": ["sorghum", "millet"],
    "cotton": ["soybean", "sunflower"],
    "jute": ["hemp", "flax"],
    "lentil": ["gram", "pea"],
    "banana": ["papaya", "plantain"],
    "mango": ["guava", "sapota"],
    "apple": ["pear", "plum"]
}

# Organic vs chemical info
organic_vs_chemical = {
    "rice": "Organic improves soil but may reduce yield. Chemicals act faster.",
    "maize": "Organic composts enhance soil; chemicals give rapid results.",
    "cotton": "Organic cotton fetches more price. Chemicals resist pests.",
    "jute": "Organic jute is eco-friendly. Chemicals boost yield.",
    "lentil": "Use Rhizobium culture for nitrogen fixation.",
    "banana": "Organic bananas are sweeter. Use vermicompost.",
    "mango": "Organic mangoes taste better. Avoid sprays.",
    "apple": "Use organic mulch. Chemicals may leave residues."
}

# Streamlit page
st.set_page_config(layout="wide")
st.title("🌾 Smart Crop Buddy – Chatbot")

# Session state setup
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'inputs' not in st.session_state:
    st.session_state.inputs = {}
if 'last_crop' not in st.session_state:
    st.session_state.last_crop = None
if 'last_inputs' not in st.session_state:
    st.session_state.last_inputs = {}

# Prediction
def predict_crop(n, p, k, temp, humidity, ph, rainfall):
    data = [[n, p, k, temp, humidity, ph, rainfall]]
    prediction = model.predict(data)
    return label_encoder.inverse_transform(prediction)[0]

# Extract values
def extract_values(text):
    text = text.lower()
    patterns = {
        'n': r"(?:n\b|nitrogen)(?:\s*(?:=|is|:)?\s*)(\d+\.?\d*)",
        'p': r"(?:p\b|phosphorus)(?:\s*(?:=|is|:)?\s*)(\d+\.?\d*)",
        'k': r"(?:k\b|potassium)(?:\s*(?:=|is|:)?\s*)(\d+\.?\d*)",
        'temp': r"(?:temp(?:erature)?)(?:\s*(?:=|is|:)?\s*)(\d+\.?\d*)",
        'humidity': r"(?:humidity)(?:\s*(?:=|is|:)?\s*)(\d+\.?\d*)",
        'ph': r"(?:p[hH])(?:\s*(?:=|is|:)?\s*)(\d+\.?\d*)",
        'rain': r"(?:rainfall|rain)(?:\s*(?:=|is|:)?\s*)(\d+\.?\d*)"
    }
    extracted = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            extracted[key] = float(match.group(1))
    return extracted

def extract_crop_name(text):
    for crop in crop_info.keys():
        if crop.lower() in text.lower():
            return crop.lower()
    return None

# Handle user message
def handle_query(query):
    extracted = extract_values(query)
    st.session_state.inputs.update(extracted)

    follow_up = query.lower()

    if any(phrase in follow_up for phrase in ["i want to grow", "suggest conditions for", "how to grow"]):
        crop_name = extract_crop_name(query)
        if crop_name:
            st.session_state.last_crop = crop_name
            return (
                f"🌾 To grow **{crop_name.capitalize()}**, here are the ideal conditions:\n\n"
                f"📘 _Why?_ {crop_info.get(crop_name)}\n\n"
                f"💧 _Water:_ {water_info.get(crop_name)}\n\n"
                f"📅 _Best Season:_ {season_info.get(crop_name)}\n\n"
                f"🧪 _Fertilizer Tip:_ {fertilizer_info.get(crop_name)}"
            )

    if st.session_state.last_crop:
        crop = st.session_state.last_crop
        if "fertilizer" in follow_up:
            return f"🧪 For **{crop.capitalize()}**, use:\n\n{fertilizer_info.get(crop)}"
        elif "season" in follow_up:
            return f"📅 Best planting time for **{crop.capitalize()}**:\n\n{season_info.get(crop)}"
        elif "water" in follow_up:
            return f"💧 Water needs for **{crop.capitalize()}**:\n\n{water_info.get(crop)}"
        elif "organic" in follow_up:
            return f"🌿 Organic vs Chemical for **{crop.capitalize()}**:\n\n{organic_vs_chemical.get(crop)}"
        elif "similar" in follow_up:
            return f"🌱 Similar crops to **{crop.capitalize()}**: {', '.join(similar_crops.get(crop))}"

    if extracted:
        noted = ', '.join(f"{k.upper()}: {v}" for k, v in extracted.items())
        st.session_state.messages.append(("bot", f"✅ Got it: {noted}"))

    required = ['n', 'p', 'k', 'temp', 'humidity', 'ph', 'rain']
    missing = [k for k in required if k not in st.session_state.inputs]
    pretty = {
        'n': 'Nitrogen', 'p': 'Phosphorus', 'k': 'Potassium',
        'temp': 'Temperature', 'humidity': 'Humidity', 'ph': 'pH', 'rain': 'Rainfall'
    }

    if missing:
        ask = ', '.join(pretty[m] for m in missing)
        return f"🤖 Just need your {ask} to make the best suggestion! 🌿"

    vals = st.session_state.inputs
    crop = predict_crop(vals['n'], vals['p'], vals['k'], vals['temp'], vals['humidity'], vals['ph'], vals['rain'])
    st.session_state.last_crop = crop.lower()
    st.session_state.last_inputs = vals.copy()
    st.session_state.inputs.clear()

    info = crop_info.get(crop.lower(), "")
    fertilizer = fertilizer_info.get(crop.lower(), "")
    season = season_info.get(crop.lower(), "")

    suggestions = [
        "✅ Want tips for increasing yield?",
        "💧 Curious how much water your crop needs?",
        "🌱 Want to know similar crops for your climate?",
        "🛆 Ask what fertilizer brands are good.",
        "🧪 Curious about organic vs chemical farming?"
    ]

    return (
        f"🌿 I recommend **{crop.capitalize()}** based on your inputs!\n\n"
        f"📘 _Why?_ {info}\n\n"
        f"🧪 _Fertilizer Tip:_ {fertilizer}\n\n"
        f"📅 _Best Planting Time:_ {season}\n\n"
        f"💬 Try asking: **{random.choice(suggestions)}**"
    )

# Display past messages
for i, (sender, msg) in enumerate(st.session_state.messages):
    message(msg, is_user=(sender == "user"), key=f"{sender}_{i}")

# Input form at bottom
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("👨‍🌾 Type your message...", key="input_text")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.messages.append(("user", user_input))
    response = handle_query(user_input)
    if response:
        st.session_state.messages.append(("bot", response))

        # Show NPK chart if available
        if st.session_state.last_inputs:
            vals = st.session_state.last_inputs
            fig, ax = plt.subplots()
            ax.bar(["Nitrogen", "Phosphorus", "Potassium"], [vals['n'], vals['p'], vals['k']], color=["green", "blue", "orange"])
            ax.set_ylabel("Value")
            ax.set_title(f"NPK for {st.session_state.last_crop.title()}")
            st.pyplot(fig)

  
