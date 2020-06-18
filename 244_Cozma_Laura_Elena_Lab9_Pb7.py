import time
from copy import deepcopy

import pygame, sys

GRAFICA = False
dim_linie = 80
padding = 30
t_start_program = int(round(time.time() * 1000))
SCOR = 2

def deseneaza_grid(display, tabla):
    '''
    Desenam pe ecran configuratia curenta a jocului
    :param display: ecranul pe care desenam
    :param tabla: configuratia curenta pe care o desenam
    :return: liniile orizontale si verticale puse in display pentru a le folosi cand dam click pe ele
    '''
    h_lines = []
    v_lines = []

    linii = tabla.NR_LINII + 1
    coloane = tabla.NR_COLOANE + 1
    x_img = pygame.image.load('cat.jpg')
    x_img = pygame.transform.scale(x_img, (dim_linie, dim_linie))
    zero_img = pygame.image.load('wdog.jpg')
    zero_img = pygame.transform.scale(zero_img, (dim_linie, dim_linie))

    #desenam patratele corespunzatoare scorurilor
    for i in range(linii - 1):
        for j in range(coloane - 1):
            #construim patratul
            p = pygame.Rect(j * (dim_linie + 1) + padding, i * (dim_linie + 1) + padding, dim_linie, dim_linie)
            pygame.draw.rect(display, (0, 0, 0), p)
            #in cazul in care patratul curent are toate laturile puse, afisam imaginea corespunzatoare castigatorului patratului
            if tabla.punctaj[i][j] == 'P':
                display.blit(x_img, (j * (dim_linie + 1) + padding, i * (dim_linie + 1) + padding))
            elif tabla.punctaj[i][j] == 'C':
                display.blit(zero_img, (j * (dim_linie + 1) + padding,  i * (dim_linie + 1) + padding))

    #desenam liniile orizontale
    for i in range(linii):
        aux = []
        for j in range(coloane - 1):
            #in cazul in care linia orizontala e ocupata, o coloram cu roz
            if tabla.linii_orizontale[i][j] == 1:
                pygame.draw.line(display, (196, 121, 121), (j * dim_linie + padding, i * dim_linie + padding),((j + 1) * dim_linie + padding, i * dim_linie + padding), 5)
            else:
                # in cazul in care linia orizontala nu e ocupata, o lasam neagra
                #o adaugam un aux, facand o matrice de linii care ne va ajuta cand dam click
                aux.append(pygame.draw.line(display, (0, 0, 0), (j * dim_linie + padding, i * dim_linie + padding),((j + 1) * dim_linie + padding, i * dim_linie + padding), 16))
        h_lines.append(aux)

    #desenam liniile verticale
    for i in range(linii - 1):
        aux = []
        for j in range(coloane):
            # in cazul in care linia verticala e ocupata, o coloram cu roz
            if tabla.linii_verticale[i][j] == 1:
                pygame.draw.line(display, (196, 121, 121), (j * dim_linie + padding, i * dim_linie + padding),(j * dim_linie + padding, (i + 1) * dim_linie + padding), 5)
            else:
                # in cazul in care linia verticala nu e ocupata, o lasam neagra
                # o adaugam un aux, facand o matrice de linii care ne va ajuta cand dam click
                aux.append(pygame.draw.line(display, (0, 0, 0), (j * dim_linie + padding, i * dim_linie + padding), (j * dim_linie + padding, (i + 1) * dim_linie + padding), 16))
        v_lines.append(aux)

    #desenam punctele
    for i in range(linii):
        for j in range(coloane):
            pygame.draw.circle(display, (255, 255, 255), (j * dim_linie + padding, i * dim_linie + padding), 5)

    pygame.display.flip()

    return h_lines, v_lines

class Joc:
    """
    Clasa care defineste jocul
    """

    SIMBOLURI_JUC = ['P', 'C']
    JMIN = None  # 'P'
    JMAX = None  # 'C'
    NR_LINII = 3
    NR_COLOANE = 3

    def __init__(self, NR_LINII = None, NR_COLOANE = None, linii_verticale=None, linii_orizontale = None, punctaj = None, lin = None, col = None, dir = None, patrat_complet = None):
        #generarea starii initiale
        #implicit nr de linii si de coloane e 3
        if NR_LINII is not None:
            self.NR_LINII = NR_LINII

        if NR_COLOANE is not None:
            self.NR_COLOANE = NR_COLOANE

        #pozitiile liniei proaspat completate pentru a forma noua configuratie
        self.lin = lin or -1

        self.col = col or -1
        # directia liniei proaspat completate pentru a forma noua configuratie
        # H = orizontal
        # V = vertical
        self.dir = dir or '0'

        #ne spune daca segmentul adaugat a completat un patrat, adica daca urmeaza tot randul nostru
        if patrat_complet is None:
            self.patrat_complet = False
        else:
            self.patrat_complet = patrat_complet

        self.linii_verticale = linii_verticale or [[0 for j in range(self.NR_COLOANE + 1)] for i in range(self.NR_LINII)]
        """
        pentru 3 linii si 3 coloane, liniile verticale sunt:
        | | | |
        | | | |
        | | | |
        """
        self.linii_orizontale = linii_orizontale or [[0 for j in range(self.NR_COLOANE)] for i in range(self.NR_LINII + 1)]
        """
        pentru 3 linii si 3 coloane, liniile verticale sunt:
        - - -
        - - -
        - - -
        - - -
        """
        self.punctaj = punctaj or [[' ' for j in range(self.NR_COLOANE)] for i in range(self.NR_LINII)]

    def interior(self, lin, col, dir):
        '''
        Pentru o linie determinata prin linie, coloana si directie, verifica daca e in interiorul careului;
        folosita la functia in care verificam daca am inchis un patrat
        Nu vrem sa verificam daca a fost pusa o linie care nu poate fi pusa
        '''

        if dir == 'H':      #in directie orizontala
            return lin >= 0 and lin <= self.NR_LINII and col >= 0 and col < self.NR_COLOANE
        elif dir == 'V':    #in directie verticala
            return lin >= 0 and lin < self.NR_LINII and col >= 0 and col <= self.NR_COLOANE

    def conversie_directie(self, lin, col, directie):
        '''
        Folosita in cazul jocului in consola
        Jucatorul va da coordonatele liniei prin coordonatele unui capat si directia aleasa (N, S, E, V)
        Actualizam lin si col la pozitia pe care ar ocupa-o linia in vectorul corespunzator(linii_verticale sau
        linii_orizontale, conform directiei) si actualizam si directie(H pentru E sau V, V pentru N sau S)
        '''
        if directie == 'V':
            col = col - 1
            directie = 'H'
        elif directie == 'N':
            lin = lin - 1
            directie = 'V'
        elif directie == 'E':
            directie = 'H'
        elif directie == 'S':
            directie = 'V'
        return lin, col, directie

    def inchide_patrat(self, lin, col, directie, jucator):
        '''
        Functie care verifica daca noua linie a inchis cel putin un patrat(1 sau 2)
        In caz afirmativ returneaza true si actualizeaza configuratia
        Altfel returneaza false
        '''
        ok = False

        if directie == 'H': #e o linie orizontala
            #lin si col indica o linie care e latura de sus a patratului
            if self.interior(lin + 1, col, 'H') and self.interior(lin, col + 1, 'V'):
                #verificam daca sunt completate toate laturile
                if self.linii_orizontale[lin][col] == 1 and self.linii_orizontale[lin + 1][col] == 1 and self.linii_verticale[lin][col] == 1 and self.linii_verticale[lin][col + 1] == 1:
                    #actualizam
                    self.punctaj[lin][col] = jucator
                    ok = True
            #lin si col indica o linie care e latura de jos a patratului
            if self.interior(lin - 1, col, 'H') and self.interior(lin - 1, col + 1, 'V'):

                if self.linii_orizontale[lin][col] == 1 and self.linii_orizontale[lin - 1][col] == 1 and self.linii_verticale[lin - 1][col] == 1 and self.linii_verticale[lin - 1][col + 1] == 1:
                    self.punctaj[lin - 1][col] = jucator
                    ok = True

        if directie == 'V': #e o linie verticala
            #latura verticala din stanga
            if self.interior(lin, col + 1, 'V') and  self.interior(lin + 1, col, 'H'):
                if self.linii_orizontale[lin][col] == 1 and self.linii_orizontale[lin + 1][col] == 1 and self.linii_verticale[lin][col] == 1 and self.linii_verticale[lin][col + 1] == 1:
                    self.punctaj[lin][col] = jucator
                    ok = True
            # latura verticala din dr
            if self.interior(lin, col - 1, 'V')  and self.interior(lin + 1, col - 1, 'H'):
                if self.linii_orizontale[lin][col - 1] == 1 and self.linii_orizontale[lin + 1][col - 1] == 1 and self.linii_verticale[lin][col] == 1 and self.linii_verticale[lin][col - 1] == 1:
                    self.punctaj[lin][col - 1] = jucator
                    ok = True

        return ok


    def mutari_joc(self, jucator):
        '''
        Functia de generare a mutarilor
        Returneaza o lista cu toate tablele de joc care s-ar forma dupa selectarea fiecarei pozitii valide
        '''
        if GRAFICA == True:         #in cazul in care folosim grafica, trebuie sa apelam get de evenimente
            pygame.event.get()      #astfel fereastra va sti ca trebuie sa ramana activa si nu va ingheta
        l_mutari = []
        #parcurgem liniile orizontale
        for lin in range(self.NR_LINII + 1):
            for col in range(self.NR_COLOANE):
                #daca am gasit o linie necompletata, putem sa o completam
                if self.linii_orizontale[lin][col] == 0:
                    nou_joc = deepcopy(self)
                    nou_joc.linii_orizontale[lin][col] = 1
                    nou_joc.patrat_complet = nou_joc.inchide_patrat(lin, col, 'H', jucator) #verificam daca se inchide un patrat, daca da patrat_complet primeste True
                    nou_joc.lin = lin
                    nou_joc.col = col
                    nou_joc.dir = 'H'           #directia liniei nou adaugate e orizontala
                    l_mutari.append(nou_joc)
                    

        # parcurgem liniile verticale
        for lin in range(self.NR_LINII):
            for col in range(self.NR_COLOANE + 1):
                # daca am gasit o linie necompletata, putem sa o completam
                if self.linii_verticale[lin][col] == 0:
                    nou_joc = deepcopy(self)
                    nou_joc.linii_verticale[lin][col] = 1
                    nou_joc.patrat_complet = nou_joc.inchide_patrat(lin, col, 'V', jucator)
                    nou_joc.lin = lin
                    nou_joc.col = col
                    nou_joc.dir = 'V'           #directia liniei nou adaugate e orizontala
                    l_mutari.append(nou_joc)

        return l_mutari


    def nr_piese_jucator(self, jucator):
        '''
        A doua modalitate de calculare a scorului
        Returneaza cate piese are jucatorul pe tabla de culoarea sa
        '''
        nr = 0
        for lin in range(self.NR_LINII):
            for col in range(self.NR_COLOANE):
                if self.punctaj[lin][col] == jucator:
                    nr += 1
        return nr

    def scor2(self, jucator):
        '''
        A doua varianta de calcul al scorului
        In cazul in care tocmai am completat un patratel inseamna ca mai avem miscari disponibile si e posibil sa ne creasca
        sansele de castig; deci incrementam cu 1 scorul, deoarece avem un avantaj
        '''
        nr = 0
        #incrementam cu 2 scorul pentru fiecare patrat ce apartine jucatorului
        for lin in range(self.NR_LINII):
            for col in range(self.NR_COLOANE):
                if self.punctaj[lin][col] == jucator:
                    nr += 1
        #daca avem mai mult de jumatate din patrate inseamna ca jucator este in mod cert castigatorul
        if nr > (self.NR_LINII * self.NR_COLOANE):
            return 999
        #daca nu avem mai mult de jumatate din patrate ocupate
        #verificam daca mai avem mutari disponibile
        #daca da, marim scorul; sansele de castig cresc
        if self.patrat_complet == True:
            nr += 1
        return nr

    def fct_euristica(self):
        '''
        Functia euristica: numarul pieselor lui max - numarul pieselor lui min
        In functie de variabila globala scor stabilim modalitatea de calcul
        '''
        if SCOR == 1:
            return self.nr_piese_jucator(Joc.JMAX) - self.nr_piese_jucator(Joc.JMIN)
        else:
            return self.scor2(Joc.JMAX) - self.scor2(Joc.JMIN)

    def afis_scor(self):
        '''
        Functie care afiseaza scorul final, reprezentat de nr_pieselor jucatorilor JMAX si JMIN; utilizata la finalul programului
        '''
        nr_mutari_max = self.nr_piese_jucator(self.JMAX)
        nr_mutari_min = self.nr_piese_jucator(self.JMIN)
        print("Scor jucator: " + str(nr_mutari_min))
        print("Scor calculator: " + str(nr_mutari_max))

    def final(self):
        '''
        returnam simbolul jucatorului castigator
        sau returnam 'remiza'
        sau 'False' daca nu s-a terminat jocul
        '''

        nr_mutari_max = self.nr_piese_jucator(self.JMAX)
        nr_mutari_min = self.nr_piese_jucator(self.JMIN)
        #daca au fost completate toate patratele
        if (nr_mutari_min + nr_mutari_max) == (self.NR_COLOANE * self.NR_LINII):
            if nr_mutari_max > nr_mutari_min:       #in functie de care numar de patrate e mai mare, acel jucator castiga
                return self.JMAX
            elif nr_mutari_max < nr_mutari_min:
                return self.JMIN
            else:
                return 'remiza'
        else:
            return False

    def estimeaza_scor(self, adancime):
        '''
        Functie care estimeaza scorul
        '''
        t_final = self.final()
        if t_final == Joc.JMAX:
            return (999 + adancime)
        elif t_final == Joc.JMIN:
            return (-999 - adancime)
        elif t_final == 'remiza':
            return 0
        else:
            return self.fct_euristica()

    def __str__(self):
        '''
        Returneaza o tabla de joc(tip sir de caractere pentru afisare)
        '''
        sir = '  '
        for i in range(self.NR_COLOANE * 2 + 1):
            if (i % 2) == 0:
                sir += str(i // 2)
            else:
                sir += ' '

        sir += '\n'
        for i in range(self.NR_LINII * 2 + 1):
            if (i % 2) == 0:
                sir += str(i // 2) + ' '
            else:
                sir += '  '
            for j in range(self.NR_COLOANE * 2 + 1):
                if (i % 2) == 0 and (j % 2) == 0:
                    sir += '.'
                elif (i % 2) == 1 and (j % 2) == 1:
                    sir += self.punctaj[i//2][j//2]
                elif (i % 2) == 1:
                    if self.linii_verticale[i//2][j//2] == 1:
                        sir += '|'
                    else:
                        sir += ' '
                elif (j % 2) == 1:
                    if self.linii_orizontale[i//2][j//2] == 1:
                        sir += '_'
                    else:
                        sir += ' '

            sir += '\n'

        return sir



class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    Are ca proprietate tabla de joc
    """

    ADANCIME_MAX = None

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, scor=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent

        # adancimea in arborele de stari
        self.adancime = adancime

        # scorul starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.scor = scor

        # lista de mutari posibile din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

        self.parinte = parinte

    def jucator_opus(self):
        '''
        Determina jucatorul opus
        '''
        if self.j_curent == Joc.JMIN:
            return Joc.JMAX
        else:
            return Joc.JMIN

    def mutari_stare(self):
        '''
        Actualiza mutarile posibile pentru starea curenta
        '''
        l_mutari = self.tabla_joc.mutari_joc(self.j_curent)
        juc_opus = self.jucator_opus()
        l_stari_mutari = []
        for mutare in l_mutari:
            #daca am construit un patrat, tot jucatorul acesta ramane
            if mutare.patrat_complet is True:
                l_stari_mutari.append(Stare(mutare, self.j_curent, self.adancime - 1, parinte=self))
            else:
                l_stari_mutari.append(Stare(mutare, juc_opus, self.adancime - 1, parinte=self))
        return l_stari_mutari

    def __str__(self):
        sir = str(self.tabla_joc) + "(Juc curent: " + self.j_curent + ")\n"
        return sir

""" Algoritmul MinMax """


def min_max(stare):
    # Daca am ajuns la o frunza a arborelui, adica:
    # - daca am expandat arborele pana la adancimea maxima permisa
    # - sau daca am ajuns intr-o configuratie finala de joc

    if stare.adancime == 0 or stare.tabla_joc.final():
        # calculam scorul frunzei apeland "estimeaza_scor"
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    # Altfel, calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari_stare()

    # aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutari_scor = [min_max(mutare) for mutare in stare.mutari_posibile]

    if stare.j_curent == Joc.JMAX:
        # daca jucatorul e JMAX aleg starea-fiica cu scorul maxim
        stare.stare_aleasa = max(mutari_scor, key=lambda x: x.scor)
    else:
        # daca jucatorul e JMIN aleg starea-fiica cu scorul minim
        stare.stare_aleasa = min(mutari_scor, key=lambda x: x.scor)

    # actualizez scorul „tatalui” = scorul „fiului” ales
    stare.scor = stare.stare_aleasa.scor
    return stare


def alpha_beta(alpha, beta, stare):
    # Daca am ajuns la o frunza a arborelui, adica:
    # - daca am expandat arborele pana la adancimea maxima permisa
    # - sau daca am ajuns intr-o configuratie finala de joc
    if stare.adancime == 0 or stare.tabla_joc.final():
        # calculam scorul frunzei apeland "estimeaza_scor"
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    # Conditia de retezare:
    if alpha >= beta:
        return stare  # este intr-un interval invalid, deci nu o mai procesez

    # Calculez toate mutarile posibile din starea curenta (toti „fiii”)
    stare.mutari_posibile = stare.mutari_stare()

    if stare.j_curent == Joc.JMAX:
        scor_curent = float('-inf')  # scorul „tatalui” de tip MAX

        # pentru fiecare „fiu” de tip MIN:
        for mutare in stare.mutari_posibile:
            # calculeaza scorul fiului curent
            stare_noua = alpha_beta(alpha, beta, mutare)

            # incerc sa imbunatatesc (cresc) scorul si alfa
            # „tatalui” de tip MAX, folosind scorul fiului curent
            if scor_curent < stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor

            if alpha < stare_noua.scor:
                alpha = stare_noua.scor
                if alpha >= beta:  # verific conditia de retezare
                    break  # NU se mai extind ceilalti fii de tip MIN


    elif stare.j_curent == Joc.JMIN:
        scor_curent = float('inf')  # scorul „tatalui” de tip MIN

        # pentru fiecare „fiu” de tip MAX:
        for mutare in stare.mutari_posibile:
            stare_noua = alpha_beta(alpha, beta, mutare)

            # incerc sa imbunatatesc (scad) scorul si beta
            # „tatalui” de tip MIN, folosind scorul fiului curent
            if scor_curent > stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor

            if beta > stare_noua.scor:
                beta = stare_noua.scor
                if alpha >= beta:  # verific conditia de retezare
                    break  # NU se mai extind ceilalti fii de tip MAX

    # actualizez scorul „tatalui” = scorul „fiului” ales
    stare.scor = stare.stare_aleasa.scor

    return stare


def afis_daca_final(stare_curenta):
    '''
    Functie folosita la afisarea starii finale a jocului
    '''
    final = stare_curenta.tabla_joc.final()
    if (final):
        if (final == "remiza"):
            print("Remiza!")
        elif final == 'P':
                print("A castigat pisica")
        else:
            print("A castigat cainele")

        return True

    return False

def update_tabla(linii_oriz, linii_v, pos, tabla):
    '''
    Pentru o pozitie aleasa din mouse, vedem daca e valida si daca nu a fost deja ocupata acea pozitie
    '''
    poz_lin = -1
    poz_col = -1
    orient = -1
    for i in range(len(linii_oriz)):
        for j in range(len(linii_oriz[i])):
            if linii_oriz[i][j].collidepoint(pos) and tabla.linii_orizontale[i][j] == 0:
                poz_lin = i
                poz_col = j
                orient = 0          #0 == orizontal

    for i in range(len(linii_v)):
        for j in range(len(linii_v[i])):
            if linii_v[i][j].collidepoint(pos) and tabla.linii_verticale[i][j] == 0:
                poz_lin = i
                poz_col = j
                orient = 1          #1 == vertical
    return poz_lin, poz_col, orient


def main():

    '''
    Citim valori pentru algoritmul folosit, adancimea maxima si jucatorul ales
    '''
    # initializare algoritm
    raspuns_valid = False
    while not raspuns_valid:
        tip_algoritm = input("Algorimul folosit? (raspundeti cu 1 sau 2)\n 1.Minimax\n 2.Alpha-Beta\n ")
        if tip_algoritm in ['1', '2']:
            raspuns_valid = True
        else:
            print("Nu ati ales o varianta corecta.")

    # initializare dificultate
    raspuns_valid = False
    while not raspuns_valid:
        n = input("Dificultatea jocului: (raspundeti cu 1,2 sau 3)\n 1.Incepator\n 2.Mediu\n 3.Avansat\n ")
        if n.isdigit() and 1 <= int(n) <= 3:
            n = int(n)
            if n == 1:
                Stare.ADANCIME_MAX = 1
            elif n == 2:
                Stare.ADANCIME_MAX = 2
            elif n == 3:
                Stare.ADANCIME_MAX = 3
            raspuns_valid = True
        else:
            print("Trebuie sa introduceti un numar natural intre 1 si 3.")

    # initializare jucatori
    raspuns_valid = False
    while not raspuns_valid:
        Joc.JMIN = input("Doriti sa jucati cu pisica sau cu caine?  (raspundeti cu 1 sau 2) \n 1.Pisica\n 2.Caine\n ").lower()
        if (Joc.JMIN in ['1', '2']):
            raspuns_valid = True
        else:
            print("Raspunsul trebuie sa fie 1 sau 2.")
    #P = pisica
    #C = caine
    Joc.JMIN = 'P' if Joc.JMIN == '1' else 'C'
    Joc.JMAX = 'C' if Joc.JMIN == 'P' else 'P'

    #initializare tip joc
    raspuns_valid = False
    while not raspuns_valid:
        tip = input("Doriti sa jucati din consola sau folosind interfata grafica?  (raspundeti cu 1 sau 2) \n 1.Consola\n 2.Interfata grafica\n ").lower()
        if (tip in ['1', '2']):
            raspuns_valid = True
        else:
            print("Raspunsul trebuie sa fie 1 sau 2.")
    GRAFICA = True if tip == '2' else False


    # initializare tabla
    tabla_curenta = Joc(4, 5)
    print("Tabla initiala")
    print(str(tabla_curenta))

    # creare stare initiala
    stare_curenta = Stare(tabla_curenta, 'P', Stare.ADANCIME_MAX)

    if GRAFICA == True:
        # setari interf grafica
        pygame.init()
        pygame.display.set_caption('Dots & Boxes')
        ecran = pygame.display.set_mode(size=(dim_linie * tabla_curenta.NR_COLOANE + 2 * padding, dim_linie * tabla_curenta.NR_LINII + 2 * padding))
        linii_oriz, linii_v = deseneaza_grid(ecran, tabla_curenta)


    end_game = False
    nr_mutari_jmin = 0
    nr_mutari_jmax = 0

    if stare_curenta.j_curent == Joc.JMIN:
        #luam timpul initial pentru jucatorul JMIN in cazul in care el face prima mutare
        t_inainte = int(round(time.time() * 1000))
        print("Este randul jucatorului")

    while end_game is False:

        if (stare_curenta.j_curent == Joc.JMIN):

            # muta jucatorul

            if GRAFICA == True:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        #daca inchidem ecranul, jocul se termina afisam timpul, scorul si nr de mutari pentru fiecare jucator

                        t_final_program = int(round(time.time() * 1000))
                        stare_curenta.tabla_joc.afis_scor()
                        print("----------------------------------------")
                        print("Numar mutari jucator: " + str(nr_mutari_jmin))
                        print("Numar mutari calculator: " + str(nr_mutari_jmax))
                        print("Jocul a durat " + str(t_final_program - t_start_program) + " milisecunde")

                        pygame.quit()
                        sys.exit()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        poz_lin, poz_col, orient = update_tabla(linii_oriz, linii_v, pos, stare_curenta.tabla_joc)

                        if orient != -1:    #este -1 daca nu a fost o mutare valida
                            nr_mutari_jmin += 1
                            if orient == 0:
                                stare_curenta.tabla_joc.linii_orizontale[poz_lin][poz_col] = 1
                                orient = 'H'
                            elif orient == 1:
                                stare_curenta.tabla_joc.linii_verticale[poz_lin][poz_col] = 1
                                orient = 'V'

                            nu_schimba = stare_curenta.tabla_joc.inchide_patrat(poz_lin, poz_col, orient, stare_curenta.j_curent)
                            deseneaza_grid(ecran, stare_curenta.tabla_joc)

                            # afisarea starii jocului in urma mutarii utilizatorului
                            print("\nTabla dupa mutarea jucatorului")
                            print(str(stare_curenta))

                            # testez daca jocul a ajuns intr-o stare finala
                            if (afis_daca_final(stare_curenta)):
                                end_game = True
                                break

                            # # preiau timpul in milisecunde de dupa mutare
                            t_dupa = int(round(time.time() * 1000))
                            print("Jucatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")

                            #vedem daca am completat un patrat si ramane acelasi jucator
                            if nu_schimba is False:
                                stare_curenta.j_curent = stare_curenta.jucator_opus()
                            else:
                                #ramane acelasi jucator, luam t_inainte
                                print("Este randul jucatorului")
                                t_inainte = int(round(time.time() * 1000))

            else:
                #citim linia, coloana, directia
                raspuns_valid = False
                while not raspuns_valid:
                    try:
                        print("Tastati exit daca vreti sa iesiti din joc")
                        linie = input("linie=")
                        if linie.lower() == 'exit':
                            end_game = True
                            break
                        coloana = input("coloana=")
                        if coloana.lower() == 'exit':
                            end_game = True
                            break
                        directie = input("directie=")
                        if directie.lower() == 'exit':
                            end_game = True
                            break
                        linie = int(linie)
                        coloana = int(coloana)
                        linie, coloana, directie = stare_curenta.tabla_joc.conversie_directie(linie, coloana, directie)

                        if stare_curenta.tabla_joc.interior(linie, coloana, directie):
                            if directie == 'H':
                                if stare_curenta.tabla_joc.linii_orizontale[linie][coloana] == 1:
                                    print("Exista deja un simbol in pozitia ceruta.")
                                else:
                                    raspuns_valid = True
                                    break
                            if directie == 'V':
                                if stare_curenta.tabla_joc.linii_verticale[linie][coloana] == 1:
                                    print("Exista deja un simbol in pozitia ceruta.")
                                else:
                                    raspuns_valid = True
                                    break
                        else:
                            print("Linie, coloana sau directie invalida")

                    except ValueError:
                        print("Linia si coloana trebuie sa fie numere naturale incadrate in dimensiunile tablei si directia N, S, E sau V")

                if not end_game:
                    #daca jocul continua(break iesea numai din try)
                    #incepem sa mutam
                    nr_mutari_jmin += 1
                    if directie == 'H':
                        stare_curenta.tabla_joc.linii_orizontale[linie][coloana] = 1
                    else:
                        stare_curenta.tabla_joc.linii_verticale[linie][coloana] = 1

                    nu_schimba = stare_curenta.tabla_joc.inchide_patrat(linie, coloana, directie, stare_curenta.j_curent)

                    # afisarea starii jocului in urma mutarii utilizatorului
                    print("\nTabla dupa mutarea jucatorului")
                    print(str(stare_curenta))

                    # testez daca jocul a ajuns intr-o stare finala
                    if (afis_daca_final(stare_curenta)):
                        end_game = True
                        break

                    # iau timpul de final si afisez
                    t_dupa = int(round(time.time() * 1000))
                    print("Jucatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")


                    if nu_schimba is False:
                        stare_curenta.j_curent = stare_curenta.jucator_opus()
                    else:
                        #continua jucatorul, ia din nou timpul
                        print("Este randul jucatorului")
                        t_inainte = int(round(time.time() * 1000))



        # --------------------------------
        else:  # jucatorul e JMAX (calculatorul)
            # Mutare calculator
            print("Este randul calculatorului")
            #adaug inca o mutare in mutarile lui JMAX
            nr_mutari_jmax += 1
            # preiau timpul in milisecunde de dinainte de mutare
            t_inainte = int(round(time.time() * 1000))

            if tip_algoritm == '1':
                stare_actualizata = min_max(stare_curenta)
            else:  # tip_algoritm==2
                stare_actualizata = alpha_beta(-500, 500, stare_curenta)

            stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
            nu_schimba = stare_curenta.tabla_joc.patrat_complet

            if GRAFICA == True:
                deseneaza_grid(ecran, stare_curenta.tabla_joc)

            print("Tabla dupa mutarea calculatorului")
            print(str(stare_curenta))

            # preiau timpul in milisecunde de dupa mutare
            t_dupa = int(round(time.time() * 1000))
            print("Calculatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")

            if (afis_daca_final(stare_curenta)):
                end_game = True
                break

            # S-a realizat o mutare
            #nu schimba e True adica abia am completat un patrat si mai putem realiza tot noi o mutare
            if nu_schimba is False:
                stare_curenta.j_curent = stare_curenta.jucator_opus()
                print("Este randul jucatorului")


    print("----------------------------------------")
    stare_curenta.tabla_joc.afis_scor()
    print("Numar mutari jucator: " + str(nr_mutari_jmin))
    print("Numar mutari calculator: " + str(nr_mutari_jmax))


if __name__ == "__main__":
    main()

    if GRAFICA == True:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    t_final_program = int(round(time.time() * 1000))
    print("Jocul a durat " + str(t_final_program - t_start_program) + " milisecunde ")

