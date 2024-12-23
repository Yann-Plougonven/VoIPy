# Client VoIP
# Écrit par Tugdual Thepaut et Yann Plougonven--Lastennet
# Projet de S3 de BUT R&T à l'IUT de Lannion - Décembre 2024 / Janvier 2025
# Dépôt GitHub : https://github.com/Yann-Plougonven/VoIPy

from pyaudio import *
from socket import *
from tkinter import *

class IHM_Authentification(Tk):
    # Utilisation du protocole UDP : on n'établit pas de connexion avec le serveur,
    # le client lui indique simplement sa présence en s'authentifiant
    def __init__(self)-> None:
        Tk.__init__(self)
        
        # déclaration des attributs
        self.__ip_client: str
        
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
        self.__label_ip_client = Label(self.__frame_serv, text=f"Votre IP client : {gethostbyname(gethostname())}")
        self.__entry_ip_serv = Entry(self.__frame_serv, width=50)
        self.__entry_ip_serv.insert(0, "192.168.1.159") # valeur par défaut
        self.__label_ip_serv = Label(self.__frame_serv, text="IP du serveur VoIP")
        self.__btn_auth = Button(self.__frame_serv, text="Authentification", command=self.authentification)
        
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
        
        # lancer l'IHM
        self.mainloop()
        
    def authentification(self)-> None:
        self.__client = Client(self.__entry_login.get(), self.__entry_mdp.get(), self.__entry_ip_serv.get()) 


class IHM_Contacts(Toplevel):
    def __init__(self, ihm_authentification: IHM_Authentification)-> None:
        Toplevel.__init__(self)
        self.ihm_connexion: IHM_Authentification


class IHM_Appel(Toplevel):
    def __init__(self)-> None:
        Toplevel.__init__(self)
        self.ihm_contacts: IHM_Appel


class Client:
    def __init__(self, login:str, mdp:str, ip_serv:str)-> None:
        
        # Déclaration des attributs       
        self.__login: str
        self.__mdp: str
        self.__ip_serv: str
        
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
        
        print("Tentative d'authentification du client auprès du serveur.")
        self.envoyer_message(f"AUTH REQUEST {self.__login}:{self.__mdp}")
        
        print("En attente de la réponse du serveur...")
        reponse_serv = self.recevoir_message()
        
        if reponse_serv.startswith("AUTH ACCEPT"):
            print("Authentification réussie.")
            # TODO ouvrir l'interface suivante
            
        else:
            print("L'authentification a échouée : ", reponse_serv)
    
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