"""Benchmarks locais simples e reproduzíveis; não medem consciência ou inteligência geral."""
import math, time, tempfile
from .neural_core import NeuralCore

def run_benchmarks():
    started=time.perf_counter(); temp=tempfile.TemporaryDirectory(); core=NeuralCore(nodes=120,seed=101,data_dir=temp.name)
    s0=core.status(); core.stimulate(); core.save_memory('benchmark'); saved=core.memory.get_pattern(1)['values']
    core.stimulate(); recall=core.recall_memory(1); exact=core.values==saved
    core.running=True
    for _ in range(20): core.tick()
    core.learn(.5)
    weights_ok=all(math.isfinite(link[2]) and -.9<=link[2]<=.9 for link in core.links)
    elapsed=round(time.perf_counter()-started,4)
    checks=[{'name':'Rede inicializada','passed':s0['nodes']==120},{'name':'Memória recupera o estado salvo','passed':exact and recall['distance_before_recall']>=0},{'name':'20 ciclos de propagação','passed':core.tick_count==20},{'name':'Pesos permanecem dentro dos limites','passed':weights_ok}]
    result={'benchmark':'CYBERCRONW-LOCAL-001','elapsed_seconds':elapsed,'passed':sum(c['passed'] for c in checks),'total':len(checks),'checks':checks,'scope':'Teste funcional do protótipo; não mede raciocínio geral, consciência nem utilidade no mundo real.'}
    temp.cleanup()
    return result
