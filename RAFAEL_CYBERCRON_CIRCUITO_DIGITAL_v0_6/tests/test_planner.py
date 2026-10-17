import tempfile, unittest
from pathlib import Path
from core.planner import TaskPlanner
from core.neural_core import NeuralCore
from core.benchmark import run_benchmarks
class PlannerTests(unittest.TestCase):
 def test_plan_has_verifiable_steps(self):
  p=TaskPlanner().plan('Construir dashboard local','Sem acesso externo')
  self.assertGreaterEqual(len(p['steps']),6); self.assertTrue(all(s['check'] for s in p['steps'])); self.assertEqual(p['status'],'rascunho_aguardando_aprovacao')
 def test_critical_task_adds_approval_gate(self):
  p=TaskPlanner().plan('Implementar pagamento Pix')
  self.assertTrue(any('aprovação' in s['title'].lower() for s in p['steps']))
 def test_empty_objective_rejected(self):
  with self.assertRaises(ValueError): TaskPlanner().plan('')
 def test_plan_persistence(self):
  with tempfile.TemporaryDirectory() as d:
   c=NeuralCore(nodes=24,data_dir=Path(d)); p=TaskPlanner().plan('Construir módulo local'); ref=c.memory.save_plan(p); self.assertEqual(c.memory.get_plan(ref['id'])['objective'],'Construir módulo local')
 def test_benchmark(self):
  b=run_benchmarks(); self.assertEqual(b['passed'],b['total'])
if __name__=='__main__': unittest.main()
