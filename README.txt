# Outil de récupération du classement de ses adversaires.

(c) Camille Coti, 2013

## Système de calcul

Le système classement de tennis mis en place par la Fédération française de tennis calcule votre nouveau classement en fonction du classement de vos adversaires non pas au moment où vous les avez battus, mais de leur calssement futur. Un 30 qui monte 15/3 comptera comme un 15/3 dans votre bilan. 

Pour faire ce calcul, la FFT effectue un gros calcul sur l'ensemble des compétiteurs en deux passes :
* la première passe a lieu en prenant en compte le classement actuel
* la deuxième passe a lieu en prenant en compte le classement calculé par la première passe
Cela nécessite de calculer ces deux passes sur l'ensemble des compétiteurs, ce qui représente un volume de calcul considérable.

L'outil proposé ici permet d'aller récupérer récursivement les palmarès de vos adversaires, jusqu'à une certaine profondeur. Ainsi, l'outil effectue une approximation du futur classement de vos adversaires, grâce à une approximation du futur classement de leurs adversaires, etc. La récursion s'arrête à un niveau défini par l'utilisateur. 

## Prérequis

Il suffit de disposer d'un interpréteur Python. Les bibliothèques utilisées sont incluses dans la distribution standard Python 2.6 ou fournies. On suppose ici que l'interpréteur est situé dans /usr/bin/python.

Les bibliothèques fournies avec ce logiciel sont :

* gaecookie, qui permet d'utiliser plusieurs cookies à la fois (plusieurs champs Set-cookie dans l'en-tête HTTP)
* keepalive : permet d'utiliser une connexion keep-alive avec la bibliothèques urllib, qui normalement ne le permet pas

J'ai apporté une légère modification à la bibliothèque keepalive : j'ai simplement supprimé les méthodes relatives à HTTPS afin de supprimer la dépendance vers la bibliothèque SSL.

## Utilisation

### Sous Unix (Mac OS, Lunix)

Dans un terminal, taper :

./palmares.py

### Sous Windows

Python 2.6 peut être téléchargé ici : http://www.python.org/ftp/python/2.6/python-2.6.msi

* lancer l'invite de commandes
* remonter dans le dossier C: grâce à la ligne de commande cd ".."
* aller dans le dossier d'installation python, par exemple
    cd "Python34" 
si Python est installé dans C://Python34)
* entrer la ligne de commande 
    python.exe palmares.py
(après avoir mis tous les fichiers .py dans ce même répertoire)

### Exécution

L'outil demande de saisie ses identifiants sur l'espace du licencié, le numéro de licence du joueur concerné et la profondeur de la recherche. Le dernier classement calculé affiché correspnd au classement calculé pour le joueur demandé. 

Il est nécessaire d'être connecté à Internet pendant toute l'opération.

### Interface graphique

Exécuter le fichier interface.py. Remplir les champs demandés et cliquer sur le bouton. La sortie s'affichera dans la grosse boite blanche en-dessous.

Attention, l'interface est pleine de bugs.

## Limitations

Il est pour le moment :
* seulement en version alpha
* verbeux et peu esthétique

## TODO list:
* améliorer la GUI
* corriger les bugs de la GUI
* prise en compte des formats courts
