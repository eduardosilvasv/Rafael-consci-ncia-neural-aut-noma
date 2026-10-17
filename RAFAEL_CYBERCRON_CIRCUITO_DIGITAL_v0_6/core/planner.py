"""Planejador transparente: transforma um objetivo em etapas verificáveis, sem executar ações externas."""
from datetime import datetime
import re

class TaskPlanner:
    def plan(self, objective, context=''):
        objective=' '.join(str(objective).split()).strip()[:500]
        context=' '.join(str(context).split()).strip()[:1000]
        if len(objective)<4: raise ValueError('Descreva um objetivo com pelo menos quatro caracteres.')
        normalized=objective.lower()
        # Sequência de engenharia conservadora; o sistema não inventa execução nem afirma conclusão.
        steps=[
          {'number':1,'title':'Definir o resultado esperado','action':'Escrever o resultado final em termos observáveis.','check':'Existe um critério claro de sucesso?','status':'pendente'},
          {'number':2,'title':'Identificar entradas e limites','action':'Listar dados, ferramentas autorizadas, prazo e restrições.','check':'As entradas e permissões estão disponíveis?','status':'pendente'},
          {'number':3,'title':'Dividir em entregas pequenas','action':'Separar o objetivo em tarefas independentes e ordenadas.','check':'Cada tarefa produz uma saída verificável?','status':'pendente'},
          {'number':4,'title':'Executar primeiro um teste seguro','action':'Validar a menor parte em ambiente local ou de teste.','check':'O teste passou sem efeitos não autorizados?','status':'pendente'},
          {'number':5,'title':'Verificar o resultado','action':'Comparar a saída com o critério definido na etapa 1.','check':'Há evidência reproduzível de sucesso?','status':'pendente'},
          {'number':6,'title':'Registrar e preparar a próxima iteração','action':'Guardar resultados, erros, decisões e próxima ação.','check':'Outra pessoa consegue entender o que foi feito?','status':'pendente'},
        ]
        if any(w in normalized for w in ('dashboard','painel','interface','site','aplicativo','app')):
            steps[2]['action']='Separar interface, lógica, dados e testes em entregas pequenas.'
            steps[3]['action']='Testar a interface localmente com dados fictícios antes de ligar integrações.'
        if any(w in normalized for w in ('dados','banco','relatório','relatorio','planilha','análise','analise')):
            steps[1]['action']='Identificar origem, formato, qualidade, sensibilidade e permissão de uso dos dados.'
            steps[4]['action']='Conferir amostras, totais e resultados com cálculos independentes.'
        if any(w in normalized for w in ('pagamento','pix','financeiro','contrato','comprar','vender','produção','producao')):
            steps.insert(3,{'number':4,'title':'Solicitar aprovação antes de ação crítica','action':'Confirmar valores, destinatário, impacto e autorização do proprietário.','check':'A aprovação explícita está registrada?','status':'bloqueada_ate_aprovacao'})
            for i,s in enumerate(steps,1): s['number']=i
        return {'objective':objective,'context':context,'created_at':datetime.now().isoformat(timespec='seconds'),'status':'rascunho_aguardando_aprovacao','steps':steps,'notice':'Plano proposto, não executado. Revise as etapas e aprove antes de qualquer trabalho real.'}
