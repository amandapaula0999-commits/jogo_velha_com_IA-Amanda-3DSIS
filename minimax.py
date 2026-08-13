import math

# Lista de índices que representam as 8 combinações possíveis de vitória no tabuleiro (3 linhas, 3 colunas, 2 diagonais)
COMBINACOES_VITORIA = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Linhas
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Colunas
    [0, 4, 8], [2, 4, 6]              # Diagonais
]

def verificar_vencedor(tabuleiro):
    """
     Recebe: 
         `tabuleiro` (list): Lista de 9 elementos representando o estado das casas ('X', 'O' ou '').
     O que testa:
         Percorre cada combinação em COMBINACOES_VITORIA e verifica se as 3 posições 
          não estão vazias e possuem exatamente o mesmo símbolo.
     O que devolve:
         O símbolo do vencedor ('X' ou 'O') se houver um ganhador.
         `None` caso ainda não haja vencedor nas combinações testadas.
    """
    for a, b, c in COMBINACOES_VITORIA:
        if tabuleiro[a] != "" and tabuleiro[a] == tabuleiro[b] == tabuleiro[c]:
            return tabuleiro[a]
    return None

def tabuleiro_cheio(tabuleiro):
    """
    DE EMPATE
     Recebe: 
         `tabuleiro` (list): Lista de 9 elementos.
     O que testa:
         Verifica se a string vazia ("") NÃO está presente na lista do tabuleiro.
     O que devolve:
         `True` se todas as casas estiverem preenchidas.
         `False` se ainda houver pelo menos uma casa livre.
    """
    return "" not in tabuleiro

def minimax(tabuleiro, profundidade, maximizando, jogador_ia, jogador_humano):
    """
    ALGORITMO MINIMAX 
     Recebe:
         `tabuleiro` (list): O estado atual da matriz lógica.
        `profundidade` (int): A quantidade de jogadas simuladas à frente (para priorizar vitórias rápidas).
         `maximizando` (bool): `True` se for a vez do turno da IA (maximizar nota), `False` se for a vez do humano (minimizar nota).
         `jogador_ia` (str): O símbolo atribuído à IA (ex: 'O').
         `jogador_humano` (str): O símbolo atribuído ao jogador (ex: 'X').
     O que testa:
         Casos Base de Parada (Fim do jogo simulado):
            - Se a IA venceu: Devolve pontuação positiva (10 - profundidade).
            - Se o Humano venceu: Devolve pontuação negativa (profundidade - 10).
            - Se deu empate (tabuleiro cheio): Devolve 0.
         Simula recursivamente todas as jogadas possíveis para o jogador atual.
    
    """
    #  Checagem de término de jogo na simulação
    vencedor = verificar_vencedor(tabuleiro)
    if vencedor == jogador_ia:
        return 10 - profundidade
    if vencedor == jogador_humano:
        return profundidade - 10
    if tabuleiro_cheio(tabuleiro):
        return 0

    # Turno da IA (Busca a MAIOR pontuação possível)
    if maximizando:
        melhor = -math.inf
        for i in range(9):
            if tabuleiro[i] == "":
                tabuleiro[i] = jogador_ia  # Simula a jogada
                melhor = max(melhor, minimax(tabuleiro, profundidade + 1, False, jogador_ia, jogador_humano))
                tabuleiro[i] = ""          # Desfaz a jogada (backtracking)
        return melhor

    # Turno do Humano (Busca a MENOR pontuação possível, assumindo que ele jogará perfeitamente)
    else:
        pior = math.inf
        for i in range(9):
            if tabuleiro[i] == "":
                tabuleiro[i] = jogador_humano  # Simula a jogada do humano
                pior = min(pior, minimax(tabuleiro, profundidade + 1, True, jogador_ia, jogador_humano))
                tabuleiro[i] = ""              # Desfaz a jogada (backtracking)
        return pior

def melhor_jogada(tabuleiro, jogador_ia, jogador_humano):
    """
    A JOGADA DA IA
     Recebe:
         `tabuleiro` (list): O estado real do jogo no momento da jogada.
         `jogador_ia` (str): Símbolo da IA.
         `jogador_humano` (str): Símbolo do jogador.
     O que testa:
         Itera sobre todas as 9 posições do tabuleiro.
     Para cada posição disponível (""), simula a jogada da IA e chama a função `minimax` para calcular o resultado.
         Compara as pontuações para identificar qual posição gera o maior valor possível.
     O que devolve:
         Uma tupla contendo:
             `melhor_posicao` (int): O índice (0 a 8) da casa escolhida para realizar o movimento.
             `avaliacoes` (list de tuplas): Uma lista no formato `[(posicao, pontuacao), ...]` com a avaliação de todas as casas testadas.
    """
    avaliacoes = []
    melhor_pontuacao = -math.inf
    melhor_posicao = None

    for i in range(9):
        if tabuleiro[i] == "":
            tabuleiro[i] = jogador_ia
            # Calcula a nota da jogada iniciando com profundidade 0 e passando o turno para o humano (False)
            pontuacao = minimax(tabuleiro, 0, False, jogador_ia, jogador_humano)
            tabuleiro[i] = "" # Desfaz a simulação
            
            # Armazena o resultado da casa para enviar ao painel de interface/neurônios
            avaliacoes.append((i, pontuacao))
            
            # Atualiza se encontrar uma jogada mais vantajosa
            if pontuacao > melhor_pontuacao:
                melhor_pontuacao = pontuacao
                melhor_posicao = i

    return melhor_posicao, avaliacoes