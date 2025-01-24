# <center> SAÉ 3.02 : Développer des applications communicantes </center>

# <center> Compte-rendu </center>

## <center> BUT2 R&T - IUT LANNION </center>

### <center> Groupe B1 - Binôme 5 </center>

### <center> Tugdual Thepaut <br> Yann Plougonven--Lastennet </center>

# I. Objectif du projet :

L'objectif de ce projet est de développer en programmation orientée objet Python un service VoIP client-serveur. Réalisé dans la cadre d'une Situation d'Apprentissage et d'Évaluation (SAE32) en binôme durant notre S3 de BUT Réseaux et Télécommunications à l'IUT de Lannion.

L'intérêt est de mettre en oeuvre diverses compétences travaillées en cours de POO Python, telles que la création de protocoles applicatifs, d'interfaces homme machine, et l'exploitation du protocole UDP avec Python. Nous profitons également de ce projet pour apprendre à utiliser l'outil git intégré à Visual Studio Code.

Le code est testé pour Python 3.12.8 sur Windows 11, et fonctionne relativement bien sur Debian 12.

# II. Utilisation du logiciel

### 1 Lancement du serveur
On lance le serveur dans un terminal via la commande "python3 *chemin du fichier serveur.py*"

![Image](/images/demarrages.png)

### Lancement du client
Lancer le client ouvre le premier IHM celui d'authentification qui nous permet de se connecter au serveur via un couple login/mdp et en paramètre l'@ip du serveur.

![Image](/images/IHM_Auth.png)

### Le serveur vérifie que le client se connecte bien via ses identifiants :

Dans l'interface du serveur, nous pouvons voir que le client s'est connecté proprement et que le serveur mets à jour sa liste de contactes

![Image](/images/auths.png)

### On arrive sur la liste des contactes

Une fois que le client s'est connecté, il accède à la liste des contactes qu'il peut appeler une fois que ceux-ci sont actifs.

![Image](/images/contactsc1.png)

### On attends que quelqu'un d'autre se connecte et on réactualise la liste des contactes:

Lorsque quelqu'un devient actif, la base de donnée s'actualise et l'on doit actualiser la liste afin de pouvoir observer l'etat de connexion de chacun.

![Image](/images/contactsc2.png)

### Lancement d'appel

On clique sur le contact disponible afin de lancer une requête CALL REQUEST qui permets de lancer une demande d'appel avec un autre client.

![Image](/images/Callrequestserv.png)

### Pendant l'attente de réponse, l'ihm affiche "ça sonne"

![Image](/images/appelsonnec%20(1).png)

### Client appellé :

Côté client appellé, un nouvel interface apparait avec le nom de l'appellant et une proposition pour décrocher le téléphone.

![Image](/images/onnousappellec.png)

### Le deuxième client accepte l'appel :

Quand le client appellé rejoint l'appel, cela se traduit par un CALL ACCEPT.

![Image](/images/call_accepts.png)

### L'ihm est alors en mode appel :

Pendant l'appel, les deux clients peuvent se parler et s'entendre.

![Image](/images/appelencours%20(1).png)

### Identifiants possibles pour les clients :
Les identifiants sont enregistrés en clair dans la base de données du serveur. 

Voici des utilisateurs créés pour tester le programme :
* Yann:lannion
* Tugdual:lannion
* John Doe:azerty
* Alice:azerty1
* Bob:123456


# III. Tableaux comparatifs entre le cahier des charges et le projet final


# Comparatif entre le cahier des charges et le projet fini

| Élément                     | Cahier des charges                                                                                       | Projet fini                                                                                          |
|-----------------------------|---------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| **Ports utilisés**          | * **5000 :** port d'émission côté client<br>  * **5001 :** port de réception côté client de la voix<br>  * **5101 :** port de réception côté client du protocole applicatif<br>  * **6000 :** port d'émission côté serveur<br>  * **6000+n :** port de réception côté serveur de la voix du client n<br>  * **6100 :** port de réception côté serveur du protocole applicatif avec tous les clients | Identique au cahier des charges                                                                      |
| **Maquette de l'IHM**       | !Nous avions 2 interfaces: un pour l'authentification et un pour l'appel ![Image](/images/maquette_IHM_connexion%20(1).png) ![Image](/images/maquette_IHM%20(1).png)|![Image](/images/IHM_Auth.png) ![Image](/images/IHM_Contact1.png)                                                                                        |
| **Diagramme des échanges**  | **Connexion, établissement et fin d'appel :**<br>  Étape 1 : Les clients utilisent le protocole applicatif ("flux de signalisation") pour demander au serveur VoIP de les authentifier.<br>  Étape 2 : Le serveur VoIP accepte l'authentification des clients.<br>  Étape 3 : Le client 1 utilise le protocole applicatif pour demander au serveur VoIP d'appeler le client 2.<br>  Étape 4 : Le serveur transmet la demande au client 2.<br>  Étape 5 : Le client 2 informe le serveur qu'il accepte l'appel.<br>  Étape 6 : Le serveur informe les deux clients que l'appel est lancé.<br>  Étape 7 (en bleu) : Les clients échangent les données de voix en passant par le serveur.<br>  Étape 8 : Le client 1 utilise le protocole applicatif pour informer le serveur qu'il raccroche.<br>  Étape 9 : Le serveur informe le client 2 que l'appel est terminé. | **Connexion, établissement, fin d'appel et refus d'appel :**<br>  Étapes 1 à 9 identiques au cahier des charges.<br><br>**Refus d'un appel :**<br>  Étape 1 : Le client 1 utilise le protocole applicatif ("flux de signalisation") pour demander au serveur VoIP d'appeler le client 2.<br>  Étape 2 : Le serveur transmet la demande au client 2.<br>  Étape 3 : Le client 2 informe le serveur qu'il refuse l'appel.<br>  Étape 4 : Le serveur informe le client 1 que l'appel est refusé. |
| **Format JSON**             | *Initialement on nous a dit qu'il ne nous était pas nécessaire d'utiliser le format JSON*                                                                                                | *Utilisation de la sérialisation / désérialisation pour l'envoie et la réception des listes de contactes*                                                                                              |
| **Base de données**         | ![Image](/images/9.png)          | ![Image](/images/10.png)                                                          |
|**Gestion d'appels multiples**|Rien de prévu initialement| La gestion de plusieurs appels en parallèle qui n'était pas initialement dans notre cahier des charges est fonctionnel|

### Fonctionnement de plusieurs appels simultanés.

![Image](/images/deux_appels_en_parrallèle.gif)
# IV. Diagrammes de Gantt

![Diagramme de Gantt](/images/diagramme_Gantt.png)

# V. Diagrammes des classes

### Class IHM_Authentification

| Attributs        |
|------------------|
| __label_erreur   |
| __frame_auth     |
| __entry_login    |
| __label_login    |
| __entry_mdp      |
| __label_mdp      |
| __frame_serv     |
| __label_ip_client|
| __entry_ip_serv  |
| __btn_auth       |
| __label_titre    |

| Méthode                          | Description                                                                                                   |
|----------------------------------|---------------------------------------------------------------------------------------------------------------|
| __init__(self, msg_erreur:str=””)| Constructeur de la classe définissant l'inteface graphique d'authentification du client VoIP auprès du serveur VoIP. d'authentification.|
| creer_utilisateur(self)          | Créer un objet Utilisateur à partir des informations renseignées dans les champs de l'IHM d'authentification.|
| quit(self)                       | Gestion de la fermeture de la fenêtre de l'IHM d'authentification.|

### Class IHM_Contacts

| Attributs                   |
|-----------------------------|
| __utilisateur               |
| __login_utilisateur         |
| __ihm_appel                 |
| __stop_thread_ecoute        |
| __thread_ecoute             |
| __frame_contacts            |
| __label_titre               |
| __label_sous_titre          |
| __btn_actualiser            |

| Méthode                                       | Description                                                                                   |
|-----------------------------------------------|-----------------------------------------------------------------------------------------------|
| __init__(self)                                | Constructeur de la classe définissant l'interface graphique des contacts du client VoIP.|
| lister_contacts(self) → None                 | Actualise la liste des contacts disponibles et gère les exceptions en cas d'erreurs.|
| appeler_correspondant(self, correspondant:str)| Instancie l'interface d'appel avec le correspondant sélectionné. Pour cela, arrête arrête d'abord l'écoute de requête d'appel pour éviter les interférences.|
| ecouter_requete_appel(self) → None           | Ecoute en arrirère-plan des potentielles requêtes d'appel entrantes.|
| demarrer_deamon_ecoute_requetes_appel(self)  | Lance un thread qui écoute les requêtes d’appel en arrière-plan.|
| stopper_deamon_ecoute_requetes_appel(self, timeout:float=190) → None | Arrête le thread d’écoute pour éviter les interférences.|
| ouvrir_ihm_appel(self, correspondant:str) → None | correspondant (str): login du correspondant qui a demandé l'appel.|
| quit(self) → None                            | Gérer la fermeture de l'IHM client : déconnexion de l'utilisateur et fermeture de la fenêtre.|


### Class IIHM_Appel

| Attributs                  |
|----------------------------|
| __utilisateur              |
| __login_utilisateur        |
| __correspondant            |
| __le_client_est_l_appellant|
| __appel_en_cours           |
| __label_etat_appel         |
| __cadre_interactif         |
| __bouton_micro             |
| __bouton_hp                |
| __bouton_decrocher         |
| __bouton_raccrocher        |

| Méthode                                          | Description                                                                                     |
|--------------------------------------------------|-------------------------------------------------------------------------------------------------|
| __init__(self)                                   | Constructeur de la classe définissant l'interface graphique d'appel VoIP.|
| envoyer_requetes_appel(self) → None             | Appel la méthode envoyer_requete_appel de l'objet utilisateur pour envoyer une requête d'appel au serveur. Adapte l'interface en fonction de la réponse du serveur.|
| decrocher(self) → None                          | Appel des fonctions de décrochage de l'appel et de démarrage de l'appel. Mise à jour de l'interface en en attendant le démarrage de l'appel.|
| demarrer_appel(self, autorisation_de_demarrer_l_appel:bool, port_reception_voix_du_serveur:int) → None | Démarrer l'appel avec le correspondant. Mise à jour de l'interface en conséquence et appel de la méthode demarrer_appel de l'objet utilisateur.|
| raccrocher(self) → None                         | Raccrocher l'appel. Si l'appel est en cours, demande au serveur de raccrocher. Si l'appel n'a pas été accepté, demande au serveur de refuser l'appel.|
| couper_micro(self) → None                       | Fonction pour couper le micro (non implémentée).|
| activer_hp(self) → None                         | Fonction pour activer le haut-parleur (non implémentée).|
| fermer_ihm_appel(self) → None                   | Ferme l’interface d’appel.|
| quit(self) → None                               | Déconnecte l’utilisateur et termine l’appel en cas de fermeture forcée.|


### Class Utilisateur

| Attributs                  |
|----------------------------|
| __login                    |
| __mdp                      |
| __ip_serv                  |
| __stop_appel               |
| __ihm_appel                |
| __flux_emission            |
| __flux_reception           | 
| __audio                    | 
| __socket_envoie            |
| __socket_reception         |
| __socket_reception_voix    |

| Méthode                                         | Description                                                                                     |
|------------------------------------------------|-------------------------------------------------------------------------------------------------|
| __init__(self, login:str, mdp:str, ip_serv:str) | Initialise les attributs pour gérer l’utilisateur, l’authentification, et les appels.|
| authentification(self) → None                  | Gère l'authentification de l'utilisateur avec le serveur.|
| deconnexion(self) → None                       | Informe le serveur de la déconnexion de l'utilisateur.|
| envoyer_message(self, msg:str) → None          | Envoie un message texte au serveur via le socket d’envoi.|
| recevoir_message(self) → str                   | Reçoit un message texte du serveur via le socket de réception.|
| actualiser_liste_contacts(self) → str          | Récupère la liste des contacts disponibles au format dictionnaire via JSON.|
| envoyer_requete_appel(self, correspondant:str) → tuple[bool, int] | Traite les requêtes d’appel pour un correspondant spécifique.|
| decrocher(self, login_correspondant, login_utilisateur) → tuple[bool, int] | Accepte un appel entrant et retourne les informations nécessaires pour démarrer l’appel.|
| rejeter_appel(self, correspondant) → None      | Permet de refuser un appel et de fermer l’IHM d’appel.|
| demarrer_appel(self, port_reception_voix_du_serveur:int) → None | Gère le démarrage d’un appel après validation par le serveur.|
| raccrocher(self) → None                        | Termine un appel en cours et informe le serveur de la fin de l’appel.|
| terminer_appel(self, ouvrir_ihm_contacts:bool) → None | Termine un appel et réouvre l’IHM des contacts si nécessaire.|
| get_login(self) → str                          | Retourne le login de l'utilisateur.|
| set_timeout_socket_reception(self, timeout:float=180) → None | Définit un délai pour le socket de réception.|
| set_attribut_ihm_appel(self, ihm_appel:IHM_Appel) → None | Permet à la classe Utilisateur d’interagir avec l’IHM d’appel.|

# VI. Bilan de fin

> Pour faire le bilan sur ce projet, nous pensons qu'il a été enrichissant. En effet nous avons découvert de nouvelles fonctionnalitées et de nouvelles méthodes pour résoudre certains problèmes rencontrés. Nous avons trouvé certains aspects du projet complexes mais cela nous a permis de nous améliorer. Nous avons également pu monter en compétences dans d'autres domaines comme par exemple l'utilisation de GitHub ou la gestion de projet.