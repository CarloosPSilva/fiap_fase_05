import pickle
import joblib
import warnings
import fitz
import nltk
import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from streamlit_extras.metric_cards import style_metric_cards

# Configurações iniciais
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")
warnings.simplefilter("ignore")


# # == == == == == == == == == == == == == == == == == == == == == == ==
# # FUNÇÕES DE CARREGAMENTO E PROCESSAMENTO
# # == == == == == == == == == == == == == == == == == == == == == == ==


# @st.cache_resource
def load_models():
    """Carrega os modelos e dados necessários"""
    with open("aplicacao/modelo/vagas.pkl", "rb") as f:
        jobs = pickle.load(f)

    logreg = joblib.load("aplicacao/modelo/logistic_model.pkl")
    xgb = joblib.load("aplicacao/modelo/xgboost_model.pkl")
    embedding_model = SentenceTransformer(
        'paraphrase-multilingual-MiniLM-L12-v2')

    job_data = joblib.load("aplicacao/modelo/job_data.pkl")
    return jobs, logreg, xgb, embedding_model, job_data["job_ids"], job_data["job_titles"], job_data["job_embeddings"]


jobs, logreg, xgb, embedding_model, job_ids, job_titles, job_embeddings = load_models()


def preprocess(text):
    import re
    import string
    from nltk.corpus import stopwords

    stop_words = set(stopwords.words('portuguese'))

    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))

    # tokenização simples
    tokens = [word for word in text.split() if word not in stop_words and len(word) > 2]

    return ' '.join(tokens)


def predict_jobs_for_cv(cv_text, top_n=5):
    """Prediz as melhores vagas para um currículo"""
    cleaned_cv = preprocess(cv_text)
    cv_vec = embedding_model.encode([cleaned_cv])
    sims = cosine_similarity(cv_vec, job_embeddings).flatten()

    results = []
    for i, sim in enumerate(sims):
        logreg_prob = logreg.predict_proba([[sim]])[0][1]
        xgb_prob = xgb.predict_proba([[sim]])[0][1]
        ensemble_prob = (logreg_prob + xgb_prob) / 2

        job = jobs.get(job_ids[i], {})
        results.append({
            "id_vaga": job_ids[i],
            "titulo_da_vaga": job.get("informacoes_basicas", {}).get("titulo_vaga", "N/A"),
            "area": job.get("perfil_vaga", {}).get("areas_atuacao", "N/A"),
            "habilidades": job.get("perfil_vaga", {}).get("competencia_tecnicas_e_comportamentais", "Não informado"),
            "atividades": job.get("perfil_vaga", {}).get("principais_atividades", "Não informado"),
            "similaridade": sim,
            "probabilidade_de_contratacao": ensemble_prob
        })

    return pd.DataFrame(sorted(results, key=lambda x: x["probabilidade_de_contratacao"], reverse=True)[:top_n])


def extract_text_from_pdf(file):
    """Extrai texto de arquivo PDF"""
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# ==============================================
# INTERFACE PRINCIPAL
# ==============================================
def predicao_1():
    # Inicialização segura dos estados usados
    if 'cv_text' not in st.session_state:
        st.session_state['cv_text'] = ""

    if 'df_recomendacoes' not in st.session_state:
        st.session_state['df_recomendacoes'] = pd.DataFrame()

    # Supondo que jobs esteja disponível globalmente ou carregado antes
    global jobs
    if 'jobs' not in globals():
        jobs = {}

    # Header moderno
    with st.container():
        st.markdown("""
        <div class="header-container">
            <h2 class="header-text">Encontre as melhores oportunidades com base no seu currículo e trajetória profissional.</h2>
        </div>
        """, unsafe_allow_html=True)

    # Seção de upload
    with st.container():
        # st.markdown("####  Envie seu currículo")
        col1, col2 = st.columns([3, 1])
        with col1:
            uploaded_file = st.file_uploader(
                "Arraste e solte seu arquivo PDF aqui ou clique para selecionar",
                type=["pdf"],
                label_visibility="visible"
            )
        with col2:
            st.markdown("""
            <div style="background-color: #e3f2fd; padding: 1rem; border-radius: 10px;">
                <p style="margin: 0; font-size: 0.9rem; color: black;">
                    📌 <strong>Dica:</strong> Seu currículo deve estar em formato PDF e conter informações claras sobre suas habilidades e experiências.
                </p>
            </div>
            """, unsafe_allow_html=True)

    if uploaded_file:
        with st.spinner('Analisando seu currículo...'):
            cv_text = extract_text_from_pdf(uploaded_file)

            if not cv_text.strip():
                st.error("""
                <div style="background-color: #ffebee; padding: 1rem; border-left: 5px solid #f44336; border-radius: 5px;">
                    ⚠️ Não foi possível extrair texto do PDF. Verifique se o arquivo não está vazio ou protegido.
                </div>
                """, unsafe_allow_html=True)
                return

            # Verificação mais robusta do conteúdo
            texto_cv = cv_text.lower()
            keywords_pt = ["experiência", "formação", "profissional", "habilidades", "projetos", "empresa", "cargo"]
            keywords_en = ["experience", "education", "professional", "skills", "projects", "company", "position"]

            total_keywords = sum(kw in texto_cv for kw in keywords_pt + keywords_en)

            if len(texto_cv.split()) < 40 or total_keywords < 2:
                st.error("""
                <div style="background-color: #ffebee; padding: 1rem; border-left: 5px solid #f44336; border-radius: 5px;">
                    ⚠️ O arquivo enviado não parece conter informações típicas de um currículo.<br>
                    Verifique se está enviando um documento válido, com detalhes sobre sua formação e experiência profissional.
                </div>
                """, unsafe_allow_html=True)
                return

            # Geração de recomendações
            df_recomendacoes = predict_jobs_for_cv(cv_text)

            if isinstance(df_recomendacoes, pd.DataFrame) and not df_recomendacoes.empty:
                st.session_state['cv_text'] = cv_text
                st.session_state['df_recomendacoes'] = df_recomendacoes
            else:
                st.error("❌ Nenhuma recomendação válida foi gerada.")
                return

    # Exibe resultados se já estiverem no session_state e tiver conteúdo
    df_recomendacoes = st.session_state.get('df_recomendacoes')
    if isinstance(df_recomendacoes, pd.DataFrame) and not df_recomendacoes.empty:
        st.markdown("""
        <div class="success-box">
             Análise concluída com sucesso! Veja abaixo as vagas que melhor se encaixam no seu perfil.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("###  Resultados da Análise")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Probabilidade Média", f"{df_recomendacoes['probabilidade_de_contratacao'].mean():.1%}")

        with col2:
            st.metric("Melhor Match", f"{df_recomendacoes['similaridade'].max():.1%}")

        with col3:
            st.metric("Área com Mais Oportunidades", df_recomendacoes["area"].mode()[0])

        style_metric_cards()

        # Top vagas
        st.markdown("###  Vagas Recomendadas")

        df_display = df_recomendacoes[[
            "titulo_da_vaga", "area", "probabilidade_de_contratacao", "similaridade"
        ]].rename(columns={
            "titulo_da_vaga": "Vaga",
            "area": "Área",
            "probabilidade_de_contratacao": "Probabilidade",
            "similaridade": "Match"
        })

        df_display["Probabilidade"] = pd.to_numeric(df_display["Probabilidade"], errors='coerce')
        df_display["Match"] = pd.to_numeric(df_display["Match"], errors='coerce')

        st.dataframe(
            df_display.style
            .format({"Probabilidade": "{:.1%}", "Match": "{:.1%}"})
            .set_properties(**{'text-align': 'left'})
            .set_table_styles([{
                'selector': 'th',
                'props': [('background-color', 'var(--primary-color)'),
                          ('color', 'white'),
                          ('font-weight', 'bold')]
            }]),
            use_container_width=True,
            height=250
        )

        st.markdown("---")
        st.markdown("###  Detalhes das Vagas Recomendadas")

        tabs = st.tabs([f"Vaga #{i+1}" for i in range(len(df_recomendacoes))])

        for idx, (tab, (_, row)) in enumerate(zip(tabs, df_recomendacoes.iterrows())):
            with tab:
                st.markdown(f"#### {row.get('titulo_da_vaga', 'Título não informado')}")

                col_prob, col_sim = st.columns(2)
                with col_prob:
                    st.progress(int(row.get('probabilidade_de_contratacao', 0) * 100))
                    st.caption(f"Probabilidade: {row.get('probabilidade_de_contratacao', 0):.1%}")

                with col_sim:
                    st.progress(int(row.get('similaridade', 0) * 100))
                    st.caption(f"Match: {row.get('similaridade', 0):.1%}")

                st.markdown("---")
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.markdown(f"**Área:** {row.get('area', 'Não informado')}")
                    st.markdown(f"**ID da Vaga:** `{row.get('id_vaga', 'N/A')}`")

                with col_info2:
                    st.markdown(f"**Localização:** {jobs.get(row['id_vaga'], {}).get('informacoes_basicas', {}).get('local_de_trabalho', 'Não informado')}")
                    st.markdown(f"**Tipo de Contratação:** {jobs.get(row['id_vaga'], {}).get('informacoes_basicas', {}).get('tipo_de_contratacao', 'Não informado')}")

                with st.expander("🛠 **Habilidades Requeridas**", expanded=False):
                    st.write(row.get('habilidades') or "Informações não disponíveis para esta vaga.")

                with st.expander("📝 **Principais Atividades**", expanded=False):
                    st.write(row.get('atividades') or "Informações não disponíveis para esta vaga.")

                with st.expander("ℹ️ **Informações Adicionais**", expanded=False):
                    job_info = jobs.get(row['id_vaga'], {})
                    st.markdown(f"**Empresa:** {job_info.get('informacoes_basicas', {}).get('empresa', 'Não informado')}")
                    st.markdown(f"**Nível:** {job_info.get('perfil_vaga', {}).get('nivel', 'Não informado')}")
                    st.markdown(f"**Formação:** {job_info.get('perfil_vaga', {}).get('formacao', 'Não informado')}")
    else:
        st.info("Faça o upload do seu currículo em PDF para descobrir as vagas mais compatíveis com seu perfil.")

# def predicao_1():
#         # Inicialização segura dos estados usados
#     if 'cv_text' not in st.session_state:
#         st.session_state['cv_text'] = ""

#     if 'df_recomendacoes' not in st.session_state:
#         st.session_state['df_recomendacoes'] = pd.DataFrame()
#         # Header moderno
#         with st.container():
#             st.markdown("""
#             <div class="header-container">
#                 <h3 class="header-text"> Encontre as vagas perfeitas com inteligência artificial</h3>
#             </div>
#             """, unsafe_allow_html=True)

#         # Seção de upload
#         with st.container():
#             st.markdown("####  Envie seu currículo")
#             col1, col2 = st.columns([3, 1])
#             with col1:
#                 uploaded_file = st.file_uploader(
#                     "Arraste e solte seu arquivo PDF aqui ou clique para selecionar",
#                     type=["pdf"],
#                     label_visibility="visible"
#                 )
#             with col2:
#                 st.markdown("""
#                 <div style="background-color: #e3f2fd; padding: 1rem; border-radius: 10px;">
#                     <p style="margin: 0; font-size: 0.9rem; color: black;">
#                         📌 <strong>Dica:</strong> Seu currículo deve estar em formato PDF e conter informações claras sobre suas habilidades e experiências.
#                     </p>
#                 </div>
#                 """, unsafe_allow_html=True)

#         if uploaded_file:
#             with st.spinner('Analisando seu currículo...'):
#                 cv_text = extract_text_from_pdf(uploaded_file)

#                 if not cv_text.strip():
#                     st.error("""
#                     <div style="background-color: #ffebee; padding: 1rem; border-left: 5px solid #f44336; border-radius: 5px;">
#                         ⚠️ Não foi possível extrair texto do PDF. Verifique se o arquivo não está vazio ou protegido.
#                     </div>
#                     """, unsafe_allow_html=True)
#                     return

#                 df_recomendacoes = predict_jobs_for_cv(cv_text)

#                 # Salvar em sessão
#                 st.session_state['cv_text'] = cv_text
#                 st.session_state['df_recomendacoes'] = df_recomendacoes

#         # Exibe resultados se já estiverem no session_state
#         if 'df_recomendacoes' in st.session_state:
#             df_recomendacoes = st.session_state['df_recomendacoes']

#             st.markdown("""
#             <div class="success-box">
#                 ✅ Análise concluída com sucesso! Veja abaixo as vagas que melhor se encaixam no seu perfil.
#             </div>
#             """, unsafe_allow_html=True)

#             st.markdown("---")

#             # Métricas resumidas
#             st.markdown("###  Resultados da Análise")
#             col1, col2, col3 = st.columns(3)

#             with col1:
#                 avg_prob = df_recomendacoes["probabilidade_de_contratacao"].mean()
#                 st.markdown("""<div style="background-color: #e3f2fd; padding: 0.5rem 1rem; border-radius: 10px; margin-bottom: 5px;">
#                     <p style="margin: 0; font-size: 0.9rem; color: black;">📈 <strong>Probabilidade Média</strong></p>
#                 </div>""", unsafe_allow_html=True)
#                 st.metric(label="", value=f"{avg_prob:.1%}")

#             with col2:
#                 best_match = df_recomendacoes["similaridade"].max()
#                 st.markdown("""<div style="background-color: #e3f2fd; padding: 0.5rem 1rem; border-radius: 10px; margin-bottom: 5px;">
#                     <p style="margin: 0; font-size: 0.9rem; color: black;">🔍 <strong>Melhor Match</strong></p>
#                 </div>""", unsafe_allow_html=True)
#                 st.metric(label="", value=f"{best_match:.1%}")

#             with col3:
#                 top_area = df_recomendacoes["area"].mode()[0]
#                 st.markdown("""<div style="background-color: #e3f2fd; padding: 0.5rem 1rem; border-radius: 10px; margin-bottom: 5px;">
#                     <p style="margin: 0; font-size: 0.9rem; color: black;">🧭 <strong>Área com Mais Oportunidades</strong></p>
#                 </div>""", unsafe_allow_html=True)
#                 st.metric(label="", value=top_area)

#             style_metric_cards()

#             # Top vagas
#             st.markdown("### 🏆 Vagas Recomendadas")

#             # Formatar dataframe
#             df_display = df_recomendacoes[[
#                 "titulo_da_vaga", "area", "probabilidade_de_contratacao", "similaridade"
#             ]].rename(columns={
#                 "titulo_da_vaga": "Vaga",
#                 "area": "Área",
#                 "probabilidade_de_contratacao": "Probabilidade",
#                 "similaridade": "Match"
#             })

#             # Garante que os dados estão como float
#             df_display["Probabilidade"] = pd.to_numeric(
#                 df_display["Probabilidade"], errors='coerce')
#             df_display["Match"] = pd.to_numeric(
#                 df_display["Match"], errors='coerce')

#             # Exibe sem gradiente de cores
#             st.dataframe(
#                 df_display.style
#                 .format({"Probabilidade": "{:.1%}", "Match": "{:.1%}"})
#                 .set_properties(**{'text-align': 'left'})
#                 .set_table_styles([{
#                     'selector': 'th',
#                     'props': [('background-color', 'var(--primary-color)'),
#                               ('color', 'white'),
#                               ('font-weight', 'bold')]
#                 }]),
#                 use_container_width=True,
#                 height=250
#             )

#             # Detalhes das vagas
#             st.markdown("---")
#             st.markdown("###  Detalhes das Vagas Recomendadas")

#             tabs = st.tabs(
#                 [f"Vaga #{i+1}" for i in range(len(df_recomendacoes))])

#             for idx, (tab, (_, row)) in enumerate(zip(tabs, df_recomendacoes.iterrows())):
#                 with tab:
#                     st.markdown(f"#### {row['titulo_da_vaga']}")

#                     # Barra de progresso para visualização
#                     col_prob, col_sim = st.columns(2)
#                     with col_prob:
#                         st.progress(
#                             int(row['probabilidade_de_contratacao'] * 100))
#                         st.caption(
#                             f"Probabilidade: {row['probabilidade_de_contratacao']:.1%}")

#                     with col_sim:
#                         st.progress(int(row['similaridade'] * 100))
#                         st.caption(f"Match: {row['similaridade']:.1%}")

#                     st.markdown("---")

#                     # Layout em colunas para informações básicas
#                     col_info1, col_info2 = st.columns(2)
#                     with col_info1:
#                         st.markdown(f"**Área:** {row['area']}")
#                         st.markdown(f"**ID da Vaga:** `{row['id_vaga']}`")

#                     with col_info2:
#                         st.markdown(
#                             f"**Localização:** {jobs.get(row['id_vaga'], {}).get('informacoes_basicas', {}).get('local_de_trabalho', 'Não informado')}")
#                         st.markdown(
#                             f"**Tipo de Contratação:** {jobs.get(row['id_vaga'], {}).get('informacoes_basicas', {}).get('tipo_de_contratacao', 'Não informado')}")

#                     # Seções expansíveis
#                     with st.expander("🛠 **Habilidades Requeridas**", expanded=False):
#                         st.write(row['habilidades'] if row['habilidades'] !=
#                                  "Não informado" else "Informações não disponíveis para esta vaga.")

#                     with st.expander("📝 **Principais Atividades**", expanded=False):
#                         st.write(row['atividades'] if row['atividades'] !=
#                                  "Não informado" else "Informações não disponíveis para esta vaga.")

#                     with st.expander("ℹ️ **Informações Adicionais**", expanded=False):
#                         job_info = jobs.get(row['id_vaga'], {})
#                         st.markdown(
#                             f"**Empresa:** {job_info.get('informacoes_basicas', {}).get('empresa', 'Não informado')}")
#                         st.markdown(
#                             f"**Nível:** {job_info.get('perfil_vaga', {}).get('nivel', 'Não informado')}")
#                         st.markdown(
#                             f"**Formação:** {job_info.get('perfil_vaga', {}).get('formacao', 'Não informado')}")
