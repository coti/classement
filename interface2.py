#!/usr/bin/env python3
#coding: utf8

""" Outil de recuperation du classement: interface graphique.
 "
 " :copyright: Copyright 2018, see AUTHORS 
 "             Copyright 2018, voir AUTHORS
 " :licence: CeCILL-C or LGPL, see COPYING for details.
 "           CeCILL-C ou LGPL, voir COPYING pour plus de details.
 "
 " Version très très très alpha.
"""

import sys

if sys.version_info[0] != 3:
    print("Erreur -- Fonctionne avec Python 3.x")
    exit(1)

import threading
import tkinter as tk
import queue
import signal
import platform
import palmares
# import palmares_dummy as palmares
from util import check_dependencies, exit_pause

# Global variables, uggly but avoids a wrapper or a functor
# or a higher level function or whatever
login_entr = None
mdp_entr = None
lic_entr = None
prof_entr = None

worker = None
root = None

# What happens when the button is clicked.
# (Main stuff is here)

def start( ):
    global login_entr
    global mdp_entr
    global lic_entr
    global prof_entr
    global root
    global worker

    # On récupère les paramètres de l'utilisateur
 
    login = login_entr.get()
    mdp =  mdp_entr.get()
    lic = lic_entr.get()
    prof_s =  prof_entr.get()

    # Check the depth is an integer (or can be converted to an int)
    try:
        prof = int( prof_s )
    except ValueError:
        print( "la profondeur n'est pas un entier" )
        popProfondeur()
        return

    # Le calcul va afficher des choses sur la sortie standard.
    # Pour que ça soit plus convivial, afficher ça dans une fenêtre.

    root = tk.Tk()
    root.wm_title( "Calcul du classement en cours" )
    output = ThreadSafeText( root )
    output.pack()
    sys.stdout = Std_redirector( output )

    # Bouton ok pour la fin du calcul, bouton stop pour tuer avant

    stop = tk.Button( root, text = "Stop", command = stopThread )
    stop.pack()
    """
    ok = tk.Button( root, text = "Ok", command = endThread )
    ok.pack()
    """
    
    # Et enfin on appelle la fonction qui fait le calcul
    
    worker = threading.Thread( target = wrapperFunction, args = ( login, mdp, lic, prof ) )
    worker.daemon = True
    worker.start()
    
    # Affichage
    
    root.mainloop()
    
    worker.join()
    root.destroy()
        
    return

# J'ai fait ce wrapper au cas où on voudrait mettre des trucs
# genre de la gestion d'exceptions avec un gros try/catch autour de l'appel

def wrapperFunction( login, mdp, lic, prof ):
    palmares.recupClassement( login, mdp, lic, prof )
    return

# J'ai fait ces deux cas pour avoir typiquement
# - un bouton stop qui arrête le thread en background
# - un bouton ok qui ferme la fenêtre une fois que c'est terminé

def endThread():
    global root
    global worker

    worker.join()
    root.destroy
    del sys.stdout
    sys.stdout = sys.__stdout__
    return

def stopThread():
    import signal
    import os
    ## Ceci ne fait rien du tout
    ## worker._Thread__stop()
    ## Donc méthode du bœuf.
    #os.kill( os.getpid(), signal.SIGKILL )
    os.kill( os.getpid(), signal.SIGUSR1 )
    worker.join()
    root.quit()
    return
    
# Used to communicate with authority b/w the threads

def sighandler( signum, frame ):
    print( "Caught signal" )
    #    sys.exit()
    import _thread
    _thread.exit()
    #raise ExitThreadNow

class ExitThreadNow( Exception ):
    def __init__( self, login="", pswd="", licence="", d="" ):
        print( "Called exit thread" )
        self.login = login
        self.pswd = pswd
        self.licence = licence
        self.d = d
    
# Input problem

def popProfondeur( ):
    wa = tk.Toplevel()
    wa.wm_title( "Classement : warning" )
    wt = tk.Label( wa, text =  "La profondeur doit être un entier, généralement entre 2 et 4 ou 5" )
    wt.config( font = ( "Verdana", 16), fg = "red" )
    wt.pack()
    ok = tk.Button( wa, text = "Ok", command = wa.destroy )
    ok.pack()
    return

# used to redirect an output (eg std[out,err]) on a widget
# (from stackoverflow)

class Std_redirector():
    def __init__(self, widget):
        self.widget = widget

    def write(self,string):
        self.widget.write(string)
        
# used to redirect an output (eg std[out,err]) on a widget
# (from stackoverflow)

class ThreadSafeText( tk.Text ):
    def __init__(self, master, **options):
        tk.Text.__init__(self, master, **options)
        self.queue = queue.Queue()
        self.update_me()

    def write(self, line):
        self.queue.put(line)

    def update_me(self):
        while not self.queue.empty():
            line = self.queue.get_nowait()
            self.insert(tk.END, line)
            self.see(tk.END)
            self.update_idletasks()
        self.after(10, self.update_me)

def displayWarning():
    warn = tk.Tk()
    
    warn.wm_title( "Classement futur de tennis" )
    txt1 = tk.Label( warn, text = "Attention" )
    txt1.config( font=("Verdana", 20), fg = "red")

    txt2 = tk.Label( warn, text = "Verion très très préliminaire, peu testée" )
    txt2.config( font=("Verdana", 18), fg = "blue")

    txt3 = tk.Label( warn, text = "En particulier, au moment de quitter (en particulier en cours de simulation), le programme risque d'avoir besoin d'un peu d'autorité", wraplength = 400 )
    txt3.config( font=("Verdana", 18), fg = "blue")

    ok = tk.Button( warn, text = "Ok, j'ai compris", command = warn.destroy )
    ok.config( font=("Verdana", 20), fg = "green" )
    ok.pack()

    txt1.pack()
    txt2.pack()
    txt3.pack()
    ok.pack()
    
    return
    
# View

def main():
    global login_entr
    global mdp_entr
    global lic_entr
    global prof_entr

    check_dependencies()
    displayWarning()
    
    signal.signal( signal.SIGUSR1, sighandler )

    window = tk.Tk()
    window.wm_title( "Classement futur de tennis" )
    txt = tk.Label( window, text = "Bienvenue dans l'application classement" )
    txt.config( font=("Verdana", 18), fg = "blue")
    
    # Entry fields
    
    login_txt = tk.StringVar()
    login_entr = tk.Entry( window, textvariable = login_txt, width=18 )
    login_label = tk.Label( window, text = "Votre login" )
    login_label.config( font=("Verdana", 14))

    mdp_txt = tk.StringVar()
    mdp_entr = tk.Entry( window, show = "*", textvariable = mdp_txt, width=18 )
    mdp_label = tk.Label( window, text = "Votre mot de passe" )
    mdp_label.config( font=("Verdana", 14))
    
    lic_txt = tk.StringVar()
    lic_entr = tk.Entry( window, textvariable = lic_txt, width=18 )
    lic_label = tk.Label( window, text = "Votre numéro de licence" )
    lic_label.config( font=("Verdana", 14))

    prof_txt = tk.StringVar()
    prof_entr = tk.Entry( window, textvariable = prof_txt, width=18 )
    prof_label = tk.Label( window, text = "Profondeur du calcul" )
    prof_label.config( font=("Verdana", 14))

    # Nice layout
    
    txt.grid( row = 0, column = 0, columnspan = 3 )
    login_label.grid( row = 1, column = 0)
    login_entr.grid( row = 1, column = 1 )
    mdp_label.grid( row = 2, column = 0)
    mdp_entr.grid( row = 2, column = 1 )
    lic_label.grid( row = 3, column = 0)
    lic_entr.grid( row = 3, column = 1 )
    prof_label.grid( row = 4, column = 0)
    prof_entr.grid( row = 4, column = 1 )

    # Buttons (Enter and quit)
    
    go = tk.Button( window, text = "Lancer le calcul", command = start )
    out = tk.Button( window, text = "Quitter", command = window.quit )
    go.config( font=("Verdana", 16), fg = "green" )
    out.config( font=("Verdana", 16), fg = "red" )
    
    go.grid( row = 6, column = 1 )
    out.grid( row = 6, column = 2 )

    window.mainloop()
    

if __name__ == "__main__" :
    try:
        main()
    except KeyboardInterrupt:
        print("Interruption par l'utilisateur")

    exit_pause()
