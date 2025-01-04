# Serveur VoIP
# Écrit par Tugdual Thepaut et Yann Plougonven--Lastennet
# Projet de S3 de BUT R&T à l'IUT de Lannion - Décembre 2024 / Janvier 2025
# Dépôt GitHub : https://github.com/Yann-Plougonven/VoIPy

from pyaudio import *
from socket import *
import sqlite3
from datetime import datetime
from time import sleep # TODO à supprimer si plus utilisé
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
            
        if msg.startswith("LOGOUT"):
            self.deconnecter(ip_client, msg)
            
        if msg.startswith("CONTACTS REQUEST"):
            self.envoyer_liste_contacts(ip_client)
        
        elif msg.startswith("CALL REQUEST"):
            self.requete_appel(ip_client, msg)
            
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
        # TODO remplacer cette fonction par une autre qui prend en paramètre le msg à log,
        # lui ajoute l'heure au début, enregistre le tout dans un fichier de log et affiche le tout dans la console
        return datetime.now().strftime("%d/%m/%y %H:%M:%S")
    
    def requete_BDD(self, requete:str)-> str:
        connecteur:sqlite3.Connection
        curseur:sqlite3.Cursor
        dossier_de_travail: str
        nom_bdd: str
        chemin_bdd: str
        reponse_bdd: str
        reponse_bdd = None
        
        nom_bdd = "utilisateurs.sqlite3"
        
        # Définition du chemin absolu de la base de données (nécessaire, sinon elle ne s'ouvre pas)
        dossier_de_travail = os.path.dirname(os.path.abspath(__file__))
        chemin_bdd = os.path.join(dossier_de_travail, "bdd", nom_bdd)
                
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
        
        msg = msg[13:] # suppression de l'entête "AUTH REQUEST" (13 caractères) du message reçu
        login, mdp = msg.split(":") # séparation du login et du mot de passe reçus

        # Interrogation de la BDD et enregistrement de la réponse
        requete_bdd = f"SELECT * FROM utilisateurs WHERE login = '{login}' AND password = '{mdp}';"
        reponse_bdd = self.requete_BDD(requete_bdd)
        
        # Si le couple login:mdp existe dans la BDD (authentification réussie) :
        if reponse_bdd:
            print(f"[{self.heure()}] [INFO] Authentification réussie pour {login} sur le poste {ip_client}.")
            
            # Mettre à jour l'IP du client et son statut (online) dans la BDD
            requete_bdd = f"UPDATE utilisateurs SET ip = '{ip_client}', online = 1 WHERE login = '{login}';"
            self.requete_BDD(requete_bdd)
            
            # Informer le client qu'il est authentifié
            self.envoyer_signalisation(ip_client, "AUTH ACCEPT")
            
        # Si le couple login:mdp n'existe pas dans la BDD (authentification refusée) :
        else:
            print(f"[{self.heure()}] [INFO] Authentification REFUSÉE pour {login} sur le poste {ip_client}.")
            self.envoyer_signalisation(ip_client, "AUTH REJECT")
    
    def is_ip_authentifiée(self, ip_client:str)-> bool:
        """Retourne True si un utilisateur est authentifié sur l'IP du client solicitant le serveur, False sinon.
        (Il ne s'agit évidement pas d'une méthode d'authentification très sécurisée, mais d'une simple vérification de l'IP
        pour limiter les risques d'usurpation d'identité. Il faudrait ajouter d'autres méthodes de sécurisation)
        
        Args:
            ip_client (str): Adresse IP du client solicitant le serveur.

        Returns:
            bool: True si un utilisateur est authentifié sur l'IP du client solicitant le serveur, False sinon.
        """ 
        requete_bdd: str
        reponse_bdd: str
        is_authentifiee: bool
        is_authentifiee = False
        
        # Demander à la BDD si un utilisateur est authentifié sur l'IP du client solicitant le serveur
        requete_bdd = f"SELECT * FROM utilisateurs WHERE ip = '{ip_client}' AND online = 1;"
        reponse_bdd = self.requete_BDD(requete_bdd)
        
        if reponse_bdd: # Si la réponse n'est pas vide, l'IP de l'utilisateur est authentifié
            is_authentifiee = True
            
        return is_authentifiee
            
    def deconnecter(self, ip_client:str, msg: str)-> None:
        login: str
        requete_bdd: str
        
        # Récupération du login de l'utilisateur à déconnecter
        login = msg[7:] # suppression de l'entête "LOGOUT" (7 caractères) du message reçu
        
        # Demander au serveur de déconnecter l'utilisateur
        requete_bdd = f"UPDATE utilisateurs SET online = 0 WHERE login = '{login}' AND ip = '{ip_client}';"
        self.requete_BDD(requete_bdd)
    
    def envoyer_liste_contacts(self, ip_client:str)-> None:
        requete_bdd: str
        reponse_bdd: str
        dict_contacts: dict
        
        if self.is_ip_authentifiée(ip_client):
            
            # Récupération de la liste des contacts et de leur statut dans la BDD
            requete_bdd = f"SELECT login, online FROM utilisateurs;"
            reponse_bdd = self.requete_BDD(requete_bdd)
                        
            # Conversion de la réponse en un dictionnaire
            dict_contacts = {login: "online" if online else "offline" for login, online in reponse_bdd}
                        
            self.envoyer_signalisation(ip_client, f"CONTACTS LIST {dict_contacts}")  
            
    def requete_appel(self, ip_appelant:str, msg: str)-> None:
        requete: str
        login_appelant: str
        login_appele: str
        ip_appele: str
        
        # Récupération du login de l'utilisateur appelant et vérifier si l'IP de l'appellant est authentifié
        requete = f"SELECT login FROM utilisateurs WHERE ip = '{ip_appelant}' AND online = 1;"
        login_appelant = self.requete_BDD(requete)[0][0] # (TODO simplfier ?) Récupération du login de l'appellant dans la liste retournée par la BDD
                
        if login_appelant: # Si un appelant est bien authentifié sur l'IP du client solicitant le serveur
            # TODO vérifier si l'utilisateur appelé n'est pas déjà appellé par quelqu'un d'autre (à part si on fait de la conférence ?)
            # TODO vérifier que plusieurs utilisateurs peuvent appeler en même temps (2 appels en parallèle)

            # Récupération du login de l'utilisateur appelé
            login_appele = msg[13:] # suppression de l'entête "CALL REQUEST " (13 caractères) du message reçu
                        
            # Récupération de l'IP de l'utilisateur appelé
            requete = f"SELECT ip FROM utilisateurs WHERE login = '{login_appele}';"
            ip_appele = self.requete_BDD(requete)[0][0]
                        
            # Envoi de la demande d'appel à l'utilisateur appelé
            self.envoyer_signalisation(ip_appele, f"CALL REQUEST {login_appelant}")
            
            # Fin de la fonction d'envoi de la requête d'appel,
            # la réponse "CALL ACCEPT" ou "CALL DENY" sera traitée dans traiter_signalisation() puis lancer_appel(),
            # Afin de ne pas bloquer le fonctionnement du serveur en attendant la réponse de l'appelé.
        
        else: # Si l'IP de l'appellant n'est pas authentifié
            # self.envoyer_signalisation(ip_appelant, "CALL REJECT") ?
            pass

    def lancer_appel(self, ip_appele:str, msg: str)-> None:
        # Le message reçu est de la forme "CALL ACCEPT login_appelant-login_appele_acceptant_l_appel"
        # TODO vérifier que les utilisateurs sont bien authentifiés ?
        login_appelant: str
        ip_appelant: str
        login_appele: str
        
        # Isolement des logins des deux utilisateurs de l'en-tête "CALL ACCEPT " (12 caractères) du message
        msg = msg[12:]
        
        # Récupération du login de l'utilisateur appelant, et du login de l'utilisateur appelé qui a accepté l'appel
        login_appelant, login_appele = msg.split("-")
        
        # Récupération de l'IP de l'utilisateur appelant
        requete_bdd = f"SELECT ip FROM utilisateurs WHERE login = '{login_appelant}';"
        ip_appelant = self.requete_BDD(requete_bdd)[0][0]
        
        # TODO lancer l'appel côté serveur (transfert de la voix)
        
        # Informer les deux utilisateurs que l'appel est en cours
        self.envoyer_signalisation(ip_appelant, f"CALL START {login_appele}")
        self.envoyer_signalisation(ip_appele, f"CALL START {login_appelant}")
    
    
    def rejeter_appel(self, ip_client:str, msg: str)-> None:
        # TODO vérifier que l'utilisateur est bien authentifié ?
        pass
    
    
    def terminer_appel(self, ip_client:str, msg: str)-> None:
        # TODO vérifier que l'utilisateur est bien authentifié
        pass
                
    
if __name__ == "__main__":
    service_signalisation: Service_Signalisation
    service_signalisation = Service_Signalisation()