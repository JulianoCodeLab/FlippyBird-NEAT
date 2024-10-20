from idlelib.multicall import MC_ENTER
from msilib.schema import SelfReg
from operator import truediv
from pydoc_data.topics import topics
from symtable import Class
from tkinter.tix import IMAGE

import pygame           #biblioteca para criar jogo
import os               #permite integrar demais arquivos
import random           #gera numeros aleatorios

TELA_LARGURA = 500
TELA_ALTURA = 800

#------------------------------------------------------1.0   Definindo constantes do jogo

# aumentando a escala em 2x (importando imagens em variaveis)
IMG_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imags', 'pipe.png')))

IMG_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imags', 'base.png')))

IMG_BACKGROUD = pygame.transform.scale2x(pygame.image.load(os.path.join('bg', 'pipe.png')))

IMGS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imags', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imags', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imags', 'bird3.png')))
]

#------------1.1----iniciando os textos de marcação de pontuação
pygame.font.init()

FONTE_PONTOS = pygame.font.SysFont('arial', 50)

#----------------||2.0  Criando os objetos do jogo

#-----------------------------------------------------2.1   Criando objetos do jogo
class Passaro:
#----------------------------2.1.1   atributos da classe
    IMGS = IMGS_PASSARO

# animações de rotação
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    #Funcao que cria o passaro
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0                        #define qual imgagem esta sendo usada
        self.imagem = self.IMGS[0]

    #--------------------------------------------------2.2.2   funcao para o passaro pular
    def pular (self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y


    #--------------------------------------------------2.2.3  funcao que determina o resultado fisico de mover o passaro
    def mover (self):

        #2.3.1   calc de deslocamento
        self.tempo += 1
        deslocameno =  1.5 * (self.tempo++2) + self.velocidade * self.tempo     #  S = so + vot + at^2 /2

        #2.3.2   restringindo deslocamento
        if deslocameno > 16:
            deslocameno = 16

        elif deslocameno < 16:
            deslocameno += 2                    #facilitando a jogabilidade

        self.y += deslocameno


        #2.3.3   angulo do passaro
        if deslocameno < 0 or self.y < (self.altura + 50):          #Jogo de animacao com as imagens do passaro
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
            else:
                if self.angulo > -90:
                    self.angulo -= self.VELOCIDADE_ROTACAO

    #--------------------------------------------------2.2.4   funcao que desenha o passaro e o desenho inicial do jogo
    def desenhar (self, tela):

    #2.2.4.1  define qual imagem do passaro usar (simula a batida de asa do passaro)
        self.contagem_imagem += 1      #conta os frame de imagem

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.IMGS = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.IMGS = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.IMGS = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.IMGS = self.IMGS [1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4 + 1:
            self.IMGS = self.IMGS [0]
            self.contagem_imagem = 0

    #2.2.4.2 quando o passaro cai ele não bate a asa
        if self.angulo <= -80:
            self.IMGS = self.IMGS[1]
        self.contagem_imagem = self.TEMPO_ANIMACAO*2

    #2.2.4.3 desenha a imagem
        img_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_img = self.imagem.get_rect(topleft = (self.x, self.y)).center
        retangulo = img_rotacionada.get_rect(center = pos_centro_img)

        #desenhando
        tela.blit(img_rotacionada, retangulo.topleft)

    #2.2.5 resolvedo bug do jogo
    def get_mask(self):
        pygame.mask.from_surface(self.imagem)       #pegando a mascara do passaro

#-----------------------------------------------------2.2   Criando o obstaculo cano
class Cano:

    #2.2.1     definindo constante
    Distancia = 200
    Velocidade = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMG_CANO, False, True)
        self.CANO_BASE = IMG_CANO
        self.passou = False
        self.def_altura()

    #2.2.2   define a altura do cano aleatoriamente
    def def_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_base = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.Distancia

    #2.2.3   define a movimentação do cano
    def mover(self):
        self.x -= self.Velocidade


    #2.2.4    desenha o cano
    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    #2.2.5    define a colisão entre os objetos
    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))


        #3.5.1   verifica o ponto de colisão
        topo_ponto = passaro_mask.overlap(base_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False

#-----------------------------------------------------2.3  Criando o obstaculo chão
class Chao:

    #2.3.1    definindo constante
    VELOCIDADAE = 5
    LARGURA = IMG_CHAO.get_width()
    IMG = IMG_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0                       #definindo a primeira img do chão
        self.x2 = self.LARGURA            #definindo a posicao da 2 img do chão


    #2.3.2    funcao que movimenta os 2 chãos sequencialmente
    def mover(self):
        self.x1 -= self.VELOCIDADAE
        self.x2 -= self.VELOCIDADAE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x1 + self.LARGURA
        if self.x2 + self.LARGURA <0:
            self.x2 = self.x2 + self.LARGURA


    #2.3.3    desenha o chao
    def desenhar(self, tela):
        tela.blit(self.IMG, (self.x1, self.y))
        tela.blit(self.IMG, (self.x2, self.y))

#------------------------------------------------------------------------------||

#---------------||3.0   Criando tela jogo

#----------------3.1    funcao para gerar a tela
def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMG_BACKGROUD, (0, 0))

#----------------3.2    preparando o jogo para receber varios passaros simuntaneos
    for passaro in passaros:
        passaro.desenhar(tela)

#----------------3.3    desenhando o cano
    for cano in canos:
        cano.desenhar(tela)

#----------------3.4    colocando pontuação
    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    pygame.display.update()     #atualiza a tela construida
#------------------------------------------------------------------------------||






#-----------------------------------------------------------------------------||

