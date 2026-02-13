import streamlit as st
import google.generativeai as genai
from huggingface_hub import InferenceClient
import os
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Logoflow",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for Animation & Styling ---
st.markdown("""
<style>
    /* Animated Gradient Background */
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp {
        background: linear-gradient(-45deg, #1e3c72, #2a5298, #6d1b7b, #a044ff);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: white;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-right: 1px solid #ddd;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #333;
    }
    
    /* Card/Box Styling */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #ced4da;
    }
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 1px solid #ced4da;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        background-color: #ffffff;
        color: #333;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #f8f9fa;
        transform: scale(1.02);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Result Box Styling */
    .generated-name-box {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 15px;
        text-align: center;
        font-weight: bold;
        font-size: 1.5em;
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    h1 {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    h3, h4, h5, p, label, .stMarkdown {
        color: white !important;
    }
    /* Fix sidebar text color override */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #333 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Secure Configuration ---
with st.sidebar:
    # Try to load logo if it exists, otherwise use text
    if os.path.exists("logo.png"):
        st.logo("logo.png", icon_image="logo.png")
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("# 🧠 Logoflow")
    
    st.header("🔐 Security & Setup")
    
    google_api_key = st.text_input("Google Gemini API Key", type="password", help="Required for name generation.")
    hf_api_key = st.text_input("Hugging Face Token", type="password", help="Required for logo generation.")
    
    st.markdown("---")
    st.markdown("### ⚙️ Models")
    
    gemini_model = st.selectbox(
        "Gemini Model",
        ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-pro"],
        help="Select the AI branding expert."
    )
    
    logo_model = st.selectbox(
        "Logo Model",
        ["black-forest-labs/FLUX.1-schnell"],
        help="Model for visual identity (Free Tier)."
    )
    st.caption("Using HF Free Serverless Tier")
    st.markdown("---")


# --- Helper Functions ---

def generate_brand_names(description, api_key, model_name):
    if not api_key: return []
    try:
        genai.configure(api_key=api_key)
        if not model_name: model_name = "gemini-3-flash-preview"
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Act as a world-class branding agency. 
        Project: {description}
        Task: Create 3 unique, modern, and memorable brand names.
        Output: ONLY the 3 names separated by commas. No numbering.
        """
        response = model.generate_content(prompt)
        return [n.strip() for n in response.text.split(',')][:3]
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
             st.error("Model not found. Try Gemini 2.5 Flash.")
        else:
            st.error(f"Gemini Error: {e}")
        return []

def generate_logo(brand_name, description, api_key, model_id):
    if not api_key: return None
    try:
        client = InferenceClient(token=api_key)
        prompt = f"""
        Logo for "{brand_name}". {description}.
        Style: Minimalist, vector, flat, gradient, modern, tech, white background.
        High quality, 4k.
        """
        return client.text_to_image(prompt, model=model_id)
    except Exception as e:
        st.error(f"Logo Error: {e}")
        return None

# --- Main Interface ---

# Header
col_logo, col_title = st.columns([1, 5])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    else:
        st.markdown("## ✨")
with col_title:
    st.title("Logoflow")
    st.markdown("#### *Your AI Branding Partner*")

# Logic to Gate Content
if not google_api_key or not hf_api_key:
    st.container()
    st.markdown("---")
    st.info("👋 **Welcome to Logoflow!**")
    st.markdown("""
    To get started, please enter your **API Keys** in the sidebar.
    
    - **Google Gemini Key**: For generating creative brand names.
    - **Hugging Face Token**: For designing your unique logo.
    
    *Your keys are safe and not stored anywhere.*
    """)
    st.stop() # Stop execution here until keys are provided

# Main Content (Only visible if keys are present)
st.markdown("---")

# Step 1: Input
st.markdown("### 1. Vision Board")
project_description = st.text_area(
    "Describe your project idea, vibe, and target audience:",
    height=120,
    placeholder="Example: A futuristic sneaker brand for urban runners. Values: Speed, Technology, Sustainability."
)

if st.button("🚀 Launch Branding Session", type="primary"):
    if not project_description:
        st.warning("Please describe your vision first.")
    else:
        with st.spinner("🔮 Summoning creativity..."):
            names = generate_brand_names(project_description, google_api_key, gemini_model)
            if names:
                st.session_state['generated_names'] = names
                st.session_state['selected_name'] = None
                st.success("Brand names crystallized!")

st.markdown("---")

# Step 2 & 3: Selection and Logo
c1, c2 = st.columns([1, 1], gap="large")

with c1:
    if 'generated_names' in st.session_state:
        st.markdown("### 2. Choose Identity")
        choice = st.radio(
            "Select the name that resonates:",
            st.session_state['generated_names'],
            index=None
        )
        if choice:
            st.session_state['selected_name'] = choice
            st.markdown(f"<div class='generated-name-box'>{choice}</div>", unsafe_allow_html=True)

with c2:
    if 'selected_name' in st.session_state and st.session_state['selected_name']:
        st.markdown("### 3. Visual Mark")
        current_name = st.session_state['selected_name']
        
        if st.button(f"🎨 Design Logo for {current_name}"):
            with st.spinner("🎨 Painting pixels..."):
                logo_image = generate_logo(current_name, project_description, hf_api_key, logo_model)
                if logo_image:
                    st.image(logo_image, caption=f"Identity for {current_name}", use_container_width=True)
                    st.balloons()


