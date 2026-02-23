import customtkinter as ctk
import json
import os
import random
from datetime import datetime, timedelta
from tkinter import messagebox

# --- CONFIGURATION VISUELLE ---
ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("green")

BG_COLOR = "#F7F9F7"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#3E5C39"
ACCENT_COLOR = "#A3B18A"
ALERT_COLOR = "#BC6C4D"
PANIC_COLOR = "#D35400"
TEXT_MAIN = "#2A2A2A"
TEXT_SEC = "#6B705C"
FONT_FAMILY = "Segoe UI" 

class CoachSante(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Coach Bien-Être Pro - Master Edition")
        self.geometry("650x1000")
        self.configure(fg_color=BG_COLOR)

        self.alternatives = [
            "Va plutôt faire 10 pompes ! 💪", "Fais 20 abdos ! ⚡",
            "Monte et descends les escaliers ! 🏃‍♂️", "Étire tes bras et ton dos. 🙆‍♂️",
            "Bois un grand verre d'eau fraîche ! 💧", "Prépare-toi un thé bio. ☕",
            "Mange une pomme. 🍎", "Lave-toi les dents ! 🪥",
            "Sors prendre l'air 5 minutes. 🌬️", "3 min de cohérence cardiaque. 🌬️"
        ]

        self.citations_motivation = [
            "Chaque bouffée non prise est une victoire. 🫁",
            "Le succès, c'est de se relever huit fois. 👣",
            "Ta liberté a une odeur : celle du frais ! 🍃",
            "Tu es plus fort que cette envie de 5 minutes. 💪"
        ]

        self.FILE_PATH = "donnees_coach_pro.json"
        self.charger_donnees()
        self.verifier_changement_jour()

        self.panic_active = False
        self.panic_timer = 180

        # --- NAVIGATION ---
        self.tabview = ctk.CTkTabview(self, 
                                      segmented_button_selected_color=PRIMARY_COLOR,
                                      segmented_button_unselected_color="#E0E5E0",
                                      text_color=TEXT_MAIN)
        self.tabview.pack(padx=20, pady=20, expand=True, fill="both")

        self.tabview.add("Tableau de bord")
        self.tabview.add("Succès & XP")
        self.tabview.add("Santé")
        self.tabview.add("Projets")
        self.tabview.add("Analyse")
        self.tabview.add("Paramètres")

        self.setup_dashboard()
        self.setup_badges()
        self.setup_sante()
        self.setup_projets()
        self.setup_analyse()
        self.setup_settings()
        
        # Lancement du chrono dynamique
        self.update_chrono_liberte()

    def charger_donnees(self):
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, "r") as f: self.data = json.load(f)
        else:
            self.data = {
                "compteur_jour": 0, "objectif_max": 20, "prix_paquet": 12.50,
                "date_debut": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "derniere_maj": datetime.now().strftime("%Y-%m-%d"),
                "derniere_cig": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "historique": {}, "projets": [], "xp": 0, "streak": 0,
                "causes": {"Stress": 0, "Ennui": 0, "Social": 0, "Café/Repas": 0, "Autre": 0}
            }
        # Migrations pour anciennes versions
        if "streak" not in self.data: self.data["streak"] = 0
        if "derniere_cig" not in self.data: self.data["derniere_cig"] = self.data["date_debut"]
        if "causes" not in self.data: self.data["causes"] = {"Stress": 0, "Ennui": 0, "Social": 0, "Café/Repas": 0, "Autre": 0}
        self.sauvegarder()

    def sauvegarder(self):
        with open(self.FILE_PATH, "w") as f: json.dump(self.data, f)

    def verifier_changement_jour(self):
        ajd = datetime.now().strftime("%Y-%m-%d")
        if self.data["derniere_maj"] != ajd:
            if self.data["compteur_jour"] == 0: self.data["streak"] += 1
            else: self.data["streak"] = 0
            self.data["historique"][self.data["derniere_maj"]] = self.data["compteur_jour"]
            self.data["compteur_jour"] = 0
            self.data["derniere_maj"] = ajd
            self.sauvegarder()

    def setup_dashboard(self):
        tab = self.tabview.tab("Tableau de bord")
        tab.configure(fg_color=CARD_BG)
        
        # Chrono de Liberté (NOUVEAU)
        self.f_chrono = ctk.CTkFrame(tab, fg_color="#EBF5FB", corner_radius=15)
        self.f_chrono.pack(pady=(15, 0), padx=20, fill="x")
        ctk.CTkLabel(self.f_chrono, text="LIBRE DEPUIS", font=(FONT_FAMILY, 11, "bold"), text_color="#2E86C1").pack(pady=(5,0))
        self.lbl_chrono_val = ctk.CTkLabel(self.f_chrono, text="00j 00h 00m 00s", font=(FONT_FAMILY, 24, "bold"), text_color="#1B4F72")
        self.lbl_chrono_val.pack(pady=(0, 5))

        self.f_streak = ctk.CTkFrame(tab, fg_color="#FFF9E6", corner_radius=20)
        self.f_streak.pack(pady=(10, 0))
        self.lbl_streak = ctk.CTkLabel(self.f_streak, text=f"🔥 {self.data['streak']} JOURS DE SÉRIE", 
                                       font=(FONT_FAMILY, 14, "bold"), text_color="#D35400")
        self.lbl_streak.pack(padx=20, pady=5)

        ctk.CTkLabel(tab, text="Progression du jour", font=(FONT_FAMILY, 22, "bold")).pack(pady=(15, 0))
        self.lbl_cigs = ctk.CTkLabel(tab, text="0", font=(FONT_FAMILY, 90, "bold"), text_color=PRIMARY_COLOR)
        self.lbl_cigs.pack()

        self.prog_bar = ctk.CTkProgressBar(tab, width=400, height=12, progress_color=ACCENT_COLOR)
        self.prog_bar.pack(pady=10)

        self.btn_panic = ctk.CTkButton(tab, text="🆘 BESOIN D'AIDE (SOS)", fg_color=PANIC_COLOR, 
                                      hover_color="#A04000", height=45, corner_radius=12, command=self.start_panic_mode)
        self.btn_panic.pack(pady=10, padx=60, fill="x")

        ctk.CTkButton(tab, text="DÉCLARER UNE CIGARETTE", fg_color=ALERT_COLOR, height=50, corner_radius=15, 
                      font=(FONT_FAMILY, 15, "bold"), command=self.ouvrir_journal_causes).pack(pady=10, padx=60, fill="x")
        
        ctk.CTkButton(tab, text="Réinitialiser la journée", fg_color="transparent", text_color=TEXT_SEC, 
                      hover_color="#F5F5F5", font=(FONT_FAMILY, 12), command=self.reset_aujourdhui).pack()
        
        self.panic_frame = ctk.CTkFrame(tab, fg_color="#FDF2E9", corner_radius=15)
        self.lbl_panic_timer = ctk.CTkLabel(self.panic_frame, text="3:00", font=(FONT_FAMILY, 30, "bold"), text_color=PANIC_COLOR)
        self.lbl_panic_timer.pack(pady=10)
        self.panic_instr = ctk.CTkLabel(self.panic_frame, text="Inspirez... Expirez...", font=(FONT_FAMILY, 16))
        self.panic_instr.pack(pady=5)
        self.maj_dashboard()

    def update_chrono_liberte(self):
        try:
            derniere = datetime.strptime(self.data["derniere_cig"], "%Y-%m-%d %H:%M:%S")
            diff = datetime.now() - derniere
            jours = diff.days
            heures, reste = divmod(diff.seconds, 3600)
            minutes, secondes = divmod(reste, 60)
            self.lbl_chrono_val.configure(text=f"{jours}j {heures:02d}h {minutes:02d}m {secondes:02d}s")
        except: pass
        self.after(1000, self.update_chrono_liberte)

    def ouvrir_journal_causes(self):
        # Fenêtre contextuelle pour la cause (Journal des envies)
        self.win_cause = ctk.CTkToplevel(self)
        self.win_cause.title("Pourquoi ?")
        self.win_cause.geometry("300x400")
        self.win_cause.attributes("-topmost", True)
        
        ctk.CTkLabel(self.win_cause, text="Déclencheur identifié :", font=(FONT_FAMILY, 14, "bold")).pack(pady=20)
        causes = ["Stress", "Ennui", "Social", "Café/Repas", "Autre"]
        for c in causes:
            ctk.CTkButton(self.win_cause, text=c, fg_color=ACCENT_COLOR, text_color=TEXT_MAIN, 
                          command=lambda cause=c: self.declarer_cig_avec_cause(cause)).pack(pady=5, padx=20, fill="x")

    def declarer_cig_avec_cause(self, cause):
        self.win_cause.destroy()
        conseil = random.choice(self.alternatives)
        if messagebox.askyesno("Dernière chance", f"Le coach suggère :\n\n{conseil}\n\nConfirmer quand même ?"):
            self.data["compteur_jour"] += 1
            self.data["derniere_cig"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.data["causes"][cause] += 1
            self.sauvegarder()
            self.actualiser_tout()

    def reset_aujourdhui(self):
        if messagebox.askyesno("Confirmation", "Remettre le compteur d'aujourd'hui à zéro ?"):
            self.data["compteur_jour"] = 0
            self.sauvegarder()
            self.actualiser_tout()

    def start_panic_mode(self):
        if self.panic_active: return
        self.panic_active = True
        self.panic_frame.pack(pady=10, padx=60, fill="x")
        self.btn_panic.configure(state="disabled")
        self.update_panic_timer()

    def update_panic_timer(self):
        if self.panic_timer > 0 and self.panic_active:
            mins, secs = divmod(self.panic_timer, 60)
            self.lbl_panic_timer.configure(text=f"{mins:02d}:{secs:02d}")
            txt = "INSPIRER..." if self.panic_timer % 10 > 5 else "EXPIRER..."
            self.panic_instr.configure(text=txt)
            self.panic_timer -= 1
            self.after(1000, self.update_panic_timer)
        else:
            self.panic_active = False
            self.panic_timer = 180
            self.panic_frame.pack_forget()
            self.btn_panic.configure(state="normal")

    def setup_badges(self):
        tab = self.tabview.tab("Succès & XP")
        tab.configure(fg_color=CARD_BG)
        self.xp_frame = ctk.CTkFrame(tab, fg_color="#F0F4F0", corner_radius=20)
        self.xp_frame.pack(fill="x", padx=20, pady=20)
        self.lbl_lvl = ctk.CTkLabel(self.xp_frame, text="NIVEAU", font=(FONT_FAMILY, 18, "bold"), text_color=PRIMARY_COLOR)
        self.lbl_lvl.pack(pady=(15, 0))
        self.xp_bar_ui = ctk.CTkProgressBar(self.xp_frame, progress_color=ACCENT_COLOR, width=400)
        self.xp_bar_ui.pack(pady=10, padx=20)
        self.lbl_xp_val = ctk.CTkLabel(self.xp_frame, text="XP", font=(FONT_FAMILY, 12), text_color=TEXT_SEC)
        self.lbl_xp_val.pack(pady=(0, 15))
        self.badge_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.badge_scroll.pack(fill="both", expand=True, padx=10)
        self.maj_badges()

    def maj_badges(self):
        for w in self.badge_scroll.winfo_children(): w.destroy()
        debut = datetime.strptime(self.data["date_debut"], "%Y-%m-%d %H:%M:%S")
        jours = max(0, (datetime.now() - debut).days)
        eco = jours * self.data["prix_paquet"]
        evitees = jours * self.data["objectif_max"]
        
        succes = [
            ("Détermination", "24h sans tabac", jours >= 1, "🏆", 50),
            ("Série de 7", "1 semaine de pureté", jours >= 7, "⭐", 150),
            ("Libération", "1 mois de victoire", jours >= 30, "🔓", 500),
            ("Vétéran", "90 jours de souffle", jours >= 90, "🌊", 1000),
            ("Légende", "1 an de liberté", jours >= 365, "👑", 5000),
            ("Économie I", "50€ sauvés", eco >= 50, "💶", 50),
            ("Économie II", "200€ sauvés", eco >= 200, "💰", 200),
            ("Économie III", "1000€ sauvés", eco >= 1000, "🏦", 1000),
            ("Nettoyage I", "100 cigs évitées", evitees >= 100, "🫁", 100),
            ("Sniper", "Une journée à 0 cig", self.data["compteur_jour"] == 0 and jours > 0, "🎯", 100),
            ("Sportif", "Coach écouté", True, "🏃", 150),
            ("Zéro Rechute", "3 jours de stabilité", self.data["streak"] >= 3, "🔥", 300)
        ]
        
        total_xp = 0
        for t, d, a, i, x in succes:
            if a: total_xp += x
            bg = "#F9FFF9" if a else "#FBFBFB"
            card = ctk.CTkFrame(self.badge_scroll, fg_color=bg, border_width=1, border_color="#EEEEEE", corner_radius=12)
            card.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(card, text=i if a else "🔒", font=("Segoe UI Emoji", 30)).pack(side="left", padx=15)
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True)
            ctk.CTkLabel(info, text=f"{t} (+{x} XP)", font=(FONT_FAMILY, 14, "bold")).pack(anchor="w")
            ctk.CTkLabel(info, text=d, font=(FONT_FAMILY, 11), text_color=TEXT_SEC).pack(anchor="w")
        self.data["xp"] = total_xp
        self.lbl_lvl.configure(text=f"NIVEAU {(total_xp // 1000) + 1}")
        self.xp_bar_ui.set((total_xp % 1000) / 1000)

    def setup_sante(self):
        tab = self.tabview.tab("Santé")
        tab.configure(fg_color=CARD_BG)
        header = ctk.CTkFrame(tab, fg_color="#F3F6F3", corner_radius=15); header.pack(pady=20, padx=20, fill="x")
        ctk.CTkLabel(header, text="🍃", font=("Segoe UI Emoji", 40)).pack()
        ctk.CTkLabel(header, text="RÉGÉNÉRATION ACTIVE", font=(FONT_FAMILY, 16, "bold"), text_color=PRIMARY_COLOR).pack(pady=5)
        self.lbl_motiv = ctk.CTkLabel(tab, text="", font=(FONT_FAMILY, 13, "italic"), wraplength=450); self.lbl_motiv.pack(pady=10)
        self.sante_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent"); self.sante_scroll.pack(fill="both", expand=True, padx=20)
        paliers = [("Rythme cardiaque", 0.33), ("Taux d'oxygène", 0.5), ("Goût & Odorat", 2), ("Capacité pulmonaire", 90)]
        self.bars = []
        for n, r in paliers:
            f = ctk.CTkFrame(self.sante_scroll, fg_color="#FBFCFB", border_width=1, border_color="#E8ECE8"); f.pack(fill="x", pady=8)
            ctk.CTkLabel(f, text=n, font=(FONT_FAMILY, 13, "bold")).pack(pady=2)
            p = ctk.CTkProgressBar(f, progress_color=PRIMARY_COLOR, height=10); p.pack(fill="x", padx=20, pady=10)
            self.bars.append((p, r))
        self.maj_sante()

    def maj_sante(self):
        debut = datetime.strptime(self.data["date_debut"], "%Y-%m-%d %H:%M:%S")
        diff = (datetime.now() - debut).total_seconds() / 86400
        for p, r in self.bars: p.set(min(diff/r, 1.0))
        self.lbl_motiv.configure(text=random.choice(self.citations_motivation))

    def setup_analyse(self):
        tab = self.tabview.tab("Analyse")
        tab.configure(fg_color=CARD_BG)
        ctk.CTkLabel(tab, text="HISTORIQUE (7 JOURS)", font=(FONT_FAMILY, 14, "bold")).pack(pady=10)
        self.graph_frame = ctk.CTkFrame(tab, fg_color="#F8FAF8", height=120, corner_radius=15); self.graph_frame.pack(fill="x", padx=30, pady=5)
        
        # NOUVEAU : Zone d'analyse des causes
        ctk.CTkLabel(tab, text="DÉCLENCHEURS PRINCIPAUX", font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_SEC).pack(pady=(10,0))
        self.causes_frame = ctk.CTkFrame(tab, fg_color="#FDF2F2", corner_radius=15); self.causes_frame.pack(fill="x", padx=30, pady=5)
        self.lbl_causes_stat = ctk.CTkLabel(self.causes_frame, text="", font=(FONT_FAMILY, 11))
        self.lbl_causes_stat.pack(pady=10)

        self.box_analyse = ctk.CTkFrame(tab, fg_color="#F8FAF8", corner_radius=20, border_width=1, border_color="#E0E5E0"); self.box_analyse.pack(padx=30, pady=10, fill="both", expand=True)
        self.lbl_coach_txt = ctk.CTkLabel(self.box_analyse, text="", font=(FONT_FAMILY, 15), justify="left"); self.lbl_coach_txt.pack(padx=25, pady=20)
        self.maj_analyse()

    def maj_analyse(self):
        for w in self.graph_frame.winfo_children(): w.destroy()
        hist = self.data["historique"]
        dates = sorted(hist.keys())[-7:]
        for d in dates:
            val = hist[d]
            h = min(val * 5, 80)
            bar = ctk.CTkFrame(self.graph_frame, width=30, height=max(5,h), fg_color=ALERT_COLOR if val > 0 else PRIMARY_COLOR, corner_radius=5)
            bar.pack(side="left", anchor="bottom", padx=10, pady=5)
        
        # Maj des causes
        c_txt = " | ".join([f"{k}: {v}" for k, v in self.data["causes"].items()])
        self.lbl_causes_stat.configure(text=c_txt)

        px = self.data["prix_paquet"]; debut = datetime.strptime(self.data["date_debut"], "%Y-%m-%d %H:%M:%S")
        jours = max(1, (datetime.now() - debut).days)
        eco = (jours * px) - ((sum(hist.values()) + self.data["compteur_jour"]) * (px/20))
        msg = (f"📊 BILAN\n\n• Économie totale : {max(0, eco):.2f}€\n• Hebdo : {px * 7:.2f}€ | Mensuel : {px * 30.5:.2f}€\n"
               f"━━━━━━━━━━━━━━━━━━━━━\n🔥 SÉRIE : {self.data['streak']} JOURS")
        self.lbl_coach_txt.configure(text=msg)

    def setup_projets(self):
        tab = self.tabview.tab("Projets")
        tab.configure(fg_color=CARD_BG)
        f_in = ctk.CTkFrame(tab, fg_color="#F1F4F1", corner_radius=15); f_in.pack(fill="x", padx=20, pady=20)
        self.en_nom = ctk.CTkEntry(f_in, placeholder_text="Projet...", border_width=0); self.en_nom.pack(side="left", padx=10, expand=True, fill="x", pady=10)
        self.en_prix = ctk.CTkEntry(f_in, placeholder_text="€", width=80, border_width=0); self.en_prix.pack(side="left", padx=10, pady=10)
        ctk.CTkButton(f_in, text="OK", width=60, fg_color=PRIMARY_COLOR, command=self.ajouter_projet).pack(side="left", padx=10, pady=10)
        self.p_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent"); self.p_scroll.pack(fill="both", expand=True, padx=20)
        self.maj_projets()

    def ajouter_projet(self):
        try:
            n, p = self.en_nom.get(), float(self.en_prix.get())
            if n: self.data["projets"].append({"nom": n, "prix": p}); self.sauvegarder(); self.maj_projets()
        except: pass

    def supprimer_projet(self, index):
        if messagebox.askyesno("Confirmation", "Supprimer ce projet ?"):
            del self.data["projets"][index]
            self.sauvegarder(); self.maj_projets()

    def maj_projets(self):
        for w in self.p_scroll.winfo_children(): w.destroy()
        px = self.data["prix_paquet"]; debut = datetime.strptime(self.data["date_debut"], "%Y-%m-%d %H:%M:%S")
        jours = max(1, (datetime.now() - debut).days)
        eco = (jours * px) - ((sum(self.data["historique"].values()) + self.data["compteur_jour"]) * (px/20))
        for i, p in enumerate(self.data["projets"]):
            f = ctk.CTkFrame(self.p_scroll, fg_color=CARD_BG, border_width=1, border_color="#E8ECE8", corner_radius=12); f.pack(fill="x", pady=8)
            prog = min(max(0, eco) / p['prix'], 1.0)
            header = ctk.CTkFrame(f, fg_color="transparent"); header.pack(fill="x", padx=10)
            ctk.CTkLabel(header, text=p['nom'].upper(), font=(FONT_FAMILY, 12, "bold"), text_color=PRIMARY_COLOR).pack(side="left", pady=10)
            ctk.CTkButton(header, text="✕", width=25, height=25, fg_color="transparent", text_color=ALERT_COLOR, 
                          command=lambda idx=i: self.supprimer_projet(idx)).pack(side="right")
            pb = ctk.CTkProgressBar(f, height=10, progress_color=ACCENT_COLOR); pb.set(prog); pb.pack(fill="x", padx=40, pady=(0, 10))
            ctk.CTkLabel(f, text=f"{prog*100:.1f}% ({max(0, eco):.2f} / {p['prix']}€)").pack(pady=(0,5))

    def setup_settings(self):
        tab = self.tabview.tab("Paramètres"); tab.configure(fg_color=CARD_BG)
        ctk.CTkLabel(tab, text="CONFIGURATION", font=(FONT_FAMILY, 20, "bold")).pack(pady=30)
        self.set_prix = ctk.CTkEntry(tab, placeholder_text=f"Prix du paquet ({self.data['prix_paquet']}€)"); self.set_prix.pack(pady=10, padx=50, fill="x")
        self.set_obj = ctk.CTkEntry(tab, placeholder_text=f"Cig/jour ({self.data['objectif_max']})"); self.set_obj.pack(pady=10, padx=50, fill="x")
        ctk.CTkButton(tab, text="ENREGISTRER", fg_color=PRIMARY_COLOR, command=self.save_settings).pack(pady=30)

    def save_settings(self):
        try:
            if self.set_prix.get(): self.data["prix_paquet"] = float(self.set_prix.get())
            if self.set_obj.get(): self.data["objectif_max"] = int(self.set_obj.get())
            self.sauvegarder(); messagebox.showinfo("Succès", "Paramètres mis à jour !"); self.actualiser_tout()
        except: messagebox.showerror("Erreur", "Valeurs invalides")

    def maj_dashboard(self):
        self.lbl_cigs.configure(text=str(self.data["compteur_jour"]))
        self.prog_bar.set(min(self.data["compteur_jour"]/self.data["objectif_max"], 1.0))
        self.lbl_streak.configure(text=f"🔥 {self.data['streak']} JOURS DE SÉRIE")

    def actualiser_tout(self):
        self.maj_dashboard(); self.maj_sante(); self.maj_analyse(); self.maj_projets(); self.maj_badges()

if __name__ == "__main__":
    app = CoachSante()
    app.mainloop()