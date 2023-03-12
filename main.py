class Prog_source:

    def __init__(self, adresse):
        self.adresse = adresse
        self.table_symbole = [";", ".", ",", "=", "+", "-", "*", "/", "(", ")", "<", ">", ":"]
        self.t_UNILEX = ["motcle", "ident", "ent", "ch", "virg", "ptvirg", "point", "deuxpts", "parouv",
                         "parfer", "sup", "eg", "plus", "moins", "mult", "divi", "diff", "aff"]
        self.table_mot_reserve = ["const", "debut", "ecrire", "fin", "lire", "programme", "var"]
        self.LONG_MAX_ENT = 20
        self.LONG_MAX_CHAINE = 50
        self.MAX_INT = 32767
        self.NB_MOT_RESERVE = 7
        self.TAILLE_HASHMAP = 5

        self.fin = False
        self.source = ""
        self.file = None
        self.table_lexeme = []
        self.table_ident = [[] for _ in range(self.TAILLE_HASHMAP)]
        self.arbre_syntaxique = None
        self.last_node = None
        self.to_treat_node = None
        self.num_point = 0
        self.num_ligne = 1
        self.CARLU = ""
        self.UNILEX = ""
        self.nombre = 0
        self.CHAINE = ""
        self.nb_const_CHAINE = 0
        self.VAL_CONST_CHAINE = []
        self.derniere_adresse_var = 0
        self.message_erreur = ""

    # reconnaitre toute les unités lexicales du fichier
    def analyse_lexicale(self):
        self.initialiser()
        self.lire_car()
        while not self.fin:
            self.UNILEX = self.analex()
            self.table_lexeme.append(self.UNILEX)
            print(self.UNILEX)
        self.terminer()

    def analyse_lexicale_partie2(self):
        self.initialiser()
        self.lire_car()
        while not self.fin:
            if self.analex() == "ident":
                if self.chercher(self.CHAINE, conversion(self.CHAINE)%self.TAILLE_HASHMAP) == -1:
                    self.inserer(self.CHAINE, "constante", "CHAINE de caractère")
        self.terminer()
        self.afficher_table_ident()

    def analyse(self):
        self.initialiser()
        self.lire_car()
        self.anasynt()
        self.terminer()
        self.afficher_table_ident()
        print(self.arbre_syntaxique)

    #lit un caractère de notre fichier
    def lire_car(self):
        if self.num_point == len(self.source) and self.CARLU != "\n":
            self.fin = True
            self.CARLU = ""
            return
        self.CARLU = self.source[self.num_point]
        self.num_point += 1
        while self.CARLU == "\n":
            self.source = self.file.readline()
            if self.source == "":
                self.CARLU =""
                return
            self.num_point = 0
            self.num_ligne += 1
            self.CARLU = self.source[self.num_point]
            self.num_point += 1
        return

    def initialiser(self):
        self.file = open(self.adresse + ".txt", "r")
        self.source = self.file.readline()
        return

    def analex(self):
        self.table_lexeme.append(self.UNILEX)
        if self.CARLU == " " or self.CARLU == "{" or self.CARLU == "	":
            self.sauter_separateur()
        if self.CARLU.isnumeric():
            return self.reco_entier()
        elif self.CARLU == "'":
            return self.reco_CHAINE()
        elif self.CARLU.isalpha():
            return self.reco_ident_ou_mot_reserve()
        elif self.CARLU in self.table_symbole:
            return self.reco_symb()
        elif self.CARLU == "" and self.CHAINE == "fin" and self.UNILEX == "motcle":
            return ""
        elif self.CARLU == "":
            self.erreur(0)
        elif self.CARLU == "}":
            self.erreur(0.2)
        else:
            self.erreur(6)

    ##va sauter tout { et si ils sont imbriquer
    def sauter_separateur(self):
        count_com = 0
        while self.CARLU == " " or self.CARLU == "	" or self.CARLU == "{" or count_com != 0:
            if self.CARLU == "{":
                count_com += 1
            elif self.CARLU == "}":
                count_com -= 1
            elif self.CARLU == "":
                self.erreur(0.1)
            self.lire_car()
        return
    #il va reconnaitre un entier et si c'en est un il va continuer
    def reco_entier(self):
        nombre = ""
        while self.CARLU.isnumeric():
            nombre += self.CARLU
            self.lire_car()
        while self.CARLU.isnumeric():
            nombre += self.CARLU
            self.lire_car()

        self.nombre = int(nombre)
        if self.nombre > self.MAX_INT:
            self.erreur(1)
        else:
            return "ent"
    #idem que reco entier mais avec des caractères maintenante
    def reco_CHAINE(self):
        self.CHAINE = ""
        while self.CARLU == "'":
            self.lire_car()
            while self.CARLU != "'":
                self.CHAINE += self.CARLU
                self.lire_car()
            self.CHAINE += self.CARLU
            self.lire_car()
        self.CHAINE = self.CHAINE[:-1]

        if len(self.CHAINE) > self.LONG_MAX_CHAINE:
            self.erreur(2)
        else:
            return "ch"
    #reconnait si c'est une ident ou un mot reserver
    def reco_ident_ou_mot_reserve(self):
        self.CHAINE = ""
        compteur = 0
        while self.CARLU.isalpha() or self.CARLU.isnumeric() or self.CARLU == "_":
            if compteur <= self.LONG_MAX_ENT:
                if self.CARLU.isalpha():
                    self.CHAINE += self.CARLU.lower()
                else:
                    self.CHAINE += self.CARLU
                compteur += 1
                self.lire_car()
            else:
                self.lire_car()

        if self.est_mot_reserve():
            return "motcle"
        else:
            return "ident"
    #symbole cette fois si
    def reco_symb(self):
        car = self.CARLU
        self.lire_car()
        if car == ";":
            return "ptvirg"
        elif car == ",":
            return "virg"
        elif car == ".":
            return "point"
        elif car == "=":
            return "eg"
        elif car == "+":
            return "plus"
        elif car == "-":
            return "moins"
        elif car == "*":
            return "mult"
        elif car == "/":
            return "divi"
        elif car == "(":
            return "parouv"
        elif car == ")":
            return "parfer"

        elif car == "<":
            if self.CARLU == "=":
                self.lire_car()
                return "infe"
            elif self.CARLU == ">":
                self.lire_car()
                return "diff"
            else:
                return "inf"

        elif car == ">":
            if self.CARLU == "=":
                self.lire_car()
                return "supe"
            else:
                return "sup"

        elif car == ":":
            if self.CARLU == "=":
                self.lire_car()
                return "aff"
            else:
                return "deuxpts"
    #donc va dire si oui ou non un mot reserver
    def est_mot_reserve(self):
        i = 0
        while i < self.NB_MOT_RESERVE and self.table_mot_reserve[i] < self.CHAINE:
            i = i + 1
        return self.table_mot_reserve[i] == self.CHAINE

    # va chercher dans la table des mots reserver et dire si oui ou non
    def chercher(self, nom, cle_hashtable):
        for i in range(len(self.table_ident[cle_hashtable])):
            if self.table_ident[cle_hashtable][i].get_name() == nom:
                return i
        return -1

    def inserer(self, nom, t_ident, typ):
        cle_hashtable = conversion(nom) % self.TAILLE_HASHMAP
        if self.chercher(nom, cle_hashtable) != -1:
            self.erreur(4)
        if t_ident == "constante" and typ == "entier":
            self.table_ident[cle_hashtable].append(Enreg_ident(nom, t_ident, self.nombre, typ))
        elif t_ident == "constante" and typ == "CHAINE de caractère":
            self.table_ident[cle_hashtable].append(Enreg_ident(nom, t_ident, self.CHAINE, typ))
        elif t_ident == "variable":
            self.table_ident[cle_hashtable].append(Enreg_ident(nom, t_ident, self.derniere_adresse_var, typ))
            self.derniere_adresse_var += 1

    def afficher_table_ident(self):
        for liste in self.table_ident:
            for enreg in liste:
                print(enreg)

    def anasynt(self):
        self.UNILEX = self.analex()
        if self.prog():
            print("Programme syntaxiquement correct")
        else:
            self.erreur(3)
        return
    #un nom pour le programme
    #une déclaration des constantes (si présente)
    #une déclaration des variables (si présente)
    #un bloc de instructions si il manque return false
    def prog(self):

        if not (self.UNILEX == "motcle" and self.CHAINE == "programme"):
            self.message_erreur = "'PROGRAMME' attendu au début du programme"
            return False

        node_p = Node("prog")
        self.arbre_syntaxique = node_p
        self.last_node = node_p
        self.UNILEX = self.analex()

        if not self.UNILEX == "ident":
            self.message_erreur = "nom du programme attendu"
            return False

        node_id = Node("titre", self.last_node)
        Node(self.CHAINE, node_id)
        self.UNILEX = self.analex()

        if not self.UNILEX == "ptvirg":
            self.message_erreur = "';' attendu aprés la déclaration du programme"
            return False
        self.UNILEX = self.analex()

        if self.UNILEX == "motcle" and self.CHAINE == "const":
            self.last_node = Node(self.CHAINE, self.last_node)
            if not self.decl_cons():
                return False
            self.last_node = self.last_node.get_parent()

        if self.UNILEX == "motcle" and self.CHAINE == "var":
            self.last_node = Node(self.CHAINE, self.last_node)
            if not self.decl_var():
                return False
            self.last_node = self.last_node.get_parent()

        if not (self.UNILEX == "motcle" and self.CHAINE == "debut"):
            self.message_erreur = "déclaration des variables, des constantes ou bloc attendu après déclaration programme"
            return False
        self.last_node = Node("bloc", self.last_node)
        return self.bloc()
    #Elle vérifie si la déclaration commence par la chaîne de caractères "CONST", puis lit les constantes suivantes et vérifie si elles sont valides.
    #la fonction vérifie si chaque constante est déclarée avec un nom unique, qui ne peut pas être un mot-clé du langage de programmation,
    # et est suivie par un signe égal = et une valeur entière ou une chaîne de caractères.
    def decl_cons(self):

        if not (self.UNILEX == "motcle" and self.CHAINE == "const"):
            self.message_erreur = "'CONST' attendu au début de la déclaration des constante"
            return False
        self.UNILEX = self.analex()

        if not self.UNILEX == "ident":
            self.message_erreur = "les identificateurs de constantes doivent être différents des mot-clé, commencer par une lettre et ne contenir que des lettes, chiffres et _"
            return False
        nom_constante = self.CHAINE
        node_cons = Node(self.CHAINE, self.last_node)
        self.UNILEX = self.analex()
        if not self.UNILEX == "eg":
            self.message_erreur = "l'identificateur de constante doit être suivi de sa valeur séparée par un =, de plus la constante doit ne contenir que des lettes, chiffres et _"
            return False
        self.UNILEX = self.analex()

        if not (self.UNILEX == "ent" or self.UNILEX == "ch"):
            self.message_erreur = "la constante doit être une CHAINE de caractère ou un entier"
            return False
        self.set_const(nom_constante)
        if self.UNILEX == "ent":
            Node(str(self.nombre), node_cons)
        else:
            Node(self.CHAINE, node_cons)
        self.UNILEX = self.analex()

        while self.UNILEX == "virg":
            self.UNILEX = self.analex()

            if not self.UNILEX == "ident":
                self.message_erreur = "les identificateurs de constantes doivent être différents des mot-clé, commencer par une lettre et ne contenir que de lettes, chiffres et _"
                return False
            node_cons = Node(self.CHAINE, self.last_node)
            nom_constante = self.CHAINE
            self.UNILEX = self.analex()

            if not self.UNILEX == "eg":
                self.message_erreur = "l'identificateur de constante doit être suivi de sa valeur séparée par un =, de plus la constante doit ne contenir que des lettes, chiffres et _"
                return False
            self.UNILEX = self.analex()

            if not (self.UNILEX == "ent" or self.UNILEX == "ch"):
                self.message_erreur = "la constante doit être une CHAINE de caractère ou un entier"
                return False
            self.set_const(nom_constante)
            if self.UNILEX == "ent":
                Node(str(self.nombre), node_cons)
            else:
                Node(self.CHAINE, node_cons)
            self.UNILEX = self.analex()

        if not self.UNILEX == "ptvirg":
            self.message_erreur = "';' attendu à la fin de la déclarations des constantes et ',' entre celle ci"
            return False
        self.UNILEX = self.analex()
        return True
    #Elle vérifie si la déclaration commence par la chaîne de caractères "VAR", puis lit les variables suivantes et vérifie si elles sont valides.
    #la fonction vérifie si chaque variable est déclarée avec un nom unique, qui ne peut pas être un mot-clé du langage de programmation et commence par une lettre
    def decl_var(self):

        if not (self.UNILEX == "motcle" and self.CHAINE == "var"):
            self.message_erreur = "'VAR' attendu au début de la déclaration des variables"
            return False
        self.UNILEX = self.analex()

        if not self.UNILEX == "ident":
            self.message_erreur = "les identificateurs de variables doivent être différents des mot-clé, commencer par une lettre et ne contenir que de lettes, chiffres et _"
            return False
        self.set_var()
        Node(self.CHAINE, self.last_node)
        self.UNILEX = self.analex()

        while self.UNILEX == "virg":
            self.UNILEX = self.analex()

            if not self.UNILEX == "ident":
                self.message_erreur = "les identificateurs de variables doivent être différents des mot-clé, commencer par une lettre et ne contenir que de lettes, chiffres et _"
                return False
            self.set_var()
            node_cons = Node(self.CHAINE, self.last_node)
            self.UNILEX = self.analex()

        if not self.UNILEX == "ptvirg":
            self.message_erreur = "';' attendu à la fin de la déclarations des variables et ',' entre celle ci"
            return False
        self.UNILEX = self.analex()
        return True
    #vérifie si le bloc commence par la chaîne de caractères "DEBUT" et se termine par
    # "FIN", puis lit les instructions suivantes et vérifie si elles sont valides.
    def bloc(self):

        if not (self.UNILEX == "motcle" and self.CHAINE == "debut"):
            self.message_erreur = "'DEBUT' attendu au début du bloc d'instruction"
            return False
        self.UNILEX = self.analex()

        if not (self.UNILEX == "ident" or (self.UNILEX == "motcle" and self.CHAINE == "lire") or (
                self.UNILEX == "motcle" and self.CHAINE == "ecrire") or (
                        self.UNILEX == "motcle" and self.CHAINE == "debut")):
            self.message_erreur = "au moins une instruction attendu à dans un bloc"
            return False

        if not self.instruction():
            return False

        if self.UNILEX != "ptvirg":
            self.message_erreur = "';' attendu à la fin des instrutions"
            return False
        self.UNILEX = self.analex()

        while self.UNILEX == "ident" or (self.UNILEX == "motcle" and self.CHAINE == "lire") or (
                self.UNILEX == "motcle" and self.CHAINE == "ecrire") or (
                self.UNILEX == "motcle" and self.CHAINE == "debut"):

            if not self.instruction():
                return False

            if self.UNILEX != "ptvirg":
                self.message_erreur = "';' attendu à la fin des instrutions"
                return False
            self.UNILEX = self.analex()

        if not (self.UNILEX == "motcle" and self.CHAINE == "fin"):
            self.message_erreur = "un block ne doit contenir que des instruction et finir par un 'FIN'"
            return False
        self.UNILEX = self.analex()
        return True
    # Elle vérifie si l'instruction commence par un identifiant, par un mot-clé "ECRIRE" ou "LIRE", ou par un mot-clé "DEBUT",
    # puis utilise une autre fonction appropriée pour analyser l'instruction et vérifier si elle est valide.
    def instruction(self):
        if self.UNILEX == "ident":
            self.last_node = Node("affectation", self.last_node)
            return self.affectation()
        elif self.UNILEX == "motcle" and self.CHAINE == "ecrire":
            self.last_node = Node("ecrire", self.last_node)
            return self.ecriture()
        elif self.UNILEX == "motcle" and self.CHAINE == "lire":
            self.last_node = Node("lire", self.last_node)
            return self.lecture()
        elif self.UNILEX == "motcle" and self.CHAINE == "debut":
            self.last_node = Node("bloc", self.last_node)
            return self.bloc()
        else:
            self.message_erreur = "une instruction ne doit commencer que par 'LIRE', 'ECRIRE', 'DEBUT', ou un identifiant pour l'affectation"
            return False
    # Elle vérifie si l'instruction commence
    # par un identifiant, puis par le symbole d'affectation ":=".
    def affectation(self):

        if not self.UNILEX == "ident":
            return False

        cle_hashtable = conversion(self.CHAINE) % self.TAILLE_HASHMAP
        index = self.chercher(self.CHAINE, cle_hashtable)
        if index == -1:
            self.erreur(5)
        if self.table_ident[cle_hashtable][index].is_cons():
            self.erreur(5.1)
        node_ = Node("var", self.last_node)
        Node(self.CHAINE, node_)
        self.UNILEX = self.analex()

        if not self.UNILEX == "aff":
            return False
        self.UNILEX = self.analex()
        if not self.exp():
            return False
        self.last_node.set_son(self.to_treat_node)
        self.last_node = self.last_node.get_parent()
        return True
    # Elle lit les identificateurs passés en argument à la fonction "lire" et vérifie que ces identificateurs sont valides (différents des mots-clés, commençant par une lettre,
    # ne contenant que des lettres, chiffres et caractères de soulignement).
    def lecture(self):

        if not (self.UNILEX == "motcle" and self.CHAINE == "lire"):
            self.message_erreur = "'LIRE' attendu au début de l'instruction de lecture"
            return False
        self.UNILEX = self.analex()
        if not self.UNILEX == "parouv":
            self.message_erreur = "'(' attendu aprés la fonction 'LIRE'"
            return False
        self.UNILEX = self.analex()

        if not self.UNILEX == "ident":
            self.message_erreur = "au moins un identificateur est attendu dans la fonction 'LIRE', les identificateurs doivent être différents des mot-clé, commencer par une lettre et ne contenir que de lettres, chiffres et _"
            return False
        cle_hashtable = conversion(self.CHAINE) % self.TAILLE_HASHMAP
        index = self.chercher(self.CHAINE, cle_hashtable)
        Node(self.CHAINE, self.last_node)
        if index == -1:
            self.erreur(5)
        if self.table_ident[cle_hashtable][index].is_cons():
            self.erreur(5.1)

        Node(self.CHAINE, self.last_node)
        self.UNILEX = self.analex()

        while self.UNILEX == "virg":
            self.UNILEX = self.analex()
            if not self.UNILEX == "ident":
                self.message_erreur = "un identificateur est attendu aprés une ',' dans la fonction 'LIRE', les identificateurs doivent être différents des mot-clé, commencer par une lettre et ne contenir que de lettres, chiffres et _"
                return False
            cle_hashtable = conversion(self.CHAINE) % self.TAILLE_HASHMAP
            index = self.chercher(self.CHAINE, cle_hashtable)
            Node(self.CHAINE, self.last_node)
            if index == -1:
                self.erreur(5)
            if self.table_ident[cle_hashtable][index].is_cons():
                self.erreur(5.1)
            Node(self.CHAINE, self.last_node)
            self.UNILEX = self.analex()

        if not self.UNILEX == "parfer":
            self.message_erreur = "')' attendu à la fin de la fonction 'LIRE'"
            return False
        self.last_node = self.last_node.get_parent()
        self.UNILEX = self.analex()
        return True
    #Elle vérifie que la syntaxe de ces instructions est correcte, en vérifiant qu'elles commencent par la fonction "ECRIRE" suivie d'une liste d'arguments entourés par des parenthèses, et qu'elles se terminent par une parenthèse fermante. Elle vérifie également que les arguments de la fonction
    # "ECRIRE" sont soit des chaînes de caractères, soit des expressions algébriques valides.
    def ecriture(self):

        if not (self.UNILEX == "motcle" and self.CHAINE == "ecrire"):
            self.message_erreur = "'ECFRIRE' attendu au début de l'instruction de écriture"
            return False
        self.UNILEX = self.analex()

        if not self.UNILEX == "parouv":
            self.message_erreur = "'(' attendu aprés la fonction 'ECRIRE'"
            return False
        self.UNILEX = self.analex()

        if self.UNILEX == "parfer":
            self.UNILEX = self.analex()
            self.last_node = self.last_node.get_parent()
            return True

        if not (self.UNILEX == "ch" or self.UNILEX == "ent" or self.UNILEX == "ident" or self.UNILEX == "parouv" or self.UNILEX == "moins"):
            self.message_erreur = "les argument de 'ECRIRE sont des CHAINE de caractère ou des expressions algébrique'"
            return False

        if not self.ecr_exp():
            return False

        while self.UNILEX == "virg":
            self.UNILEX = self.analex()

            if not (
                    self.UNILEX == "ch" or self.UNILEX == "ent" or self.UNILEX == "ident" or self.UNILEX == "parouv" or self.UNILEX == "moins"):
                self.message_erreur = "les argument de 'ECRIRE sont des CHAINE de caractère ou des expressions algébrique'"
                return False

            if not self.ecr_exp():
                return False

        if not self.UNILEX == "parfer":
            self.message_erreur = "')' attendu à la fin de la fonction 'ECRIRE'"
            return False

        self.last_node = self.last_node.get_parent()
        self.UNILEX = self.analex()
        return True
    #vérifie le type de l'entrée courante (stockée dans la propriété UNILEX) et agit en conséquence. Si l'entrée courante est un chaîne de caractères (indiquée par "ch"), la fonction ajoute un nouveau noeud enfant à l'arbre en cours avec la chaîne de caractères en tant que nom de noeud. Si l'entrée courante est une expression algébrique (indiquée par "ent", "ident", "parouv", ou "moins"), la fonction appelle
    # la méthode exp pour traiter cette expression algébrique, puis ajoute le noeud résultant en tant que fils du noeud en cours.
    def ecr_exp(self):

        if self.UNILEX == "ch":
            Node(self.CHAINE, self.last_node)
            self.UNILEX = self.analex()
            return True

        if self.UNILEX == "ent" or self.UNILEX == "ident" or self.UNILEX == "parouv" or self.UNILEX == "moins":
            if not self.exp():
                return False
            self.last_node.set_son(self.to_treat_node)
            return True

        else:
            self.message_erreur = "les argument de 'ECRIRE sont des CHAINE de caractère ou des expressions algébrique'"
    #La fonction commence par vérifier si l'entrée courante est valide pour une expression algébrique
    def exp(self):

        if not (self.UNILEX == "ent" or self.UNILEX == "ident" or self.UNILEX == "parouv" or self.UNILEX == "moins"):
            self.message_erreur = "les expressions arithmétiques sont composés d'entier de variable et de constantes, parenthésé ou précédé de '-'"
            return False

        if not self.therme():
            return False
        node_therme = self.to_treat_node

        while self.UNILEX == "plus" or self.UNILEX == "moins" or self.UNILEX == "mult" or self.UNILEX == "divi":

            if self.UNILEX == "plus":
                node_op = Node("addition")

            elif self.UNILEX == "moins":
                node_op = Node("différence")

            elif self.UNILEX == "mult":
                node_op = Node("produit")

            elif self.UNILEX == "divi":
                node_op = Node("rapport")

            self.UNILEX = self.analex()
            if not (self.UNILEX == "ent" or self.UNILEX == "ident" or self.UNILEX == "parouv" or self.UNILEX == "moins"):
                self.message_erreur = "les expressions arithmétiques sont composés d'entier de variable et de constantes, parenthésé ou précédé de '-'"
                return False

            self.exp()
            node_op.set_son(node_therme)
            node_op.set_son(self.to_treat_node)
            self.to_treat_node = node_op
        return True

    def therme(self):

        if not (self.UNILEX == "ent" or self.UNILEX == "ident" or self.UNILEX == "parouv" or self.UNILEX == "moins"):
            self.message_erreur = "les thermes des expressions arithmétiques sont  des entiers, des variables et des constantes, des expresions parenthésé ou l'opposé de therme par le '-'"
            return False

        if self.UNILEX == "ent":
            self.to_treat_node = Node(str(self.nombre))
            self.UNILEX = self.analex()
            return True

        elif self.UNILEX == "ident":
            cle_hashtable = conversion(self.CHAINE) % self.TAILLE_HASHMAP
            index = self.chercher(self.CHAINE, cle_hashtable)
            if index == -1:
                self.erreur(5)
            if self.table_ident[cle_hashtable][index].is_cons() and self.table_ident[cle_hashtable][index].typc == "CHAINE de caractère":
                self.erreur(5.2)
            if self.table_ident[cle_hashtable][index].is_var():
                self.to_treat_node = Node("var")
            elif self.table_ident[cle_hashtable][index].is_cons():
                self.to_treat_node = Node("cons")
            Node(self.CHAINE, self.to_treat_node)

            self.UNILEX = self.analex()
            return True

        elif self.UNILEX == "parouv":
            self.UNILEX = self.analex()
            if not self.exp():
                return False
            if not self.UNILEX == "parfer":
                return False
            self.UNILEX = self.analex()
            return True

        elif self.UNILEX == "moins":
            self.UNILEX = self.analex()
            if not self.therme():
                return False
            node_ = Node("opposé")
            node_.set_son(self.to_treat_node)
            self.to_treat_node = node_
            return True

    def set_const(self, nom_constante):
        self.nb_const_CHAINE += 1
        if self.UNILEX == "ent":
            self.inserer(nom_constante, "constante", "entier")
            self.VAL_CONST_CHAINE.append(self.nombre)
        else:
            self.inserer(nom_constante, "constante", "CHAINE de caractère")
            self.VAL_CONST_CHAINE.append(self.CHAINE)

    def set_var(self):
        self.inserer(self.CHAINE, "variable", "entier")

    def terminer(self):
        self.file.close()

    def erreur(self, nb):
        self.file.close()
        if nb == 0:
            print("erreur à la ligne ", self.num_ligne, " au caractère ", self.num_point,
                  " de type : fin de fichier", end='')
        if nb == 0.1:
            print("erreur à la ligne ", self.num_ligne, " au caractère ", self.num_point,
                  " de type : commentaire non fermé", end='')
        if nb == 0.2:
            print("erreur à la ligne ", self.num_ligne, " au caractère ", self.num_point,
                  " de type : fermeture de commentaire non entamé", end='')
        elif nb == 1:
            print("erreur lexicale à la ligne ", self.num_ligne, " au caractère ", self.num_point,
                  " de type : un entier est plus grand que la taille maximal des entiers = ", self.MAX_INT, end='')
        elif nb == 2:
            print("erreur lexicale à la ligne ", self.num_ligne, " au caractère ", self.num_point,
                  " de type : une CHAINE de caractère est plus grand que la taille maximal des CHAINEs = ",
                  self.LONG_MAX_CHAINE, end='')
        elif nb == 3:
            print("erreur syntaxique à la ligne ", self.num_ligne, " au caractère ", self.num_point, "de type : ",
                  self.message_erreur, end='')
        elif nb == 4:
            print("erreur sémantique à la ligne ", self.num_ligne, " au caractère ", self.num_point,
                  "de type : variable ou consante déclarée deux fois : ", self.CHAINE, end='')
        elif nb == 5:
            print("erreur sémantique à la ligne ", self.num_ligne, " au caractère ", self.num_point,
                  "de type : variable ou consante non déclarée : ", self.CHAINE, end='')
        elif nb == 5.1:
            print("erreur sémantique à la ligne ", self.num_ligne, " au caractère ", self.num_point,
                  "de type : on ne peut affecter une valeur à une constante : ", self.CHAINE, end='')
        elif nb == 5.2:
            print("erreur sémantique à la ligne ", self.num_ligne, " au caractère ", self.num_point,
                  "de type : un therme ne peut être une constante CHAINE de carractère :", self.CHAINE, end='')
        elif nb == 6:
            print("erreur lexicale à la ligne ", self.num_ligne, " au caractère ", self.num_point,
                  "de type : caractère non reconnu : ", self.CARLU, end='')
        exit()

#Cette fonction si elle lis un seul caractère elle retourne le code ASCII
def conversion(CHAINE):
    if len(CHAINE) == 1:
        return ord(CHAINE)
    alpha = 3
    return alpha * conversion(CHAINE[1:]) + ord(CHAINE[0])

#La classe inclut des méthodes pour vérifier si l'identificateur en question est une constante ou une variable,
# ainsi que pour obtenir le nom de l'identificateur et pour définir le type de la variable.
class Enreg_ident:

    def __init__(self, name, t_ident, arg, typ="unknown"):
        self.name = name
        self.t_ident = t_ident
        if t_ident == "constante":
            self.val = arg
            self.typc = typ
        elif t_ident == "variable":
            self.adrv = arg
            self.typv = typ

    def __str__(self):
        if self.is_cons():
            return "constante :" + self.name + "\n" + "   type de la constante: " + self.typc + "\n" + "   valeur de la constante: " + str(
                self.val)
        elif self.is_var():
            return "variable :" + self.name + "\n" + "   type de la variable: " + self.typv + "\n" + "   adresse de la variable: " + str(
                self.adrv)

    def get_name(self):
        return self.name

    def is_var(self):
        return self.t_ident == "variable"

    def is_cons(self):
        return self.t_ident == "constante"

    def set_typ_var(self, typv):
        if self.is_var():
            self.typv = typv

class Node:

    def __init__(self, name, parent=None):
        self.name = name
        self.son = []
        self.parent = parent
        if parent is not None:
            parent.set_son(self)

    def set_son(self, node):
        self.son.append(node)

    def __str__(self):
        if self.son == []:
            return self.name
        return self.name + "("+self.string_son()+")"

    def string_son(self):
        res = ""
        for son in self.son:
            res += str(son) + ","
        return res[:-1]

    def get_parent(self):
        return self.parent

"*-----------------------------------------------------------------------------------------*"

mon_object = Prog_source("programme")
mon_object.analyse_lexicale_partie2()