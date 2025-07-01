import pickle

import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier


class agent():
    arvore = DecisionTreeClassifier
    arvore_count = DecisionTreeClassifier
    reglog = LogisticRegression
    reglog_count = LogisticRegression
    
    def __init__(self, folder):
        '''
        Agente que contém os métodos para prever as jogadas

        Argumentos:
        - folder: (pasta onde estão os modelos com .pkl)
        '''

        self.arvore = pickle.load(open(f'{folder}/arvore.pkl', 'rb'))
        self.arvore_count = pickle.load(open(f'{folder}/arvore_count.pkl', 'rb'))
        self.reglog = pickle.load(open(f'{folder}/reglog.pkl', 'rb'))
        self.reglog_count = pickle.load(open(f'{folder}/reglog_count.pkl', 'rb'))
    
    def jogar(self, dealer, player, count=None, regressao=False) -> str:
        '''
        Prevê as jogadas. Retorna uma das strings "pedir", "double", "split" ou "parar". 

        Argumentos:
        - dealer: inteiro que representa o valor da carta virada do dealer
        - player: inteiro que representa o valor somado das cartas do jogador
        - count: (opcional) inteiro que representa o valor do true count
        - regressao: usa o método de regressão linear ao invés da árvore de decisão
        '''

        df = pd.DataFrame([(dealer, player)], columns=['dealer_final', 'player_final'])
        
        r = ''

        if count != None:
            df['true_count'] = count

            if regressao:
                r = self.reglog_count.predict(df)

            else:
                r = self.arvore_count.predict(df)

        elif regressao:
            r = self.reglog.predict(df)

        else:
            r = self.arvore.predict(df)
        
        match r:
            case 'H':
                return 'pedir'

            case 'D':
                return 'double'
            
            case 'P':
                return 'split'
            
            case 'S':
                return 'parar'


def main():
    a = agent('Agent/out')  # Diretório onde estão os arquivos com os modelos treinados
    print(a.jogar(10, 7))
    print(a.jogar(4, 16))
    print(a.jogar(4, 18))
    print(a.jogar(5, 10))


if __name__ == '__main__':
    main()
