import streamlit as st
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Mon Coach Liberté", page_icon="🍃")

# Style pour mobile
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #3E5C39; color: white; }
    .status-box { background-color: #f0f2f6; padding: 20px; border-radius: 15px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍃 Coach Santé Mobile")

# --- LOGIQUE DE CALCUL ---
if 'last_cig' not in st.session_state:
    st.session_state.last_cig = datetime.now()

diff = datetime.now() - st.session_state.last_cig
jours = diff.days
heures, reste = divmod(diff.seconds, 3600)
minutes, _ = divmod(reste, 60)

# --- AFFICHAGE ---
st.markdown(f"""
    <div class="status-box">
        <h3 style="margin:0;">LIBRE DEPUIS</h3>
        <h1 style="color: #1B4F72; margin:0;">{jours}j {heures:02d}h {minutes:02d}m</h1>
    </div>
    """, unsafe_allow_html=True)

st.write("##")

col1, col2 = st.columns(2)
with col1:
    if st.button("🆘 SOS ENVIE"):
        st.toast("Respire... Ça va passer ! 🌬️")
        st.warning("Bois un verre d'eau et attends 3 minutes.")

with col2:
    if st.button("🚬 J'AI CRAQUÉ"):
        st.session_state.last_cig = datetime.now()
        st.rerun()

st.divider()

# Simulation d'économie
prix_paquet = 12.50
economie = (diff.total_seconds() / 86400) * prix_paquet
st.metric("Argent sauvé 💶", f"{economie:.2f} €")

st.info("💡 Ajoute cette page aux favoris de ton téléphone !")
