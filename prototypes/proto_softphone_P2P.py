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
    CHANNELS = 1
    FREQUENCE = 44100
    NB_ECHANTILLONS = 1024
    PORT_SORTIE = 5000
    PORT_ENTREE = 5001
    
    def __init__(self, ip_correspondant:str):
        # Déclaration des attributs réseau
        self.__adr_correspondant:tuple[str, int]
        self.__ip_correspondant: str # inutile
        self.__socket_emetteur:socket
        self.__socket_recepteur:socket
        
        # Declaration des attributs audio
        self.__flux_emission:PyAudio.Stream      # flux audio émis
        self.__flux_reception:PyAudio.Stream     # flux audio reçu
        self.__audio: PyAudio                    # connecteur audio
        self.__data:bytes                        # liste des enregistrements simultanés
        
        # initialisation des attributs réseau du correspondant
        self.__adr_correspondant = (ip_correspondant, Softphone.PORT_ENTREE)
        
        # initialisation des attributs réseau locaux
        self.__socket_emetteur = socket(AF_INET, SOCK_DGRAM)
        self.__socket_emetteur.bind(("", Softphone.PORT_SORTIE))
        
        self.__socket_recepteur = socket(AF_INET, SOCK_DGRAM)
        self.__socket_recepteur.bind(("", Softphone.PORT_ENTREE))
        
        print(f"Le serveur UDP a démarré.\nPort d'émission : {Softphone.PORT_SORTIE}\nPort de réception : {Softphone.PORT_ENTREE}")
        
        # initialisation des attributs audio
        self.__audio = PyAudio()   # Initialisation port audio
        self.__flux_emission = self.__audio.open(format = Softphone.FORMAT, channels = Softphone.CHANNELS,
                                                 rate= Softphone.FREQUENCE, input=True,
                                                 frames_per_buffer = Softphone.NB_ECHANTILLONS)
        self.__flux_reception = self.__audio.open(format = Softphone.FORMAT, channels = Softphone.CHANNELS,
                                                 rate= Softphone.FREQUENCE, output=True,
                                                 frames_per_buffer = Softphone.NB_ECHANTILLONS)
        
        # Lancement de l'enregistrement de la voix
        print ("Lancement de l'enregistrement de votre voix...")
        
        try:
            while True:
                # enregistrement et émission
                data = self.__flux_emission.read(Softphone.NB_ECHANTILLONS)
                self.__socket_emetteur.sendto(data, self.__adr_correspondant)
                
                # réception et lecture
                data, self.__ip_correspondant = self.__socket_recepteur.recvfrom(2*Softphone.NB_ECHANTILLONS) 
                data = self.__flux_reception.write(data)
                
        except KeyboardInterrupt:
            pass
        
        finally: # fermeture de la communication
            self.__audio.close(self.__flux_emission)
            self.__audio.close(self.__flux_reception)
            self.__socket_recepteur.close()
            # self.__flux_emission.stop_stream()
            # self.__flux_emission.close()
            print ("Fin de la communication.")


if __name__ == "__main__":
    ### RENSEIGNER L'IP DU CORRESPONDANT ICI ###
    ip_correspondant = "192.168.11.134"     ### <-----
    ### RENSEIGNER L'IP DU CORRESPONDANT ICI ###
    
    softphone:Softphone = Softphone(ip_correspondant) 