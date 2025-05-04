import re
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import pandas as pd
import streamlit as st
from aplicacao.utils.carregar_dados import carregar_base


def limpar_remuneracao(texto):
    if pd.isna(texto) or texto == '':
        return np.nan

    texto = str(texto).strip()
    original = texto

    negativos = [
        'zero', 'não informado', 'none', 'nan', 'salário', 'variável',
        'trabalho', 'sem', 'semanal', 'sem experiências', 'salário mínimo',
        'variavel', 'valor/hora', 'taxa', 'remuneração'
    ]

    if any(term in texto.lower() for term in negativos):
        return np.nan

    texto = texto.lower()
    texto = texto.replace('r$', 'brl').replace(
        'us$', 'usd').replace('usd', 'usd')
    texto = texto.replace('mensal', 'mes').replace(
        'mês', 'mes').replace('mensais', 'mes')
    texto = texto.replace('hora', 'h').replace(
        '/h', 'h').replace('hr', 'h').replace('valor', '')
    texto = texto.replace('taxa', '').replace(
        'rem.', '').replace('rem:', '').replace('rs', 'brl')
    texto = re.sub(r'[^\d.,a-z/]', '', texto)

    valor = None

    padrao_brl = re.compile(r'brl(\d+[,.]?\d*[,.]?\d*)')
    match_brl = padrao_brl.search(texto)
    if match_brl:
        num = match_brl.group(1).replace('.', '').replace(',', '.')
        try:
            valor = float(num)
        except:
            pass

    if valor is None:
        padrao_usd = re.compile(r'usd(\d+[,.]?\d*[,.]?\d*)')
        match_usd = padrao_usd.search(texto)
        if match_usd:
            num = match_usd.group(1).replace('.', '').replace(',', '.')
            try:
                valor = float(num)
            except:
                pass

    if valor is None:
        padrao_num = re.compile(r'(\d+[,.]?\d*[,.]?\d*)')
        match_num = padrao_num.search(texto.replace('.', '').replace(',', '.'))
        if match_num:
            try:
                valor = float(match_num.group(1))
            except:
                pass

    if valor is not None:
        if 'h' in texto or '/hora' in original.lower():
            valor *= 160
        elif '/dia' in original.lower() or 'por dia' in original.lower():
            valor *= 22

    return valor




def preparar_candidatos_df(prospects_json=None, applicants_json=None, vagas_df=None, prospects_df=None, applicants_df=None):
    if not all([vagas_df, prospects_df, applicants_df, prospects_json, applicants_json]):
        vagas_df, prospects_df, applicants_df, prospects_json, applicants_json = carregar_base()

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

    # Preparar applicants
    lista_applicants = []
    for codigo, dados in applicants_json.items():
        lista_applicants.append({
            'codigo': dados['infos_basicas'].get('codigo_profissional', ''),
            'nome': dados['infos_basicas'].get('nome', ''),
            'email': dados['infos_basicas'].get('email', ''),
            'local': dados['infos_basicas'].get('local', ''),
            'nivel_academico': dados['formacao_e_idiomas'].get('nivel_academico', '') or 'Não informado',
            'nivel_ingles': dados['formacao_e_idiomas'].get('nivel_ingles', '') or 'Nenhum',
            'nivel_espanhol': dados['formacao_e_idiomas'].get('nivel_espanhol', '') or 'Nenhum',
            'remuneracao': dados['informacoes_profissionais'].get('remuneracao', ''),
            'area_atuacao': dados['informacoes_profissionais'].get('area_atuacao', '') or 'Não informado',
            'dados_completos': dados
        })

    applicants_df = pd.DataFrame(lista_applicants)

    # Tratamento da remuneração
    applicants_df['remuneracao'] = applicants_df['remuneracao'].apply(limpar_remuneracao)
    applicants_df['remuneracao'] = pd.to_numeric(applicants_df['remuneracao'], errors='coerce')
    applicants_df['remuneracao'].fillna(applicants_df['remuneracao'].median(), inplace=True)

    # Merge
    candidatos_df = pd.merge(prospects_df, applicants_df, on='codigo', how='left')

    return candidatos_df, vagas_df, prospects_json, applicants_json


def clusterizar_candidatos(candidatos_df):
    # ✅ Filtrar candidatos com dados válidos
    candidatos_df = candidatos_df[
        (candidatos_df['nivel_academico'] != 'Não informado') &
        (candidatos_df['nivel_ingles'] != 'Nenhum') &
        (candidatos_df['nivel_espanhol'] != 'Nenhum')
    ].dropna(subset=['remuneracao'])

    # 🔒 Amostragem para performance
    MAX_REGISTROS = 75
    if len(candidatos_df) > MAX_REGISTROS:
        candidatos_df = candidatos_df.sample(n=MAX_REGISTROS, random_state=42).reset_index(drop=True)

    try:
        # Base para cluster
        df_cluster = candidatos_df[['codigo', 'nivel_academico', 'nivel_ingles', 'nivel_espanhol', 'remuneracao']].copy()

        df_dummies = pd.get_dummies(df_cluster.drop(columns=['codigo', 'remuneracao']), drop_first=True)
        df_final = pd.concat([df_dummies, df_cluster[['remuneracao']]], axis=1)
        X_scaled = (df_final - df_final.mean()) / df_final.std()

        kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
        df_cluster['cluster'] = kmeans.fit_predict(X_scaled)

        # Merge no original
        candidatos_df = candidatos_df.merge(df_cluster[['codigo', 'cluster']], on='codigo', how='left')

    except Exception as e:
        st.error(f"Erro durante a clusterização: {e}")
        return pd.DataFrame()

    return candidatos_df