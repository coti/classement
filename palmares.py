#!/usr/bin/env python3
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

import sys

if sys.version_info[0] != 3:
    print("Erreur -- Fonctionne avec Python 3.x")
    exit(1)

import argparse
import urllib
import re
import html
import logging
import itertools
import time
import _thread
import json

from getpass import getpass
from threading import Thread
from queue import Queue
from decimal import Decimal

from classement import calculClassement
from util import *

millesime = 2019
server    = "https://tenup.fft.fr"


class Resultat(object):
    """
    :type joueur: Joueur
    """

    def __init__(self, joueur, wo, championnat, coefficient):
        self.coefficient = coefficient
        self.championnat = championnat
        self.wo = wo
        self.joueur = joueur

    def __str__(self):
        return str(self.joueur)


class Joueur(object):
    """
    :type victoires: list[Resultat]
    :type defaites: list[Resultat]
    """

    def __init__(self, nom, identifiant, classement):
        self.classement = classement
        self.classement_calcul = None
        self.identifiant = identifiant
        self.nom = nom
        self.victoires = []
        self.defaites = []
        self.calcul_fait = None

    def __str__(self):
        return "{} - {}".format(self.identifiant, self.nom)


def requete(session, url, data=None, timeout=20, retries=4):
    from requests.exceptions import HTTPError, Timeout, ConnectionError

    while retries > 0:
        logging.debug('requete: {}, data:{}, timeout: {}, retries:{}'.format(url, data, timeout, retries))
        try:
            if data is not None:
                reponse = session.post(url, data=data, timeout=timeout)
            else:
                reponse = session.get(url, timeout=timeout)
            reponse.raise_for_status()  # Lève une HTTPError si le statut n'est pas OK
            return reponse.text

        except HTTPError as e:
            print("Le serveur a répondu avec un code d'erreur:", e)
            if e.response.status_code == 403:
               print("Le serveur vous a refusé l'accès")
            elif e.response.status_code == 404:
               print("La page demandée n'existe pas. Peut-être la FFT a-t-elle changé ses adresses ?")
        except ConnectionError as e:
            print("Erreur de connection au serveur:", e)
            print("Verifiez votre connexion, ou l'état du serveur de la FFT")
        except Timeout:
            print("Timeout -- connexion impossible au serveur de la FFT")
        except KeyboardInterrupt:
            _thread.interrupt_main()
        except Exception as e:
            print("Autre exception : {} - {}".format(type(e).__name__, e))

        retries -= 1


# S'authentifie aupres du serveur
def authentification(login, password, session):
    print('Connexion au site de la FFT')

    page      = "/ajax_register/login/ajax"
    payload   = { 'form_id': 'user_login', 'name': login, 'pass': password }

    # On ouvre la page d'authentification
    rep = requete(session, server + page, data=payload, retries=2)
    if not rep:
        exit_pause(1, "Echec de chargement de la page d'authentification")

    rep_json = json.loads(rep)
    if "nom d'utilisateur ou mot de passe non reconnu" in rep_json[1]['output']:
        exit_pause(1, "L'identifiant ou le mot de passe n'est pas correct")
    if rep_json[1]['title'] != 'Connexion réussie':
        exit_pause(1, "Echec de connexion")


# Retourne l'identifiant interne d'un licencie
def getIdentifiant(session, numLicence):
    print('Récupération de l\'identifiant')

    page      = "/recherche-licencies"
    payload   = { 'numeroLicence' : numLicence }
    data      = urllib.parse.urlencode(payload)

    rep = requete(session, server + page + '?' + data, retries=2)
    if rep is None:
        exit_pause(1, "Erreur à la récupération de l'identifiant")

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
        prenom = matches[2]

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

    return nom + ' ' + prenom, idu, cl, sexe


# Obtenir le palma d'un joueur d'identifiant donne
def getPalma(annee, joueur, joueurs, session):
    """
    :type joueur: Joueur
    :type joueurs: dict[str, Joueur]
    """

    page      = "/simulation-classement/" + joueur.identifiant
    payload   = { 'millesime': annee }
    data      = urllib.parse.urlencode(payload)
    timeout   = 8

    logging.debug('getPalma ' + joueur.nom)
    start_time = time.time()
    rep = requete(session, server + page + '?' + data, timeout=timeout)
    logging.debug('getPalma {} OK ({:.0f} ms)'.format(joueur.nom, (time.time() - start_time) * 1000))

    r_ligne = r"<input type=\"hidden\" name=\"(?:victories|defeats)_part\[(?:victories|defeats)_idadversaire.*?</tr>"
    lignes = re.findall( r_ligne, rep, re.DOTALL )

    for p in lignes:	    
        r = extractInfo(p, joueurs)
        if r is None:
            continue

        # Le classement est vide pour les matchs jeunes, qui ne comptent pas
        if not r.joueur.classement:
            continue

        if 'victories' in p:
            joueur.victoires.append(r)
        elif 'defeats' in p:
            joueur.defaites.append(r)


def getPalmaRecursif(annee, joueur, session, profondeurMax):
    """
    :type joueur: Joueur
    """

    # File des joueurs dont le palmarès reste à récupérer
    q = Queue()

    # Identifiants des joueurs dont les palmarès ont été récupérés ou sont en cours de récupération
    id_palmares = set()

    # Map ID -> joueur pour n'avoir qu'un objet Joueur par joueur réel
    joueurs = {joueur.identifiant: joueur}

    def getAndEnqueue(joueur, profondeur):
        id_palmares.add(joueur.identifiant)
        getPalma(annee, joueur, joueurs, session)
        if profondeur < profondeurMax:
            for resultat in itertools.chain(joueur.victoires, joueur.defaites):
                logging.debug('enqueue {} (P={})'.format(resultat.joueur.nom, profondeur + 1))
                q.put((resultat.joueur, profondeur + 1))

    def traitement():
        while True:
            joueur, p = q.get()
            if joueur.identifiant not in id_palmares:
                getAndEnqueue(joueur, p)
            q.task_done()

    # Récupération du palmarès du joueur de départ
    print('Récupération de mon palmarès')
    getAndEnqueue(joueur, 0)

    print('Récupération des palmarès des adversaires (profondeur : {})'.format(profondeurMax))

    # Lancement des threads de traitement
    concurrence = 10
    for i in range(concurrence):
        t = Thread(target=traitement)
        t.daemon = True
        t.start()

    # Attente de la fin de tous les threads
    # q.join() empêche toute interruption par l'utilisateur, on vérifie donc plutôt
    # périodiquement si q est vide
    c = 0
    while not q.empty():
        c += 1
        if c % 5 == 0:
            print('{} palmarès restants à récupérer'.format(q.qsize()))
        time.sleep(1)

    # Même une fois q vide, il faut attendre que les derniers palmarès terminent d'être récupérés
    max_time = time.time() + 120
    while q.unfinished_tasks and time.time() < max_time:
        c += 1
        if c % 5 == 0:
            print('Attente des derniers palmarès ({})'.format(q.unfinished_tasks))
        time.sleep(1)

    if q.unfinished_tasks:
        print('{} palmarès n\'ont pas pu être récupérés'.format(q.unfinished_tasks))

    joueurs_avec_palmares = len(set(j.identifiant for j in joueurs.values() if j.victoires or j.defaites))
    print('Palmarès récupérés pour {} joueurs'.format(joueurs_avec_palmares))
    print()


# Extraire les infos d'un joueur dans un palma
def extractInfo(ligne, joueurs):
    """
    :type joueurs: dict[str, Joueur]
    """

    # id du joueur
    r_id = r'<input type="hidden" name="(?:victories|defeats)_part\[(?:victories|defeats)_idadversaire_\d+\]" value="(\d+)" />'
    id_matches = re.findall(r_id, ligne)
    if id_matches:
        idu = id_matches[0]
    else:
        return None

    r_cellule = r'<td.*?>(.*?)</td>'
    cell_matches = re.findall( r_cellule, ligne, re.DOTALL | re.MULTILINE )
    if not cell_matches:
        return None

    # Il peut y avoir des caractères spéciaux à décoder dans le nom
    nom = html.unescape(cell_matches[0]).strip() or '(anonyme)'

    # classement du joueur
    clmt = cell_matches[1]

    joueur = joueurs.setdefault(idu, Joueur(nom, idu, clmt))

    # wo ?
    w = cell_matches[4] == 'Oui'

    # championnat ?
    champ = cell_matches[5] == 'Championnat individuel'

    # Coefficient
    r_coeff = r'\(coefficient (\d\.\d+)\)'
    coeff_matches = re.findall(r_coeff, cell_matches[6])
    if coeff_matches:
        coeff = Decimal(coeff_matches[0].replace(',', '.'))
    else:
        coeff = Decimal(1)

    return Resultat(joueur, w, champ, coeff)


# Retourne le nombre de victoires en championnat individuel
def nbVictoiresChamp( tab ):
    nb = 0
    for t in tab:
        if t.championnat and not t.wo:
            nb += 1
    return nb


# Prepare une chaine mettant en forme le classement et le palma
def strClassement(joueur, classement_calcul, classement_harmonise):
    """
    :type joueur: Joueur
    """

    chaine = "Nouveau classement de {} : {} (calcul) - {} (harmonisation)\n".format(
        joueur.nom, classement_calcul, classement_harmonise)
    chaine += "Palmarès de " + joueur.nom + " :\n"
    chaine += "[Nom] [Ancien classement] [Nouveau classement] [WO] [Coeff]\n"

    def print_line(r):
        if r.joueur.classement_calcul:
            nouveau_classement = r.joueur.classement_calcul[1]
        else:
            nouveau_classement = r.joueur.classement
        return "{:24} {:5}  {:5}  {:2}  {}" \
            .format(r.joueur.nom, r.joueur.classement, nouveau_classement,
                    "WO" if r.wo else "", str(r.coefficient) if r.coefficient != 1 else "")

    chaine += " === VICTOIRES ===\n"
    if len(joueur.victoires) == 0:
        chaine += "Aucune\n"
    else:
        for v in joueur.victoires:
            chaine += print_line(v) + "\n"

    chaine += " === DÉFAITES ===\n"
    if len(joueur.defaites) == 0:
        chaine += "Aucune\n"
    else:
        for d in joueur.defaites:
            chaine += print_line(d) + "\n"
    return chaine


# Calcule le classement d'un joueur
def classementJoueur(joueur, sexe, profondeur, details_profondeur):
    """
    :param details_profondeur: Seuil de profondeur à partir duquel les détails sont affichés
    :type joueur: Joueur
    """

    if joueur.calcul_fait and joueur.calcul_fait >= profondeur:
        logging.debug("Calcul déjà fait pour {} en profondeur {} ou plus ({})".format(joueur.nom, profondeur, joueur.calcul_fait))
        nc, harm = joueur.classement_calcul
        return nc, harm, None

    myV = []
    myD = []
    # en cas de classement qui contient l'annee,
    # e.g. 'NC (2014)' -> garder uniquement la 1ere partie
    c = joueur.classement.split()
    if len(c) > 1:
        joueur.classement = c[0]

    if profondeur == 0:
        for v in joueur.victoires:
            myV.append((v.joueur.classement, v.wo, v.coefficient))
        for d in joueur.defaites:
            myD.append((d.joueur.classement, d.wo, d.coefficient))
    else:
        # calcul du futur classement de mes victoires
        for v in joueur.victoires:
            nc, harm, s = classementJoueur(v.joueur, sexe, profondeur - 1, details_profondeur)
            v.joueur.classement_calcul = (nc, harm)
            myV.append((nc, v.wo, v.coefficient))

        # calcul du futur classement de mes defaites
        for d in joueur.defaites:
            nc, harm, s = classementJoueur(d.joueur, sexe, profondeur - 1, details_profondeur)
            d.joueur.classement_calcul = (nc, harm)
            myD.append((nc, d.wo, d.coefficient))

    impression = profondeur >= details_profondeur

    if impression:
        print("Calcul du classement de {} (profondeur {})".format(joueur.nom, profondeur))

    # nb de victoires en championnat indiv
    champ = nbVictoiresChamp(joueur.victoires)
    if impression:
        print(champ, "victoire(s) en championnat individuel")

    # calcul du classement a jour
    cl, harm = calculClassement(myV, myD, sexe, joueur.classement, champ, impression)

    if impression:
        # sorties
        s = strClassement(joueur, cl, harm)
        print(s)
    else:
        s = None

    joueur.calcul_fait = profondeur
    return cl, harm, s


def recupClassement( login, password, LICENCE, profondeur, details_profondeur=0 ):
    """
    :param profondeur: Le niveau de profondeur maximum du calcul
    :param details_profondeur: Le nombre de niveaux de profondeur pour lesquels on veut afficher les détails
        (0: seulement le résultat final)
    :return:
    """

    import requests
    session = requests.session()

    # On s'identifie et on obtient ses prores infos
    authentification(login, password, session)

    nom, id, cl, sexe = getIdentifiant(session, LICENCE )

    if id == '':
        exit_pause(1, "Impossible de récupérer l'identifiant")

    print(nom)
    print(cl)
    print(sexe)
    print()

    joueur = Joueur(nom, id, cl)

    # recuperation de son propre palma, et recursivement de celui des autres
    getPalmaRecursif(millesime, joueur, session, profondeur)

    # calcul du nouveau classement
    new_cl, harm, s = classementJoueur(joueur, sexe, profondeur,
                                       profondeur - min(details_profondeur, profondeur))

    print("Nouveau classement: ", harm, " (après harmonisation) - ", new_cl, " (calculé)")

    # on crache la sortie du joueur dans un fichier
    fn = "{}_{}_p{}.txt".format(LICENCE, nom, profondeur)
    fd = open( fn, "w" )
    fd.write(s)
    fd.close()

    return


# Prend le numero de licence tel qu'il est retourne par raw_input, vire l'eventuel lettre finale, rajoute des 0 si
# ils ont ete perdus
def trimNumLicence(s):
    match = re.match(r"(\d{1,7})[a-zA-Z]?$", s)
    if not match:
        return None
    numero = match.group(1)
    return "0" * max(0, 7 - len(numero)) + numero


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("login", nargs="?", default=None)
    parser.add_argument("password", nargs="?", default=None)
    parser.add_argument("licence", nargs="?", default=None)
    parser.add_argument("profondeur", nargs="?", default=None, type=int)
    parser.add_argument("-f", "--force", action="store_true",
                        help="Désactive le message de confirmation en cas de profondeur élevée")
    parser.add_argument("-d", "--details", type=int, default=0,
                        help="Le nombre de niveaux de profondeurs pour lesquels on veut afficher"
                             "le détail du calcul. Par défaut : 0 (le résultat final uniquement)")
    parser.add_argument('-v', '--verbeux', action='store_true', default=False)
    args = parser.parse_args()

    if args.verbeux:
        logging.basicConfig(level=logging.DEBUG)

    login = args.login if args.login else input("Identifiant : ")
    password = args.password if args.password else getpass("Mot de passe : ")

    licence = trimNumLicence(args.licence if args.licence else input("Numero de licence : "))
    if licence is None:
        print("Erreur de saisie du numéro de licence")
        return -1

    try:
        profondeur = args.profondeur if args.profondeur is not None else int(input("Profondeur : "))
    except:
        print('Erreur de saisie de la profondeur')
        return -1

    if profondeur > 2 and not args.force:
        print("Vous avez choisi une profondeur importante ({}).\n"
              "Cela va générer un très grand nombre de requêtes au site de la FFT.\n"
              "Êtes-vous sûr de vouloir continuer ?".format(profondeur))
        if not confirmation():
            return -1

    recupClassement(login, password, licence, profondeur, args.details)
    return


if __name__ == "__main__" :
    check_dependencies()

    try:
        main()
    except KeyboardInterrupt:
        print("Interruption par l'utilisateur")

    exit_pause()
