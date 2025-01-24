# Client VoIP
# Écrit par Tugdual Thepaut et Yann Plougonven--Lastennet
# Projet de S3 de BUT R&T à l'IUT de Lannion - Décembre 2024 / Janvier 2025
# Information : si vous exécutez ce programme dans VSCode, pensez à ouvrir tout le dossier "VoIPy" dans VSCode.
# Dépôt GitHub : https://github.com/Yann-Plougonven/VoIPy

from pyaudio import *
from socket import *
from tkinter import *
from threading import *
from time import sleep
from pydub import AudioSegment
import json

class IHM_Authentification(Tk):
    def __init__(self, msg_erreur:str="")-> None:
        """Constructeur de la classe définissant l'inteface graphique d'authentification du client VoIP auprès du serveur VoIP.

        Args:
            msg_erreur (str, optional): message d'erreur affiché sur l'interface en cas de problème. Defaults to "".
        """
        Tk.__init__(self)
        
        # déclaration des attributs
        self.__label_erreur: Label
        
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
        
        # Message d'erreur
        self.__label_erreur = Label(self, text=msg_erreur, font=("Arial", 11), fg="red2")
        
        # Frame d'authentification
        self.__frame_auth = Frame(self, borderwidth=10, relief="groove", padx=10, pady=10)
        self.__entry_login = Entry(self.__frame_auth, width=50)
        self.__label_login = Label(self.__frame_auth, text="Identifiant")
        self.__entry_mdp = Entry(self.__frame_auth, width=50, show="*")
        self.__label_mdp = Label(self.__frame_auth, text="Mot de passe")
        
        # Frame de choix du serveur
        self.__frame_serv = Frame(self, borderwidth=10, relief="groove", padx=10, pady=10)
        self.__label_ip_client = Label(self.__frame_serv, text=f"Votre IP client : {gethostbyname(gethostname())}")
        self.__entry_ip_serv = Entry(self.__frame_serv, width=50)
        self.__entry_ip_serv.insert(0, "127.0.0.1") # valeur par défaut
        self.__label_ip_serv = Label(self.__frame_serv, text="IP du serveur VoIP")
        self.__btn_auth = Button(self.__frame_serv, text="Authentification", command=self.creer_utilisateur) # lance la création de l'utilisateur (et son authentification)
        
        # Ajout des widgets
        self.__label_erreur.pack(pady=10)
        
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
        
        # intercepte la fermeture de la fenêtre et appellera la méthode quit
        self.protocol("WM_DELETE_WINDOW", self.quit)
        
        # Ajouter le support de l'appui sur la touche "Entrée" pour valider l'authentification
        self.bind("<Return>", lambda event: self.creer_utilisateur())
        self.bind("<KP_Enter>", lambda event: self.creer_utilisateur())
        
        # lancer l'IHM
        self.mainloop()
        
    def creer_utilisateur(self)-> None:
        """Créer un objet Utilisateur à partir des informations renseignées dans les champs de l'IHM d'authentification.
        """
        login: str
        mdp: str
        ip_serv: str
        
        login = self.__entry_login.get()
        mdp = self.__entry_mdp.get()
        ip_serv = self.__entry_ip_serv.get()
        self.destroy()
        
        Utilisateur(login, mdp, ip_serv)
        
    def quit(self)-> None:
        """Gestion de la fermeture de la fenêtre de l'IHM d'authentification.
        """
        self.destroy()


class IHM_Contacts(Tk):
    def __init__(self, utilisateur)-> None:
        """Constructeur de la classe définissant l'interface graphique des contacts du client VoIP.

        Args:
            utilisateur (Utilisateur): objet Utilisateur correspondant à l'utilisateur connecté.
        """
        Tk.__init__(self)
        
        # déclaration des attributs
        self.__utilisateur: Utilisateur
        self.__login_utilisateur: str
        
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
        self.__label_sous_titre = Label(self, text="Les contacts disponibles apparaissent en vert", font=("Helvetica", 12))
        self.__label_titre.pack(pady=10)
        self.__label_sous_titre.pack()
        
        # Bouton d'actualisation de la liste des contacts
        self.__btn_actualiser = Button(self, text="Actualiser la liste", font=("Helvetica", 14), command=self.lister_contacts)
        self.__btn_actualiser.pack(pady=10)
        
        # Frame des contacts
        self.__frame_contacts = Frame(self, borderwidth=10, relief="groove", padx=10, pady=10)
        self.__frame_contacts.pack(pady=20, fill='x')
        
        # Intercepte la fermeture de la fenêtre et appelle la méthode quit
        self.protocol("WM_DELETE_WINDOW", self.quit)
        
        # Liste/Boutons des contacts
        try:
            self.lister_contacts()
        except:
            print("Erreur lors de l'actualisation de la liste des contacts.")
    
    def lister_contacts(self)-> None:
        """Initialise ou actualise la liste des contacts.
        Appelle la fonction actualiser_liste_contacts() de la classe Utilisateur pour obtenir la liste des contacts.
        Note : le choix de ne pas passer la liste de contacts en paramètre de la classe IHM_Contacts
        est dû au fait que la liste des contacts peut être actualisée manuellement par l'utilisateur.
        """
        # Initialisation des variables/attributs
        contact: str
        widget: Widget
        dict_contacts: dict[str: list[str]]
        
        # Arrêt de l'écoute de requête d'appel, si elle est déjà lancée, pour éviter les interférences
        self.stopper_deamon_ecoute_requetes_appel()
        
        # Récupérer la liste des contacts (format : dictionnaire python)
        dict_contacts = self.__utilisateur.actualiser_liste_contacts()
        
        # Supprimer les anciens boutons de la liste de contacts
        for widget in self.__frame_contacts.winfo_children():
            widget.destroy()
        
        # Ajouter les contacts sous forme de boutons
        for contact in dict_contacts.keys():          
            btn_contact = Button(self.__frame_contacts, text=contact, font=("Helvetica", 14), command=lambda correspondant=contact: self.appeler_correspondant(correspondant))
            btn_contact.pack(pady=4, fill=X)
            
            # Si le contact est en ligne, mais pas en appel, le bouton est vert
            if "online" in dict_contacts[contact] and "available" in dict_contacts[contact]:
                btn_contact.configure(bg="PaleGreen1")

                # Si le contact est le client lui même, le bouton est désactivé (il ne peut pas s'appeller lui-même)
                if contact == self.__login_utilisateur:
                    btn_contact.configure(state=DISABLED)
            
            # Si le contact est en ligne, mais en appel, le bouton est orange et désactivé
            elif "online" in dict_contacts[contact] and "oncall" in dict_contacts[contact]:
                btn_contact.configure(bg="light goldenrod")
                btn_contact.configure(state=DISABLED)
            
            # Sinon, si le contact est hors ligne (ou que son statut semble incorrect), le bouton est rouge et désactivé.
            else:
                btn_contact.configure(bg="RosyBrown1")
                btn_contact.configure(state=DISABLED)
        
        # Ecouter les potentielles requêtes d'appel, 100ms après l'ouverture de la fenêtre.
        # Cela permet de laisser la fenêtre s'ouvrir avant que le client boucle sur l'écoute de requête d'appel.
        self.after(100, self.demarrer_deamon_ecoute_requetes_appel) # after() permet d'appeler ecouter_requete_appel après 100ms. 
        
        # lancer l'IHM (Note : même si on dirait que ça ne sert à rien, 
        # c'est notamment nécessaire pour que la fenêtre se ferme correctement)
        self.mainloop()
        
    def appeler_correspondant(self, correspondant: str)-> None:
        """Instancie l'interface d'appel avec le correspondant sélectionné.
        Pour cela, arrête arrête d'abord l'écoute de requête d'appel pour éviter les interférences.

        Args:
            correspondant (str): login du correspondant à appeller
        """
        # Arrêt de l'écoute de requête d'appel pour éviter les interférences
        self.stopper_deamon_ecoute_requetes_appel()
                
        # Ouverture de l'interface d'appel
        print(f"Ouverture de l'interface d'appel avec {correspondant}...")
        self.destroy() # fermeture de la fenêtre de contacts
        IHM_Appel(self.__utilisateur, correspondant, le_client_est_l_appellant=True) # ouverture de l'IHM d'appel
        
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
                    self.__utilisateur.set_timeout_socket_reception(60) # réinitialiser le timeout du socket de réception
                    
                    
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
        
    def stopper_deamon_ecoute_requetes_appel(self)-> None:
        """Arrêt du thread d'écoute de requête d'appel, s'il est déjà démarré, pour éviter les interférences.
        Définit un "long" timeout pour le socket de réception de la signalisation (protocole applicatif),
        étant donné que le timeout est de seulement 100ms pour le deamon d'écoute des requête d'appel.
        et que la réception de signalisations plus spécifiques peut prendre plus de temps et n'est effectuée en boucle.
        """
        try:
            if self.__thread_ecoute.is_alive():
                print(f"Arrêt temporaire de l'écoute des requêtes d'appels")
                self.__stop_thread_event.set() # Demande d'arrêt du thread d'écoute de requête d'appel
                self.__thread_ecoute.join() # Attente de l'arrêt du thread d'écoute de requête d'appel
                self.__utilisateur.set_timeout_socket_reception(60) # Définir le timeout du socket de réception à 60 secondes

        except AttributeError:
            # évite le plantage du programme en cas de problème
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
        self.destroy()
        # Ouvrir l'IHM d'appel avec le correspondant
        IHM_Appel(self.__utilisateur, correspondant, le_client_est_l_appellant=False)
    
    def quit(self)-> None:
        """Gérer la fermeture de l'IHM client : déconnexion de l'utilisateur et fermeture de la fenêtre.
        """
        self.__utilisateur.deconnexion()
        self.destroy() 


class IHM_Appel(Tk):
    def __init__(self, utilisateur, correspondant: str, le_client_est_l_appellant:bool)-> None:
        """Constructeur de la classe définissant l'interface graphique d'appel VoIP.

        Args:
            utilisateur (Utilisateur): objet Utilisateur correspondant à l'utilisateur connecté.
            correspondant (str): login du correspondant.
            le_client_est_l_appellant (bool): True si le client est l'appellant, False si le client est appellé : l'interface s'adapte en conséquence.
        """
        Tk.__init__(self)
        
        # Déclaration des attributs
        self.__utilisateur: Utilisateur
        self.__login_utilisateur: str
        self.__correspondant: str
        self.__le_client_est_l_appellant: bool
        self.__appel_en_cours: bool
        self.__label_correspondant: Label
        self.__label_etat_appel: Label
        self.__cadre_interactif: Frame
        self.__bouton_micro: Button
        self.__bouton_hp: Button
        self.__bouton_decrocher: Button
        self.__bouton_raccrocher: Button
        
        # Instanciation des attributs
        self.__utilisateur = utilisateur
        self.__login_utilisateur = self.__utilisateur.get_login()
        self.__correspondant = correspondant
        self.__le_client_est_l_appellant = le_client_est_l_appellant
        self.__appel_en_cours = False
        self.title("Appel VoIP")
        self.geometry(f"{LARGEUR_FEN}x{HAUTEUR_FEN}") # Taille de fenêtre pour simuler un écran de téléphone

        # État de l'appel
        self.__label_etat_appel = Label(self, text="État de l'appel : Ça sonne", font=("Arial", 12), bg="white")
        self.__label_etat_appel.pack(pady=10)

        # Nom du correspondant
        self.__label_correspondant = Label(self, text=f"Correspondant : {self.__correspondant}", font=("Arial", 12), bg="white")
        self.__label_correspondant.pack(pady=10)

        # Partie interactive
        self.__cadre_interactif = Frame(self, bg="lightgrey", bd=2, relief="ridge")
        self.__cadre_interactif.pack(pady=20, padx=10, fill="both", expand=True)

        # Configurer la grille pour le placement des boutons
        self.__cadre_interactif.grid_rowconfigure(0, weight=1)  # Pour centrer les éléments à la verticale
        self.__cadre_interactif.grid_rowconfigure(1, weight=1)
        self.__cadre_interactif.grid_rowconfigure(2, weight=1)
        self.__cadre_interactif.grid_columnconfigure(0, weight=1)  # Pour centrer les éléments à l'horizontale
        self.__cadre_interactif.grid_columnconfigure(1, weight=1)
        
        # Boutons interactifs (Couper micro, Haut-parleur)
        self.__bouton_micro = Button(
            self.__cadre_interactif, text=" Couper Micro", font=("Arial", 12), command=self.couper_micro)
        self.__bouton_micro.grid(row=0, column=0, padx=10 , pady=10, sticky="e") # aligné à droite de sa cellule

        self.__bouton_hp = Button(
            self.__cadre_interactif, text=" Haut-parleur", font=("Arial", 12), command=self.activer_hp)
        self.__bouton_hp.grid(row=0, column=1, padx=10, pady=10, sticky="w") # alligné à gauche de la cellule

        # Bouton pour décrocher (centré)
        self.__bouton_decrocher = Button(
            self.__cadre_interactif, text="Décrocher", font=("Arial", 12), bg="PaleGreen1", command=self.decrocher)
        self.__bouton_decrocher.grid(row=1, column=0, columnspan=2 ,pady=10, sticky="n") # centré sur les 2 colonnes
        
        # Bouton pour raccrocher (centré en bas)
        self.__bouton_raccrocher = Button(
            self.__cadre_interactif, text="Raccrocher", font=("Arial", 12), bg="RosyBrown1", command=self.raccrocher)
        self.__bouton_raccrocher.grid(row=2, column=0, columnspan=2, pady=10, sticky="s") # centré sur 2 colonnes
        self.__bouton_decrocher.configure(state=DISABLED) # Désactiver le bouton "Décrocher" (il est réactivé si le client est appellé)
        
        # Intercepte la fermeture de la fenêtre et appelle la méthode quit
        self.protocol("WM_DELETE_WINDOW", self.quit)
        
        # Mettre à jour la valeur de l'attribut __ihm_appel de l'objet utilisateur,
        # afin que l'objet utilisateur puisse facilement interagir avec l'IHM d'appel.
        self.__utilisateur.set_attribut_ihm_appel(self)
        
        # Envoyer une requête d'appel au serveur si le client est l'appellant, 100ms après l'ouverture de la fenêtre.
        # Cela permet de laisser la fenêtre s'ouvrir avant que le correspondant décroche.
        if self.__le_client_est_l_appellant:
            self.after(100, self.envoyer_requete_appel) # after() permet d'appeler envoyer_requete_appel après 100ms.
        
        # Si le client est appellé, activer le bouton "Décrocher" et lancer la sonnerie d'appel
        else:
            # Activer le bouton "Décrocher"
            self.__bouton_decrocher.configure(state=NORMAL)
            
            # Jouer la sonnerie (dans un thread séparé pour ne pas bloquer l'interface)
            Thread(target=self.play_audio_with_pyaudio, args=("sonnerie/appel.mp3",)).start()
            
        # lancer l'IHM
        self.mainloop()

    def envoyer_requete_appel(self)-> None:
        """Appel la méthode envoyer_requete_appel de l'objet utilisateur pour envoyer une requête d'appel au serveur.
        Adapte l'interface en fonction de la réponse du serveur.
        """
        autorisation_de_demarrer_l_appel: bool
        port_reception_voix_du_serveur: int
        
        # Jouer la sonnerie (dans un thread séparé pour ne pas bloquer l'interface)
        Thread(target=self.play_audio_with_pyaudio, args=("sonnerie/appel.mp3",)).start()
        
        # Envoi de la requête d'appel
        autorisation_de_demarrer_l_appel, port_reception_voix_du_serveur = self.__utilisateur.envoyer_requete_appel(self.__correspondant)
        
        # Si l'appel est accepté
        if autorisation_de_demarrer_l_appel:
            print("Le client doit envoyer sa voix sur le port serveur", port_reception_voix_du_serveur)
            
            # Démarer l'appel dans un thread séparé :
            Thread(target=self.demarrer_appel, args=(port_reception_voix_du_serveur,)).start()
        
        # Si l'appel est refusé
        else:
            # Afficher un message d'appel refusé et attendre 3 secondes pour que l'utilisateur puisse lire le message
            self.__label_etat_appel.configure(text="Appel refusé", bg="RosyBrown1")
            self.play_audio_with_pyaudio("sonnerie/raccrocher.mp3")
            
            # Fermer l'IHM d'appel et réouvrir la fenêtre des contacts
            self.destroy()
            IHM_Contacts(self.__utilisateur)

    def decrocher(self)-> None:
        """Appel des fonctions de décrochage de l'appel et de démarrage de l'appel.
        Mise à jour de l'interface en en attendant le démarrage de l'appel.
        """
        port_reception_voix_du_serveur: int
        
        # Mise à jour de l'interface en "Acceptation de l'appel..."
        self.__label_etat_appel.configure(text="Acceptation de l'appel...", bg="white")
        
        # Décrocher l'appel et récupérer le port de réception de la voix du serveur
        port_reception_voix_du_serveur = self.__utilisateur.decrocher(self.__correspondant, self.__login_utilisateur)
        
        # Démarrer l'appel dans un thread séparé pour ne pas que l'interface freeze
        Thread(target=self.demarrer_appel, args=(port_reception_voix_du_serveur,)).start()

    def demarrer_appel(self, port_reception_voix_du_serveur:int)-> None:
        """Démarrer l'appel avec le correspondant.
        Mise à jour de l'interface en conséquence et appel de la méthode demarrer_appel de l'objet utilisateur.

        Args:
            port_reception_voix_du_serveur (int): port que le serveur veut que le client utilise pour envoyer sa voix
        """
        self.__appel_en_cours = True
        
        # Mettre à jour l'interface
        self.__bouton_decrocher.configure(state=DISABLED) # Désactiver le bouton "Décrocher"
        self.__label_etat_appel.configure(text="Appel en cours", bg="PaleGreen1") # Mettre à jour l'état de l'appel
        sleep(1) # attendre 1 seconde sinon l'interface plante
        
        # Démarrer l'appel
        self.__utilisateur.demarrer_appel(port_reception_voix_du_serveur)
        
    def raccrocher(self):   
        """Raccrocher l'appel.
        Si l'appel est en cours, demande au serveur de raccrocher.
        Si l'appel n'a pas été accepté, demande au serveur de refuser l'appel."""     
        # Si l'appel est en cours, demander au serveur de raccrocher
        if self.__appel_en_cours:
            print("Raccrochage de l'appel...")
            self.__label_etat_appel.configure(text="Demande de fin de l'appel...", bg="RosyBrown1")
            self.__utilisateur.raccrocher()
            
        # Si quelqu'un nous appelle mais que l'appel n'a pas été accepté, demander au serveur de refuser l'appel
        else:
            print("Refus de l'appel...")
            self.__label_etat_appel.configure(text="Refus de l'appel...", bg="RosyBrown1")
            self.play_audio_with_pyaudio("sonnerie/raccrocher.mp3")
            self.__utilisateur.rejeter_appel(self.__correspondant)
        
    def couper_micro(self):
        """Coupe/Active le micro du client (logique non implémentée).
        Constitue une piste de reflexion sur les nouvelles fonctionnalités possibles.
        """
        print("Micro coupé/activé (non implémenté) !")
        
    def activer_hp(self):
        """Active/Désactive le haut-parleur du client (logique non implémentée).
        Constitue une piste de reflexion sur les nouvelles fonctionnalités possibles.
        """
        print("Haut-parleur activé/désactivé (non implémenté) !")
        
    def play_audio_with_pyaudio(self, mp3_file:str):
        """Lit un fichier audio sur le client (sonnerie d'appel, sonnerie de raccrochage, ...).

        Args:
            mp3_file (str): chemin vers le fichier audio à lire
        """
        try:
            # Charger le fichier MP3 avec pydub
            audio = AudioSegment.from_mp3(mp3_file)

            # Initialiser PyAudio
            p = PyAudio()

            # Ouvrir un flux audio
            stream = p.open(format=p.get_format_from_width(audio.sample_width),
                            channels=audio.channels,
                            rate=audio.frame_rate,
                            output=True)

            # Lire les données audio en morceaux
            data = audio.raw_data
            stream.write(data)

            # Fermer le flux et PyAudio
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier audio (vérifiez l'installation de FFMPEG): {e}")
        
    def fermer_ihm_appel(self)-> None:
        """Fermer l'IHM d'appel.
        L'appel de cette fonction peut-être nécessaire pour fermer l'IHM d'appel depuis la classe Utilisateur.
        """
        self.after(1000, self.destroy) # fermer l'IHM d'appel

    def quit(self)-> None:
        """Gérer la fermeture forcée de l'IHM client : déconnexion de l'utilisateur, raccrocher, et fermeture de la fenêtre.
        """
        # Informer le serveur qu'on raccroche
        self.raccrocher()
        
        # Informer le serveur de notre déconnexion
        self.__utilisateur.deconnexion()
        
        # Forcer la fin de l'appel, même si le serveur n'a pas encore envoyé de "CALL END",
        # en précisant de ne pas rouvrir l'IHM des contacts
        sleep(0.5)
        self.__appel_en_cours = False
        self.__utilisateur.terminer_appel(ouvrir_ihm_contacts=False)
        
        # Fermer la fenêtre de l'IHM appel
        self.destroy()


class Utilisateur:
    # Déclaration des variables statiques pour la voix
    FORMAT:paInt16             # taille des echantillons # type: ignore car VSCode ne reconnait pas paInt16 comme type
    CHANNELS:int               # nombre de canaux (mono ou stereo)
    FREQUENCE:int              # fréquence d'échantillonnage (Hz)
    NB_ECHANTILLONS:int        # nombre d'échantillons du son simultanés
    
    # Instanciation des variables statiques pour la voix
    FORMAT = paInt16           # taille des echantillons
    CHANNELS = 1               # nombre de canaux : 1:(mono)
    FREQUENCE = 44100          # fréquence d'échantillonnage 
    NB_ECHANTILLONS = 1024     # nombre d'échantillons du son simultanés
    
    def __init__(self, login:str, mdp:str, ip_serv:str)-> None:
        """Constructeur de la classe Utilisateur.
        La classe Utilisateur est chargée de toutes les communications avec le serveur VoIP.

        Args:
            login (str): login de l'utilisateur
            mdp (str): mot de passe de l'utilisateur
            ip_serv (str): adresse ip du serveur VoIP
        """
        
        # Déclaration des attributs
        self.__login: str
        self.__mdp: str
        self.__ip_serv: str
        self.__stop_appel: bool
        self.__ihm_appel: IHM_Appel
        
        self.__flux_emission:PyAudio.Stream     # flux audio émis # type: ignore car VSCode ne reconnait pas Stream comme type
        self.__flux_reception:PyAudio.Stream    # flux audio reçu # type: ignore car VSCode ne reconnait pas Stream comme type
        self.__audio: PyAudio                   # connecteur audio
        
        # Déclaration des sockets
        self.__socket_envoi: socket             # socket d'envoi des messages et de la voix (UDP)
        self.__socket_reception_sig: socket     # socket de réception des messages de signalisation (UDP)
        self.__socket_reception_voix: socket    # socket de réception de la voix (UDP) 
        
        # Instanciation des attributs
        self.__login = login
        self.__mdp = mdp
        self.__ip_serv = ip_serv
        self.__stop_appel = False
        
        # Création du socket d'envoi des messages et de la voix (UDP)
        self.__socket_envoi = socket(AF_INET, SOCK_DGRAM)
        self.__socket_envoi.bind(("", 5000))
        
        # Création du socket de réception de messages (UDP)
        self.__socket_reception_sig = socket(AF_INET, SOCK_DGRAM)
        self.__socket_reception_sig.bind(("", 5101))
        
        # Création du socket de réception de la voix (UDP) :
        # Le (re-)création du socket de réception de la voix
        # est nécessaire pour chaque nouveau appel, donc elle se fait
        # dans la méthode demarrer_appel() de la classe Utilisateur
        
        # Tentative d'authentification auprès du serveur
        self.authentification()
    
    def authentification(self)-> None:
        """Tente d'authentifier l'utilisateur auprès du serveur VoIP.
        """
        reponse_serv: str
        
        # Définir le timeout de réception de la réponse serveur à quelques secondes
        self.set_timeout_socket_reception(4) 
        
        # Envoi de la requête d'authentification au serveur
        print("Tentative d'authentification de l'utilisateur auprès du serveur.")
        self.envoyer_message(f"AUTH REQUEST {self.__login}:{self.__mdp}")
        print("En attente de la réponse du serveur...")
        
        # Tentative de réception de la réponse serveur
        try:
            reponse_serv = self.recevoir_message()
            
        # Si le serveur ne répond pas dans les delais impartis :
        except timeout:
            # Fermer les sockets ouverts
            self.__socket_envoi.close()
            self.__socket_reception_sig.close()
            
            # Afficher un message d'erreur dans la console et relancer l'IHM d'authentification en affichant un message d'erreur
            print("Timed out : Vérifiez l'IP renseignée et si le serveur est bien lancé et accessible.")
            IHM_Authentification(msg_erreur="Timed out : Vérifiez l'IP renseignée et l'état du serveur.")
        
        # Si l'authentification est réussie :
        if reponse_serv.startswith("AUTH ACCEPT"):
            print("Authentification réussie.")
            IHM_Contacts(self)
            
        # Si l'authentification est refusée :
        elif reponse_serv.startswith("AUTH REJECT"):
            # Fermer les sockets ouverts
            self.__socket_envoi.close()
            self.__socket_reception_sig.close()
            
            # Afficher un message d'erreur dans la console et relancer l'IHM d'authentification en affichant un message d'erreur
            print("L'authentification a échouée :", reponse_serv)
            IHM_Authentification(msg_erreur="Login ou mot de passe incorrect.")
        
        # Si le serveur renvoie un message inattendu :
        else:
            # Fermer les sockets ouverts
            self.__socket_envoi.close()
            self.__socket_reception_sig.close()
            
            # Afficher un message d'erreur dans la console et relancer l'IHM d'authentification en affichant un message d'erreur
            print("Erreur inattendue :", reponse_serv)
            IHM_Authentification(msg_erreur="Erreur inattendue : veuillez réessayer.")
            
    def deconnexion(self)-> None:
        """Informe le serveur de la déconnexion de l'utilsiateur.
        """
        print("Information du serveur de notre déconnexion...")
        self.envoyer_message(f"LOGOUT {self.__login}")
    
    def envoyer_message(self, msg:str)-> None:
        """Envoie le message passé en paramètre au serveur.

        Args:
            msg (str): message à envoyer au serveur
        """
        tab_octets = msg.encode(encoding="utf-8")
        self.__socket_envoi.sendto(tab_octets, (self.__ip_serv, 6100))
        
    def recevoir_message(self)-> str:
        """Attends la réception d'un message de la part du serveur.

        Returns:
            str: message reçu du serveur
        """
        tab_octets = self.__socket_reception_sig.recv(255)
        msg = tab_octets.decode(encoding="utf-8")
        return msg
    
    def actualiser_liste_contacts(self)-> dict:
        """Solicite le serveur pour obtenir la liste des contacts et de leur statut mis à jour.
        Convertie la réponse JSON du serveur en dictionnaire Python exploitable par le client.

        Returns:
            dict: liste des contacts sous forme de dictionnaire Python
        """
        reponse_serv_contacts: str
        contacts_json: json
        dict_contacts: dict[str]
        reponse_serv_contacts = ""
        
        print("Tentative d'actualisation de la liste de contacts...")
        
        # Demander la liste des contacts au serveur
        self.envoyer_message(f"CONTACTS REQUEST")
        
        # Tentative de reception de la réponse du serveur
        try:
            reponse_serv_contacts = self.recevoir_message()
        except Exception as e:
            print(f"Erreur lors de la réception de la liste des contacts : {e}")
        
        # Si la liste des contacts a été récupérée :
        if reponse_serv_contacts.startswith("CONTACTS LIST"):
            
            # Récupérer les données JSON dans la réponse du serveur
            contacts_json = reponse_serv_contacts[14:] # suppression de l'entête "CONTACTS LIST " de 14 caractères
            
            # Désérialiser le JSON en dictionnaire
            dict_contacts = json.loads(contacts_json)

            print("La liste de contacts a été récupérée et extraite de la réponse du serveur.")
            
        # Si la liste des contacts n'a pas pu être récupérée, 
        # rappeler récursivement la méthode jusqu'à ce que la liste des contacts soit récupérée.
        # Cette solution est un peu "bourrine" (elle contourne juste le problème), mais elle est simple et efficace.
        else: 
            print("Erreur lors de la réception de la liste des contacts.")
            reponse_serv_contacts = self.actualiser_liste_contacts()
        
        return dict_contacts
    
    def envoyer_requete_appel(self, correspondant:str)-> tuple[bool, int]:
        """Envoyer une requête d'appel au serveur pour appeler le correspondant passé en paramètre.

        Args:
            correspondant (str): correspondant à appeler

        Returns:
            tuple[bool, int]: autorisation de démarrer l'appel (bool), port de réception de la voix du serveur (str)
        """
        reponse_serv_requete_demarrer_appel:str
        port_reception_voix_du_serveur:int
        autorisation_de_demarrer_appel:bool
        port_reception_voix_du_serveur = None
        autorisation_de_demarrer_appel = False
        
        print(f"Envoi de la requête d'appel pour {correspondant} au serveur...")
        self.envoyer_message(f"CALL REQUEST {correspondant}")
        # Le message envoyé est de la forme "CALL REQUEST login_correspondant"
        
        reponse_serv_requete_demarrer_appel = self.recevoir_message()
        
        # Si l'appel est accepté
        if reponse_serv_requete_demarrer_appel.startswith("CALL START"):
            print(f"Le serveur et {correspondant} ont accepté la requête d'appel.")
            
            # Autoriser le démarrage de l'appel
            autorisation_de_demarrer_appel = True
            
            # Récupérer le port de communication audio client vers serveur (différent selon le client) :
            port_reception_voix_du_serveur = int(reponse_serv_requete_demarrer_appel[11:])
            
        # Si l'appel est refusé
        elif reponse_serv_requete_demarrer_appel.startswith("CALL DENY"):
            print(f"Le serveur et {correspondant} ont refusé la requête d'appel.")
            # Autorisation_de_demarrer_appel reste à False et port_reception_voix_du_serveur à None.

        # Reception de message inattendu
        else:
            print(f"Erreur : le serveur a renvoyé une réponse inattendue : {reponse_serv_requete_demarrer_appel}")
            # Autorisation_de_demarrer_appel reste à False et port_reception_voix_du_serveur à None.
        
        return autorisation_de_demarrer_appel, port_reception_voix_du_serveur
    
    def decrocher(self, login_correspondant:str, login_utilisateur:str)-> int:
        """Décrocher l'appel avec le correspondant passé en paramètre.

        Args:
            login_correspondant (str): login du correspondant dont l'appel est accepté
            login_utilisateur (str): login de l'utilisateur qui accepte l'appel (le client)

        Returns:
            port_reception_voix_du_serveur (int): port du serveur vers lequel le serveur veut que le client envoie sa voix
        """
        reponse_serv_requete_demarrer_appel = str
        port_reception_voix_du_serveur: int
        
        # Envoi de l'acceptation de l'appel au serveur
        print(f"Envoi de l'acceptation de l'appel avec {login_correspondant} au serveur...")
        self.envoyer_message(f"CALL ACCEPT {login_correspondant}-{login_utilisateur}") 
        # Le message envoyé est de la forme "CALL ACCEPT login_appelant-login_appele_acceptant_l_appel"
        
        # Attendre le "CALL ACCEPT" du serveur
        reponse_serv_requete_demarrer_appel = self.recevoir_message() 
        
        # Si le serveur démarre l'appel, récupérer le port de communication audio client vers serveur (différent selon le client)
        if reponse_serv_requete_demarrer_appel.startswith("CALL START "):
            print(f"Le serveur a accepté le démarrage de l'appel avec {login_correspondant}.")
            # Récupérer le port de communication audio client vers serveur (différent selon le client) :
            port_reception_voix_du_serveur = int(reponse_serv_requete_demarrer_appel[11:])
        
        return port_reception_voix_du_serveur
    
    def rejeter_appel(self, correspondant:str)-> None:
        """Informe le serveur du refus de l'appel avec le correspondant passé en paramètre.

        Args:
            correspondant (str): login du correspondant avec qui l'appel est refusé
        """
        # Informer le serveur du refus de l'appel
        self.envoyer_message(f"CALL DENY {correspondant}")
        
        # Fermer l'IHM d'appel
        try:
            self.__ihm_appel.fermer_ihm_appel()
            
        except Exception as e:
            print(f"Erreur lors de la fermeture de l'IHM: {e}")
                    
        # Ouvrir une nouvelle fenêtre des contacts
        IHM_Contacts(self)
        
    def demarrer_appel(self, port_reception_voix_du_serveur:int)-> None:
        """Démarrer un appel

        Args:
            port_reception_voix_du_serveur (int): port du serveur vers lequel le serveur veut que le client envoie sa voix
        """
        data:bytes # paquets audio
        msg:str # message reçu
        bin: str # poubelle
        
        print(f"Le serveur a accepté le démarrage de l'appel et demande de recevoir les paquets audio sur le port {port_reception_voix_du_serveur}.")
        
        # Réinitialisation de l'attribut stop_appel
        self.__stop_appel = False
        
        # (Re-)création du socket de réception de la voix (UDP)
        self.__socket_reception_voix = socket(AF_INET, SOCK_DGRAM)
        self.__socket_reception_voix.bind(("", 5001))
        
        # Définir un timeout de 5s pour le socket de réception de la voix (pour ne pas que le programme reste bloqué)
        self.__socket_reception_voix.settimeout(5)
        
        # Définir un timeout de 1ms pour le socket de réception de la signalisation (pour ne pas que le programme reste bloqué)
        # Evolution possible : gérer la reception de la signalisation dans un thread séparé
        self.set_timeout_socket_reception(0.001)
        
        # Initialisation des attributs audio
        self.__audio = PyAudio()   # initialisation port audio
        self.__flux_emission = self.__audio.open(format = Utilisateur.FORMAT, channels = Utilisateur.CHANNELS,
                                                 rate= Utilisateur.FREQUENCE, input=True,
                                                 frames_per_buffer = Utilisateur.NB_ECHANTILLONS)
        self.__flux_reception = self.__audio.open(format = Utilisateur.FORMAT, channels = Utilisateur.CHANNELS,
                                                 rate= Utilisateur.FREQUENCE, output=True,
                                                 frames_per_buffer = Utilisateur.NB_ECHANTILLONS)
        
        print("L'appel est en cours...")
        
        while not self.__stop_appel:
            # enregistrement et émission
            data = self.__flux_emission.read(Utilisateur.NB_ECHANTILLONS)
            self.__socket_envoi.sendto(data, (self.__ip_serv, port_reception_voix_du_serveur))
            
            # Réception et lecture de la voix
            try:
                data, bin = self.__socket_reception_voix.recvfrom(2*Utilisateur.NB_ECHANTILLONS)
                data = self.__flux_reception.write(data)

            except timeout:
                print("[INFO] Paquet audio manquant.")
            
            # Reception d'un potentiel message "CALL END" du serveur
            try:
                msg = self.recevoir_message()
                if msg == "CALL END":
                    print("CALL END reçu de la part du serveur.")
                    self.terminer_appel(ouvrir_ihm_contacts=True)
            
            except timeout:
                # Pas de CALL END reçu, l'appel continue
                pass
            
    def raccrocher(self)-> None:
        """Raccrocher : envoyer une requête de fin d'appel ""CALL END REQUEST" au serveur.
        """
        self.envoyer_message("CALL END REQUEST")
            
    def terminer_appel(self, ouvrir_ihm_contacts:bool)-> None:  
        """Terminer l'appel à la demande du serveur
        (fermer les flux audio, et le socket de réception de la voix, etc.)"""    
        print("Le serveur informe tous les correspondants de la fin de l'appel.")
            
        # Arrêter la boucle de l'appel
        self.__stop_appel = True
        
        # Tenter de fermer les flux audio
        try:
            self.__audio.close(self.__flux_emission)
            self.__audio.close(self.__flux_reception)
        except Exception as e:
            print(f"Information : Les flux audios n'ont pas pu être fermés car ils n'existent pas : {e}")
        
        # Fermer le socket de reception de la voix s'il existe
        try:
            self.__socket_reception_voix.close()
        except Exception as e:
            print(f"Information : Le socket de réception de la voix n'a pas pu être fermé car il n'existe pas : {e}")
            
        # Définir un timeout un peu plus long pour le socket de réception de la signalisation
        self.set_timeout_socket_reception(1)
        
        # Jouer le son de fin d'appel
        self.__ihm_appel.play_audio_with_pyaudio("sonnerie/raccrocher.mp3")
                
        # Fermer l'IHM d'appel
        try:
            self.__ihm_appel.fermer_ihm_appel()
            
        except Exception as e:
            print(f"Erreur lors de la fermeture de l'IHM: {e}")
                    
        # Ouvrir une nouvelle fenêtre des contacts si demandé
        if ouvrir_ihm_contacts:
            IHM_Contacts(self)
        
    def get_login(self)-> str:
        """Retourne le login de l'utilisateur.

        Returns:
            str: login de l'utilisateur
        """
        return self.__login
    
    def set_timeout_socket_reception(self, timeout:float=60)-> None:
        """Modifie le timeout du socket de réception de la signalisation.

        Args:
            timeout (float, optional): timeout en secondes. Defaults to 60.
        """
        self.__socket_reception_sig.settimeout(timeout)
        
    def set_attribut_ihm_appel(self, ihm_appel:IHM_Appel)-> None:
        """Permet de définir l'attribut ihm_appel de la classe Utilisateur.
        Cela est nécesssaire pour que la classe Utilisateur puisse fermer la fenêtre d'appel,
        sans nécessiter de passer par plusieurs appels de méthodes externes.

        Args:
            ihm_appel (IHM_Appel): objet de la classe IHM_Appel
        """
        self.__ihm_appel = ihm_appel


if __name__ == "__main__":
    LARGEUR_FEN:int = 375
    HAUTEUR_FEN:int = 700
    
    IHM_Authentification()