import sys
import random
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

valores = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'V', 'D', 'R', 'A']
naipes = ['P', 'E', 'O', 'C']  # Paus, Espadas, Ouros, Copas

def calcular_valor(mao):
    total = 0
    ases = 0
    for carta in mao:
        valor = carta[:-1]
        if valor in ['V', 'D', 'R']:
            total += 10
        elif valor == 'A':
            total += 11
            ases += 1
        else:
            total += int(valor)
    while total > 21 and ases:
        total -= 10
        ases -= 1
    return total

def is_blackjack(mao):
    return len(mao) == 2 and calcular_valor(mao) == 21

class BlackjackWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blackjack PySide6")
        pixmap_mesa = QPixmap("mesa.png")
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(pixmap_mesa)
        self.bg_label.setGeometry(0, 0, pixmap_mesa.width(), pixmap_mesa.height())
        self.setFixedSize(pixmap_mesa.width(), pixmap_mesa.height())

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(20, 20, 20, 20)
        self.layout_principal.setSpacing(15)

        self.layout_principal.addSpacing(150)

        self.container_dealer = QWidget(self)
        self.container_dealer.setFixedSize(pixmap_mesa.width(), 120)
        self.container_dealer.setStyleSheet("background: transparent;")
        self.layout_principal.addWidget(self.container_dealer)

        self.label_pont_dealer = QLabel("")
        self.label_pont_dealer.setStyleSheet("color: black; font-size: 20px; font-weight: bold; background-color: cyan;")
        self.layout_principal.addWidget(self.label_pont_dealer, alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout_principal.addSpacing(150)

        self.container_maos = QWidget(self)
        self.container_maos.setFixedSize(pixmap_mesa.width(), 150)
        self.container_maos.setStyleSheet("background: transparent;")
        self.layout_principal.addWidget(self.container_maos)

        self.label_resultado = QLabel("")
        self.label_resultado.setStyleSheet("color: yellow; font-size: 20px; font-weight: bold;")
        self.layout_principal.addWidget(self.label_resultado, alignment=Qt.AlignmentFlag.AlignCenter)

        self.botoes_layout = QHBoxLayout()
        self.btn_pedir = QPushButton("Pedir")
        self.btn_parar = QPushButton("Parar")
        self.btn_split = QPushButton("Split")
        self.btn_double = QPushButton("Double")
        self.btn_nova = QPushButton("Nova Rodada")
        for btn in (self.btn_pedir, self.btn_parar, self.btn_split, self.btn_double, self.btn_nova):
            self.botoes_layout.addWidget(btn)
        self.layout_principal.addLayout(self.botoes_layout)

        self.btn_pedir.clicked.connect(self.pedir_carta)
        self.btn_parar.clicked.connect(self.parar_vez)
        self.btn_split.clicked.connect(self.fazer_split)
        self.btn_double.clicked.connect(self.fazer_double)
        self.btn_nova.clicked.connect(self.nova_partida)

        self.fichas = 10000 # Numero de Fichas
        self.aposta = 100 # Aposta

        self.label_fichas = QLabel(self)
        self.label_fichas.setText(f"Fichas: {self.fichas}")
        self.label_fichas.setStyleSheet("""
            color: white; 
            font-size: 16px; 
            font-weight: bold; 
            background-color: rgba(0,0,0,0.6); 
            padding: 5px; 
            border-radius: 5px;
        """)
        largura_label = 140
        self.label_fichas.setFixedWidth(largura_label)
        self.label_fichas.move(self.width() - largura_label - 20, 20)
        self.label_fichas.show()

        self.label_ganho = QLabel(self)
        self.label_ganho.setText("")
        self.label_ganho.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            background-color: rgba(0,0,0,0.6);
            padding: 3px;
            border-radius: 5px;
        """)
        self.label_ganho.setFixedWidth(largura_label)
        self.label_ganho.move(self.width() - largura_label - 20, 20 + self.label_fichas.height() + 5)
        self.label_ganho.show()

        self.deck = []
        self.maos = []
        self.mao_dealer = []
        self.mao_ativa_idx = 0
        self.mao_ativa_terminada = False
        self.carta_revelada = False
        self.jogador_estourou = []
        
        self.timer_animar_fichas = None
        
        self.nova_partida()

    def animar_fichas(self, valor_final):
        texto_atual = self.label_fichas.text()
        try:
            valor_atual = int(texto_atual.split(":")[1].strip())
        except Exception:
            valor_atual = self.fichas  # fallback

        diferenca = valor_final - valor_atual
        passos = 30
        passo_valor = diferenca / passos if passos else diferenca
        passo_atual = 0

        def atualizar():
            nonlocal passo_atual, valor_atual
            if passo_atual < passos:
                valor_atual += passo_valor
                self.label_fichas.setText(f"Fichas: {int(valor_atual)}")
                passo_atual += 1
            else:
                self.label_fichas.setText(f"Fichas: {valor_final}")
                self.timer_animar_fichas.stop()

        if self.timer_animar_fichas and self.timer_animar_fichas.isActive():
            self.timer_animar_fichas.stop()

        self.timer_animar_fichas = QTimer()
        self.timer_animar_fichas.timeout.connect(atualizar)
        self.timer_animar_fichas.start(30)

    def atualizar_label_fichas(self):
        self.animar_fichas(self.fichas)

    def nova_partida(self):
        if self.fichas < self.aposta:
            self.label_resultado.setText("Fichas insuficientes para apostar!")
            self.btn_pedir.setEnabled(False)
            self.btn_parar.setEnabled(False)
            self.btn_split.setEnabled(False)
            self.btn_double.setEnabled(False)
            return

        if len(self.deck) <= 52 * 0.25:
            self.deck = [v + n for v in valores for n in naipes]
            random.shuffle(self.deck)

        self.fichas -= self.aposta
        self.atualizar_label_fichas()
        self.label_ganho.setStyleSheet("color: red; font-size: 14px; font-weight: bold; background-color: rgba(0,0,0,0.6); padding: 3px; border-radius: 5px;")
        self.label_ganho.setText(f"-{self.aposta}")
        
        QTimer.singleShot(2000, lambda: self.label_ganho.setText(""))

        self.maos = [[self.deck.pop(), self.deck.pop()]]
        self.jogador_estourou = [False]
        self.mao_dealer = [self.deck.pop(), self.deck.pop()]
        self.mao_ativa_idx = 0
        self.mao_ativa_terminada = False
        self.carta_revelada = False

        self.mostrar_maos()
        self.limpar_container(self.container_dealer)
        self.mostrar_cartas(self.mao_dealer, self.container_dealer, hide_second=True)
        self.label_resultado.setText("")

        for b in (self.btn_pedir, self.btn_parar, self.btn_split, self.btn_double):
            b.setEnabled(True)
        self.btn_split.setEnabled(self.pode_split())

        if is_blackjack(self.maos[0]):
            self.label_resultado.setText("Blackjack! Jogador venceu.")
            self.mao_ativa_terminada = True
            self.jogada_dealer()
            return

    def carregar_imagem(self, nome_carta):
        caminho = f"Cartas/{nome_carta}.png"
        pix = QPixmap(caminho)
        if pix.isNull():
            print(f"Erro: {caminho} não encontrado.")
        return pix.scaled(80, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def limpar_container(self, container):
        for ch in container.findChildren(QLabel):
            ch.deleteLater()
        for ch in container.findChildren(QWidget):
            ch.deleteLater()

    def mostrar_cartas(self, mao, container, hide_second=False):
        self.limpar_container(container)
        largura, altura = 80, container.height()
        inicio_x = max(0, (container.width() - largura * len(mao)) // 2)
        for i, carta in enumerate(mao):
            lbl = QLabel(container)
            if hide_second and i == 1:
                pix = QPixmap("Cartas/Verso.png").scaled(80, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            else:
                pix = self.carregar_imagem(carta)
            lbl.setPixmap(pix)
            lbl.setFixedSize(pix.size())
            lbl.move(inicio_x + i * largura, (altura - pix.height()) // 2)
            lbl.show()

        if container == self.container_dealer and not hide_second:
            self.label_pont_dealer.setText(f"Dealer: {calcular_valor(mao)}")
        elif container == self.container_dealer and hide_second:
            parcial = calcular_valor([mao[0]])
            self.label_pont_dealer.setText(f"Dealer: ? + {parcial}")

    def mostrar_maos(self):
        self.limpar_container(self.container_maos)
        largura_carta, altura_carta = 80, 120
        espac = 40
        total_w = sum(len(m) * largura_carta for m in self.maos) + (len(self.maos) - 1) * espac
        x = max(0, (self.container_maos.width() - total_w) // 2)
        altura_container = self.container_maos.height()

        for idx, mao in enumerate(self.maos):
            widget_mao = QWidget(self.container_maos)
            largura_mao = len(mao) * largura_carta
            altura_mao = altura_carta + 30
            widget_mao.setFixedSize(largura_mao, altura_mao)
            widget_mao.move(x, (altura_container - altura_mao) // 2)
            widget_mao.setStyleSheet("background: transparent;")
            widget_mao.show()

            if idx == self.mao_ativa_idx:
                linha = QLabel(widget_mao)
                linha.setGeometry(0, altura_mao - 5, largura_mao, 3)
                linha.setStyleSheet("background: red;")
                linha.show()

            for i, carta in enumerate(mao):
                lbl_carta = QLabel(widget_mao)
                pix = self.carregar_imagem(carta)
                lbl_carta.setPixmap(pix)
                lbl_carta.setFixedSize(pix.size())
                lbl_carta.move(i * largura_carta, 0)
                lbl_carta.show()

            val = calcular_valor(mao)
            lbl_valor = QLabel(widget_mao)
            lbl_valor.setText(str(val))
            lbl_valor.setStyleSheet("color: black; font-size: 20px; font-weight: bold; background-color: cyan;")
            lbl_valor.adjustSize()
            lbl_valor.move((largura_mao - lbl_valor.width()) // 2, altura_carta + 5)
            lbl_valor.show()

            x += largura_mao + espac

    def pode_split(self):
        mao = self.maos[self.mao_ativa_idx]
        if len(mao) == 2 and not self.mao_ativa_terminada and len(self.maos) < 4:
            r1, r2 = mao[0][:-1], mao[1][:-1]
            face10 = ['10', 'V', 'D', 'R']
            return r1 == r2 or (r1 in face10 and r2 in face10)
        return False

    def pedir_carta(self):
        if self.mao_ativa_terminada or not self.deck:
            return
        self.maos[self.mao_ativa_idx].append(self.deck.pop())
        self.mostrar_maos()
        self.atualizar_label_deck()
        valor_mao = calcular_valor(self.maos[self.mao_ativa_idx])
        if valor_mao > 21:
            self.label_resultado.setText(f"Mão {self.mao_ativa_idx + 1} estourou!")
            self.mao_ativa_terminada = True
            self.jogador_estourou[self.mao_ativa_idx] = True
            self.btn_pedir.setEnabled(False)
            self.btn_parar.setEnabled(False)
            self.btn_split.setEnabled(False)
            self.btn_double.setEnabled(False)
            self.proxima_mao()
            return
        else:
            self.label_resultado.setText("")
        self.btn_split.setEnabled(self.pode_split())
        self.btn_double.setEnabled(True)

    def fazer_split(self):
        if not self.pode_split():
            return
        if self.fichas < self.aposta:
            self.label_resultado.setText("Fichas insuficientes para fazer split!")
            return

        self.fichas -= self.aposta
        self.atualizar_label_fichas()
        self.label_ganho.setStyleSheet("color: red; font-size: 14px; font-weight: bold; background-color: rgba(0,0,0,0.6); padding: 3px; border-radius: 5px;")
        self.label_ganho.setText(f"-{self.aposta} (Split)")
        QTimer.singleShot(2000, lambda: self.label_ganho.setText(""))

        # Divide as cartas da mão atual
        m = self.maos[self.mao_ativa_idx]
        c1, c2 = m

        # A mão atual continua com c1 e recebe uma nova carta
        self.maos[self.mao_ativa_idx] = [c1, self.deck.pop()]

        # Cria uma nova mão apenas com c2; a nova carta será comprada quando essa mão for jogada
        self.maos.insert(self.mao_ativa_idx + 1, [c2])
        self.jogador_estourou.insert(self.mao_ativa_idx + 1, False)

        self.mao_ativa_terminada = False
        self.mostrar_maos()
        self.atualizar_label_deck()
        self.btn_split.setEnabled(self.pode_split())
        self.label_resultado.setText("")

    def fazer_double(self):
        # Double só pode ser feito no início da mão (2 cartas), e se houver fichas suficientes
        mao = self.maos[self.mao_ativa_idx]
        if len(mao) != 2 or self.mao_ativa_terminada:
            return
        if self.fichas < self.aposta:
            self.label_resultado.setText("Fichas insuficientes para fazer Double!")
            return

        self.fichas -= self.aposta
        self.atualizar_label_fichas()
        self.label_ganho.setStyleSheet("color: red; font-size: 14px; font-weight: bold; background-color: rgba(0,0,0,0.6); padding: 3px; border-radius: 5px;")
        self.label_ganho.setText(f"-{self.aposta} (Double)")
        QTimer.singleShot(2000, lambda: self.label_ganho.setText(""))

        # Compra uma carta e termina a vez da mão
        self.maos[self.mao_ativa_idx].append(self.deck.pop())
        self.mostrar_maos()
        self.atualizar_label_deck()

        self.mao_ativa_terminada = True
        self.btn_pedir.setEnabled(False)
        self.btn_parar.setEnabled(False)
        self.btn_split.setEnabled(False)
        self.btn_double.setEnabled(False)

        valor_mao = calcular_valor(self.maos[self.mao_ativa_idx])
        if valor_mao > 21:
            self.label_resultado.setText(f"Mão {self.mao_ativa_idx + 1} estourou!")
            self.jogador_estourou[self.mao_ativa_idx] = True

        self.proxima_mao()

    def proxima_mao(self):
        if self.mao_ativa_idx + 1 < len(self.maos):
            self.mao_ativa_idx += 1
            self.mao_ativa_terminada = False
            if self.jogador_estourou[self.mao_ativa_idx]:
                self.proxima_mao()
                return

            # Compra a segunda carta da nova mão dividida aqui (no momento em que começa a jogá-la)
            if len(self.maos[self.mao_ativa_idx]) == 1:
                self.maos[self.mao_ativa_idx].append(self.deck.pop())
                self.mostrar_maos()
                self.atualizar_label_deck()

            self.label_resultado.setText(f"Agora é a vez da mão {self.mao_ativa_idx + 1}.")
            self.mostrar_maos()
            self.btn_pedir.setEnabled(True)
            self.btn_parar.setEnabled(True)
            self.btn_split.setEnabled(self.pode_split())
            self.btn_double.setEnabled(True)
        else:
            self.jogada_dealer()

    def parar_vez(self):
        self.mao_ativa_terminada = True
        self.label_resultado.setText(f"Você parou a mão {self.mao_ativa_idx + 1}.")
        self.proxima_mao()

    def jogada_dealer(self):
        for b in (self.btn_pedir, self.btn_parar, self.btn_split, self.btn_double):
            b.setEnabled(False)

        self.limpar_container(self.container_dealer)

        if all(self.jogador_estourou):
            self.label_resultado.setText("Todas as mãos estouraram! Dealer não joga.")
            return

        self.carta_revelada = True
        self.mostrar_cartas(self.mao_dealer, self.container_dealer, hide_second=False)

        def c():
            if calcular_valor(self.mao_dealer) < 17 and self.deck:
                self.mao_dealer.append(self.deck.pop())
                self.limpar_container(self.container_dealer)
                self.mostrar_cartas(self.mao_dealer, self.container_dealer, hide_second=False)
                self.atualizar_label_deck()
                QTimer.singleShot(700, c)
            else:
                self.verificar_resultados()

        QTimer.singleShot(700, c)

    def verificar_resultados(self):
        vd = calcular_valor(self.mao_dealer)
        res = []
        ganho_total = 0

        for idx, m in enumerate(self.maos):
            v = calcular_valor(m)
            ganho = 0

            if v > 21 and vd > 21:
                res.append(f"Mão {idx+1}: Empate! Ambos estouraram.")
                ganho = self.aposta
            elif v > 21:
                res.append(f"Mão {idx+1}: Estourou! Você perdeu.")
            elif vd > 21:
                res.append(f"Mão {idx+1}: Dealer estourou! Você venceu.")
                ganho = self.aposta * 2
            elif is_blackjack(m) and not is_blackjack(self.mao_dealer):
                res.append(f"Mão {idx+1}: Blackjack! Você ganhou 3:2.")
                ganho = int(self.aposta * 2.5)
            elif is_blackjack(m) and is_blackjack(self.mao_dealer):
                res.append(f"Mão {idx+1}: Empate com Blackjack.")
                ganho = self.aposta
            elif v > vd:
                res.append(f"Mão {idx+1}: Você venceu!")
                ganho = self.aposta * 2
            elif v < vd:
                res.append(f"Mão {idx+1}: Você perdeu.")
            else:
                res.append(f"Mão {idx+1}: Empate.")
                ganho = self.aposta

            ganho_total += ganho

        self.fichas += ganho_total
        self.atualizar_label_fichas()
        ganho_exibicao = ganho_total

        if ganho_exibicao > 0:
            self.label_ganho.setStyleSheet("color: green; font-size: 14px; font-weight: bold; background-color: rgba(0,0,0,0.6); padding: 3px; border-radius: 5px;")
        else:
            self.label_ganho.setStyleSheet("color: red; font-size: 14px; font-weight: bold; background-color: rgba(0,0,0,0.6); padding: 3px; border-radius: 5px;")

        self.label_ganho.setText(f"{'+' if ganho_exibicao > 0 else ''}{ganho_exibicao}")
        self.label_resultado.setText("\n".join(res))

    def atualizar_label_deck(self):
        # Pode adicionar se quiser mostrar cartas restantes, por exemplo
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BlackjackWindow()
    window.show()
    sys.exit(app.exec())
