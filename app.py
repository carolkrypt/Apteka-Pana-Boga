import streamlit as st
import google.generativeai as genai

# --- 1. Konfiguracja strony ---
st.set_page_config(
    page_title="Apteka Pana Boga - Asystent",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS (Stylizacja - Zielony/Ekologiczny klimat) ---
st.markdown("""
<style>
    /* TŁO I KOLORY */
    .stApp {
        background-color: #fcfdfa;
        background-image: linear-gradient(to bottom right, #fcfdfa, #f0f4ec);
        color: #1a4011;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #e6ebe0 !important;
        border-right: 1px solid #d1d9cc;
    }
    section[data-testid="stSidebar"] * {
        color: #2c3e28 !important;
    }

    /* ALERTY */
    div[data-testid="stInfo"] { background-color: #e8f4f8 !important; color: #0f3c4b !important; }
    div[data-testid="stWarning"] { background-color: #fff9e6 !important; color: #5c4b12 !important; }
    
    /* NAGŁÓWKI */
    h1, h2, h3 { color: #2c5e1e !important; font-family: 'Georgia', serif; }
    
    /* POLE TEKSTOWE */
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #dde6d5 !important;
    }
    .stTextArea textarea:focus { border-color: #6c9e5b !important; box-shadow: 0 0 10px rgba(108, 158, 91, 0.2) !important; }
    
    /* PRZYCISK */
    .stButton button {
        background: linear-gradient(to bottom, #5d9c4b, #3e7a2e) !important;
        color: white !important;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
    }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }

    /* KARTA WYNIKU */
    .result-card {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 15px;
        border-left: 8px solid #5d9c4b;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-top: 20px;
        font-family: 'Helvetica', sans-serif;
        line-height: 1.7;
        color: #333333;
    }
    .stMarkdown a { display: none; }
</style>
""", unsafe_allow_html=True)

# --- 3. Konfiguracja API Google ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # --- TU JEST ZMIANA ---
    # Wybieramy model z Twojej listy diagnostycznej.
    # 'gemini-2.0-flash' jest bardzo szybki i nowoczesny.
    model = genai.GenerativeModel('gemini-2.0-flash')
    
except Exception:
    st.error("BŁĄD: Brakuje klucza API w Streamlit Secrets.")
    st.stop()

# --- 4. System Prompt (Mózg Zielarza) ---
SYSTEM_PROMPT = """
Jesteś ekspertem od książki Marii Treben "Apteka Pana Boga".
Twoim zadaniem jest tworzenie gotowych protokołów leczniczych.

ZASADY:
1. Opieraj się TYLKO na wiedzy z "Apteki Pana Boga".
2. Bądź konkretny (podawaj przepisy).
3. Używaj formatowania markdown (pogrubienia, listy).

STRUKTURA ODPOWIEDZI:
### 1. Diagnoza i Zioła
Co stosować i dlaczego.

### 2. Przygotowanie (Dokładny przepis)
Czy to napar, odwar czy macerat? Jakie proporcje? Ile minut parzyć?

### 3. Dawkowanie
Ile razy dziennie? Przed czy po jedzeniu?

### 4. Zalecenia dodatkowe
Okłady, dieta, kąpiele (jeśli dotyczy).

### 5. Zioła (Techniczne)
Na samym końcu, w nowej linii napisz:
"NAZWY_LACIŃSKIE: Nazwa1, Nazwa2" (tylko główne zioła do wyszukania zdjęć).
"""

# --- 5. Funkcje pomocnicze ---
def get_plant_images(text):
    try:
        if "NAZWY_LACIŃSKIE:" in text:
            parts = text.split("NAZWY_LACIŃSKIE:")
            clean_txt = parts[0]
            # Pobieramy nazwy po przecinku
            latin_line = parts[1].strip().split("\n")[0]
            plant_list = [name.strip() for name in latin_line.split(",")]
            return clean_txt, plant_list
    except:
        pass
    return text, []

# --- 6. Interfejs Użytkownika ---
with st.sidebar:
    st.header("📖 O Projekcie")
    st.info("Aplikacja oparta na wiedzy Marii Treben.")
    st.warning("⚠️ Pamiętaj: To nie jest porada lekarska.")
    st.caption("Powered by Gemini 2.0 Flash")

st.title("🌿 Apteka Pana Boga")

st.markdown("""
<div style="background-color: #f0f7ee; padding: 20px; border-radius: 10px; border-left: 5px solid #5d9c4b; margin-bottom: 25px;">
    <h3 style="margin-top: 0; color: #2c5e1e;">Witaj w wirtualnej Aptece! 🌿</h3>
    <p style="color: #333;">Napisz co Ci dolega (np. <i>"bóle głowy", "problemy skórne"</i>), a znajdę kurację wg Marii Treben.</p>
</div>
""", unsafe_allow_html=True)

# Formularz
with st.form("my_form"):
    query = st.text_area("Twoje dolegliwości:", height=100)
    submitted = st.form_submit_button("🔍 Znajdź Kurację", type="primary")

if submitted and query:
    if len(query) < 3:
        st.warning("Wpisz dłuższą nazwę dolegliwości.")
    else:
        with st.spinner('Analizuję pisma Marii Treben (Model Gemini 2.0)...'):
            try:
                # Wysłanie zapytania do AI
                response = model.generate_content(f"{SYSTEM_PROMPT}\nPACJENT: {query}")
                
                # Oddzielenie tekstu od nazw ziół (do zdjęć)
                display_text, plants = get_plant_images(response.text)
                
                # Wyświetlenie wyniku w "karcie"
                st.markdown(f'<div class="result-card">{display_text}</div>', unsafe_allow_html=True)
                
                # Wyświetlenie zdjęć (jeśli są)
                if plants:
                    st.markdown("### 📸 Zioła w tej kuracji:")
                    cols = st.columns(len(plants))
                    for i, p in enumerate(plants):
                        # Bezpieczny link do obrazka
                        img = f"https://tse2.mm.bing.net/th?q={p.replace(' ','+')}+plant+botanical&w=300&h=300&c=7"
                        with cols[i]:
                            st.image(img, caption=p)
                            
            except Exception as e:
                st.error(f"Wystąpił błąd: {e}")
