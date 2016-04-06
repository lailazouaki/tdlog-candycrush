#*********************************************************
# TP3
# Laïla Zouaki
#*********************************************************

import sys

from PyQt4 import QtGui, QtCore
from random import randint

# Pour ce TP, j'ai utilisé l'architecture Modele/Vue que Qt permet de mettre en oeuvre 
# grâce aux objets QStandardItemModel, QItemSelectionModel et QTableView

# Dans tout le code, les objets "case" sont de type QModelIndex et permettent d'avoir 
# accès aux coordonnées de la case courante et de la case précédente grâce au signal 
# currentChanged.

# Remarques : plusieurs choses ne fonctionnent pas (un week-end entier ne suffit pas...!)
# - On ne peut pas faire des alignements de plus de 3 cases identiques. Par contre, un bonus est accordé lors de réactions en cascade
# - Je n'ai pas réussi à créer mes propres signaux pour pouvoir afficher le score au fur et à mesure sur la fenêtre. 
# Du coup, j'ai laissé les print dans la console
# - Parfois, une erreur RunTimeError s'affiche : "RuntimeError: wrapped C/C++ object of type QStandardItem has been deleted". 
# Je n'ai pas su la corriger (elle n'a lieu qu'occasionnellement), mais bon ça ne fait pas planter le jeu...
# - Je n'ai pas fait de fonction pour vérifier qu'il existe encore des possibiltés 
# - On ne voit pas forcément très bien ce qui se passe lorsqu'on bouge les cases mais normalement ça fonctionne bien!
# - Les clics ne sont pas symétriques : il faut amener la case qui va réaliser l'alignement à sa place. 
# Essayer de bouger la case qui va être remplacée ne marchera pas. 

class Fenetre(QtGui.QMainWindow):
	def __init__(self, modele):

		super().__init__(None)
		self.modele = modele
		self.initUI()

	def initUI(self):
		self.setGeometry(200, 100, 700, 700)

		zoneCentrale = QtGui.QWidget()
		self.setCentralWidget(zoneCentrale)

		layout = QtGui.QGridLayout()
		zoneCentrale.setLayout(layout)

		vue = QtGui.QTableView()
		vue.setShowGrid(False)

		vue.verticalHeader().setVisible(False)
		vue.verticalHeader().setDefaultSectionSize(90)

		vue.horizontalHeader().setVisible(False)
		vue.horizontalHeader().setDefaultSectionSize(90)

		vue.setModel(self.modele)
		vue.setSelectionModel(QtGui.QItemSelectionModel(self.modele, vue))

		# Lorsque la case sélectionnée est modifiée, le jeu est lancé
		vue.selectionModel().currentChanged.connect(self.modele.case_selectionnee)
		
		layout.addWidget(vue)

class Modele(QtGui.QStandardItemModel):

	# Constructeur
	def __init__(self, taille_grille=7):

		self.taille_grille = taille_grille
		self.case_courante = None
		self.case_precedente = None
		self.score = 0
		self.coups = 10

		super().__init__(self.taille_grille, self.taille_grille)
		
		items = [QtGui.QStandardItem(str(randint(1, self.taille_grille))) for i in range(self.taille_grille*self.taille_grille)]
		positions = [(i,j) for i in range(self.taille_grille) for j in range(self.taille_grille)]

		for position, item in zip(positions, items):
			self.setItem(position[0], position[1], item)
			item.setEditable(False)

		self.validite_grille_initiale()
		self.initIcons()

	# Initialise les icones en fonction de la valeur de la case
	def initIcons(self):

		positions = [(i,j) for i in range(self.taille_grille) for j in range(self.taille_grille)]

		for position in positions:
			if self.item(position[0], position[1]).text() == "1":
				pixmap = QtGui.QPixmap("figure_1.png")
			elif self.item(position[0], position[1]).text() == "2":
				pixmap = QtGui.QPixmap("figure_2.png")
			elif self.item(position[0], position[1]).text() == "3":
				pixmap = QtGui.QPixmap("figure_3.png")
			elif self.item(position[0], position[1]).text() == "4":
				pixmap = QtGui.QPixmap("figure_4.png")
			elif self.item(position[0], position[1]).text() == "5":
				pixmap = QtGui.QPixmap("figure_5.png")
			elif self.item(position[0], position[1]).text() == "6":
				pixmap = QtGui.QPixmap("figure_6.png")
			elif self.item(position[0], position[1]).text() == "7":
				pixmap = QtGui.QPixmap("figure_7.png")

			icone = QtGui.QIcon(pixmap)
			self.item(position[0], position[1]).setIcon(icone)

	# Permet de vérifier qu'il n'y a pas de cases alignées au début du jeu, et de les changer s'il y en a
	def validite_grille_initiale(self):

		positions = [(i, j) for i in range(self.taille_grille) for j in range(self.taille_grille)]

		# Pour la validité de la grille, on teste seulement s'il y en a trois alignés (on se fiche de savoir s'il y en a plus)
		for position in positions:
			# Si on n'est pas dans un coin particulier (bas gauche ou haut droit ou bas droit) 
			if position[0] <= self.taille_grille-3 and position[1] <= self.taille_grille-3:
				if self.egalite_cases(position[0], position[1], "BAS"):
					self.regenerer_case(position[0], position[1], "BAS")
			
				# Même processus à droite de la case actuelle
				if self.egalite_cases(position[0], position[1], "DROITE"):
					self.regenerer_case(position[0], position[1], "DROITE")

			# Dernière colonne et avant dernière colonne : processus sur les cases en dessous
			elif position[0] <= self.taille_grille-3 and (position[1] == self.taille_grille-2 or position[1] == self.taille_grille-1):
				if self.egalite_cases(position[0], position[1], "BAS"):
					self.regenerer_case(position[0], position[1], "BAS")

			# Dernière ligne et avant dernière ligne : processus sur les cases de droite
			elif position[1] <= self.taille_grille-3 and (position[0] == self.taille_grille-2 or  position[1] == self.taille_grille-1):
				if self.egalite_cases(position[0], position[1], "DROITE"):
					self.regenerer_case(position[0], position[1], "DROITE")

	def case_selectionnee(self, case_courante, case_precedente):

		# S'il reste encore des coups à jouer 
		if self.coups > 0:
			self.case_courante = case_courante
			self.case_precedente = case_precedente

			# On vérifie si les cases sélectionnées sont voisines
			self.cases_voisines()

		# Sinon, on arrête de jouer
		else:
			print("C'est la fin du jeu ! ")
			print("Bravo, tu as marqué {} points ! ".format(self.score))
			return True

	# Vérifie si la case précédente et la case courante sont voisines
	def cases_voisines(self):
		# Teste si les deux cases sont sur la même ligne
		if self.case_courante.row() == self.case_precedente.row():
			if self.case_courante.column() == self.case_precedente.column()-1 or self.case_courante.column() == self.case_precedente.column()+1:
				# Si les cases sont voisines, on appelle la méthode echanger_cases pour voir si on peut marquer des points en bougeant ces deux cases
				self.echanger_cases()
				return True

		# Teste si les deux cases sont sur la même colonne
		elif self.case_courante.column() == self.case_precedente.column():
			if self.case_courante.row() == self.case_precedente.row()-1 or self.case_courante.row() == self.case_precedente.row()+1:
				# Si les cases sont voisines, on appelle la méthode echanger_cases pour voir si on peut marquer des points en bougeant ces deux cases
				self.echanger_cases()
				return True

		# Si les cases ne sont pas voisines, on ne fait rien

	# Permet un échange éventuellement temporaire de la case courante et la case précédente
	# Si, en échangeant, on aligne trois cases identiques, on garde le changement
	# Sinon, on revient à la configuration initiale
	def echanger_cases(self):

		# Echange seulement la valeur des cases
		self.echanger_valeur()

		directions = ["BAS", "DROITE", "HAUT", "GAUCHE", "CENTRE_H", "CENTRE_V"]

		for direction in directions:

			# Si, en échangeant, on aligne trois cases identiques dans la direction "direction"
			if self.egalite_cases(self.case_courante.row(), self.case_courante.column(), direction, "JEU"):
				self.score += 20
				self.coups -= 1
				print("Bravo, +20 points !")
				print("Score : {}".format(self.score))
				print("Plus que {} coups ! ".format(self.coups))

				# On échange aussi les icones
				self.echanger_icones()

				# On applique la gravité pour faire tomber les cases au dessus
				self.gravite(direction, self.case_courante)

				# On vérifie si la gravité a créé des alignements identiques
				self.reaction_cascade()
				return True

		# L'échange n'a pas donné d'alignement identique, on revient à la configuration initiale
		self.echanger_valeur()

	def echanger_valeur(self):
		valeur_precedente = self.item(self.case_precedente.row(), self.case_precedente.column()).text()
		valeur_courante = self.item(self.case_courante.row(), self.case_courante.column()).text()
		
		self.item(self.case_precedente.row(), self.case_precedente.column()).setText(valeur_courante)
		self.item(self.case_courante.row(), self.case_courante.column()).setText(valeur_precedente)

	def echanger_icones(self):
		icone_precedente = self.item(self.case_precedente.row(), self.case_precedente.column()).icon()
		icone_courante = self.item(self.case_courante.row(), self.case_courante.column()).icon()

		self.item(self.case_precedente.row(), self.case_precedente.column()).setIcon(icone_courante)
		self.item(self.case_courante.row(), self.case_courante.column()).setIcon(icone_precedente)

	def egalite_cases(self, case_i, case_j, direction, mode="INITIALISATION"):

		# Le mode "INITIALISATION" permet de corriger la grille initiale : 
		# S'il y a trois cases alignées, on en modifie une pour que ce ne soit plus le cas
		if mode == "INITIALISATION":
			if direction == "BAS":
				if self.item(case_i, case_j).text() == self.item(case_i+1, case_j).text():
					if self.item(case_i, case_j).text() == self.item(case_i+2, case_j).text():
						return True
				return False

			elif direction == "DROITE":
				if self.item(case_i, case_j).text() == self.item(case_i, case_j+1).text():
					if self.item(case_i, case_j).text() == self.item(case_i, case_j+2).text():
						return True
				return False

		# Le mode "JEU" permet seulement de détecter la présence d'un alignement de trois cases identiques
		if mode == "JEU":
			if direction == "BAS":
				if case_i+1 <= self.taille_grille-1 and self.item(case_i, case_j).text() == self.item(case_i+1, case_j).text():
					if case_i+2 <= self.taille_grille-1 and self.item(case_i, case_j).text() == self.item(case_i+2, case_j).text():
						return True
				return False

			elif direction == "DROITE":
				if case_j+1 <= self.taille_grille-1 and self.item(case_i, case_j).text() == self.item(case_i, case_j+1).text():
					if case_j+2 <= self.taille_grille-1 and self.item(case_i, case_j).text() == self.item(case_i, case_j+2).text():
						return True
				return False

			elif direction == "HAUT":
				if case_i-1 >= 0 and self.item(case_i, case_j).text() == self.item(case_i-1, case_j).text():
					if case_i-2 >= 0 and self.item(case_i, case_j).text() == self.item(case_i-2, case_j).text():
						return True
				return False

			elif direction == "GAUCHE":
				if case_j-1 >= 0 and self.item(case_i, case_j).text() == self.item(case_i, case_j-1).text():
					if case_j-2 >= 0 and self.item(case_i, case_j).text() == self.item(case_i, case_j-2).text():
						return True
				return False

			# Seuls cas où il peut y avoir des alignements plus grands
			# CENTRE_H = centre_horizontal : la case courante est placée horizontalement entre deux cases identiques à celle-ci
			elif direction == "CENTRE_H":
				if case_j-1 >= 0 and self.item(case_i, case_j).text() == self.item(case_i, case_j-1).text():
					if case_j+1 <=self.taille_grille-1 and self.item(case_i, case_j).text() == self.item(case_i, case_j+1).text():
						return True
				return False

			# CENTRE_V = centre_vertical : la case courante est placée verticalement entre deux cases identiques à celle-ci
			elif direction == "CENTRE_V":
				if case_i-1 >= 0 and self.item(case_i, case_j).text() == self.item(case_i-1, case_j).text():
					if case_i+1 <= self.taille_grille-1 and self.item(case_i, case_j).text() == self.item(case_i+1, case_j).text():
						return True
				return False

	def regenerer_case(self, case_i, case_j, direction, mode="INITIALISATION"):

		# Regénère une case pour valider la grille initiale
		if mode == "INITIALISATION":
			if direction == "BAS":
				while self.item(case_i+1, case_j).text() == self.item(case_i+2, case_j).text():
					self.setItem(case_i+2, case_j, QtGui.QStandardItem(str(randint(1, self.taille_grille))))

			elif direction == "DROITE":
				while self.item(case_i, case_j+1).text() == self.item(case_i, case_j+2).text():
					self.setItem(case_i, case_j+2, QtGui.QStandardItem(str(randint(1, self.taille_grille))))

		# Regénère des cases après avoir appliqué la gravité
		elif mode == "JEU":
			if direction == "GAUCHE":
				self.setItem(case_i, case_j, QtGui.QStandardItem(str(randint(1, self.taille_grille))))
				self.setItem(case_i, case_j-1, QtGui.QStandardItem(str(randint(1, self.taille_grille))))
				self.setItem(case_i, case_j-2, QtGui.QStandardItem(str(randint(1, self.taille_grille))))
				self.initIcons()

			elif direction == "DROITE":
				self.setItem(case_i, case_j, QtGui.QStandardItem(str(randint(1, self.taille_grille))))
				self.setItem(case_i, case_j+1, QtGui.QStandardItem(str(randint(1, self.taille_grille))))
				self.setItem(case_i, case_j+2, QtGui.QStandardItem(str(randint(1, self.taille_grille))))
				self.initIcons()

			elif direction == "HAUT":
				self.setItem(case_i, case_j, QtGui.QStandardItem(str(randint(1, self.taille_grille))))
				self.initIcons()

	# Renvoie la case voisine dans une direction donnée
	# La variable portee permet d'obtenir une case voisine au delà de la case voisine directe dans une direction donnée
	def get_voisin(self, case, direction, portee=1):

		if case.column()-portee >= 0 and direction == "GAUCHE":
			return self.item(case.row(), case.column()-portee)

		elif case.column()+portee <= self.taille_grille-1 and direction == "DROITE":
			return self.item(case.row(), case.column()+portee)

		elif case.row()+portee <= self.taille_grille-1 and direction == "BAS":
			return self.item(case.row()+portee, case.column())

		elif case.row()-portee >= 0 and direction == "HAUT":
			return self.item(case.row()-portee, case.column())

		return False

	def remplacer_case(self, ancienne_case, nouvelle_case):
		nouvelle_valeur = self.item(nouvelle_case.row(), nouvelle_case.column()).text()
		nouvelle_icone = self.item(nouvelle_case.row(), nouvelle_case.column()).icon()

		self.item(ancienne_case.row(), ancienne_case.column()).setText(nouvelle_valeur)
		self.item(ancienne_case.row(), ancienne_case.column()).setIcon(nouvelle_icone)

	def gravite(self, direction, case_courante): 

		if direction == "GAUCHE" or direction == "DROITE":
			if case_courante.row() > 0:
				voisins = [case_courante]
				
				# On considere les deux cases à gauche (resp. à droite) de la case courante 
				if self.get_voisin(case_courante, direction) != False:
					voisins.append(self.get_voisin(case_courante, direction))
					voisins.append(self.get_voisin(voisins[1], direction))

				# Pour chacune de ces cases, on remplace par la case au dessus 
				for voisin in voisins:
					self.remplacer_case(voisin, self.get_voisin(voisin, "HAUT"))

				# On réapplique la gravité sur la ligne au dessus 
				self.gravite(direction, self.get_voisin(case_courante, "HAUT"))

			if case_courante.row() == 0:
				# Lorsqu'on arrive en haut, on génère une nouvelle case 
				self.regenerer_case(case_courante.row(), case_courante.column(), direction, "JEU")

		# Même principe général pour les autres directions
		elif direction == "HAUT":
			if self.get_voisin(case_courante, "HAUT", 3) != False:
				self.remplacer_case(case_courante, self.get_voisin(case_courante, "HAUT", 3))
				self.gravite(direction, self.get_voisin(case_courante, "HAUT"))

			else:
			 	[self.regenerer_case(i, case_courante.column(), direction, "JEU") for i in range(0, case_courante.row())]

		elif direction == "BAS":
			self.gravite("HAUT", self.get_voisin(case_courante, "BAS", 2))

		elif direction == "CENTRE_V":
			self.gravite("HAUT", self.get_voisin(case_courante, "BAS", 1))

		elif direction == "CENTRE_H":
			self.afficher_case(case_courante)
			self.gravite("GAUCHE", self.get_voisin(case_courante, "GAUCHE"))

		# On vérifie si la gravité a créé des alignements de trois cases identiques
		self.reaction_cascade()

	# Pour chaque case du jeu, on regarde dans toutes les directions s'il y a un alignement de trois cases identiques
	def reaction_cascade(self):

		directions = ["BAS", "DROITE", "HAUT", "GAUCHE", "CENTRE_H", "CENTRE_V"]
		coefficient_bonus = 2

		positions = [(i,j) for i in range(self.taille_grille) for j in range(self.taille_grille)]

		for position in positions:
			for direction in directions:
				if self.egalite_cases(position[0], position[1], direction, "JEU"):
					print("Bravo, réaction en cascade en ({},{})!".format(position[0], position[1]))
					print("Score : {}".format(self.score))
					self.score += 20*coefficient_bonus
					coefficient_bonus += 1

					# .index() permet de retourner le QModelIndex correspondant aux objets "case"
					self.gravite(direction, self.item(position[0], position[1]).index())

	def afficher_case(self, case):

		print("Case ({},{}) a pour valeur {}".format(case.row(), case.column(), self.item(case.row(), case.column()).text()))




application = QtGui.QApplication(sys.argv)
modele = Modele(7)
fenetre = Fenetre(modele)
fenetre.show()

sys.exit(application.exec_())
