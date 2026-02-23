import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Coach Bien-Être Master", page_icon="🍃", layout="centered")

# --- STYLE CSS (Inspiré de ta version PC) ---
st.markdown("""
    <style>
    .main { background-color: #F7F9F7; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; }
    .card { background-color: white; padding: 20px; border-radius: 15px; border-bottom: 5px solid #3E5C39; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .chrono-val { color: #1B4F72; font-size: 32px; font-weight: bold; text-align: center; }
    .stat-label { color: #6B705C; font-size: 12px; font-weight: bold; text-align: center; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DES DONNÉES (Session State) ---
if 'data' not in st.session_state:
    st.session_state.data = {
        "compteur_jour": 0, "objectif_max": 20, "prix_paquet": 12.50,
        "date_debut": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "derniere_cig": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "xp": 0, "streak": 0,
        "causes": {"Stress": 0, "Ennui": 0, "Social": 0, "Café/Repas": 0, "Autre": 0},
        "projets": [], "historique": {}
    }

d = st.session_state.data

# --- LOGIQUE DE CALCUL ---
debut = datetime.strptime(d["date_debut"], "%Y-%m-%d %H:%M:%S")
derniere = datetime.strptime(d["derniere_cig"], "%Y-%m-%d %H:%M:%S")
diff_liberte = datetime.now() - derniere
jours_libres = (datetime.now() - debut).days
eco_totale = (max(1, jours_libres) * d["prix_paquet"]) - (sum(d["historique"].values()) * (d["prix_paquet"]/20))

# --- SIDEBAR (PARAMÈTRES) ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    d["prix_paquet"] = st.number_input("Prix du paquet (€)", value=d["prix_paquet"])
    d["objectif_max"] = st.number_input("Objectif max (cig/jour)", value=d["objectif_max"])
    if st.button("Reset Aujourd'hui"):
        d["compteur_jour"] = 0
        st.rerun()

# --- TITRE PRINCIPAL ---
st.title("🍃 Coach Master Edition")

# --- ONGLET 1 : TABLEAU DE BORD ---
t1, t2, t3, t4 = st.tabs(["🏠 Bord", "🎖️ Succès", "🫁 Santé", "🎯 Projets"])

with t1:
    # Chrono
    st.markdown(f"""<div class="card"><p class="stat-label">Libre depuis</p><p class="chrono-val">{diff_liberte.days}j {diff_liberte.seconds//3600}h {(diff_liberte.seconds//60)%60}m</p></div>""", unsafe_allow_html=True)
    
    # Streak & Compteur
    col_a, col_b = st.columns(2)
    col_a.metric("🔥 Streak", f"{d['streak']} Jours")
    col_b.metric("🚬 Aujourd'hui", d["compteur_jour"], delta=f"Max: {d['objectif_max']}", delta_color="inverse")
    
    st.progress(min(d["compteur_jour"]/d["objectif_max"], 1.0))

    # Boutons d'action
    if st.button("🆘 BESOIN D'AIDE (SOS)", type="primary"):
        st.session_state.panic = True
    
    if st.session_state.get('panic', False):
        st.warning("💨 Respire... Inspire pendant 5s, expire pendant 5s. Cette envie va passer.")
        if st.button("Ça va mieux"): st.session_state.panic = False

    if st.button("⚠️ DÉCLARER UNE CIGARETTE"):
        st.session_state.show_causes = True

    if st.session_state.get('show_causes', False):
        st.write("---")
        cause = st.radio("Quel est le déclencheur ?", list(d["causes"].keys()), horizontal=True)
        if st.button("Confirmer le craquage"):
            d["compteur_jour"] += 1
            d["causes"][cause] += 1
            d["derniere_cig"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.show_causes = False
            st.rerun()

with t2:
    # XP & Badges
    lvl = (d["xp"] // 1000) + 1
    st.subheader(f"Niveau {lvl}")
    st.progress((d["xp"] % 1000) / 1000)
    
    st.write("### Tes Trophées")
    badges = [
        ("🏆 Premier Pas", "24h de liberté", diff_liberte.days >= 1, 100),
        ("⭐ Semaine d'Or", "7 jours de série", d["streak"] >= 7, 500),
        ("💶 Économe", "50€ sauvés", eco_totale >= 50, 200),
        ("🎯 Sniper", "Une journée à 0", d["compteur_jour"] == 0 and jours_libres > 0, 150)
    ]
    
    temp_xp = 0
    for title, desc, won, xp_val in badges:
        if won:
            st.success(f"{title} : {desc} (+{xp_val} XP)")
            temp_xp += xp_val
        else:
            st.text(f"🔒 {title} : {desc}")
    d["xp"] = temp_xp

with t3:
    st.subheader("Régénération de ton corps")
    # Paliers identiques au code PC
    paliers = [
        ("Rythme cardiaque (20 min)", 0.014), # ~20min en jours
        ("Taux d'oxygène (8h)", 0.33),
        ("Goût & Odorat (48h)", 2),
        ("Capacité pulmonaire (9 mois)", 270)
    ]
    for nom, jours_req in paliers:
        prog = min(diff_liberte.total_seconds() / (jours_req * 86400), 1.0)
        st.write(f"**{nom}**")
        st.progress(prog)

with t4:
    st.subheader("Tes Projets")
    # Ajout de projet
    with st.expander("➕ Ajouter un projet"):
        n_p = st.text_input("Nom du projet")
        p_p = st.number_input("Prix (€)", min_value=1.0)
        if st.button("Ajouter"):
            d["projets"].append({"nom": n_p, "prix": p_p})
            st.rerun()

    # Liste des projets
    for i, p in enumerate(d["projets"]):
        prog = min(max(0.01, eco_totale / p['prix']), 1.0)
        st.write(f"**{p['nom']}** ({p['prix']}€)")
        st.progress(prog)
        st.caption(f"{eco_totale:.2f}€ accumulés")
