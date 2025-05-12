import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards


def analise_candidato_04(prospects_json):

    st.title(" Painel de Análise de Candidatos")


    # Processamento dos dados
    lista_prospects = []
    for vaga_id, vaga_info in prospects_json.items():
        titulo = vaga_info.get("titulo", "")
        modalidade = vaga_info.get("modalidade", "")
        for prospect in vaga_info.get("prospects", []):
            prospect['titulo_vaga'] = titulo
            prospect['modalidade'] = modalidade
            lista_prospects.append(prospect)

    prospects_df = pd.DataFrame(lista_prospects)

    # Agrupar status de aprovação
    aprovados = [
        "Aprovado",
        "Contratado como Hunting",
        "Contratado pela Decision",
        "Proposta Aceita"
    ]
    prospects_df['situacao_candidado_agrupado'] = prospects_df['situacao_candidado'].apply(
        lambda x: "Aprovado" if x in aprovados else x
    )

    # Métricas resumidas
    st.markdown("### Visão Geral")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total de Candidatos",
            value=len(prospects_df),
            help="Número total de candidatos no sistema"
        )

    with col2:
        aprovados_count = len(
            prospects_df[prospects_df['situacao_candidado_agrupado'] == "Aprovado"])
        st.metric(
            label="Candidatos Aprovados",
            value=aprovados_count,
            delta=f"{aprovados_count/len(prospects_df)*100:.1f}% do total"
        )

    with col3:
        recrutador_top = prospects_df['recrutador'].mode(
        )[0] if not prospects_df['recrutador'].empty else "N/A"
        st.metric(
            label="Recrutador com Mais Candidatos",
            value=recrutador_top
        )

    style_metric_cards()

    # Filtros interativos
    with st.expander("Filtros Avançados", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            situacao_filtro = st.multiselect(
                "Situação do Candidato",
                prospects_df['situacao_candidado_agrupado'].unique(),
                default=["Aprovado"]
            )

        with col2:
            recrutador_filtro = st.multiselect(
                "Recrutador",
                prospects_df['recrutador'].unique()
            )

        with col3:
            vaga_filtro = st.multiselect(
                "Título da Vaga",
                prospects_df['titulo_vaga'].unique()
            )

    # Aplicar filtros
    filtered_df = prospects_df.copy()
    if situacao_filtro:
        filtered_df = filtered_df[filtered_df['situacao_candidado_agrupado'].isin(
            situacao_filtro)]
    if recrutador_filtro:
        filtered_df = filtered_df[filtered_df['recrutador'].isin(
            recrutador_filtro)]
    if vaga_filtro:
        filtered_df = filtered_df[filtered_df['titulo_vaga'].isin(vaga_filtro)]

    # Tabela de candidatos
    st.markdown("###  Lista de Candidatos")
    st.dataframe(
        filtered_df[[
            'nome', 'codigo', 'situacao_candidado',
            'data_candidatura', 'recrutador', 'titulo_vaga'
        ]].rename(columns={
            'nome': 'Nome',
            'codigo': 'Código',
            'situacao_candidado': 'Situação',
            'data_candidatura': 'Data Candidatura',
            'recrutador': 'Recrutador',
            'titulo_vaga': 'Vaga'
        }),
        height=400,
        use_container_width=True,
        hide_index=True
    )

    # Visualizações gráficas
    st.markdown("###  Análises Gráficas")
    tab1, tab2, tab3 = st.tabs(
        ["Status dos Candidatos", "Distribuição por Recrutador", "Evolução Temporal"])

    with tab1:
        status_df = filtered_df['situacao_candidado_agrupado'].value_counts(
        ).reset_index()
        status_df.columns = ['situacao', 'quantidade']

        fig_status = px.pie(
            status_df,
            names='situacao', values='quantidade',
            title='Distribuição por Status dos Candidatos',
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with tab2:
        recrutador_df = filtered_df['recrutador'].value_counts().reset_index()
        recrutador_df.columns = ['recrutador', 'quantidade']

        fig_recrutador = px.bar(
            recrutador_df,
            x='recrutador', y='quantidade',
            labels={'recrutador': 'Recrutador',
                    'quantidade': 'Número de Candidatos'},
            title='Distribuição por Recrutador',
            color='recrutador'
        )
        fig_recrutador.update_layout(showlegend=False)
        st.plotly_chart(fig_recrutador, use_container_width=True)

    with tab3:
        if not filtered_df.empty and 'data_candidatura' in filtered_df.columns:
            filtered_df['data_candidatura'] = pd.to_datetime(
                filtered_df['data_candidatura'], errors='coerce')
            temporal_df = filtered_df.set_index(
                'data_candidatura').resample('M').size().reset_index()
            temporal_df.columns = ['data', 'quantidade']

            fig_temporal = px.line(
                temporal_df,
                x='data', y='quantidade',
                labels={'data': 'Data', 'quantidade': 'Novos Candidatos'},
                title='Evolução Mensal de Candidaturas',
                markers=True
            )
            st.plotly_chart(fig_temporal, use_container_width=True)
        else:
            st.warning("Dados temporais insuficientes para análise")
