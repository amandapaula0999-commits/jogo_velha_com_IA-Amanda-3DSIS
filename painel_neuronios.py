from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt6.QtCore import Qt

class PainelNeuronios(QWidget):
#Classe responsável por criar e gerenciar a interface gráfica do painel
#que exibe a avaliação das jogadas pela IA.
    
    
    def __init__(self):
        """

         Recebe: A instância do objeto (self).
         O que faz: 
             Inicializa a lista `self.neuronios` para guardar a referência dos 9 rótulos.
             Cria um layout em grade (`QGridLayout`) de 3x3.
             Instancia 9 rótulos (`QLabel`) com formato circular e estilo visual escuro.
             Posiciona cada rótulo no layout usando a divisão inteira (i // 3) para linha
              e o resto da divisão (i % 3) para coluna.
         Devolve: Nulo (None), mas inicializa o widget na tela.
        """
        super().__init__()
        self.neuronios = []
        grade = QGridLayout()
        
        # Criação dos 9 rótulos do painel
        for i in range(9):
            lbl = QLabel("?")
            lbl.setFixedSize(60, 60)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background-color: #333; color: white; border-radius: 30px; font-weight: bold; font-size: 16px;")
            self.neuronios.append(lbl)
            grade.addWidget(lbl, i // 3, i % 3)
            
        self.setLayout(grade)

    def iniciar_analise(self):
        """
         Recebe: Apenas 'self'.
         O que faz: Executa a limpeza do painel antes da IA calcular a próxima jogada.
         Devolve: Nulo (None).
        """
        self.reiniciar()

    def adicionar_avaliacao(self, posicao, pontuacao):
        """
           Recebe:
             `posicao` (int): Índice da casa no tabuleiro (de 0 a 8).
             `pontuacao` (int): O valor retornado pelo algoritmo (ex: Minimax).
         O que testa:
             Se `pontuacao > 0`: Define a cor verde (#4CAF50) -> Vantagem/Boa jogada.
             Se `pontuacao < 0`: Define a cor vermelha (#F44336) -> Desvantagem/Má jogada.
             Se `pontuacao == 0`: Define a cor cinza (#9E9E9E) -> Empate técnico.
         O que faz: Atualiza o texto do botão com a pontuação numérica e altera sua cor de fundo.
         Devolve: Nulo (None).
        """
        cor = "#4CAF50" if pontuacao > 0 else "#5236F4" if pontuacao < 0 else "#9E9E9E"
        self.neuronios[posicao].setText(str(pontuacao))
        self.neuronios[posicao].setStyleSheet(
            f"background-color: {cor}; color: white; border-radius: 30px; font-weight: bold; font-size: 16px;"
        )

    def mostrar_escolha(self, posicao, pontuacao):
        """
         Recebe:
             `posicao` (int): A casa escolhida para realizar a jogada (0 a 8).
             `pontuacao` (int): A pontuação associada a essa jogada final.
         O que faz: Aplica um destaque visual amarelado com borda laranja no rótulo
             da posição escolhida para indicar ao jogador a decisão tomada pela IA.
         Devolve: Nulo (None).
        """
        self.neuronios[posicao].setStyleSheet(
            "background-color: #FFD700; color: black; border-radius: 30px; font-weight: bold; font-size: 16px; border: 3px solid #FF8C00;"
        )

    def reiniciar(self):
        """
         Recebe: Apenas 'self'.
         O que faz: Percorre a lista `self.neuronios` restaurando o estado inicial
            de todos os 9 elementos (texto "?" e fundo escuro `#333`).
         Devolve: Nulo (None).
        """
        for lbl in self.neuronios:
            lbl.setText("?")
            lbl.setStyleSheet("background-color: #333; color: white; border-radius: 30px; font-weight: bold; font-size: 16px;")