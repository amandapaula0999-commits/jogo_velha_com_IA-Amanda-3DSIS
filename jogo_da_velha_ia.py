import random
import sys

# Compatibilidade entre PyQt6 e PyQt5
try:
    from PyQt6.QtWidgets import (
        QApplication, QWidget, QGridLayout, QPushButton, QLabel,
        QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QButtonGroup
    )
    from PyQt6.QtCore import QTimer, Qt
except Exception:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QGridLayout, QPushButton, QLabel,
        QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QButtonGroup
    )
    from PyQt5.QtCore import QTimer, Qt

# Ajustes de enums para manter compatibilidade entre versões de PyQt
try:
    _ = Qt.AlignmentFlag.AlignCenter
except Exception:
    Qt.AlignmentFlag = Qt

try:
    _ = QFrame.Shape.VLine
except Exception:
    QFrame.Shape = QFrame

# Importação dos módulos com as regras lógicas e a interface visual da IA
from minimax import melhor_jogada, verificar_vencedor, tabuleiro_cheio
from painel_neuronios import PainelNeuronios

# Constantes globais
JOGADOR_HUMANO = "X"
JOGADOR_IA = "O"
ATRASO_ENTRE_ANALISES_MS = 300  # Intervalo de tempo entre a animação de cada casa analisada

# Mapeamento de dificuldades e probabilidade da IA cometer erros
DIFICULDADES = {
    "Fácil": 0.75,     # 75% de chance de jogar uma posição subótima
    "Mediano": 0.4,    # 40% de chance de erro
    "Difícil": 0.15,   # 15% de chance de erro
    "Minimax": 0.0,    # 0% de erro (Modo imbatível)
}
DIFICULDADE_PADRAO = "Mediano"


class PainelPensamentoIA(QWidget):
    """
    PAINEL DE PENSAMENTO DA IA
     Encapsula o título informativo e a visualização dos 'neurônios' (avaliações).
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label_titulo = QLabel("calma, você vai perder de qualquer forma")
        layout.addWidget(self.label_titulo)
        self.painel = PainelNeuronios()
        layout.addWidget(self.painel)
        self.setLayout(layout)

    def iniciar_analise(self):
        self.painel.iniciar_analise()
        self.label_titulo.setText("Analisando jogadas")

    def adicionar_avaliacao(self, posicao, pontuacao):
        self.painel.adicionar_avaliacao(posicao, pontuacao)

    def mostrar_escolha(self, posicao, pontuacao):
        self.label_titulo.setText(f"Melhor jogada: posição {posicao} (pontuação {pontuacao})")
        self.painel.mostrar_escolha(posicao, pontuacao)

    def reiniciar(self):
        self.painel.reiniciar()
        self.label_titulo.setText("calma, você vai perder de qualquer forma")


class JanelaJogo(QWidget):
    """
    JANELA PRINCIPAL DO JOGO DA VELHA
     Gerencia a interface gráfica principal, o estado do tabuleiro, o placar,
    as interações do usuário e o encadeamento dos turnos com a IA.
    """
    def __init__(self):
        """
        CRIAÇÃO DA JANELA E VARIÁVEIS DE ESTADO
        
         Recebe: 'self' (A instância do widget).
         O que faz:
             Define o título da janela ("Umjogo legal").
             Inicializa a matriz lógica `self.tabuleiro` com 9 casas vazias ("").
            Cria as variáveis de controle de estado (`jogo_ativo`, dificuldade atual e placares).
             Invoca a montagem dos componentes visuais (`montar_interface`).
         Devolve: Nulo (`None`).
        """
        super().__init__()
        
        self.setWindowTitle("Umjogo legal")
        
        self.painel_ia = PainelPensamentoIA()
        self.tabuleiro = [""] * 9
        self.botoes = []
        self.jogo_ativo = True
        self.dificuldade_atual = DIFICULDADE_PADRAO
        self.probabilidade_aleatoria = DIFICULDADES[DIFICULDADE_PADRAO]
        
        self.placar_jogador = 0
        self.placar_ia = 0
        self.placar_empates = 0
        
        self.montar_interface()

    def montar_interface(self):
        """
        MONTAGEM DA INTERFACE GRÁFICA
        
         Recebe: 'self'.
         O que faz:
             Organiza os layouts horizontal e vertical.
             Adiciona o painel de placar permanente.
             Cria os botões para seleção de dificuldade.
             Instancia os 9 botões do tabuleiro ($3 \times 3$) e os conecta ao método `jogada_humano`.
             Adiciona o botão de "Nova partida" e o painel de pensamentos da IA.
         Devolve: Nulo (`None`).
        """
        layout_principal = QHBoxLayout()
        layout_jogo = QVBoxLayout()

        # Placar
        self.label_placar = QLabel(f"Jogador: {self.placar_jogador} | IA: {self.placar_ia} | Empates: {self.placar_empates}")
        self.label_placar.setStyleSheet("font-size: 16px; font-weight: bold; color: blue;")
        self.label_placar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_jogo.addWidget(self.label_placar)

        # Seletor de Dificuldades
        layout_jogo.addWidget(QLabel("Dificuldade da IA:"))
        layout_dificuldade = QHBoxLayout()
        self.grupo_dificuldade = QButtonGroup(self)
        self.grupo_dificuldade.setExclusive(True)

        for nome in DIFICULDADES:
            botao = QPushButton(nome)
            botao.setCheckable(True)
            botao.setChecked(nome == self.dificuldade_atual)
            botao.clicked.connect(lambda _, n=nome: self.selecionar_dificuldade(n))
            self.grupo_dificuldade.addButton(botao)
            layout_dificuldade.addWidget(botao)

        layout_jogo.addLayout(layout_dificuldade)

        # Rótulo de Status (Indica de quem é o turno)
        self.label_status = QLabel("Sua vez")
        self.label_status.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout_jogo.addWidget(self.label_status)

        # OS 9 BOTÕES DO TABULEIRO
        grade = QGridLayout()
        for i in range(9):
            botao = QPushButton("")
            botao.setFixedSize(80, 80)
            botao.setStyleSheet("font-size: 24px;")
            botao.clicked.connect(lambda _, pos=i: self.jogada_humano(pos))
            self.botoes.append(botao)
            grade.addWidget(botao, i // 3, i % 3)

        layout_jogo.addLayout(grade)

        # Botão de reinício de partida
        botao_nova_partida = QPushButton("Nova partida")
        botao_nova_partida.setStyleSheet("font-size: 16px; padding: 10px;")
        botao_nova_partida.clicked.connect(self.reiniciar)
        layout_jogo.addWidget(botao_nova_partida)
        
        layout_jogo.addStretch()

        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.VLine)

        layout_principal.addLayout(layout_jogo)
        layout_principal.addWidget(separador)
        layout_principal.addWidget(self.painel_ia)

        self.setLayout(layout_principal)

    def selecionar_dificuldade(self, nome):
        """
        SELEÇÃO DE DIFICULDADE
      
         Recebe: `nome` (str) - O nome da dificuldade selecionada.
         O que faz: Atualiza o nível de erro probabilístico utilizado pela IA.
         Devolve: Nulo (`None`).
        """
        self.dificuldade_atual = nome
        self.probabilidade_aleatoria = DIFICULDADES[nome]

    def jogada_humano(self, posicao):
        """
         A FUNÇÃO EXECUTADA QUANDO O JOGADOR CLICA
        
         Recebe: `posicao` (int) - O índice do botão clicado (0 a 8).
         O que testa:
             Se o jogo está inativo (`jogo_ativo == False`) ou se a casa já está ocupada.
              Caso positivo, encerra a função sem aplicar a jogada.
         O que faz:
             Atualiza a matriz `self.tabuleiro` com "X".
             Altera o texto do botão clicado para "X".
             Verifica se o movimento resultou em fim de jogo.
             Se o jogo continuar: altera o status da vez, trava os botões para impedir 
              cliques adicionais e agenda o turno da IA com um pequeno atraso (300ms).
         Devolve: Nulo (`None`).
        """
        if not self.jogo_ativo or self.tabuleiro[posicao] != "":
            return

        self.tabuleiro[posicao] = JOGADOR_HUMANO
        self.botoes[posicao].setText(JOGADOR_HUMANO)

        if self.verificar_fim_de_jogo():
            return

        self.label_status.setText("Vez da IA")
        self.travar_tabuleiro(True)
        QTimer.singleShot(300, self.turno_ia)

    def escolher_jogada(self, melhor_posicao, avaliacoes):
        """
        SELEÇÃO DE JOGADA COM BASE NA DIFICULDADE

         Recebe: 
             `melhor_posicao` (int): A casa ótima indicada pelo algoritmo Minimax.
             `avaliacoes` (list): A lista contendo todas as jogadas possíveis e suas notas.
         O que testa:
             Gera um número aleatório. Se for menor que `self.probabilidade_aleatoria`, 
              decide cometer um "erro" proposital.
         O que faz: Escolhe uma posição subótima (caso o teste de erro passe) ou mantém a melhor posição.
         Devolve: A posição final escolhida (int).
        """
        if random.random() < self.probabilidade_aleatoria:
            posicoes_piores = [pos for pos, _ in avaliacoes if pos != melhor_posicao]
            if posicoes_piores:
                return random.choice(posicoes_piores)
        return melhor_posicao

    def turno_ia(self):
        """
        EXECUÇÃO DA IA E ANIMAÇÃO DOS NEURÔNIOS
         Recebe: 'self'.
         O que faz:
             Chama a função `melhor_jogada` do algoritmo Minimax.
             Executa o filtro de dificuldade em `escolher_jogada`.
             Inicia a animação sequencial no `painel_ia`, preenchendo as avaliações 
              das casas uma a uma com um intervalo temporizado (`QTimer`).
             Agenda a execução final do movimento da IA para quando a animação terminar.
         Devolve: Nulo (`None`).
        """
        melhor_posicao, avaliacoes = melhor_jogada(self.tabuleiro, JOGADOR_IA, JOGADOR_HUMANO)
        posicao_escolhida = self.escolher_jogada(melhor_posicao, avaliacoes)
        self.painel_ia.iniciar_analise()

        for indice, (pos, pontuacao) in enumerate(avaliacoes):
            atraso = ATRASO_ENTRE_ANALISES_MS * (indice + 1)
            QTimer.singleShot(
                atraso,
                lambda p=pos, pt=pontuacao: self.painel_ia.adicionar_avaliacao(p, pt)
            )

        atraso_final = ATRASO_ENTRE_ANALISES_MS * (len(avaliacoes) + 1)
        QTimer.singleShot(atraso_final, lambda: self.executar_jogada_ia(posicao_escolhida, avaliacoes))

    def executar_jogada_ia(self, posicao, avaliacoes):
        """
        A JOGADA DA IA
         Recebe:
             `posicao` (int): A casa definida para a jogada.
             `avaliacoes` (list): Lista de notas das posições para exibição de status.
         O que faz:
             Destaca visualmente no painel a escolha tomada.
             Marca a casa com "O" no tabuleiro lógico e na interface gráfica.
             Testa se a jogada finalizou a partida.
             Se o jogo continuar: devolve a vez ao jogador humano e destrava os botões.
         Devolve: Nulo (`None`).
        """
        pontuacao_escolhida = next((pt for p, pt in avaliacoes if p == posicao), 0)
        self.painel_ia.mostrar_escolha(posicao, pontuacao_escolhida)

        self.tabuleiro[posicao] = JOGADOR_IA
        self.botoes[posicao].setText(JOGADOR_IA)

        if self.verificar_fim_de_jogo():
            return

        self.label_status.setText("Sua vez")
        self.travar_tabuleiro(False)

    def verificar_fim_de_jogo(self):
        """
         VERIFICAÇÃO DE VITÓRIA,TÉRMINO DA PARTIDA
       
         Recebe: 'self'.
        O que testa:
             Chama `verificar_vencedor(self.tabuleiro)` para buscar trincas.
             Chama `tabuleiro_cheio(self.tabuleiro)` para checar empate.
         O que faz:
             Se houver vencedor: Atualiza a pontuação do jogador correspondente no placar, 
              altera o rótulo de status e exibe uma caixa de mensagem (`QMessageBox`).
             Se houver empate: Incrementa o contador de empates e exibe aviso de empate.
         O que devolve:
             `True` se a partida chegou ao fim.
             `False` se o jogo deve continuar.
        """
        vencedor = verificar_vencedor(self.tabuleiro)
        if vencedor:
            self.jogo_ativo = False
            if vencedor == JOGADOR_HUMANO:
                texto = "Você venceu!"
                self.label_status.setText("você venceu")
                self.placar_jogador += 1
            else:
                texto = "A IA venceu!"
                self.label_status.setText("A IA venceu")
                self.placar_ia += 1
                
            self.atualizar_placar()
            QMessageBox.information(self, "Fim de jogo", texto)
            return True

        if tabuleiro_cheio(self.tabuleiro):
            self.jogo_ativo = False
            self.label_status.setText("empate")
            self.placar_empates += 1
            self.atualizar_placar()
            QMessageBox.information(self, "Fim de jogo", "Empate!")
            return True

        return False
        
    def atualizar_placar(self):
        """
        ATUALIZAÇÃO DE PLACAR
    
         Recebe: 'self'.
         O que faz: Formata o texto atualizado dos pontos e aplica no elemento `label_placar`.
         Devolve: Nulo (`None`).
        """
        self.label_placar.setText(f"Jogador: {self.placar_jogador} | IA: {self.placar_ia} | Empates: {self.placar_empates}")

    def travar_tabuleiro(self, travado):
        """
        BLOQUEIO TEMPORÁRIO DOS BOTÕES
         Recebe: `travado` (bool) - `True` para desabilitar, `False` para habilitar.
         O que faz: Desabilita as casas vazias durante o turno de processamento da IA
            para evitar que o usuário clique fora de hora.
         Devolve: Nulo (`None`).
        """
        for i, botao in enumerate(self.botoes):
            if self.tabuleiro[i] == "":
                botao.setEnabled(not travado)

    def reiniciar(self):
        """
        REINÍCIO DA PARTIDA
          Recebe: 'self'.
         O que faz:
             Limpa a lista `self.tabuleiro` preenchendo novamente com 9 posições vazias ("").
         Reativa a flag `self.jogo_ativo = True`.
             Restaura os rótulos de texto de todos os botões para `""` e reabilita o clique neles.
             Limpa o painel visual da IA chamando `self.painel_ia.reiniciar()`.
             Reseta o texto de status do turno para "Sua vez".
        Devolve: Nulo (`None`).
        """
        self.tabuleiro = [""] * 9
        self.jogo_ativo = True
        self.label_status.setText("Sua vez")
        for botao in self.botoes:
            botao.setText("")
            botao.setEnabled(True)
        self.painel_ia.reiniciar()

# Bloco de inicialização da aplicação Qt
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = JanelaJogo()
    janela.show()
    sys.exit(app.exec())