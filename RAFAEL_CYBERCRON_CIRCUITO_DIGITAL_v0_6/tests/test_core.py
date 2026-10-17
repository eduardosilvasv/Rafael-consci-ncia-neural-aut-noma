import tempfile, unittest
from pathlib import Path
from core.neural_core import NeuralCore
class CoreTests(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.core=NeuralCore(nodes=40,seed=4,data_dir=Path(self.tmp.name))
 def tearDown(self): self.tmp.cleanup()
 def test_status_shape(self):
  s=self.core.status(); self.assertEqual(s['nodes'],40); self.assertGreater(s['connections'],0)
 def test_memory_round_trip(self):
  self.core.stimulate(); self.core.save_memory('teste'); self.core.stimulate(); result=self.core.recall_memory(1); self.assertGreater(result['distance_before_recall'],0.0); self.assertEqual(self.core.values,self.core.memory.get_pattern(1)['values'])
 def test_memory_survives_new_core(self):
  self.core.save_memory('persistente'); second=NeuralCore(nodes=40,seed=9,data_dir=Path(self.tmp.name)); self.assertEqual(second.memory.list_memories()[0]['label'],'persistente')
 def test_learning_bounds(self):
  before=[x[2] for x in self.core.links]; self.core.learn(.7); after=[x[2] for x in self.core.links]; self.assertTrue(all(-.9<=w<=.9 for w in after)); self.assertEqual(len(before),len(after))
 def test_invalid_reward(self):
  with self.assertRaises(ValueError): self.core.learn(4)
 def test_task_approval_flow(self):
  t=self.core.create_task('Tarefa teste','resultado'); self.assertEqual(t['status'],'aguardando_aprovacao'); t=self.core.update_task(t['id'],'aprovada'); self.assertEqual(t['status'],'aprovada')
if __name__=='__main__': unittest.main()
