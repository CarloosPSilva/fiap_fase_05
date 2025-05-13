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
    print("Arquivos de dados extraídos com sucesso.")


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

    # Apenas retorna o JSON, o DataFrame não é mais necessário se não for usado
    applicants_df = pd.DataFrame()  # Placeholder vazio, se não utilizado

    #  Retorno completo e compatível com `preparar_candidatos_df()`
    return vagas_df, prospects_df, applicants_df, prospects_json, applicants_json