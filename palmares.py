#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Outil de recuperation du classement.
 "
 " :copyright: Copyright 2013-2015, see AUTHORS 
 "             Copyright 2013-2014, voir AUTHORS
 " :licence: CeCILL-C or LGPL, see COPYING for details.
 "           CeCILL-C ou LGPL, voir COPYING pour plus de details.
 "
 "
 "
 " Todo : 
 " Meilleure gestion des erreurs
"""


import urllib
import urllib2
import httplib
import cookielib
import re
import socket

from gaecookie import GAECookieProcessor
from urlgrabber import keepalive

from classement import calculClassement, penaliteWO, nbWO

server    = "https://edl.app.fft.fr"

# Construit l'opener, l'objet urllib2 qui gere les comm http, et le cookiejar
def buildOpener():
    global server
    headers = {  "Connection" : "Keep-alive",
                 #'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.65 Safari/537.36',
                 'User-Agent' : 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/4.0.3 Safari/531.9',
                'Cache-Control' : 'max-age=0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Origin' : server,
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Referer' : server + 'espaceclic/connection.do',
                'Accept-Encoding' : 'gzip,deflate,sdch',
                'Accept-Language' : 'fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4'
                }

    policy = cookielib.DefaultCookiePolicy( rfc2965=True )
    cj = cookielib.CookieJar( policy )
    keepalive_handler = keepalive.HTTPSHandler( )
    try:
        opener = urllib2.build_opener( keepalive_handler, GAECookieProcessor( cj )  )
    except urllib2.URLError as e:
        print "URL error"
        if hasattr(e, 'reason'):
            print 'Serveur inaccessible.'
            print 'Raison : ', e.reason
        if hasattr(e, 'code'):
            print 'Le serveur n\'a pas pu répondre à la requete.'
            print 'Code d\'erreur : ', e.code
            if e.code == 403:
                print 'Le serveur vous a refusé l\'accès'
            if e.code == 404:
                print 'La page demandée n\'existe pas. Peut-être la FFT a-t-elle changé ses adresses ?'
        exit( -1 )
    except urllib2.HTTPError as e:
        print "HTTP error code ", e.code, " : ", e.reason
        print "Vérifiez votre connexion, ou l\'état du serveur de la FFT"
        exit( -1 )
    except:
        import sys
        print "Build opener : Autre exception : ", sys.exc_type, sys.exc_value
        exit( -1 )

    t_headers = []
    for k, v in headers.items():
        t_headers.append( ( k, v ) )
    opener.addheaders = t_headers 

    return cj, opener

def requete( opener, url, data, timeout=60 ):
    try:
        rep = opener.open( url, data, timeout )
        return rep
    except urllib2.URLError as e:
        print "URL error:", e.reason
        print "Verifiez votre connexion, ou l\'état du serveur de la FFT"
        if hasattr(e, 'reason'):
            print 'Serveur inaccessible.'
            print 'Raison : ', e.reason
        if hasattr(e, 'code'):
            print 'Le serveur n\'a pas pu répondre à la requete.'
            print 'Code d\'erreur : ', e.code
            if e.code == 403:
                print 'Le serveur vous a refusé l\'accès'
            if e.code == 404:
                print 'La page demandée n\'existe pas. Peut-être la FFT a-t-elle changé ses adresses ?'
        exit( -1 )
    except socket.timeout as e:
        print "Timeout -- connexion impossible au serveur de la FFT"
        print "Verifiez votre connexion, ou l\'etat du serveur de la FFT"
        exit( -1 )
    except:
        import sys
        print "Autre exception : ", sys.exc_type, sys.exc_value
        exit( -1 )

# S'authentifie aupres du serveur
def authentification( login, password, opener, cj ):
    global server
    page      = "/espacelic/connexion.do"
    payload   = { 'dispatch' : 'identifier', 'login' : login, 'motDePasse' : password }
    data      = urllib.urlencode( payload )
    timeout   = 60

    # On ouvre la page d'authentification
    requete( opener, server + page, data, timeout )

    # On recupere alors les cookies, donc on les insere dans l'en-tete http
    cookietab = []
    for c in cj:
        cookietab.append( c.name + '=' + c.value )
    myCookie = '; '.join( cookietab )

    opener.addheaders.append( ( "Cache-Control", "no-cache=\"set-cookie, set-cookie2\"" ) )
    opener.addheaders.append( ( "Cookie", myCookie ) )
    
    return

# Retourne l'identifiant interne d'un licencie
def getIdentifiant( opener, numLicence ):

    global server
    page      = "/espacelic/private/recherchelic.do"
    payload   = { 'dispatch' : 'rechercher', 'numeroLicence' : numLicence }
    data      = urllib.urlencode( payload )
    timeout   = 60

    rep = requete( opener, server+page, data, timeout )
    line = rep.read()

    # on parse et on recupere le nom
    r_nom = r'<td class="r_nom">\s*(.*?)\s*</td>'
    match = re.search( r_nom, line )
    if match:
        nom = match.group(1)
    else:
        nom = ''

    # on recupere le sexe
    r_sexe = r'<td class="r_sexe">\s*(.*?)\s*</td>'
    match = re.search( r_sexe, line )
    if match:
        sexe = match.group(1)
    else:
        sexe = ''

    # on recupere l'id interne
    r_id = r'<a href="javascript:classement\((.*?)\);">'
    match = re.search( r_id, line )
    if match:
        idu = match.group(1)
    else:
        idu = ''

    # et on recupere le classement
    r_class = r'<a href="javascript:classement\([0-9]+\);">\s*(.*?)\s*</a>'
    match = re.search( r_class, line )
    if match:
        cl = match.group(1)
        print "classement: ", cl
    else:
        cl = ''

    return nom, idu, cl, sexe

# Obtenir le palma d'un joueur d'identifiant donne
def getPalma( annee, id, opener ):
    global server
    page      = "/espacelic/private/palmares.do"
    payload = { 'identifiant' : id, 'millesime' : annee }
    data = urllib.urlencode( payload )

    rep = requete( opener, server+page, data )
    line = rep.read()

    # Separation victoires/defaites

    r_limite = r'<th colspan="11" class="titre">(.*?)<th colspan="11" class="titre">(.*?)</tbody>'
    results = re.findall( r_limite, line, re.S|re.M )[0]
    victoires = results[0]
    defaites = results[1]

    r_player = r'<tr>(.*?)</tr>'
    tab_vic = re.findall( r_player, victoires, re.S|re.M )
    tab_def = re.findall( r_player, defaites, re.S|re.M )

    V = []
    for p in tab_vic:
        r = extractInfo( p )
        if '' not in r:
            V.append( r )
    print V

    D = []
    for p in tab_def:
        r = extractInfo( p )
        if '' not in r:
            D.append( r )
    print D

    return V, D

# Extraire les infos d'un joueur dans un palma
def extractInfo( ligne ):

    # id du joueur
    r_id = r'<a href="javascript:changerDePersonne\((.*?)\);">'
    match = re.search( r_id, ligne )
    if match:
        idu = match.group(1)
    else:
        idu = ''

    # nom du joueur
    r_nom = r'<a href="javascript:changerDePersonne\([0-9]+\);">\s*(.*?)\s*</a>'
    match = re.search( r_nom, ligne )
    if match:
        nom = match.group(1)
    else:
        nom = ''

    # classement du joueur
    r_class = r'<a href="javascript:classement\([0-9]*\);">\s*(.*?)\s*</a>'
    match = re.search( r_class, ligne )
    if match:
        clmt = match.group(1)
    else:
        clmt = ''
        
    # wo ?
    r_wo = r'<td class="wo" >(.*?)</td>'
    match = re.search( r_wo, ligne )
    w = False
    if match:
        wo = match.group(1)
        if 'o' == wo or 'O' == wo:
            print "WO ", nom, wo
            w = True

    # championnat ?
    r_type = r'<td class="typeHomol"\s*>\s*(.*?)\s*</td>'
    match = re.search( r_type, ligne )
    champ = False
    if match:
        c = match.group(1)
        if 'C' == c or 'c' == c:
            print "Victoire en championnat indiv contre ", nom, c
            champ = True

    return nom, idu, clmt, w, champ

# Retourne le nombre de victoires en championnat individuel
def nbVictoiresChamp( tab ):
    nb = 0
    for t in tab:
        if t[4]:
            nb = nb + 1
    return nb

# Prepare une chaine mettant en forme le classement et le palma
def strClassement( nom, classement, harmonise, palmaV, palmaD ):
    chaine = "Nouveau classement de " + nom + " : " + classement + "(calcul)" + harmonise + "(harmonisation)\n"
    chaine += "Palmarès de " + nom + " :\n"
    chaine += "[Nom] [Ancien classement] [Nouveau classement] [WO]\n"
    chaine += " === VICTOIRES ===\n"
    if len( palmaV ) == 0:
        chaine += "Aucune\n"
    else:
        for _v in palmaV:
            if True == _v[3] :
                o = ( _v[0],_v[1], _v[2], "WO" ) 
                chaine += "\t".join( o )
                chaine += "\n"
            else:
                o = ( _v[0],_v[1], _v[2] ) 
                chaine += "\t".join( o )
                chaine += "\n"
    chaine += " === DÉFAITES ===\n"
    if len( palmaD ) == 0:
        chaine += "Aucune"
    else:
        for _d in palmaD:
            if True == _d[3] :
                o = ( _d[0],_d[1], _d[2], "WO" ) 
            else:
                o = ( _d[0],_d[1], _d[2] ) 
            chaine += "\t".join( o )
            chaine += "\n"
    return chaine

# Calcule le classement d'un joueur
def classementJoueur( opener, id, nom, classement, sexe, profondeur ):
    V, D = getPalma( 2015, id, opener )
    myV = []
    myD = []
    palmaV = []
    palmaD = []
    print "profondeur : ", profondeur
    print "calcul du classement de ", nom

    # en cas de classement qui contient l'annee,
    # e.g. 'NC (2014)' -> garder uniquement la 1ere partie
    c = classement.split( )
    if len( c ) > 1:
        classement = c[0]

    # nb de victoires en championnat indiv
    champ = nbVictoiresChamp( V )
    print champ, " victoire(s) en championnat individuel"

    if profondeur == 0:
        for _v in V:
            myV.append( ( _v[2], _v[3] ) )
            palmaV.append( ( _v[0], _v[2], _v[2], _v[3] ) )
        for _d in D:
            myD.append( ( _d[2], _d[3] ) )
            palmaD.append( ( _d[0], _d[2], _d[2], _d[3] ) )
    else:
        profondeur = profondeur - 1

        # calcul du futur classement de mes victoires
        for _v in V:
            nc,harm,s = classementJoueur( opener, _v[1], _v[0], _v[2], sexe, profondeur )
            myV.append( ( nc, _v[3] ) )
            palmaV.append( ( _v[0], _v[2], nc, _v[3] ) )

        # calcul du futur classement de mes defaites
        for _d in D:
            nc,harm,s = classementJoueur( opener, _d[1], _d[0], _d[2], sexe, profondeur )
            myD.append( ( nc, _d[3] ) )
            palmaD.append( ( _d[0], _d[2], nc, _d[3] ) )

    # calcul du classement a jour
    cl,harm = calculClassement( myV, myD, sexe,  classement, champ )

    # sorties
    s = strClassement( nom, cl, harm, palmaV, palmaD )
    print s

    return ( cl, harm, s )

def recupClassement( login, password, LICENCE, profondeur ):
    
    # On s'identifie et on obtient ses prores infos
    cj, op = buildOpener()
    authentification( login, password, op, cj )

    nom, id, cl, sexe = getIdentifiant( op, LICENCE )
    print nom
    print id
    print cl
    print sexe

    # recuperation de son propre palma, et recursivement de celui des autres

    new_cl, harm, s = classementJoueur( op, id, nom, cl, sexe, profondeur )

    print "nouveau classement: ", harm, " (après harmonisation) - ", new_cl, " (calculé)"

    # on crache la sortie du joueur dans un fichier
    fn = str( LICENCE ) + ".txt"
    fd = open( fn, "w" )
    fd.write( s )
    fd.close()

    return

# Prend le numero de licence tel qu'il est retourne par raw_input, vire l'eventuel lettre finale, rajoute des 0 si ils ont ete perdus
def trimNumLicence( s ) :
    i = -1
    try:
        i = int( s )
    except:
        try:
            i = int( s[:-1] )
        except:
            print "Problème avec le numero de licence"
    l = str( i )
    if len( l ) < 7:
        for k in range( 0, 7 - len( l ) ):
            l = '0'+l
    return l

def main():

    import sys

    if len(sys.argv) < 5:
        login = raw_input( "Login : " )
        password = raw_input("Mot de passe : " )
        licence = trimNumLicence( raw_input( "Numero de licence : " ) )
        if -1 == licence:
            print "Erreur fatale -- Fin de l\'execution"
            return -1
        try:
            profondeur = int( raw_input( "Profondeur : " ) )
        except:
            print "Erreur de saisie de la profondeur."
            print "Erreur fatale -- Fin de l\'execution"
            return -1
    else:
        login      = sys.argv[1]
        password   = sys.argv[2]
        licence = trimNumLicence( sys.argv[3] )
        if -1 == licence:
            print "Erreur fatale -- Fin de l\'execution"
            return -1
        try:
            profondeur = int( sys.argv[4])
        except:
            print "Erreur de saisie de la profondeur."
            print "Erreur fatale -- Fin de l\'execution"
            return -1

    recupClassement( login, password, licence, profondeur )
    return


if __name__ == "__main__" :
    import sys
    if sys.version_info[0] != 2:
        print "Erreur -- Fonctionne avec Python 2.x"
        exit -1
    main()
