# -*- coding: utf-8 -*-

import time

# =============================================================================
# Convention de nommage: PEP 8
#   - les classes : PascalCase
#   - les fonctions : snake_case
#   - les variables : snake_case
#   - les constantes : UPPER_CASE_WITH_UNDERSCORES
# =============================================================================

import programme_tkinter as Pt

#paramètres généraux de l'objet Jeu
nbc_hauteur = 6         # nombre de cases sur la hauteur de la grille
nbc_largeur = 7         # nombre de cases sur la largeur de la grille
profondeur = 3      
nb_aligne = 4

dico_temps = {}     

class Jeu():    
    # l'animation n'est pas finalisée mais donne un avant-goût du projet final
    animation_jeton = False # True ssi l'animation du jeton qui tombe
    affiche_tkinter = True  # idem
    affiche_console = False # idem
    
    def __init__(self, type_j1 = "humain",  type_j2 = "bot", premier_coup = 2, prof = profondeur, nb_aligne = nb_aligne, type_algo = "Alpha-Beta", type_eval = "Complexe" ):
        
        # la grille est une liste de listes avec la dernière ligne reservée pour le nombre de jetons sur la colonne
        self.grille = [[0 for i in range(nbc_largeur)] for j in range(nbc_hauteur)] + [[0]*nbc_largeur]
        
        self.types_de_joueur = ['', type_j1, type_j2]
        self.joueur = 1
        self.nb_aligne = nb_aligne

        self.temps = time.time()

        self.gagnant,self.liste_alignements = None,None
        self.fin_game = False
        self.liste_coups=[] # liste de tous les coups qui ont été joué
        self.liste_prochain_coups=[] # liste de tous les coups qui peuvent être joués
        
        # Pour le Minimax
        
        self.profondeur = prof
        self.liste_coups_Minimax=[]
        
        self.type_algo = type_algo     # Minimax ou Alpha-Beta
        self.type_eval = type_eval     # evaluation_simple ou evaluation_complexe
        

        self.afficher_console("coup numéro : 1", self.affiche_console)

        if self.affiche_tkinter :
            self.afficher_tkinter()
        else:
            self.premier_coup = premier_coup
            self.types_de_joueur = ['', "bot", "bot"]
            self.coup(premier_coup)
            self.mise_a_jour()


    def rejouer(self):
        self.grille = [[0 for i in range(nbc_largeur)] for j in range(nbc_hauteur)] + [[0]*nbc_largeur]
        self.joueur = 1

        if not self.gagnant:
            self.mise_a_jour_fichier_txt("rejouer")
        
        self.gagnant, self.liste_alignements = None, None
        self.liste_coups=[]     # liste de tous les coups qui ont été joué
        self.liste_prochain_coups=[]    # liste de tous les coups qui peuvent être joués
        self.types_de_joueur = ['', "humain", "humain"]

        self.afficher_console("Nouvelle partie\n", self.affiche_console)

        self.affichage_tkinter.root.destroy()
        self.afficher_tkinter()
        self.mise_a_jour()


#----------------------------Fonctions utilitaires----------------------------------
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
    
    def afficher_console(self, obj = None, bool = True): # permettrait de jouer dans la console
        if obj == None:
            copie_plateau = self.copie_conv1et2()
            for i in range(len(self.grille)-1):
                print(copie_plateau[i])
            print("\n") 
        elif bool == True:
            print(obj)
    
    def afficher_liste(self, liste, nom_liste):
        print(nom_liste)
        for i in range(len(liste)):
            print(liste[i])
            

        
    def afficher_tkinter(self): # permet de jouer avec une interface tkinter
        if self.affiche_tkinter:
            self.affichage_tkinter = Pt.GrilleTkinter(self, self.animation_jeton)
            self.affichage_tkinter.root.mainloop()
    
    def prochain_joueur(self):
        self.joueur =- self.joueur
    
    def prochain_coups_legaux(self): # renvoit la liste de tous les coups possibles ex: [0,1,5,6]
        liste = []
        for i in range(len(self.grille[0])):
            if self.grille[-1][i] < len(self.grille)-1 : #peut-être problème d'indicage (-1)
                liste.append(i)
        return liste
    
#---------------------------------------------------------------------------------

    def coup(self, colonne, Minimax = False): # modifie directement la grille 
        PCL = self.prochain_coups_legaux()
        if colonne in PCL :
            ligne = len(self.grille) - self.grille[-1][colonne] - 2   # calcul la ligne à partir du nombre de jetons sur la colonne
            self.grille[ligne][colonne] = self.joueur
            if Minimax :
                self.liste_coups_Minimax.append([ligne, colonne])  
            else:
                if self.affiche_tkinter:
                    self.affichage_tkinter.dernier_coup = ligne, colonne
                self.liste_coups.append([ligne, colonne])   # coordonnées: permettra d'enregistrer les parties jouées 

            self.grille[-1][colonne] += 1
    

    def retirer_coup(self, Minimax = False):
        if Minimax :
            ligne, colonne = self.liste_coups_Minimax[-1]
            self.liste_coups_Minimax.pop(-1)
        else :
            ligne, colonne = self.liste_coups[-1] 
            self.liste_coups.pop(-1)
        self.grille[-1][colonne] -= 1
        self.grille[ligne][colonne] = 0        
        self.prochain_joueur()
    
#----------------------------Tests grille terminale-------------------------------

    def grille_pleine(self):
        return self.prochain_coups_legaux() == []
      
    def test_gagant(self):
        # True permet d'arrêter la fonction de recherche dès le premier alignement découvert
        return self.recherche_n_aligne(self.nb_aligne, True) != [] 
    
    def test_fin_game(self):
        lst_jo = [0, 1, 2]
        self.liste_alignements = self.recherche_n_aligne(self.nb_aligne)
        self.gagnant = self.liste_alignements != []
        lst_pc = self.prochain_coups_legaux()
        self.fin_game = (lst_pc == [] or self.gagnant)
        if self.fin_game:
            if self.gagnant :
                gagnant = lst_jo[self.liste_alignements[-1][-1]]
                self.afficher_console("victoire"+str(gagnant), self.affiche_console)
                if self.affiche_tkinter : 
                    mid = (self.affichage_tkinter.largeur_can//2, self.affichage_tkinter.hauteur_can//2)
                    try:
                       self.affichage_tkinter.canvas.delete(self.test_victoire)
                    except:None
                    self.test_victoire = self.affichage_tkinter.canvas.create_text(mid[0], mid[1], text = f"Le joueur {gagnant} a gagné !!!", font=("Helvetica", 50), fill = "black", tags = "phrase de fin")
                self.mise_a_jour_fichier_txt("victoire", gagnant)
                self.afficher_console(self.liste_coups, self.affiche_console)
                dico_temps[self.profondeur] = round(time.time() - self.temps, 3)
            else:
                self.afficher_console("égalité", self.affiche_console)
                if self.affiche_tkinter:
                    mid = (self.affichage_tkinter.largeur_can//2, self.affichage_tkinter.hauteur_can//2)
                    self.test_victoire = self.affichage_tkinter.canvas.create_text(mid[0], mid[1], text = "Egalité !", font = ("Helvetica", 50), fill = "black", tags = "phrase de fin")
                self.mise_a_jour_fichier_txt("égalité")
                self.afficher_console(self.liste_coups, self.affiche_console)

#---------------------------------------------------------------------------------

    def mise_a_jour_fichier_txt(self, str_type_fin, gagnant = None):
        fichier = open("liste_des_parties_effectue.txt", "r")
        liste = fichier.readlines()
        prem_ligne = liste[0].split(".")
        score = prem_ligne[1].split("_")
        if gagnant != None:
            if gagnant == 1:
                score[0] = str(int(score[0]) + 1)
            else:
                score[1] = str(int(score[1]) + 1)
        fichier.close()

        texte_remplacement = ""
        texte_remplacement += prem_ligne[0] + "." + score[0] + "_" + score[1] + "." + prem_ligne[-1]
        for txt in liste[1::]:
            texte_remplacement += txt
        
        fichier = open("liste_des_parties_effectue.txt", "w")
        fichier.write(texte_remplacement)
        fichier.write("\n" + str(self.liste_coups) + str_type_fin)
        fichier.close()
 

    #----------------------------Fonction de recherche-------------------------
    # Fonction pour récupérer des segments pour ensuite chercher l'alignement

    # x et y sont les coordonnées du premier chiffre de la liste
    # dx et dy permettent d'avoir la direction du segement sur la grille : _\|/
    
    def recup_segment(self, longueur_segment, y, x, dy, dx): 
        return [self.grille[y+i*dy][x+i*dx] for i in range(longueur_segment)]     
    
    def recherche_n_aligne(self, longueur_alignement, test = False): 
        
        n = longueur_alignement
        liste_alignements = []
        hauteur, largeur = len(self.grille)-1, len(self.grille[0])
        
        for l in range(largeur):
            for h in range(hauteur):
                
                if self.grille[h][l] != 0:
                    
                    if l <= largeur-n:
                        if abs(sum(self.recup_segment(n, h, l, 0, 1))) == n:
                            liste_alignements.append([ h, l, h, l+n-1, self.grille[h][l]])
                            
                    if h <= hauteur-n:
                        if abs(sum(self.recup_segment(n, h, l, 1, 0))) == n:
                            liste_alignements.append([ h, l, h+n-1, l, self.grille[h][l]])
                            
                    if l <= largeur-n and h <= hauteur-n :
                        if abs(sum(self.recup_segment(n, h, l, 1, 1))) == n:
                            liste_alignements.append([ h, l, h+n-1, l+n-1, self.grille[h][l]])
                            
                    if l >= n-1 and h <= hauteur-n :
                        if abs(sum(self.recup_segment(n, h, l, 1, -1))) == n:
                            liste_alignements.append([ h, l, h-n+1, l+n-1, self.grille[h][l]])
                            
                if liste_alignements != [] and test :
                    return liste_alignements

        return liste_alignements
    
    
    #--------------------------------------------------------------------------
    # Premier test avec les menaces n-1

    def recherche_menaces_et_categ(self, longueur_alignement):  
        
        n = longueur_alignement
        liste_menaces = [ [ [[], [], []], [[], [], []] ] for _ in range(n-1)] + [[[], []]]  # liste_menaces[i] correspond aux menaces de longueur i+1
       
        hauteur, largeur = len(self.grille)-1, len(self.grille[0])
        h_max = max(self.grille[-1])
        
        for l in range(largeur):
            for h in range(hauteur):
                
                if l == 0 and  h >= hauteur - h_max :   # la 2e condition permet de regarder seulement les lignes contenant des jetons
                    segment = self.recup_segment(largeur, h, 0, 0, 1)
                    self.trouver_menaces(segment, liste_menaces)
                    
                if h == 0:                              # recherche verticale
                    segment = self.recup_segment(hauteur, 0, l, 1, 0)
                    self.trouver_menaces(segment, liste_menaces)
                    
                if l == 0  or  h == 0 :                 # recherche diagonale \
                    longueur_segment = min(largeur-l, hauteur-h)
                    segment = self.recup_segment(longueur_segment, h, l, 1, 1)
                    self.trouver_menaces(segment, liste_menaces)
                    
                if l == largeur -1 or h == 0:           # recherche antidiagonale /
                    longueur_segment = min(l+1, hauteur-h)
                    segment = self.recup_segment(longueur_segment, h, l, 1, -1)
                    self.trouver_menaces(segment, liste_menaces)
                
        return liste_menaces
    
    


    def trouver_menaces(self, segment, liste_menaces):
        
        s = segment
        b = [ False for _ in range(len(s))]
        for i in range(len(s)):
            if s[i]==0 or b[i]:
                continue
            if s[i]==1 or s[i]==-1 :
                saut=0
                nb_align=1
                debut=i
                fin=i
                while fin<len(s):
                    if s[debut]==s[fin]:
                        b[fin]=True
                        fin+=1
                        nb_align+=1
                    elif s[fin]==0:
                        if saut <2:
                            if fin+1<len(s) and s[fin+1]==s[debut]:
                                fin+=1
                                b[fin-1]=True
                                saut+=1
                            else:
                                fin-=1
                                break
                        else:
                            fin-=1
                            break
                    else:
                        fin-=1
                        break
                nb_align -= 1
            
            nb_pos = nb_align
            
            if debut>0 and s[debut-1] == 0 :
                nb_pos += 1
            if fin+1 < len(s) and s[fin+1] == 0:
                nb_pos += 1
            
            menace = [ nb_align, nb_pos, saut >= 1 ]
            jo = 0 if s[debut] == 1 else s[debut]
            if nb_align >= self.nb_aligne: liste_menaces[-1][jo].append(menace)
            else: liste_menaces[nb_align-1][jo][self.categ_menace(menace)].append(menace)        
            
    #----------------------Catégorisation des menaces-------------------------------
    # Types de menaces:
        # menace ouverte -> 1
        # menace mi-ouverte -> 0
        # menace fermée -> -1
    
    def categ_menace(self, menace):  # menace = [longueur_menace ,nb_pos ,possede_un_trou]
        n = self.nb_aligne
        if menace[0] == n-1 and menace[-1] :
            return 0 
        else:
            self.nb_aligne_pos = menace[1]
            if self.nb_aligne_pos == n:
                return 0
            else:
                if self.nb_aligne_pos < n:
                    return -1
                else:
                    return 1

    #--------------------------------------------------------------------------
   
    #----------------------------Minimax---------------------------------------
    # Fonction Minimax généralisée à toute fonction d'évaluation

    def Minimax(self, joueur, profondeur = profondeur-1):  # profondeur -1
        if profondeur == 0 or self.recherche_n_aligne(self.nb_aligne) != [] or self.fin_game:
            if self.type_eval == "Simple":
                return self.evaluation_simple()
            elif self.type_eval == "Complexe":
                return self.evaluation_complexe()
        else:
            PCL = self.prochain_coups_legaux()
            if joueur == 1:
                liste_val = []
                for i in PCL:
                    self.coup(i, True)
                    self.prochain_joueur()
                    liste_val.append(self.Minimax(-joueur, profondeur-1))
                    self.retirer_coup(True)
                return max(liste_val)
            else:
                liste_val = []
                for i in PCL:
                    self.coup(i, True)
                    self.prochain_joueur()
                    liste_val.append(self.Minimax(-joueur, profondeur-1))
                    self.retirer_coup(True)
                return min(liste_val)
            
    # Si on utilise la fonction d'évaluation simple alors Inf = 1 suffit

    def elagageAB(self, joueur, a, b, profondeur = profondeur -1):
        if profondeur == 0 or self.recherche_n_aligne(self.nb_aligne) != [] or self.fin_game:
            if self.type_eval == "Simple":
                return self.evaluation_simple()
            elif self.type_eval == "Complexe":
                return self.evaluation_complexe()
            
        else:
            PCL = self.prochain_coups_legaux()
            if joueur == 1: # le joueur qui veut maximiser
                v = -1_000_000 # -Inf
                for i in PCL:
                    self.coup(i, True)
                    self.prochain_joueur()
                    v = max(v, self.elagageAB(-joueur, a, b, profondeur-1))
                    self.retirer_coup(True)
                    if v >= b :
                        return v
                    a = max(a,v)
            else:
                v = 1_000_000 # Inf
                for i in PCL:
                    self.coup(i, True)
                    self.prochain_joueur()
                    v = min(v, self.elagageAB(-joueur, a, b, profondeur-1))
                    self.retirer_coup(True)
                    if v <= a :
                        return v
                    b = min(b,v)
            return v
                

            
    #---------------------détermination d'un meilleur coup--------------------------
    
    def deter_best_coup(self):
        liste = []
        PCL = self.prochain_coups_legaux()
        for colonne in PCL:
            self.coup(colonne, True)
            self.prochain_joueur()
            
            if self.type_algo == "Minimax":
                liste.append([self.Minimax(self.joueur, self.profondeur), colonne])
            elif self.type_algo == "Alpha-Beta":
                liste.append([self.elagageAB(self.joueur, -1_000_000, 1_000_000, self.profondeur), colonne])
            self.retirer_coup(True)
            
        return self.trouver_coup_centre(liste)


    def trouver_coup_centre(self, liste):
        nb_lignes = len(self.grille[0])
        mid, maxi = nb_lignes//2, liste[0]
        if self.joueur == 1:
            for (val,col) in liste :
                if val > maxi[0]:
                    maxi = [val,col]
                if val == maxi[0] and abs(col - mid) < abs(maxi[1] - mid):
                    maxi = [val,col]
            txt = f"meilleur coup :{maxi} joueur :{self.joueur}"
            self.afficher_console(txt, self.affiche_console)
        else:
            for (val,col)in liste :
                if val < maxi[0]:
                    maxi = [val,col]
                if val == maxi[0] and abs(col - mid) < abs(maxi[1] - mid):
                    maxi = [val,col]
            txt = f"meilleur coup :{maxi} joueur :{self.joueur}"
            self.afficher_console(txt, self.affiche_console)
        return maxi[1]
    
    #--------------------------------------------------------------------------

    def maj_etat_joueurs_eval_algo(self):
        self.type_j1 = self.affichage_tkinter.set_joueur_1.get()
        self.type_j2 = self.affichage_tkinter.set_joueur_2.get()
        self.type_algo = self.affichage_tkinter.set_type_algo.get()
        self.type_eval = self.affichage_tkinter.set_type_eval.get()


    #--------------------------------------------------------------------------


    def mise_a_jour(self):
        if self.affiche_tkinter :
            self.maj_etat_joueurs_eval_algo()
                    
        jo = self.joueur
        if not self.fin_game:
            if self.liste_prochain_coups != [] and self.types_de_joueur[jo] == "humain" :            
                    
                colonne=self.liste_prochain_coups[0]
                self.deter_best_coup() # pour afficher le meilleur coup
                
                # faire le coup dans la grille avec l'information de la colone
                if colonne in self.prochain_coups_legaux():
                    self.coup(colonne)
                    # self.afficher_console()
                    if self.affiche_tkinter:
                        self.affichage_tkinter.maj_tkinter()
                    if self.affiche_console:
                        self.afficher_console()
                    # self.afficher_liste(self.recherche_menaces_et_categ(self.nb_aligne),"liste_menaces :")

                    self.afficher_console("éval complexe humain:" + str(self.evaluation_complexe()), self.affiche_console)
                    
                    self.prochain_joueur()

                    
                self.liste_prochain_coups.pop(0)
                self.test_fin_game()
                self.afficher_console("\n" + "coup numéro :" + str(len(self.liste_coups)+1), self.affiche_console)
                self.mise_a_jour()

            if self.types_de_joueur[jo] == "bot": 
                coup = self.deter_best_coup()
                self.coup(coup)
                if self.affiche_tkinter:
                    self.affichage_tkinter.maj_tkinter()
                if self.affiche_console:
                    self.afficher_console()
                self.afficher_console("éval complexe bot:" + str(self.evaluation_complexe()), self.affiche_console)

                self.test_fin_game()
                self.prochain_joueur()
                self.afficher_console("\n" + "coup numéro :" + str(len(self.liste_coups)+1), self.affiche_console)

                self.mise_a_jour()
        

    #----------------------Fonctions d'évaluations-----------------------------
    

    # Fonction d'évaluation simple qui renvoit 1 si le joueur 1 a aligné n jetons, -1 si c'est le joueur 2, 0 si ce n'est aucun d'eux 
    def evaluation_simple(self):
        liste = self.recherche_n_aligne(self.nb_aligne, True) # le "True" sert à sortir de la fonction au premier alignement trouvé => meilleure complexité
        if liste == []:
            return 0
        else:
            return liste[0][-1] * 1_000_000 # pour coincider avec la fonction d'évaluation complexe
    
    # Calcul des valeurs du tableau de coefficients des menaces moindres
    
    def tableau_coef_menaces_moindres_Aglin(self):
        n = self.nb_aligne
        tab = [0 for i in range(2*(n-3)+1)]
        pas = 10/len(tab)
        temp = pas
        tab[0] = temp
        if n > 3:
            for i in range(len(tab)-2):
                temp += pas
                tab[i+2] = temp
                temp += pas
                tab[i+1] = temp
        return tab


    def tableau_coef_menaces_moindres_arithmetique(self):
        n = Jeu.nbaligne
        return [ 10*i for i in range(n) ]
        
    
    # Fonction d'évaluation plus complexe : le joueur 1 est caractérisé par une valeur positive
    def evaluation_complexe(self):
        liste_menace = self.recherche_menaces_et_categ(self.nb_aligne)
        
        if self.nb_aligne == 3: # je suppose que n >= 3
            A = 1_000_000*len(liste_menace[-1][0]) + 250*len(liste_menace[-2][0][1]) + 80*len(liste_menace[-2][0][0]) + 10*len(liste_menace[-3][0][1])
            B = 1_000_000*len(liste_menace[-1][1]) + 5020*len(liste_menace[-2][1][1]) + 2000*len(liste_menace[-2][1][0]) + 10*len(liste_menace[-3][1][1])
        else: 
            
            A = 1_000_000*len(liste_menace[-1][0]) + 250*len(liste_menace[-2][0][1]) + 80*len(liste_menace[-2][0][0]) 
            B = 1_000_000*len(liste_menace[-1][1]) + 5020*len(liste_menace[-2][1][1]) + 2000*len(liste_menace[-2][1][0]) 
        
        tab_coef = self.tableau_coef_menaces_moindres_Aglin()

        return A-B
               

if __name__=='__main__':
    Jeu()