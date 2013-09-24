#!/usr/bin/env python

""" Outil de recuperation du classement.
 " (c) Camille Coti, 2013
 " TODO:
 " - Prise en compte des formats courts
 " - Joli formattage de sortie
  """


classementNumerique = { "S"  : -1,
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
                        "-30" : 23,
                        "Promo" : 24,
                        "1S" : 25}

points = { -3 : 15,
           -2 : 20,
           -1 : 30,
            0 : 60,
            1 : 90,
            2 : 120 }

maintienF = { "NC" : 0,
              "40" : 6,
              "30/5" : 50,
              "30/4" : 100,
              "30/3" : 150,
              "30/2" : 190,
              "30/1" : 210,
              "30" : 260,
              "15/5" : 290,
              "15/4" : 300,
              "15/3" : 310,
              "15/2" : 330,
              "15/1" : 350,
              "15" : 400,
              "5/6" : 400,
              "4/6" : 430,
              "3/6" : 490,
              "2/6" : 550,
              "1/6" : 600,
              "0" : 700,
              "-2/6" : 740,
              "-4/6" : 750,
              "-15" : 800,
              "-30" : 850,
              "Promo" : 950,
              "1S" : 5000}

maintienH = { "NC" : 0,
              "40" : 6,
              "30/5" : 50,
              "30/4" : 100,
              "30/3" : 150,
              "30/2" : 190,
              "30/1" : 210,
              "30" : 280,
              "15/5" : 300,
              "15/4" : 310,
              "15/3" : 320,
              "15/2" : 340,
              "15/1" : 370,
              "15" : 430,
              "5/6" : 430,
              "4/6" : 430,
              "3/6" : 480,
              "2/6" : 490,
              "1/6" : 540,
              "0" : 600,
              "-2/6" : 750,
              "-4/6" : 850,
              "-15" : 950,
              "-30" : 1000,
              "Promo" : 1100,
              "1S" : 5000}

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
               "-30" : 17,
               "Promo" : 19,
               "1S" : 19}

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
               "-30" : 20,
               "Promo" : 22,
               "1S" : 22}

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
          "-30" : -2,
          "Promo" : -2,
          "1S" : 1}

# calcule le V - E - 2I - 5G
def VE2I5G( classement, victoires, defaites ):
    v = len( victoires )
    e = nbInf( classement, defaites, 0 )
    i = nbInf( classement, defaites, 1 )
    g = nbInf( classement, defaites, -1 )
    return ( v - e - 2*i - 5*g )


# Calcule le nb de defaites E echelons en-dessous
def nbInf( myClassement, defaites, E ):
    global classementNumerique
    nb = 0
    for i in defaites:
        if( E >= 0 ) :
            if( classementNumerique[ i[0] ] == ( classementNumerique[ myClassement ] - E ) ):
                nb = nb+1
        else:
            if( classementNumerique[ i[0] ] < ( classementNumerique[ myClassement ] - 2 ) ):
                nb = nb+1

    return nb

# Retourne le nombre de points apportes par une victoire
def pointsVictoire( myClassement, classementBattu ):
    global classementNumerique
    global points
    diff = classementNumerique[ classementBattu ] - classementNumerique[ myClassement ]
    if( diff  < -3 ):
        return 0
    else:
        if( diff > 2 ):
            diff = 2
        return points[ diff ]

# Retourne le nombre de victoires prises en compte
def nbVictoiresComptant( myClassement, sexe, myVictoires, myDefaites ):
    global serie
    global victoiresH
    global victoiresF

    if( "H" == sexe ):
        victoires = victoiresH
    else:
        victoires = victoiresF

    nb = victoires[ myClassement ]
    v = VE2I5G( myClassement, myVictoires, myDefaites )

    print "V - E - 2I - 5G : ", v
    
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
        elif( v >= -40 and v <= 31 ):
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
        elif( v >= -80 and v <= 61 ):
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
    else: # 1S et promo
        add = 0
    return nb + add


# Calcule les points a un classement donne
def calculPoints( myClassement, sexe, myVictoires, myDefaites, nbVicChampIndiv ):
    nbV = nbVictoiresComptant( myClassement, sexe, myVictoires, myDefaites )
    sortedVictoires = sortVictoires( myVictoires )
    victoiresComptant = victoiresQuiComptent( sortedVictoires, nbV )
#    victoiresComptant = sortedVictoires[:nbV]

    print "Victoires prises en compte : ", victoiresComptant

    nbPoints = 0

    for v in victoiresComptant:
        nbPoints = nbPoints + pointsVictoire( myClassement, v )

    # Bonifs

    nb = nbWO( myVictoires )
    bonifAbsenceDefaitesPossible = ( ( len( myVictoires ) - nb ) >= 5 )

    bonif = 0

    if True == bonifAbsenceDefaitesPossible:
        global serie
        if serie[ myClassement ] == 2:
            if True == absenceDef( myDefaites, myClassement ):
                bonif =150
        if serie[ myClassement ] == 3:
            if True == absenceDef( myDefaites, myClassement ):
                bonif = 100
        if myClassement == '30/2' or myClassement == '30/1' :
            if True == absenceDef( myDefaites, myClassement ):
                bonif = 50
    if bonif != 0:
        print "bonif absence de defaite significative: ", bonif

    nbPoints = nbPoints + bonif

    if nbVicChampIndiv > 3:
        nbVicChampIndiv = 3
    bonif = nbVicChampIndiv * 15

    nbPoints = nbPoints + bonif
    if bonif != 0:
        print "bonif championnat indiv: ", bonif


    return nbPoints

# Trie les victoires par ordre decroissant
def sortVictoires( myVictoires ):
    global classementNumerique

    if 0 == len( myVictoires ):
        return []

    dicVictoires = {}
    pairVictoires = []
    sortedVictoires = []

    for v in myVictoires:
        pairVictoires.append( ( v[0], classementNumerique[ v[0] ], v[1] ) )
        dicVictoires[ v[0] ] = classementNumerique[ v[0] ]

    sortedValues = sorted( dicVictoires.values(), reverse=True ) 

    for s in sortedValues:
        for k, v, w in pairVictoires:
            if( v == s ):
                sortedVictoires.append( ( k, w ) )

    return sortedVictoires


# Teste si les points de maintien sont atteints pour le classement
def maintienOK( myClassement, mySexe, myPoints ):
    global maintienH
    global maintienF
    
    if( 'H' == mySexe ):
        maintien = maintienH
    else:
        maintien = maintienF

    print "Points acquis : ", myPoints, " - points necessaires pour le maintien a ", myClassement, " : ", maintien[ myClassement ]

    if( maintien[ myClassement ] > myPoints ):
        return False
    else:
        return True

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
    global classementNumerique

    if 0 == len( myVictoires ):
        return None

    grosse = plusGrosseVictoire( myVictoires )
    if grosse[0] == "Promo" or grosse[0] == "1S":
        return "1S"
    else:
        for( k, v ) in classementNumerique.iteritems():
            if( k == grosse ):
                for( k_, v_ ) in classementNumerique.iteritems():
                    if( v_ == v + E ):
                        return k_

# Echelon inferieur au classement d'entree
def echelonInferieur( myClassement ):
    global classementNumerique
    v = classementNumerique[ myClassement ]

    if( v == 0 ):
        return 0
    
    for( k_, v_ ) in classementNumerique.iteritems():
        if( v_ == v - 1 ):
            return k_

# Classement propose au premier tour
def classementPropose1erTour( myVictoires, myClassement ):
    global serie
    global classementNumerique

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
def normalisation( cl, sexe ):
    classement = cl[0]
    if len( classement ) < 2:
        return cl
    o = classement
    if 'N' == classement[0] and 'C' != classement[1] :
        # on est sur un numerote
        s = classement[1:]
        n = int( s )
        if 'H' == sexe:
            if n <= 30:
                o = "1S"
            else:
                o = "Promo"
        else:
            if n <= 20:
                o = "1S"
            else:
                o = "Promo"
    else:
        if "PROMO" == classement or "promo" == classement :
            o = "Promo"
    return o, cl[1]

# Conversion des numerotes en "Promo" ou "1S"
def normalisationTab( tab, sexe ):
    tabSortie = []
    for c in tab:
        o = normalisation( c, sexe )
        tabSortie.append( o )
    # Insertion de la penalite wo
    if nbWO( tab ) >= 3:
        penaliteWO( tab )
    return tabSortie

# Compter le nombre de wo
def nbWO( tab ):
    n = 0
    for t in tab:
        if t[1]:
            n = n + 1
    return n

# Insertion de la penalite wo : a partir de 3, tout wo compte comme une defaite significative
def penaliteWO( defaites ):
    _def = []
    w = 0
    for d in defaites:
        if d[1] == True:
            w = w + 1
            if w >= 3:
                o = ( 'S', d[1] )
                # on insere une defaite qu'on appelle S pour que ca compte comme une def significative
                print "Defaite significative ajoutee"
            else:
                o = d
        else:
            o = d
        _def.append( o )

    return defaites

# Absence de defaite significative ?
def absenceDef( defaites, classement ):
    global classementNumerique

    for d in defaites:
#        if 'S' != d: # on exclu les wo
        if d[1] == False:
            if( classementNumerique[ d[0] ] <= ( classementNumerique[ classement ] ) ):
                return False
    return True

# Victoires comptant : on supprime les wo
def victoiresQuiComptent( vic, nb ):
    tab = []
    for v in vic:
        if False == v[1] :
            tab.append( v[0] )
    return tab[:nb]

# Calcul du classement
def calculClassement( myVictoires, myDefaites, mySexe, myClassement, nbVicChampIndiv ):

    ok = False
    if 0 == len( victoiresQuiComptent( myVictoires, len( myVictoires ) ) ):

        if( 'NC' == myClassement ):
            return 'NC'
        else:
            return echelonInferieur( myClassement )

    myVictoires = normalisationTab( myVictoires, mySexe )
    myDefaites = normalisationTab( myDefaites, mySexe )

    myClassement = normalisation( myClassement, mySexe )

    classementPropose = classementPropose1erTour( myVictoires, myClassement )
    borneInf = echelonInferieur( myClassement ) # on ne peut pas descendre plus d'un echelon en-dessous

    while( ( False == ok ) and ( "NC" != classementPropose ) and not ( classementPropose is borneInf ) ):

        print "Classement propose : ", classementPropose

        pt = calculPoints( classementPropose, mySexe, myVictoires, myDefaites, nbVicChampIndiv )
        ok = maintienOK( classementPropose, mySexe, pt )
        if( True != ok ):
            classementPropose = echelonInferieur( classementPropose )

    # penalite WO ?
    if nbWO( myDefaites ) >= 5:
        classementPropose = echelonInferieur( classementPropose )

    print "Classement de sortie : ", classementPropose, " - classement d\' origine : ", myClassement
    return classementPropose

# TODO : if( ( serie[classement] ) == 2 or serie[classement] ) == -2 ) and VE2I5G < -100 ):
#    classement = classement - 1



def test():
    testDef = [ "30/2", "30/1", "NC", "15/2", "30/3", "30/4", "30/5", "30/3" ]
    testVic = [ "30", "30", "NC", "15/5", "15/4", "30/1", "30/3", "30/5", "N2", "N42", "N3" ]
    testCl = "30/2"
    testSexe = "H"

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

    calculClassement( testVic, testDef, testSexe, testCl, True, 2 )




def main():
    test()



if __name__ == "__main__":
    import sys
    if sys.version_info[0] != 2:
        print "Erreur -- Fonctionne avec Python 2.x"
        exit -1
    main()
