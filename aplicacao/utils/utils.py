import streamlit as st

def style():
    st.markdown(
        """
        <style>
        /* ========== TEMA CLARO ========== */
        @media (prefers-color-scheme: light) {
            [data-testid="stSidebar"] {
                background-color: #F3F2EF !important;
                color: #1D2226 !important;
            }

            .sidebar-label {
                color: #0A66C2;
            }

            .menu-navegacao {
                background-color: #E6E9EC;
                color: #1D2226;
            }

            .stApp h1, .stApp h2 {
                color: #0A66C2 !important;
                text-align: center !important;
            }
            .stApp h3 {
                color: #0A66C2 !important;

            }

            .stDataFrame td, .stDataFrame th {
                color: #1D2226 !important;
            }

            div[data-testid="stMetricValue"] {
                color: #0A66C2 !important;
                font-weight: bold;
            }

            div[data-testid="stMetric"] {
                background-color: #ffffff !important;
                border-radius: 0.5rem;
                padding: 1rem;
                border: 1px solid #ccc;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }

            div[data-testid="metric-container"] {
                background-color: #ffffff !important;
                padding: 16px;
                border-radius: 8px;
                border: 1px solid #ccc;
            }
        }

        /* ========== TEMA ESCURO ========== */
        @media (prefers-color-scheme: dark) {
            [data-testid="stSidebar"] {
                background-color: #1E1E1E !important;
                color: white !important;
            }

            .sidebar-label {
                color: #60AFFF;
            }

            .menu-navegacao {
                background-color: #333333;
                color: white !important;
            }

            .stApp h1, .stApp h2{
                color: #60AFFF !important;
                text-align: center !important;
            }
            .stApp h3 {
                color: #0A66C2 !important;

            }

            .stDataFrame td, .stDataFrame th {
                color: white !important;
            }

            div[data-testid="stMetric"] {
                background-color: #2C2C2C !important;
                border-radius: 0.5rem;
                padding: 1rem;
                border: 1px solid #444;
                box-shadow: 0 2px 8px rgba(255,255,255,0.05);
            }

            div[data-testid="stMetricLabel"] {
                color: #EEE !important;
                font-size: 16px !important;
                font-weight: 500 !important;
            }

            div[data-testid="metric-container"] {
                background-color: #222 !important;
                padding: 16px;
                border-radius: 8px;
                border: 1px solid #444;
            }

            .element-container:has(div[data-testid="stNotification"]) {
                color: white !important;
            }

            .st-emotion-cache-1avcm0n {
                color: #EAF6FF !important;
                font-weight: 500;
            }
        }

        /* ========== ESTILOS COMUNS ========== */
        .sidebar-label {
            font-size: 25px !important;
            font-weight: bold;
            text-align: center;
            margin-top: 15px;
            margin-bottom: 15px;
            display: block;
        }

        .menu-navegacao {
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
            width: 90%;
        }

        div[data-testid="stSidebar"] select {
            font-size: 20px !important;
        }

        div[data-testid="stSidebar"] select,
        div[data-baseweb="select"] > div {
            font-weight: bold !important;
            border-radius: 5px !important;
            border: 2px solid #0A66C2 !important;
        }

        div[data-testid="stSidebar"] select:hover,
        div[data-baseweb="select"]:hover > div {
            background-color: #004182 !important;
            color: white !important;
        }

        .stButton>button {
            background-color: #0A66C2;
            color: white;
            border-radius: 10px;
            font-weight: bold;
            transition: 0.3s;
            padding: 8px 15px;
            border: none;
        }

        .stButton>button:hover {
            background-color: #004182;
            transform: scale(1.05);
        }

        section[data-testid="stFileUploader"] div[role="button"] {
            background-color: #0A66C2 !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-weight: bold;
            box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
            border: none;
        }

        section[data-testid="stFileUploader"] div[role="button"]:hover {
            background-color: #004182 !important;
            transform: scale(1.02);
        }
        </style>
        """,
        unsafe_allow_html=True
    )