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
TABELA_HISTORICO = "captacao_lead_historico"
TABELA_BENEFICIOS = "captacao_beneficios"
TABELA_LOCAIS = "captacao_locais_captacao"
LOGO_FILE = "Logo_Molina_1_Traco_negativomenor.png"
VERSAO_APP = "executivo-v360-captação-v8-logo-sidebar"

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
    "13 de Setembro",
    "Aeroporto",
    "Alvorada",
    "Aparecida",
    "Aquilino Mota Duarte",
    "Araceli Souto Maior",
    "Asa Branca",
    "Bela Vista",
    "Buritis",
    "Caçari",
    "Caimbé",
    "Calungá",
    "Cambará",
    "Canarinho",
    "Caranã",
    "Cauamé",
    "Centenário",
    "Centro",
    "Cidade Satélite",
    "Cinturão Verde",
    "Cruviana",
    "Dr. Silvio Botelho",
    "Equatorial",
    "Estados",
    "Jardim Caranã",
    "Jardim Floresta",
    "Jardim Neves",
    "Jardim Olímpico",
    "Jardim Primavera",
    "Jardim Tropical",
    "Jóquei Clube",
    "Laura Moreira",
    "Liberdade",
    "Marechal Rondon",
    "Mecejana",
    "Murilo Teixeira",
    "Nova Canaã",
    "Nova Cidade",
    "Olímpico",
    "Operário",
    "Paraviana",
    "Pintolândia",
    "Piscicultura",
    "Prata",
    "Professora Said Salomão",
    "Raiar do Sol",
    "Santa Luzia",
    "Santa Tereza",
    "São Francisco",
    "São Vicente",
    "Senador Hélio Campos",
    "Sílvio Leite",
    "Tancredo Neves",
    "Trinta e Um de Março",
    "União",
    "Outro",
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
        [data-testid="stSidebar"] { display: none !important; }
        header[data-testid="stHeader"] { background: transparent; }
        .block-container {
            max-width: 460px;
            padding: 0 !important;
            background: #F4F8FC;
        }
        .main .block-container { margin: 0 auto; }
        .mobile-header {
            background: linear-gradient(145deg, #061A33 0%, #09294D 65%, #064A80 100%);
            color: white;
            padding: 14px 16px 12px 16px;
            border-bottom: 4px solid #18BDF2;
            border-radius: 0 0 18px 18px;
            box-shadow: 0 10px 22px rgba(6,26,51,.18);
            overflow: hidden;
            margin-bottom: 10px;
        }
        .brand-line {
            display:flex;
            flex-direction:row;
            align-items:center;
            justify-content:space-between;
            gap:12px;
            width:100%;
        }
        .v360-title { font-size: 28px; font-weight: 950; letter-spacing: -1px; line-height:1; white-space:nowrap; }
        .v360-sub { color:#18BDF2; font-size:12px; font-weight:900; letter-spacing:3px; margin-top:5px; white-space:nowrap; }
        .molina-logo-wrap { flex:1; display:flex; justify-content:flex-end; min-width:0; }
        .molina-logo { width: 100%; max-width: 175px; max-height: 54px; height:auto; object-fit:contain; display:block; }
        .mobile-user-line { color:#B8D9EF; font-size:12px; margin-top:8px; }
        .mobile-nav-box {
            margin: 10px 14px 8px 14px;
            padding: 8px;
            background: rgba(255,255,255,.92);
            border: 1px solid #DCE8F4;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(6,26,51,.08);
        }
        .mobile-nav-box div[role="radiogroup"] {
            display:grid !important;
            grid-template-columns: 1fr 1fr;
            gap:8px;
        }
        .mobile-nav-box div[role="radiogroup"] label {
            background:#F4F8FC !important;
            border:1px solid #DCE8F4 !important;
            border-radius:14px !important;
            padding:10px 8px !important;
            margin:0 !important;
            min-height:44px;
            display:flex !important;
            align-items:center !important;
            justify-content:center !important;
            text-align:center !important;
            font-weight:900 !important;
            color:#34435A !important;
            font-size:13px !important;
        }
        .mobile-nav-box div[role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(90deg, #18BDF2, #0077C8) !important;
            border-color:#18BDF2 !important;
            color:white !important;
            box-shadow: 0 8px 18px rgba(0,119,200,.20);
        }
        .mobile-nav-box div[role="radiogroup"] label:has(input:checked) * { color:white !important; }
        .mobile-nav-box div[role="radiogroup"] label > div:first-child { display:none !important; }
        .mobile-card {
            margin: 10px 14px 16px 14px;
            padding: 18px 16px 16px 16px;
            background: white;
            border-radius: 22px;
            border: 1px solid #E0E8F0;
            box-shadow: 0 12px 28px rgba(6,26,51,.10);
        }
        .card-title { display:flex; align-items:center; gap:12px; margin-bottom:4px; }
        .pin-circle {
            background: linear-gradient(145deg, #0077C8, #18BDF2);
            color:white; min-width:48px; width:48px; height:48px; border-radius:50%;
            display:flex; align-items:center; justify-content:center; font-size:24px;
        }
        .card-title h2 { margin:0; font-size:27px; color:#1E2A3A; }
        .card-sub { color:#65748A; margin:0 0 12px 60px; }
        label, .stTextInput label, .stTextArea label, .stSelectbox label { font-weight: 700 !important; color:#34435A !important; }
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 12px !important;
            min-height: 48px;
        }
        .mobile-card .stButton > button {
            width: 100%;
            height: 50px;
            border-radius: 14px;
            border: none;
            background: linear-gradient(90deg, #18BDF2, #0077C8);
            color: white;
            font-size: 16px;
            font-weight: 900;
            box-shadow: 0 10px 22px rgba(0,119,200,.22);
        }
        .mobile-card .stButton > button:hover { color:white; filter: brightness(1.02); }
        .mobile-note { text-align:center; color:#65748A; font-size:14px; padding-top:6px; }
        div[data-testid="stAlert"] { margin-left:16px; margin-right:16px; }
        @media (max-width: 390px) {
            .v360-title { font-size: 24px; }
            .v360-sub { font-size: 10px; letter-spacing:2.5px; }
            .molina-logo { max-width: 150px; max-height: 48px; }
            .card-title h2 { font-size: 24px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def aplicar_css_sidebar_desktop():
    st.markdown(
        """
        <style>
        /* SIDEBAR V360 - versão atualizada */
        section[data-testid="stSidebar"],
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div {
            background: linear-gradient(180deg, #061A33 0%, #09294D 56%, #0A3D7A 100%) !important;
        }
        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(24,189,242,.35) !important;
            box-shadow: 8px 0 26px rgba(6,26,51,.10);
        }
        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] a,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] div {
            color: #FFFFFF !important;
        }
        .sidebar-brand {
            text-align: center;
            padding: 20px 8px 18px 8px;
            margin: 0 0 16px 0;
            border-bottom: 1px solid rgba(255,255,255,.16);
        }
        .sidebar-v360 {
            font-size: 58px;
            line-height: 1;
            font-weight: 950;
            letter-spacing: -2px;
        }
        .sidebar-v360 .v360-letter {
            color: #18BDF2 !important;
        }
        .sidebar-v360 .v360-number {
            color: #FFFFFF !important;
        }
        .sidebar-cap {
            margin-top: 10px;
            color: #18BDF2 !important;
            font-size: 18px;
            font-weight: 950;
            letter-spacing: 5px;
        }
        .sidebar-user-card {
            background: rgba(255,255,255,.09) !important;
            border: 1px solid rgba(255,255,255,.18) !important;
            border-radius: 16px;
            padding: 14px 12px;
            margin: 8px 0 18px 0;
            box-shadow: 0 10px 24px rgba(0,0,0,.14);
        }
        .sidebar-user-name {
            font-weight: 900;
            font-size: 15px;
            margin-bottom: 7px;
            color:#FFFFFF !important;
        }
        .sidebar-user-profile {
            color: #B8D9EF !important;
            font-weight: 700;
            font-size: 13px;
        }
        .sidebar-menu-title {
            color: #B8D9EF !important;
            text-transform: uppercase;
            font-size: 12px;
            font-weight: 950;
            letter-spacing: 1.4px;
            margin: 12px 0 8px 0;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label {
            background: rgba(255,255,255,.07) !important;
            border: 1px solid rgba(255,255,255,.14) !important;
            border-radius: 12px !important;
            padding: 9px 10px !important;
            margin-bottom: 8px !important;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: rgba(24,189,242,.18) !important;
            border-color: rgba(24,189,242,.55) !important;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            border-color: #18BDF2 !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            background: rgba(255,255,255,.09) !important;
            border: 1px solid rgba(255,255,255,.22) !important;
            color: #FFFFFF !important;
            border-radius: 12px;
            font-weight: 850;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(24,189,242,.20) !important;
            border-color: rgba(24,189,242,.60) !important;
            color: #FFFFFF !important;
        }
        .sidebar-version {
            margin-top: 18px;
            color: rgba(255,255,255,.45) !important;
            font-size: 10px;
            text-align:center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def header_mobile():
    logo64 = get_logo_base64()
    logo_html = f'<img class="molina-logo" src="data:image/png;base64,{logo64}" />' if logo64 else '<div style="font-weight:800">MOLINA<br><span style="font-size:12px;letter-spacing:3px">ADVOGADOS</span></div>'
    user_line = ""
    if st.session_state.get("usuario"):
        u = st.session_state.usuario
        user_line = f"<div class='mobile-user-line'>Boa Vista • {u.get('nome','')}</div>"
    st.markdown(
        f"""
        <div class="mobile-header">
            <div class="brand-line">
                <div>
                    <div class="v360-title"><span style="color:#18BDF2">V</span>360</div>
                    <div class="v360-sub">CAPTAÇÃO</div>
                </div>
                <div class="molina-logo-wrap">{logo_html}</div>
            </div>
            {user_line}
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


def apenas_digitos(valor: str) -> str:
    if not valor:
        return ""
    return "".join(ch for ch in str(valor) if ch.isdigit())


def limpar_cpf(valor: str) -> str:
    return apenas_digitos(valor)


def formatar_cpf(valor: str) -> str:
    digitos = apenas_digitos(valor)
    if len(digitos) != 11:
        return valor or ""
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


def formatar_telefone(valor: str) -> str:
    digitos = apenas_digitos(valor)
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return valor.strip() if isinstance(valor, str) else ""


def cpf_valido_ou_vazio(valor: str) -> bool:
    digitos = apenas_digitos(valor)
    return digitos == "" or len(digitos) == 11


def telefone_valido(valor: str) -> bool:
    digitos = apenas_digitos(valor)
    return len(digitos) in (10, 11)


def buscar_lead_por_cpf(cpf: str):
    cpf_limpo = limpar_cpf(cpf)
    if not cpf_limpo:
        return None
    try:
        resp = (
            supabase.table(TABELA_LEADS)
            .select("id,nome_cliente,cpf,telefone,bairro,captador_nome,data_captacao,status_lead")
            .eq("cpf", cpf_limpo)
            .limit(1)
            .execute()
        )
        return resp.data[0] if resp.data else None
    except Exception:
        return None


def preparar_dataframe_exibicao(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    if "cpf" in df2.columns:
        df2["cpf"] = df2["cpf"].fillna("").apply(formatar_cpf)
    if "telefone" in df2.columns:
        df2["telefone"] = df2["telefone"].fillna("").apply(formatar_telefone)
    return df2


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


def listar_beneficios():
    try:
        resp = (
            supabase.table(TABELA_BENEFICIOS)
            .select("nome,ativo")
            .eq("ativo", True)
            .order("nome")
            .execute()
        )
        itens = [r["nome"] for r in (resp.data or []) if r.get("nome")]
        return itens or TIPOS_BENEFICIO
    except Exception:
        return TIPOS_BENEFICIO


def listar_locais_captacao():
    try:
        resp = (
            supabase.table(TABELA_LOCAIS)
            .select("nome,ativo")
            .eq("ativo", True)
            .order("nome")
            .execute()
        )
        return [r["nome"] for r in (resp.data or []) if r.get("nome")]
    except Exception:
        return []


def criar_beneficio(nome: str):
    return supabase.table(TABELA_BENEFICIOS).insert({"nome": normalizar_texto(nome), "ativo": True}).execute()


def criar_local_captacao(nome: str):
    return supabase.table(TABELA_LOCAIS).insert({"nome": normalizar_texto(nome), "ativo": True}).execute()


def salvar_historico(lead_id: str, usuario_nome: str, status: str, observacao: str, acao: str = "Atualização"):
    if not lead_id:
        return None
    dados = {
        "lead_id": lead_id,
        "usuario_nome": usuario_nome,
        "status": status,
        "observacao": observacao.strip() if observacao else "",
        "acao": acao,
    }
    return supabase.table(TABELA_HISTORICO).insert(dados).execute()


def carregar_historico(lead_id: str) -> pd.DataFrame:
    try:
        resp = (
            supabase.table(TABELA_HISTORICO)
            .select("*")
            .eq("lead_id", lead_id)
            .order("criado_em", desc=True)
            .execute()
        )
        dfh = pd.DataFrame(resp.data or [])
        if not dfh.empty and "criado_em" in dfh.columns:
            dfh["criado_em"] = pd.to_datetime(dfh["criado_em"], errors="coerce")
        return dfh
    except Exception:
        return pd.DataFrame()


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

    st.caption("Utilize seu usuário e senha fornecidos pelo administrador.")
    st.stop()

usuario = st.session_state.usuario
perfil = usuario.get("perfil")

# -------------------------------
# ROTAS DO CAPTADOR - ESTILO CELULAR
# -------------------------------
if perfil == "captador":
    aplicar_css_mobile()
    header_mobile()

    nav_atual = "➕ Novo Lead" if st.session_state.captador_pagina == "Novo Lead" else "📋 Minhas Captações"
    st.markdown("<div class='mobile-nav-box'>", unsafe_allow_html=True)
    nav_escolhida = st.radio(
        "Navegação",
        ["➕ Novo Lead", "📋 Minhas Captações"],
        index=0 if nav_atual == "➕ Novo Lead" else 1,
        horizontal=True,
        label_visibility="collapsed",
        key="captador_nav_radio",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    nova_pagina = "Novo Lead" if nav_escolhida == "➕ Novo Lead" else "Minhas Captações"
    if nova_pagina != st.session_state.captador_pagina:
        st.session_state.captador_pagina = nova_pagina
        st.rerun()

    if st.session_state.captador_pagina == "Novo Lead":
        abrir_card_mobile("Novo Lead", "Preencha os dados do cliente")
        with st.form("form_novo_lead_mobile", clear_on_submit=True):
            nome_cliente = st.text_input("Nome do cliente *", placeholder="Digite o nome completo")
            cpf = st.text_input("CPF", placeholder="000.000.000-00")
            telefone = st.text_input("Telefone *", placeholder="(95) 99999-9999")
            bairro = st.selectbox("Bairro *", BAIRROS_BOA_VISTA)
            locais_opcoes = listar_locais_captacao()
            if locais_opcoes:
                local_sel = st.selectbox("Local da captação *", ["Outro / digitar"] + locais_opcoes)
                local_captacao = st.text_input("Digite o local" if local_sel == "Outro / digitar" else "Confirmar local", value="" if local_sel == "Outro / digitar" else local_sel, placeholder="Ex.: Feira, praça, INSS, ação social...")
            else:
                local_captacao = st.text_input("Local da captação *", placeholder="Ex.: Feira, praça, INSS, ação social...")
            area_acao = st.selectbox("Área da ação *", AREAS_ACAO)
            tipo_beneficio = st.selectbox("Tipo de benefício *", listar_beneficios())
            observacao = st.text_area("Observação", placeholder="Informações úteis para o atendimento posterior")
            enviar = st.form_submit_button("💾 SALVAR LEAD")
            st.markdown("<div class='mobile-note'>🔒 Captador identificado automaticamente</div>", unsafe_allow_html=True)
        fechar_card_mobile()

        if enviar:
            cpf_limpo = limpar_cpf(cpf)
            duplicado = buscar_lead_por_cpf(cpf_limpo) if cpf_limpo else None
            if not nome_cliente or not telefone or not bairro or not local_captacao:
                st.error("Preencha os campos obrigatórios marcados com *.")
            elif not cpf_valido_ou_vazio(cpf):
                st.error("CPF inválido. Use 11 números ou deixe em branco.")
            elif not telefone_valido(telefone):
                st.error("Telefone inválido. Use DDD + número, exemplo: (95) 99999-9999.")
            elif duplicado:
                st.warning(
                    f"⚠️ Cliente já cadastrado: {duplicado.get('nome_cliente','')} | "
                    f"Captador: {duplicado.get('captador_nome','')} | "
                    f"Status: {duplicado.get('status_lead','')}"
                )
            else:
                dados = {
                    "captador_id": usuario["id"],
                    "captador_nome": usuario["nome"],
                    "unidade": "Boa Vista",
                    "nome_cliente": normalizar_texto(nome_cliente),
                    "cpf": cpf_limpo,
                    "telefone": formatar_telefone(telefone),
                    "bairro": bairro,
                    "local_captacao": normalizar_texto(local_captacao),
                    "area_acao": area_acao,
                    "tipo_beneficio": tipo_beneficio,
                    "observacao": observacao.strip(),
                    "status_lead": "Novo",
                }
                try:
                    resp = salvar_lead(dados)
                    novo_id = (resp.data or [{}])[0].get("id") if hasattr(resp, "data") else None
                    if novo_id:
                        salvar_historico(novo_id, usuario["nome"], "Novo", observacao.strip(), "Lead criado")
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
            st.dataframe(preparar_dataframe_exibicao(df[colunas]), use_container_width=True, hide_index=True)
        fechar_card_mobile()

    if st.button("Sair"):
        st.session_state.usuario = None
        st.rerun()
    st.stop()

# -------------------------------
# MENU DESKTOP - GESTOR / SUPERVISOR
# -------------------------------
aplicar_css_sidebar_desktop()
header_desktop(usuario)

st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <div class="sidebar-v360"><span class="v360-letter">V</span><span class="v360-number">360</span></div>
        <div class="sidebar-cap">CAPTAÇÃO</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f"""
    <div class="sidebar-user-card">
        <div class="sidebar-user-name">👤 {usuario['nome']}</div>
        <div class="sidebar-user-profile">🏷️ {usuario['perfil'].title()}</div>
    </div>
    <div class="sidebar-menu-title">Menu</div>
    """,
    unsafe_allow_html=True,
)

opcoes_base = {
    "➕ Novo Lead": "Novo Lead",
    "📋 Minhas Captações": "Minhas Captações",
}
if pode_ver_todos(usuario):
    opcoes_base.update({
        "📊 Dashboard Executivo": "Painel Gestor",
        "💡 Insights V360": "Insights V360",
        "✏️ Atualizar Lead": "Atualizar Lead",
        "⚙️ Cadastros": "Cadastros",
        "👥 Usuários": "Usuários",
    })

pagina_label = st.sidebar.radio("", list(opcoes_base.keys()), label_visibility="collapsed")
pagina = opcoes_base[pagina_label]

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div class='sidebar-version'>Versão: {VERSAO_APP}</div>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Sair"):
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
            locais_opcoes = listar_locais_captacao()
            if locais_opcoes:
                local_sel = st.selectbox("Local da captação *", ["Outro / digitar"] + locais_opcoes)
                local_captacao = st.text_input("Digite o local" if local_sel == "Outro / digitar" else "Confirmar local", value="" if local_sel == "Outro / digitar" else local_sel, placeholder="Ex.: Feira, praça, INSS, ação social...")
            else:
                local_captacao = st.text_input("Local da captação *", placeholder="Ex.: Feira, praça, INSS, ação social...")
            area_acao = st.selectbox("Área da ação *", AREAS_ACAO)
            tipo_beneficio = st.selectbox("Tipo de benefício *", listar_beneficios())
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
                resp = salvar_lead(dados)
                novo_id = (resp.data or [{}])[0].get("id") if hasattr(resp, "data") else None
                if novo_id:
                    salvar_historico(novo_id, usuario["nome"], "Novo", observacao.strip(), "Lead criado")
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
        st.dataframe(preparar_dataframe_exibicao(df[colunas]), use_container_width=True, hide_index=True)

        csv = df[colunas].to_csv(index=False).encode("utf-8-sig")
        st.download_button("Baixar CSV", csv, "captacoes.csv", "text/csv")

# -------------------------------
# PAINEL GESTOR - EXECUTIVO V360
# -------------------------------
elif pagina == "Painel Gestor":
    st.title("📊 Dashboard Executivo V360 Captação")
    st.caption("Boa Vista • Visão executiva de captação, conversão, produtividade, bairros, locais e gargalos.")

    st.markdown(
        """
        <style>
        .exec-card {
            background: linear-gradient(145deg, #061A33 0%, #0A3D7A 100%);
            border: 1px solid rgba(24,189,242,.25);
            border-radius: 18px;
            padding: 18px 16px;
            box-shadow: 0 12px 28px rgba(6,26,51,.12);
            min-height: 118px;
        }
        .exec-card-title { color: #B8D9EF; font-size: 12px; font-weight: 900; text-transform: uppercase; letter-spacing: .8px; }
        .exec-card-value { color: white; font-size: 33px; font-weight: 950; margin-top: 8px; line-height: 1; }
        .exec-card-sub { color: #18BDF2; font-size: 13px; font-weight: 700; margin-top: 10px; }
        .v360-section-title {
            color: #061A33;
            font-weight: 950;
            font-size: 22px;
            margin-top: 20px;
            margin-bottom: 8px;
        }
        .insight-box {
            background: linear-gradient(145deg, #EEF8FF 0%, #FFFFFF 100%);
            border-left: 5px solid #18BDF2;
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 10px;
            font-weight: 650;
            box-shadow: 0 8px 22px rgba(6,26,51,0.05);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    df_original = carregar_leads()

    if df_original.empty:
        st.info("Nenhum dado encontrado. Cadastre alguns leads de teste para visualizar o executivo.")
        st.stop()

    df = df_original.copy()
    for col in ["status_lead", "captador_nome", "bairro", "tipo_beneficio", "motivo_perda", "local_captacao", "quem_atendeu"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("")
    df["status_lead"] = df["status_lead"].replace("", "Novo")
    df["captador_nome"] = df["captador_nome"].replace("", "Não informado")
    df["bairro"] = df["bairro"].replace("", "Não informado")
    df["tipo_beneficio"] = df["tipo_beneficio"].replace("", "Não informado")
    df["local_captacao"] = df["local_captacao"].replace("", "Não informado")

    hoje = date.today()

    st.markdown("### 🔎 Filtros Executivos")
    colf1, colf2, colf3, colf4 = st.columns(4)
    with colf1:
        periodo = st.selectbox("Período", ["Últimos 7 dias", "Últimos 30 dias", "Mês atual", "Todos", "Personalizado"], index=1)
    with colf2:
        data_ini = st.date_input("Data inicial", hoje - timedelta(days=30))
    with colf3:
        data_fim = st.date_input("Data final", hoje)
    with colf4:
        status_filtro = st.multiselect("Status", STATUS_LEAD, default=STATUS_LEAD)

    if periodo == "Últimos 7 dias":
        data_ini, data_fim = hoje - timedelta(days=7), hoje
    elif periodo == "Últimos 30 dias":
        data_ini, data_fim = hoje - timedelta(days=30), hoje
    elif periodo == "Mês atual":
        data_ini, data_fim = hoje.replace(day=1), hoje
    elif periodo == "Todos":
        data_ini = df["data_captacao"].dt.date.min()
        data_fim = df["data_captacao"].dt.date.max()

    colf5, colf6, colf7, colf8 = st.columns(4)
    with colf5:
        captador_filtro = st.multiselect("Captador", sorted(df["captador_nome"].dropna().unique().tolist()))
    with colf6:
        bairro_filtro = st.multiselect("Bairro", sorted(df["bairro"].dropna().unique().tolist()))
    with colf7:
        beneficio_filtro = st.multiselect("Benefício", sorted(df["tipo_beneficio"].dropna().unique().tolist()))
    with colf8:
        local_filtro = st.multiselect("Local", sorted(df["local_captacao"].dropna().unique().tolist()))

    df = df[(df["data_captacao"].dt.date >= data_ini) & (df["data_captacao"].dt.date <= data_fim)]
    if status_filtro:
        df = df[df["status_lead"].isin(status_filtro)]
    if captador_filtro:
        df = df[df["captador_nome"].isin(captador_filtro)]
    if bairro_filtro:
        df = df[df["bairro"].isin(bairro_filtro)]
    if beneficio_filtro:
        df = df[df["tipo_beneficio"].isin(beneficio_filtro)]
    if local_filtro:
        df = df[df["local_captacao"].isin(local_filtro)]

    if df.empty:
        st.warning("Nenhum lead encontrado com os filtros selecionados.")
        st.stop()

    total = len(df)
    novos = int((df["status_lead"] == "Novo").sum())
    atendimento = int((df["status_lead"] == "Em atendimento").sum())
    convertidos = int((df["status_lead"] == "Convertido").sum())
    perdidos = int((df["status_lead"] == "Perdido").sum())
    conversao = (convertidos / total * 100) if total else 0
    perda_pct = (perdidos / total * 100) if total else 0

    def card_exec(titulo, valor, subtitulo=""):
        st.markdown(
            f"""
            <div class="exec-card">
                <div class="exec-card-title">{titulo}</div>
                <div class="exec-card-value">{valor}</div>
                <div class="exec-card-sub">{subtitulo}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 1 - CARDS EXECUTIVOS
    st.markdown("<div class='v360-section-title'>1. Cards Executivos</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: card_exec("📍 Captados", total, "leads no período")
    with c2: card_exec("📞 Em atendimento", atendimento, f"{novos} novos aguardando")
    with c3: card_exec("✅ Convertidos", convertidos, f"{conversao:.1f}% de conversão")
    with c4: card_exec("❌ Perdidos", perdidos, f"{perda_pct:.1f}% de perda")
    with c5: card_exec("📈 Conversão", f"{conversao:.1f}%", f"{convertidos}/{total} leads")

    # Preparações gerais
    ranking = df.groupby("captador_nome").agg(
        leads=("id", "count"),
        convertidos=("status_lead", lambda s: (s == "Convertido").sum()),
        em_atendimento=("status_lead", lambda s: (s == "Em atendimento").sum()),
        perdidos=("status_lead", lambda s: (s == "Perdido").sum()),
    ).reset_index()
    ranking["conversao_%"] = (ranking["convertidos"] / ranking["leads"] * 100).round(1)
    ranking = ranking.sort_values(["convertidos", "leads"], ascending=False)

    bairros = df.groupby("bairro").agg(
        leads=("id", "count"),
        convertidos=("status_lead", lambda s: (s == "Convertido").sum()),
        perdidos=("status_lead", lambda s: (s == "Perdido").sum()),
    ).reset_index()
    bairros["conversao_%"] = (bairros["convertidos"] / bairros["leads"] * 100).round(1)
    bairros = bairros.sort_values("leads", ascending=False)

    locais = df.groupby("local_captacao").agg(
        leads=("id", "count"),
        convertidos=("status_lead", lambda s: (s == "Convertido").sum()),
        perdidos=("status_lead", lambda s: (s == "Perdido").sum()),
    ).reset_index()
    locais["conversao_%"] = (locais["convertidos"] / locais["leads"] * 100).round(1)
    locais = locais.sort_values("leads", ascending=False)

    # 2 e 3
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<div class='v360-section-title'>2. Funil de Conversão</div>", unsafe_allow_html=True)
        funil_df = pd.DataFrame({
            "Etapa": ["Captados", "Novos", "Em atendimento", "Convertidos", "Perdidos"],
            "Quantidade": [total, novos, atendimento, convertidos, perdidos],
        })
        fig = px.funnel(funil_df, x="Quantidade", y="Etapa", text="Quantidade")
        fig.update_layout(height=390, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("<div class='v360-section-title'>3. Evolução Diária</div>", unsafe_allow_html=True)
        df_dia = df.copy()
        df_dia["dia"] = df_dia["data_captacao"].dt.date
        diario = df_dia.groupby("dia").size().reset_index(name="Leads")
        fig = px.line(diario, x="dia", y="Leads", markers=True)
        fig.update_layout(height=390, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # 4 - Ranking captadores
    st.markdown("<div class='v360-section-title'>4. Ranking de Captadores</div>", unsafe_allow_html=True)
    col3, col4 = st.columns([1.15, .85])
    with col3:
        fig = px.bar(ranking.head(10), x="leads", y="captador_nome", orientation="h", text="leads", title="Ranking por volume de leads")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=430, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        st.dataframe(ranking.rename(columns={
            "captador_nome": "Captador", "leads": "Leads", "convertidos": "Convertidos",
            "em_atendimento": "Em atendimento", "perdidos": "Perdidos", "conversao_%": "Conversão %"
        }), use_container_width=True, hide_index=True)

    # 5 - Benefícios
    st.markdown("<div class='v360-section-title'>5. Benefícios Mais Captados</div>", unsafe_allow_html=True)
    beneficio_df = df["tipo_beneficio"].value_counts().reset_index().head(12)
    beneficio_df.columns = ["Benefício", "Quantidade"]
    fig = px.bar(beneficio_df, x="Quantidade", y="Benefício", orientation="h", text="Quantidade")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=430, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # 6 e 7 - Bairros
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("<div class='v360-section-title'>6. Bairros com Mais Captação</div>", unsafe_allow_html=True)
        fig = px.bar(bairros.head(15), x="leads", y="bairro", orientation="h", text="leads")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=430, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with col6:
        st.markdown("<div class='v360-section-title'>7. Bairros com Maior Conversão</div>", unsafe_allow_html=True)
        bairros_conv = bairros[bairros["leads"] >= 3].copy()
        if bairros_conv.empty:
            st.info("Ainda não há volume suficiente por bairro. Mínimo: 3 leads por bairro.")
        else:
            bairros_conv = bairros_conv.sort_values(["conversao_%", "convertidos", "leads"], ascending=False).head(15)
            fig = px.bar(bairros_conv, x="conversao_%", y="bairro", orientation="h", text="conversao_%")
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=430, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(bairros_conv.rename(columns={"bairro":"Bairro", "leads":"Leads", "convertidos":"Convertidos", "perdidos":"Perdidos", "conversao_%":"Conversão %"}), use_container_width=True, hide_index=True)

    # 8 - Locais captação
    st.markdown("<div class='v360-section-title'>8. Locais de Captação</div>", unsafe_allow_html=True)
    col7, col8 = st.columns(2)
    with col7:
        fig = px.bar(locais.head(15), x="leads", y="local_captacao", orientation="h", text="leads", title="Locais com mais leads")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=430, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with col8:
        locais_conv = locais[locais["leads"] >= 3].copy()
        if locais_conv.empty:
            st.info("Ainda não há volume suficiente por local. Mínimo: 3 leads por local.")
        else:
            locais_conv = locais_conv.sort_values(["conversao_%", "convertidos", "leads"], ascending=False).head(15)
            st.dataframe(locais_conv.rename(columns={
                "local_captacao":"Local", "leads":"Leads", "convertidos":"Convertidos",
                "perdidos":"Perdidos", "conversao_%":"Conversão %"
            }), use_container_width=True, hide_index=True)

    # 9 - Motivos perda
    st.markdown("<div class='v360-section-title'>9. Motivos de Perda</div>", unsafe_allow_html=True)
    perdas = df[df["status_lead"] == "Perdido"].copy()
    if perdas.empty:
        st.info("Nenhum lead perdido no período selecionado.")
    else:
        perdas_df = perdas["motivo_perda"].fillna("Não informado").replace("", "Não informado").value_counts().reset_index()
        perdas_df.columns = ["Motivo", "Quantidade"]
        fig = px.bar(perdas_df, x="Quantidade", y="Motivo", orientation="h", text="Quantidade")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=390, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # 10 - Base completa
    st.markdown("<div class='v360-section-title'>10. Base Completa</div>", unsafe_allow_html=True)
    colunas_base = [
        "data_captacao", "nome_cliente", "cpf", "telefone", "bairro", "local_captacao",
        "area_acao", "tipo_beneficio", "status_lead", "captador_nome",
        "quem_atendeu", "motivo_perda", "observacao"
    ]
    colunas_base = [c for c in colunas_base if c in df.columns]
    st.dataframe(preparar_dataframe_exibicao(df[colunas_base]), use_container_width=True, hide_index=True)
    csv = df[colunas_base].to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Baixar base filtrada", csv, "v360_captacao_executivo.csv", "text/csv")

# -------------------------------
# INSIGHTS V360
# -------------------------------
elif pagina == "Insights V360":
    st.title("💡 Insights V360")
    st.caption("Boa Vista • Inteligência comercial, oportunidades e alertas da captação.")

    st.markdown(
        """
        <style>
        .insights-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 14px;
            margin-bottom: 18px;
        }
        .insight-card-v360 {
            background: linear-gradient(145deg, #FFFFFF 0%, #F4FAFF 100%);
            border: 1px solid #DCE8F4;
            border-left: 5px solid #18BDF2;
            border-radius: 18px;
            padding: 16px 16px;
            box-shadow: 0 10px 24px rgba(6,26,51,.07);
            min-height: 118px;
        }
        .insight-card-title { color:#061A33; font-size:14px; font-weight:950; margin-bottom:8px; }
        .insight-card-value { color:#0A3D7A; font-size:22px; font-weight:950; line-height:1.1; }
        .insight-card-sub { color:#65748A; font-size:13px; font-weight:700; margin-top:8px; }
        .alert-card {
            background:#FFF8E8;
            border:1px solid #FFE4A3;
            border-left:5px solid #F59E0B;
            border-radius:16px;
            padding:14px 16px;
            margin-bottom:10px;
            font-weight:700;
        }
        .op-card {
            background:#EEFDF7;
            border:1px solid #BDEEDB;
            border-left:5px solid #10B981;
            border-radius:16px;
            padding:14px 16px;
            margin-bottom:10px;
            font-weight:700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    df_original = carregar_leads()
    if df_original.empty:
        st.info("Nenhum dado encontrado. Cadastre alguns leads para gerar os insights.")
        st.stop()

    df = df_original.copy()
    for col in ["status_lead", "captador_nome", "bairro", "tipo_beneficio", "motivo_perda", "local_captacao", "quem_atendeu"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("")
    df["status_lead"] = df["status_lead"].replace("", "Novo")
    df["captador_nome"] = df["captador_nome"].replace("", "Não informado")
    df["bairro"] = df["bairro"].replace("", "Não informado")
    df["tipo_beneficio"] = df["tipo_beneficio"].replace("", "Não informado")
    df["local_captacao"] = df["local_captacao"].replace("", "Não informado")

    hoje = date.today()
    st.markdown("### 🔎 Filtros dos Insights")
    colf1, colf2, colf3, colf4 = st.columns(4)
    with colf1:
        periodo = st.selectbox("Período", ["Últimos 7 dias", "Últimos 30 dias", "Mês atual", "Todos", "Personalizado"], index=1, key="ins_periodo")
    with colf2:
        data_ini = st.date_input("Data inicial", hoje - timedelta(days=30), key="ins_data_ini")
    with colf3:
        data_fim = st.date_input("Data final", hoje, key="ins_data_fim")
    with colf4:
        status_filtro = st.multiselect("Status", STATUS_LEAD, default=STATUS_LEAD, key="ins_status")

    if periodo == "Últimos 7 dias":
        data_ini, data_fim = hoje - timedelta(days=7), hoje
    elif periodo == "Últimos 30 dias":
        data_ini, data_fim = hoje - timedelta(days=30), hoje
    elif periodo == "Mês atual":
        data_ini, data_fim = hoje.replace(day=1), hoje
    elif periodo == "Todos":
        data_ini = df["data_captacao"].dt.date.min()
        data_fim = df["data_captacao"].dt.date.max()

    colf5, colf6, colf7, colf8 = st.columns(4)
    with colf5:
        captador_filtro = st.multiselect("Captador", sorted(df["captador_nome"].dropna().unique().tolist()), key="ins_captador")
    with colf6:
        bairro_filtro = st.multiselect("Bairro", sorted(df["bairro"].dropna().unique().tolist()), key="ins_bairro")
    with colf7:
        beneficio_filtro = st.multiselect("Benefício", sorted(df["tipo_beneficio"].dropna().unique().tolist()), key="ins_beneficio")
    with colf8:
        local_filtro = st.multiselect("Local", sorted(df["local_captacao"].dropna().unique().tolist()), key="ins_local")

    df = df[(df["data_captacao"].dt.date >= data_ini) & (df["data_captacao"].dt.date <= data_fim)]
    if status_filtro:
        df = df[df["status_lead"].isin(status_filtro)]
    if captador_filtro:
        df = df[df["captador_nome"].isin(captador_filtro)]
    if bairro_filtro:
        df = df[df["bairro"].isin(bairro_filtro)]
    if beneficio_filtro:
        df = df[df["tipo_beneficio"].isin(beneficio_filtro)]
    if local_filtro:
        df = df[df["local_captacao"].isin(local_filtro)]

    if df.empty:
        st.warning("Nenhum lead encontrado com os filtros selecionados.")
        st.stop()

    total = len(df)
    convertidos = int((df["status_lead"] == "Convertido").sum())
    perdidos = int((df["status_lead"] == "Perdido").sum())
    conversao = (convertidos / total * 100) if total else 0
    perda_pct = (perdidos / total * 100) if total else 0

    def top_valor(coluna):
        vc = df[coluna].replace("", "Não informado").value_counts()
        if vc.empty:
            return "Sem dados", 0, 0
        nome = vc.index[0]
        qtd = int(vc.iloc[0])
        pct = (qtd / total * 100) if total else 0
        return nome, qtd, pct

    def agg_conversao(campo, minimo=3):
        base = df.groupby(campo).agg(
            leads=("id", "count"),
            convertidos=("status_lead", lambda s: (s == "Convertido").sum()),
        ).reset_index()
        if base.empty:
            return base
        base["conversao_%"] = (base["convertidos"] / base["leads"] * 100).round(1)
        base = base[base["leads"] >= minimo]
        return base.sort_values(["conversao_%", "convertidos", "leads"], ascending=False)

    def card_insight(titulo, valor, subtitulo=""):
        # Importante: retornar HTML sem espaços iniciais.
        # O Streamlit/Markdown interpreta linhas com 4+ espaços como bloco de código.
        return (
            f"<div class='insight-card-v360'>"
            f"<div class='insight-card-title'>{titulo}</div>"
            f"<div class='insight-card-value'>{valor}</div>"
            f"<div class='insight-card-sub'>{subtitulo}</div>"
            f"</div>"
        )

    top_bairro, top_bairro_qtd, top_bairro_pct = top_valor("bairro")
    top_captador, top_captador_qtd, top_captador_pct = top_valor("captador_nome")
    top_beneficio, top_beneficio_qtd, top_beneficio_pct = top_valor("tipo_beneficio")
    top_local, top_local_qtd, top_local_pct = top_valor("local_captacao")

    perdas = df[df["status_lead"] == "Perdido"].copy()
    if perdas.empty:
        top_motivo, top_motivo_qtd, top_motivo_pct = "Sem perdas", 0, 0
    else:
        motivo_vc = perdas["motivo_perda"].fillna("Não informado").replace("", "Não informado").value_counts()
        top_motivo = motivo_vc.index[0]
        top_motivo_qtd = int(motivo_vc.iloc[0])
        top_motivo_pct = (top_motivo_qtd / len(perdas) * 100) if len(perdas) else 0

    st.markdown("## 📌 Resumo Executivo")
    st.markdown(
        "<div class='insights-grid'>" +
        card_insight("🏆 Bairro líder em captação", top_bairro, f"{top_bairro_qtd} leads • {top_bairro_pct:.1f}% do período") +
        card_insight("🥇 Captador destaque", top_captador, f"{top_captador_qtd} leads • {top_captador_pct:.1f}% do período") +
        card_insight("📋 Benefício mais procurado", top_beneficio, f"{top_beneficio_qtd} leads • {top_beneficio_pct:.1f}% do período") +
        card_insight("🏪 Local mais produtivo", top_local, f"{top_local_qtd} leads • {top_local_pct:.1f}% do período") +
        card_insight("⚠️ Principal motivo de perda", top_motivo, f"{top_motivo_qtd} ocorrências • {top_motivo_pct:.1f}% das perdas") +
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("## 📈 Inteligência Comercial")
    df_int = df.copy()
    df_int["dia_semana_num"] = df_int["data_captacao"].dt.weekday
    dias_map = {0:"Segunda-feira", 1:"Terça-feira", 2:"Quarta-feira", 3:"Quinta-feira", 4:"Sexta-feira", 5:"Sábado", 6:"Domingo"}
    df_int["dia_semana"] = df_int["dia_semana_num"].map(dias_map)

    def melhor_bairro_beneficio(texto_beneficio):
        sub = df[df["tipo_beneficio"].str.contains(texto_beneficio, case=False, na=False)].copy()
        if sub.empty:
            return "Sem dados", "Nenhum lead encontrado"
        sub_conv = sub[sub["status_lead"] == "Convertido"]
        base = sub_conv if not sub_conv.empty else sub
        vc = base["bairro"].value_counts()
        nome = vc.index[0]
        qtd = int(vc.iloc[0])
        label = "contratos" if not sub_conv.empty else "leads"
        return nome, f"{qtd} {label} de {texto_beneficio}"

    bairro_loas, sub_loas = melhor_bairro_beneficio("LOAS")
    bairro_aux, sub_aux = melhor_bairro_beneficio("Auxílio")

    dia_vc = df_int["dia_semana"].value_counts()
    melhor_dia = dia_vc.index[0] if not dia_vc.empty else "Sem dados"
    melhor_dia_qtd = int(dia_vc.iloc[0]) if not dia_vc.empty else 0

    mes_atual = hoje.replace(day=1)
    df_mes = df_original.copy()
    if not df_mes.empty:
        df_mes["data_captacao"] = pd.to_datetime(df_mes["data_captacao"], errors="coerce")
        df_mes = df_mes[df_mes["data_captacao"].dt.date >= mes_atual]
    conv_mes = df_mes[df_mes["status_lead"] == "Convertido"] if not df_mes.empty and "status_lead" in df_mes.columns else pd.DataFrame()
    if conv_mes.empty:
        melhor_captador_mes, melhor_captador_mes_sub = "Sem conversões", "Nenhum contrato no mês atual"
    else:
        vc = conv_mes["captador_nome"].fillna("Não informado").replace("", "Não informado").value_counts()
        melhor_captador_mes = vc.index[0]
        melhor_captador_mes_sub = f"{int(vc.iloc[0])} conversões no mês"

    locais_conv = agg_conversao("local_captacao")
    bairros_conv = agg_conversao("bairro")
    benef_conv = agg_conversao("tipo_beneficio")
    capt_conv = agg_conversao("captador_nome")

    def top_conv(base, campo, nome_vazio="Sem dados"):
        if base.empty:
            return nome_vazio, "Volume mínimo: 3 leads"
        linha = base.iloc[0]
        return linha[campo], f"{linha['conversao_%']:.1f}% • {int(linha['convertidos'])}/{int(linha['leads'])} convertidos"

    local_tx, local_tx_sub = top_conv(locais_conv, "local_captacao")
    bairro_tx, bairro_tx_sub = top_conv(bairros_conv, "bairro")
    beneficio_tx, beneficio_tx_sub = top_conv(benef_conv, "tipo_beneficio")
    captador_tx, captador_tx_sub = top_conv(capt_conv, "captador_nome")

    st.markdown(
        "<div class='insights-grid'>" +
        card_insight("📈 Melhor bairro para LOAS", bairro_loas, sub_loas) +
        card_insight("📈 Melhor bairro para Auxílio Doença", bairro_aux, sub_aux) +
        card_insight("📈 Melhor dia da semana para captação", melhor_dia, f"{melhor_dia_qtd} leads no período") +
        card_insight("📈 Melhor captador do mês", melhor_captador_mes, melhor_captador_mes_sub) +
        card_insight("📈 Local com maior taxa de conversão", local_tx, local_tx_sub) +
        card_insight("📈 Bairro com maior conversão geral", bairro_tx, bairro_tx_sub) +
        card_insight("📈 Benefício com maior conversão", beneficio_tx, beneficio_tx_sub) +
        card_insight("📈 Captador com maior taxa de conversão", captador_tx, captador_tx_sub) +
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("## 🎯 Oportunidades")
    oportunidades = []
    if not bairros_conv.empty:
        bairros_volume = df.groupby("bairro").size().reset_index(name="leads").sort_values("leads", ascending=False)
        top_vol_bairro = bairros_volume.iloc[0]
        conv_top_vol = bairros_conv[bairros_conv["bairro"] == top_vol_bairro["bairro"]]
        if not conv_top_vol.empty and float(conv_top_vol.iloc[0]["conversao_%"]) < conversao:
            oportunidades.append(
                f"<b>{top_vol_bairro['bairro']}</b> possui alto volume de leads, mas conversão abaixo da média. Recomenda-se revisar abordagem e acompanhamento."
            )
    if not locais_conv.empty:
        linha = locais_conv.iloc[0]
        oportunidades.append(
            f"<b>{linha['local_captacao']}</b> apresenta a maior taxa de conversão ({linha['conversao_%']:.1f}%). Recomenda-se priorizar novas ações nesse local."
        )
    if not benef_conv.empty:
        linha = benef_conv.iloc[0]
        oportunidades.append(
            f"<b>{linha['tipo_beneficio']}</b> é o benefício com melhor conversão ({linha['conversao_%']:.1f}%). Pode ser prioridade em campanhas e roteiros de captação."
        )
    if not oportunidades:
        oportunidades.append("Ainda não há volume suficiente para oportunidades avançadas. Continue cadastrando leads para o V360 identificar padrões.")
    for item in oportunidades:
        st.markdown(f"<div class='op-card'>🎯 {item}</div>", unsafe_allow_html=True)

    st.markdown("## 🚨 Alertas")
    alertas = []
    if perda_pct >= 30:
        alertas.append(f"Taxa de perda em <b>{perda_pct:.1f}%</b> no período filtrado. Verificar motivos de perda e velocidade de atendimento.")
    pendentes = int(((df["status_lead"] == "Novo") | (df["status_lead"] == "Em atendimento")).sum())
    if pendentes >= max(5, int(total * 0.4)):
        alertas.append(f"Existem <b>{pendentes}</b> leads ainda sem conclusão. Pode haver gargalo no atendimento posterior.")
    if total < 10:
        alertas.append("Volume de dados ainda baixo. Alguns insights podem mudar bastante com novos cadastros.")
    if not alertas:
        alertas.append("Nenhum alerta crítico identificado no período filtrado.")
    for item in alertas:
        st.markdown(f"<div class='alert-card'>🚨 {item}</div>", unsafe_allow_html=True)

# -------------------------------
# ATUALIZAR LEAD - V2
# -------------------------------
elif pagina == "Atualizar Lead":
    st.title("✏️ Atualizar Lead")
    st.caption("Busque o lead, atualize o funil e registre o histórico do atendimento.")
    df = carregar_leads()

    if df.empty:
        st.info("Nenhum lead encontrado.")
        st.stop()

    termo = st.text_input("Pesquisar por nome, CPF, telefone ou captador", placeholder="Digite parte do nome, CPF, telefone ou captador...")
    df_busca = df.copy()
    if termo:
        termo_norm = termo.lower().strip()
        cols_busca = ["nome_cliente", "cpf", "telefone", "captador_nome", "bairro", "status_lead"]
        mask = pd.Series(False, index=df_busca.index)
        for c in cols_busca:
            if c in df_busca.columns:
                mask = mask | df_busca[c].fillna("").astype(str).str.lower().str.contains(termo_norm, na=False)
        df_busca = df_busca[mask]

    if df_busca.empty:
        st.warning("Nenhum lead encontrado para essa busca.")
        st.stop()

    df_busca["label"] = (
        df_busca["nome_cliente"].fillna("") + " | " +
        df_busca["telefone"].fillna("") + " | " +
        df_busca["bairro"].fillna("") + " | " +
        df_busca["status_lead"].fillna("")
    )
    lead_label = st.selectbox("Selecione o lead", df_busca["label"].tolist())
    lead = df_busca[df_busca["label"] == lead_label].iloc[0]
    lead_id = str(lead["id"])

    st.markdown("### Ficha do Lead")
    c1, c2, c3 = st.columns(3)
    c1.metric("Cliente", lead.get("nome_cliente", ""))
    c2.metric("Status", lead.get("status_lead", "Novo"))
    c3.metric("Captador", lead.get("captador_nome", ""))

    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"**CPF:** {formatar_cpf(lead.get('cpf','') or '')}")
        st.write(f"**Telefone:** {formatar_telefone(lead.get('telefone','') or '')}")
        st.write(f"**Bairro:** {lead.get('bairro','')}")
        st.write(f"**Local:** {lead.get('local_captacao','')}")
    with col_b:
        st.write(f"**Benefício:** {lead.get('tipo_beneficio','')}")
        st.write(f"**Área:** {lead.get('area_acao','')}")
        data_cap = lead.get("data_captacao")
        st.write(f"**Data captação:** {data_cap.strftime('%d/%m/%Y %H:%M') if hasattr(data_cap, 'strftime') else data_cap}")
        st.write(f"**Quem atendeu:** {lead.get('quem_atendeu','') or 'Ainda não informado'}")

    st.markdown("### Atualização do Atendimento")
    with st.form("form_atualizar_lead_v2"):
        col1, col2 = st.columns(2)
        with col1:
            status_atual = lead.get("status_lead", "Novo")
            status_idx = STATUS_LEAD.index(status_atual) if status_atual in STATUS_LEAD else 0
            status = st.selectbox("Status do Lead", STATUS_LEAD, index=status_idx)

            usuarios = listar_usuarios_ativos()
            nomes_usuarios = [u["nome"] for u in usuarios]
            quem_atendeu_atual = lead.get("quem_atendeu") or ""
            lista_atendentes = [""] + nomes_usuarios
            idx_atendente = lista_atendentes.index(quem_atendeu_atual) if quem_atendeu_atual in lista_atendentes else 0
            quem_atendeu = st.selectbox("Quem atendeu", lista_atendentes, index=idx_atendente)
        with col2:
            motivo_atual = lead.get("motivo_perda") or ""
            idx_motivo = MOTIVOS_PERDA.index(motivo_atual) if motivo_atual in MOTIVOS_PERDA else 0
            motivo_perda = st.selectbox("Motivo da perda", MOTIVOS_PERDA, index=idx_motivo)
            observacao_atual = lead.get("observacao") or ""
            observacao_principal = st.text_area("Observação principal do lead", value=observacao_atual)

        observacao_atendimento = st.text_area(
            "Nova observação do atendimento / histórico",
            placeholder="Ex.: Cliente respondeu, documentos solicitados, atendimento agendado..."
        )
        salvar = st.form_submit_button("💾 Salvar Atualização")

    if salvar:
        if status == "Perdido" and not motivo_perda:
            st.error("Informe o motivo da perda quando o status for Perdido.")
        else:
            dados = {
                "status_lead": status,
                "quem_atendeu": quem_atendeu or None,
                "motivo_perda": motivo_perda if status == "Perdido" else None,
                "observacao": observacao_principal.strip(),
            }
            if status == "Convertido" and lead.get("status_lead") != "Convertido":
                dados["data_conversao"] = "now()"
                dados["responsavel_conversao"] = quem_atendeu or usuario["nome"]

            # Supabase não aceita now() como string para timestamptz via update; grava pelo banco se coluna existir usando datetime ISO.
            if dados.get("data_conversao") == "now()":
                from datetime import datetime, timezone
                dados["data_conversao"] = datetime.now(timezone.utc).isoformat()

            try:
                atualizar_lead(lead_id, dados)
                texto_hist = observacao_atendimento.strip() or f"Status alterado para {status}."
                salvar_historico(lead_id, usuario["nome"], status, texto_hist, "Atualização de atendimento")
                st.success("Lead atualizado e histórico registrado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar lead: {e}")

    st.markdown("### Histórico do Lead")
    hist = carregar_historico(lead_id)
    if hist.empty:
        st.info("Nenhum histórico registrado para este lead.")
    else:
        hist_exibir = hist.copy()
        if "criado_em" in hist_exibir.columns:
            hist_exibir["criado_em"] = hist_exibir["criado_em"].dt.strftime("%d/%m/%Y %H:%M")
        cols = ["criado_em", "acao", "usuario_nome", "status", "observacao"]
        cols = [c for c in cols if c in hist_exibir.columns]
        st.dataframe(hist_exibir[cols], use_container_width=True, hide_index=True)

# -------------------------------
# CADASTROS
# -------------------------------
elif pagina == "Cadastros":
    st.title("⚙️ Cadastros")
    st.caption("Cadastre benefícios e locais de captação sem precisar alterar o código.")

    tab1, tab2 = st.tabs(["Benefícios", "Locais de Captação"])
    with tab1:
        st.subheader("Benefícios")
        with st.form("form_novo_beneficio"):
            nome_beneficio = st.text_input("Novo benefício", placeholder="Ex.: Aposentadoria por invalidez")
            salvar_beneficio = st.form_submit_button("Adicionar benefício")
        if salvar_beneficio:
            if not nome_beneficio.strip():
                st.error("Informe o nome do benefício.")
            else:
                try:
                    criar_beneficio(nome_beneficio)
                    st.success("Benefício cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar benefício: {e}")
        st.dataframe(pd.DataFrame({"Benefícios ativos": listar_beneficios()}), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Locais de Captação")
        with st.form("form_novo_local"):
            nome_local = st.text_input("Novo local", placeholder="Ex.: Feira do Nova Cidade")
            salvar_local = st.form_submit_button("Adicionar local")
        if salvar_local:
            if not nome_local.strip():
                st.error("Informe o nome do local.")
            else:
                try:
                    criar_local_captacao(nome_local)
                    st.success("Local cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar local: {e}")
        locais = listar_locais_captacao()
        if locais:
            st.dataframe(pd.DataFrame({"Locais ativos": locais}), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum local cadastrado ainda. O captador poderá digitar livremente até você cadastrar os principais locais.")

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
