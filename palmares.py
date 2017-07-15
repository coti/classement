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


from __future__ import print_function, unicode_literals

import urllib
import urllib2
import cookielib
import re
import socket
import HTMLParser
import logging
import sys
import itertools
import time
import thread

from _ssl import SSLError
from threading import Thread
from Queue import Queue
from collections import namedtuple
from decimal import Decimal

from gaecookie import GAECookieProcessor
from urlgrabber import keepalive

from classement import calculClassement, penaliteWO, nbWO

millesime = 2017
server    = "https://mon-espace-tennis.fft.fr"

Resultat = namedtuple('Resultat', 'nom, identifiant, classement, wo, championnat, coefficient')


# Construit l'opener, l'objet urllib2 qui gere les comm http, et le cookiejar
def buildOpener():
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
        print("URL error")
        if hasattr(e, 'reason'):
            print('Serveur inaccessible.')
            print('Raison : ', e.reason)
        if hasattr(e, 'code'):
            print('Le serveur n\'a pas pu répondre à la requete.')
            print('Code d\'erreur : ', e.code)
            if e.code == 403:
                print('Le serveur vous a refusé l\'accès')
            if e.code == 404:
                print('La page demandée n\'existe pas. Peut-être la FFT a-t-elle changé ses adresses ?')
        exit( -1 )
    except urllib2.HTTPError as e:
        print("HTTP error code ", e.code, " : ", e.reason)
        print("Vérifiez votre connexion, ou l\'état du serveur de la FFT")
        exit( -1 )
    except:
        print("Build opener : Autre exception : ", sys.exc_type, sys.exc_value)
        exit( -1 )

    t_headers = []
    for k, v in headers.items():
        t_headers.append( ( k, v ) )
    opener.addheaders = t_headers 

    return cj, opener

def requete( opener, url, data, timeout=60 ):
    if data is not None:
        data = urllib.urlencode(data)

    # Le timeout donné à opener.open n'est pas respecté. Il faut définir le default socket timeout
    # qui par défaut est infini
    socket.setdefaulttimeout(timeout)

    retries = 5
    while retries > 0:
        retries -= 1
        try:
            logging.debug('requete: {}, data:{}, timeout: {}, retries:{}'.format(url, data, timeout, retries))
            rep = opener.open( url, data, timeout )
            return rep.read().decode('utf-8')
        except urllib2.URLError as e:
            print("Verifiez votre connexion, ou l\'état du serveur de la FFT")
            if hasattr(e, 'reason'):
                print('Serveur inaccessible.')
                print('Raison : ', ''.join(e.reason))
            if hasattr(e, 'code'):
                print('Le serveur n\'a pas pu répondre à la requete.')
                print('Code d\'erreur : ', e.code)
                if e.code == 403:
                    print('Le serveur vous a refusé l\'accès')
                if e.code == 404:
                    print('La page demandée n\'existe pas. Peut-être la FFT a-t-elle changé ses adresses ?')
        except socket.timeout as e:
            print("Timeout -- connexion impossible au serveur de la FFT")
        except SSLError as e:
            if e.message == 'The read operation timed out':
                # On reçoit cette exception en cas de timeout, pas la peine de la montrer
                # à l'utilisateur
                logging.debug("{} {}".format(sys.exc_type.__name__, e.message))
            else:
                print("Autre exception : {} - {}".format(type(e).__name__, e.message))
        except KeyboardInterrupt:
            thread.interrupt_main()
        except Exception as e:
            print("Autre exception : {} - {}".format(type(e).__name__, e.message))


# S'authentifie aupres du serveur
def authentification( login, password, opener, cj ):
    print('Connexion au site de la FFT')

    page      = "/ajax_register/login/ajax"
    payload   = { 'form_id': 'user_login', 'name': login, 'pass': password }
    timeout   = 20

    # On ouvre la page d'authentification
    rep = requete( opener, server + page, payload, timeout )
    if rep is None:
        print("Erreur à l'authentification")
        exit(-1)

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
    print('Récupération de l\'identifiant')

    page      = "/recherche-joueur"
    payload   = { 'numeroLicence' : numLicence }
    data      = urllib.urlencode( payload )
    timeout   = 20

    rep = requete( opener, server+page+'?'+data, None, timeout )
    if rep is None:
        print("Erreur à la récupération de l'identifiant")
        exit(-1)

    vide = ('', '', '', '')

    r_tableau = r'<tbody>.*</tbody>'
    match = re.search( r_tableau, rep, re.DOTALL )
    if match:
        tableau = match.group()
    else:
        return vide

    r_cellule = r'<td>(.*?)</td>'
    matches = re.findall( r_cellule, tableau, re.DOTALL )
    if matches:
        sexe = matches[0]
        nom = matches[1]

        # id interne
        r_idu = r'<a href="/palmares/(\d+)">.+</a>'
        match = re.match( r_idu, matches[8] )
        if match:
            idu = match.group(1)
        else:
            return vide

        # classement
        r_class = r'<a href="/classement/\d+">(.+)</a>'
        match = re.match( r_class, matches[4] )
        if match:
            cl = match.group(1)
        else:
            cl = 'NC'
    else:
        return vide

    print("classement: ", cl)

    return nom, idu, cl, sexe


# Obtenir le palma d'un joueur d'identifiant donne
def getPalma( annee, id, opener ):
    page      = "/simulation-classement/" + id
    payload   = { 'millesime': annee }
    data      = urllib.urlencode( payload )
    timeout   = 8

    logging.debug('getPalma ' + id)
    rep = requete( opener, server+page+'?'+data, None, timeout )
    logging.debug('getPalma ' + id + ' OK')

    r_ligne = r"<tr><td>.*?<input type=\"hidden\" name=\"(?:victories|defeats)_part\[(?:victories|defeats)_idadversaire.*?</tr>"
    lignes = re.findall( r_ligne, rep, re.DOTALL )

    V = []
    D = []

    for p in lignes:
        r = extractInfo( p )
        if r is None:
            continue

        # On élimine les matchs jeunes
        if r.classement.startswith('Niveau'):
            continue

        if 'victories' in p:
            V.append( r )
        elif 'defeats' in p:
            D.append( r )

    return V, D


def getPalmaRecursif(annee, identifiant, opener, profondeurMax):

    q = Queue()
    palmaresJoueurs = {}

    def getAndEnqueue(idJoueur, profondeur):
        V, D = getPalma(annee, idJoueur, opener)
        palmaresJoueurs[idJoueur] = (V, D)
        if profondeur < profondeurMax:
            for resultat in itertools.chain(V, D):
                if resultat.identifiant is not None:
                    logging.debug('enqueue {} (P={})'.format(resultat.identifiant, profondeur + 1))
                    q.put((resultat.identifiant, profondeur + 1))

    def traitement():
        while True:
            idJoueur, p = q.get()
            if idJoueur not in palmaresJoueurs:
                getAndEnqueue(idJoueur, p)
            q.task_done()

    # Récupération du palmarès du joueur de départ
    print('Récupération de mon palmarès')
    getAndEnqueue(identifiant, 0)

    print('Récupération des palmarès des adversaires')

    # Lancement des threads de traitement
    concurrence = 10
    for i in range(concurrence):
        t = Thread(target=traitement)
        t.daemon = True
        t.start()

    # Attente de la fin de tous les threads
    # q.join() empêche toute interruption par l'utilisateur, on vérifie donc
    # périodiquement si q est vide
    c = 0
    while not q.empty():
        c += 1
        if c % 5 == 0:
            print('{} palmarès restants à récupérer'.format(q.qsize()))
        time.sleep(1)

    # Même une fois q vide, il faut attendre que les derniers palmarès soient récupérés
    print('Attente des derniers palmarès')
    q.join()

    print('Palmarès récupérés pour {} joueurs'.format(len(palmaresJoueurs)))
    return palmaresJoueurs


# Extraire les infos d'un joueur dans un palma
def extractInfo( ligne ):

    # id du joueur
    r_id = r'<input type="hidden" name="(?:victories|defeats)_part\[(?:victories|defeats)_idadversaire_\d+\]" value="(\d+)" />'
    id_matches = re.findall( r_id, ligne )
    if id_matches:
        idu = id_matches[0]
    else:
        return None

    r_cellule = r'<td.*?>(.*?)</td>'
    cell_matches = re.findall( r_cellule, ligne, re.DOTALL | re.MULTILINE )
    if not cell_matches:
        return None

    # Il peut y avoir des caractères spéciaux à décoder dans le nom
    nom = HTMLParser.HTMLParser().unescape(cell_matches[1]).strip() or '(anonyme)'

    # classement du joueur
    clmt = cell_matches[2]

    # wo ?
    w = cell_matches[4] == 'Oui'

    # championnat ?
    champ = cell_matches[5] == 'Championnat individuel'

    # Coefficient
    r_coeff = r'\(Coef\. (\d,\d+)\)'
    coeff_matches = re.findall(r_coeff, cell_matches[6])
    if coeff_matches:
        coeff = Decimal(coeff_matches[0].replace(',', '.'))
    else:
        coeff = Decimal(1)

    return Resultat(nom, idu, clmt, w, champ, coeff)


# Retourne le nombre de victoires en championnat individuel
def nbVictoiresChamp( tab ):
    nb = 0
    for t in tab:
        if t.championnat:
            nb += 1
    return nb


# Prepare une chaine mettant en forme le classement et le palma
def strClassement( nom, classement, harmonise, palmaV, palmaD ):
    chaine = "Nouveau classement de " + nom + " : " + classement + " (calcul) - " + harmonise + " (harmonisation)\n"
    chaine += "Palmarès de " + nom + " :\n"
    chaine += "[Nom] [Ancien classement] [Nouveau classement] [WO] [Coeff]\n"

    def print_line(m):
        return "{:24} {:5}  {:5}  {:2}  {}" \
            .format(m[0], m[1], m[2],
                    "WO" if m[3] else "", str(m[4]) if m[4] != 1 else "")

    chaine += " === VICTOIRES ===\n"
    if len( palmaV ) == 0:
        chaine += "Aucune\n"
    else:
        for _v in palmaV:
            chaine += print_line(_v) + "\n"

    chaine += " === DÉFAITES ===\n"
    if len( palmaD ) == 0:
        chaine += "Aucune"
    else:
        for _d in palmaD:
            chaine += print_line(_d) + "\n"
    return chaine


# Calcule le classement d'un joueur
def classementJoueur( palmaresJoueurs, id, nom, classement, sexe, profondeur ):

    # Pour les joueurs anonymes ou dont le palmarès est manquant on renvoie le classement d'origine
    if id is None or id not in palmaresJoueurs:
        return classement, classement, ''

    V, D = palmaresJoueurs[id]
    myV = []
    myD = []
    palmaV = []
    palmaD = []
    print("profondeur : ", profondeur)
    print("calcul du classement de ", nom)

    # en cas de classement qui contient l'annee,
    # e.g. 'NC (2014)' -> garder uniquement la 1ere partie
    c = classement.split( )
    if len( c ) > 1:
        classement = c[0]

    # nb de victoires en championnat indiv
    champ = nbVictoiresChamp( V )
    print(champ, " victoire(s) en championnat individuel")

    if profondeur == 0:
        for _v in V:
            myV.append( ( _v.classement, _v.wo, _v.coefficient ) )
            palmaV.append( ( _v.nom, _v.classement, _v.classement, _v.wo, _v.coefficient ) )
        for _d in D:
            myD.append( ( _d.classement, _d.wo, _d.coefficient ) )
            palmaD.append( ( _d.nom, _d.classement, _d.classement, _d.wo, _d.coefficient ) )
    else:
        profondeur -= 1

        # calcul du futur classement de mes victoires
        for _v in V:
            nc,harm,s = classementJoueur( palmaresJoueurs, _v.identifiant, _v.nom, _v.classement, sexe, profondeur )
            myV.append( ( nc, _v.wo, _v.coefficient ) )
            palmaV.append( ( _v.nom, _v.classement, nc, _v.wo, _v.coefficient ) )

        # calcul du futur classement de mes defaites
        for _d in D:
            nc,harm,s = classementJoueur( palmaresJoueurs, _d.identifiant, _d.nom, _d.classement, sexe, profondeur )
            myD.append( ( nc, _d.wo, _d.coefficient ) )
            palmaD.append( ( _d.nom, _d.classement, nc, _d.wo, _d.coefficient ) )

    # calcul du classement a jour
    cl,harm = calculClassement( myV, myD, sexe,  classement, champ )

    # sorties
    s = strClassement( nom, cl, harm, palmaV, palmaD )
    print(s)

    return ( cl, harm, s )


def recupClassement( login, password, LICENCE, profondeur ):
    
    # On s'identifie et on obtient ses prores infos
    cj, op = buildOpener()
    authentification( login, password, op, cj )

    nom, id, cl, sexe = getIdentifiant( op, LICENCE )

    if id == '':
        print("Impossible de récupérer l'identifiant")
        exit(1)

    print(nom)
    print(id)
    print(cl)
    print(sexe)

    # recuperation de son propre palma, et recursivement de celui des autres
    palmaresJoueurs = getPalmaRecursif(millesime, id, op, profondeur)

    # calcul du nouveau classement
    new_cl, harm, s = classementJoueur( palmaresJoueurs, id, nom, cl, sexe, profondeur )

    print("nouveau classement: ", harm, " (après harmonisation) - ", new_cl, " (calculé)")

    # on crache la sortie du joueur dans un fichier
    fn = str( LICENCE ) + ".txt"
    fd = open( fn, "w" )
    fd.write( s.encode('utf-8') )
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
            print("Problème avec le numero de licence")
    l = str( i )
    if len( l ) < 7:
        for k in range( 0, 7 - len( l ) ):
            l = '0'+l
    return l


def main():
    if len(sys.argv) < 5:
        login = raw_input( "Login : " )
        password = raw_input("Mot de passe : " )
        licence = trimNumLicence( raw_input( "Numero de licence : " ) )
        if -1 == licence:
            print("Erreur fatale -- Fin de l\'execution")
            return -1
        try:
            profondeur = int( raw_input( "Profondeur : " ) )
        except:
            print("Erreur de saisie de la profondeur.")
            print("Erreur fatale -- Fin de l\'execution")
            return -1
    else:
        login      = sys.argv[1]
        password   = sys.argv[2]
        licence = trimNumLicence( sys.argv[3] )
        if -1 == licence:
            print("Erreur fatale -- Fin de l\'execution")
            return -1
        try:
            profondeur = int( sys.argv[4])
        except:
            print("Erreur de saisie de la profondeur.")
            print("Erreur fatale -- Fin de l\'execution")
            return -1

    recupClassement( login, password, licence, profondeur )
    return


if __name__ == "__main__" :
    if sys.version_info[0] != 2:
        print("Erreur -- Fonctionne avec Python 2.x")
        exit( -1 )

    try:
        main()
    except KeyboardInterrupt:
        print("Interruption par l'utilisateur")
