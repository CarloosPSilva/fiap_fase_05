import streamlit as st

def visao_geral_02():
    st.title(" Visão Geral do Projeto")

    def styled_subheader(titulo):
        st.markdown(
            f"""<h3 style="margin-top: 1.5em; margin-bottom: 0.5em; font-weight: bold; color: #003366; text-align: left;">{titulo}</h3>""",
            unsafe_allow_html=True
        )
    st.markdown("""
    ---
    """)
    styled_subheader("Objetivo do Projeto")
    st.markdown("""
    Este projeto tem como objetivo aplicar **Inteligência Artificial** para **otimizar o processo de recrutamento** da empresa **Decision**.

    A proposta consiste em:
    - Identificar os perfis com maior chance de aprovação
    - Fornecer recomendações personalizadas de vagas com base no currículo
    - Explorar padrões e agrupamentos nos perfis de candidatos e vagas

    ---
    """)

    styled_subheader("Estratégia da Solução")
    st.markdown("""
    A solução foi dividida em duas frentes principais:
    - **Predição de Aprovação (Página 1):** o usuário envia seu currículo em PDF, e o sistema recomenda as 5 vagas com maior similaridade e probabilidade de contratação.
    - **Exploração dos Dados Históricos (Páginas 2 a 4):** análise das vagas, candidatos, clusters e recomendações com base no histórico de contratações.

    ---
    """)

    styled_subheader("Bases de Dados Utilizadas")
    st.markdown("""
    Os dados utilizados são amostras fornecidas pela Decision:
    - `vagas.json`: Informações detalhadas sobre cada vaga
    - `prospects.json`: Candidatos encaminhados por vaga
    - `applicants.json`: Perfil completo dos candidatos (formação, idiomas, skills, localidade, remuneração)

   ---
    """)

    styled_subheader("Tecnologias e Modelos")
    st.markdown("""
    - **Streamlit:** Interface interativa do MVP
    - **Pandas & JSON:** Tratamento e exploração dos dados
    - **Sentence Transformers:** Embeddings dos currículos e das vagas
    - **XGBoost + Regressão Logística:** Modelo de ensemble para predição de aprovação
    - **Scikit-learn + Plotly:** Análise estatística, clusterização e visualizações

    ---
    """
    )

    styled_subheader("Como Navegar no MVP")
    st.markdown("""
    Use o menu lateral para explorar cada parte do MVP:

    - **Página 1:** Envie seu currículo em PDF e veja as vagas mais compatíveis com base em IA
    - **Página 2:** Visão geral estatística das vagas
    - **Página 3:** Perfil dos candidatos recebidos
    - **Página 4:** Recomendação e insights baseados no histórico de aprovações

    ---
    Desenvolvido com foco em aplicabilidade real e geração de valor para recrutamento inteligente.
    """)