import streamlit as st
import google.generativeai as genai

# --- 1. Konfiguracja strony ---
st.set_page_config(
    page_title="Apteka Pana Boga - Asystent",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS (Style - WYMUSZENIE JASNEGO MOTYWU I POPRAWA KOLORÓW) ---
st.markdown("""
<style>
    /* 1. GŁÓWNE TŁO - Jasny beż/złamana biel (niezależnie od trybu dark mode) */
    .stApp {
        background-color: #fcfdfa;
        background-image: linear-gradient(to bottom right, #fcfdfa, #f0f4ec);
        color: #1a4011;
    }

    /* 2. SIDEBAR (Pasek boczny) - Wymuszamy jasne tło */
    section[data-testid="stSidebar"] {
        background-color: #e6ebe0 !important; /* Jasna zieleń */
        border-right: 1px solid #d1d9cc;
    }
    /* Tekst w sidebarze */
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] li, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] span {
        color: #2c3e28 !important; /* Ciemna zieleń */
    }

    /* 3. ALERTY (Niebieskie i Żółte pola) - Naprawa kolorów */
    /* Info (Niebieskie) */
    div[data-testid="stInfo"] {
        background-color: #e8f4f8 !important;
        color: #0f3c4b !important;
        border: 1px solid #b8dae6;
    }
    /* Warning (Żółte) */
    div[data-testid="stWarning"] {
        background-color: #fff9e6 !important;
        color: #5c4b12 !important;
        border: 1px solid #faecc2;
    }
    /* Tekst wewnątrz alertów */
    div[data-testid="stAlert"] p {
        color: inherit !important;
    }

    /* 4. NAGŁÓWKI */
    h1, h2, h3, h4 {
        color: #2c5e1e !important;
        font-family: 'Georgia', serif;
    }

    /* 5. POLE TEKSTOWE */
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #000000 !important; /* Zawsze czarny tekst */
        border: 2px solid #dde6d5 !important;
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stTextArea textarea:focus {
        border-color: #6c9e5b !important;
        box-shadow: 0 0 10px rgba(108, 158, 91, 0.2) !important;
    }
    /* Etykieta nad polem tekstowym */
    .stTextArea label {
        color: #2c5e1e !important;
        font-weight: bold;
    }

    /* 6. PRZYCISK */
    .stButton button {
        background: linear-gradient(to bottom, #5d9c4b, #3e7a2e) !important;
        color: white !important;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    /* 7. KARTA WYNIKU */
    .result-card {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 15px;
        border: 1px solid #e0e6da;
        border-left: 8px solid #5d9c4b; /* Zielony akcent */
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-top: 20px;
        font-family: 'Helvetica', sans-serif;
        line-height: 1.7;
        color: #333333;
    }

    /* Ukrycie linków */
    .stMarkdown a { display: none; }
</style>
""", unsafe_allow_html=True)

# --- 3. Konfiguracja API Google ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
except Exception:
    st.error("BŁĄD: Brakuje klucza API. Upewnij się, że ustawiłeś 'GEMINI_API_KEY' w Streamlit Secrets.")
    st.stop()

# --- 4. SYSTEM PROMPT ---
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

# --- 5. Funkcja pomocnicza ---
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

# --- 6. Pasek Boczny (Sidebar) ---
with st.sidebar:
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
        Treści mają charakter edukacyjny i opierają się na literaturze ludowej z XX wieku. Nie zastępują porady lekarza.
        """
    )
    st.markdown("---")
    st.caption("Autor: Karol hagiroshyy | Powered by Gemini Pro")

# --- 7. Główny Ekran ---
st.title("🌿 Apteka Pana Boga")

# --- NOWY TEKST POWITALNY ---
st.markdown("""
<div style="background-color: #f0f7ee; padding: 20px; border-radius: 10px; border-left: 5px solid #5d9c4b; margin-bottom: 25px;">
    <h3 style="margin-top: 0; color: #2c5e1e;">Witaj serdecznie w wirtualnej Aptece Pana Boga! 🌿</h3>
    <p style="font-size: 1.05rem; color: #333;">
        Bardzo dziękuję, że zdecydowałeś się skorzystać z tego asystenta. 
        Jego autorem jest <b>Karol hagiroshyy</b>, który stworzył to narzędzie, aby ułatwić Ci szybki dostęp do sprawdzonej wiedzy Marii Treben.
    </p>
    <p style="font-size: 1.05rem; color: #333;">
        Jestem gotowy do pomocy. Napisz po prostu, co Ci dolega (np. <i>"bóle pleców"</i>, <i>"problemy z żołądkiem"</i>), 
        a wspólnie znajdziemy odpowiednią kurację ziołową.
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
    submit_button = st.form_submit_button("🔍 Znajdź Kurację", type="primary")

# Logika
if submit_button and user_query:
    if len(user_query) < 3:
        st.warning("Proszę wpisać co najmniej jedno słowo określające dolegliwość.")
    else:
        with st.spinner('Kartkuję "Aptekę Pana Boga"...'):
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

                # Zdjęcia
                if plant_names:
                    st.markdown("### 📸 Zioła w tej kuracji:")
                    cols = st.columns(len(plant_names))
                    for i, plant_name in enumerate(plant_names):
                        img_url = f"https://tse2.mm.bing.net/th?q={plant_name.replace(' ', '+')}+botanical+photo&w=300&h=300&c=7&rs=1&p=0&dpr=3&pid=1.7&mkt=en-US&adlt=moderate"
                        with cols[i]:
                            st.image(img_url, caption=plant_name, use_column_width=True)

            except Exception as e:
                st.error(f"Wystąpił błąd połączenia: {e}")
