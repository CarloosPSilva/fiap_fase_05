from PIL import Image
import streamlit as st
st.set_page_config(page_title="MVP IA - Recrutamento Decision", layout="wide")

from aplicacao.operacoes.pagina_1 import predicao_01
from aplicacao.operacoes.pagina_2 import visao_geral_02
from aplicacao.operacoes.pagina_3 import analise_vaga_03
from aplicacao.operacoes.pagina_4 import analise_candidato_04
from aplicacao.operacoes.pagina_5 import clusterizacao_perfil_05
from aplicacao.operacoes.pagina_6 import consulta_candidato_profissional_06
from aplicacao.operacoes.pagina_7 import recomendacao_07
from aplicacao.utils.carregar_dados import carregar_base
from aplicacao.utils.utils import style




img = Image.open("aplicacao/imagens/p1.png")
st.sidebar.image(img)

st.title(" MVP Inteligência Artificial para Recrutamento - Decision")
style()

# Menu lateral com emojis e nova ordem
st.sidebar.markdown(
    '<label class="sidebar-label"> Menu de Navegação</label>', unsafe_allow_html=True)

# Menu lateral
pagina = st.sidebar.selectbox("", [
    "🔍 1. Predição de Aprovação",
    "📊 2. Visão Geral",
    "📌 3. Análise de Vagas",
    "🧑‍💼 4. Análise de Candidatos",
    "🧬 5. Clusterização de Perfis",
    "🔎 6. Consulta de Candidato",
    "📈 7. Recomendação e Insights"
], key="menu_principal")

# Carregamento de dados
vagas_df, prospects_json, applicants_json = carregar_base()

# Inicialização de variáveis globais
if 'candidatos_df_clusterizado' not in st.session_state:
    st.session_state['candidatos_df_clusterizado'] = None

# Direcionamento das páginas
if pagina == "🔍 1. Predição de Aprovação":
    predicao_01()

elif pagina == "📊 2. Visão Geral":
    visao_geral_02()

elif pagina == "📌 3. Análise de Vagas":
    analise_vaga_03(vagas_df)

elif pagina == "🧑‍💼 4. Análise de Candidatos":
    analise_candidato_04(prospects_json)

elif pagina == "🧬 5. Clusterização de Perfis":
    candidatos_df = clusterizacao_perfil_05(prospects_json, applicants_json)

elif pagina == "🔎 6. Consulta de Candidato":
    consulta_candidato_profissional_06(
        prospects_json, applicants_json, codigo_fixo="33404")

elif pagina == "📈 7. Recomendação e Insights":
    recomendacao_07(prospects_json, applicants_json)


st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 **Desenvolvido por Carlos Pereira Silva**")
