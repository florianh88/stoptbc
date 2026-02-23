import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import random

# --- CONFIGURATION & STYLE ---
st.set_page_config(page_title="Coach Master Mobile", page_icon="🏆")

st.markdown("""
    <style>
    .main { background-color: #F7F9F7; }
    .stButton>button { width: 100%; border-radius: 15px; height: 3.5em; font-weight: bold; }
    .card { background-color: white; padding: 20px; border-radius: 15px; border-bottom: 4px solid #3E5C39; margin-bottom: 20px; text-align: center; }
    .chrono { color: #1B4F72; font-size: 28px; font-weight: bold; }
    .stat-val { font-size: 40px; font-weight: bold; color: #3E5C39; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DES DONNÉES (Session State) ---
if 'data' not in st.session_state:
    st.session_state.data = {
        "compteur_jour": 0, "xp": 0, "streak": 0,
        "derniere_cig": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "causes": {"Stress": 0, "Ennui": 0, "Social": 0, "Café/Repas": 0, "Autre": 0},
        "projets": [{"nom": "Exemple : Voyage", "prix": 1000}]
    }

data = st.session_state.data

# --- LOGIQUE DU CHRONO ---
derniere = datetime.strptime(data["derniere_cig"], "%Y-%m-%d %H:%M:%S")
diff = datetime.now() - derniere
jours, heures, minutes = diff.days, diff.seconds // 3600, (diff.seconds // 60) % 60

# --- INTERFACE MOBILE ---
st.title("🏆 Coach Master")

# 1. CHRONO DE LIBERTÉ
st.markdown(f"""
    <div class="card">
        <p style="color: #6B705C; margin:0;">LIBRE DEPUIS</p>
        <p class="chrono">{jours}j {heures:02d}h {minutes:02d}m</p>
    </div>
    """, unsafe_allow_html=True)

# 2. ACTIONS
col1, col2 = st.columns(2)
with col1:
    if st.button("🆘 SOS PANIC"):
        st.toast("Respire 3 secondes... expire 3 secondes...", icon="🌬️")
        st.warning("Bois un verre d'eau !")

with col2:
    if st.button("🚬 CIGARETTE"):
        st.session_state.show_causes = True

# Menu des causes (si on clique sur cigarette)
if st.session_state.get('show_causes', False):
    st.subheader("Quelle est la cause ?")
    cause_cols = st.columns(2)
    for i, c in enumerate(data["causes"].keys()):
        if cause_cols[i % 2].button(c):
            data["compteur_jour"] += 1
            data["causes"][c] += 1
            data["derniere_cig"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.show_causes = False
            st.rerun()

# 3. ONGLETS (Comme sur PC)
tab1, tab2, tab3 = st.tabs(["📊 Analyse", "💎 Succès", "🎯 Projets"])

with tab1:
    st.markdown(f"""<div class="card"><p>AUJOURD'HUI</p><p class="stat-val">{data['compteur_jour']}</p></div>""", unsafe_allow_html=True)
    st.subheader("Déclencheurs")
    df_causes = pd.DataFrame(list(data["causes"].items()), columns=["Cause", "Nombre"])
    st.bar_chart(df_causes.set_index("Cause"))

with tab2:
    lvl = (data["xp"] // 1000) + 1
    st.metric("Niveau", f"LVL {lvl}")
    st.progress(min((data["xp"] % 1000) / 1000, 1.0))
    st.write("XP Totale :", data["xp"])
    # Simulation de badges
    if jours >= 1: st.success("🏆 Badge : 24h de victoire !")

with tab3:
    st.subheader("Mes objectifs financiers")
    prix_paquet = 12.50
    eco_totale = (diff.total_seconds() / 86400) * prix_paquet
    for p in data["projets"]:
        prog = min(max(0.01, eco_totale / p['prix']), 1.0)
        st.write(f"**{p['nom']}** ({p['prix']}€)")
        st.progress(prog)
        st.caption(f"{eco_totale:.2f}€ économisés sur {p['prix']}€")

st.info(f"💡 Astuce : Tu es à {data['streak']} jours de série !")
