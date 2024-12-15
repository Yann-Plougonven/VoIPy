# Prototype softphone Peer to Peer
# Programme sans IHM assurant la transmission et la réception de la communication

from pyaudio import *
from socket import *
from threading import Thread

class Softphone():
    # Déclaration des variables statiques
    FORMAT:paInt16             # taille des echantillons
    CHANNELS:int               # 1:mono 2:stereo
    FREQUENCE:int              # fréquence d'échantillonnage 
    NB_ECHANTILLONS:int        # nombre d'échantillons simultanes
    PORT_SORTIE:int
    PORT_ENTREE:int
    
    # Initialisation des variables statiques
    FORMAT = paInt16
    CHANNELS = 2
    FREQUENCE = 16000
    NB_ECHANTILLONS = 1024
    PORT_SORTIE = 5000
    PORT_ENTREE = 5001
    
    def __init__(self, ip_correspondant:str):
        
        # Déclaration des attributs
        self.__ip_correspondant = ip_correspondant
        self.__fin: bool = False
        self.__socket_emetteur:socket
        
        # Declaration des attributs audio
        self.__audio: PyAudio             # connecteur audio
        self.__stream_entree:PyAudio.Stream      # flux audio
        self.__data:bytes     # liste des enregistrements simultanes
        
        # initialisation des attributs réseau
        self.__socket_emetteur = socket(AF_INET, SOCK_DGRAM)
        self.__socket_emetteur.bind(("", Softphone.PORT_SORTIE))
        self.__adr_recepteur = ("192.168.28.87", Softphone.PORT_ENTREE)
        print("Le serveur UDP a démarré sur le port", Softphone.PORT_SORTIE)
        
        # initialisation des attributs audio
        self.__audio = PyAudio()   # Initialisation port audio
        self.__stream_entree = self.__audio.open(format = Softphone.FORMAT, channels = Softphone.CHANNELS,
                                                 rate= Softphone.FREQUENCE, input=True,
                                                 frames_per_buffer = Softphone.NB_ECHANTILLONS)