import streamlit as st
import os
import time

# --- 1. WYMUSZENIE AKTUALIZACJI ---
try:
    os.system('pip install -U google-generativeai')
except:
    pass

import google.generativeai as genai

# --- 2. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Apteka Pana Boga - Asystent",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. CSS (JASNY MOTYW) ---
st.markdown("""
<style>
    .stApp {
        background-color: #fdfefc !important;
        background-image: linear-gradient(to bottom, #fdfefc, #f4f8f0);
        color: #1a2e12 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #f0f4ec !important;
        border-right: 1px solid #dce4d9;
    }
    section[data-testid="stSidebar"] * {
        color: #2c4a22 !important;
    }
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #1a2e12 !important;
        border: 2px solid #cbdbc2 !important;
        border-radius: 10px;
    }
    .stTextArea textarea:focus {
        border-color: #6da356 !important;
        box-shadow: 0 0 8px rgba(109, 163, 86, 0.3) !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #6da356, #4a7a3a) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 10px 30px !important;
    }
    .result-card {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 4px;
        border: 1px solid #e0e6da;
        border-left: 6px solid #6da356;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        font-family: 'Georgia', serif;
        line-height: 1.8;
        color: #2b2b2b;
        margin-top: 20px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 4. KONFIGURACJA API I MODELU ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # --- ZMIANA NA MODEL PRO (STANDARDOWY) ---
        # Wersja 1.5 PRO jest bardzo mądra (dużo lepsza od Flasha).
        # W darmowym planie ma limit 2 zapytań na minutę.
        # Dla jednego użytkownika to wystarczy, a jakość odpowiedzi będzie wysoka.
        model = genai.GenerativeModel('gemini-1.5-pro')
        
    else:
        st.error("⚠️ Brak klucza API w Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Błąd połączenia: {e}")
    st.stop()

# --- 5. ULEPSZONY PROMPT (BARDZIEJ PRECYZYJNY) ---
SYSTEM_PROMPT = """
Jesteś wybitnym ekspertem od książki Marii Treben "Apteka Pana Boga". 
Twoim celem jest idealne odwzorowanie zaleceń autorki.

BARDZO WAŻNE INSTRUKCJE:
1. Nie ogólnikuj. Jeśli Maria Treben podaje konkretne zioło na konkretną chorobę (np. Widłak na marskość/stłuszczenie wątroby, a nie tylko Krwawnik), musisz wskazać to najsilniejsze ziele.
2. Rozróżniaj lekkie dolegliwości od ciężkich.
3. Bazuj TYLKO na "Aptece Pana Boga".

STRUKTURA ODPOWIEDZI:
### 1. Diagnoza i Główne Zioła
Wskaż najsilniejsze zioło zalecane przez Treben na tę konkretną dolegliwość. Wyjaśnij dlaczego.

### 2. Przepis i Przygotowanie
Dokładna instrukcja (napar/odwar/macerat). Pamiętaj: Widłaka i Tataraku nigdy nie gotujemy!

### 3. Dawkowanie
Ile razy dziennie? Przed czy po jedzeniu?

### 4. Zalecenia Dodatkowe
Dieta, okłady (np. ze ziół szwedzkich), kąpiele.

### 5. Techniczne
W nowej linii na samym dole:
NAZWY_LACIŃSKIE: Nazwa1, Nazwa2
"""

# --- 6. FUNKCJA POMOCNICZA ---
def get_plant_images(text):
    try:
        if "NAZWY_LACIŃSKIE:" in text:
            parts = text.split("NAZWY_LACIŃSKIE:")
            clean_text = parts[0]
            latin_line = parts[1].strip().split("\n")[0]
            plant_names = [name.strip() for name in latin_line.split(",")]
            return clean_text, plant_names
    except Exception:
        return text, []
    return text, []

# --- 7. PASEK BOCZNY ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/herbal-medicine.png", width=80)
    st.header("📖 O Projekcie")
    st.info("Ekspercka wiedza Marii Treben.")
    st.warning("⚠️ Nota prawna: Treści edukacyjne. Skonsultuj się z lekarzem.")
    st.markdown("---")
    st.caption("Silnik: Gemini 1.5 PRO (High Intelligence)")

# --- 8. GŁÓWNY EKRAN ---
st.markdown("<h1 style='color: #2c4a22;'>🌿 Apteka Pana Boga</h1>", unsafe_allow_html=True)

st.markdown("""
<div style="background-color: #f0f7ee; padding: 20px; border-radius: 10px; border-left: 5px solid #6da356; margin-bottom: 25px; color: #1a2e12;">
    <h3 style="margin-top: 0; color: #2c4a22;">Witaj w wirtualnej Aptece! 🌿</h3>
    <p>Napisz co Ci dolega, a znajdę <b>dokładną</b> kurację wg Marii Treben.</p>
</div>
""", unsafe_allow_html=True)

with st.form("diagnosis_form"):
    user_query = st.text_area("Opisz dolegliwości:", height=100)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.form_submit_button("🔍 Znajdź Precyzyjną Kurację", type="primary", use_container_width=True)

if submit_button and user_query:
    if len(user_query) < 3:
        st.warning("Wpisz dolegliwość.")
    else:
        with st.spinner('Analizuję pisma Marii Treben (Tryb PRO)...'):
            try:
                full_prompt = f"{SYSTEM_PROMPT}\n\nPACJENT ZGŁASZA: {user_query}"
                response = model.generate_content(full_prompt)
                
                clean_response, plant_names = get_plant_images(response.text)

                st.markdown(f'<div class="result-card">{clean_response}</div>', unsafe_allow_html=True)

                if plant_names:
                    st.markdown("<br><h3 style='color: #2c4a22;'>📸 Zioła:</h3>", unsafe_allow_html=True)
                    cols = st.columns(len(plant_names))
                    for i, plant_name in enumerate(plant_names):
                        img_url = f"https://tse2.mm.bing.net/th?q={plant_name.replace(' ', '+')}+botanical+drawing&w=300&h=300&c=7"
                        with cols[i]:
                            st.image(img_url, caption=plant_name, use_column_width=True)

            except Exception as e:
                st.error("Wystąpił błąd.")
                # Jeśli PRO 1.5 też ma limit, to wyświetli ten komunikat
                if "429" in str(e):
                     st.warning("⚠️ Model PRO jest obciążony. Odczekaj minutę i spróbuj ponownie (limit darmowy to 2 zapytania/min).")
                else:
                    st.error(f"{e}")
