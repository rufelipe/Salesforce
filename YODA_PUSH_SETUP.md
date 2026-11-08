# Alertas Push do YODA

Esta implementação prepara notificações Web Push para compromissos com data e horário. O lembrete é programado para cinco minutos antes do horário informado no campo **Prazo** + **Horário do compromisso** da tarefa.

## 1. Banco de dados

1. Crie um projeto no Supabase.
2. Abra **SQL Editor** e execute `supabase/yoda_push_schema.sql`.
3. Copie a URL do projeto e a chave **service_role**. A chave service_role fica somente nas variáveis de ambiente da Vercel; nunca a coloque no HTML.

## 2. Chaves VAPID

Gere um par de chaves VAPID compatível com Web Push. Com Node.js instalado, execute:

```bash
npx web-push generate-vapid-keys
```

Cadastre a chave pública em `VAPID_PUBLIC_KEY` e a chave privada em `VAPID_PRIVATE_KEY`. Não gere outro par depois que os navegadores começarem a se inscrever, pois a chave pública precisa continuar igual. Configure `VAPID_SUBJECT` com um endereço seu, por exemplo `mailto:seu-email@exemplo.com`.

## 3. Variáveis de ambiente na Vercel

Em **Project → Settings → Environment Variables**, configure:

- `SUPABASE_URL`: URL do projeto Supabase.
- `SUPABASE_SERVICE_ROLE_KEY`: chave service_role do Supabase.
- `VAPID_PUBLIC_KEY`: chave pública VAPID.
- `VAPID_PRIVATE_KEY`: chave privada VAPID.
- `VAPID_SUBJECT`: endereço `mailto:` para identificação VAPID.
- `CRON_SECRET`: segredo aleatório longo para proteger o endpoint de agendamento.
- `APP_ORIGIN` (opcional): `https://salesforceteste.vercel.app`.

Depois de salvar as variáveis, faça um novo deploy.

## 4. Agendador a cada minuto

O endpoint que procura lembretes vencidos é:

`https://salesforceteste.vercel.app/api/send_reminders`

Configure um agendador externo (por exemplo, cron-job.org) para chamar esse endereço **a cada minuto**, usando o método GET e o cabeçalho:

`Authorization: Bearer SEU_CRON_SECRET`

Não publique o segredo em repositórios ou no navegador. Se a conta Vercel tiver plano que permita Cron a cada minuto, também é possível configurar o Cron nativo da Vercel; no plano Hobby, a frequência pode ser limitada a uma execução diária, o que não serve para lembretes de cinco minutos.

## 5. Ativar no navegador

1. Abra o Salesforce publicado em HTTPS.
2. Clique em **Ativar alertas do YODA**.
3. Permita notificações quando o navegador perguntar.
4. Cadastre ou edite uma tarefa com data e horário da ligação futuros.
5. O backend grava o lembrete no Supabase. O agendador consulta os lembretes e envia a notificação Push.

O navegador precisa ter permitido notificações e não pode ter bloqueado o site nas configurações do sistema. O Push permite receber alertas com a página fechada, desde que o navegador/sistema operacional ainda aceite notificações.

## Limitações atuais

- Os lembretes são associados às tarefas da demonstração e usam o campo de data e o horário da ligação.
- A lista de tarefas principal continua usando o armazenamento de demonstração/localStorage; esta implementação persiste no Supabase os lembretes e as assinaturas Push, não transforma todo o CRM em um banco de dados.
- O envio depende da execução do agendador. Com frequência de um minuto, o alerta pode variar aproximadamente até um minuto em relação aos cinco minutos exatos.
- Antes de considerar produção, configure autenticação por usuário para que assinaturas e lembretes não sejam compartilhados entre usuários.
