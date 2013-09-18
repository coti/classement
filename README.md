Outil de récupération du classement de ses adversaires.

Le système classement de tennis mis en place par la Fédération française de tennis calcule votre nouveau classement en fonction du classement de vos adversaires non pas au moment où vous les avez battus, mais de leur calssement futur. Un 30 qui monte 15/3 comptera comme un 15/3 dans votre bilan. 

Pour faire ce calcul, la FFT effectue un gros calcul sur l'ensemble des compétiteurs en deux passes :
- la première passe a lieu en prenant en compte le classement actuel
- la deuxième passe a lieu en prenant en compte le classement calculé par la première passe
Cela nécessite de calculer ces deux passes sur l'ensemble des compétiteurs, ce qui représente un volume de calcul considérable.

L'outil proposé ici permet d'aller récupérer récursivement les palmarès de vos adversaires, jusqu'à une certaine profondeur. Ainsi, l'outil effectue une approximation du futur classement de vos adversaires, grâce à une approximation du futur classement de leurs adversaires, etc. La récursion s'arrête à un niveau défini par l'utilisateur. 

Il est pour le moment :
- seulement en version alpha
- incomplet (voir TODO list)
- uniquement en ligne de commande
- verbeux et peu esthétique

TODO list:
- prise en compte de la pénalisation pour 5 WO et au-delà de 3 WO
- quand des numérotés entrent en compte, l'outil plante
- prise en compte de la bonif de championnat
- écrire une GUI