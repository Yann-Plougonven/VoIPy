# Client VoIP
# Écrit par Tugdual Thepaut et Yann Plougonven--Lastennet
# Projet de S3 de BUT R&T à l'IUT de Lannion - Décembre 2024 / Janvier 2025
# Dépôt GitHub : https://github.com/Yann-Plougonven/VoIPy

from pyaudio import *
from socket import *
from tkinter import *

class IHM_Connexion(Tk):
    def __init__(self, client)-> None:
        Tk.__init__(self)
        
        # déclaration des attributs
        self.__client: Client
        
        self.__frame_auth: Frame
        self.__entry_login: Entry
        self.__label_login: Label
        self.__entry_mdp: Entry
        self.__label_mdp: Label
        
        self.__frame_serv: Frame
        self.__entry_ip_serv: Entry
        self.__label_ip_serv: Label
        self.__btn_connexion: Button
        
        # instanciation des attributs
        self.__client = client # récupération de l'objet client
        self.title("Connexion au serveur")
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
        
        # Frame de connexion au serveur
        self.__frame_serv = Frame(self, borderwidth=10, relief="groove", padx=10, pady=10)
        self.__entry_ip_serv = Entry(self.__frame_serv, width=50)
        self.__label_ip_serv = Label(self.__frame_serv, text="IP du serveur VoIP")
        
        print(self.__entry_login.get())
        
        # J'ai fait nimp, on ne peut pas faire d'authentification comme en TCP, juste prévenir le serv qu'on a cette IP  
        self.__btn_connexion = Button(self.__frame_serv, text="Connexion",
                                      command=self.__client.connexion(self.__entry_login.get(), 
                                                                      self.__entry_mdp.get(), 
                                                                      self.__entry_ip_serv.get()))
        
        # Ajout des widgets
        self.__frame_auth.pack(pady=20)
        self.__label_login.grid(row=0, column=0, pady=5)
        self.__entry_login.grid(row=1, column=0, pady=5)
        self.__label_mdp.grid(row=2, column=0, pady=5)
        self.__entry_mdp.grid(row=3, column=0, pady=5)
        
        self.__frame_serv.pack(pady=20)
        self.__label_ip_serv.grid(row=0, column=0, pady=5)
        self.__entry_ip_serv.grid(row=1, column=0, pady=5)
        self.__btn_connexion.grid(row=2, column=0, pady=20)
        
        # lancer l'IHM
        self.mainloop()
        

class IHM_Contacts(Toplevel):
    def __init__(self, ihm_connexion: IHM_Connexion)-> None:
        Toplevel.__init__(self)
        self.ihm_connexion: IHM_Connexion


class IHM_Appel(Toplevel):
    def __init__(self)-> None:
        Toplevel.__init__(self)
        self.ihm_contacts: IHM_Appel


class Client:
    def __init__(self)-> None:
        # J'ai fait nimp, on ne peut pas faire d'authentification comme en TCP, juste prévenir le serv qu'on a cette IP  
        self.__ihm_connexion: IHM_Connexion
        self.__ihm_connexion = IHM_Connexion(self)
    
    def connexion(login:str, mdp:str, ip_serv:str):
        pass



if __name__ == "__main__":
    LARGEUR_FEN:int = 375
    HAUTEUR_FEN:int = 700
    
    client: Client
    client = Client()