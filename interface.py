#!/usr/bin/python

## http://alain72.developpez.com/tutos/wxPython/
## http://www.borer.name/files/eivd/wxpython/introduction_a_wxpython.pdf

""" Outil de recuperation du classement.
 " (c) Camille Coti, 2013
 " Todo : 
 " Gestion des exceptions
 " Cas ou la FFT est en maintenance
"""


import wx
import sys
import palmares

DEFAULT_PROF = 2
ID_EXIT = 110
 
class RedirectText( object ):
    def __init__( self,aWxTextCtrl ):
        self.out = aWxTextCtrl

    def write( self, string ):
        str_safe = string.decode('iso-8859-1') #.encode( 'latin-1' )
        self.out.WriteText( str_safe )
 
class MainPanel( wx.Panel ):
    def __init__( self, parent ):
        wx.Panel.__init__( self, parent )

        # Les 2 boutons a droite : envoyer la sauce et quitter

        self.buttonRun = wx.Button( self, label="Executer" )
        self.buttonRun.Bind( wx.EVT_BUTTON, self.OnRun )
        self.buttonExit = wx.Button( self, label="Quitter")
        self.buttonExit.Bind( wx.EVT_BUTTON, self.OnExit )

        # Les legendes des champs de texte, sur la gauche

        self.lLogin = wx.StaticText( self, label = "Login : " ) 
        self.lPassword = wx.StaticText( self, label = "Mot de passe : " )
        self.lLicence = wx.StaticText( self, label = "Numero de licence : " )
        self.lProfondeur = wx.StaticText( self, label = "Profondeur : " )

        # Les champs de texte

        self.tLogin = wx.TextCtrl( self, size = ( 210, -1 ) )
        self.tPassword = wx.TextCtrl( self, size = ( 210, -1 ), style=wx.TE_PASSWORD )
        self.tLicence = wx.TextCtrl( self, size = (210, -1 ) )
        self.tProfondeur = wx.TextCtrl( self, size = (210, -1 ), value = "2" )
        self.textOutput = wx.TextCtrl( self, style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL )

        # Rediriger stdout sur textOutput

        redir = RedirectText( self.textOutput )
        sys.stdout = redir

        # Positionnement sur une grille 4x2

        self.sizerF = wx.FlexGridSizer( 4, 2, 5, 5 )
        self.sizerF.Add( self.lLogin )      # rangee 1, colonne 1
        self.sizerF.Add( self.tLogin )      # rangee 1, colonne 2
        self.sizerF.Add( self.lPassword )   # rangee 2, colonne 1
        self.sizerF.Add( self.tPassword )   # rangee 2, colonne 2
        self.sizerF.Add( self.lLicence )    # rangee 3, colonne 1
        self.sizerF.Add( self.tLicence )    # rangee 3, colonne 2
        self.sizerF.Add( self.lProfondeur ) # rangee 4, colonne 1
        self.sizerF.Add( self.tProfondeur ) # rangee 4, colonne 2

        # Attachement des trucs sur le panel

        self.sizerB = wx.BoxSizer( wx.VERTICAL )
        self.sizerB.Add( self.buttonRun, 1, wx.ALIGN_RIGHT|wx.ALL, 5 )
        self.sizerB.Add( self.buttonExit, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.sizer1 = wx.BoxSizer( )
        self.sizer1.Add( self.sizerF, 0, wx.ALIGN_RIGHT | wx.EXPAND | wx.ALL, 10 )
        self.sizer1.Add( self.sizerB, 0, wx.ALIGN_RIGHT | wx.EXPAND | wx.ALL )

        self.sizer2 = wx.BoxSizer( )
        self.sizer2.Add( self.textOutput, 1, wx.EXPAND | wx.ALL, 5 )

        self.sizerFinal = wx.BoxSizer( wx.VERTICAL )
        self.sizerFinal.Add( self.sizer1, 0, wx.ALIGN_RIGHT | wx.EXPAND | wx.ALL )
        self.sizerFinal.Add( self.sizer2, 1, wx.ALIGN_RIGHT | wx.EXPAND | wx.ALL )

        self.SetSizerAndFit( self.sizerFinal )

    # Affiche une boite de dialogue
    def creerDial( self, message ):
        dlg = wx.MessageDialog( self, message, "oops", wx.ICON_EXCLAMATION | wx.CENTRE | wx.OK )
        dlg.ShowModal()
        dlg.Destroy()

    # Recupere les valeurs saisies dans les champs:
    # les identifiants (login, password : strings), le numero de licence (int) 
    # et la profondeur optionnelle (int)
    def getValues( self ):
        textLogin = self.tLogin.GetValue( )
        if '' == textLogin:
            self.creerDial( "Il manque un champ de texte obligatoire : le login" )
        textPassword = self.tPassword.GetValue( )
        if '' == textPassword:
            self.creerDial( "Il manque un champ de texte obligatoire : le mot de passe" )
        try:
            sLicence = self.tLicence.GetValue( )
            if '' == sLicence:
                numLicence = -1
                self.creerDial( "Il manque un champ de texte obligatoire : le numero de licence" )
            else:
                numLicence = int( sLicence ) 
        except:
            sLicence = sLicence[:-1]
            try:
                numLicence = int( sLicence ) 
            except:
                print("probleme avec le numero de licence saisi ", self.tLicence.GetValue( ))
                self.creerDial( "probleme avec le numero de licence saisi " + self.tLicence.GetValue( ) )
        sProf = self.tProfondeur.GetValue( )
        if '' == sProf :
            global DEFAULT_PROF
            profondeur = int( DEFAULT_PROF )
        else:
            try:
                profondeur = int( sProf ) 
            except:
                print("probleme avec la profondeur saisie ", end=' ')
        return textLogin, textPassword, numLicence, profondeur

    def OnRun( self, event ):
        # Recuperer ce qui a ete saisi
        textLogin, textPassword, numLicence, profondeur = self.getValues()
        print(textLogin, textPassword, numLicence, profondeur)

        # Calcul du classement
        palmares.recupClassement( textLogin, textPassword, numLicence, profondeur )

        # Ecriture du resultat dans la boite
        # self.textOutput.SetValue( "toto" )
        
        return

    def OnExit( self, event ):
        self.GetParent( ).Close( )
        return

class MainWindow( wx.Frame ):
    def __init__( self ):
        wx.Frame.__init__(  self, None, title = "Classement : l\'appli de K-mille", size = ( 455, 330 ), 
                           style = (  (  wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE | 
                                  wx.STAY_ON_TOP ) ^ wx.RESIZE_BORDER ) )
        self.CreateStatusBar( ) 

        self.fileMenu = wx.Menu( )
        self.fileMenu.Append( ID_EXIT, "E&xit", "Quitter" )
        self.menuBar = wx.MenuBar( )
        self.menuBar.Append( self.fileMenu, "&File" )
        self.SetMenuBar( self.menuBar )
        wx.EVT_MENU( self, ID_EXIT, self.OnExit )                    

        self.Panel = MainPanel( self )

        self.CentreOnScreen( )
        self.Show( )

    def OnExit( self,  event ):
        self.Close( )

if __name__ == "__main__":
    app = wx.App( False )
    frame = MainWindow( )
    app.MainLoop( )
