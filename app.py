import streamlit as st
import google.generativeai as genai
import sys

st.set_page_config(page_title="Diagnostyka", layout="wide")
st.title("🛠️ Tryb Diagnostyczny")

# 1. Sprawdzenie wersji biblioteki
st.header("1. Wersje Oprogramowania")
st.write(f"**Python version:** `{sys.version}`")
try:
    st.write(f"**Google GenAI version:** `{genai.__version__}`")
    # Wersja musi być >= 0.8.3, żeby Flash działał
    if genai.__version__ < "0.8.3":
        st.error("❌ STARA BIBLIOTEKA! Zaktualizuj requirements.txt")
    else:
        st.success("✅ Wersja biblioteki jest OK (obsługuje Flash/Pro 1.5)")
except Exception as e:
    st.error(f"Nie można sprawdzić wersji: {e}")

# 2. Test Klucza i Listy Modeli
st.header("2. Co widzi Twój Klucz API?")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    st.info("Pytam Google o dostępne modele...")
    
    models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            models.append(m.name)
            
    if not models:
        st.error("❌ Twój klucz API działa, ale NIE WIDZI ŻADNYCH MODELI. To oznacza problem z kontem Google AI Studio (blokada regionu lub projektu).")
    else:
        st.success(f"✅ Znaleziono {len(models)} modeli:")
        st.code("\n".join(models))
        
        # Sprawdźmy czy Flash jest na liście
        if any("flash" in m for m in models):
            st.success("🎉 HURRA! Model Flash jest dostępny!")
        else:
            st.warning("⚠️ Brak modelu Flash na liście. Musimy użyć jednego z powyższych.")

except Exception as e:
    st.error(f"❌ Błąd krytyczny klucza API: {e}")
    st.warning("Sprawdź, czy w Secrets nie ma spacji na końcu klucza!")
