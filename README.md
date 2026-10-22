# Testeia — base para plugin de IA

Núcleo funcional em Python, independente da plataforma. Inclui CLI, contrato de provedor substituível, demonstração offline, adaptador HTTP, testes e CI. Ainda não é uma extensão instalável de navegador, WordPress, editor ou ChatGPT: a plataforma não foi definida.

## Estado inspecionado em 22/10/2026

O repositório público foi criado em 13/10/2026 com descrição “testando plugin ia”. A API informou repositório vazio, sem branches, issues abertas ou PRs abertos. Não havia código, README, licença ou AGENTS.md para preservar ou orientar a implementação. Esta estrutura é o ponto de partida, sem remoções.

## Usar agora, sem chave e sem instalação

Requer Python 3.11 ou superior. Na pasta do projeto:

```bash
python -m testeia "Olá, teste do plugin"
python -m unittest discover -s tests -v
```

O modo padrão `demo` responde com um eco identificado como demonstração. Ele não usa IA nem acessa a rede. Em alguns sistemas, use `python3` em vez de `python`.

Instalação opcional em ambiente virtual:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell (em vez da linha acima):
# .venv\Scripts\Activate.ps1
python -m pip install -e .
testeia "Olá"
```

## Conectar um provedor real

O adaptador `remote` exige um endpoint HTTPS fornecido por você que aceite POST JSON com `model` e `messages`, autenticação `Authorization: Bearer`, e retorne texto em `choices[0].message.content`. Nem toda API usa esse contrato; confirme a compatibilidade na documentação do provedor escolhido. Não há provedor ou modelo contratado por padrão.

Linux/macOS:

```bash
export TESTEIA_ENDPOINT="https://SEU-HOST/CAMINHO-COMPLETO"
export TESTEIA_MODEL="SEU-MODELO"
read -rs -p "Chave: " TESTEIA_API_KEY; echo
export TESTEIA_API_KEY
python -m testeia --provider remote "Explique o objetivo deste projeto"
unset TESTEIA_API_KEY
```

PowerShell:

```powershell
$env:TESTEIA_ENDPOINT = "https://SEU-HOST/CAMINHO-COMPLETO"
$env:TESTEIA_MODEL = "SEU-MODELO"
$secret = Read-Host "Chave" -AsSecureString
$env:TESTEIA_API_KEY = [System.Net.NetworkCredential]::new('', $secret).Password
python -m testeia --provider remote "Explique o objetivo deste projeto"
Remove-Item Env:TESTEIA_API_KEY
```

`.env.example` é apenas referência; não há carregamento automático de `.env`. A chave fica no ambiente do processo e não é impressa pelo programa. O prompt é enviado ao endpoint escolhido e pode gerar cobrança; o modo demo nunca faz isso. Não envie dados sensíveis durante os testes. O programa não persiste prompts nem respostas, mas as políticas do provedor se aplicam.

Limites atuais: 20.000 caracteres de entrada, timeout de 30 segundos, resposta de até 1 MiB, sem streaming ou retentativas automáticas. Redirecionamentos HTTP são recusados. Erros retornam código de saída 1 sem imprimir respostas de erro do provedor.

## Estrutura e extensão

- `testeia/plugin.py`: `AIPlugin.run(prompt)` e provedores.
- `testeia/__main__.py`: interface de terminal.
- `tests/test_plugin.py`: validação, contrato HTTP simulado e erros.
- `pyproject.toml`: pacote e comando `testeia`, sem dependências em execução.
- `.github/workflows/tests.yml`: testes em Python 3.11, 3.12 e 3.13.

Um novo provedor precisa implementar `generate(prompt: str) -> str` e pode ser passado a `AIPlugin`. Um futuro adaptador da plataforma deve chamar `AIPlugin.run`, mantendo as credenciais no backend quando houver cliente público.

## Validação e próximo passo

Os testes usam HTTP simulado: não validam credenciais, disponibilidade ou qualidade de nenhum modelo real. A integração real deve ser validada depois de escolher e configurar o provedor. A CI executa testes e uma chamada demo a cada push/PR.

**Próximo passo recomendado:** definir onde o plugin será usado e uma primeira tarefa concreta, por exemplo, resumir um texto selecionado no navegador. Depois implementar o adaptador dessa plataforma e testar uma chamada real com o provedor escolhido.

### Decisões que dependem de você

1. **Plataforma e tarefa inicial:** navegador, WordPress, editor, outro sistema? Esta base evita assumir uma plataforma.
2. **Provedor, modelo e orçamento:** serviço pago ou solução própria; a chave real deve ser configurada fora do Git.
3. **Distribuição e licença:** nenhuma licença foi atribuída sem sua escolha; repositório público não equivale a autorização geral de uso.

Autenticação multiusuário, armazenamento, interface visual e publicação ficam para depois dessas decisões. Não há servidor exposto nem implantação automática nesta versão.
