import streamlit as st
import pandas as pd

def recomendacao_07(candidatos_df: pd.DataFrame):
    st.subheader(" Recomendação e Insights Inteligentes")

    try:
        if 'remuneracao' not in candidatos_df.columns:
            st.error("Erro: Coluna 'remuneracao' não encontrada nos dados.")
            return

        if candidatos_df.empty:
            st.warning("Não há dados suficientes para gerar recomendações.")
            return

        st.markdown("###  Perfis por Cluster")

        agg_dict = {
            'remuneracao': 'mean',
            'nivel_academico': lambda x: x.mode()[0] if not x.mode().empty else 'Não informado',
            'nivel_ingles': lambda x: x.mode()[0] if not x.mode().empty else 'Não informado'
        }

        cluster_summary = candidatos_df.groupby('cluster').agg(agg_dict).reset_index()

        cluster_summary['Remuneração Média'] = cluster_summary['remuneracao'].apply(
            lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        st.dataframe(
            cluster_summary[[
                'cluster', 'Remuneração Média', 'nivel_academico', 'nivel_ingles'
            ]].rename(columns={
                'cluster': 'Cluster',
                'nivel_academico': 'Nível Acadêmico Mais Comum',
                'nivel_ingles': 'Inglês Mais Comum'
            })
        )

        st.markdown("###  Análise dos Clusters")

        if 'remuneracao' in cluster_summary.columns:
            top_cluster = cluster_summary.loc[cluster_summary['remuneracao'].idxmax()]
            recomendacoes = []

            recomendacoes.append(
                f"- **Cluster {int(top_cluster['cluster'])}** possui a maior remuneração média "
                f"({top_cluster['Remuneração Média']})"
            )

            if 'nivel_academico' in top_cluster:
                recomendacoes[-1] += f", predominantemente com **{top_cluster['nivel_academico']}**"
            if 'nivel_ingles' in top_cluster:
                recomendacoes[-1] += f" e inglês **{top_cluster['nivel_ingles']}**"

            for _, row in cluster_summary.iterrows():
                if row['cluster'] != top_cluster['cluster']:
                    diff = top_cluster['remuneracao'] - row['remuneracao']
                    diff_percent = (diff / row['remuneracao']) * 100 if row['remuneracao'] > 0 else 0
                    recomendacoes.append(
                        f"- Cluster {int(row['cluster'])} ganha em média **{diff_percent:.1f}% menos**"
                    )

            st.markdown("### ✅ Recomendações Estratégicas")
            for rec in recomendacoes:
                st.markdown(rec)

            st.markdown("""
            - **Priorize candidatos** do cluster com maior remuneração média para posições estratégicas
            - **Invista em treinamento** de idiomas para candidatos promissores de clusters com menor remuneração
            - **Considere o nível acadêmico** como critério de qualificação
            """)

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar os dados: {str(e)}")