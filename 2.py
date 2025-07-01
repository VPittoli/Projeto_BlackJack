# ====================================
# BLACKJACK: TABELA DE ESTRATÉGIA FIXA
# ====================================

# Tabela completa 
tabela = {
    # Mãos hard
    (8, 2): 'P', (8, 3): 'P', (8, 4): 'P', (8, 5): 'P', (8, 6): 'P', (8, 7): 'P', (8, 8): 'P', (8, 9): 'P', (8, 10): 'P', (8, 11): 'P',
    (9, 2): 'DB', (9, 3): 'DB', (9, 4): 'DB', (9, 5): 'DB', (9, 6): 'DB', (9, 7): 'P', (9, 8): 'P', (9, 9): 'P', (9, 10): 'P', (9, 11): 'P',
    (10, 2): 'DB', (10, 3): 'DB', (10, 4): 'DB', (10, 5): 'DB', (10, 6): 'DB', (10, 7): 'DB', (10, 8): 'DB', (10, 9): 'DB', (10, 10): 'P', (10, 11): 'P',
    (11, 2): 'DB', (11, 3): 'DB', (11, 4): 'DB', (11, 5): 'DB', (11, 6): 'DB', (11, 7): 'DB', (11, 8): 'DB', (11, 9): 'DB', (11, 10): 'DB', (11, 11): 'DB',
    (12, 2): 'P', (12, 3): 'P', (12, 4): 'F', (12, 5): 'F', (12, 6): 'F', (12, 7): 'P', (12, 8): 'P', (12, 9): 'P', (12, 10): 'P', (12, 11): 'P',
    (13, 2): 'F', (13, 3): 'F', (13, 4): 'F', (13, 5): 'F', (13, 6): 'F', (13, 7): 'P', (13, 8): 'P', (13, 9): 'P', (13, 10): 'P', (13, 11): 'P',
    (14, 2): 'F', (14, 3): 'F', (14, 4): 'F', (14, 5): 'F', (14, 6): 'F', (14, 7): 'P', (14, 8): 'P', (14, 9): 'P', (14, 10): 'P/D', (14, 11): 'P',
    (15, 2): 'F', (15, 3): 'F', (15, 4): 'F', (15, 5): 'F', (15, 6): 'F', (15, 7): 'P', (15, 8): 'P', (15, 9): 'P/D', (15, 10): 'P/D', (15, 11): 'P',
    (16, 2): 'F', (16, 3): 'F', (16, 4): 'F', (16, 5): 'F', (16, 6): 'F', (16, 7): 'P', (16, 8): 'P/D', (16, 9): 'P/D', (16, 10): 'P/D', (16, 11): 'P',
    (17, 2): 'F', (17, 3): 'F', (17, 4): 'F', (17, 5): 'F', (17, 6): 'F', (17, 7): 'F', (17, 8): 'F', (17, 9): 'F', (17, 10): 'F', (17, 11): 'F',

    # Exemplos soft (A,x)
    ('A,2', 2): 'P', ('A,2', 3): 'DB', ('A,2', 4): 'DB', ('A,2', 5): 'DB', ('A,2', 6): 'DB',
    ('A,2', 7): 'P', ('A,2', 8): 'P', ('A,2', 9): 'P', ('A,2', 10): 'P', ('A,2', 11): 'P',
    ('A,6', 2): 'DB', ('A,6', 3): 'DB', ('A,6', 4): 'DB', ('A,6', 5): 'DB', ('A,6', 6): 'DB',
    ('A,6', 7): 'F', ('A,6', 8): 'P', ('A,6', 9): 'P', ('A,6', 10): 'P', ('A,6', 11): 'P',

    # Exemplos par
    ('2,2', 2): 'D', ('2,2', 3): 'D', ('2,2', 4): 'P', ('2,2', 5): 'P', ('2,2', 6): 'P',
    ('8,8', 2): 'D', ('8,8', 3): 'D', ('8,8', 4): 'D', ('8,8', 5): 'D', ('8,8', 6): 'D',
    ('8,8', 7): 'D', ('8,8', 8): 'D', ('8,8', 9): 'D', ('8,8', 10): 'D', ('8,8', 11): 'D',
    ('A,A', 2): 'D', ('A,A', 3): 'D', ('A,A', 4): 'D', ('A,A', 5): 'D', ('A,A', 6): 'D',
    ('A,A', 7): 'D', ('A,A', 8): 'D', ('A,A', 9): 'D', ('A,A', 10): 'D', ('A,A', 11): 'D',
}

def tipo_mao(cartas):
    if len(cartas) == 2 and cartas[0] == cartas[1]:
        return 'par'
    elif 1 in cartas:
        return 'soft'
    else:
        return 'hard'

def total_mao(cartas):
    total = sum(cartas)
    if tipo_mao(cartas) == 'soft':
        return f"A,{total - 1}"  # Exemplo: A,6 para A+6
    elif tipo_mao(cartas) == 'par':
        return f"{cartas[0]},{cartas[1]}"
    else:
        return total

def decisao_tabela(cartas, dealer):
    valor_dealer = 11 if dealer == 'A' else dealer
    chave = (total_mao(cartas), valor_dealer)
    return tabela.get(chave, 'P')  # Padrão: Pedir carta

# --------------------------
# EXEMPLOS DE USO
# --------------------------

mao = [1, 6]   # A,6
dealer = 6
print(f"Decisão: {decisao_tabela(mao, dealer)}")  # Espera: DB

mao2 = [8, 8]
dealer2 = 10
print(f"Decisão: {decisao_tabela(mao2, dealer2)}")  # Espera: D

mao3 = [10, 6]
dealer3 = 10
print(f"Decisão: {decisao_tabela(mao3, dealer3)}")  # Espera: P/D
