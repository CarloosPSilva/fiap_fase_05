from PIL import Image
import streamlit as st
import sys
st.set_page_config(page_title="MVP IA - Recrutamento Decision", layout="wide")
from aplicacao.operacoes.pagina_1 import predicao_1
from aplicacao.operacoes.pagina_2 import visao_geral_02
from aplicacao.operacoes.pagina_3 import analise_vaga_03
from aplicacao.operacoes.pagina_4 import analise_candidato_04

from aplicacao.utils.preparar_candidatos_df import preparar_candidatos_df
from aplicacao.utils.utils import style

# Corrige possível erro com torch.classes
sys.modules["torch.classes"] = None

# Configuração da página


# Estilo global
style()

# Logo lateral
img = Image.open("aplicacao/imagens/p1.png")
st.sidebar.image(img)

# Título principal
st.title("MVP Inteligência Artificial para Recrutamento - Decision")

# Menu lateral
pagina = st.sidebar.selectbox("Selecione a página: ", [
    "1. Predição de Aprovação",
    "2. Visão Geral",
    "3. Análise de Vagas",
    "4. Análise de Candidatos"
], key="menu_principal")


@st.cache_data(show_spinner="Carregando dados e preparando base...")
def carregar_dados():
    vagas_df, prospects_df, prospects_json = preparar_candidatos_df()
    return vagas_df, prospects_df, prospects_json

# Carregamento e roteamento
try:
    vagas_df, prospects_df, prospects_json = carregar_dados()

    if pagina == "1. Predição de Aprovação":
        predicao_1()

    elif pagina == "2. Visão Geral":
        visao_geral_02()

    elif pagina == "3. Análise de Vagas":
        analise_vaga_03(vagas_df)

    elif pagina == "4. Análise de Candidatos":
        analise_candidato_04(prospects_json)

except Exception as e:
    st.error(f"Erro ao carregar dados ou renderizar a página: {e}")
    st.stop()

# Rodapé
st.sidebar.markdown("---")
st.sidebar.markdown("**Desenvolvido por Carlos Pereira Silva**")