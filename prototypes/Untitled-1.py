import tkinter as tk
from tkinter import ttk

class Ihm_Telephone(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interface Téléphone")
        self.geometry("300x600")  # Taille pour simuler un écran de téléphone
        self.configure(bg="white")  # Fond blanc

        # État de l'appel
        self.etat_appel = tk.Label(self, text="État de l'appel : Ça sonne", font=("Arial", 12), bg="white")
        self.etat_appel.pack(pady=10)

        # Nom du correspondant
        self.nom_correspondant = tk.Label(self, text="Nom du correspondant : John Doe", font=("Arial", 12), bg="white")
        self.nom_correspondant.pack(pady=10)

        # Liste déroulante pour l'annuaire de contacts
        self.label_liste = tk.Label(self, text="Annuaire de contacts :", font=("Arial", 10), bg="white")
        self.label_liste.pack()
        self.liste_contacts = ttk.Combobox(self, values=["John Doe", "Alice", "Bob", "Eve"], font=("Arial", 10))
        self.liste_contacts.set("Sélectionner un contact")
        self.liste_contacts.pack(pady=5)

        # Partie interactive
        cadre_interactif = tk.Frame(self, bg="lightgrey", bd=2, relief="ridge")
        cadre_interactif.pack(pady=20, padx=10, fill="both", expand=True)

        # Boutons interactifs (Couper micro, Haut-parleur)
        self.bouton_micro = tk.Button(
            cadre_interactif, text=" Couper Micro", font=("Arial", 12), command=self.couper_micro
        )
        self.bouton_micro.pack(pady=10)

        self.bouton_hp = tk.Button(
            cadre_interactif, text=" Haut-parleur", font=("Arial", 12), command=self.activer_hp
        )
        self.bouton_hp.pack(pady=10)

        # Bouton d'appel/raccrocher
        self.bouton_appel = tk.Button(
            cadre_interactif, text=" Appel/Raccrocher", font=("Arial", 12), bg="lightgreen", command=self.appel
        )
        self.bouton_appel.pack(pady=20)

    def couper_micro(self):
        print("Micro coupé!")

    def activer_hp(self):
        print("Haut-parleur activé!")

    def appel(self):
        print("Appel lancé ou raccroché!")


if __name__ == "__main__":
    app = Ihm_Telephone()
    app.mainloop()
