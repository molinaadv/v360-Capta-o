import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from supabase import create_client, Client

# =====================================================
# APP DE CAPTAÇÃO - MOLINA ADVOGADOS / BOA VISTA
# Streamlit + Supabase
# =====================================================

st.set_page_config(
    page_title="Captação Molina - Boa Vista",
    page_icon="📍",
    layout="wide"
)

TABELA_USUARIOS = "captacao_usuarios"
TABELA_LEADS = "captacao_leads"

# -------------------------------
# CONEXÃO SUPABASE
# -------------------------------
@st.cache_resource
def conectar_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        st.error("Configure SUPABASE_URL e SUPABASE_ANON_KEY no secrets do Streamlit.")
        st.stop()
    return create_client(url, key)

supabase = conectar_supabase()

# -------------------------------
# LISTAS PADRÃO
# -------------------------------
BAIRROS_BOA_VISTA = [
    "13 de Setembro", "Aeroporto", "Alvorada", "Asa Branca", "Bela Vista",
    "Buritis", "Caimbé", "Calungá", "Canarinho", "Caranã", "Cauamé",
    "Centenário", "Centro", "Cidade Satélite", "Cinturão Verde", "Dos Estados",
    "Dr. Airton Rocha", "Equatorial", "Jardim Caranã", "Jardim Floresta",
    "Jóquei Clube", "Laura Moreira", "Liberdade", "Mecejana", "Nova Canaã",
    "Nova Cidade", "Operário", "Paraviana", "Pintolândia", "Pricumã",
    "Professora Araceli Souto Maior", "Raiar do Sol", "Santa Luzia", "Santa Tereza",
    "São Bento", "São Francisco", "São Pedro", "Senador Hélio Campos",
    "Tancredo Neves", "União", "Outro"
]

AREAS_ACAO = [
    "Previdenciário", "Trabalhista", "Cível", "Família", "Outro"
]

TIPOS_BENEFICIO = [
    "LOAS Idoso",
    "LOAS Deficiente",
    "Auxílio-doença / Incapacidade temporária",
    "Aposentadoria por idade urbana",
    "Aposentadoria rural",
    "Salário-maternidade",
    "Pensão por morte",
    "Auxílio-reclusão",
    "Revisão de benefício",
    "Outro"
]

STATUS_LEAD = ["Novo", "Em atendimento", "Convertido", "Perdido"]
MOTIVOS_PERDA = [
    "", "Não possui direito", "Cliente desistiu", "Já possui advogado",
    "Não apresentou documentos", "Sem contato", "Benefício negado anteriormente",
    "Valor de honorários", "Outro"
]

# -------------------------------
# FUNÇÕES AUXILIARES
# -------------------------------
def normalizar_texto(valor: str) -> str:
    if not valor:
        return ""
    return " ".join(valor.strip().split()).title()


def limpar_cpf(valor: str) -> str:
    if not valor:
        return ""
    return "".join(ch for ch in valor if ch.isdigit())


def buscar_usuario(email: str, senha: str):
    try:
        resp = (
            supabase.table(TABELA_USUARIOS)
            .select("id,nome,email,perfil,ativo")
            .eq("email", email.strip().lower())
            .eq("senha", senha)
            .eq("ativo", True)
            .limit(1)
            .execute()
        )
        return resp.data[0] if resp.data else None
    except Exception as e:
        st.error(f"Erro ao buscar usuário: {e}")
        return None


def listar_usuarios_ativos():
    try:
        resp = (
            supabase.table(TABELA_USUARIOS)
            .select("id,nome,email,perfil,ativo")
            .eq("ativo", True)
            .order("nome")
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


def carregar_leads():
    try:
        resp = (
            supabase.table(TABELA_LEADS)
            .select("*")
            .order("data_captacao", desc=True)
            .execute()
        )
        df = pd.DataFrame(resp.data or [])
        if not df.empty:
            df["data_captacao"] = pd.to_datetime(df["data_captacao"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar leads: {e}")
        return pd.DataFrame()


def salvar_lead(dados: dict):
    return supabase.table(TABELA_LEADS).insert(dados).execute()


def atualizar_lead(lead_id: str, dados: dict):
    return supabase.table(TABELA_LEADS).update(dados).eq("id", lead_id).execute()


def pode_ver_todos(usuario: dict) -> bool:
    return usuario.get("perfil") in ["gestor", "supervisor"]

# -------------------------------
# LOGIN
# -------------------------------
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("📍 Captação Molina - Boa Vista")
    st.subheader("Acesso")

    with st.form("form_login"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

    if entrar:
        usuario = buscar_usuario(email, senha)
        if usuario:
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos, ou usuário inativo.")

    st.info("Usuário inicial de teste: gestor@molina.com / 123456 ou captador@molina.com / 123456")
    st.stop()

usuario = st.session_state.usuario

# -------------------------------
# MENU LATERAL
# -------------------------------
st.sidebar.title("📍 Captação")
st.sidebar.write(f"**Usuário:** {usuario['nome']}")
st.sidebar.write(f"**Perfil:** {usuario['perfil'].title()}")

opcoes = ["Novo Lead", "Minhas Captações"]
if pode_ver_todos(usuario):
    opcoes += ["Painel Gestor", "Atualizar Lead", "Usuários"]

pagina = st.sidebar.radio("Menu", opcoes)

if st.sidebar.button("Sair"):
    st.session_state.usuario = None
    st.rerun()

# -------------------------------
# NOVO LEAD
# -------------------------------
if pagina == "Novo Lead":
    st.title("➕ Novo Lead")
    st.caption("O captador é preenchido automaticamente pelo usuário logado.")

    with st.form("form_novo_lead", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome_cliente = st.text_input("Nome do cliente *")
            cpf = st.text_input("CPF")
            telefone = st.text_input("Telefone *")
            bairro = st.selectbox("Bairro *", BAIRROS_BOA_VISTA)
        with col2:
            local_captacao = st.text_input("Local da captação *", placeholder="Ex.: Feira, praça, INSS, ação social...")
            area_acao = st.selectbox("Área da ação *", AREAS_ACAO)
            tipo_beneficio = st.selectbox("Tipo de benefício *", TIPOS_BENEFICIO)
            observacao = st.text_area("Observação", placeholder="Informações úteis para o atendimento posterior")

        enviar = st.form_submit_button("Salvar Lead")

    if enviar:
        if not nome_cliente or not telefone or not bairro or not local_captacao:
            st.error("Preencha os campos obrigatórios marcados com *.")
        else:
            dados = {
                "captador_id": usuario["id"],
                "captador_nome": usuario["nome"],
                "unidade": "Boa Vista",
                "nome_cliente": normalizar_texto(nome_cliente),
                "cpf": limpar_cpf(cpf),
                "telefone": telefone.strip(),
                "bairro": bairro,
                "local_captacao": normalizar_texto(local_captacao),
                "area_acao": area_acao,
                "tipo_beneficio": tipo_beneficio,
                "observacao": observacao.strip(),
                "status_lead": "Novo"
            }
            try:
                salvar_lead(dados)
                st.success("Lead salvo com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar lead: {e}")

# -------------------------------
# MINHAS CAPTAÇÕES
# -------------------------------
elif pagina == "Minhas Captações":
    st.title("📋 Minhas Captações")
    df = carregar_leads()

    if df.empty:
        st.info("Nenhuma captação encontrada.")
    else:
        if not pode_ver_todos(usuario):
            df = df[df["captador_id"].astype(str) == str(usuario["id"])]

        col1, col2 = st.columns(2)
        with col1:
            status_filtro = st.multiselect("Status", STATUS_LEAD, default=STATUS_LEAD)
        with col2:
            bairro_filtro = st.multiselect("Bairro", sorted(df["bairro"].dropna().unique().tolist()))

        if status_filtro:
            df = df[df["status_lead"].isin(status_filtro)]
        if bairro_filtro:
            df = df[df["bairro"].isin(bairro_filtro)]

        colunas = [
            "data_captacao", "nome_cliente", "telefone", "bairro", "local_captacao",
            "area_acao", "tipo_beneficio", "status_lead", "captador_nome", "observacao",
            "quem_atendeu", "motivo_perda"
        ]
        colunas = [c for c in colunas if c in df.columns]
        st.dataframe(df[colunas], use_container_width=True, hide_index=True)

        csv = df[colunas].to_csv(index=False).encode("utf-8-sig")
        st.download_button("Baixar CSV", csv, "captacoes.csv", "text/csv")

# -------------------------------
# PAINEL GESTOR
# -------------------------------
elif pagina == "Painel Gestor":
    st.title("📊 Painel Gestor - Boa Vista")
    df = carregar_leads()

    if df.empty:
        st.info("Nenhum dado encontrado.")
        st.stop()

    hoje = date.today()
    colf1, colf2, colf3 = st.columns(3)
    with colf1:
        data_ini = st.date_input("Data inicial", hoje - timedelta(days=30))
    with colf2:
        data_fim = st.date_input("Data final", hoje)
    with colf3:
        status_filtro = st.multiselect("Status", STATUS_LEAD, default=STATUS_LEAD)

    df = df[(df["data_captacao"].dt.date >= data_ini) & (df["data_captacao"].dt.date <= data_fim)]
    if status_filtro:
        df = df[df["status_lead"].isin(status_filtro)]

    total = len(df)
    novos = int((df["status_lead"] == "Novo").sum())
    atendimento = int((df["status_lead"] == "Em atendimento").sum())
    convertidos = int((df["status_lead"] == "Convertido").sum())
    perdidos = int((df["status_lead"] == "Perdido").sum())
    conversao = (convertidos / total * 100) if total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Captado", total)
    c2.metric("Novos", novos)
    c3.metric("Em Atendimento", atendimento)
    c4.metric("Convertidos", convertidos)
    c5.metric("Conversão", f"{conversao:.1f}%")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Funil por Status")
        status_df = df["status_lead"].value_counts().reset_index()
        status_df.columns = ["Status", "Quantidade"]
        fig = px.bar(status_df, x="Status", y="Quantidade", text="Quantidade")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Captações por Benefício")
        beneficio_df = df["tipo_beneficio"].value_counts().reset_index().head(10)
        beneficio_df.columns = ["Benefício", "Quantidade"]
        fig = px.bar(beneficio_df, x="Quantidade", y="Benefício", orientation="h", text="Quantidade")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Ranking por Captador")
        ranking = df.groupby("captador_nome").agg(
            leads=("id", "count"),
            convertidos=("status_lead", lambda s: (s == "Convertido").sum()),
            perdidos=("status_lead", lambda s: (s == "Perdido").sum())
        ).reset_index()
        ranking["conversao_%"] = (ranking["convertidos"] / ranking["leads"] * 100).round(1)
        ranking = ranking.sort_values(["convertidos", "leads"], ascending=False)
        st.dataframe(ranking, use_container_width=True, hide_index=True)

    with col4:
        st.subheader("Ranking por Bairro")
        bairros = df.groupby("bairro").agg(
            leads=("id", "count"),
            convertidos=("status_lead", lambda s: (s == "Convertido").sum()),
            perdidos=("status_lead", lambda s: (s == "Perdido").sum())
        ).reset_index()
        bairros["conversao_%"] = (bairros["convertidos"] / bairros["leads"] * 100).round(1)
        bairros = bairros.sort_values("leads", ascending=False)
        st.dataframe(bairros, use_container_width=True, hide_index=True)

    st.subheader("Motivos de Perda")
    perdas = df[df["status_lead"] == "Perdido"]
    if perdas.empty:
        st.info("Nenhum lead perdido no período selecionado.")
    else:
        perdas_df = perdas["motivo_perda"].fillna("Não informado").replace("", "Não informado").value_counts().reset_index()
        perdas_df.columns = ["Motivo", "Quantidade"]
        fig = px.bar(perdas_df, x="Motivo", y="Quantidade", text="Quantidade")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Base Completa")
    st.dataframe(df, use_container_width=True, hide_index=True)

# -------------------------------
# ATUALIZAR LEAD
# -------------------------------
elif pagina == "Atualizar Lead":
    st.title("✏️ Atualizar Lead")
    df = carregar_leads()

    if df.empty:
        st.info("Nenhum lead encontrado.")
        st.stop()

    df["label"] = df["nome_cliente"].fillna("") + " | " + df["telefone"].fillna("") + " | " + df["bairro"].fillna("") + " | " + df["status_lead"].fillna("")
    lead_label = st.selectbox("Selecione o lead", df["label"].tolist())
    lead = df[df["label"] == lead_label].iloc[0]

    with st.form("form_atualizar_lead"):
        status_atual = lead.get("status_lead", "Novo")
        status_idx = STATUS_LEAD.index(status_atual) if status_atual in STATUS_LEAD else 0
        status = st.selectbox("Status do Lead", STATUS_LEAD, index=status_idx)

        usuarios = listar_usuarios_ativos()
        nomes_usuarios = [u["nome"] for u in usuarios]
        quem_atendeu_atual = lead.get("quem_atendeu") or ""
        lista_atendentes = [""] + nomes_usuarios
        idx_atendente = lista_atendentes.index(quem_atendeu_atual) if quem_atendeu_atual in lista_atendentes else 0
        quem_atendeu = st.selectbox("Quem atendeu depois", lista_atendentes, index=idx_atendente)

        motivo_atual = lead.get("motivo_perda") or ""
        idx_motivo = MOTIVOS_PERDA.index(motivo_atual) if motivo_atual in MOTIVOS_PERDA else 0
        motivo_perda = st.selectbox("Motivo da perda", MOTIVOS_PERDA, index=idx_motivo)

        observacao = st.text_area("Observação", value=lead.get("observacao") or "")

        salvar = st.form_submit_button("Salvar Atualização")

    if salvar:
        if status == "Perdido" and not motivo_perda:
            st.error("Informe o motivo da perda quando o status for Perdido.")
        else:
            dados = {
                "status_lead": status,
                "quem_atendeu": quem_atendeu or None,
                "motivo_perda": motivo_perda if status == "Perdido" else None,
                "observacao": observacao.strip()
            }
            try:
                atualizar_lead(str(lead["id"]), dados)
                st.success("Lead atualizado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao atualizar lead: {e}")

# -------------------------------
# USUÁRIOS
# -------------------------------
elif pagina == "Usuários":
    st.title("👥 Usuários")
    st.caption("Cadastre captadores, supervisores e gestores. O captador do lead será automático pelo login.")

    with st.form("form_usuario"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
        with col2:
            senha = st.text_input("Senha", type="password")
            perfil = st.selectbox("Perfil", ["captador", "supervisor", "gestor"])
        criar = st.form_submit_button("Criar Usuário")

    if criar:
        if not nome or not email or not senha:
            st.error("Preencha nome, e-mail e senha.")
        else:
            try:
                supabase.table(TABELA_USUARIOS).insert({
                    "nome": normalizar_texto(nome),
                    "email": email.strip().lower(),
                    "senha": senha,
                    "perfil": perfil,
                    "ativo": True
                }).execute()
                st.success("Usuário criado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao criar usuário: {e}")

    usuarios = listar_usuarios_ativos()
    st.subheader("Usuários ativos")
    st.dataframe(pd.DataFrame(usuarios), use_container_width=True, hide_index=True)
