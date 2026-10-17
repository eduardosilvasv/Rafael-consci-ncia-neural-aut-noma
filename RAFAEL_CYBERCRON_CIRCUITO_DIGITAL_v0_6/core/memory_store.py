"""Memória persistente local baseada em SQLite."""
from pathlib import Path
from contextlib import contextmanager
import json, sqlite3, time

class MemoryStore:
    def __init__(self, path: Path):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.session() as db:
            db.execute('CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT NOT NULL, pattern TEXT NOT NULL, created_at TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, category TEXT NOT NULL, message TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS plans (id INTEGER PRIMARY KEY AUTOINCREMENT, objective TEXT NOT NULL, plan_json TEXT NOT NULL, created_at TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS evaluations (id INTEGER PRIMARY KEY AUTOINCREMENT, objective TEXT NOT NULL, criterion TEXT NOT NULL, expected TEXT NOT NULL, observed TEXT NOT NULL, score REAL NOT NULL, threshold REAL NOT NULL, passed INTEGER NOT NULL, evidence TEXT NOT NULL, created_at TEXT NOT NULL)')
    def connect(self):
        db=sqlite3.connect(self.path, timeout=5); db.row_factory=sqlite3.Row; return db
    @contextmanager
    def session(self):
        db=self.connect()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    @staticmethod
    def now(): return time.strftime('%Y-%m-%d %H:%M:%S')
    def add_event(self, category, message):
        with self.session() as db: db.execute('INSERT INTO events(created_at,category,message) VALUES(?,?,?)',(self.now(),str(category)[:40],str(message)[:500]))
    def save_pattern(self,label,values):
        label=str(label).strip()[:80] or 'Padrão sem nome'
        with self.session() as db:
            cur=db.execute('INSERT INTO memories(label,pattern,created_at) VALUES(?,?,?)',(label,json.dumps([round(float(v),5) for v in values]),self.now())); mid=cur.lastrowid
        self.add_event('memória',f'Padrão "{label}" salvo (ID {mid}).'); return mid
    def list_memories(self,limit=30):
        with self.session() as db: rows=db.execute('SELECT id,label,created_at FROM memories ORDER BY id DESC LIMIT ?',(max(1,min(int(limit),100)),)).fetchall()
        return [dict(r) for r in rows]
    def get_pattern(self,mid):
        with self.session() as db: row=db.execute('SELECT * FROM memories WHERE id=?',(int(mid),)).fetchone()
        if not row:return None
        return {'id':row['id'],'label':row['label'],'values':json.loads(row['pattern']),'created_at':row['created_at']}
    def add_task(self,title,description=''):
        title=str(title).strip()[:160]; description=str(description).strip()[:1000]
        if not title: raise ValueError('A tarefa precisa de um título.')
        now=self.now()
        with self.session() as db:
            cur=db.execute('INSERT INTO tasks(title,description,status,created_at,updated_at) VALUES(?,?,?,?,?)',(title,description,'aguardando_aprovacao',now,now)); tid=cur.lastrowid
        self.add_event('planejamento',f'Tarefa #{tid} criada e aguardando aprovação do operador.'); return self.get_task(tid)
    def get_task(self,tid):
        with self.session() as db: row=db.execute('SELECT * FROM tasks WHERE id=?',(int(tid),)).fetchone()
        return dict(row) if row else None
    def list_tasks(self,limit=50):
        with self.session() as db: rows=db.execute('SELECT * FROM tasks ORDER BY id DESC LIMIT ?',(max(1,min(int(limit),100)),)).fetchall()
        return [dict(r) for r in rows]
    def set_task_status(self,tid,status):
        allowed={'aguardando_aprovacao','aprovada','em_execucao','concluida','cancelada'}
        if status not in allowed: raise ValueError('Estado de tarefa inválido.')
        now=self.now()
        with self.session() as db:
            cur=db.execute('UPDATE tasks SET status=?,updated_at=? WHERE id=?',(status,now,int(tid)))
            if cur.rowcount==0:return None
        self.add_event('planejamento',f'Tarefa #{tid}: estado alterado para {status}.'); return self.get_task(tid)
    def save_plan(self, plan):
        with self.session() as db:
            cur=db.execute('INSERT INTO plans(objective,plan_json,created_at) VALUES(?,?,?)',(plan['objective'],json.dumps(plan,ensure_ascii=False),plan['created_at'])); pid=cur.lastrowid
        self.add_event('planejamento',f'Plano #{pid} salvo como rascunho aguardando aprovação.')
        return {'id':pid,'objective':plan['objective'],'status':plan['status'],'created_at':plan['created_at']}
    def list_plans(self,limit=30):
        with self.session() as db: rows=db.execute('SELECT id,objective,created_at FROM plans ORDER BY id DESC LIMIT ?',(max(1,min(int(limit),100)),)).fetchall()
        return [dict(r) for r in rows]
    def get_plan(self,pid):
        with self.session() as db: row=db.execute('SELECT plan_json FROM plans WHERE id=?',(int(pid),)).fetchone()
        return json.loads(row['plan_json']) if row else None

    def save_evaluation(self, objective, criterion, expected, observed, score, threshold=80, evidence=''):
        objective=str(objective).strip()[:200]
        criterion=str(criterion).strip()[:300]
        expected=str(expected).strip()[:500]
        observed=str(observed).strip()[:500]
        evidence=str(evidence).strip()[:1000]
        if len(objective)<4: raise ValueError('O objetivo precisa ter pelo menos quatro caracteres.')
        if not criterion: raise ValueError('Informe um critério verificável.')
        if not expected or not observed: raise ValueError('Informe o resultado esperado e o observado.')
        score=float(score); threshold=float(threshold)
        if not 0 <= score <= 100: raise ValueError('A pontuação deve estar entre 0 e 100.')
        if not 0 <= threshold <= 100: raise ValueError('O limite de aprovação deve estar entre 0 e 100.')
        passed=score>=threshold
        now=self.now()
        with self.session() as db:
            cur=db.execute('INSERT INTO evaluations(objective,criterion,expected,observed,score,threshold,passed,evidence,created_at) VALUES(?,?,?,?,?,?,?,?,?)',(objective,criterion,expected,observed,score,threshold,int(passed),evidence,now))
            eid=cur.lastrowid
        self.add_event('avaliação',f'Avaliação #{eid}: {"APROVADA" if passed else "NÃO APROVADA"} ({score:.1f}/100).')
        return self.get_evaluation(eid)
    def get_evaluation(self, eid):
        with self.session() as db: row=db.execute('SELECT * FROM evaluations WHERE id=?',(int(eid),)).fetchone()
        if not row: return None
        item=dict(row); item['passed']=bool(item['passed']); return item
    def list_evaluations(self, limit=50):
        with self.session() as db: rows=db.execute('SELECT * FROM evaluations ORDER BY id DESC LIMIT ?',(max(1,min(int(limit),100)),)).fetchall()
        result=[]
        for row in rows:
            item=dict(row); item['passed']=bool(item['passed']); result.append(item)
        return result

    def counts(self):
        with self.session() as db:
            m=db.execute('SELECT COUNT(*) FROM memories').fetchone()[0]; e=db.execute('SELECT COUNT(*) FROM events').fetchone()[0]; t=db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        return {'memories':m,'persistent_events':e,'tasks':t}
