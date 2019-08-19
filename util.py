# coding=utf-8

from __future__ import print_function, unicode_literals

import importlib
import os
import platform
import sys
import subprocess


def confirmation():
    oui = {"oui", "o", ""}
    non = {"non", "n"}
    choix = raw_input("(oui/non) ").lower()
    if choix in oui:
        return True
    elif choix in non:
        return False
    else:
        print("Choix invalide. Entrez oui ou non.")
        return confirmation()


def exit_pause(status=0, error_message=""):
    if error_message:
        print(error_message)

    if platform.system() == "Windows" and "PROMPT" not in os.environ:
        # Si le script a été lancé en dehors de cmd (en double-cliquant), on pause l'exécution
        # pour laisser la possibilité de lire la sortie.
        # La variable PROMPT n'est présente qu'avec cmd (https://stackoverflow.com/q/558776/119323)
        raw_input("Appuyez sur une touche pour terminer")

    sys.exit(status)


def has_dependency(name):
    try:
        importlib.import_module(name)
        return True
    except ImportError:
        return False


def install_package(name):
    print("Installation du package {}".format(name))
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', name])
        print("Installation du package {} OK".format(name))
    except subprocess.CalledProcessError:
        print("Echec de l'installation du package {}".format(name))
        exit_pause(1)


def check_dependencies():
    dependencies = ('requests',)
    for package in dependencies:
        if not has_dependency(package):
            install_package(package)
