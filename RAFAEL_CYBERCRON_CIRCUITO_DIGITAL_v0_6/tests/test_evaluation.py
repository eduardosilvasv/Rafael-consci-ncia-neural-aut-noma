import tempfile, unittest
from pathlib import Path
from core.neural_core import NeuralCore
from core.evaluation import OutcomeEvaluator

class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.core=NeuralCore(nodes=24,data_dir=Path(self.temp.name))
        self.evaluator=OutcomeEvaluator(self.core.memory)
    def tearDown(self): self.temp.cleanup()
    def test_passes_at_threshold_and_persists(self):
        r=self.evaluator.evaluate('Testar planejador','Etapas verificáveis','6 etapas','6 etapas',90,80,'teste local')
        self.assertTrue(r['passed']); self.assertEqual(self.core.memory.get_evaluation(r['id'])['threshold'],80)
    def test_below_threshold_fails(self):
        r=self.evaluator.evaluate('Testar interface','Sem erro crítico','sem erro','um erro',65,80)
        self.assertFalse(r['passed'])
    def test_invalid_score_rejected(self):
        with self.assertRaises(ValueError): self.evaluator.evaluate('Testar interface','critério','x','y',101)
    def test_required_fields(self):
        with self.assertRaises(ValueError): self.evaluator.evaluate('abc','','x','y',50)
    def test_history(self):
        self.evaluator.evaluate('Verificar histórico','passou','sim','sim',100,80)
        self.assertEqual(len(self.core.memory.list_evaluations()),1)
if __name__=='__main__': unittest.main()
