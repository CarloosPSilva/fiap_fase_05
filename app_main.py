from PIL import Image
import streamlit as st
import sys

from aplicacao.operacoes.pagina_7 import recomendacao_07
sys.modules["torch.classes"] = None

# Configuração da página
st.set_page_config(page_title="MVP IA - Recrutamento Decision", layout="wide")

# Importações internas
from aplicacao.operacoes.pagina_1 import predicao_55
from aplicacao.operacoes.pagina_2 import visao_geral_02
from aplicacao.operacoes.pagina_3 import analise_vaga_03
from aplicacao.operacoes.pagina_4 import analise_candidato_04
from aplicacao.operacoes.pagina_5 import clusterizacao_perfil_05
from aplicacao.operacoes.pagina_6 import consulta_candidato_profissional_06

from aplicacao.utils.utils import style

from aplicacao.utils.preparar_candidatos_df import clusterizar_candidatos, preparar_candidatos_df

# Estilo global
style()

# Logo lateral
img = Image.open("aplicacao/imagens/p1.png")
st.sidebar.image(img)

# Título principal
st.title("MVP Inteligência Artificial para Recrutamento - Decision")

# Menu lateral
pagina = st.sidebar.selectbox("Selecione a página: ", [
    "🔍 1. Predição de Aprovação",
    "📊 2. Visão Geral",
    "📌 3. Análise de Vagas",
    "🧑‍💼 4. Análise de Candidatos",
    # "🧬 5. Clusterização de Perfis",
    # "🔎 6. Consulta de Candidato",
    # "📈 7. Recomendação e Insights"
], key="menu_principal")

@st.cache_data(show_spinner="Carregando dados e preparando base...")
def carregar_e_preparar():
    candidatos_df, vagas_df, prospects_json, applicants_json = preparar_candidatos_df()

    # ⚠️ Remove o campo com dicts para evitar erro no cache
    if 'dados_completos' in candidatos_df.columns:
        candidatos_df = candidatos_df.drop(columns=['dados_completos'])

    return candidatos_df, vagas_df, prospects_json, applicants_json

# @st.cache_data(show_spinner="Executando clusterização...")
# def carregar_clusterizados(candidatos_df):
#     return clusterizar_candidatos(candidatos_df)

# 🔃 Carregar dados uma única vez
try:
    _, vagas_df, prospects_json, applicants_json = carregar_e_preparar()
    # candidatos_clusterizados_df = carregar_clusterizados(candidatos_df)

    if pagina == "🔍 1. Predição de Aprovação":
        predicao_55()

    elif pagina == "📊 2. Visão Geral":
        visao_geral_02()

    elif pagina == "📌 3. Análise de Vagas":
        analise_vaga_03(vagas_df)

    elif pagina == "🧑‍💼 4. Análise de Candidatos":
        analise_candidato_04(prospects_json)

    # elif pagina == "🧬 5. Clusterização de Perfis":
    #     clusterizacao_perfil_05(candidatos_clusterizados_df)

    # elif pagina == "🔎 6. Consulta de Candidato":
    # #     consulta_candidato_profissional_06(prospects_json, applicants_json, codigo_fixo="33404")

    # elif pagina == "📈 7. Recomendação e Insights":
    #     recomendacao_07(candidatos_clusterizados_df)

except Exception as e:
    st.error(f"Erro ao carregar dados ou renderizar a página: {e}")
    st.stop()

# Rodapé lateral
st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 **Desenvolvido por Carlos Pereira Silva**")