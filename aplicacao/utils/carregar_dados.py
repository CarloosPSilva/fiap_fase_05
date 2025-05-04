import pandas as pd
import json
import os
import shutil
import zipfile

def garantir_dados_extraidos():
    caminho_zip = 'aplicacao/dados.zip'
    pasta_destino = 'aplicacao/dados'

    if os.path.exists(pasta_destino):
        shutil.rmtree(pasta_destino)

    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
        zip_ref.extractall('aplicacao')
    print("📦 Arquivos de dados extraídos com sucesso.")


def carregar_base():
    # Garante que os arquivos JSON estejam disponíveis
    garantir_dados_extraidos()

    path_vagas = 'aplicacao/dados/vagas.json'
    path_prospects = 'aplicacao/dados/prospects.json'
    path_applicants = 'aplicacao/dados/applicants.json'

    # --- VAGAS ---
    with open(path_vagas, "r", encoding="utf-8") as f:
        vagas_json = json.load(f)

    vagas_list = []
    for job_id, job_data in vagas_json.items():
        flat_data = {"job_id": str(job_id)}
        for section, details in job_data.items():
            if isinstance(details, dict):
                for key, value in details.items():
                    col_name = f"{section}_{key}".replace(" ", "_")
                    flat_data[col_name] = value
            else:
                flat_data[section] = details
        vagas_list.append(flat_data)

    vagas_df = pd.DataFrame(vagas_list)
    vagas_df.columns = [col.replace(" ", "_") for col in vagas_df.columns]

    # --- PROSPECTS ---
    with open(path_prospects, "r", encoding="utf-8") as f:
        prospects_json = json.load(f)

    prospects_list = []
    for job_id, job_data in prospects_json.items():
        if "prospects" in job_data:
            for candidate in job_data["prospects"]:
                candidate["job_id"] = str(job_id)
                prospects_list.append(candidate)

    prospects_df = pd.DataFrame(prospects_list)

    # --- APPLICANTS ---
    with open(path_applicants, "r", encoding="utf-8") as f:
        applicants_json = json.load(f)

    applicants_list = []
    for codigo, dados in applicants_json.items():
        row = {
            'codigo': dados.get('infos_basicas', {}).get('codigo_profissional', ''),
            'local': dados.get('infos_basicas', {}).get('local', ''),
            'skills': dados.get('informacoes_profissionais', {}).get('skills', ''),
            'nivel_academico': dados.get('formacao_e_idiomas', {}).get('nivel_academico', ''),
            'nivel_ingles': dados.get('formacao_e_idiomas', {}).get('nivel_ingles', ''),
            'nivel_espanhol': dados.get('formacao_e_idiomas', {}).get('nivel_espanhol', ''),
            'area_atuacao': dados.get('informacoes_profissionais', {}).get('area_atuacao', ''),
            'remuneracao': dados.get('informacoes_profissionais', {}).get('remuneracao', ''),
            'job_id': dados.get('job_id', ''),
        }
        applicants_list.append(row)

    applicants_df = pd.DataFrame(applicants_list)

    # Novo retorno com os 5 elementos necessários
    return vagas_df, prospects_df, applicants_df, prospects_json, applicants_json