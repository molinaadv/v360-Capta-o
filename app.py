import base64
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client, Client

# =====================================================
# V360 CAPTAÇÃO - MOLINA ADVOGADOS / BOA VISTA
# Streamlit + Supabase
# =====================================================

st.set_page_config(
    page_title="V360 Captação",
    page_icon="📍",
    layout="wide"
)

TABELA_USUARIOS = "captacao_usuarios"
TABELA_LEADS = "captacao_leads"
LOGO_FILE = "Logo_Molina_1_Traco_negativomenor.png"

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

AREAS_ACAO = ["Previdenciário", "Trabalhista", "Cível", "Família", "Outro"]

TIPOS_BENEFICIO = [
    "LOAS Idoso", "LOAS Deficiente", "Auxílio-doença / Incapacidade temporária",
    "Aposentadoria por idade urbana", "Aposentadoria rural", "Salário-maternidade",
    "Pensão por morte", "Auxílio-reclusão", "Revisão de benefício", "Outro"
]

STATUS_LEAD = ["Novo", "Em atendimento", "Convertido", "Perdido"]
MOTIVOS_PERDA = [
    "", "Não possui direito", "Cliente desistiu", "Já possui advogado",
    "Não apresentou documentos", "Sem contato", "Benefício negado anteriormente",
    "Valor de honorários", "Outro"
]

# -------------------------------
# VISUAL / MARCA
# -------------------------------
def get_logo_base64() -> str:
    caminho = Path(LOGO_FILE)
    if not caminho.exists():
        caminho = Path(__file__).parent / LOGO_FILE
    if caminho.exists():
        return base64.b64encode(caminho.read_bytes()).decode("utf-8")
    return ""


def aplicar_css_base():
    st.markdown(
        """
        <style>
        :root {
            --v360-navy: #061A33;
            --v360-navy-2: #09294D;
            --v360-cyan: #18BDF2;
            --v360-blue: #0077C8;
            --v360-text: #1E2A3A;
            --v360-soft: #F4F8FC;
        }
        .block-container { padding-top: 1rem; }
        h1, h2, h3 { color: var(--v360-text); }
        .stButton > button {
            border-radius: 12px;
            border: 1px solid #D8E2ED;
            font-weight: 700;
        }
        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #E0E8F0;
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 8px 24px rgba(6,26,51,0.06);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def aplicar_css_mobile():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display: none; }
        .block-container {
            max-width: 460px;
            padding: 0 !important;
            background: #F4F8FC;
        }
        .main .block-container { margin: 0 auto; }
        .mobile-header {
            background: linear-gradient(145deg, #061A33 0%, #09294D 65%, #064A80 100%);
            color: white;
            padding: 26px 24px 60px 24px;
            border-bottom: 5px solid #18BDF2;
            border-radius: 0 0 28px 28px;
            box-shadow: 0 12px 28px rgba(6,26,51,.22);
        }
        .brand-line { display:flex; align-items:center; justify-content:space-between; gap:14px; }
        .v360-title { font-size: 32px; font-weight: 900; letter-spacing: -1px; line-height:1; }
        .v360-sub { color:#18BDF2; font-size:17px; font-weight:800; letter-spacing:4px; margin-top:6px; }
        .molina-logo { max-width: 142px; height:auto; }
        .mobile-card {
            margin: -38px 16px 18px 16px;
            padding: 20px 18px 18px 18px;
            background: white;
            border-radius: 22px;
            border: 1px solid #E0E8F0;
            box-shadow: 0 16px 36px rgba(6,26,51,.14);
        }
        .card-title { display:flex; align-items:center; gap:12px; margin-bottom:4px; }
        .pin-circle {
            background: linear-gradient(145deg, #0077C8, #18BDF2);
            color:white; width:48px; height:48px; border-radius:50%;
            display:flex; align-items:center; justify-content:center; font-size:24px;
        }
        .card-title h2 { margin:0; font-size:28px; color:#1E2A3A; }
        .card-sub { color:#65748A; margin:0 0 16px 60px; }
        label, .stTextInput label, .stTextArea label, .stSelectbox label { font-weight: 700 !important; color:#34435A !important; }
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 12px !important;
            min-height: 48px;
        }
        .stButton > button {
            width: 100%;
            height: 54px;
            border-radius: 14px;
            border: none;
            background: linear-gradient(90deg, #18BDF2, #0077C8);
            color: white;
            font-size: 18px;
            font-weight: 900;
            box-shadow: 0 10px 22px rgba(0,119,200,.25);
        }
        .stButton > button:hover { color:white; filter: brightness(1.02); }
        .mobile-note { text-align:center; color:#65748A; font-size:14px; padding-top:6px; }
        .mobile-tabs {
            display:grid; grid-template-columns:1fr 1fr; gap:8px;
            background:white; border-top:1px solid #E0E8F0; padding:10px 14px 12px 14px;
            position: sticky; bottom:0; z-index:99;
        }
        .mobile-tab {
            text-align:center; color:#34435A; font-weight:800; font-size:13px;
            padding:8px 4px; border-radius:12px;
        }
        .mobile-tab.active { color:#0077C8; background:#EAF7FE; }
        div[data-testid="stAlert"] { margin-left:16px; margin-right:16px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def header_mobile():
    logo64 = get_logo_base64()
    logo_html = f'<img class="molina-logo" src="data:image/png;base64,{logo64}" />' if logo64 else '<div style="font-weight:800">MOLINA<br><span style="font-size:12px;letter-spacing:3px">ADVOGADOS</span></div>'
    st.markdown(
        f"""
        <div class="mobile-header">
            <div class="brand-line">
                <div>
                    <div class="v360-title"><span style="color:#18BDF2">V</span>360</div>
                    <div class="v360-sub">CAPTAÇÃO</div>
                </div>
                {logo_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def abrir_card_mobile(titulo="Novo Lead", subtitulo="Preencha os dados do cliente"):
    st.markdown(
        f"""
        <div class="mobile-card">
            <div class="card-title"><div class="pin-circle">📍</div><h2>{titulo}</h2></div>
            <p class="card-sub">{subtitulo}</p>
        """,
        unsafe_allow_html=True,
    )


def fechar_card_mobile():
    st.markdown("</div>", unsafe_allow_html=True)


def mobile_bottom_nav(ativo="Novo Lead"):
    novo_class = "mobile-tab active" if ativo == "Novo Lead" else "mobile-tab"
    minhas_class = "mobile-tab active" if ativo == "Minhas Captações" else "mobile-tab"
    st.markdown(
        f"""
        <div class="mobile-tabs">
            <div class="{novo_class}">➕<br>Novo Lead</div>
            <div class="{minhas_class}">📋<br>Minhas Captações</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def header_desktop(usuario):
    logo64 = get_logo_base64()
    logo_html = f'<img src="data:image/png;base64,{logo64}" style="height:52px; object-fit:contain;" />' if logo64 else "<b>MOLINA ADVOGADOS</b>"
    st.markdown(
        f"""
        <div style="background:linear-gradient(90deg,#061A33,#09294D); padding:18px 24px; border-radius:18px; margin-bottom:22px; display:flex; align-items:center; justify-content:space-between; color:white;">
            <div>
                <div style="font-size:30px;font-weight:900;"><span style="color:#18BDF2">V</span>360 Captação</div>
                <div style="color:#B8D9EF;">Boa Vista • Usuário: {usuario['nome']}</div>
            </div>
            {logo_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

aplicar_css_base()

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
if "captador_pagina" not in st.session_state:
    st.session_state.captador_pagina = "Novo Lead"

if st.session_state.usuario is None:
    aplicar_css_mobile()
    header_mobile()
    abrir_card_mobile("Acesso", "Entre para registrar captações")
    with st.form("form_login"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("ENTRAR")
    fechar_card_mobile()

    if entrar:
        usuario = buscar_usuario(email, senha)
        if usuario:
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos, ou usuário inativo.")

    st.info("Teste: gestor@molina.com / 123456 ou captador@molina.com / 123456")
    st.stop()

usuario = st.session_state.usuario
perfil = usuario.get("perfil")

# -------------------------------
# ROTAS DO CAPTADOR - ESTILO CELULAR
# -------------------------------
if perfil == "captador":
    aplicar_css_mobile()
    header_mobile()

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("➕ Novo Lead"):
            st.session_state.captador_pagina = "Novo Lead"
            st.rerun()
    with col_nav2:
        if st.button("📋 Minhas"):
            st.session_state.captador_pagina = "Minhas Captações"
            st.rerun()

    if st.session_state.captador_pagina == "Novo Lead":
        abrir_card_mobile("Novo Lead", "Preencha os dados do cliente")
        with st.form("form_novo_lead_mobile", clear_on_submit=True):
            nome_cliente = st.text_input("Nome do cliente *", placeholder="Digite o nome completo")
            cpf = st.text_input("CPF", placeholder="000.000.000-00")
            telefone = st.text_input("Telefone *", placeholder="(95) 00000-0000")
            bairro = st.selectbox("Bairro *", BAIRROS_BOA_VISTA)
            local_captacao = st.text_input("Local da captação *", placeholder="Ex.: Feira, praça, INSS, ação social...")
            area_acao = st.selectbox("Área da ação *", AREAS_ACAO)
            tipo_beneficio = st.selectbox("Tipo de benefício *", TIPOS_BENEFICIO)
            observacao = st.text_area("Observação", placeholder="Informações úteis para o atendimento posterior")
            enviar = st.form_submit_button("💾 SALVAR LEAD")
            st.markdown("<div class='mobile-note'>🔒 Captador identificado automaticamente</div>", unsafe_allow_html=True)
        fechar_card_mobile()

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
                    "status_lead": "Novo",
                }
                try:
                    salvar_lead(dados)
                    st.success("Lead salvo com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar lead: {e}")

    else:
        abrir_card_mobile("Minhas Captações", "Últimos leads cadastrados")
        df = carregar_leads()
        if df.empty:
            st.info("Nenhuma captação encontrada.")
        else:
            df = df[df["captador_id"].astype(str) == str(usuario["id"])]
            status_filtro = st.multiselect("Status", STATUS_LEAD, default=STATUS_LEAD)
            if status_filtro:
                df = df[df["status_lead"].isin(status_filtro)]
            colunas = ["data_captacao", "nome_cliente", "telefone", "bairro", "tipo_beneficio", "status_lead"]
            colunas = [c for c in colunas if c in df.columns]
            st.dataframe(df[colunas], use_container_width=True, hide_index=True)
        fechar_card_mobile()

    if st.button("Sair"):
        st.session_state.usuario = None
        st.rerun()
    mobile_bottom_nav(st.session_state.captador_pagina)
    st.stop()

# -------------------------------
# MENU DESKTOP - GESTOR / SUPERVISOR
# -------------------------------
header_desktop(usuario)
st.sidebar.title("📍 V360 Captação")
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
# NOVO LEAD DESKTOP
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
                "status_lead": "Novo",
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
