#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" Outil de recuperation du classement.
 "
 " :copyright: Copyright 2013-2015, see AUTHORS 
 "             Copyright 2013-2015, voir AUTHORS
 " :licence: CeCILL-C or LGPL, see COPYING for details.
 "           CeCILL-C ou LGPL, voir COPYING pour plus de details.
 "
 "
 " TODO:
 " - Prise en compte des formats courts
 " - Joli formattage de sortie
  """


from __future__ import print_function, unicode_literals

import re

classementNumerique = { "S"  : -1,
                        "ND" : 0,
                        "NC" : 0,
                        "40" : 1,
                        "30/5" : 2,
                        "30/4" : 3,
                        "30/3" : 4,
                        "30/2" : 5,
                        "30/1" : 6,
                        "30" : 7,
                        "15/5" : 8,
                        "15/4" : 9,
                        "15/3" : 10,
                        "15/2" : 11,
                        "15/1" : 12,
                        "15" : 13,
                        "5/6" : 14,
                        "4/6" : 15,
                        "3/6" : 16,
                        "2/6" : 17,
                        "1/6" : 18,
                        "0" : 19,
                        "-2/6" : 20,
                        "-4/6" : 21,
                        "-15" : 22,
                        "Top 60/Top 100" : 23,
                        "Top 40/Top 60" : 24}

points = { -3 : 15,
           -2 : 20,
           -1 : 30,
            0 : 60,
            1 : 90,
            2 : 120 }

maintienF = { "NC" : 0,
              "40" : 0,
              "30/5" : 6,
              "30/4" : 70,
              "30/3" : 120,
              "30/2" : 170,
              "30/1" : 210,
              "30" : 265,
              "15/5" : 295,
              "15/4" : 305,
              "15/3" : 310,
              "15/2" : 330,
              "15/1" : 350,
              "15" : 395,
              "5/6" : 405,
              "4/6" : 435,
              "3/6" : 500,
              "2/6" : 560,
              "1/6" : 610,
              "0" : 630,
              "-2/6" : 760,
              "-4/6" : 760,
              "-15" : 810,
              "Top 60/Top 100" : 860,
              "Top 40/Top 60" : 920}

maintienH = { "NC" : 0,
              "40" : 0,
              "30/5" : 6,
              "30/4" : 70,
              "30/3" : 120,
              "30/2" : 170,
              "30/1" : 210,
              "30" : 285,
              "15/5" : 305,
              "15/4" : 315,
              "15/3" : 325,
              "15/2" : 340,
              "15/1" : 370,
              "15" : 430,
              "5/6" : 435,
              "4/6" : 435,
              "3/6" : 465,
              "2/6" : 495,
              "1/6" : 555,
              "0" : 605,
              "-2/6" : 760,
              "-4/6" : 860,
              "-15" : 960,
              "Top 60/Top 100" : 1010,
              "Top 40/Top 60" : 1110}

victoiresF = { "NC" : 6,
               "40" : 6,
               "30/5" : 6,
               "30/4" : 6,
               "30/3" : 6,
               "30/2" : 6,
               "30/1" : 6,
               "30" : 8,
               "15/5" : 8,
               "15/4" : 8,
               "15/3" : 8,
               "15/2" : 8,
               "15/1" : 8,
               "15" : 9,
               "5/6" : 9,
               "4/6" : 9,
               "3/6" : 10,
               "2/6" : 11,
               "1/6" : 12,
               "0" : 14,
               "-2/6" : 15,
               "-4/6" : 16,
               "-15" : 17,
               "Top 60/Top 100" : 17,
               "Top 40/Top 60" : 19}

victoiresH = { "NC" : 6,
               "40" : 6,
               "30/5" : 6,
               "30/4" : 6,
               "30/3" : 6,
               "30/2" : 6,
               "30/1" : 6,
               "30" : 8,
               "15/5" : 8,
               "15/4" : 8,
               "15/3" : 8,
               "15/2" : 8,
               "15/1" : 8,
               "15" : 9,
               "5/6" : 9,
               "4/6" : 9,
               "3/6" : 10,
               "2/6" : 10,
               "1/6" : 11,
               "0" : 12,
               "-2/6" : 15,
               "-4/6" : 17,
               "-15" : 19,
               "Top 60/Top 100" : 20,
               "Top 40/Top 60" : 22}

serie = { "NC" : 4,
          "40" : 4,
          "30/5" : 4,
          "30/4" : 4,
          "30/3" : 4,
          "30/2" : 4,
          "30/1" : 4,
          "30" : 3,
          "15/5" : 3,
          "15/4" : 3,
          "15/3" : 3,
          "15/2" : 3,
          "15/1" : 3,
          "15" : 2,
          "5/6" : 2,
          "4/6" : 2,
          "3/6" : 2,
          "2/6" : 2,
          "1/6" : 2,
          "0" : -2,
          "-2/6" : -2,
          "-4/6" : -2,
          "-15" : -2,
          "Top 60/Top 100" : -2,
          "Top 40/Top 60" : -2}

# affiche le classement calculé d'un joueur
def afficheClassement( origine, calcul, harmonise, impression=True ):
    if impression:
        print(" ==> Classement de sortie :", calcul, "- Harmonisé :" , harmonise, "-  classement d\'origine :", origine)
    return


def match_list_str(match_list):
    g = (classement + (' ({})'.format(coeff) if coeff != 1 else '') + (' (WO)' if wo else '')
         for classement, wo, coeff in match_list)
    return ', '.join(g)


# calcule le V - E - 2I - 5G
def VE2I5G(classement, victoires, defaites, impression=False):
    def sum_coeff(match_list):
        return sum(coeff for _, _, coeff in match_list)

    v = sum_coeff(victoires)

    lstE = lstInf(classement, defaites, 0)
    e = sum_coeff(lstE)

    lstI = lstInf(classement, defaites, 1)
    i = sum_coeff(lstI)

    lstG = lstInf(classement, defaites, -1)
    g = sum_coeff(lstG)

    if impression:
        print("V = ", v, "(Nombre de victoires) : ", match_list_str(victoires))
        print("E = ", e, "(Nb de défaites à échelon égal) :", match_list_str(lstE))
        print("I = ", i, "(Nb de défaites à échelon -1) :", match_list_str(lstI))
        print("G = ", g, "(Nb de défaites à échelons <= -2 et par w.o à partir du 3e) :", match_list_str(lstG))

    return int(round(v - e - 2 * i - 5 * g))


# Calcule le nb de defaites E echelons en-dessous
def lstInf(myClassement, defaites, E):
    lst = []
    for classement, wo, coeff in defaites:
        if E >= 0:
            if not wo:  # exclure les WO
                if classementNumerique[classement] == (classementNumerique[myClassement] - E):
                    lst.append((classement, wo, coeff))
        else:
            if not wo or classement == "S":  # exclure les WO sauf à partir du 3eme
                if classementNumerique[classement] <= (classementNumerique[myClassement] - 2):
                    lst.append((classement, wo, coeff))

    return lst

# Retourne le nombre de points apportes par une victoire
def pointsVictoire( myClassement, classementBattu ):
    diff = classementNumerique[ classementBattu ] - classementNumerique[ myClassement ]
    if( diff  < -3 ):
        return 0
    else:
        if( diff > 2 ):
            diff = 2
        return points[ diff ]

# Retourne le nombre de victoires prises en compte
def nbVictoiresComptant( myClassement, sexe, myVictoires, myDefaites, impression=True ):
    if( "M" == sexe ):
        victoires = victoiresH
    else:
        victoires = victoiresF

    nb = victoires[ myClassement ]
    v = VE2I5G( myClassement, myVictoires, myDefaites, impression )

    if impression:
        print("V - E - 2I - 5G :", v)
    
    add = 0
    if( 4 == serie[ myClassement ] ): 
        if( v < 0 ) :
            add = 0
        elif( v >= 0 and v <= 4 ):
            add = 1
        elif( v >= 5 and v <= 9 ):
            add = 2
        elif( v >= 10 and v <= 14 ):
            add = 3
        elif( v >= 15 and v <= 19 ):
            add = 4
        elif( v >= 20 and v <= 24 ):
            add = 5
        elif( v >= 25 ):
            add = 6
    elif( 3 == serie[ myClassement ] ): 
        if( v < 0 ) :
            add = 0
        elif( v >= 0 and v <= 7 ):
            add = 1
        elif( v >= 8 and v <= 14 ):
            add = 2
        elif( v >= 15 and v <= 22 ):
            add = 3
        elif( v >= 23 and v <= 29 ):
            add = 4
        elif( v >= 30 and v <= 39 ):
            add = 5
        elif( v >= 40 ):
            add = 6
    elif( 2 == serie[ myClassement ] ): 
        if( v < -41 ) :
            add = -3
        elif( v >= -40 and v <= -31 ):
            add = -2
        elif( v >= -30 and v <= -21 ):
            add = -1
        elif( v >= -1 and v <= -20 ):
            add = 0
        elif( v >= 0 and v <= 7 ):
            add = 1
        elif( v >= 8 and v <= 14 ):
            add = 2
        elif( v >= 15 and v <= 22 ):
            add = 3
        elif( v >= 23 and v <= 29 ):
            add = 4
        elif( v >= 30 and v <= 39 ):
            add = 5
        elif( v >= 40 ):
            add = 6
    elif( -2 == serie[ myClassement ] ): 
        if( v < -81 ) :
            add = -4
        elif( v >= -80 and v <= -61 ):
            add = -4
        elif( v >= -60 and v <= -41 ):
            add = -3
        elif( v >= -31 and v <= -40 ):
            add = -2
        elif( v >= -21 and v <= -30 ):
            add = -1
        elif( v >= -1 and v <= -20 ):
            add = 0
        elif( v >= 0 and v <= 9 ):
            add = 1
        elif( v >= 10 and v <= 19 ):
            add = 2
        elif( v >= 20 and v <= 24 ):
            add = 3
        elif( v >= 25 and v <= 29 ):
            add = 4
        elif( v >= 30 and v <= 34 ):
            add = 5
        elif( v >= 35 and v <= 44 ):
            add = 6
        elif( v >= 45 ):
            add = 7
    else:
        add = 0
    return nb + add


# Calcule les points a un classement donne
def calculPoints( myClassement, sexe, myVictoires, myDefaites, nbVicChampIndiv, impression=True ):
    nbV = nbVictoiresComptant( myClassement, sexe, myVictoires, myDefaites, impression )
    sortedVictoires = sortVictoires( myVictoires )
    victoiresComptant = victoiresQuiComptent( sortedVictoires, nbV )

    if impression:
        print("Victoires prises en compte ({}) : {}".format(nbV, match_list_str(victoiresComptant)))

    nbPoints = 0

    for classement, _, coeff in victoiresComptant:
        nbPoints += pointsVictoire( myClassement, classement ) * coeff

    # Bonifs

    nb = nbWO( myVictoires )
    bonifAbsenceDefaitesPossible = ( ( len( myVictoires ) - nb ) >= 5 )

    bonif = 0

    if True == bonifAbsenceDefaitesPossible:
        if serie[ myClassement ] == 2:
            if True == absenceDef( myDefaites, myClassement ):
                bonif =150
        if serie[ myClassement ] == 3:
            if True == absenceDef( myDefaites, myClassement ):
                bonif = 100
        if myClassement == '30/2' or myClassement == '30/1' :
            if True == absenceDef( myDefaites, myClassement ):
                bonif = 50
    if bonif != 0 and impression:
        print("Bonif absence de defaite significative:", bonif)

    nbPoints = nbPoints + bonif

    if nbVicChampIndiv > 3:
        nbVicChampIndiv = 3
    bonif = nbVicChampIndiv * 15

    nbPoints = nbPoints + bonif
    if bonif != 0 and impression:
        print("Bonif championnat indiv :", bonif)

    return int(nbPoints)

# Trie les victoires par ordre decroissant
def sortVictoires( myVictoires ):
    if not myVictoires:
        return []

    return sorted(myVictoires, key=lambda v: (classementNumerique[v[0]], v[2]), reverse=True)


# Teste si les points de maintien sont atteints pour le classement
def maintienOK( myClassement, mySexe, myPoints, impression=True ):
    if 'M' == mySexe:
        maintien = maintienH
    else:
        maintien = maintienF

    if impression:
        print("Points acquis :", myPoints, "- points nécessaires pour le maintien à", myClassement, ":", maintien[ myClassement ])

    return myPoints >= maintien[myClassement]


# Plus gros classement battu
def plusGrosseVictoire( myVictoires ):
    if 0 == len( myVictoires ):
        return None
    sorted = sortVictoires( myVictoires )
    for v in sorted:
        if v[1] != True:
            return v[0]

# Plus gros classement battu + E echelons
def plusGrosseVictoirePlusN( myVictoires, E ):
    if 0 == len( myVictoires ):
        return None

    grosse = plusGrosseVictoire( myVictoires )
    if grosse == "Top 60/Top 100" or grosse == "Top 40/Top 60":
        return "Top 40/Top 60"
    else:
        for( k, v ) in classementNumerique.iteritems():
            if( k == grosse ):
                for( k_, v_ ) in classementNumerique.iteritems():
                    if( v_ == v + E ):
                        return k_

# Echelon inferieur au classement d'entree
def echelonInferieur( myClassement ):
    v = classementNumerique[ myClassement ]

    if( v == 0 ):
        return 0
    
    for( k_, v_ ) in classementNumerique.iteritems():
        if( v_ == v - 1 ):
            return k_

# Classement propose au premier tour
def classementPropose1erTour( myVictoires, myClassement ):
    grosse = plusGrosseVictoire( myVictoires )
    if( 4 == serie[ grosse ] ): 
        plus = plusGrosseVictoirePlusN( myVictoires, 2 )
    else:
        plus = plusGrosseVictoirePlusN( myVictoires, 1 )

    if classementNumerique[ plus ] >  classementNumerique[ myClassement ]:
        return plus
    else:
        return myClassement

# Normalise un classement
def normalisation(classement, sexe):
    c = classement.split( ) # certains classements ont des precisions, e.g. 'NC (2014)' -> garder uniquement la 1ere partie
    if len( c ) > 1:
        classement = c[0]
    if estNumerote( classement ):
        # on est sur un numerote
        s = classement[1:]
        n = int( s )
        if 'H' == sexe:
            if n <= 60:
                classement = "Top 40/Top 60"
            else:
                classement = "Top 60/Top 100"
        else:
            if n <= 40:
                classement = "Top 40/Top 60"
            else:
                classement = "Top 60/Top 100"
    return classement

# determine si le joueur est numéroté
def estNumerote( classement ):
    return re.match(r'[NT]\d+', classement) is not None

# Conversion des numerotes en "Top 40/Top 60" ou "Top 60/Top 100"
def normalisationTab( tab, sexe ):
    tabSortie = []
    for classement, wo, coeff in tab:
        tabSortie.append((normalisation(classement, sexe), wo, coeff))
    return tabSortie

# Compter le nombre de wo
def nbWO( tab ):
    n = 0
    for t in tab:
        if t[1]:
            n = n + 1
    return n

# Insertion de la penalite wo : a partir de 3, tout wo compte comme une defaite significative
def penaliteWO( defaites, impression=True ):
    _def = []
    w = 0
    for d in defaites:
        if d[1] == True:
            w = w + 1
            if w >= 3:
                o = ( 'S', d[1] )
                # on insere une defaite qu'on appelle S pour que ca compte comme une def significative
                if impression:
                    print("Defaite significative ajoutée (wo)")
            else:
                o = d
        else:
            o = d
        _def.append( o )

    return defaites

# Absence de defaite significative ?
def absenceDef( defaites, classement ):
    for d in defaites:
#        if 'S' != d: # on exclu les wo
        if d[1] == False:
            if( classementNumerique[ d[0] ] <= ( classementNumerique[ classement ] ) ):
                return False
    return True

# Victoires comptant : on supprime les wo
def victoiresQuiComptent( vic, nb ):
    return [v for v in vic if not v[1]][:nb]

# Calcul du classement
def calculClassement( myVictoires, myDefaites, mySexe, myClassement, nbVicChampIndiv, impression ):

    ok = False

    if estNumerote( myClassement ):
        if impression:
            print("Cas particulier : le joueur est numéroté. On le calcule au meme classement.")
            afficheClassement( myClassement, myClassement, myClassement )
        return ( myClassement, myClassement )

    if 0 == len( victoiresQuiComptent( myVictoires, len( myVictoires ) ) ):

        if( 'NC' == myClassement ):
            if 0 != len( myDefaites ):
                afficheClassement( myClassement, '40', '40', impression )
                return ( '40', '40' )
            else:
                afficheClassement( myClassement, '40', '40', impression )
                return ( 'NC', 'NC' )
        else:
            cl = echelonInferieur( myClassement )
            if 'NC' == cl:
                if 0 != len( myDefaites ):
                    afficheClassement( myClassement, '40', '40', impression )
                    return ( '40', '40' )
                else:
                    afficheClassement( myClassement, '40', '40', impression )
                    return ( 'NC', 'NC' )
            else:
                afficheClassement( myClassement, cl, cl, impression )
                return ( cl, cl )
                
    myVictoires = normalisationTab( myVictoires, mySexe )
    myDefaites = normalisationTab( myDefaites, mySexe )
    
    # Insertion de la penalite wo
    if nbWO( myDefaites ) >= 3:
        myDefaites = penaliteWO( myDefaites, impression )

    myClassement = normalisation( myClassement, mySexe )

    classementPropose = classementPropose1erTour( myVictoires, myClassement )
    borneInf = echelonInferieur( myClassement ) # on ne peut pas descendre plus d'un echelon en-dessous

    while( ( False == ok ) and ( "NC" != classementPropose ) and not ( classementPropose is borneInf ) ):

        if impression:
            print(" ==> Classement proposé :", classementPropose)

        pt = calculPoints( classementPropose, mySexe, myVictoires, myDefaites, nbVicChampIndiv, impression )
        ok = maintienOK( classementPropose, mySexe, pt, impression )
        if( True != ok ):
            classementPropose = echelonInferieur( classementPropose )

    # harmonisation du classement
    classementHarmonise = classementPropose

    # penalite WO ?
    if nbWO( myDefaites ) >= 5:
        if impression:
            print("Penalite car trop de WO (", nbWO( myDefaites ), "> 5)")
        classementHarmonise = echelonInferieur( classementPropose )

    # penalite mauvais V - E - 2I - 5G ?
    if 2 == serie[ classementHarmonise ]:
        v = VE2I5G( classementHarmonise, myVictoires, myDefaites, impression=False )
        if v <= -100:
            if impression:
                print("Joueur en 2eme serie, V-E-2I-5G inférieur ou égal à 100 (" + str( v ) + ") : pénalité et descente d'un classement")
            classementHarmonise = echelonInferieur( classementHarmonise )

    if 'NC' == classementPropose:
        if 0 != ( len( myDefaites ) + len( myVictoires ) ):
            classementPropose = classementHarmonise = '40'
        else:
            classementPropose = classementHarmonise = 'NC'

    afficheClassement( myClassement, classementPropose, classementHarmonise, impression )

    return ( classementPropose, classementHarmonise )

def test():

    """
    testDef = [ "30/2", "30/1", "NC", "15/2", "30/3", "30/4", "30/5", "30/3" ]
    testVic = [ "30", "30", "NC", "15/5", "15/4", "30/1", "30/3", "30/5", "N2", "N42", "N3" ]
    testCl = "30/2"
    """

    file_vic = './test_victoires.txt'
    file_def = './test_defaites.txt'

    testVic = []
    testDef = []

    testVic_n = []
    testDef_n = []

    try:
        fd_v = open( file_vic, 'r' )
        fd_d = open( file_def, 'r' )
    except:
        import sys
        print("Erreur ouverture", sys.exc_type, sys.exc_value)


    try:
        lines = fd_v.readlines( )
        for l in lines:
            if l != "\n" : # si la ligne n'est pas vide
                s = l.split( '\t' )
                if 3 == len(s):
                    wo = False
                else:
                    wo = True

                n = [] # retirer les \n
                for st in s[1], s[2]:
                    if "\n" == st[-1:]:
                        st =  st[:-1]
                    n.append( st )
                    
                testVic.append( [ n[0], wo ] )
                testVic_n.append( [ n[1], wo ] )
            
        fd_v.close()

        lines = fd_d.readlines( )
        for l in lines:
            if l != "\n" : # si la ligne n'est pas vide
                s = l.split( '\t' )
                if 3 == len(s):
                    wo = False
                else:
                    wo = True
                    
                n = [] # retirer les \n
                for st in s[1], s[2]:
                    if "\n" == st[-1:]:
                        st =  st[:-1]
                    n.append( st )

                testDef.append( [ n[0], wo ] )
                testDef_n.append( [ n[1], wo ] )
        fd_d.close()
                
    except:    

        import sys
        print("Erreur lecture", sys.exc_type, sys.exc_value)
            
        fd_v.close()
        fd_d.close()

    """
    print "Palma de Martin :"
    print " === VICTOIRES === "
    for m in testVic:
        print m
    print " === DEFAITES === "
    for m in testDef:
        print m
    """

    champ = 0
    testSexe = "H"
    classement = "15"

    """
    print "Victoires :", testVic
    testVic = normalisationTab( testVic, testSexe )
    print "Apres normalisation :", testVic
    

    print "En etant", testCl

    rc = VE2I5G( testCl, testVic, testDef )
    print "V - E - 2I - 5G = ", rc

    for p in testVic:
        print "Points pour ", p, " : ", pointsVictoire( testCl, p )


    print "Nb de victoires prises en compte: ", nbVictoiresComptant( testCl, testSexe, testVic, testDef )

    print "Victoires triees:"
    print sortVictoires( testVic )
    print "Defaites triees:"
    print sortVictoires( testDef )

    pt = calculPoints( testCl, testSexe, testVic, testDef, True )
    print "Points: ", pt, " - maintien: ", maintienOK( testCl, testSexe, pt )

    print "Plus gros classement battu: ", plusGrosseVictoire( testVic )
    print "Plus gros classement battu + 2: ", plusGrosseVictoirePlusN( testVic, 2 )


    print "Plus grosse victoire :", plusGrosseVictoire( testVic )

    print " - * - * - * - * - * - * - * - * - * -"

    """

    calculClassement( testVic_n, testDef_n, testSexe, classement, champ, True )




def main():
    test()



if __name__ == "__main__":
    import sys
    if sys.version_info[0] != 2:
        print("Erreur -- Fonctionne avec Python 2.x")
        exit( -1 )
    main()
