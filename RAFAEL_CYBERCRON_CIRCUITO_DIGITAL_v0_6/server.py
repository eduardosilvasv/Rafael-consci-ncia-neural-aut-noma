from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.cookies import SimpleCookie
import json, os, hmac, hashlib, time, html
from core.neural_core import NeuralCore
from core.planner import TaskPlanner
from core.benchmark import run_benchmarks
from core.evaluation import OutcomeEvaluator
BASE=Path(__file__).resolve().parent
HTML=BASE/'dashboard'/'index.html'
DATA_DIR=Path(os.environ.get('RAFAEL_DATA_DIR', str(BASE/'data'))).resolve()
ACCESS_CODE=os.environ.get('RAFAEL_ACCESS_CODE','').strip()
SESSION_SECRET=os.environ.get('RAFAEL_SESSION_SECRET','').strip()
COOKIE_SECURE=os.environ.get('RAFAEL_COOKIE_SECURE','1').strip() != '0'
SESSION_SECONDS=12*60*60
if __name__ == '__main__' and (not ACCESS_CODE.isdigit() or len(ACCESS_CODE)<8):
    raise SystemExit('Configure RAFAEL_ACCESS_CODE com pelo menos 8 dígitos numéricos.')
if __name__ == '__main__' and len(SESSION_SECRET)<32:
    raise SystemExit('Configure RAFAEL_SESSION_SECRET com uma chave aleatória de pelo menos 32 caracteres.')
core=NeuralCore(nodes=240,seed=7,data_dir=DATA_DIR); planner=TaskPlanner(); evaluator=OutcomeEvaluator(core.memory)
LOGIN_HTML = """<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Acesso RAFAEL</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#07111f;color:#edf5ff;font:16px system-ui}.card{width:min(90vw,390px);box-sizing:border-box;padding:28px;border:1px solid #29415f;border-radius:22px;background:#0e1c2e;box-shadow:0 20px 70px #0006}h1{letter-spacing:.12em}p{color:#a9bbd2;line-height:1.5}input,button{box-sizing:border-box;width:100%;padding:14px;border-radius:10px;font:inherit}input{background:#07111f;color:white;border:1px solid #36506f;letter-spacing:.2em}button{margin-top:12px;background:#70e1c2;color:#07111f;border:0;font-weight:700;cursor:pointer}.err{color:#ffb3b3;min-height:1.4em}</style><main class="card"><h1>RAFAEL</h1><p>Núcleo digital · Acesso privado</p><form method="post" action="/login"><label for="pin">Código numérico de acesso</label><p><input id="pin" name="pin" inputmode="numeric" pattern="[0-9]{8,}" minlength="8" maxlength="64" type="password" autocomplete="current-password" required></p><button>Entrar no RAFAEL</button></form><p class="err">{{ERROR}}</p><p>Use somente o endereço privado fornecido após a implantação.</p></main></html>"""
class Handler(BaseHTTPRequestHandler):
    def _session_token(self, expiry):
        payload=str(expiry)
        signature=hmac.new(SESSION_SECRET.encode(),payload.encode(),hashlib.sha256).hexdigest()
        return payload+'.'+signature
    def _valid_session(self):
        cookie=SimpleCookie()
        try: cookie.load(self.headers.get('Cookie',''))
        except Exception: return False
        morsel=cookie.get('rafael_session')
        if not morsel: return False
        try:
            expiry_text,signature=morsel.value.split('.',1)
            expiry=int(expiry_text)
            if expiry < int(time.time()) or expiry > int(time.time())+SESSION_SECONDS+60: return False
            expected=hmac.new(SESSION_SECRET.encode(),expiry_text.encode(),hashlib.sha256).hexdigest()
            return hmac.compare_digest(signature,expected)
        except (ValueError,TypeError): return False
    def _login_page(self, error=''):
        self.send_data(200,LOGIN_HTML.replace('{{ERROR}}',html.escape(error)),'text/html; charset=utf-8')
    def _require_auth(self,path):
        if path in ('/login','/healthz') or self._valid_session(): return True
        if path.startswith('/api/'):
            self.send_data(401,json.dumps({'erro':'Acesso não autorizado.'},ensure_ascii=False)); return False
        self.send_response(303); self.send_header('Location','/login'); self.send_header('Cache-Control','no-store'); self.end_headers(); return False
    def send_data(self,status,body,ctype='application/json; charset=utf-8'):
        data=body if isinstance(body,bytes) else body.encode('utf-8'); self.send_response(status); self.send_header('Content-Type',ctype); self.send_header('Content-Length',str(len(data))); self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.end_headers(); self.wfile.write(data)
    def body(self):
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size>10000: raise ValueError('Requisição muito grande.')
            obj=json.loads(self.rfile.read(size).decode('utf-8') or '{}')
            if not isinstance(obj,dict): raise ValueError('Envie um objeto JSON.')
            return obj
        except (ValueError,UnicodeDecodeError,json.JSONDecodeError) as e: raise ValueError('JSON inválido ou requisição grande demais.') from e
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/healthz': self.send_data(200,json.dumps({'status':'ok'})); return
        if path=='/login': self._login_page(); return
        if not self._require_auth(path): return
        if path in ('/','/index.html'): self.send_data(200,HTML.read_bytes(),'text/html; charset=utf-8')
        elif path=='/api/status': self.send_data(200,json.dumps(core.status(),ensure_ascii=False))
        elif path=='/api/tick': self.send_data(200,json.dumps(core.tick(),ensure_ascii=False))
        elif path=='/api/logs': self.send_data(200,json.dumps({'logs':list(core.logs)[-80:]},ensure_ascii=False))
        elif path=='/api/memories': self.send_data(200,json.dumps({'memories':core.memory.list_memories(50)},ensure_ascii=False))
        elif path=='/api/tasks': self.send_data(200,json.dumps({'tasks':core.memory.list_tasks(50)},ensure_ascii=False))
        elif path=='/api/plans': self.send_data(200,json.dumps({'plans':core.memory.list_plans(50)},ensure_ascii=False))
        elif path=='/api/benchmark': self.send_data(200,json.dumps(run_benchmarks(),ensure_ascii=False))
        elif path=='/api/evaluations': self.send_data(200,json.dumps({'evaluations':core.memory.list_evaluations(50)},ensure_ascii=False))
        elif path.startswith('/api/plans/') and path.endswith('/detail'):
            plan=core.memory.get_plan(path.split('/')[-2])
            if plan is None: self.send_data(404,json.dumps({'erro':'Plano não encontrado.'},ensure_ascii=False))
            else: self.send_data(200,json.dumps(plan,ensure_ascii=False))
        else:self.send_data(404,json.dumps({'erro':'Rota não encontrada'},ensure_ascii=False))
    def do_POST(self):
        path=urlparse(self.path).path
        if path=='/login':
            size=int(self.headers.get('Content-Length','0') or 0)
            if size>4096:
                self.send_data(413,'Requisição muito grande.','text/plain; charset=utf-8'); return
            raw=self.rfile.read(size).decode('utf-8','replace')
            pin=parse_qs(raw).get('pin',[''])[0]
            if not hmac.compare_digest(pin,ACCESS_CODE):
                time.sleep(1)
                self._login_page('Código inválido. Tente novamente.')
                return
            expiry=int(time.time())+SESSION_SECONDS
            token=self._session_token(expiry)
            self.send_response(303); self.send_header('Location','/')
            cookie=f'rafael_session={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={SESSION_SECONDS}'
            if COOKIE_SECURE: cookie+='; Secure'
            self.send_header('Set-Cookie',cookie); self.send_header('Cache-Control','no-store'); self.end_headers(); return
        if not self._require_auth(path): return
        try:
            b={}
            if path not in ('/api/start','/api/pause','/api/reset','/api/stimulus'): b=self.body()
            if path=='/api/start': core.running=True; core.log('Motor experimental iniciado pelo operador.'); result=core.status()
            elif path=='/api/pause': core.running=False; core.log('Motor pausado pelo operador.'); result=core.status()
            elif path=='/api/reset': core.reset(); result=core.status()
            elif path=='/api/stimulus': result=core.stimulate()
            elif path=='/api/memory/save': result=core.save_memory(b.get('label','Padrão experimental'))
            elif path=='/api/memory/recall': result=core.recall_memory(b.get('id'))
            elif path=='/api/learn': result=core.learn(b.get('reward',1.0))
            elif path=='/api/tasks': result=core.create_task(b.get('title',''),b.get('description',''))
            elif path=='/api/plan': result=core.memory.save_plan(planner.plan(b.get('objective',''),b.get('context','')))
            elif path=='/api/evaluations': result=evaluator.evaluate(b.get('objective',''),b.get('criterion',''),b.get('expected',''),b.get('observed',''),b.get('score',0),b.get('threshold',80),b.get('evidence',''))
            elif path.startswith('/api/plans/') and path.endswith('/detail'):
                result=core.memory.get_plan(path.split('/')[-2])
                if result is None: raise ValueError('Plano não encontrado.')
            elif path.startswith('/api/tasks/') and path.endswith('/status'):
                tid=path.split('/')[-2]; result=core.update_task(tid,b.get('status',''))
            else:self.send_data(404,json.dumps({'erro':'Rota não encontrada'},ensure_ascii=False)); return
            self.send_data(200,json.dumps(result,ensure_ascii=False))
        except (ValueError,TypeError,KeyError) as e:self.send_data(400,json.dumps({'erro':str(e) or 'Parâmetros inválidos.'},ensure_ascii=False))
    def log_message(self,fmt,*args): pass
if __name__=='__main__':
    host=os.environ.get('HOST','0.0.0.0'); port=int(os.environ.get('PORT','8000'))
    print(f'RAFAEL 0.6 | painel web ativo na porta {port}; armazenamento: {DATA_DIR}')
    try: ThreadingHTTPServer((host,port),Handler).serve_forever()
    except KeyboardInterrupt: print('\nServidor encerrado.')
