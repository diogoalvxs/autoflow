# 🛠️ AutoView Enterprise
> **Sistema de Gestão de Oficinas & Transparência ao Cliente (MVP)**

O **AutoView** é uma solução de software desenhada para modernizar a relação entre oficinas mecânicas e os seus clientes, eliminando a desconfiança e reduzindo a carga administrativa através da transparência em tempo real.

---

## 💡 O Conceito
A reparação automóvel é, historicamente, uma "caixa negra" para o cliente. O carro entra, o cliente perde a visão sobre o processo e surgem as dúvidas: *"Será que já começaram?", "Será que a peça foi mesmo trocada?", "Porque é que está a demorar tanto?"*.

O **AutoView** resolve isto aplicando o conceito de **"Pizza Tracker"** à mecânica automóvel: um sistema onde cada etapa é visível, justificada e comprovada visualmente.

## 😟 O Problema a Resolver
1.  **Falta de Confiança:** O cliente desconfia de orçamentos e peças não visíveis.
2.  **Interrupções Constantes:** Os mecânicos e gestores perdem horas ao telefone a responder a *"O meu carro já está pronto?"*.
3.  **Desorganização Interna:** Em oficinas maiores, é difícil saber qual mecânico está sobrecarregado ou qual viatura está parada à espera de peças.

## 🚀 A Solução
Uma Aplicação Web Unificada (All-in-One) que serve três públicos distintos:

### 1. Para a Oficina (Gestão & Operação)
* **Gestão de Fluxo:** Um painel Kanban digital para acompanhar o estado de cada viatura.
* **Atribuição de Tarefas:** O gestor atribui carros a mecânicos específicos.
* **Prova Visual:** O mecânico carrega fotos da peça danificada e da reparação pronta diretamente na app.
* **Base de Dados de Contactos:** Registo rápido de clientes e telemóveis para contacto imediato.

### 2. Para o Cliente (Transparência)
* **Acesso Seguro:** Login anónimo via **Matrícula** + **Token Único** (sem necessidade de criar conta/email).
* **Barra de Progresso:** Visualização gráfica do estado (ex: "Em Análise", "A aguardar peças", "Pronto").
* **Evidência Fotográfica:** O cliente vê a foto do trabalho realizado.

---

## ⚙️ Arquitetura Técnica
O projeto foi desenhado como um Monólito Modular para facilitar o *deployment* e manutenção em pequenas e médias empresas.

* **Linguagem:** Python 3.9+
* **Frontend & Backend:** Streamlit (Framework reativo).
* **Base de Dados:** SQLite (Ficheiro local `.db`).
    * *Self-Healing:* O sistema recria a base de dados automaticamente se o ficheiro for corrompido ou apagado.
    * *Blob Storage:* As imagens são convertidas em binário e guardadas dentro da própria base de dados para facilitar backups.
* **Análise de Dados:** Pandas & Plotly (para Dashboards de gestão).

---

## 🔄 Como Funciona (User Journey)

### Passo 1: A Entrada (Receção)
O cliente chega com o carro. O Gestor regista os dados no sistema (Nome, Matrícula, Telemóvel, Avaria).
> 🤖 **O Sistema:** Cria uma ficha na base de dados e gera um **Token de Acesso (ex: `BMW999`)**. O Gestor entrega este token ao cliente.

### Passo 2: O Diagnóstico (Oficina)
O Mecânico acede à sua "Fila de Trabalho" no tablet/PC da oficina. Vê a tarefa atribuída a si.
> 🔧 **Ação:** O mecânico desmonta a peça, tira uma foto e atualiza o estado para *"A aguardar peças"*. Insere uma nota técnica.

### Passo 3: A Consulta (Cliente)
Em casa, o cliente acede ao site, insere a Matrícula e o Token.
> 📱 **Visão:** Vê uma barra de progresso nos 40% e lê a nota: *"Peça encomendada à origem"*. O cliente sente-se informado e não telefona para a oficina.

### Passo 4: Conclusão
O carro é reparado. O mecânico muda o estado para *"Pronto"* e carrega a foto final.
> ✅ **Resultado:** O cliente vê o estado "Pronto" (verde) e dirige-se à oficina para levantar a viatura.

---

## 🛠️ Instalação e Execução

### Pré-requisitos
* Anaconda ou Python instalado.

### Comandos Rápidos
```bash
# 1. Criar ambiente virtual
conda create -n autoview python=3.9
conda activate autoview

# 2. Instalar dependências
pip install streamlit pandas plotly

# 3. Executar a aplicação
streamlit run app.py
```


### 🔮 Roadmap Futuro (Ideias v2.0)
[ ] Integração com WhatsApp API para enviar o Token automaticamente.

[ ] Notificações Push quando o estado muda para "Pronto".

[ ] Histórico de reparações passadas por viatura.

[ ] Exportação de faturas em PDF.
