import pygame  # biblioteca para criar jogo
import os  # permite integrar demais arquivos
import random  # gera números aleatórios

# Dimensões da tela do jogo
TELA_LARGURA = 500
TELA_ALTURA = 800

# Carregando e escalando as imagens dos elementos do jogo
IMG_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMG_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMG_BACKGROUD = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMGS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

# Iniciando os textos de marcação de pontuação
pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 50)

# Criando a classe do pássaro
class Passaro:
    IMGS = IMGS_PASSARO
    ROTACAO_MAXIMA = 25  # Limite de rotação para cima
    VELOCIDADE_ROTACAO = 20  # Velocidade de rotação para baixo
    TEMPO_ANIMACAO = 5  # Tempo de exibição de cada imagem do pássaro

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    # Função para fazer o pássaro pular
    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    # Função que move o pássaro e calcula seu deslocamento
    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo ** 2) + self.velocidade * self.tempo

        # Limita a velocidade de queda
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        # Atualiza a posição do pássaro
        self.y += deslocamento

        # Ajusta o ângulo do pássaro durante a subida e a queda
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    # Desenha o pássaro na tela com animação e rotação
    def desenhar(self, tela):
        self.contagem_imagem += 1

        # Muda a imagem do pássaro para criar a animação
        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4:
            self.imagem = self.IMGS[1]
        else:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        # Ajusta a imagem do pássaro quando está em queda
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO * 2

        # Rotaciona a imagem do pássaro de acordo com o ângulo
        img_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_img = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = img_rotacionada.get_rect(center=pos_centro_img)
        tela.blit(img_rotacionada, retangulo.topleft)

    # Função para obter a máscara da imagem do pássaro para detectar colisões
    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)

# Classe para os canos
class Cano:
    DISTANCIA = 200  # Distância entre o cano superior e o inferior
    VELOCIDADE = 5  # Velocidade com que os canos se movem para a esquerda

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMG_CANO, False, True)
        self.CANO_BASE = IMG_CANO
        self.passou = False  # Verifica se o pássaro já passou pelo cano
        self.def_altura()

    # Define uma altura aleatória para os canos
    def def_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    # Move os canos para a esquerda
    def mover(self):
        self.x -= self.VELOCIDADE

    # Desenha os canos na tela
    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    # Verifica colisão do pássaro com os canos usando máscaras
    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        return base_ponto or topo_ponto

# Classe para o chão
class Chao:
    VELOCIDADE = 5  # Velocidade do movimento do chão
    LARGURA = IMG_CHAO.get_width()
    IMG = IMG_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    # Move o chão para a esquerda, criando um efeito de movimento contínuo
    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        # Reposiciona o chão para criar um loop
        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    # Desenha o chão na tela
    def desenhar(self, tela):
        tela.blit(self.IMG, (self.x1, self.y))
        tela.blit(self.IMG, (self.x2, self.y))

# Função para desenhar a tela e todos os elementos do jogo
def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMG_BACKGROUD, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)
    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    pygame.display.update()

# Função principal que executa o jogo
def main():
    passaros = [Passaro(230, 250)]  # Cria um pássaro
    chao = Chao(730)  # Cria o chão
    canos = [Cano(700)]  # Cria os canos
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()

    rodando = True
    while rodando:
        relogio.tick(30)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    for passaro in passaros:
                        passaro.pular()

        # Move os elementos do jogo e verifica colisões
        for passaro in passaros:
            passaro.mover()
        chao.mover()
        adicionar_cano = False
        remover_canos = []

        for cano in canos:
            for passaro in passaros:
                if cano.colidir(passaro):
                    rodando = False
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))

        for cano in remover_canos:
            canos.remove(cano)

        for passaro in passaros:
            if (passaro.y + passaro.imagem.get_height()) >= 730 or passaro.y < 0:
                rodando = False

        desenhar_tela(tela, passaros, canos, chao, pontos)

    pygame.quit()

if __name__ == '__main__':
    main()
