import streamlit as st
import os

# --- 0. WYMUSZENIE AKTUALIZACJI (HACK NA BŁĘDY 404) ---
# To naprawia problem, gdy serwer Streamlit "udaje", że nie widzi modeli.
try:
    os.system('pip install -U google-generativeai')
except:
    pass

import google.generativeai as genai

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Apteka Pana Boga - Asystent",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS (NOWA SZATA GRAFICZNA - JASNA I CZYSTA) ---
st.markdown("""
<style>
    /* RESET: Wymuszenie jasnego tła (Paper Style) */
    .stApp {
        background-color: #fdfefc !important;
        background-image: linear-gradient(to bottom, #fdfefc, #f4f8f0);
        color: #1a2e12 !important;
    }

    /* SIDEBAR (Pasek boczny) */
    section[data-testid="stSidebar"] {
        background-color: #f0f4ec !important;
        border-right: 1px solid #dce4d9;
    }
    section[data-testid="stSidebar"] * {
        color: #2c4a22 !important;
    }

    /* POLA TEKSTOWE (Naprawa ciemnych elementów) */
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
    .stTextArea label p {
        color: #2c4a22 !important;
        font-weight: 600 !important;
    }

    /* PRZYCISKI */
    .stButton button {
        background: linear-gradient(135deg, #6da356, #4a7a3a) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 10px 30px !important;
        transition: transform 0.2s;
    }
    .stButton button:hover {
        transform: scale(1.02);
    }

    /* KARTA WYNIKU (Wygląd książkowy) */
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
    
    /* Ukrycie stopki Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. KONFIGURACJA API I MODELU ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # TU JEST KLUCZ DO SUKCESU:
        # Używamy modelu 'gemini-pro-latest'. 
        # Był on na Twojej liście diagnostycznej, więc NIE ZWRÓCI błędu 404.
        # Jest to model "myślący" (PRO), idealny do Twojego promptu.
        model = genai.GenerativeModel('gemini-pro-latest')
        
    else:
        st.error("⚠️ Brak klucza API w Secrets. Uzupełnij go w ustawieniach aplikacji.")
        st.stop()
except Exception as e:
    # Fallback - gdyby jednak coś poszło nie tak, próba awaryjna
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
    except:
        st.error(f"Błąd połączenia: {e}")
        st.stop()

# --- 4. TWÓJ PROMPT (Ten, który działa najlepiej) ---
SYSTEM_PROMPT = """
Jesteś zaawansowanym systemem eksperckim dedykowanym wyłącznie wiedzy zawartej w książce Marii Treben pt. "Apteka Pana Boga". 

TWOJE ŹRÓDŁO WIEDZY:
Korzystasz ze swojej wewnętrznej wiedzy treningowej na temat tej książki. Znasz jej treść "na pamięć". Nie wymyślaj niczego, co nie zostało napisane przez Marię Treben. Jeśli autorka nie podała lekarstwa na daną chorobę, poinformuj o tym uczciwie.

ZASADA NACZELNA:
Użytkownik otrzymuje gotową instrukcję "krok po kroku".

STRUKTURA ODPOWIEDZI (WYMAGANA):
Użyj pogrubionych nagłówków dla każdej sekcji.

### 1. DIAGNOZA I GŁÓWNA KURACJA
- Wskaż konkretne rośliny lub mieszanki.
- Krótko wyjaśnij "dlaczego".

### 2. PRECYZYJNY PROCES PRZYGOTOWANIA (Krok po kroku)
- Zdefiniuj proces fizyczny: NAPAR, MACERAT NA ZIMNO czy ODWAR?
- Podaj dokładne proporcje.

### 3. DAWKOWANIE I METODYKA SPOŻYWANIA
- Ile razy dziennie? Kiedy? Temperatura.

### 4. TERAPIA WSPOMAGAJĄCA
- Okłady, kąpiele, dieta (jeśli dotyczy).

### 5. KONTROLA JAKOŚCI ZIOŁA
- Jak rozpoznać dobre zioło.

### 6. CZAS KURACJI
- Szacowany czas leczenia.

### 7. ZIOŁA W TEJ KURACJI (Techniczne)
Na samym końcu, w osobnej linii:
"NAZWY_LACIŃSKIE: Nazwa1, Nazwa2"
"""

# --- 5. FUNKCJA POMOCNICZA ---
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

# --- 6. PASEK BOCZNY ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/herbal-medicine.png", width=80)
    st.header("📖 O Projekcie")
    
    st.info(
        """
        **Idea projektu:**
        Aplikacja powstała, aby ocalić od zapomnienia starą wiedzę zielarską i podać ją w nowoczesnej, łatwo dostępnej formie.
        """
    )
    
    st.warning(
        """
        **⚠️ Nota prawna:**
        Treści mają charakter edukacyjny. Nie zastępują porady lekarza.
        """
    )
    st.markdown("---")
    st.caption("Autor: Karol hagiroshyy | Silnik: Gemini Pro Latest")

# --- 7. GŁÓWNY EKRAN ---
st.markdown("<h1 style='color: #2c4a22;'>🌿 Apteka Pana Boga</h1>", unsafe_allow_html=True)

# Nowy tekst powitalny (Twój)
st.markdown("""
<div style="background-color: #f0f7ee; padding: 20px; border-radius: 10px; border-left: 5px solid #6da356; margin-bottom: 25px; color: #1a2e12;">
    <h3 style="margin-top: 0; color: #2c4a22;">Witaj serdecznie w wirtualnej Aptece Pana Boga! 🌿</h3>
    <p style="font-size: 1.05rem;">
        Bardzo dziękuję, że zdecydowałeś się skorzystać z tego asystenta. 
        Jego autorem jest <b>Karol hagiroshyy</b>.
    </p>
    <p style="font-size: 1.05rem;">
        Jestem gotowy do pomocy. Napisz po prostu, co Ci dolega (np. <i>"bóle pleców"</i>, <i>"problemy z żołądkiem"</i>).
    </p>
</div>
""", unsafe_allow_html=True)

# Formularz
with st.form("diagnosis_form"):
    user_query = st.text_area(
        "Opisz tutaj swoje dolegliwości:",
        placeholder="Wpisz objawy, np. zgaga, ból wątroby, łuszczyca...",
        height=100
    )
    # Wyśrodkowanie przycisku
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.form_submit_button("🔍 Znajdź Kurację", type="primary", use_container_width=True)

# Logika
if submit_button and user_query:
    if len(user_query) < 3:
        st.warning("Proszę wpisać co najmniej jedno słowo określające dolegliwość.")
    else:
        with st.spinner('Kartkuję "Aptekę Pana Boga" (analiza Gemini Pro)...'):
            try:
                full_prompt = f"{SYSTEM_PROMPT}\n\nPACJENT ZGŁASZA: {user_query}"
                response = model.generate_content(full_prompt)
                
                clean_response, plant_names = get_plant_images(response.text)

                # Wyświetlenie karty z wynikiem
                st.markdown(f"""
                <div class="result-card">
                    {clean_response}
                </div>
                """, unsafe_allow_html=True)

                # Zdjęcia (Rysunki botaniczne)
                if plant_names:
                    st.markdown("<br><h3 style='color: #2c4a22;'>📸 Zioła w tej kuracji:</h3>", unsafe_allow_html=True)
                    cols = st.columns(len(plant_names))
                    for i, plant_name in enumerate(plant_names):
                        # Zmiana na 'botanical drawing' dla ładniejszego efektu
                        img_url = f"https://tse2.mm.bing.net/th?q={plant_name.replace(' ', '+')}+botanical+drawing&w=300&h=300&c=7"
                        with cols[i]:
                            st.image(img_url, caption=plant_name, use_column_width=True)

            except Exception as e:
                st.error("Wystąpił błąd połączenia.")
                st.error(f"Szczegóły: {e}")
                if "404" in str(e):
                     st.info("Wskazówka: Twoje konto może wymagać innej nazwy modelu. Spróbuj zmienić 'gemini-pro-latest' na 'gemini-flash-latest' w kodzie.")
