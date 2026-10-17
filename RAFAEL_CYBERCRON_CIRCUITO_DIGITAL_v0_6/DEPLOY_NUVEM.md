# RAFAEL 0.6 — preparação para nuvem

Esta versão mantém o núcleo experimental existente e acrescenta uma camada inicial de autenticação por PIN numérico e empacotamento Docker. Ainda NÃO está publicada na internet.

## Antes de publicar
1. Escolha um provedor de hospedagem que execute containers Docker.
2. Configure `RAFAEL_ACCESS_CODE` com um PIN numérico de 8+ dígitos e `RAFAEL_SESSION_SECRET` com uma chave aleatória de 32+ caracteres. Nunca coloque esses valores no repositório nem os envie em mensagens.
3. Configure um volume/disco persistente montado em `/var/lib/rafael` para que o banco SQLite sobreviva a reinicializações e novas implantações.
4. Ative HTTPS no provedor. Deixe `RAFAEL_COOKIE_SECURE=1`.
5. Configure a verificação de saúde em `/healthz`. O contêiner escuta em `0.0.0.0` na porta indicada pela variável `PORT`.
6. Após publicar, teste `/healthz`, abra a URL HTTPS no Chrome, digite o PIN e verifique o painel.

## O que foi acrescentado
- PIN exigido antes de servir o dashboard e as APIs.
- Cookie de sessão HttpOnly, SameSite=Strict, validade de 12 horas e assinatura HMAC.
- PIN e segredo fora do código-fonte, por variáveis de ambiente.
- Diretório de dados configurável para SQLite.
- Dockerfile para plataforma de nuvem compatível com containers.

## Limites antes de uso real
- Proteção inicial, ainda não auditada. Antes de ações críticas, adicionar limitação de tentativas persistente, MFA, recuperação de conta, logs de segurança e revisão de CSRF.
- Não exponha o serviço sem HTTPS e sem configurar os segredos.
- A nuvem não torna o sistema indestrutível. Volume persistente e backup são necessários.
- O núcleo atual é experimental: rede matemática finita, planejador heurístico e comandos explícitos. Não executa tarefas externas por conta própria nem demonstra consciência.

## Opção de implantação preparada
O arquivo `render.yaml` descreve um serviço web Docker com plano pago `starter`, disco persistente de 1 GB, HTTPS do provedor e verificação `/healthz`. É um modelo para revisão antes de criar o serviço; não significa que a publicação já aconteceu. O PIN deve ser configurado como segredo no painel do provedor. Consulte a documentação oficial: https://render.com/docs/web-services e https://render.com/docs/disks.
