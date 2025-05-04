import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import numpy as np
import re

from aplicacao.utils.preparar_candidatos_df import preparar_candidatos_df


@st.cache_data(show_spinner="Executando clusterização...")
def clusterizar_candidatos(prospects_json, applicants_json):
    _, _, candidatos_df = preparar_candidatos_df(prospects_json, applicants_json)

    # ✅ Filtrar candidatos com dados genéricos
    candidatos_df = candidatos_df[
        (candidatos_df['nivel_academico'] != 'Não informado') &
        (candidatos_df['nivel_ingles'] != 'Nenhum') &
        (candidatos_df['nivel_espanhol'] != 'Nenhum')
    ]

    # 🔒 Limitar amostragem para não sobrecarregar
    MAX_REGISTROS = 100
    if len(candidatos_df) > MAX_REGISTROS:
        candidatos_df = candidatos_df.sample(n=MAX_REGISTROS, random_state=42).reset_index(drop=True)

    # Clusterização
    df_cluster = candidatos_df[['codigo', 'nivel_academico',
                                'nivel_ingles', 'nivel_espanhol', 'remuneracao']].copy().dropna()

    df_dummies = pd.get_dummies(df_cluster.drop(columns=['codigo', 'remuneracao']))
    df_final = pd.concat([df_dummies, df_cluster[['remuneracao']]], axis=1)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_final)

    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    df_cluster['cluster'] = clusters

    candidatos_df = candidatos_df.merge(df_cluster[['codigo', 'cluster']], on='codigo', how='left')

    # Libera variáveis intermediárias (opcional)
    del df_cluster, df_dummies, df_final, X_scaled

    return candidatos_df

def clusterizacao_perfil_05(prospects_json, applicants_json):
    candidatos_df = clusterizar_candidatos(prospects_json, applicants_json)

    st.title("Painel Clusterização de Perfis de Candidatos")
    st.markdown("**Observação:** Apenas candidatos com informações completas foram considerados na análise.")

    # 🔒 Limitar amostra de dados para performance
    MAX_REGISTROS = 100
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