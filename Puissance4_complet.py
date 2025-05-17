# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 15:58:36 2023

@author: ELIOT
"""

# =============================================================================
'''
idée : 
    - séparer le programme en deux fichiers: une partie tkinter et une partie 
    seulement pour la classe Jeu -> est-il possible de séparer deux classes
    sachant que l\'une hérite de l\'autre?
 
    - trier les menaces :
        - celles inutiles en fonction de la parité de la ligne où elles se situent
        
Prochains ajouts :
    
    - améliorer la fonction d'\évaluation -> pour comparer avec la fonction simple
    - considérer implémenter la grille sous forme de graphe
    - finir intérface
    
    # idée : étudier l'ensemble des parties jouées pour faire du machine learning ?
    # idée : enregistrer les pièges en certaines profondeur pour pouvoir les éviter lors d'une profondeur 
    # plus faible

'''
# =============================================================================

import tkinter as tk
from tkinter import ttk # pour faire un menu déroulant


nbc_hauteur = 6
nbc_largeur = 7



Offset=2




class Jeu():
    liste_fonction_evaluation = [ "evaluation_simple" ]
    animation_jeton = False #True ssi le jeton tombe
    nb_aligne = 4
    
    def __init__(self, type_j1="humain",  type_j2="humain", nbc_hauteur=nbc_hauteur, nbc_largeur=nbc_largeur):
        #la grille est une liste de liste avec la dernière ligne reservé pour le nombre de jeton sur la colonne
        self.grille=[[0 for i in range(nbc_largeur)]for j in range(nbc_hauteur)]+[[0]*nbc_largeur]
        self.types_de_joueur = ['',type_j1,type_j2]
        self.joueur=1
        self.gagnant,self.alignement=None,None
        self.liste_coups=[] #liste de tous les coups qui ont été joué
        self.liste_prochain_coups=[] #liste de tous les coups qui peuvent être joués
        # Pour le Minmax
        self.liste_coups_Minimax=[]
        
        self.afficher_tkinter()
        #self.afficher_console()

    def rejouer(self):
        self.grille=[[0 for i in range(nbc_largeur)]for j in range(nbc_hauteur)]+[[0]*nbc_largeur]
        self.joueur=1
        if not self.gagnant:
            self.ajout_partie_txt("rejouer")
        self.gagnant,self.alignement=None,None
        self.liste_coups=[] #liste de tous les coups qui ont été joué
        self.liste_prochain_coups=[] #liste de tous les coups qui peuvent être joués
        self.types_de_joueur = ['',"humain","humain"]
        self.affichage_tkinter.root.destroy()
        self.afficher_tkinter()

    def copie(self): # fait une copie profonde de la grille
        copie = []
        for i in range(len(self.grille)):
            copie.append([])
            for j in range(len(self.grille[0])):
                copie[i].append(self.grille[i][j]*1 )
        return copie
    
    def copie_conv1et2(self): # renvoit une grille fait de 1 et de 2 au lieu de -1                                         
        copie_grille = self.copie()
        for i in range(len(self.grille)-1):
            for j in range(len(self.grille[0])):
                if copie_grille[i][j] == -1:
                    copie_grille[i][j] = 2
        return copie_grille
    
    def afficher_console(self): # permettrait de jouer dans la console
        copie_plateau = self.copie_conv1et2()
        for i in range(len(self.grille)-1):
            print(copie_plateau[i]) 
        print("\n")    
            
    def afficher_tkinter(self): # permet de jouer avec une interface tkinter
        self.affichage_tkinter = GrilleTkinter(self)
        self.affichage_tkinter.root.mainloop()
    
    def next_joueur(self):
        self.joueur =- self.joueur
    
    def prochain_coups_legaux(self): # renvoit la liste de tous les coups possibles ex: [0,1,5,6]
        liste = []
        for i in range(len(self.grille[0])):
            if self.grille[-1][i] < len(self.grille)-1 : #peut-être problème d'indicage (-1)
                liste.append(i)
        return liste
    
    def coup(self, colonne, Minimax = False): # modifie directement la grille 
        PCL = self.prochain_coups_legaux()
        if colonne in PCL :
            ligne = len(self.grille)-self.grille[-1][colonne]-2 # calcul la ligne à partir du nombre de jeton sur la colonne
            self.grille[ligne][colonne] = self.joueur
            if Minimax :
                self.liste_coups_Minimax.append([ligne, colonne])  
                # print(ligne, colonne, "coup")
            else:
                self.affichage_tkinter.dernier_coup = (ligne, colonne)
                self.liste_coups.append([ligne, colonne, len(self.liste_coups)]) # coordonnées , i-ème coup joué  # permettra d'enregistrer les parties jouées 

            self.grille[-1][colonne] += 1
    
    def retirer_coup(self, Minimax = False):
        if Minimax :
            ligne, colonne = self.liste_coups_Minimax[-1]
            self.liste_coups_Minimax.pop(-1)
        else :
            ligne, colonne, _ = self.liste_coups[-1]
            self.liste_coups.pop(-1)
        self.grille[-1][colonne] -= 1
        self.grille[ligne][colonne] = 0        
        self.next_joueur()
    
    def grille_pleine(self):
        return self.prochain_coups_legaux() == []
      
    def test_gagant(self):
        return self.recherche_n_aligne(Jeu.nb_aligne,True) != []
            
    def test_fin_game(self):
        lst_jo=[0,1,2]
        self.alignement = self.recherche_n_aligne(Jeu.nb_aligne)
        self.gagnant = self.alignement != []
        lst_pc = self.prochain_coups_legaux()
        self.fin_game = lst_pc == []
        
        if self.gagnant :
            print("victoire")
            gagnant = lst_jo[self.alignement[-1][-1]]
            mid = (self.affichage_tkinter.largeur_can//2, self.affichage_tkinter.hauteur_can//2)
            try:
                self.affichage_tkinter.canvas.delete(self.test_victoire)
            except:None
            self.test_victoire = self.affichage_tkinter.canvas.create_text(mid[0], mid[1], text= f"Le joueur {gagnant} a gagné !!!", font=("Helvetica", 50), fill="black",tags="phrase de fin")
            self.ajout_partie_txt("victoire"+str(gagnant))
            print(self.liste_coups)
        
        if self.fin_game :
            print("égalité")
            mid = (self.affichage_tkinter.largeur_can//2, self.affichage_tkinter.hauteur_can//2)
            self.test_victoire = self.affichage_tkinter.canvas.create_text(mid[0], mid[1], text = "Egalité !", font = ("Helvetica", 50), fill = "black",tags="phrase de fin")
            self.ajout_partie_txt("égalité")
            print(self.liste_coups)
    
    def ajout_partie_txt(self,str_type_fin):
        # fichier = open("liste_des_parties_effectue.txt","r")
        # liste_parties = fichier.readlines()
        # print(liste_parties)
        # fichier.close() 
        fichier = open("liste_des_parties_effectue.txt","a")
        fichier.write("\n"+str(self.liste_coups)+str_type_fin)
        fichier.close()
        
        
        
    #----------------------------fonction de recherche-------------------------
    # on va d'abord faire les fonctions pour rechercher naïvement des n-aligné
    
    
    # fonction pour récupérer des segments pour ensuite chercher l'alignement
    #x et y sont les coordonnées du premier chiffre de la liste
    #dx et dy permettent d'avoir la direction du segement sur la plateau : _\|/
    def recup_segment(self, longueur_alignement, y, x, dy, dx): 
        return [self.grille[y+i*dy][x+i*dx] for i in range(longueur_alignement)]     
    
    
    
    def recherche_n_aligne(self, longueur_alignement,test=False): 
        
# =============================================================================
#         
# rajouter des conditions pour baisser la complexité comme regarder le nombre de jeton sur la colonne
# ou le nombre de jetons déjà jouer
#
# =============================================================================
    
        n = longueur_alignement
        liste_alignement = []
        hauteur, largeur = len(self.grille)-1, len(self.grille[0])
        
        for l in range(largeur):
            for h in range(hauteur):
                
                if self.grille[h][l] != 0:
                    
                    if l <= largeur-n:
                        if abs(sum(self.recup_segment(n, h, l, 0, 1))) == n:
                            liste_alignement.append([ h, l, h, l+n-1, self.grille[h][l]])
                            
                    if h <= hauteur-n:
                        if abs(sum(self.recup_segment(n, h, l, 1, 0))) == n:
                            liste_alignement.append([ h, l, h+n-1, l, self.grille[h][l]])
                            
                    if l<=largeur-n and h<=hauteur-n :
                        if abs(sum(self.recup_segment(n, h, l, 1, 1))) == n:
                            liste_alignement.append([ h, l, h+n-1, l+n-1, self.grille[h][l]])
                            
                    if l>=n-1 and h<=hauteur-n :
                        if abs(sum(self.recup_segment(n, h, l, 1, -1))) == n:
                            liste_alignement.append([ h, l, h-n+1, l+n-1, self.grille[h][l]])
                if liste_alignement != [] and test :
                    return liste_alignement
        return liste_alignement

    # #----------------------catégorisation menace-------------------------------
    # # type de menace:
    #     # menace ouverte -> 1
    #     # menace mi ouverte -> 0
    #     # menace fermée -> -1
    
    # def cater_menace(self,taille_menace):  # menace =[début_x,début_y,fin_x,fin_y,possede_un_trou]
    #     n = Jeu.nb_aligne
    #     if taille_menace== n and self.menace_a_trou() :
    #         return 0 
    #     else:
    #         nb_aligne_pos = self.nb_align_possible()
    #         if nb_aligne_pos== n:
    #             return 0
    #         else:
    #             if nb_aligne_pos<n:
    #                 return -1
    #             else:
    #                 return 1
            
    # def recherche_menace(self,long_menace):
    #     n = Jeu.nb_aligne
    #     liste = []
    # #--------------------------------------------------------------------------
   
    #----------------------------Minimax---------------------------------------
    #fonction minimax généraliser à toute fonction d'évaluation

    def Minimax(self, joueur, profondeur = 5):  #profondeur -1
        # self.afficher_console()
        # print(self.evaluation_simple())
        if profondeur == 0 or self.recherche_n_aligne(Jeu.nb_aligne) != []:
            return self.evaluation_simple()
        else:
            PCL = self.prochain_coups_legaux()
            if joueur == 1:
                liste_val = []
                for i in PCL:
                    self.coup(i, True)
                    self.next_joueur()
                    liste_val.append(self.Minimax(-joueur, profondeur-1))
                    self.retirer_coup(True)
                return max(liste_val)
            else:
                liste_val = []
                for i in PCL:
                    self.coup(i, True)
                    self.next_joueur()
                    liste_val.append(self.Minimax(-joueur, profondeur-1))
                    self.retirer_coup(True)
                return min(liste_val)
            
    #si on utilise la fonction d'évaluation simple alors Inf = 1 suffit
    Inf=1
            
    def elagageAB(self,joueur,a,b,profondeur = 6):
        if profondeur == 0 or self.recherche_n_aligne(Jeu.nb_aligne) != []:
            return self.evaluation_simple()
        else:
            PCL = self.prochain_coups_legaux()
            if joueur == 1: #le joueur qui essaie de maximiser
                v=-1 #-Inf
                for i in PCL:
                    self.coup(i, True)
                    self.next_joueur()
                    v = max(v,self.elagageAB(-joueur, a,b,profondeur-1))
                    self.retirer_coup(True)
                    if v >= b :
                        return v
                    a = max(a,v)
            else:
                v=1 #Inf
                for i in PCL:
                    self.coup(i, True)
                    self.next_joueur()
                    v = min(v,self.elagageAB(-joueur, a,b,profondeur-1))
                    self.retirer_coup(True)
                    if v <= a :
                        return v
                    b = min(b,v)
        return v
                

            
    #---------------------détermination meilleur coup--------------------------
    
    def deter_best_coup(self):
        liste = []
        PCL = self.prochain_coups_legaux()
        for colonne in PCL:
            self.coup(colonne, True)
            self.next_joueur()
            liste.append([self.elagageAB(self.joueur,-1,1), colonne]) #-----------------------------------------------------------
            # liste.append([self.Minimax(self.joueur),colonne])
            self.retirer_coup(True)
        nb_lignes = len(self.grille[0])
        mid, maxi = nb_lignes//2, liste[0]
        if self.joueur == 1:
            for val,col in liste :
                if val > maxi[0]:
                    maxi = [val,col]
                if val == maxi[0] and abs(col - mid) < abs(maxi[1] - mid):
                    maxi = [val,col]
            print(maxi,self.joueur)
        else:
            for val,col in liste :
                if val < maxi[0]:
                    maxi = [val,col]
                if val == maxi[0] and abs(col - mid) < abs(maxi[1] - mid):
                    maxi = [val,col]
            print(maxi,self.joueur)
        return maxi[1]

    #--------------------------------------------------------------------------


    def mise_a_jour(self):
        jo = self.joueur
        
        if self.liste_prochain_coups != [] and self.types_de_joueur[jo] == "humain" : 
                    
            colonne=self.liste_prochain_coups[0]
            # faire le coup dans la grille avec l'info de la colone
            if colonne in self.prochain_coups_legaux():
                self.coup(colonne)
                # self.afficher_console()
                self.affichage_tkinter.maj_tkinter()
                self.next_joueur()
            self.liste_prochain_coups.pop(0)
            self.test_fin_game()
            self.mise_a_jour()

        if self.types_de_joueur[jo] == "bot": 
            self.coup(self.deter_best_coup())
            self.affichage_tkinter.maj_tkinter()
            self.test_fin_game()
            self.next_joueur()
            self.deter_best_coup()

            self.mise_a_jour()
        

        
        



    #----------------------fonctions d'évaluations-----------------------------
    
    #fonction d'évaluation simple qui renvoit 1 si le joueur 1 gagne, -1 si le 2 gagne, 0 si aucun ne gagne
    def evaluation_simple(self):
        liste = self.recherche_n_aligne(Jeu.nb_aligne,True)
        if liste == []:
            return 0
        else:
            return liste[0][-1]
        
# permet d'avoir un canva adapté a toutes les dimensions possibles (limite de ~30 de hauteur et ~50 de largeur)
def calcul_dim_canva(nb_colonne, nb_ligne):
    largeur_max, hauteur_max = 1100, 610
    #calcul de la largeur d'un carré en l'arrondissant à la dizaine en dessous
    largeur_case = (min(largeur_max//nb_colonne , hauteur_max//nb_ligne)//10)*10

    largeur_can = nb_colonne * largeur_case 
    hauteur_can = nb_ligne * largeur_case 
    
    return ( largeur_can , hauteur_can , largeur_case )

# =============================================================================
# Pour jouer avec une interface tkinter
# =============================================================================
class GrilleTkinter(Jeu):

    def __init__(self, jeu):
        
        self.grille = jeu.grille
        self.nb_ligne, self.nb_colonne = len(self.grille)-1, len(self.grille[0])
        self.largeur_can, self.hauteur_can, self.largeur_case = calcul_dim_canva(self.nb_colonne, self.nb_ligne)
        self.jeu = jeu
        self.root = tk.Tk()                       #400
        self.root.geometry(str(self.largeur_can+200 ) + 'x' + str(self.hauteur_can+Offset*5) + '+0+0')
        #jetons :
        self.dernier_coup, self.jeton_coord = None, None
        self.vitesse, self.accel = 0, 10
        
        self.canvas=tk.Canvas(self.root, width = str(self.largeur_can+Offset), height = str(self.hauteur_can+Offset), bg = 'grey')
        self.canvas.bind('<Button-1>', self.clic_gauche)
        
        #les bouttons
        self.frame=tk.Frame(self.root)
        
        #menu déroulant        
        self.set_joueur_1_txt = tk.Label(self.frame, text="Le Joueur 1")
        self.set_joueur_1 = ttk.Combobox(self.frame, value=["humain","bot"])
        self.set_joueur_1.current(0)
        self.set_joueur_2_txt = tk.Label(self.frame, text="Le Joueur 2")
        self.set_joueur_2 = ttk.Combobox(self.frame, value=["humain","bot"])
        self.set_joueur_2.current(0)
        self.set_joueur_1.bind("<<ComboboxSelected>>", self.set_j1)
        self.set_joueur_2.bind("<<ComboboxSelected>>", self.set_j2)   
        
        self.set_joueur_1_txt.pack()
        self.set_joueur_1.pack()
        self.set_joueur_2_txt.pack()
        self.set_joueur_2.pack()
        
        #
        self.Button_retirer_coup = tk.Button(self.frame, text="Revenir en arrière", command = self.enlever_coup)
        self.Button_destroy = tk.Button(self.frame, text="Quitter", command = self.root.destroy)
        self.Button_rejouer = tk.Button(self.frame, text = "rejouer", command = self.jeu.rejouer)
        
        self.Button_retirer_coup.pack()
        self.Button_rejouer.pack()
        self.Button_destroy.pack()

        self.frame.pack(side = "right")
        
        self.dessine_grille()
        self.canvas.pack(side="left")
    
    
    def enlever_coup(self):
        try:
            self.canvas.delete(self.jeu.test_victoire) 
        except:None
        try:
            self.jeu.retirer_coup()
            self.canvas.delete("jeton")
        except:
            print("non mais stop là !")
        self.maj_tkinter()
    
    def set_j1(self, event):
        self.jeu.types_de_joueur[1] = self.set_joueur_1.get()
        self.jeu.mise_a_jour()
        
    def set_j2(self, event):
        self.jeu.types_de_joueur[2] = self.set_joueur_2.get()
        self.jeu.mise_a_jour()
    
    def clic_gauche(self, event):
        x = event.x
        colonne = x//(self.largeur_case)
        try:
            self.canvas.after_cancel(self.id)
        except: 
            None
        self.vitesse = 0
        self.jeu.liste_prochain_coups.append(colonne)
        self.jeu.mise_a_jour()
        
    def dessine_grille(self):
        l = self.largeur_case
        for j in range(self.nb_ligne):               
            for i in range(self.nb_colonne):
                self.canvas.create_rectangle(l*i+Offset, l*j+Offset, l*(i+1)+Offset, l*(j+1)+Offset, fill='white', tags="grille") 



    def maj_tkinter(self):
        self.canvas.delete("jeton")
        self.canvas.delete("falling")
        self.create_jetons_fixes()
        self.maj_jeton()

    def create_jetons_fixes(self):        
        for ligne in range(len(self.grille)-1):
            for colonne in range(len(self.grille[0])):
                if self.grille[ligne][colonne] != 0 :
                    couleur = "yellow" if self.grille[ligne][colonne] == 1 else "red"
                    if (ligne,colonne) != self.dernier_coup or not Jeu.animation_jeton :
                        Jeton(couleur, (ligne, colonne), self)
                                
                        
    def maj_jeton(self):
        self.create_jetons_fixes()
        #animation de la chute du jeton qui vient d'être joué
        if Jeu.animation_jeton:
            self.jeton_coord = self.dernier_coup
            ligne, colonne = self.dernier_coup
            self.jeton_pos = ( self.largeur_case * colonne, - self.largeur_case)
            l, o = self.largeur_case, Offset 
            couleur = "yellow" if self.grille[ligne][colonne] == 1 else "red"
            self.jeton_fall = self.canvas.create_oval(l * colonne+o, -l+o, l*(colonne+1)+o, o,fill = couleur, tags = "falling")
            self.id = self.canvas.after(1, self.anime_dernier_jeton)
    
    
    def anime_dernier_jeton(self):
        ligne , colonne  = self.dernier_coup
        l, o = self.largeur_case, Offset 
        
        #condition terminal pour sortir de l'appel récursif .after
        if self.jeton_pos[1] >= ligne*l+o and self.vitesse == 0 :
            self.canvas.coords(self.jeton_fall, l*colonne+o, l*ligne+ o, l*(colonne+1)+o,l*(ligne+1)+o)
            print("c'est la fin", self.id)
            self.canvas.after_cancel(self.id)
            
        else:
            _ , y = self.jeton_pos
            if y >= ligne*l :
                self.vitesse = (int(self.vitesse*-0.7)//10)*10
                print(y,self.vitesse)
            else :
                self.vitesse += self.accel
            y += self.vitesse
            self.canvas.coords(self.jeton_fall, l*colonne+o, y+ o, l*(colonne+1)+o, y+l+o)
            self.jeton_pos = l*colonne+o, y
            self.id = self.canvas.after(50,self.anime_dernier_jeton)
        
class Jeton(GrilleTkinter):
    
    def __init__(self, couleur, coordonnee, grille_tkinter):
        self.grille_tkinter = grille_tkinter
        self.ligne, self.colonne = coordonnee[0], coordonnee[1]
        self.couleur = couleur
        self.jeton = self.dessine_jeton()
    
    def dessine_jeton(self):
        l  = self.grille_tkinter.largeur_case
        j , i  = self.ligne, self.colonne
        return self.grille_tkinter.canvas.create_oval(l*i+Offset, l*j+Offset, l*(i+1)+Offset, l*(j+1)+Offset, fill = self.couleur, tags = "jeton")

#-------démarrage-------

if __name__=='__main__':
    Jeu()
















