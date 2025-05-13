import re
import numpy as np
from sklearn.cluster import KMeans
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




def preparar_candidatos_df(prospects_json=None, vagas_df=None, prospects_df=None):
    if not all([vagas_df, prospects_df, prospects_json]):
        # Ajustado para ignorar apenas o que não será usado
        vagas_df, prospects_df, _, prospects_json, _ = carregar_base()

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

    return vagas_df, prospects_df, prospects_json
