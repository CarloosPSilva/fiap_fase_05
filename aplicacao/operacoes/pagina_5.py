import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import numpy as np
import re

from aplicacao.utils.preparar_candidatos_df import limpar_remuneracao, preparar_candidatos_df


@st.cache_data(show_spinner="Executando clusterização...")
def clusterizar_candidatos(prospects_json, applicants_json):

    # Preparar dataframe de prospects
    lista_prospects = []
    for vaga_id, vaga_info in prospects_json.items():
        titulo = vaga_info.get("titulo", "")
        modalidade = vaga_info.get("modalidade", "")
        for prospect in vaga_info.get("prospects", []):
            prospect['titulo_vaga'] = titulo
            prospect['modalidade'] = modalidade
            lista_prospects.append(prospect)

    prospects_df = pd.DataFrame(lista_prospects)

    aprovados = [
        "Aprovado",
        "Contratado como Hunting",
        "Contratado pela Decision",
        "Proposta Aceita"
    ]
    prospects_df['situacao_candidado_agrupado'] = prospects_df['situacao_candidado'].apply(
        lambda x: "Aprovado" if x in aprovados else x
    )

    lista_applicants = []
    for codigo, dados in applicants_json.items():
        # Remover valores vazios ou "Não informado" antes de criar o dicionário
        infos_basicas = {
            k: v for k, v in dados['infos_basicas'].items() if v and v != "Não informado"}
        formacao = {k: v for k, v in dados['formacao_e_idiomas'].items(
        ) if v and v != "Não informado"}
        profissionais = {k: v for k, v in dados['informacoes_profissionais'].items(
        ) if v and v != "Não informado"}

        base = {
            'codigo': infos_basicas.get('codigo_profissional', ''),
            'nome': infos_basicas.get('nome', ''),
            'email': infos_basicas.get('email', ''),
            'local': infos_basicas.get('local', ''),
            'nivel_academico': formacao.get('nivel_academico', ''),
            'nivel_ingles': formacao.get('nivel_ingles', ''),
            'nivel_espanhol': formacao.get('nivel_espanhol', ''),
            'remuneracao': profissionais.get('remuneracao', ''),
            'area_atuacao': profissionais.get('area_atuacao', ''),
            'dados_completos': dados
        }
        # Remover valores vazios do dicionário base
        base = {k: v for k, v in base.items() if v or k == 'codigo'}
        lista_applicants.append(base)

    applicants_df = pd.DataFrame(lista_applicants)
    MAX_REGISTROS = 500
    if len(applicants_df) > MAX_REGISTROS:
        applicants_df = applicants_df.sample(n=MAX_REGISTROS, random_state=42).reset_index(drop=True)

    # Processamento de remuneração
    applicants_df['remuneracao_limpa'] = applicants_df['remuneracao'].apply(
        limpar_remuneracao)
    applicants_df['remuneracao_limpa'] = pd.to_numeric(
        applicants_df['remuneracao_limpa'], errors='coerce')

    # Remover linhas com valores ausentes críticos para a clusterização
    applicants_df = applicants_df.dropna(
        subset=['nivel_academico', 'nivel_ingles', 'nivel_espanhol'])

    # Preencher remuneração ausente apenas para candidatos com outros dados completos
    mediana_salario = applicants_df['remuneracao_limpa'].median()
    applicants_df['remuneracao_limpa'] = applicants_df['remuneracao_limpa'].fillna(
        mediana_salario)

    applicants_df['remuneracao_formatada'] = applicants_df['remuneracao_limpa'].apply(
        lambda x: f"R$ {x:,.2f}".replace(
            ",", "X").replace(".", ",").replace("X", ".")
    )

    applicants_df['remuneracao'] = applicants_df['remuneracao_limpa'].astype(
        float)
    applicants_df = applicants_df.drop('remuneracao_limpa', axis=1)

    # Usar inner join para manter apenas candidatos com dados completos
    candidatos_df = pd.merge(
        prospects_df, applicants_df, on='codigo', how='inner')

    # Clusterização
    df_cluster = candidatos_df[['codigo', 'nivel_academico',
                                'nivel_ingles', 'nivel_espanhol', 'remuneracao']].copy()

    # Remover linhas com valores ausentes (já tratado anteriormente, mas garantindo)
    df_cluster = df_cluster.dropna()

    # Criar dummies apenas para valores existentes
    df_dummies = pd.get_dummies(df_cluster.drop(
        columns=['codigo', 'remuneracao']))
    df_final = pd.concat([df_dummies, df_cluster[['remuneracao']]], axis=1)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_final)

    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    df_cluster['cluster'] = clusters

    candidatos_df = candidatos_df.merge(
        df_cluster[['codigo', 'cluster']], on='codigo', how='left')

    return candidatos_df


def clusterizacao_perfil_05(prospects_json, applicants_json):
    candidatos_df = clusterizar_candidatos(prospects_json, applicants_json)

    st.title("Painel Clusterização de Perfis de Candidatos")
    st.markdown("**Observação:** Apenas candidatos com informações completas foram considerados na análise.")

    # 🔒 Limitar amostra de dados para performance
    MAX_REGISTROS = 500
    if len(candidatos_df) > MAX_REGISTROS:
        candidatos_df = candidatos_df.sample(n=MAX_REGISTROS, random_state=42).reset_index(drop=True)
        st.info(f"Atenção: foram carregados apenas {MAX_REGISTROS} candidatos de um total maior, para otimizar a performance.")

    # Redução de dimensionalidade com PCA
    df_cluster = candidatos_df[['codigo', 'nivel_academico',
                                'nivel_ingles', 'nivel_espanhol', 'remuneracao', 'cluster']].dropna()

    # Dummies e PCA
    df_dummies = pd.get_dummies(df_cluster.drop(columns=['codigo', 'remuneracao', 'cluster']))
    df_final = pd.concat([df_dummies, df_cluster[['remuneracao']]], axis=1)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_final)

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    df_plot = pd.DataFrame({
        'PC1': X_pca[:, 0],
        'PC2': X_pca[:, 1],
        'cluster': df_cluster['cluster'].astype(str),
        'codigo': df_cluster['codigo'],
        'remuneracao': df_cluster['remuneracao'].apply(
            lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
        'nivel_academico': df_cluster['nivel_academico']
    })

    fig = px.scatter(
        df_plot, x='PC1', y='PC2',
        color='cluster',
        title="Clusters de Candidatos - Redução PCA",
        labels={'cluster': 'Cluster'},
        hover_data=['codigo', 'remuneracao', 'nivel_academico'],
        symbol='nivel_academico'
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Distribuição de Candidatos por Cluster")
    cluster_counts = df_cluster['cluster'].value_counts().reset_index()
    cluster_counts.columns = ['Cluster', 'Quantidade']
    st.dataframe(cluster_counts)

    st.markdown("### Características Médias por Cluster")
    cluster_stats = df_cluster.groupby('cluster').agg({
        'remuneracao': 'mean',
        'nivel_academico': lambda x: x.mode()[0] if not x.empty else None,
        'nivel_ingles': lambda x: x.mode()[0] if not x.empty else None,
        'nivel_espanhol': lambda x: x.mode()[0] if not x.empty else None
    }).reset_index()

    cluster_stats['Remuneração Média'] = cluster_stats['remuneracao'].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.dataframe(cluster_stats[['cluster', 'Remuneração Média', 'nivel_academico', 'nivel_ingles', 'nivel_espanhol']]
        .rename(columns={
            'cluster': 'Cluster',
            'nivel_academico': 'Nível Acadêmico',
            'nivel_ingles': 'Inglês',
            'nivel_espanhol': 'Espanhol'
        })
    )

    st.markdown("### Detalhes dos Candidatos por Cluster (máx. 100 exibidos)")
    st.caption("A tabela abaixo exibe apenas os primeiros 100 registros da amostra utilizada.")
    st.dataframe(df_cluster[['codigo', 'nivel_academico', 'nivel_ingles', 'nivel_espanhol', 'remuneracao', 'cluster']]
        .rename(columns={
            'codigo': 'Código',
            'nivel_academico': 'Nível Acadêmico',
            'nivel_ingles': 'Inglês',
            'nivel_espanhol': 'Espanhol',
            'remuneracao': 'Remuneração',
            'cluster': 'Cluster'
        }).head(100)
    )