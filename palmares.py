#!/usr/bin/env python2.6


""" Outil de recuperation du classement.
 " (c) Camille Coti, 2013
 " Todo : 
 " Meilleure gestion des erreurs
"""


import urllib
import urllib2
import httplib
import cookielib
import re

from gaecookie import GAECookieProcessor
from keepalive import HTTPHandler

from classement import calculClassement


# Construit l'opener, l'objet urllib2 qui gere les comm http, et le cookiejar
def buildOpener():
    headers = {  "Connection" : "Keep-alive",
                 #'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.65 Safari/537.36',
                 'User-Agent' : 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/4.0.3 Safari/531.9',
                'Cache-Control' : 'max-age=0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Origin' : 'http://www.espacelic.applipub-fft.fr',
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Referer' : 'http://www.espacelic.applipub-fft.fr/espacelic/connexion.do?url=http://ww2.fft.fr/action/espace_licencies/default.asp',
                'Accept-Encoding' : 'gzip,deflate,sdch',
                'Accept-Language' : 'fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4'
                }

    policy = cookielib.DefaultCookiePolicy( rfc2965=True )
    cj = cookielib.CookieJar( policy )
    keepalive_handler = HTTPHandler()
    opener = urllib2.build_opener( keepalive_handler, GAECookieProcessor( cj )  )

    t_headers = []
    for k, v in headers.items():
        t_headers.append( ( k, v ) )
    opener.addheaders = t_headers 

    return cj, opener

# S'authentifie aupres du serveur
def authentification( login, password, opener, cj ):
    server    = "http://www.espacelic.applipub-fft.fr"
    page      = "/espacelic/connexion.do"
    payload   = { 'dispatch' : 'identifier', 'login' : login, 'motDePasse' : password }
    data      = urllib.urlencode( payload )

    # On ouvre la page d'authentification
    rep = opener.open( server+page, data )

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

    server    = "http://www.espacelic.applipub-fft.fr"
    page      = "/espacelic/private/recherchelic.do"
    payload = { 'dispatch' : 'rechercher', 'numeroLicence' : numLicence }
    data = urllib.urlencode( payload )

    rep = opener.open( server+page, data ) 
    line = rep.read()

    # on parse et on recupere le nom
    r_nom = r'<td class="r_nom">(.*)</td>'
    match = re.search( r_nom, line )
    if match:
        nom = match.group(1)
    else:
        nom = ''

    # on recupere le sexe
    r_sexe = r'<td class="r_sexe">(.*)</td>'
    match = re.search( r_sexe, line )
    if match:
        sexe = match.group(1)
    else:
        sexe = ''

    # on recupere l'id interne
    r_id = r'<a href="javascript:classement\((.*)\);">'
    match = re.search( r_id, line )
    if match:
        idu = match.group(1)
    else:
        idu = ''

    # et on recupere le classement
    r_class = r'<a href="javascript:classement\([0-9]+\);">\s*(.*)\s*</a>'
    match = re.search( r_class, line )
    if match:
        cl = match.group(1)
    else:
        cl = ''

    return nom, idu, cl, sexe

# Obtenir le palma d'un joueur d'identifiant donne
def getPalma( annee, id, opener ):
    server    = "http://www.espacelic.applipub-fft.fr"
    page      = "/espacelic/private/palmares.do"
    payload = { 'identifiant' : id, 'millesime' : annee }
    data = urllib.urlencode( payload )

    rep = opener.open( server+page, data ) 
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
    r_id = r'<a href="javascript:changerDePersonne\((.*)\);">'
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

    return nom, idu, clmt

# Calcule le classement d'un joueur
def classementJoueur( opener, id, nom, classement, sexe, profondeur ):
    V, D = getPalma( 2013, id, opener )
    myV = []
    myD = []
    print "profondeur : ", profondeur
    print "calcul du classement de ", nom

    if profondeur == 0:
        for _v in V:
            myV.append( _v[2] )
        for _d in D:
            myD.append( _d[2] )
    else:
        profondeur = profondeur - 1

        # calcul du futur classement de mes victoires
        for _v in V:
            nc = classementJoueur( opener, _v[1], _v[0], _v[2], sexe, profondeur )
            myV.append( nc )

        # calcul du futur classement de mes defaites
        for _d in D:
            nc = classementJoueur( opener, _d[1], _d[0], _d[2], sexe, profondeur )
            myD.append( nc )
            

    # calcul du classement a jour
    cl = calculClassement( myV, myD, sexe,  classement )
    print "Nouveau classement de ", nom, " : ", cl

    return cl

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

    new_cl = classementJoueur( op, id, nom, cl, sexe, profondeur )

    print "nouveau classement: ", new_cl

def main():

    import sys

    if len(sys.argv) < 5:
        login = raw_input( "Login : " )
        password = raw_input("Mot de passe : " )
        licence = int( raw_input( "Numero de licence : " ) )
        profondeur = int( raw_input( "Profondeur : " ) )
    else:
        login      = sys.argv[1]
        password   = sys.argv[2]
        licence    = int( sys.argv[3] )
        profondeur = int( sys.argv[4] )

    recupClassement( login, password, licence, profondeur )



if __name__ == "__main__":
    main()
