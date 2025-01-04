# Client VoIP
# Écrit par Tugdual Thepaut et Yann Plougonven--Lastennet
# Projet de S3 de BUT R&T à l'IUT de Lannion - Décembre 2024 / Janvier 2025
# Dépôt GitHub : https://github.com/Yann-Plougonven/VoIPy

from pyaudio import *
from socket import *
from tkinter import *
from threading import *
from time import sleep
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
        self.__label_ip_client = Label(self.__frame_serv, text=f"Votre IP client : {gethostbyname(gethostname())}") # TODO l'IP affichée n'est pas celle de la bonne carte réseau
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
        
        # TODO : ajouter le support de l'appui sur la touche "Entrée" pour valider l'authentification
        
        # lancer l'IHM
        self.mainloop()
        
    def creer_utilisateur(self)-> None:
        # (il est nécessaire de récupérer les valeurs renseignées champs avant de fermer la fenêtre)
        login: str
        mdp: str
        ip_serv: str
        self.__utilisateur: Utilisateur
        
        login = self.__entry_login.get()
        mdp = self.__entry_mdp.get()
        ip_serv = self.__entry_ip_serv.get()
        self.destroy()
        
        self.__utilisateur = Utilisateur(login, mdp, ip_serv)
        
    # def quit(self)-> None: # TODO
    #     self.destroy()


class IHM_Contacts(Tk):
    def __init__(self, utilisateur)-> None:
        Tk.__init__(self)
        
        # déclaration des attributs
        self.__utilisateur: Utilisateur
        self.__login_utilisateur: str
        self.__ihm_appel: IHM_Appel
        
        self.__stop_thread_event: Event
        self.__thread_ecoute: Thread
        
        self.__frame_contacts: Frame
        self.__label_titre: Label
        self.__label_sous_titre: Label
        self.__btn_actualiser: Button
        
        # Instanciation des attributs
        self.title("Choix du collaborateur à appeler")
        self.geometry(f"{LARGEUR_FEN}x{HAUTEUR_FEN}")
        self.__utilisateur = utilisateur
        self.__login_utilisateur = self.__utilisateur.get_login()
        self.__stop_thread_event = Event()
        
        # Titre principal
        self.__label_titre = Label(self, text="Appeler un collaborateur", font=("Helvetica", 20, "bold"))
        self.__label_sous_titre = Label(self, text="Les contacts connectés apparaissent en vert", font=("Helvetica", 12))
        self.__label_titre.pack(pady=10)
        self.__label_sous_titre.pack()
        
        # Bouton d'actualisation de la liste des contacts TODO
        self.__btn_actualiser = Button(self, text="Actualiser la liste", font=("Helvetica", 14), command=self.lister_contacts)
        self.__btn_actualiser.pack(pady=10)
        
        # Frame des contacts
        self.__frame_contacts = Frame(self, borderwidth=10, relief="groove", padx=10, pady=10)
        self.__frame_contacts.pack(pady=20, fill='x')
        
        # Intercepte la fermeture de la fenêtre et appelle la méthode quit
        self.protocol("WM_DELETE_WINDOW", self.quit)
        
        # Liste/Boutons des contacts
        self.lister_contacts()
    
    def lister_contacts(self)-> None:
        """Initialise ou actualise la liste des contacts.
        Appelle la fonction actualiser_liste_contacts() de la classe Utilisateur pour obtenir la liste des contacts.
        Note : le choix de ne pas passer la liste de contacts en paramètre de la classe IHM_Contacts
        est dû au fait que la liste des contacts peut être actualisée par l'utilisateur
        """
        # Initialisation des variables/attributs
        str_contacts: str
        contact: str
        widget: Widget
        self.__dict_contacts: dict[str]
        
        # Arrêt de l'écoute de requête d'appel, si elle est déjà lancée, pour éviter les interférences
        self.stopper_deamon_ecoute_requetes_appel(180)
        
        # Récupérer la liste des contacts
        str_contacts = self.__utilisateur.actualiser_liste_contacts() # obtenir les contacts sous forme de chaine
        str_contacts = str_contacts[13:] # supprimer l'entête "CONTACTS LIST" (13 premiers caractères de la chaine)
        self.__dict_contacts = eval(str_contacts) # convertir la chaine en dicts de contacts liés à leur statut (online, offline)
        
        # Supprimer les anciens boutons de la liste de contacts
        for widget in self.__frame_contacts.winfo_children():
            widget.destroy()
        
        # Ajouter les contacts sous forme de boutons
        for contact in self.__dict_contacts.keys():          
            btn_contact = Button(self.__frame_contacts, text=contact, font=("Helvetica", 14), command=lambda correspondant=contact: self.appeler_correspondant(correspondant))
            btn_contact.pack(pady=4, fill=X)
            
            # Si le contact est en ligne, le bouton est vert.
            if self.__dict_contacts[contact] == "online":
                btn_contact.configure(bg="PaleGreen1")

                # Si le contact est le client lui même, le bouton est désactivé (il ne peut pas s'appeller lui-même)
                if contact == self.__login_utilisateur:
                    btn_contact.configure(state=DISABLED)
            
            # Sinon, si le contact est hors ligne ou est le client lui même, le bouton est rouge et désactivé.
            else:
                btn_contact.configure(bg="RosyBrown1")
                btn_contact.configure(state=DISABLED)
        
        # Ecouter les potentielles requêtes d'appel, 100ms après l'ouverture de la fenêtre.
        # Cela permet de laisser la fenêtre s'ouvrir avant que le client boucle sur l'écoute de requête d'appel.
        self.after(100, self.demarrer_deamon_ecoute_requetes_appel) # after() permet d'appeler ecouter_requete_appel après 100ms. 
                                                    # TODO jsp si c'est utile ici
        
        # lancer l'IHM (Note : même si on dirait que ça ne sert à rien, 
        # c'est notamment nécessaire pour que la fenêtre se ferme correctement)
        self.mainloop()
        
    def appeler_correspondant(self, correspondant: str)-> None:
        # Arrêt de l'écoute de requête d'appel pour éviter les interférences
        self.stopper_deamon_ecoute_requetes_appel(180)
                
        # Ouverture de l'interface d'appel
        print(f"Ouverture de l'interface d'appel avec {correspondant}...")
        self.destroy() # fermeture de la fenêtre de contacts
        self.__ihm_appel = IHM_Appel(self.__utilisateur, correspondant, le_client_est_l_appellant=True) # ouverture de l'IHM d'appel
        
    def ecouter_requete_appel(self)-> None:
        """Ecoute en arrirère-plan des potentielles requêtes d'appel entrantes.
        L'écoute en arrière-plan a lieu quand le client est connecté n'est pas en appel,
        c'est-à-dire, quand la fenêtre des contacts est ouvertes.
        """
        msg:str
        correspondant:str
                
        # Définir un court timeout de réception pour vérifier régulièrement si le programme demande l'arrêt du thread
        self.__utilisateur.set_timeout_socket_reception(0.1) 
        
        print("Écoute en cours de potentielle requête d'appel...")
        
        # Tant qu'on ne demande pas l'arrêt du thread, on écoute les potentielles requêtes d'appel
        while not self.__stop_thread_event.is_set(): 
            try:
                msg = self.__utilisateur.recevoir_message()
                
                # Si le message reçu est une requête d'appel, on ouvre l'IHM d'appel et on arrête l'écoute des requêtes d'appel
                if msg.startswith("CALL REQUEST"):
                    correspondant = msg[13:] # supprimer l'entête "CALL REQUEST " du message (13 premiers caractères de la chaine)
                    print(f"Requête d'appel reçue de {correspondant}.")
                    self.__stop_thread_event.set() # demander l'arrêt du thread
                    self.__utilisateur.set_timeout_socket_reception(180) # réinitialiser le timeout du socket de réception
                    
                    # Ouvrir l'IHM d'appel avec le correspondant, et détruire la fenêtre des contacts
                    # Il est nécessaire d'utiliser after() pour détruire l'IHM_contacts 
                    # en étant dans le bon thread (thread principal), sinon le programme plante.
                    self.after(0, self.ouvrir_ihm_appel, correspondant) 
            
            except timeout: 
                continue # Si le timeout est atteint, on recommence la boucle, qui vérifie d'abord si l'arrêt du thread est demandé
                        
    def demarrer_deamon_ecoute_requetes_appel(self):
        """Démarre le thread d'écoute de requête d'appel en arrière-plan.
        """
        self.__stop_thread_event.clear() # réinitialiser l'événement de demande d'arrêt du thread
        self.__thread_ecoute = Thread(target=self.ecouter_requete_appel) # création du thread
        self.__thread_ecoute.daemon = True # configuration du thread en mode deamon
        self.__thread_ecoute.start() # démarrage du thread
        
    def stopper_deamon_ecoute_requetes_appel(self, timeout:float=190)-> None:
        """Arrêt du thread d'écoute de requête d'appel, s'il est déjà démarré, pour éviter les interférences.
        Définit un "long" timeout pour le socket de réception de la signalisation (protocole applicatif),
        étant donné que le timeout est de seulement 100ms pour le deamon d'écoute des requête d'appel.
        et que la réception de signalisations plus spécifiques peut prendre plus de temps et n'est pas bouclée.

        Args:
            timeout (float): timeout du socket de réception de la signalisation (180s pour répondre à l'appel, par défaut)
        """
        try:
            if self.__thread_ecoute.is_alive():
                print(f"Arrêt temporaire de l'écoute des requêtes d'appels")
                self.__stop_thread_event.set() # Demande d'arrêt du thread d'écoute de requête d'appel
                self.__thread_ecoute.join() # Attente de l'arrêt du thread d'écoute de requête d'appel
                self.__utilisateur.set_timeout_socket_reception(timeout) # Définir le timeout passé en paramètre

        except AttributeError: # Si le thread d'écoute n'est pas encore démarré
            pass
        
    def ouvrir_ihm_appel(self, correspondant:str)-> None:
        """Fermer l'IHM des contacts depuis le thread principal,
        et ouvrir l'IHM d'appel avec le correspondant.
        Il est nécessaire d'utiliser le thread principal pour détruire l'IHM des contacts,
        sinon le programme plante.

        Args:
            correspondant (str): login du correspondant qui a demandé l'appel
        """
        # Fermer l'IHM des contacts depuis le thread principal
        self.destroy() # fermer l'IHM des contacts
        # Ouvrir l'IHM d'appel avec le correspondant
        self.__ihm_appel = IHM_Appel(self.__utilisateur, correspondant, le_client_est_l_appellant=False) # ouvrir l'IHM d'appel
    
    def quit(self)-> None:
        """Gérer la fermeture de l'IHM client : déconnexion de l'utilisateur et fermeture de la fenêtre.
        """
        self.__utilisateur.deconnexion()
        
        # TODO gestion de la fermeture des sockets (jsp si c'est nécessaire)
        self.destroy() 

# TODO : faire en sorte que toutes les IMH aient la même charte graphique, et supprimer les éléments inutiles 
# de IHM_Appel (certainement la liste déroulante de contacts)
class IHM_Appel(Tk):
    def __init__(self, utilisateur, correspondant: str, le_client_est_l_appellant:bool)-> None:
        Tk.__init__(self)
        
        # Déclaration des attributs
        self.__utilisateur: Utilisateur
        self.__login_utilisateur: str
        self.__correspondant: str
        self.__le_client_est_l_appellant: bool
        self.__label_correspondant: Label
        self.__label_etat_appel: Label
        self.__label_liste: Label
        self.__liste_contacts: ttk.Combobox
        self.__cadre_interactif: Frame
        self.__bouton_micro: Button
        self.__bouton_hp: Button
        self.__bouton_decrocher: Button
        self.__bouton_racrocher: Button
        
        # Instanciation des attributs
        self.__utilisateur = utilisateur
        self.__login_utilisateur = self.__utilisateur.get_login()
        self.__correspondant = correspondant
        self.__le_client_est_l_appellant = le_client_est_l_appellant
        self.title("Appel VoIP")
        self.geometry(f"{LARGEUR_FEN}x{HAUTEUR_FEN}") # Taille de fenêtre pour simuler un écran de téléphone

        # État de l'appel
        self.__label_etat_appel = Label(self, text="État de l'appel : Ça sonne", font=("Arial", 12), bg="white")
        self.__label_etat_appel.pack(pady=10)

        # Nom du correspondant
        self.__label_correspondant = Label(self, text=f"Correspondant : {self.__correspondant}", font=("Arial", 12), bg="white")
        self.__label_correspondant.pack(pady=10)

        # Liste déroulante pour l'annuaire de contacts
        self.__label_liste = Label(self, text="Annuaire de contacts :", font=("Arial", 10), bg="white")
        self.__label_liste.pack()
        self.__liste_contacts = ttk.Combobox(self, values=["John Doe", "Alice", "Bob", "Eve"], font=("Arial", 10)) # TODO a supprimer une fois le nouveau menu réalisé
        self.__liste_contacts.set("Sélectionner un contact")
        self.__liste_contacts.pack(pady=5)

        # Partie interactive
        self.__cadre_interactif = Frame(self, bg="lightgrey", bd=2, relief="ridge")
        self.__cadre_interactif.pack(pady=20, padx=10, fill="both", expand=True)

        # Boutons interactifs (Couper micro, Haut-parleur)
        self.__bouton_micro = Button(
            self.__cadre_interactif, text=" Couper Micro", font=("Arial", 12), command=self.couper_micro)
        self.__bouton_micro.grid(row=0, column=0, pady=10)

        self.__bouton_hp = Button(
            self.__cadre_interactif, text=" Haut-parleur", font=("Arial", 12), command=self.activer_hp)
        self.__bouton_hp.grid(row=0, column=1, pady=10)

        # Bouton pour décrocher TODO ne doit pas être visible si l'appel est en cours
        self.__bouton_decrocher = Button(
            self.__cadre_interactif, text="Décrocher", font=("Arial", 12), bg="PaleGreen1", command=self.decrocher)
        self.__bouton_decrocher.grid(row=2, column=0, pady=10)
        
        # Bouton pour raccrocher
        self.__bouton_raccrocher = Button(
            self.__cadre_interactif, text="Racrocher", font=("Arial", 12), bg="RosyBrown1", command=self.raccrocher)
        self.__bouton_raccrocher.grid(row=2, column=1, pady=10)
        self.__bouton_decrocher.configure(state=DISABLED) # Désactiver le bouton "Décrocher" (il est réactivé si le client est appellé)
        
        # Intercepte la fermeture de la fenêtre et appelle la méthode quit
        self.protocol("WM_DELETE_WINDOW", self.quit)
        
        # Envoyer une requête d'appel au serveur si le client est l'appellant, 100ms après l'ouverture de la fenêtre.
        # Cela permet de laisser la fenêtre s'ouvrir avant que le correspondant décroche.
        if self.__le_client_est_l_appellant:
            self.after(100, self.envoyer_requete_appel) # after() permet d'appeler envoyer_requete_appel après 100ms.
        
        # Si le client est appellé, activer le bouton "Décrocher"
        else:
            self.__bouton_decrocher.configure(state=NORMAL)
            
        # lancer l'IHM
        self.mainloop()


    def envoyer_requete_appel(self)-> None:
        requete_appel_acceptee: bool
        requete_appel_acceptee = self.__utilisateur.envoyer_requete_appel(self.__correspondant)
        
        # Si l'appel est accepté
        if requete_appel_acceptee:
            # TODO : c'est la même chose que dans la méthode "décrocher" : à factoriser
            self.__bouton_decrocher.configure(state=DISABLED) # Désactiver le bouton "Décrocher"
            self.__label_etat_appel.configure(text="Appel en cours", bg="PaleGreen1")
            self.__utilisateur.demarrer_appel()
        
        # Si l'appel est refusé
        else: 
            self.__label_etat_appel.configure(text="Appel refusé", bg="RosyBrown1")
            sleep(3) # attendre 3 secondes pour que l'utilisateur puisse lire le message
            self.destroy() # fermeture de la fenêtre d'appel
            # TODO rouvrir la fenêtre de contacts
    
    def couper_micro(self):
        print("Micro coupé!")
        # TODO

    def activer_hp(self):
        print("Haut-parleur activé!")
        # TODO
        
    def decrocher(self):
        autorisation_de_demarrer_appel: bool
        autorisation_de_demarrer_appel = False # Interdit avant la réception du "CALL START" du serveur
        
        print("Vous avez décroché l'appel.")
        self.__label_etat_appel.configure(text="Acceptation de l'appel...", bg="white")
        
        autorisation_de_demarrer_appel = self.__utilisateur.accepter_appel(self.__correspondant, self.__login_utilisateur)
        
        if autorisation_de_demarrer_appel:
            # TODO : c'est la même chose que dans la méthode "envoyer_requete_appel" : à factoriser
            self.__bouton_decrocher.configure(state=DISABLED) # Désactiver le bouton "Décrocher"
            self.__label_etat_appel.configure(text="Appel en cours", bg="PaleGreen1")
            self.__utilisateur.demarrer_appel()
        
    def raccrocher(self):
        print("Vous avez raccroché l'appel.")
        # TODO à faire

    def quit(self)-> None:
        """Gérer la fermeture de l'IHM client : déconnexion de l'utilisateur et fermeture de la fenêtre.
        """
        self.__utilisateur.deconnexion()
        
        # TODO gestion de la fermeture de la fenêtre de contacts (j'ai pas regardé comment faire)
        self.destroy() 


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
        reponse_serv_contacts: str
        
        print("Tentative d'authentification de l'utilisateur auprès du serveur.")
        self.envoyer_message(f"AUTH REQUEST {self.__login}:{self.__mdp}")
        
        print("En attente de la réponse du serveur...")
        reponse_serv = self.recevoir_message()
        
        # Si l'authentification est réussie, on récupère la liste des contacts et affiche la fenêtre de contacts :
        if reponse_serv.startswith("AUTH ACCEPT"):
            print("Authentification réussie.")
            self.__ihm_contacts = IHM_Contacts(self)
            
        # Si l'authentification est refusée :
        else:
            print("L'authentification a échouée :", reponse_serv)
            # TODO Rappeller une nouvelle IHM d'authentification ou afficher un message d'erreur
            
    def deconnexion(self)-> None:
        print("Information du serveur de notre déconnexion...")
        self.envoyer_message(f"LOGOUT {self.__login}")
    
    def envoyer_message(self, msg:str)-> None:
        tab_octets = msg.encode(encoding="utf-8")
        self.__socket_envoi.sendto(tab_octets, (self.__ip_serv, 6100))
        
    def recevoir_message(self)-> str:
        tab_octets = self.__socket_reception.recv(255)
        msg = tab_octets.decode(encoding="utf-8")
        return msg
    
    def actualiser_liste_contacts(self)-> str:
        reponse_serv_contacts: str
        reponse_serv_contacts = "" # TODO mieux gérer l'erreur si la liste des contacts n'a pas pu être récupérée
        
        print("Tentative d'actualisation de la liste de contacts...")
        self.envoyer_message(f"CONTACTS REQUEST")
        reponse_serv_contacts = self.recevoir_message()
        
        if reponse_serv_contacts.startswith("CONTACTS LIST"):
            print("La liste de contacts a été récupérée.")
        
        else: # Si la liste des contacts n'a pas pu être récupérée
                print("Erreur : la liste des contacts n'a pas pu être récupérée.")
        
        return reponse_serv_contacts
    
    def envoyer_requete_appel(self, correspondant:str)-> bool:
        reponse_serv_requete_appel:str
        requete_appel_acceptee:bool
        requete_appel_acceptee = False
        
        print(f"Envoi de la requête d'appel pour {correspondant} au serveur...")
        self.envoyer_message(f"CALL REQUEST {correspondant}")
        reponse_serv_requete_appel = self.recevoir_message()
        
        if reponse_serv_requete_appel.startswith("CALL START"):
            print(f"Le serveur et {correspondant} ont accepté la requête d'appel.")
            requete_appel_acceptee = True
        
        return requete_appel_acceptee
    
    def accepter_appel(self, login_correspondant, login_utilisateur)-> bool:
        autorisation_de_demarrer_appel: bool
        autorisation_de_demarrer_appel = False # Interdit avant la réception du "CALL ACCEPT" du serveur
        reponse_serv_requete_demarrer_appel = str # Réponse "CALL ACCEPT" du serveur
        
        print(f"Envoi de l'acceptation de l'appel avec {login_correspondant} au serveur...")
        # Le message à envoyer est de la forme "CALL ACCEPT login_appelant-login_appele_acceptant_l_appel"
        self.envoyer_message(f"CALL ACCEPT {login_correspondant}-{login_utilisateur}") 
        
        reponse_serv_requete_demarrer_appel = self.recevoir_message() # Attendre le "CALL ACCEPT" du serveur
        
        if reponse_serv_requete_demarrer_appel.startswith("CALL START"):
            print(f"Le serveur a accepté le démarrage de l'appel avec {login_correspondant}.")
            autorisation_de_demarrer_appel = True
        
        return autorisation_de_demarrer_appel
        
    def demarrer_appel(self)-> None:
        print("L'appel est en cours...")
        # TODO gros travail ici, recevoir et envoyer les paquets de conversation audio
    
    def get_login(self)-> str:
        return self.__login
    
    def set_timeout_socket_reception(self, timeout:float=180)-> None:
        self.__socket_reception.settimeout(timeout)


if __name__ == "__main__":
    LARGEUR_FEN:int = 375
    HAUTEUR_FEN:int = 700
    
    ihm_auth: IHM_Authentification
    ihm_auth = IHM_Authentification()