# Client VoIP
# Écrit par Tugdual Thepaut et Yann Plougonven--Lastennet
# Projet de S3 de BUT R&T à l'IUT de Lannion - Décembre 2024 / Janvier 2025
# Dépôt GitHub : https://github.com/Yann-Plougonven/VoIPy

from pyaudio import *
from socket import *
from tkinter import *

class IMH_Connexion(Tk):
    def __init__(self)-> None:
        Tk.__init__(self)
        
        # déclaration des attributs
        
        
        # instanciation des attributs
        
        

class IHM_Contacts(Toplevel):
    def __init__(self)-> None:
        Toplevel.__init__(self)
        self.ihm_connexion: IMH_Connexion

class IHM_Appel(Toplevel):
    def __init__(self)-> None:
        Toplevel.__init__(self)
        self.ihm_contacts: IHM_Appel
        
