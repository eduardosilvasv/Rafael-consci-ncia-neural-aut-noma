"""Avaliação explícita e rastreável de resultados experimentais."""
from datetime import datetime

class OutcomeEvaluator:
    """Registra observações fornecidas pelo operador; não inventa evidências."""
    def __init__(self, store):
        self.store = store

    def evaluate(self, objective, criterion, expected, observed, score, threshold=80, evidence=''):
        result = self.store.save_evaluation(objective, criterion, expected, observed, score, threshold, evidence)
        result['interpretation'] = (
            'O resultado atingiu o limite definido pelo operador.' if result['passed']
            else 'O resultado ficou abaixo do limite; revisar hipótese, método ou implementação.'
        )
        result['limitation'] = 'A avaliação depende dos dados informados pelo operador; não comprova inteligência geral.'
        return result
