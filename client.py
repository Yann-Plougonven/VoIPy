# Client VoIP
# Écrit par Tugdual Thepaut et Yann Plougonven--Lastennet
# Projet de S3 de BUT R&T à l'IUT de Lannion - Décembre 2024 / Janvier 2025
# Dépôt GitHub : https://github.com/Yann-Plougonven/VoIPy

from pyaudio import *
from socket import *
from tkinter import *
from tkinter import ttk # TODO à supprimer quand on aura retiré la liste déroulante de contacts

class IHM_Authentification(Tk):
    # Utilisation du protocole UDP : on n'établit pas de connexion avec le serveur,
    # le client lui indique simplement sa présence en s'authentifiant
    def __init__(self)-> None:
        Tk.__init__(self)
        
        # déclaration des attributs 
        self.__frame_auth: Frame
        self.__entry_login: Entry
        self.__label_login: Label
        self.__entry_mdp: Entry
        self.__label_mdp: Label
        
        self.__frame_serv: Frame
        self.__label_ip_client: Label
        self.__entry_ip_serv: Entry
        self.__label_ip_serv: Label
        self.__btn_auth: Button
        
        # Instanciation des attributs
        self.title("Authentification auprès du serveur")
        self.geometry(f"{LARGEUR_FEN}x{HAUTEUR_FEN}")
        
        # Titre principal
        self.__label_titre = Label(self, text="VoIPy", font=("Helvetica", 24, "bold"))
        self.__label_titre.pack(pady=20)
        
        # Frame d'authentification
        self.__frame_auth = Frame(self, borderwidth=10, relief="groove", padx=10, pady=10)
        self.__entry_login = Entry(self.__frame_auth, width=50)
        self.__label_login = Label(self.__frame_auth, text="Identifiant")
        self.__entry_mdp = Entry(self.__frame_auth, width=50, show="*")
        self.__label_mdp = Label(self.__frame_auth, text="Mot de passe")
        
        # Frame de choix du serveur
        self.__frame_serv = Frame(self, borderwidth=10, relief="groove", padx=10, pady=10)
        self.__label_ip_client = Label(self.__frame_serv, text=f"Votre IP client : {gethostbyname(gethostname())}") # affiche l'IP du client
        self.__entry_ip_serv = Entry(self.__frame_serv, width=50)
        self.__entry_ip_serv.insert(0, "127.0.0.1") # valeur par défaut
        self.__label_ip_serv = Label(self.__frame_serv, text="IP du serveur VoIP")
        self.__btn_auth = Button(self.__frame_serv, text="Authentification", command=self.creer_utilisateur) # lance la création de l'utilisateur (et son authentification)
        
        # Ajout des widgets
        self.__frame_auth.pack(pady=20)
        self.__label_login.grid(row=0, column=0, pady=5)
        self.__entry_login.grid(row=1, column=0, pady=5)
        self.__label_mdp.grid(row=2, column=0, pady=5)
        self.__entry_mdp.grid(row=3, column=0, pady=5)
        
        self.__frame_serv.pack(pady=20)
        self.__label_ip_client.grid(row=0, column=0, pady=5)
        self.__label_ip_serv.grid(row=1, column=0, pady=5)
        self.__entry_ip_serv.grid(row=2, column=0, pady=5)
        self.__btn_auth.grid(row=3, column=0, pady=20)
        
        # intercepte la fermeture de la fenêtre et appellera la méthode quit TODO sur les 3 IHM
        # self.protocol("WM_DELETE_WINDOW", self.quit)
        
        # lancer l'IHM
        self.mainloop()
        
    def creer_utilisateur(self)-> None:
        # (il est nécessaire de récupérer les valeurs renseignées champs avant de fermer la fenêtre)
        login: str
        mdp: str
        ip_serv: str
        utilisateur: Utilisateur
        
        login = self.__entry_login.get()
        mdp = self.__entry_mdp.get()
        ip_serv = self.__entry_ip_serv.get()
        self.destroy()
        
        utilisateur = Utilisateur(login, mdp, ip_serv)
        
    # def quit(self)-> None: # TODO
    #     self.destroy()


class IHM_Contacts(Tk):
    def __init__(self, liste_collaborateurs)-> None:
        Tk.__init__(self)
        
        # déclaration des attributs
        self.__liste_collaborateurs: list[str] = liste_collaborateurs
        self.__ihm_appel: IHM_Appel
        self.__frame_contacts: Frame
        self.__label_titre: Label
        
        # Instanciation des attributs
        self.title("Choix du collaborateur à appeler")
        self.geometry(f"{LARGEUR_FEN}x{HAUTEUR_FEN}")
        
        # Titre principal
        self.__label_titre = Label(self, text="Appeler un collaborateur", font=("Helvetica", 20, "bold"))
        self.__label_titre.pack(pady=20)
        
        # Frame des contacts
        self.__frame_contacts = Frame(self, borderwidth=10, relief="groove", padx=10, pady=10)
        self.__frame_contacts.pack(pady=20)
        
        # Boutons des contacts
        for contact in self.__liste_collaborateurs:
            btn_contact = Button(self.__frame_contacts, text=contact, font=("Helvetica", 14), command=lambda c=contact: self.appeler_contact(c))
            btn_contact.pack(pady=5, fill=X)
        
        # lancer l'IHM
        self.mainloop()
        
    def appeler_contact(self, contact):
        print(f"Ouverture de l'interface d'appel avec {contact}")
        self.destroy()
        self.__ihm_appel = IHM_Appel(contact)

# TODO INTEGRATION EXPERIMENTALE DE L'INTERFACE TELEPHONE
class IHM_Appel(Tk):
    def __init__(self, correspondant: str)-> None:
        super().__init__()
        self.title("Interface Téléphone")
        self.geometry(f"{LARGEUR_FEN}x{HAUTEUR_FEN}")  # Taille pour simuler un écran de téléphone
        self.configure(bg="white")  # Fond blanc

        # État de l'appel
        self.etat_appel = Label(self, text="État de l'appel : Ça sonne", font=("Arial", 12), bg="white")
        self.etat_appel.pack(pady=10)

        # Nom du correspondant
        self.nom_correspondant = Label(self, text="Nom du correspondant : John Doe", font=("Arial", 12), bg="white")
        self.nom_correspondant.pack(pady=10)

        # Liste déroulante pour l'annuaire de contacts
        self.label_liste = Label(self, text="Annuaire de contacts :", font=("Arial", 10), bg="white")
        self.label_liste.pack()
        self.liste_contacts = ttk.Combobox(self, values=["John Doe", "Alice", "Bob", "Eve"], font=("Arial", 10)) # TODO a supprimer une fois le nouveau menu réalisé
        self.liste_contacts.set("Sélectionner un contact")
        self.liste_contacts.pack(pady=5)

        # Partie interactive
        cadre_interactif = Frame(self, bg="lightgrey", bd=2, relief="ridge")
        cadre_interactif.pack(pady=20, padx=10, fill="both", expand=True)

        # Boutons interactifs (Couper micro, Haut-parleur)
        self.bouton_micro = Button(
            cadre_interactif, text=" Couper Micro", font=("Arial", 12), command=self.couper_micro
        )
        self.bouton_micro.pack(pady=10)

        self.bouton_hp = Button(
            cadre_interactif, text=" Haut-parleur", font=("Arial", 12), command=self.activer_hp
        )
        self.bouton_hp.pack(pady=10)

        # Bouton d'appel/raccrocher
        self.bouton_appel = Button(
            cadre_interactif, text=" Appel/Raccrocher", font=("Arial", 12), bg="lightgreen", command=self.appel
        )
        self.bouton_appel.pack(pady=20)

    def couper_micro(self):
        print("Micro coupé!")

    def activer_hp(self):
        print("Haut-parleur activé!")

    def appel(self):
        print("Appel lancé ou raccroché!")


class Utilisateur:
    def __init__(self, login:str, mdp:str, ip_serv:str)-> None:
        
        # Déclaration des attributs       
        self.__login: str
        self.__mdp: str
        self.__ip_serv: str
        # self.__ihm_appel: IHM_Appel
        self.__ihm_contacts: IHM_Contacts
        
        # Déclaration des sockets
        self.__socket_envoi: socket
        self.__socket_reception: socket
        
        # Instanciation des attributs
        self.__login = login
        self.__mdp = mdp
        self.__ip_serv = ip_serv
        
        # Création du socket d'envoi de messages
        self.__socket_envoi = socket(AF_INET, SOCK_DGRAM)
        self.__socket_envoi.bind(("", 5000))
        
        # Création du socket de réception de messages
        self.__socket_reception = socket(AF_INET, SOCK_DGRAM)
        self.__socket_reception.bind(("", 5101))
        
        # Tentative d'authentification auprès du serveur
        self.authentification()
    
    def authentification(self)-> None:
        reponse_serv: str
        
        print("Tentative d'authentification de l'utilisateur auprès du serveur.")
        self.envoyer_message(f"AUTH REQUEST {self.__login}:{self.__mdp}")
        
        print("En attente de la réponse du serveur...")
        reponse_serv = self.recevoir_message()
        
        if reponse_serv.startswith("AUTH ACCEPT"):
            print("Authentification réussie.")
            self.__ihm_contacts = IHM_Contacts(["John Doe", "Alice", "Bob", "Eve", "aaa", "bbb", "ccc", "ddd", "eee", "fff", "ggg", "hhh", "i", "j", "k", "l", "m", "n"]) # TODO à remplacer par la liste des collaborateurs donnée par le serveur
            
        else:
            print("L'authentification a échouée : ", reponse_serv)
            # TODO Rappeller une nouvelle IHM d'authentification ?
    
    def envoyer_message(self, msg:str)-> None:
        tab_octets = msg.encode(encoding="utf-8")
        self.__socket_envoi.sendto(tab_octets, (self.__ip_serv, 6100))
        
    def recevoir_message(self)-> str:
        tab_octets = self.__socket_reception.recv(255)
        msg = tab_octets.decode(encoding="utf-8")
        return msg


if __name__ == "__main__":
    LARGEUR_FEN:int = 375
    HAUTEUR_FEN:int = 700
    
    ihm_auth: IHM_Authentification
    ihm_auth = IHM_Authentification()