import os
import json
import pickle
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, f1_score
from sklearn.utils import resample
from sentence_transformers import SentenceTransformer

import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def preprocess(text):
    stop_words = set(stopwords.words('portuguese'))
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text, language="portuguese")
    tokens = [
        word for word in tokens if word not in stop_words and len(word) > 2]
    return ' '.join(tokens)


def extract_job_requirements(job):
    skills = job["perfil_vaga"].get(
        "competencia_tecnicas_e_comportamentais", "")
    activities = job["perfil_vaga"].get("principais_atividades", "")
    return skills.lower() + " " + activities.lower()


def carregar_modelo():
    df = pd.read_pickle('aplicacao/modelo/labeled_df_emb')

    df_majority = df[df.label == 0]
    df_minority = df[df.label == 1]

    df_majority_downsampled = resample(
        df_majority,
        replace=False,
        n_samples=len(df_minority) * 3,
        random_state=42
    )

    df_balanced = pd.concat([df_majority_downsampled, df_minority])
    X = df_balanced[["similarity_score"]]
    y = df_balanced["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.2, random_state=42
    )

    logreg = LogisticRegression(class_weight='balanced')
    logreg.fit(X_train, y_train)

    scale = y_train.value_counts()[0] / y_train.value_counts()[1]
    xgb = XGBClassifier(
        scale_pos_weight=scale,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    xgb.fit(X_train, y_train)

    logreg_probs = logreg.predict_proba(X_test)[:, 1]
    xgb_probs = xgb.predict_proba(X_test)[:, 1]

    ensemble_probs = (logreg_probs + xgb_probs) / 2
    ensemble_preds = (ensemble_probs >= 0.5).astype(int)

    print("📈 Avaliação do Modelo Ensemble:")
    print(classification_report(y_test, ensemble_preds))
    print(f"ROC AUC Score: {roc_auc_score(y_test, ensemble_probs):.4f}")
    print(f"F1 Score: {f1_score(y_test, ensemble_preds):.4f}")

    os.makedirs("aplicacao/modelo", exist_ok=True)
    joblib.dump(logreg, "aplicacao/modelo/logistic_model.pkl")
    joblib.dump(xgb, "aplicacao/modelo/xgboost_model.pkl")


def gerar_embeddings_vagas():
    with open('aplicacao/dados/vagas.json', encoding='utf-8') as f:
        jobs = json.load(f)

    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    job_ids = list(jobs.keys())
    job_texts = [preprocess(extract_job_requirements(jobs[jid]))
                 for jid in job_ids]
    job_embeddings = model.encode(job_texts, show_progress_bar=True)
    job_titles = [jobs[jid]["informacoes_basicas"]["titulo_vaga"]
                  for jid in job_ids]

    os.makedirs("aplicacao/modelo", exist_ok=True)
    joblib.dump({
        "job_ids": job_ids,
        "job_titles": job_titles,
        "job_embeddings": job_embeddings
    }, "aplicacao/modelo/job_data.pkl")

    with open("aplicacao/modelo/vagas.pkl", "wb") as f:
        pickle.dump(jobs, f)
