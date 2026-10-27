# 📊 Relatório de Análise e Assunção do Projeto

## 1. Identificação e Propósito do Projeto

* **Nome do Projeto:** Assistente de Investimentos com RPA e IA Generativa (*DIO Lab Base*).
* **Objetivo:** Construir um pipeline de automação inteligente de ponta a ponta:
  1. **RPA (Extração):** Coletar dados cadastrais e financeiros de clientes simulados via web scraping em Python.
  2. **Orquestração (N8N):** Receber os dados via Webhook, processar e cruzar os perfis dos clientes com uma base de produtos financeiros (`data.csv`).
  3. **Personalização (IA Generativa / Templates):** Gerar recomendações de investimentos individualizadas e humanizadas para cada cliente conforme perfil de risco e saldo disponível.

---

## 2. Inventário dos Arquivos Analisados

| Arquivo / Diretório | Tamanho | Função no Projeto | Status |
| :--- | :---: | :--- | :---: |
| [`README.md`](file:///t:/Google/n8n-assistente-investimentos/README.md) | ~7.6 KB | Documentação com arquitetura (Mermaid), especificações de MVP, etapas e referências. | Completo |
| [`docs/index.html`](file:///t:/Google/n8n-assistente-investimentos/docs/index.html) | ~2.7 KB | Página web simulada com tabela `#clientes` contendo 10 clientes fictícios. | Pronto |
| [`docs/data.csv`](file:///t:/Google/n8n-assistente-investimentos/docs/data.csv) | 371 B | Matriz de produtos de investimento por perfil, aplicação mínima e rentabilidade. | Pronto |
| [`rpa/extrair_clientes.ipynb`](file:///t:/Google/n8n-assistente-investimentos/rpa/extrair_clientes.ipynb) | ~6.7 KB | Jupyter Notebook para extração via `requests` + `BeautifulSoup`. | Pendente integração |

---

## 3. Diagnóstico Técnico Detalhado

### 3.1. Dados de Clientes ([`docs/index.html`](file:///t:/Google/n8n-assistente-investimentos/docs/index.html))
* Contém uma tabela HTML (`#clientes`) com classes semânticas (`.nome`, `.email`, `.saldo`, `.perfil`).
* Amostra de clientes: **10 registros**, cobrindo 3 perfis:
  * **Conservador:** Ana Silva (R$ 12.500,00), Daniel Oliveira (R$ 850,00), Gabriela Costa (R$ 1.500,00), Isabela Martins (R$ 500,00).
  * **Moderado:** Bruno Lima (R$ 3.200,00), Felipe Santos (R$ 7.800,00), Henrique Alves (R$ 22.300,00).
  * **Arrojado:** Carla Souza (R$ 28.900,00), Elena Rodrigues (R$ 45.000,00), João Pereira (R$ 15.000,00).

### 3.2. Catálogo de Investimentos ([`docs/data.csv`](file:///t:/Google/n8n-assistente-investimentos/docs/data.csv))
* Colunas: `perfil,produto,minimo,rentabilidade`.
* Produtos cadastrados:
  * **Conservador:** Poupança (mín. R$ 100, 6.2%), CDB Liquidez Diária (mín. R$ 1.000, 12.5%), Tesouro Selic (mín. R$ 500, 13.0%).
  * **Moderado:** CDB Prefixado (mín. R$ 1.000, 14.0%), Tesouro IPCA+ (mín. R$ 1.000, IPCA+6.0%), Fundo Multimercado (mín. R$ 5.000, 16.0%).
  * **Arrojado:** Criptomoedas (mín. R$ 100, Variável), Ações ETF (mín. R$ 500, Variável), Fundo de Ações (mín. R$ 10.000, Variável).

### 3.3. Script RPA ([`rpa/extrair_clientes.ipynb`](file:///t:/Google/n8n-assistente-investimentos/rpa/extrair_clientes.ipynb))
* Faz requisição HTTP via `requests` e faz o parse da tabela com `BeautifulSoup`.
* **Gargalo/Ponto de Atenção:**
  1. O envio dos dados para o Webhook do N8N está atualmente comentado como `# TODO (N8N)`.
  2. O código está apenas em formato de Notebook Jupyter (`.ipynb`), o que dificulta automações autônomas via agendamento (cron, CLI ou background process).

---

## 4. Diagnóstico do Ambiente Local

* **Python:** `3.14.6` instalado e funcional.
* **Node.js & NPM:** `v24.19.0` e `11.17.0` instalados.
  * O CLI global `n8n` não está no PATH, mas pode ser executado localmente sem instalação global via `npx n8n` ou conectado a uma instância na nuvem / Docker.
* **Git:** Repositório ainda não inicializado localmente.

---

## 5. O Que Falta Implementar (Entregáveis do Projeto)

Conforme os critérios de entrega especificados no [`README.md`](file:///t:/Google/n8n-assistente-investimentos/README.md):

1. **Repositório e Estrutura:**
   - [ ] Inicializar o versionamento Git (`git init`).
   - [ ] Criar arquivo `.gitignore` (para `.env`, `__pycache__`, arquivos temporários).
   - [ ] Criar `.env.example` para URLs de webhook e credenciais de IA (OpenAI / Gemini / Anthropic).
2. **Script RPA Autônomo:**
   - [ ] Criar versão em script Python padrão (`rpa/extrair_clientes.py`), permitindo rodar via terminal ou agendamento, com suporte a variáveis de ambiente e argumentos de linha de comando.
   - [ ] Atualizar o notebook [`extrair_clientes.ipynb`](file:///t:/Google/n8n-assistente-investimentos/rpa/extrair_clientes.ipynb) para parametrizar a URL do webhook.
3. **Fluxo N8N (`n8n/workflow.json`):**
   - [ ] Criar a pasta `n8n/` e construir o workflow JSON exportável.
   - [ ] Configurar nós no N8N:
     - **Webhook Trigger (POST):** Recebe a lista de clientes.
     - **Data Fetch / Reading:** Obtenção das opções de investimento do `data.csv`.
     - **Code Node / Cruzamento:** Filtra e seleciona os produtos compatíveis com o perfil e com o saldo mínimo do cliente.
     - **Geração de Mensagens:**
       - **Modo MVP:** Templates de mensagem estruturados por perfil.
       - **Modo Desafio (IA Generativa):** Nó com LLM (OpenAI/Gemini/Ollama) para gerar recomendações personalizadas com tom consultivo e amigável.
     - **Resposta / Output:** Retorno de confirmação ou disparo das mensagens.

---

## 🚀 Próximo Passo Recomendado

Podemos iniciar a estruturação do projeto de imediato:
1. **Criar a versão executável em Python (`extrair_clientes.py`)** e o `.env.example`.
2. **Construir o arquivo `n8n/workflow.json`** completo (pronto para importar no N8N, já configurado para cruzar clientes, produtos e gerar as mensagens).
3. **Inicializar o Git** com `.gitignore` adequado.

Como deseja proceder para começarmos a implementação?
