# Serveur VoIP
# Écrit par Tugdual Thepaut et Yann Plougonven--Lastennet
# Projet de S3 de BUT R&T à l'IUT de Lannion - Décembre 2024 / Janvier 2025
# Dépôt GitHub : https://github.com/Yann-Plougonven/VoIPy

from pyaudio import *
from socket import *
from datetime import datetime

class Service_Signalisation:
    def __init__(self) -> None:
        # déclaration des sockets
        self.__socket_ecoute: socket
        self.__socket_emission: socket
        
        # initialisation du socket écoute du flux de signalisation (port 6100)
        self.__socket_ecoute = socket(family=AF_INET, type=SOCK_DGRAM)
        self.__socket_ecoute.bind(("", 6100))
        
        # initialisation du socket d'émission du flux de signalisation (port 6000)
        self.__socket_emission = socket(family=AF_INET, type=SOCK_DGRAM)
        self.__socket_emission.bind(("", 6000))
        
        self.ecouter_signalisation()

   
    def ecouter_signalisation(self) -> None:
        tab_octets: bytearray
        msg: str
        addr: set
        ip_client: str
        port_client: int
        
        while True:
            # Suppression du message précédent
            msg = "" 
            
            # Réception du message
            tab_octets, addr = self.__socket_ecoute.recvfrom(255)
            msg = tab_octets.decode(encoding="utf-8")
            
            # Enregistrement des coordonnées du client
            ip_client, port_client = addr
            print(f"[{self.heure()}] [FROM {ip_client}:{port_client}] {msg}")
            
            # Traitement du message
            self.traiter_signalisation(ip_client, msg)

      
    def traiter_signalisation(self, ip_client:str, msg: str)-> None:
        # Traitement du message
        if msg.startswith("AUTH REQUEST"):
            self.authentifier(ip_client, msg)
            
        if msg.startswith("DISCONNECTION REQUEST"):
            self.deconnecter(ip_client, msg)
        
        elif msg.startswith("CALL REQUEST"):
            self.appeler(ip_client, msg)
            
        elif msg.startswith("CALL ACCEPT"):
            self.lancer_appel(ip_client, msg)
            
        elif msg.startswith("CALL REJECT"):
            self.rejeter_appel(ip_client, msg)
        
        elif msg.startswith("CALL END REQUEST"):
            self.terminer_appel(ip_client, msg)

            
    def envoyer_signalisation(self, ip_client:str, msg: str)-> None:
        tab_octets: bytearray
        
        tab_octets = msg.encode(encoding="utf-8")
        self.__socket_emission.sendto(tab_octets, (ip_client, 5000)) # remplacer par 5101
        
    def heure(self)-> str:
        return datetime.now().strftime("%m/%d/%y %H:%M:%S")
                
    def authentifier(self, ip_client:str, msg: str)-> None:
        
        if True: # TODO consulter la BDD pour vérifier que l'utilisateur est bien enregistré
            print(f"[{self.heure()}] [Serveur] Authentification réussie pour {ip_client}.") # TODO pseudo de l'utilisateur
            self.envoyer_signalisation(ip_client, "AUTH ACCEPT")
            # TODO mettre à jour la BDD avec l'adresse IP du client
            # Ajouter le client à la liste des clients actuellement authentifiés
        
        else: # utilisateur inexistant
            self.envoyer_signalisation(ip_client, "AUTH REJECT")
            
    def deconnecter(self, ip_client:str, msg: str)-> None:
        # TODO vérifier que l'utilisateur est bien authentifié sur cette Ip
        # TODO déconnecter le client (mise la jour de la liste des clients actuellement authentifiés)
        pass        
            
    def appeler(self, ip_client:str, msg: str)-> None:
        # TODO vérifier que l'utilisateur est bien authentifié
        pass
    
    
    def lancer_appel(self, ip_client:str, msg: str)-> None:
        # TODO vérifier que l'utilisateur est bien authentifié
        pass
    
    
    def rejeter_appel(self, ip_client:str, msg: str)-> None:
        # TODO vérifier que l'utilisateur est bien authentifié ?
        pass
    
    
    def terminer_appel(self, ip_client:str, msg: str)-> None:
        # TODO vérifier que l'utilisateur est bien authentifié
        pass
                
    
if __name__ == "__main__":
    service_signalisation: Service_Signalisation
    service_signalisation = Service_Signalisation()