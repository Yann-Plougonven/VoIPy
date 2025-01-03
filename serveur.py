# Serveur VoIP
# Écrit par Tugdual Thepaut et Yann Plougonven--Lastennet
# Projet de S3 de BUT R&T à l'IUT de Lannion - Décembre 2024 / Janvier 2025
# Dépôt GitHub : https://github.com/Yann-Plougonven/VoIPy

from pyaudio import *
from socket import *
import sqlite3
from datetime import datetime
import os.path

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
            
        if msg.startswith("LOGOUT REQUEST"):
            self.deconnecter(ip_client, msg)
            
        if msg.startswith("CONTACTS REQUEST"):
            self.envoyer_liste_contacts(ip_client)
        
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
        port_client: int
        port_client = 5101
        
        tab_octets = msg.encode(encoding="utf-8")
        self.__socket_emission.sendto(tab_octets, (ip_client, port_client))
        print(f"[{self.heure()}] [TO {ip_client}:{port_client}] {msg}")
        
    def heure(self)-> str:
        return datetime.now().strftime("%m/%d/%y %H:%M:%S")
    
    def requete_BDD(self, requete:str)-> str:
        connecteur:sqlite3.Connection
        curseur:sqlite3.Cursor
        nom_bdd: str
        chemin_bdd: str
        reponse_bdd: str
        reponse_bdd = None
        
        nom_bdd = "utilisateurs.sqlite3"
        
        # Définition du chemin absolu de la base de données (nécessaire sinon elle ne s'ouvre pas)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        chemin_bdd = os.path.join(BASE_DIR, nom_bdd)
        
        # Connexion à la BDD
        print(f"[{self.heure()}] [INFO] [SQL] {requete}")
        connecteur = sqlite3.connect(chemin_bdd)
        curseur = connecteur.cursor()
        
        # Execution de la requete
        try:
            curseur.execute(requete)
            reponse_bdd = curseur.fetchall()
        
        except Exception as e:
            print(f"[{self.heure()}] [ERREUR] [SQL] {e}")
        
        connecteur.commit()
        connecteur.close()
        
        return reponse_bdd
        
                
    def authentifier(self, ip_client:str, msg: str)-> None:
        login: str
        mdp: str
        requete_bdd: str
        reponse_bdd: str
        
        msg = msg[13:] # suppression de l'entête "AUTH REQUEST" (13 caractères) du messag reçu
        login, mdp = msg.split(":") # séparation du login et du mot de passe

        # Interrogation de la BDD et enregistrement de la réponse
        requete_bdd = f"SELECT * FROM utilisateurs WHERE login = '{login}' AND password = '{mdp}';"
        reponse_bdd = self.requete_BDD(requete_bdd)
        
        if reponse_bdd: # TODO consulter la BDD pour vérifier que l'utilisateur est bien enregistré
            
            print(f"[{self.heure()}] [INFO] Authentification réussie pour {ip_client}.") # TODO pseudo de l'utilisateur
            self.envoyer_signalisation(ip_client, "AUTH ACCEPT")
            # TODO mettre à jour la BDD avec l'adresse IP du client
            # Ajouter le client à la liste des clients actuellement authentifiés
        
        else: # utilisateur inexistant
            self.envoyer_signalisation(ip_client, "AUTH REJECT")
            
    def deconnecter(self, ip_client:str, msg: str)-> None:
        # TODO vérifier que l'utilisateur est bien authentifié sur cette Ip
        # TODO déconnecter le client (mise la jour de la liste des clients actuellement authentifiés)
        pass
    
    def envoyer_liste_contacts(self, ip_client:str)-> None:
        # TODO vérifier que l'utilisateur est bien authentifié
        self.envoyer_signalisation(ip_client, "CONTACTS LIST {'John Doe':'online', 'Alice':'online', 'Bob':'offline', 'Eve':'offline'}")  
            
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