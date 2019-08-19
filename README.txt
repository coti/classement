# Outil de r�cup�ration du classement de ses adversaires.

(c) Camille Coti, 2013-2018

## Syst�me de calcul

Le syst�me classement de tennis mis en place par la F�d�ration fran�aise de tennis calcule votre nouveau classement en fonction du classement de vos adversaires non pas au moment o� vous les avez battus, mais de leur calssement futur. Un 30 qui monte 15/3 comptera comme un 15/3 dans votre bilan. 

Pour faire ce calcul, la FFT effectue un gros calcul sur l'ensemble des comp�titeurs en deux phases :
* la premi�re phase a lieu en prenant en compte le classement actuel
* la deuxi�me phase a lieu en prenant en compte le classement calcul� par la passe pr�c�dente, jusqu'� stabilisation
Cela n�cessite de calculer ces deux phases sur l'ensemble des comp�titeurs, ce qui repr�sente un volume de calcul consid�rable.

L'outil propos� ici permet d'aller r�cup�rer r�cursivement les palmar�s de vos adversaires, jusqu'� une certaine profondeur. Ainsi, l'outil effectue une approximation du futur classement de vos adversaires, gr�ce � une approximation du futur classement de leurs adversaires, etc. La r�cursion s'arr�te � un niveau d�fini par l'utilisateur. 

## Pr�requis

Il suffit de disposer d'un interpr�teur Python. Les biblioth�ques utilis�es sont incluses dans la distribution standard Python 2.7 ou install�es automatiquement au lancement du script. On suppose ici que l'interpr�teur est situ� dans /usr/bin/python.

## Utilisation

### Sous Unix (Mac OS, Lunix)

Dans un terminal, taper :

./palmares.py

### Sous Windows

Python 2.7 peut �tre t�l�charg� ici : https://www.python.org/ftp/python/2.7.11/python-2.7.11.msi

* lancer l'invite de commandes
* remonter dans le dossier C: gr�ce � la ligne de commande cd ".."
* aller dans le dossier d'installation python, par exemple
    cd "Python27" 
si Python est install� dans C://Python27)
* entrer la ligne de commande 
    python.exe palmares.py
(apr�s avoir mis tous les fichiers .py dans ce m�me r�pertoire)

Autre fa�on de faire :
* faire un clic droit sur le fichier palmares.py
* s�lectionner "ouvrir avec"
* choisir le terminal dans le dossier applications/utilitaires

### Ex�cution

L'outil demande de saisie ses identifiants sur l'espace du licenci�, le num�ro de licence du joueur concern� et la profondeur de la recherche. Le dernier classement calcul� affich� correspnd au classement calcul� pour le joueur demand�. 

Il est n�cessaire d'�tre connect� � Internet pendant toute l'op�ration.

### Interface graphique

Ex�cuter le fichier interface2.py. Remplir les champs demand�s et cliquer sur le bouton. La sortie s'affichera dans la grosse boite blanche en-dessous.

Attention, l'interface est pleine de bugs. Merci aux testeurs !

## Limitations

Il est pour le moment :
* seulement en version alpha
* verbeux et peu esth�tique

## TODO list:
* am�liorer la GUI
* corriger les bugs de la GUI
* prise en compte des formats courts

## Copyright

Classement est un programme informatique servant � estimer son futur
classement de tennis d'apr�s la FFT en estimant r�cursivement le futur
classement de ses adversaires.

Ce logiciel est un logiciel Libre distribu� sous deux licences, la licence 
CeCILL-C correspondant au droit europ�en, et la Licence Publique G�n�rale 
Limit�e GNU. Ce programme est libre, vous pouvez le redistribuer et/ou le 
modifier selon les termes de la licence CeCILL-C comme distribu�e par le CEA,
le CRNS et l'INRIA � l'URL suivante <http://www.cecill.info> ou de la Licence 
Publique G�n�rale Limit�e GNU publi�e par la Free Software Foundation 
(version 2 ou bien toute autre version ult�rieure choisie par vous).

Ce programme est distribu� car potentiellement utile, mais SANS AUCUNE GARANTIE,
ni explicite ni implicite, y compris les garanties de commercialisation ou 
d'adaptation dans un but sp�cifique. Reportez-vous � la Licence Publique 
G�n�rale Limit�e GNU ou � la licence CeCILL-C pour plus de d�tails.

Vous devez avoir re�u une copie de la Licence Publique G�n�rale Limit�e GNU 
et de la licence CeCILL-C en m�me temps que ce programme ; si ce n'est pas le
cas, �crivez � la Free Software Foundation, Inc., 59 Temple Place, Suite 330, 
Boston, MA 02111-1307, �tats-Unis.

Si vous �tes en train de lire ceci, c'est que vous avez eu connaissance des 
licences CeCILL-C et LGPL et que vous en avez accept� les conditions.
