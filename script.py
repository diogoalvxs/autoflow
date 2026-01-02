import streamlit as st
import sqlite3
import pandas as pd
import uuid
from datetime import datetime, timedelta

# --- Configuração da Página ---
st.set_page_config(page_title="AutoView - Oficina Enterprise", layout="wide", initial_sidebar_state="expanded")

# --- Constantes ---
DB_FILE = "oficina_mvp.db"
STATUS_OPTIONS = ["A aguardar", "Em Análise", "A aguardar peças", "Em Reparação", "Pronto", "Entregue"]
TEAM_MEMBERS = ["Carlos (Mecânico Chefe)", "André (Júnior)", "Susana (Eletricista)", "Miguel (Pneus)"]

STATUS_PROGRESS = {
    "A aguardar": 10, "Em Análise": 25, "A aguardar peças": 40, 
    "Em Reparação": 60, "Pronto": 90, "Entregue": 100
}

# --- Camada de Base de Dados ---

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # ADICIONADO: campo 'telemovel'
    c.execute('''
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nome TEXT,
            telemovel TEXT,
            matricula TEXT,
            modelo_carro TEXT,
            descricao_problema TEXT,
            status TEXT,
            orcamento REAL,
            notas_mecanico TEXT,
            data_entrada TEXT,
            data_previsao_saida TEXT,
            token_acesso TEXT,
            foto_evidencia BLOB,
            mechanic_assigned TEXT
        )
    ''')
    
    # --- INSERÇÃO DE DADOS DE TESTE (PT-PT) ---
    c.execute('SELECT count(*) FROM ordens_servico')
    if c.fetchone()[0] == 0:
        hoje = datetime.now()
        
        dados_reais = [
            # CASO 1: Complexo
            (
                "Transportes Rápidos Lda", "910000001", "22-XX-33", "Mercedes Sprinter", 
                "Luz do motor acesa e perda de potência em subidas.", 
                "Em Reparação", 1250.00, 
                "Turbo desmontado. Geometria presa. A proceder à limpeza e substituição das juntas.", 
                (hoje - timedelta(days=2)).strftime("%Y-%m-%d"), 
                (hoje + timedelta(days=2)).strftime("%Y-%m-%d"), 
                "MERC01", 
                None, "Carlos (Mecânico Chefe)"
            ),
            # CASO 2: Peças
            (
                "Ana Pereira", "960000002", "AA-00-BB", "BMW 320d", 
                "Vidro do pendura não sobe.", 
                "A aguardar peças", 180.50, 
                "Elevador do vidro queimado. Peça encomendada à origem (BMW Alemanha), chega em 3 dias.", 
                (hoje - timedelta(days=5)).strftime("%Y-%m-%d"), 
                "A definir",
                "BMW999", 
                None, "Susana (Eletricista)"
            ),
            # CASO 3: Rápido
            (
                "Pedro Costa", "930000003", "QQ-11-WW", "Fiat 500", 
                "Mudar óleo e filtros.", 
                "Pronto", 120.00, 
                "Serviço concluído. Pressão dos pneus verificada. Calços de travão ainda com 50% de vida. Viatura pronta a levantar.", 
                hoje.strftime("%Y-%m-%d"), 
                hoje.strftime("%Y-%m-%d"),
                "FIAT55", 
                None, "André (Júnior)"
            )
        ]
        
        # Atualizado query para incluir telemovel
        c.executemany('''
            INSERT INTO ordens_servico (
                cliente_nome, telemovel, matricula, modelo_carro, descricao_problema, status, orcamento, 
                notas_mecanico, data_entrada, data_previsao_saida, token_acesso, foto_evidencia, mechanic_assigned
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', dados_reais)
        
        conn.commit()
    
    conn.close()

def create_os(nome, telemovel, matricula, modelo, problema, mecanico):
    token = uuid.uuid4().hex[:6].upper()
    conn = get_connection()
    c = conn.cursor()
    # Inserção atualizada com telemovel
    c.execute('''
        INSERT INTO ordens_servico (cliente_nome, telemovel, matricula, modelo_carro, descricao_problema, status, orcamento, notas_mecanico, data_entrada, data_previsao_saida, token_acesso, foto_evidencia, mechanic_assigned)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?)
    ''', (nome, telemovel, matricula, modelo, problema, "A aguardar", 0.0, "A aguardar avaliação.", datetime.now().strftime("%Y-%m-%d"), "A definir", token, mecanico))
    conn.commit()
    conn.close()
    return token

def update_os(os_id, status, orcamento, notas, previsao, mecanico, foto_bytes=None):
    conn = get_connection()
    c = conn.cursor()
    query = '''UPDATE ordens_servico SET status=?, orcamento=?, notas_mecanico=?, data_previsao_saida=?, mechanic_assigned=?'''
    params = [status, orcamento, notas, previsao, mecanico]
    if foto_bytes:
        query += ''', foto_evidencia=? WHERE id=?'''
        params.extend([foto_bytes, os_id])
    else:
        query += ''' WHERE id=?'''
        params.append(os_id)
    c.execute(query, tuple(params))
    conn.commit()
    conn.close()

def get_data_as_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM ordens_servico", conn)
    conn.close()
    return df

def get_client_os(matricula, token):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM ordens_servico WHERE matricula = ? AND token_acesso = ?", (matricula, token))
    data = c.fetchone()
    conn.close()
    return data

# --- Inicialização ---
init_db()

# --- Interface & Navegação ---
st.sidebar.title("🛠️ MechFlow Enterprise")
st.sidebar.markdown("---")
perfil = st.sidebar.selectbox("Perfil de Utilizador:", ["Cliente (Público)", "Gestor / Proprietário", "Mecânico (Funcionário)"])

# =========================================================
# PERFIL: CLIENTE
# =========================================================
if perfil == "Cliente (Público)":
    st.header("Área do Cliente")
    st.markdown("Bem-vindo à área de transparência da MechFlow. Consulte o estado da sua viatura.")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        mat = c1.text_input("Matrícula")
        tok = c2.text_input("Token de Acesso")
        st.write("") 
        if c3.button("🔍 Pesquisar", use_container_width=True):
            if mat and tok:
                data = get_client_os(mat.strip(), tok.strip())
                if data:
                    st.success("Viatura Encontrada!")
                    st.divider()
                    
                    # Cabeçalho do Carro
                    h1, h2 = st.columns([3, 1])
                    h1.title(f"{data[4]}") # Modelo agora é indice 4 devido ao novo campo
                    h1.caption(f"Matrícula: {data[3]} | Entrada: {data[9]}")
                    
                    # Barra de Progresso
                    perc = STATUS_PROGRESS.get(data[6], 0)
                    st.progress(perc)
                    st.caption(f"Progresso Global: {perc}% ({data[6]})")
                    
                    st.divider()
                    
                    # Detalhes
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Orçamento Aprovado", f"{data[7]:.2f} €")
                    col_b.metric("Previsão de Entrega", data[10])
                    # Ajuste de índices: mechanic_assigned é o último (13)
                    col_c.metric("Mecânico Responsável", data[13].split("(")[0] if data[13] else "N/A")

                    st.subheader("📋 Relatório Técnico")
                    with st.chat_message("assistant"):
                        st.write(f"**Avaria Reportada:** {data[5]}")
                        st.write(f"**Última Atualização:** {data[8]}")
                    
                    # Foto é indice 12
                    if data[12]:
                        st.subheader("📸 Evidência Fotográfica")
                        st.image(data[12], caption="Foto da Reparação / Peça", use_container_width=True)
                        
                else:
                    st.error("Dados inválidos. Por favor, verifique a matrícula e o token.")
            else:
                st.warning("Por favor, preencha ambos os campos.")

# =========================================================
# PERFIL: GESTOR
# =========================================================
elif perfil == "Gestor / Proprietário":
    st.header("📊 Painel de Gestão")
    
    # --- ÁREA DE REGISTO (MOVIDA PARA CIMA) ---
    with st.container(border=True):
        st.subheader("➕ Registar Nova Entrada")
        with st.form("nova_entrada"):
            c1, c2, c3 = st.columns(3)
            nome = c1.text_input("Nome do Cliente")
            telemovel = c2.text_input("Telemóvel") # Novo Campo
            mat = c3.text_input("Matrícula")
            
            c4, c5 = st.columns(2)
            mod = c4.text_input("Modelo da Viatura")
            mec = c5.selectbox("Atribuir a", TEAM_MEMBERS)
            
            prob = st.text_area("Descrição da Avaria")
            
            if st.form_submit_button("🚀 Gerar Ficha e Token", use_container_width=True):
                if nome and mat and mod:
                    tk = create_os(nome, telemovel, mat, mod, prob, mec)
                    st.success(f"Ficha criada com sucesso!")
                    st.code(f"TOKEN DE ACESSO: {tk}", language="text")
                    st.info(f"Envie este token ao cliente {nome} ({telemovel}).")
                else:
                    st.error("Preencha os dados obrigatórios.")

    st.divider()

    # --- DASHBOARD ---
    df = get_data_as_df()
    total_rev = df['orcamento'].sum()
    pendentes = len(df[df['status'] != 'Entregue'])
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Faturação Estimada", f"{total_rev:.2f} €", delta="+12%")
    k2.metric("Viaturas em Oficina", pendentes, delta="-2")
    k3.metric("Equipa Ativa", f"{len(TEAM_MEMBERS)} Pessoas")

    tab_dash, tab_lista = st.tabs(["Dashboard Visual", "Lista Detalhada"])
    
    with tab_dash:
        g1, g2 = st.columns(2)
        with g1:
            st.write("**Carga de Trabalho (Viaturas por Mecânico)**")
            if not df.empty:
                st.bar_chart(df['mechanic_assigned'].value_counts())
        with g2:
            st.write("**Estado da Oficina**")
            if not df.empty:
                st.bar_chart(df['status'].value_counts(), color="#ffaa00")

    with tab_lista:
        if not df.empty:
            df_display = df.rename(columns={
                'cliente_nome': 'Cliente', 
                'telemovel': 'Telemóvel',
                'matricula': 'Matrícula', 
                'modelo_carro': 'Modelo',
                'status': 'Estado', 
                'orcamento': 'Orçamento', 
                'mechanic_assigned': 'Mecânico',
                'token_acesso': 'Token'
            })
            # Mostra o telemóvel na tabela
            st.dataframe(df_display[['id', 'Cliente', 'Telemóvel', 'Matrícula', 'Modelo', 'Estado', 'Mecânico', 'Orçamento', 'Token']], use_container_width=True)
        else:
            st.info("Sem dados para mostrar.")

# =========================================================
# PERFIL: MECÂNICO
# =========================================================
elif perfil == "Mecânico (Funcionário)":
    me = st.sidebar.selectbox("Identifique-se:", TEAM_MEMBERS)
    st.header(f"Olá, {me.split(' ')[0]} 👋")
    
    df = get_data_as_df()
    minhas_obras = df[(df['mechanic_assigned'] == me) & (df['status'] != 'Entregue')]
    
    if minhas_obras.empty:
        st.info("Não tem tarefas pendentes. Bom trabalho!")
    else:
        st.write(f"Tem **{len(minhas_obras)} viaturas** na sua fila.")
        for i, row in minhas_obras.iterrows():
            with st.expander(f"🚘 {row['modelo_carro']} ({row['matricula']}) - {row['status']}", expanded=True):
                st.info(f"Problema: {row['descricao_problema']}")
                st.caption(f"Cliente: {row['cliente_nome']} | Tel: {row['telemovel']}") # Mecânico vê o telefone caso precise ligar
                
                with st.form(f"update_{row['id']}"):
                    c1, c2 = st.columns(2)
                    n_stat = c1.selectbox("Novo Estado", STATUS_OPTIONS, index=STATUS_OPTIONS.index(row['status']))
                    n_orc = c2.number_input("Orçamento Atualizado (€)", value=row['orcamento'])
                    
                    data_prev_val = datetime.now()
                    if row['data_previsao_saida'] != "A definir":
                        try:
                            data_prev_val = datetime.strptime(row['data_previsao_saida'], "%Y-%m-%d")
                        except:
                            pass
                            
                    n_prev = c1.date_input("Previsão de Saída", value=data_prev_val)
                    n_nota = st.text_area("Notas Técnicas (Cliente vai ler)", value=row['notas_mecanico'])
                    foto = st.file_uploader("Carregar Foto", key=f"f_{row['id']}")
                    
                    if st.form_submit_button("Guardar Progresso"):
                        b_foto = foto.getvalue() if foto else None
                        update_os(row['id'], n_stat, n_orc, n_nota, n_prev, me, b_foto)
                        st.success("Atualizado com sucesso!")
                        st.rerun()