# Cybercron Circuito Digital — Continuidade do RAFAEL

## Versão atual: 0.6

**Empresa:** Cybercron Circuito Digital  
**Sistema/cérebro digital:** RAFAEL

A empresa e o sistema são nomes diferentes e devem continuar distintos na interface, documentação e futuras versões.

## Recursos presentes
- Rede matemática simulada e visualização esférica.
- Memórias, eventos, tarefas e planos em SQLite.
- Ajuste experimental limitado de pesos.
- Planejador heurístico que salva planos como rascunhos para revisão.
- Benchmark funcional local.
- Interface simples de voz do navegador para comandos predefinidos.
- Avaliação persistente de resultados, com objetivo, critério, esperado/observado, pontuação, limite, evidência e status.
- Identidade atualizada no dashboard: Cybercron Circuito Digital é a empresa; RAFAEL é o cérebro/sistema.

## Executar
No Windows, extraia o ZIP, execute `run.bat` e abra `http://127.0.0.1:8000`. Execute `run_tests.bat` para rodar os testes.

## Verificações
A suíte atual tem 16 testes automatizados. Antes de anunciar novos resultados, executar novamente os testes no ambiente-alvo.

## Limites assumidos
A esfera é uma visualização de uma simulação finita, não bilhões de neurônios reais. O planejador é heurístico. As avaliações dependem das observações fornecidas pelo operador. Não há consciência demonstrada, inteligência geral, treinamento autônomo de modelo de linguagem, execução autônoma de planos ou acesso externo habilitado. Ações importantes continuam sob controle humano.

## Próximos marcos
1. Adicionar comparação entre execuções e relatório de regressão.
2. Criar testes de integração HTTP.
3. Investigar integração opcional com modelo de linguagem, mantendo o modo local funcional e sem chaves secretas embutidas.
4. Expandir voz conversacional e manter permissões explícitas.

## Continuidade
Não existe execução em segundo plano após o fim da conversa. Este arquivo registra o estado para retomada.
