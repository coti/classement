#!/usr/bin/python

"""
 " TODO:
 " - Prise en compte des WO
 " - Prise en compte des formats courts
 " - Joli formattage de sortie
 " - Bonif championnat
  """

classementNumerique = { "NC" : 0,
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
                        "Promotion" : 24 }

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
              "Promotion" : 950 }

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
              "Promotion" : 1100 }

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
               "Promotion" : 19 }

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
               "Promotion" : 22 }

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
          "Promotion" : -2 }

# calcule le V - E - 2I - 5G
# TODO = prendre en compte les WO
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
            if( classementNumerique[ i ] == ( classementNumerique[ myClassement ] - E ) ):
                nb = nb+1
        else:
            if( classementNumerique[ i ] < ( classementNumerique[ myClassement ] - 2 ) ):
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
    return nb + add


# Calcule les points a un classement donne
def calculPoints( myClassement, sexe, myVictoires, myDefaites ):
    nbV = nbVictoiresComptant( myClassement, sexe, myVictoires, myDefaites )
    sortedVictoires = sortVictoires( myVictoires )
    victoiresComptant = sortedVictoires[:nbV]

    print "Victoires prises en compte : ", victoiresComptant

    nbPoints = 0

    for v in victoiresComptant:
        nbPoints = nbPoints + pointsVictoire( myClassement, v )

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
        pairVictoires.append( ( v, classementNumerique[ v ] ) )
        dicVictoires[ v ] = classementNumerique[ v ]

    sortedValues = sorted( dicVictoires.values(), reverse=True ) 

    for s in sortedValues:
        for k, v in pairVictoires:
            if( v == s ):
                sortedVictoires.append( k )

    return sortedVictoires


# Teste si les points de maintien sont atteints pour le classement
def maintienOK( myClassement, mySexe, myPoints ):
    global maintienH
    global maintienF
    
    if( 'H' == mySexe ):
        maintien = maintienH
    else:
        maintien = maintienF

    if( maintien[ myClassement ] > myPoints ):
        return False
    else:
        return True

# Plus gros classement battu
def plusGrosseVictoire( myVictoires ):
    if 0 == len( myVictoires ):
        return None
    sorted = sortVictoires( myVictoires )
    return sorted[0]

# Plus gros classement battu + E echelons
def plusGrosseVictoirePlusN( myVictoires, E ):
    global classementNumerique

    if 0 == len( myVictoires ):
        return None

    grosse = plusGrosseVictoire( myVictoires )
    if( len( classementNumerique.keys() ) < classementNumerique[ grosse ] + E ):
        return "Promotion"
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
def classementPropose1erTour( myVictoires ):
    global serie

    grosse = plusGrosseVictoire( myVictoires )    
    if( 4 == serie[ grosse ] ): 
        return plusGrosseVictoirePlusN( myVictoires, 2 )
    else:
        return plusGrosseVictoirePlusN( myVictoires, 1 )

# Calcul du classement
def calculClassement( myVictoires, myDefaites, mySexe, myClassement ):

    ok = False
    if 0 == len( myVictoires ):
        if( 'NC' == myClassement ):
            return 'NC'
        else:
            return echelonInferieur( myClassement )

    classementPropose = classementPropose1erTour( myVictoires )

    while( ( False == ok ) and ( "NC" != classementPropose ) ):

        print "Classement propose : ", classementPropose

        pt = calculPoints( classementPropose, mySexe, myVictoires, myDefaites )
        ok = maintienOK( classementPropose, mySexe, pt )
        if( True != ok ):
            classementPropose = echelonInferieur( classementPropose )

    print "Classement de sortie : ", classementPropose
    return classementPropose

# TODO : if( ( serie[classement] ) == 2 or serie[classement] ) == -2 ) and VE2I5G < -100 ):
#    classement = classement - 1



def test():
    testDef = [ "30/2", "30/1", "NC", "15/2", "30/3", "30/4", "30/5", "30/3" ]
    testVic = [ "30", "30", "NC", "15/5", "15/4", "30/1", "30/3", "30/5" ]
    testCl = "30/2"
    testSexe = "H"

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

    pt = calculPoints( testCl, testSexe, testVic, testDef )
    print "Points: ", pt, " - maintien: ", maintienOK( testCl, testSexe, pt )

    print "Plus gros classement battu: ", plusGrosseVictoire( testVic )
    print "Plus gros classement battu + 2: ", plusGrosseVictoirePlusN( testVic, 2 )


    print "Plus grosse victoire :", plusGrosseVictoire( testVic )

    print " - * - * - * - * - * - * - * - * - * -"

    calculClassement( testVic, testDef, testSexe, testCl )




def main():
    test()



if __name__ == "__main__":
    main()
