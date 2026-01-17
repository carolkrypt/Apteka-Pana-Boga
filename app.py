import streamlit as st
import google.generativeai as genai
import time

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Apteka Pana Boga", page_icon="🌿", layout="wide")

# --- STYLE CSS (Twoje, ładne) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(to bottom right, #fcfdfa, #f0f4ec); color: #1a4011; }
    div[data-testid="stSidebar"] { background-color: #e6ebe0 !important; }
    h1, h2, h3 { color: #2c5e1e !important; font-family: 'Georgia', serif; }
    .result-card { background: white; padding: 30px; border-radius: 15px; border-left: 6px solid #5d9c4b; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
    .stButton button { background: linear-gradient(to bottom, #5d9c4b, #3e7a2e) !important; color: white !important; border: none; border-radius: 25px; }
</style>
""", unsafe_allow_html=True)

# --- INICJALIZACJA MODELU (PANCERNA) ---
def get_working_model():
    """Próbuje połączyć się z najlepszym dostępnym modelem."""
    try:
        # Pobieramy klucz
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
        else:
            st.error("❌ Brak klucza API w Secrets!")
            st.stop()
            
        genai.configure(api_key=api_key)
        
        # Lista modeli do sprawdzenia (od najlepszego)
        models_to_try = [
            'gemini-1.5-flash',       # Priorytet: Szybki i tani
            'models/gemini-1.5-flash', # Inny zapis
            'gemini-1.5-pro',         # Alternatywa: Mądry
            'gemini-pro',             # Ostateczność: Stary, ale stabilny
        ]
        
        # Pętla sprawdzająca
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                return model, model_name # Zwracamy działający model
            except Exception:
                continue # Jak błąd, próbujemy następny
                
        # Jak żaden nie działa:
        st.error("❌ Żaden model nie odpowiada. Sprawdź klucz API.")
        st.stop()
        
    except Exception as e:
        st.error(f"Krytyczny błąd konfiguracji: {e}")
        st.stop()

# Uruchamiamy funkcję wyboru modelu
model, active_model_name = get_working_model()

# --- PROMPT ZIELARZA ---
SYSTEM_PROMPT = """
Jesteś ekspertem od "Apteki Pana Boga" Marii Treben.
1. Diagnoza.
2. Przepis (dokładny: napar/odwar).
3. Dawkowanie.
4. Na końcu w nowej linii: NAZWY_LACIŃSKIE: Nazwa1, Nazwa2
"""

def get_plant_images(text):
    try:
        if "NAZWY_LACIŃSKIE:" in text:
            parts = text.split("NAZWY_LACIŃSKIE:")
            return parts[0], [x.strip() for x in parts[1].split(",")]
    except: pass
    return text, []

# --- INTERFEJS ---
with st.sidebar:
    st.header("📖 O Projekcie")
    st.info("Baza wiedzy Marii Treben.")
    # Informacja techniczna, żebyś wiedział co działa
    st.caption(f"✅ Połączono z: {active_model_name}")

st.title("🌿 Apteka Pana Boga")

with st.form("my_form"):
    q = st.text_area("Opisz dolegliwości:", height=100)
    submitted = st.form_submit_button("Znajdź Kurację", type="primary")

if submitted and q:
    with st.spinner('Szukam w zapiskach...'):
        try:
            # Próba generowania
            response = model.generate_content(f"{SYSTEM_PROMPT}\nPACJENT: {q}")
            
            text, plants = get_plant_images(response.text)
            st.markdown(f'<div class="result-card">{text}</div>', unsafe_allow_html=True)
            
            if plants:
                st.markdown("### 📸 Zioła:")
                cols = st.columns(len(plants))
                for i, p in enumerate(plants):
                    with cols[i]:
                        st.image(f"https://tse2.mm.bing.net/th?q={p.replace(' ','+')}+plant&w=300&h=300&c=7", caption=p)
                        
        except Exception as e:
            # Jeśli wywali błąd podczas generowania (np. 429), pokaż go ładnie
            st.error(f"Wystąpił błąd podczas generowania odpowiedzi: {e}")
            if "429" in str(e):
                st.warning("Przekroczono limit zapytań. Odczekaj chwilę.")
