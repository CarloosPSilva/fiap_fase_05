import streamlit as st
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards


def analise_vaga_03(vagas_df):
    # Configuração do layout da página
    # st.set_page_config(layout="wide")

    # Título e introdução
    st.title("Painel de Análise de Vagas")
    st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        border-radius: 0.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .css-1v0mbdj {
        border-radius: 0.5rem;
    }

    </style>
    """, unsafe_allow_html=True)

    # Seção de filtros com layout expandido
    with st.expander(" Filtros Avançados", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            cliente = st.selectbox(
                "Selecione o Cliente",
                vagas_df['informacoes_basicas_cliente'].dropna().unique(),
                key="cliente_vagas"
            )

        with col2:
            tipo_contratacao = st.selectbox(
                "Tipo de Contratação",
                vagas_df['informacoes_basicas_tipo_contratacao'].dropna().unique(),
                key="tipo_contratacao_vagas"
            )

    # Aplicar filtros
    vagas_filtradas = vagas_df[
        (vagas_df['informacoes_basicas_cliente'] == cliente) &
        (vagas_df['informacoes_basicas_tipo_contratacao'] == tipo_contratacao)
    ]

    # Métricas resumidas
    st.markdown("###  Visão Geral")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total de Vagas",
            value=len(vagas_filtradas),
            delta=f"{len(vagas_filtradas)/len(vagas_df)*100:.1f}% do total"
        )

    with col2:
        nivel_mais_comum = vagas_filtradas['perfil_vaga_nivel_profissional'].mode()[0] \
            if not vagas_filtradas['perfil_vaga_nivel_profissional'].empty else "N/A"
        st.metric(
            label="Nível Profissional Mais Comum",
            value=nivel_mais_comum
        )

    with col3:
        estado_mais_comum = vagas_filtradas['perfil_vaga_estado'].mode()[0] \
            if not vagas_filtradas['perfil_vaga_estado'].empty else "N/A"
        st.metric(
            label="Estado Mais Comum",
            value=estado_mais_comum
        )

    style_metric_cards()

    # Seção de visualização de dados
    st.markdown("### 📋 Detalhes das Vagas")
    st.dataframe(
        vagas_filtradas[[
            'informacoes_basicas_titulo_vaga',
            'perfil_vaga_nivel_profissional',
            'perfil_vaga_estado',
            'perfil_vaga_nivel_ingles',
            'perfil_vaga_areas_atuacao'
        ]].rename(columns={
            'informacoes_basicas_titulo_vaga': 'Vaga',
            'perfil_vaga_nivel_profissional': 'Nível',
            'perfil_vaga_estado': 'Estado',
            'perfil_vaga_nivel_ingles': 'Inglês',
            'perfil_vaga_areas_atuacao': 'Áreas de Atuação'
        }),
        height=400,
        use_container_width=True
    )

    # Visualizações gráficas
    st.markdown("###  Análises Gráficas")
    tab1, tab2, tab3 = st.tabs(
        ["Distribuição por Estado", "Nível de Inglês", "Áreas de Atuação"])

    with tab1:
        estado_df = vagas_filtradas['perfil_vaga_estado'].value_counts(
        ).reset_index()
        estado_df.columns = ['estado', 'quantidade']

        fig_estado = px.bar(
            estado_df,
            x='estado', y='quantidade',
            labels={'estado': 'Estado', 'quantidade': 'Quantidade de Vagas'},
            title='Distribuição Geográfica das Vagas',
            color='estado',
            template='plotly_white'
        )
        fig_estado.update_layout(showlegend=False)
        st.plotly_chart(fig_estado, use_container_width=True)

    with tab2:
        ingles_df = vagas_filtradas['perfil_vaga_nivel_ingles'].value_counts(
        ).reset_index()
        ingles_df.columns = ['nivel_ingles', 'quantidade']

        fig_ingles = px.pie(
            ingles_df,
            names='nivel_ingles', values='quantidade',
            title='Distribuição por Nível de Inglês',
            hole=0.3,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_ingles, use_container_width=True)

    with tab3:
        areas_df = vagas_filtradas['perfil_vaga_areas_atuacao'].value_counts(
        ).reset_index()
        areas_df.columns = ['area', 'quantidade']

        fig_areas = px.treemap(
            areas_df,
            path=['area'], values='quantidade',
            title='Áreas de Atuação Mais Demandadas',
            color='quantidade',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_areas, use_container_width=True)
