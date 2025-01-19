# VoIPy : Projet de VoIP avec Python
L'objectif de ce projet est de développer en programmation orientée objet Python un service VoIP client-serveur. Réalisé dans la cadre d'une Situation d'Apprentissage et d'Évaluation (SAE32) en binôme durant notre S3 de BUT Réseaux et Télécommunications à l'IUT de Lannion.

L'intérêt est de mettre en oeuvre diverses compétences travaillées en cours de POO Python, telles que la création de protocoles applicatifs, d'interfaces homme machine, et l'exploitation du protocole UDP avec Python. Nous profitons également de ce projet pour apprendre à utiliser l'outil git intégré à Visual Studio Code.

Le code est testé pour Python 3.12.8 sur Windows 11, et fonctionne relativement bien sur Debian 12.

## Comment essayer VoIPy ?
Avertissement : VoIPy ne devrait pas être utilisé pour communiquer des informations sensibles, les communications et le stockage des identifiants n'étant pas sécurisés.
1. Lancez le programme serveur.py.
2. Lancez le programme client.py sur deux ordinateurs connectés sur le même réseau local.
3. Sur l'interface cliente, connectez-vous avec un utilisateur différent par ordinateur (grâce aux identifiants enregistrés dans la BDD du serveur) et renseignez l'IP de la machine serveur.
5. Cliquez sur le bouton "Actualiser la liste" pour voir les utilisateurs connectés et disponible, afin de pouvoir les appeler.
6. Ou restez connecté sur l'interface pour pouvoir recevoir des appels.

### Identifiants utilisables
Les identifiants sont enregistrés en clair dans la base de données du serveur. 

Voici des utilisateurs créés pour tester le programme :
* Yann:lannion
* Tugdual:lannion
* John Doe:azerty
* Alice:azerty1
* Bob:123456
