# Client VoIP
# Écrit par Tugdual Thepaut et Yann Plougonven--Lastennet
# Projet de S3 de BUT R&T à l'IUT de Lannion - Décembre 2024 / Janvier 2025
# Dépôt GitHub : https://github.com/Yann-Plougonven/VoIPy

from pyaudio import *
from socket import *
from tkinter import *

class IHM_Connexion(Tk):
    def __init__(self)-> None:
        Tk.__init__(self)
        
        # déclaration des attributs
        self.__id: str
        self.__mdp: str
        self.__ip_serv: str
        
        self.__frame_auth: Frame
        self.__entry_id: Entry
        self.__label_id: Label
        self.__entry_mdp: Entry
        self.__label_mdp: Label
        
        self.__frame_serv: Frame
        self.__entry_ip_serv: Entry
        self.__label_ip_serv: Label
        self.__btn_connexion: Button
        
        # instanciation des attributs
        self.title("Connexion au serveur")
        self.geometry(f"{LARGEUR_FEN}x{HAUTEUR_FEN}")
        
        self.__frame_auth = Frame(borderwidth= 10, relief= "groove", padx = 10, pady = 10)
        self.__entry_id = Entry(self.__frame_auth, width=50)
        self.__label_id = Label(self.__frame_auth, text="Identifiant")
        self.__entry_mdp = Entry(self.__frame_auth, width=50)
        self.__label_mdp = Label(self.__frame_auth, text="Mot de passe")
        
        self.__frame_serv = Frame(borderwidth= 10, relief= "groove", padx = 10, pady = 10)
        self.__entry_ip_serv = Entry(self.__frame_serv, width=50)
        self.__label_ip_serv = Label(self.__frame_serv, text="IP du serveur VoIP")
        self.__btn_connexion = Button(self.__frame_serv, text="Connexion")
        
        # ajout des widgets
        self.__frame_auth.pack(side=TOP)
        self.__entry_id.grid(row=1)
        self.__label_id.grid(row=0)
        self.__entry_mdp.grid(row=3)
        self.__label_mdp.grid(row=2)
        
        self.__frame_serv.pack(side=BOTTOM)
        self.__entry_ip_serv.grid(row=1)
        self.__label_ip_serv.grid(row=0)
        self.__btn_connexion.grid(row=2)
        
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
        
if __name__ == "__main__":
    LARGEUR_FEN:int = 375
    HAUTEUR_FEN:int = 700
    
    ihm: IHM_Connexion
    ihm = IHM_Connexion()