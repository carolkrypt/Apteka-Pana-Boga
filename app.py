import streamlit as st
import os

# --- BRUTALNA AKTUALIZACJA BIBLIOTEKI (HACK) ---
# To polecenie wymusza pobranie najnowszych narzędzi Google
# bezpośrednio przed uruchomieniem aplikacji.
try:
    os.system('pip install -U google-generativeai')
except:
    pass

import google.generativeai as genai

# --- 1. Konfiguracja strony ---
st.set_page_config(
    page_title="Apteka Pana Boga",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(to bottom right, #fcfdfa, #f0f4ec); color: #1a4011; }
    div[data-testid="stSidebar"] { background-color: #e6ebe0 !important; }
    h1, h2, h3 { color: #2c5e1e !important; font-family: 'Georgia', serif; }
    .result-card { background: white; padding: 40px; border-radius: 15px; border-left: 8px solid #5d9c4b; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# --- 3. Konfiguracja API ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # --- TU JEST ZMIANA KLUCZOWA ---
        # Zamiast 'gemini-1.5-flash' (którego nie masz na liście),
        # używamy aliasu, który BYŁ na Twojej liście diagnostycznej.
        model = genai.GenerativeModel('gemini-flash-latest')
        
    else:
        st.error("⚠️ Brak klucza API w Secrets. Aplikacja nie zadziała.")
        st.stop()
except Exception as e:
    st.error(f"Błąd konfiguracji: {e}")
    st.stop()

# --- 4. Prompt ---
SYSTEM_PROMPT = """
Jesteś ekspertem od książki Marii Treben "Apteka Pana Boga".
Twoim zadaniem jest tworzenie gotowych protokołów leczniczych.
Opieraj się TYLKO na tej książce.

STRUKTURA:
1. Diagnoza i zioła.
2. Przepis (dokładny: napar/odwar/macerat).
3. Dawkowanie.
4. Na samym końcu w nowej linii: "NAZWY_LACIŃSKIE: Nazwa1, Nazwa2"
"""

def get_plant_images(text):
    try:
        if "NAZWY_LACIŃSKIE:" in text:
            parts = text.split("NAZWY_LACIŃSKIE:")
            return parts[0], [x.strip() for x in parts[1].split(",")]
    except: pass
    return text, []

# --- 5. Interfejs ---
with st.sidebar:
    st.header("📖 O Projekcie")
    st.caption("Powered by Gemini (Flash Latest)")

st.title("🌿 Apteka Pana Boga")

with st.form("my_form"):
    q = st.text_area("Twoje dolegliwości:", height=100)
    submitted = st.form_submit_button("🔍 Znajdź Kurację", type="primary")

if submitted and q:
    with st.spinner('Szukam w zapiskach...'):
        try:
            # Generowanie
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
            st.error(f"Wystąpił błąd: {e}")
            # Jeśli ten model też zawiedzie, podpowiedź co robić
            if "404" in str(e):
                st.info("Spróbuj zmienić w kodzie 'gemini-flash-latest' na 'gemini-pro'.")
            elif "429" in str(e):
                st.info("Przekroczono limity zapytań.")
