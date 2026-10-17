"""Rede neural recorrente esparsa para experimentação; não é consciência nem IA geral."""
from collections import deque
from pathlib import Path
import math, random, time
from .memory_store import MemoryStore

class NeuralCore:
    def __init__(self,nodes=240,seed=7,data_dir=None):
        self.node_count=max(12,min(int(nodes),2000)); self.random=random.Random(seed); self.running=False; self.tick_count=0; self.last_activity=0.0
        self.values=[self.random.uniform(-.08,.08) for _ in range(self.node_count)]; self.links=[]
        seen=set()
        for i in range(self.node_count):
            for _ in range(4):
                j=self.random.randrange(self.node_count)
                if i!=j and (i,j) not in seen: self.links.append([i,j,self.random.uniform(-.7,.7)]); seen.add((i,j))
        self.logs=deque(maxlen=300); self.learning_steps=0
        self.memory=MemoryStore(Path(data_dir or Path(__file__).resolve().parents[1]/'data')/'cybercronw.sqlite3')
        self.log(f'Rede criada: {self.node_count} nós e {len(self.links)} conexões direcionadas.')
    def log(self,msg):
        entry={'time':time.strftime('%H:%M:%S'),'message':str(msg)[:500]}; self.logs.append(entry); self.memory.add_event('núcleo',entry['message'])
    def stimulate(self):
        for _ in range(max(1,self.node_count//30)):
            i=self.random.randrange(self.node_count); self.values[i]=max(-1.,min(1.,self.values[i]+self.random.uniform(.45,.9)))
        self.log('Estímulo experimental aplicado.'); return self.status()
    def tick(self):
        if self.running:
            incoming=[0.]*self.node_count; degree=[0]*self.node_count
            for i,j,w in self.links: incoming[j]+=self.values[i]*w; degree[j]+=1
            self.values=[math.tanh(old*.62+(incoming[i]/max(1,degree[i]))*.72+self.random.uniform(-.015,.015)) for i,old in enumerate(self.values)]
            self.tick_count+=1; self.last_activity=sum(abs(v) for v in self.values)/self.node_count
            if self.tick_count%25==0:self.log(f'Ciclo {self.tick_count}: atividade média {self.last_activity:.4f}.')
        return self.status()
    def save_memory(self,label):
        mid=self.memory.save_pattern(label,self.values); self.log(f'Memória #{mid} gravada de forma persistente.'); return {'ok':True,'id':mid,'label':label,'counts':self.memory.counts()}
    def recall_memory(self,mid):
        pattern=self.memory.get_pattern(mid)
        if not pattern: raise ValueError('Memória não encontrada.')
        if len(pattern['values'])!=self.node_count: raise ValueError('A memória pertence a uma rede de tamanho diferente.')
        distance=sum(abs(a-b) for a,b in zip(self.values,pattern['values']))/self.node_count
        self.values=list(pattern['values']); self.log(f'Memória #{mid} recuperada; distância antes da recuperação: {distance:.5f}.')
        return {'ok':True,'id':pattern['id'],'label':pattern['label'],'distance_before_recall':round(distance,5),'status':self.status()}
    def learn(self,reward=1.0):
        try: reward=float(reward)
        except (ValueError,TypeError): raise ValueError('Recompensa deve ser numérica.')
        if not math.isfinite(reward) or not -1<=reward<=1: raise ValueError('Recompensa deve estar entre -1 e 1.')
        # Regra didática de correlação local, limitada para estabilidade; não é aprendizado geral.
        updated=[]
        for i,j,w in self.links:
            delta=max(-.02,min(.02,reward*self.values[i]*self.values[j]*.04))
            updated.append([i,j,max(-.9,min(.9,w+delta))])
        self.links=updated; self.learning_steps+=1; self.log(f'Passo de ajuste experimental #{self.learning_steps}; recompensa={reward:.2f}.')
        return {'ok':True,'learning_steps':self.learning_steps,'status':self.status()}
    def create_task(self,title,description=''):
        return self.memory.add_task(title,description)
    def update_task(self,tid,status):
        task=self.memory.set_task_status(tid,status)
        if task is None: raise ValueError('Tarefa não encontrada.')
        return task
    def reset(self):
        self.running=False; self.tick_count=0; self.values=[self.random.uniform(-.08,.08) for _ in range(self.node_count)]; self.last_activity=0.; self.log('Estado neural volátil reiniciado; memória persistente preservada.')
    def status(self):
        counts=self.memory.counts()
        return {'name':'CYBERCRONW — Núcleo Neural','version':'0.4','running':self.running,'nodes':self.node_count,'connections':len(self.links),'cycles':self.tick_count,'activity':round(sum(abs(v) for v in self.values)/self.node_count,5),'active_nodes':sum(abs(v)>.12 for v in self.values),'values':[round(v,4) for v in self.values],'links':[[i,j,round(w,3)] for i,j,w in self.links],'memory_count':counts['memories'],'persistent_events':counts['persistent_events'],'task_count':counts['tasks'],'learning_steps':self.learning_steps,'logs':list(self.logs)[-30:]}
