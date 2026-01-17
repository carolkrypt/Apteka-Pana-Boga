import streamlit as st
import google.generativeai as genai

# --- 1. Konfiguracja strony ---
st.set_page_config(
    page_title="Wirtualny Zielarz Marii Treben",
    page_icon="🌿",
    layout="wide"
)

# --- 2. CSS (Style - Wersja Premium z cieniami i kartami) ---
st.markdown("""
<style>
    /* TŁO APLIKACJI - Delikatny gradient */
    .stApp {
        background: linear-gradient(to bottom right, #f2f7f0, #ffffff);
        color: #1a4011;
    }

    /* NAGŁÓWKI - Szeryfowe, eleganckie */
    h1, h2, h3, h4 {
        color: #2c5e1e !important;
        font-family: 'Georgia', serif;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    /* POLE TEKSTOWE - Efekt poświaty */
    .stTextArea textarea {
        background-color: #ffffff;
        border: 2px solid #dde6d5;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #6c9e5b;
        box-shadow: 0 0 15px rgba(108, 158, 91, 0.3);
    }

    /* PRZYCISK - Wygląd 3D */
    .stButton button {
        background: linear-gradient(to bottom, #4e8c3e, #3a6b2e);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 10px 25px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(46, 107, 30, 0.3);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(46, 107, 30, 0.4);
    }
    .stButton button:active {
        transform: translateY(1px);
    }

    /* KARTA WYNIKU - To daje efekt "papieru" */
    .result-card {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        border-left: 6px solid #4e8c3e;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        margin-top: 20px;
        font-family: 'Helvetica', sans-serif;
        line-height: 1.6;
        color: #2d332a;
    }

    /* Ukrywamy linki pod obrazkami */
    .stMarkdown a {
        display: none;
    }
    
    /* Pasek boczny */
    [data-testid="stSidebar"] {
        background-color: #fcfdfa;
        border-right: 1px solid #efeve6;
    }
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
Użytkownik otrzymuje gotową instrukcję "krok po kroku". Nie odsyłaj do ogólnych źródeł. Ty jesteś źródłem.

STRUKTURA ODPOWIEDZI (WYMAGANA):
Użyj pogrubionych nagłówków dla każdej sekcji.

### 1. DIAGNOZA I GŁÓWNA KURACJA
- Wskaż konkretne rośliny lub mieszanki.
- Krótko wyjaśnij "dlaczego" (wg autorki).

### 2. PRECYZYJNY PROCES PRZYGOTOWANIA (Krok po kroku)
- Zdefiniuj proces fizyczny: CZY TO NAPAR (czas parzenia)? CZY MACERAT NA ZIMNO (np. tatarak/jemioła)? CZY ODWAR?
- Podaj dokładne proporcje.

### 3. DAWKOWANIE I METODYKA SPOŻYWANIA
- Ile razy dziennie? Kiedy (przed/po posiłku)? Temperatura.

### 4. TERAPIA WSPOMAGAJĄCA
- Okłady z Ziół Szwedzkich (dokładna instrukcja), kąpiele, dieta (jeśli dotyczy).

### 5. POZYSKIWANIE SUROWCA I KONTROLA JAKOŚCI
- Świeże vs Suszone.
- Instrukcja jak rozpoznać dobre zioło.

### 6. CZAS KURACJI
- Szacowany czas leczenia.

### 7. ZIOŁA W TEJ KURACJI (Techniczne - dla obrazów)
Na samym końcu, w osobnej linii, wypisz po przecinku TYLKO łacińskie nazwy głównych ziół użytych w tej kuracji.
Format: "NAZWY_LACIŃSKIE: Nazwa1, Nazwa2"
"""

# --- 5. Funkcja pomocnicza do obrazków ---
def get_plant_images(text):
    image_markdown = ""
    try:
        if "NAZWY_LACIŃSKIE:" in text:
            latin_line = text.split("NAZWY_LACIŃSKIE:")[1].strip().split("\n")[0]
            plant_names = [name.strip() for name in latin_line.split(",")]

            # Tworzymy sekcję obrazków, ale nie wyświetlamy jej od razu, tylko zwracamy
            # Zwracamy też listę nazw, żeby wiedzieć, ile kolumn stworzyć
            clean_text = text.split("### 7. ZIOŁA W TEJ KURACJI")[0]
            return clean_text, plant_names
    except Exception:
        return text, []
    return text, []

# --- 6. Pasek Boczny (Sidebar) ---
with st.sidebar:
    st.header("📖 O Aplikacji")
    st.info(
        """
        To narzędzie to Twój osobisty asystent oparty na książce **"Apteka Pana Boga"**.
        
        **Jak to działa?**
        System analizuje Twoje objawy i dobiera kurację zgodnie z zaleceniami Marii Treben (lata 80. XX wieku).
        """
    )
    st.warning(
        """
        **⚠️ Ważne:**
        Aplikacja ma charakter edukacyjny. Porady pochodzą z literatury ludowej. Nie zastępują wizyty u lekarza!
        """
    )
    st.markdown("---")
    st.caption("Powered by Gemini Pro & Streamlit")

# --- 7. Główny Ekran ---
st.title("🌿 Wirtualny Zielarz")
st.subheader("Według Marii Treben")

st.markdown("""
Wpisz poniżej, co Ci dolega. System przeanalizuje metody leczenia opisane w *"Aptece Pana Boga"* i dobierze odpowiednie zioła (wraz z instrukcją parzenia).
""")

# Formularz
with st.form("diagnosis_form"):
    user_query = st.text_area(
        "Opisz dolegliwości:",
        placeholder="np. bóle jelit, stłuszczona wątroba, problemy skórne...",
        height=130
    )
    submit_button = st.form_submit_button("🔍 Znajdź Kurację", type="primary")

# Logika po kliknięciu
if submit_button and user_query:
    if len(user_query) < 3:
        st.warning("Opisz problem nieco dokładniej.")
    else:
        with st.spinner('Przeszukuję zapiski Marii Treben...'):
            try:
                full_prompt = f"{SYSTEM_PROMPT}\n\nPACJENT ZGŁASZA: {user_query}"
                response = model.generate_content(full_prompt)
                
                clean_response, plant_names = get_plant_images(response.text)

                st.success("Kuracja została przygotowana.")
                
                # WYŚWIETLANIE WYNIKU W "KARCIE" (Styl .result-card)
                st.markdown(f"""
                <div class="result-card">
                    {clean_response}
                </div>
                """, unsafe_allow_html=True)

                # WYŚWIETLANIE ZDJĘĆ NA DOLE
                if plant_names:
                    st.markdown("### 📸 Zioła w tej kuracji:")
                    cols = st.columns(len(plant_names))
                    for i, plant_name in enumerate(plant_names):
                        img_url = f"https://tse2.mm.bing.net/th?q={plant_name.replace(' ', '+')}+botanical+photo&w=300&h=300&c=7&rs=1&p=0&dpr=3&pid=1.7&mkt=en-US&adlt=moderate"
                        with cols[i]:
                            st.image(img_url, caption=plant_name, use_column_width=True)

            except Exception as e:
                st.error(f"Wystąpił błąd: {e}")
