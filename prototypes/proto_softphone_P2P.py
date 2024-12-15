# Prototype d'un softphone Peer to Peer émetteur/récepteur sans IHM
# Écrit par Tugdual Thepaut et Yann Plougonven--Lastennet
# Projet de S3 de BUT R&T à l'IUT de Lannion - Décembre 2024
# https://github.com/Yann-Plougonven/VoIPy pour la version finale "client/serveur"

from pyaudio import *
from socket import *

class Softphone():
    # Déclaration des variables statiques
    FORMAT:paInt16             # taille des echantillons
    CHANNELS:int               # 1:mono 2:stereo
    FREQUENCE:int              # fréquence d'échantillonnage 
    NB_ECHANTILLONS:int        # nombre d'échantillons simultanes
    PORT_SORTIE:int            # port de sortie
    PORT_ENTREE:int            # port d'entrée
    
    # Initialisation des variables statiques
    FORMAT = paInt16
    CHANNELS = 2
    FREQUENCE = 16000
    NB_ECHANTILLONS = 1024
    PORT_SORTIE = 5000
    PORT_ENTREE = 5001
    
    def __init__(self, ip_correspondant:str):
        # Déclaration des attributs
        self.__socket_correspondant:tuple[str, int]
        self.__socket_emetteur:socket
        self.__fin: bool = False
        
        # Declaration des attributs audio
        self.__audio: PyAudio                    # connecteur audio
        self.__stream_entree:PyAudio.Stream      # flux audio
        self.__data:bytes                        # liste des enregistrements simultanés
        
        # initialisation des attributs réseau du correspondant
        self.__socket_correspondant = (ip_correspondant, Softphone.PORT_ENTREE)
        
        # initialisation des attributs réseau locaux
        self.__socket_emetteur = socket(AF_INET, SOCK_DGRAM)
        self.__socket_emetteur.bind(("", Softphone.PORT_SORTIE))
        print(f"Le serveur UDP a démarré sur le port {Softphone.PORT_SORTIE}.")
        
        # initialisation des attributs audio
        self.__audio = PyAudio()   # Initialisation port audio
        self.__stream_entree = self.__audio.open(format = Softphone.FORMAT, channels = Softphone.CHANNELS,
                                                 rate= Softphone.FREQUENCE, input=True,
                                                 frames_per_buffer = Softphone.NB_ECHANTILLONS)
        
        # Lancement de l'enregistrement de la voix
        print ("Lancement de l'enregistrement de votre voix...")
        
        try:
            while not self.__fin:
                data = self.__stream_entree.read(2*Softphone.NB_ECHANTILLONS) # lecture des echantillons simultanes
                self.__socket_emetteur.sendto(data, self.__socket_correspondant)
                
        except KeyboardInterrupt:
            pass
        
        finally: # fermeture de la communication
            self.__audio.close(self.__stream_entree)
            self.__socket_emetteur.close()
            # self.__stream_entree.stop_stream()
            # self.__stream_entree.close()
            print ("Fin de la communication.")


if __name__ == "__main__":
    softphone:Softphone = Softphone("127.0.0.2")