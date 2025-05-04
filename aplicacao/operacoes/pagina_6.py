import streamlit as st
import pandas as pd
from datetime import datetime


def formatar_data(data_str):
    """Formata datas para o padrão brasileiro"""
    try:
        if data_str and data_str != "0000-00-00":
            if " " in data_str:  # Se contiver hora
                return datetime.strptime(data_str.split(" ")[0], "%d-%m-%Y").strftime("%d/%m/%Y")
            return datetime.strptime(data_str, "%d-%m-%Y").strftime("%d/%m/%Y")
        return "Não informado"
    except:
        return data_str


def formatar_telefone(telefone):
    """Formata números de telefone"""
    if not telefone:
        return "Não informado"
    return telefone


def criar_secao_curriculo(curriculo_texto):
    """Organiza o currículo em seções temáticas"""
    linhas = [linha.strip()
              for linha in curriculo_texto.strip().split("\n") if linha.strip()]

    secoes = {
        'resumo': [],
        'formacao': [],
        'experiencia': [],
        'habilidades': [],
        'outros': []
    }

    for linha in linhas:
        linha_lower = linha.lower()
        if any(palavra in linha_lower for palavra in ["resumo", "perfil", "objetivo", "solteiro", "casado", "brasileiro"]):
            secoes['resumo'].append(linha)
        elif any(palavra in linha_lower for palavra in ["formação", "acadêmica", "graduação", "mba", "ensino", "curso", "fatec", "faculdade"]):
            secoes['formacao'].append(linha)
        elif any(palavra in linha_lower for palavra in ["experiência", "profissional", "empresa", "cargo", "atividades", "histórico"]):
            secoes['experiencia'].append(linha)
        elif any(palavra in linha_lower for palavra in ["habilidades", "competências", "skills", "ferramentas", "conhecimento"]):
            secoes['habilidades'].append(linha)
        else:
            secoes['outros'].append(linha)

    return secoes


def processar_prospects(prospects_json):
    """Processa os dados de prospects e retorna um DataFrame"""
    lista_prospects = []
    for vaga_id, vaga_info in prospects_json.items():
        titulo = vaga_info.get("titulo", "Vaga sem título")
        modalidade = vaga_info.get("modalidade", "Não informado")
        for prospect in vaga_info.get("prospects", []):
            prospect['titulo_vaga'] = titulo
            prospect['modalidade'] = modalidade
            prospect['vaga_id'] = vaga_id
            lista_prospects.append(prospect)
    return pd.DataFrame(lista_prospects)


def exibir_informacoes_pessoais(candidato):
    """Exibe as informações pessoais em um layout organizado"""
    with st.expander("📋 Informações Pessoais", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"**📅 Data de Nascimento:** {formatar_data(candidato['informacoes_pessoais'].get('data_nascimento', ''))}")
            st.markdown(
                f"**👤 Sexo:** {candidato['informacoes_pessoais'].get('sexo', 'Não informado')}")
            st.markdown(
                f"**💍 Estado Civil:** {candidato['informacoes_pessoais'].get('estado_civil', 'Não informado')}")
            st.markdown(
                f"**♿ PCD:** {candidato['informacoes_pessoais'].get('pcd', 'Não informado')}")

        with col2:
            st.markdown(
                f"**📱 Telefone:** {formatar_telefone(candidato['infos_basicas'].get('telefone', ''))}")
            st.markdown(
                f"**📞 Telefone Recado:** {formatar_telefone(candidato['informacoes_pessoais'].get('telefone_recado', ''))}")
            st.markdown(
                f"**📧 Email Secundário:** {candidato['informacoes_pessoais'].get('email_secundario', 'Não informado')}")
            st.markdown(
                f"**🏠 Endereço:** {candidato['informacoes_pessoais'].get('endereco', 'Não informado')}")

        st.markdown("**🔗 LinkedIn:** " + (f"[Link]({candidato['informacoes_pessoais'].get('url_linkedin', '')})"
                    if candidato['informacoes_pessoais'].get('url_linkedin') else "Não informado"))


def exibir_informacoes_profissionais(candidato):
    """Exibe as informações profissionais"""
    with st.expander("💼 Informações Profissionais", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"**🎯 Objetivo Profissional:** {candidato['infos_basicas'].get('objetivo_profissional', 'Não informado')}")
            st.markdown(
                f"**🏆 Título Profissional:** {candidato['informacoes_profissionais'].get('titulo_profissional', 'Não informado')}")
            st.markdown(
                f"**📌 Área de Atuação:** {candidato['informacoes_profissionais'].get('area_atuacao', 'Não informado')}")

        with col2:
            st.markdown(
                f"**💰 Pretensão Salarial:** R$ {candidato['informacoes_profissionais'].get('remuneracao', 'Não informado')}")
            st.markdown(
                f"**📊 Nível Profissional:** {candidato['informacoes_profissionais'].get('nivel_profissional', 'Não informado')}")

        st.markdown("---")
        st.markdown("**📜 Conhecimentos Técnicos:**")
        st.text(candidato['informacoes_profissionais'].get(
            'conhecimentos_tecnicos', 'Não informado'))

        st.markdown("**🏅 Certificações:**")
        certs = candidato['informacoes_profissionais'].get(
            'certificacoes', 'Não informado')
        if certs and certs != "Não informado":
            for cert in certs.split(", "):
                st.markdown(f"- {cert}")
        else:
            st.text(certs)


def exibir_formacao_idiomas(candidato):
    """Exibe informações de formação e idiomas"""
    with st.expander("🎓 Formação e Idiomas", expanded=False):
        st.markdown(
            f"**📚 Nível Acadêmico:** {candidato['formacao_e_idiomas'].get('nivel_academico', 'Não informado')}")

        if 'instituicao_ensino_superior' in candidato['formacao_e_idiomas']:
            st.markdown(
                f"**🏫 Instituição de Ensino Superior:** {candidato['formacao_e_idiomas'].get('instituicao_ensino_superior', 'Não informado')}")
            st.markdown(
                f"**📖 Curso:** {candidato['formacao_e_idiomas'].get('cursos', 'Não informado')}")
            st.markdown(
                f"**🎓 Ano de Conclusão:** {candidato['formacao_e_idiomas'].get('ano_conclusao', 'Não informado')}")

        st.markdown("---")
        st.markdown("**🌍 Idiomas:**")
        st.markdown(
            f"- Inglês: {candidato['formacao_e_idiomas'].get('nivel_ingles', 'Não informado')}")
        st.markdown(
            f"- Espanhol: {candidato['formacao_e_idiomas'].get('nivel_espanhol', 'Não informado')}")
        st.markdown(
            f"- Outros: {candidato['formacao_e_idiomas'].get('outro_idioma', 'Não informado')}")


def exibir_curriculo(candidato):
    """Exibe o currículo formatado"""
    with st.expander("📄 Currículo Completo", expanded=False):
        tab1, tab2 = st.tabs(["📋 Visualização Organizada", "📜 Texto Completo"])

        with tab1:
            curriculo_formatado = criar_secao_curriculo(candidato['cv_pt'])

            if curriculo_formatado['resumo']:
                st.markdown("#### 👤 Resumo Profissional")
                st.markdown(
                    "\n".join([f"- {item}" for item in curriculo_formatado['resumo']]))
                st.markdown("---")

            if curriculo_formatado['formacao']:
                st.markdown("#### 🎓 Formação Acadêmica")
                st.markdown(
                    "\n".join([f"- {item}" for item in curriculo_formatado['formacao']]))
                st.markdown("---")

            if curriculo_formatado['experiencia']:
                st.markdown("#### 💼 Experiência Profissional")
                st.markdown(
                    "\n".join([f"- {item}" for item in curriculo_formatado['experiencia']]))
                st.markdown("---")

            if curriculo_formatado['habilidades']:
                st.markdown("#### 🛠️ Habilidades Técnicas")
                st.markdown(
                    "\n".join([f"- {item}" for item in curriculo_formatado['habilidades']]))
                st.markdown("---")

            if curriculo_formatado['outros']:
                st.markdown("#### 📌 Outras Informações")
                st.markdown(
                    "\n".join([f"- {item}" for item in curriculo_formatado['outros']]))

        with tab2:
            st.text_area("Texto completo do currículo",
                         value=candidato['cv_pt'],
                         height=400,
                         disabled=True,
                         key="cv_full_text")


def exibir_metadados(candidato):
    """Exibe metadados do cadastro"""
    with st.expander("📊 Metadados do Cadastro", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"**📅 Data de Criação:** {candidato['infos_basicas'].get('data_criacao', 'Não informado')}")
            st.markdown(
                f"**🔄 Data de Atualização:** {candidato['infos_basicas'].get('data_atualizacao', 'Não informado')}")
            st.markdown(
                f"**👤 Inserido por:** {candidato['infos_basicas'].get('inserido_por', 'Não informado')}")

        with col2:
            st.markdown(
                f"**📌 Sabendo de nós por:** {candidato['infos_basicas'].get('sabendo_de_nos_por', 'Não informado')}")
            st.markdown(
                f"**🔗 Fonte de Indicação:** {candidato['informacoes_pessoais'].get('fonte_indicacao', 'Não informado')}")
            st.markdown(
                f"**📅 Data de Aceite:** {candidato['informacoes_pessoais'].get('data_aceite', 'Não informado')}")


def exibir_historico_candidaturas(prospects_df, codigo_candidato):
    """Exibe o histórico de candidaturas do profissional"""
    candidaturas = prospects_df[prospects_df['codigo'] == codigo_candidato]

    if len(candidaturas) == 0:
        st.info("Este candidato não possui histórico de candidaturas registrado.")
        return

    with st.expander("📋 Histórico de Candidaturas", expanded=True):
        st.markdown(f"**Total de candidaturas:** {len(candidaturas)}")

        for _, candidatura in candidaturas.iterrows():
            with st.container():
                st.markdown(f"""
                <div style='
                    background-color:#f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                '>
                    <h4>{candidatura['titulo_vaga']}</h4>
                    <p><b>Status:</b> {candidatura['situacao_candidado']}</p>
                    <p><b>Data da Candidatura:</b> {formatar_data(candidatura['data_candidatura'])}</p>
                    <p><b>Última Atualização:</b> {formatar_data(candidatura['ultima_atualizacao'])}</p>
                    <p><b>Recrutador:</b> {candidatura['recrutador']}</p>
                    <p><b>Comentários:</b> {candidatura['comentario'] if candidatura['comentario'] else 'Nenhum comentário registrado'}</p>
                </div>
                """, unsafe_allow_html=True)


def consulta_candidato_profissional(prospects_json, applicants_json, codigo_fixo=None):
    """
    Função principal para consulta profissional de candidatos

    Args:
        prospects_json (dict): Dados dos prospects em formato JSON
        applicants_json (dict): Dados dos candidatos em formato JSON
        codigo_fixo (str): Código do candidato para carregar automaticamente (opcional)
    """
    # Configuração da página
    st.markdown("#  Consulta Profissional de Candidatos")
    st.markdown("### Página dedicada à análise detalhada de perfis")

    # Processar os DataFrames
    prospects_df = processar_prospects(prospects_json)

    # Sidebar com filtros
    with st.sidebar:
        st.header("🔍 Filtros")

        # Lista de candidatos para seleção
        lista_candidatos = [(codigo, dados['infos_basicas']['nome'])
                            for codigo, dados in applicants_json.items()]
        lista_candidatos.sort(key=lambda x: x[1])  # Ordenar por nome

        # Encontrar o índice do candidato fixo, se especificado
        indice_padrao = 0
        if codigo_fixo:
            for i, (codigo, _) in enumerate(lista_candidatos):
                if codigo == codigo_fixo:
                    indice_padrao = i
                    break

        candidato_selecionado = st.selectbox(
            "Selecione o candidato:",
            lista_candidatos,
            index=indice_padrao,
            format_func=lambda x: f"{x[0]} - {x[1]}"
        )

        codigo_selecionado = candidato_selecionado[0]
        candidato = applicants_json[codigo_selecionado]

    # =====================
    # CABEÇALHO
    # =====================
    st.markdown(f"""
    <div style='
        background-color:#f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    '>
        <div style='display: flex; justify-content: space-between;'>
            <div>
                <h2 style='color: #2c3e50; margin-bottom: 5px;'>{candidato['infos_basicas']['nome']}</h2>
                <p style='margin: 0;'><b>Código:</b> {candidato['infos_basicas']['codigo_profissional']}</p>
            </div>
            <div style='text-align: right;'>
                <p style='margin: 0;'><b>📧 Email:</b> {candidato['infos_basicas']['email']}</p>
                <p style='margin: 0;'><b>📱 Telefone:</b> {formatar_telefone(candidato['infos_basicas']['telefone'])}</p>
                <p style='margin: 0;'><b>📍 Local:</b> {candidato['infos_basicas'].get('local', 'Não informado')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =====================
    # SEÇÕES PRINCIPAIS
    # =====================

    # Seção de histórico de candidaturas
    exibir_historico_candidaturas(prospects_df, codigo_selecionado)

    # Abas para demais informações
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Informações Pessoais", "💼 Profissional", "🎓 Formação", "📄 Currículo"])

    with tab1:
        exibir_informacoes_pessoais(candidato)

    with tab2:
        exibir_informacoes_profissionais(candidato)

    with tab3:
        exibir_formacao_idiomas(candidato)

    with tab4:
        exibir_curriculo(candidato)

    # Metadados (rodapé)
    exibir_metadados(candidato)
