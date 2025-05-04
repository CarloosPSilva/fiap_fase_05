
import streamlit as st
import pandas as pd

from aplicacao.operacoes.pagina_5 import clusterizar_candidatos


def recomendacao_07(prospects_json, applicants_json):
    st.subheader(" Recomendação e Insights Inteligentes")

    try:
        # Utiliza a função de clusterização já existente
        candidatos_df = clusterizar_candidatos(prospects_json, applicants_json)

        # Verificar se a coluna 'remuneracao' existe no DataFrame
        if 'remuneracao' not in candidatos_df.columns:
            st.error("Erro: Coluna 'remuneracao' não encontrada nos dados.")
            return

        # Verificar se há dados suficientes para análise
        if candidatos_df.empty:
            st.warning("Não há dados suficientes para gerar recomendações.")
            return

        # Tabela resumo dos clusters
        st.markdown("###  Perfis por Cluster")

        # Criar dataframe de resumo dos clusters com verificação de colunas
        agg_dict = {}
        if 'nivel_academico' in candidatos_df.columns:
            agg_dict['nivel_academico'] = lambda x: x.mode(
            )[0] if not x.mode().empty else 'Não informado'
        if 'nivel_ingles' in candidatos_df.columns:
            agg_dict['nivel_ingles'] = lambda x: x.mode(
            )[0] if not x.mode().empty else 'Não informado'
        if 'remuneracao' in candidatos_df.columns:
            agg_dict['remuneracao'] = 'mean'

        cluster_summary = candidatos_df.groupby(
            'cluster').agg(agg_dict).reset_index()

        # Renomear colunas para exibição
        display_columns = []
        if 'cluster' in cluster_summary.columns:
            display_columns.append('cluster')
        if 'nivel_academico' in cluster_summary.columns:
            cluster_summary = cluster_summary.rename(
                columns={'nivel_academico': 'Nível Acadêmico Mais Comum'})
            display_columns.append('Nível Acadêmico Mais Comum')
        if 'nivel_ingles' in cluster_summary.columns:
            cluster_summary = cluster_summary.rename(
                columns={'nivel_ingles': 'Inglês Mais Comum'})
            display_columns.append('Inglês Mais Comum')
        if 'remuneracao' in cluster_summary.columns:
            # Formatar a remuneração
            cluster_summary['Remuneração Média'] = cluster_summary['remuneracao'].apply(
                lambda x: f"R$ {x:,.2f}".replace(
                    ",", "X").replace(".", ",").replace("X", ".")
            )
            display_columns.append('Remuneração Média')

        # Exibir tabela formatada apenas com colunas disponíveis
        st.dataframe(cluster_summary[display_columns]
                     .rename(columns={'cluster': 'Cluster'}))

        # Análise dos clusters para gerar recomendações
        st.markdown("###  Análise dos Clusters")

        # Verificar se temos dados de remuneração para análise
        if 'remuneracao' in cluster_summary.columns:
            # Identificar o cluster com maior remuneração
            top_cluster = cluster_summary.loc[cluster_summary['remuneracao'].idxmax(
            )]

            # Gerar recomendações baseadas nos dados
            recomendacoes = []

            recomendacoes.append(
                f"- **Cluster {int(top_cluster['cluster'])}** possui a maior remuneração média "
                f"({top_cluster['Remuneração Média']})"
            )

            # Adicionar informações acadêmicas se disponíveis
            if 'Nível Acadêmico Mais Comum' in top_cluster:
                recomendacoes[-1] += f" e é composto principalmente por candidatos com " \
                    f"**{top_cluster['Nível Acadêmico Mais Comum']}**"

            # Adicionar informações de idioma se disponíveis
            if 'Inglês Mais Comum' in top_cluster:
                recomendacoes[-1] += f" e nível de inglês **{top_cluster['Inglês Mais Comum']}**"

            # Comparar clusters
            for _, row in cluster_summary.iterrows():
                if row['cluster'] != top_cluster['cluster'] and 'remuneracao' in row:
                    diff = top_cluster['remuneracao'] - row['remuneracao']
                    diff_percent = (
                        diff / row['remuneracao']) * 100 if row['remuneracao'] > 0 else 0

                    recomendacoes.append(
                        f"- Candidatos no **Cluster {int(row['cluster'])}** ganham em média "
                        f"**{diff_percent:.1f}% menos** que os do Cluster {int(top_cluster['cluster'])}"
                    )

            # Recomendações estratégicas
            st.markdown("### ✅ Recomendações Estratégicas")

            if recomendacoes:
                for rec in recomendacoes:
                    st.markdown(rec)

                st.markdown("""
                - **Priorize candidatos** do cluster com maior remuneração média para posições estratégicas
                - **Invista em treinamento** de idiomas para candidatos promissores de clusters com menor remuneração
                - **Considere o nível acadêmico** como um diferencial importante para cargos mais bem remunerados
                """)
            else:
                st.warning(
                    "Não foi possível gerar recomendações com base nos dados disponíveis.")
        else:
            st.warning(
                "Dados de remuneração não disponíveis para análise comparativa.")

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar os dados: {str(e)}")
