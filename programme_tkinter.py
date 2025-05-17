# -*- coding: utf-8 -*-

# =============================================================================
# Convention de nommage: PEP 8
#   - les classes : PascalCase
#   - les fonctions : snake_case
#   - les variables : snake_case
#   - les constantes : UPPER_CASE_WITH_UNDERSCORES
# =============================================================================

import tkinter as tk
from tkinter import ttk # pour faire un menu déroulant
import programme_main as Pm

OFFSET = 2 # permet de recadrer le cadrillage de l'interface pour le voir correctement


# permet d'avoir un canvas adapté à toutes les dimensions possibles (limite de ~30 de hauteur et ~50 de largeur)

def calcul_dim_canvas(nb_colonne, nb_ligne):
    largeur_max, hauteur_max = 1100, 610 # ces valeurs conviennent à mon ordinateur
    
    #calcul de la largeur d'un carré en l'arrondissant à la dizaine en dessous
    largeur_case = (min(largeur_max//nb_colonne , hauteur_max//nb_ligne)//10)*10

    largeur_can = nb_colonne * largeur_case 
    hauteur_can = nb_ligne * largeur_case 
    
    return ( largeur_can , hauteur_can , largeur_case )


# =============================================================================
# Pour jouer avec une interface tkinter
# =============================================================================

class GrilleTkinter(Pm.Jeu):


    def __init__(self, jeu, animation_jeton):

        self.animation_jeton = animation_jeton # True ou False
        self.grille = jeu.grille
        self.jeu = jeu

        self.nb_ligne, self.nb_colonne = len(self.grille)-1, len(self.grille[0])
        self.largeur_can, self.hauteur_can, self.largeur_case = calcul_dim_canvas(self.nb_colonne, self.nb_ligne)
        
        self.root = tk.Tk()
        self.root.geometry(str(self.largeur_can + 200 ) + 'x' + str(self.hauteur_can + OFFSET*5) + '+0+0')
        
        # Jetons :
        self.dernier_coup, self.jeton_coord = None, None
        self.vitesse, self.accel = 0, 10
        
        self.canvas = tk.Canvas(self.root, width = str(self.largeur_can + OFFSET), height = str(self.hauteur_can + OFFSET), bg = 'grey')
        self.canvas.bind('<Button-1>', self.clic_gauche)
        
        # Frame du côté droit du canvas, pour y mettre tous les widgets 
        self.frame = tk.Frame(self.root)
        
        # Menu déroulant        
        self.set_joueur_1_txt = tk.Label(self.frame, text = "Le Joueur 1")
        self.set_joueur_1 = ttk.Combobox(self.frame, value = ["humain","bot"])
        self.set_joueur_1.current(0)
        self.set_joueur_1.bind("<<ComboboxSelected>>", self.set_j1)
        
        self.set_joueur_2_txt = tk.Label(self.frame, text = "Le Joueur 2")
        self.set_joueur_2 = ttk.Combobox(self.frame, value = ["humain","bot"])
        self.set_joueur_2.current(1)
        self.set_joueur_2.bind("<<ComboboxSelected>>", self.set_j2) 
        
        self.set_type_algo_txt = tk.Label(self.frame, text = "Type d'algorithme ")
        self.set_type_algo = ttk.Combobox(self.frame, value = ["Minimax","Alpha-Beta"])
        self.set_type_algo.current(1)
        self.set_type_algo.bind("<<ComboboxSelected>>", self.set_algo)
        
        self.set_type_eval_txt = tk.Label(self.frame, text = "Type d'évaluation")
        self.set_type_eval = ttk.Combobox(self.frame, value = ["Simple","Complexe"])
        self.set_type_eval.current(1)
        self.set_type_eval.bind("<<ComboboxSelected>>", self.set_eval)

        self.set_joueur_1_txt.pack()
        self.set_joueur_1.pack()
        self.set_joueur_2_txt.pack()
        self.set_joueur_2.pack()
        self.set_type_algo_txt.pack()
        self.set_type_algo.pack()
        self.set_type_eval_txt.pack()
        self.set_type_eval.pack()
        
        # Les Bouttons :
        self.Button_retirer_coup = tk.Button(self.frame, text="Revenir en arrière", command = self.enlever_coup)
        self.Button_rejouer = tk.Button(self.frame, text = "rejouer", command = self.jeu.rejouer)
        self.Button_affichage_console = tk.Button(self.frame, text = "Affichage console", command = self.afficher_console)
        self.Button_destroy = tk.Button(self.frame, text="Quitter", command = self.root.destroy)

        self.Button_retirer_coup.pack()
        self.Button_rejouer.pack()
        self.Button_affichage_console.pack()
        self.Button_destroy.pack()

        self.frame.pack(side = "right")
        
        self.dessine_grille()
        self.canvas.pack(side = "left")



    def enlever_coup(self):
        try:
            self.canvas.delete(self.jeu.test_victoire) 
        except: None
        try:
            self.jeu.retirer_coup()
            self.canvas.delete("jeton")
        except IndexError: 
            print("Aucun coups en mémoire")
        self.maj_tkinter()
    
    
    def set_j1(self, event):
        self.jeu.types_de_joueur[1] = self.set_joueur_1.get()
        self.jeu.mise_a_jour()
        
    def set_j2(self, event):
        self.jeu.types_de_joueur[-1] = self.set_joueur_2.get()
        self.jeu.mise_a_jour()
    
    def set_algo(self, event):
        self.jeu.type_algo = self.set_type_algo.get()
        self.jeu.mise_a_jour()
    
    def set_eval(self, event):
        self.jeu.type_eval = self.set_type_eval.get()
        self.jeu.mise_a_jour()
    
    def clic_gauche(self, event):
        x = event.x
        colonne = x//(self.largeur_case)
        try:
            self.canvas.after_cancel(self.id)
        except: 
            None
        self.vitesse = 0 # pour l'animation des jetons
        self.jeu.liste_prochain_coups.append(colonne)
        self.jeu.mise_a_jour()
        
    def dessine_grille(self):
        l = self.largeur_case
        for j in range(self.nb_ligne):               
            for i in range(self.nb_colonne):
                self.canvas.create_rectangle(l*i+OFFSET, l*j+OFFSET, l*(i+1)+OFFSET, l*(j+1) + OFFSET, fill = 'white', tags = "grille") 

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
                    if (ligne,colonne) != self.dernier_coup or not self.animation_jeton :
                        Jeton(couleur, (ligne, colonne), self)
                        
    def maj_jeton(self):
        self.create_jetons_fixes()
        #animation de la chute du jeton qui vient d'être joué
        if self.animation_jeton:
            self.jeton_coord = self.dernier_coup
            ligne, colonne = self.dernier_coup
            self.jeton_pos = ( self.largeur_case * colonne, - self.largeur_case)
            l, o = self.largeur_case, OFFSET 
            couleur = "yellow" if self.grille[ligne][colonne] == 1 else "red"
            self.jeton_fall = self.canvas.create_oval(l * colonne+o, -l+o, l*(colonne+1)+o, o,fill = couleur, tags = "falling")
            self.id = self.canvas.after(1, self.anime_dernier_jeton)


    # animation du jeton qui vient d'être joué
    
    def anime_dernier_jeton(self):
        ligne , colonne  = self.dernier_coup
        l, o = self.largeur_case, OFFSET 
        
        # conditions terminales pour sortir de l'appel récursif .after
        if self.jeton_pos[1] >= ligne*l+o and self.vitesse == 0 :
            self.canvas.coords(self.jeton_fall, l*colonne+o, l*ligne+o, l*(colonne+1)+o,l*(ligne+1)+o)
            print("fin", self.id)
            self.canvas.after_cancel(self.id)
            
        else:
            _ , y = self.jeton_pos
            if y >= ligne*l :
                self.vitesse = (int(self.vitesse*-0.7)//10)*10
            else :
                self.vitesse += self.accel
            y += self.vitesse
            self.canvas.coords(self.jeton_fall, l*colonne+o, y+ o, l*(colonne+1)+o, y+l+o)
            self.jeton_pos = l*colonne+o, y
            self.id = self.canvas.after(50, self.anime_dernier_jeton)
        
class Jeton(GrilleTkinter):
    
    def __init__(self, couleur, coordonnee, grille_tkinter):
        self.grille_tkinter = grille_tkinter
        self.ligne, self.colonne = coordonnee[0], coordonnee[1]
        self.couleur = couleur
        self.jeton = self.dessine_jeton()
    
    def dessine_jeton(self):
        l  = self.grille_tkinter.largeur_case
        j , i  = self.ligne, self.colonne
        return self.grille_tkinter.canvas.create_oval(l*i+OFFSET, l*j+OFFSET, l*(i+1)+OFFSET, l*(j+1)+OFFSET, fill = self.couleur, tags = "jeton")


