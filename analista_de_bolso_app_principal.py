import streamlit as st
import requests
import pandas as pd
import yfinance as yf

# ==========================================
# CONFIGURAÇÃO DE PÁGINA & TEMA EXECUTIVE (DELOITTE / GARTNER)
# ==========================================
st.set_page_config(
    page_title="Analista de Bolso | Executive Terminal",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject CSS para forçar Dark Theme em ABSOLUTAMENTE TUDO (incluindo o Glide Data Grid do Streamlit)
st.markdown("""
<style>
    /* Reset Global & Fundo Carvão Deloitte Executive */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0b0e14 !important;
        color: #e2e8f0 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }
    
    /* Ocultar elementos nativos do Streamlit */
    [data-testid="stSidebar"] { display: none !important; }
    footer { visibility: hidden !important; display: none !important; }
    header { visibility: hidden !important; display: none !important; }

    .block-container {
        padding: 1.5rem 3rem !important;
        max-width: 1400px;
    }

    /* Banner Superior Deloitte / Gartner Executive Style */
    .deloitte-header {
        background: #141824;
        border-left: 4px solid #86bc25; /* Deloitte Green */
        border-radius: 8px;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #2d3548;
        border-right: 1px solid #2d3548;
        border-bottom: 1px solid #2d3548;
    }
    .deloitte-title { font-size: 1.4rem; font-weight: 700; color: #ffffff; margin: 0; letter-spacing: -0.5px; }
    .deloitte-title span { color: #86bc25; }
    .deloitte-subtitle { font-size: 0.85rem; color: #94a3b8; margin-top: 4px; }

    /* Customização dos Botões da Top Navbar (Unificados e Alinhados) */
    div.stButton > button {
        width: 100%;
        height: 44px;
        background-color: #141824 !important;
        color: #94a3b8 !important;
        border: 1px solid #2d3548 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #1e2333 !important;
        color: #ffffff !important;
        border-color: #86bc25 !important;
    }
    div.stButton > button:focus, div.stButton > button:active {
        background-color: #86bc25 !important;
        color: #0b0e14 !important;
        font-weight: 700 !important;
        border-color: #86bc25 !important;
    }

    /* Cards de Métricas Executive */
    .metric-card {
        background-color: #141824;
        border: 1px solid #2d3548;
        border-radius: 8px;
        padding: 1.1rem;
        margin-bottom: 1rem;
    }
    .metric-label { font-size: 0.72rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.08em; }
    .metric-val { font-size: 1.5rem; font-weight: 700; color: #ffffff; margin: 6px 0; }
    
    /* Badges Corporativas */
    .badge-green { background: rgba(134, 188, 37, 0.15); color: #86bc25; border: 1px solid rgba(134, 188, 37, 0.4); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .badge-amber { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.4); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .badge-red { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }

    /* Inputs Escuros */
    div[data-baseweb="select"] > div, input {
        background-color: #141824 !important;
        border: 1px solid #2d3548 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
    }

    /* FORÇAR A ELIMINAÇÃO TOTAL DO BLOCO BRANCO DA TABELA (GLIDE DATA GRID OVERRIDE) */
    div[data-testid="stDataFrame"] {
        background-color: #141824 !important;
        border: 1px solid #2d3548 !important;
        border-radius: 8px !important;
        padding: 8px !important;
    }
    
    /* Hack CSS para forçar o Canvas/IFrame do Streamlit DataFrame a ficar escuro */
    div[data-testid="stDataFrame"] > div {
        background-color: #141824 !important;
    }
    
    /* Tabela HTML Customizada 100% Dark para garantir que NUNCA fique branca */
    .deloitte-table-container {
        background-color: #141824;
        border: 1px solid #2d3548;
        border-radius: 8px;
        overflow-x: auto;
        padding: 0;
        margin-top: 15px;
    }
    .deloitte-table {
        width: 100%;
        border-collapse: collapse;
        color: #e2e8f0;
        font-size: 0.88rem;
    }
    .deloitte-table th {
        background-color: #1e2333;
        color: #86bc25; /* Deloitte Green Accent */
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        padding: 12px 16px;
        text-align: left;
        border-bottom: 1px solid #2d3548;
    }
    .deloitte-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #1e2333;
    }
    .deloitte-table tr:hover {
        background-color: #1b202e;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER EXECUTIVE
# ==========================================
st.markdown("""
<div class="deloitte-header">
    <div>
        <div class="deloitte-title">Analista de Bolso <span>.</span></div>
        <div class="deloitte-subtitle">Terminal de Inteligência Financeira, Valuation & Análises Quantitativas</div>
    </div>
    <div>
        <span class="badge-green">DELOITTE & GARTNER STANDARD</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# TOP NAVBAR (3 BOTÕES PERFEITAMENTE ALINHADOS E AGRUPADOS)
# ==========================================
if 'aba_ativa' not in st.session_state:
    st.session_state.aba_ativa = "cripto"

c_nav1, c_nav2, c_nav3, _ = st.columns([1.5, 1.5, 2, 4])

with c_nav1:
    if st.button("🪙 Mercado Cripto"):
        st.session_state.aba_ativa = "cripto"

with c_nav2:
    if st.button("📈 Ações B3"):
        st.session_state.aba_ativa = "acoes"

with c_nav3:
    if st.button("💡 Pílulas de Conhecimento"):
        st.session_state.aba_ativa = "pilulas"

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# ==========================================
# FUNÇÕES DE DATA & FORMATAÇÃO PT-BR
# ==========================================
def formatar_moeda_br(valor):
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

def formatar_cap_mercado(valor):
    try:
        if valor >= 1_000_000_000:
            return f"R$ {valor / 1_000_000_000:,.2f}".replace(".", ",") + " Bi"
        elif valor >= 1_000_000:
            return f"R$ {valor / 1_000_000:,.2f}".replace(".", ",") + " Mi"
        else:
            return formatar_moeda_br(valor)
    except Exception:
        return "R$ 0,00"

@st.cache_data(ttl=300)
def get_fear_and_greed():
    try:
        url = "https://api.alternative.me/fng/?limit=1"
        res = requests.get(url, timeout=5).json()
        val = int(res['data'][0]['value'])
        status = res['data'][0]['value_classification']
        return val, status
    except Exception:
        return 50, "Neutro"

@st.cache_data(ttl=300)
def get_coingecko_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'brl',
            'order': 'market_cap_desc',
            'per_page': 20,
            'page': 1,
            'sparkline': 'false',
            'price_change_percentage': '24h'
        }
        res = requests.get(url, params=params, timeout=8)
        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            btc_row = df[df['symbol'] == 'btc']
            btc_info = {}
            if not btc_row.empty:
                btc_info = {
                    'price': btc_row.iloc[0]['current_price'],
                    'change_24h': btc_row.iloc[0]['price_change_percentage_24h'],
                    'high_24h': btc_row.iloc[0]['high_24h'],
                    'low_24h': btc_row.iloc[0]['low_24h']
                }
            return df, btc_info
        return pd.DataFrame(), {}
    except Exception:
        return pd.DataFrame(), {}

@st.cache_data(ttl=600)
def get_b3_stocks(tickers):
    results = []
    for symbol in tickers:
        try:
            t = yf.Ticker(f"{symbol}.SA")
            info = t.info
            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
            pvp = info.get('priceToBook') if isinstance(info.get('priceToBook'), (int, float)) else 0.0
            pl = info.get('trailingPE') if isinstance(info.get('trailingPE'), (int, float)) else 0.0
            dy = (info.get('dividendYield') or 0.0) * 100
            name = info.get('shortName') or symbol

            results.append({
                'Ticker': symbol,
                'Empresa': name,
                'Preço (R$)': price,
                'P/VP': round(pvp, 2),
                'P/L': round(pl, 2),
                'DY (%)': round(dy, 2)
            })
        except Exception:
            continue
    return pd.DataFrame(results)

# ==========================================
# CONTEÚDO DAS TELAS
# ==========================================

# ------------------------------------------
# 1. TELA CRIPTO
# ------------------------------------------
if st.session_state.aba_ativa == "cripto":
    fg_val, fg_status = get_fear_and_greed()
    df_crypto, btc_info = get_coingecko_data()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Fear & Greed Index</div>
            <div class="metric-val">{fg_val}/100</div>
            <span class="badge-amber">{fg_status.upper()}</span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        btc_price_str = formatar_moeda_br(btc_info.get('price', 0)) if btc_info else "N/A"
        btc_var = btc_info.get('change_24h', 0) if btc_info else 0
        badge_class = "badge-green" if btc_var >= 0 else "badge-red"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Bitcoin (BTC/BRL)</div>
            <div class="metric-val">{btc_price_str}</div>
            <span class="{badge_class}">{btc_var:+.2f}% (24h)</span>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        btc_high_str = formatar_moeda_br(btc_info.get('high_24h', 0)) if btc_info else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Máxima 24h</div>
            <div class="metric-val">{btc_high_str}</div>
            <span class="badge-amber">Topo Diário</span>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        btc_low_str = formatar_moeda_br(btc_info.get('low_24h', 0)) if btc_info else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Mínima 24h</div>
            <div class="metric-val">{btc_low_str}</div>
            <span class="badge-amber">Suporte Diário</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Panorama do Mercado Global de Criptoativos")

    if not df_crypto.empty:
        rows_html = ""
        for _, row in df_crypto.iterrows():
            var = row.get('price_change_percentage_24h', 0) or 0
            var_color = "#86bc25" if var >= 0 else "#ef4444"
            var_badge = f"<span style='color:{var_color}; font-weight:600;'>{var:+.2f}%</span>"
            
            rows_html += f"""
            <tr>
                <td><b>{row['name']}</b></td>
                <td><span style='color:#94a3b8;'>{row['symbol'].upper()}</span></td>
                <td>{formatar_moeda_br(row['current_price'])}</td>
                <td>{var_badge}</td>
                <td>{formatar_cap_mercado(row['market_cap'])}</td>
            </tr>
            """

        table_html = f"""
        <div class="deloitte-table-container">
            <table class="deloitte-table">
                <thead>
                    <tr>
                        <th>Moeda</th>
                        <th>Símbolo</th>
                        <th>Preço (R$)</th>
                        <th>Variação 24h</th>
                        <th>Cap. Mercado</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)

# ------------------------------------------
# 2. TELA AÇÕES B3
# ------------------------------------------
elif st.session_state.aba_ativa == "acoes":
    st.subheader("🔎 Monitor de Múltiplos & Valuation B3")

    col1, col2, col3 = st.columns([1.5, 1.5, 2])
    with col1:
        preco_max = st.slider("Preço Máximo da Ação (R$):", 1.0, 100.0, 50.0)
    with col2:
        pvp_max = st.slider("P/VP Máximo (Desconto):", 0.2, 3.0, 1.5)
    with col3:
        busca = st.text_input("Buscar Ticker ou Empresa:").upper()

    tickers_b3 = ["ENJU3", "BHIA3", "OIBR3", "CASH3", "VIVR3", "BBAS3", "PETR4", "VALE3", "ITSA4", "WEGE3"]

    with st.spinner("Carregando B3..."):
        df_stocks = get_b3_stocks(tickers_b3)

    if not df_stocks.empty:
        df_filtered = df_stocks.copy()
        df_filtered = df_filtered[df_filtered['Preço (R$)'] <= preco_max]
        df_filtered = df_filtered[df_filtered['P/VP'] <= pvp_max]

        if busca:
            df_filtered = df_filtered[
                df_filtered['Ticker'].str.contains(busca) |
                df_filtered['Empresa'].str.upper().str.contains(busca)
            ]

        rows_html = ""
        for _, row in df_filtered.iterrows():
            preco = row['Preço (R$)']
            pvp = row['P/VP']
            
            if preco < 2.0:
                status = "<span class='badge-red'>⚡ Penny Stock</span>"
            elif 0 < pvp < 0.85:
                status = "<span class='badge-green'>🟢 Descontada (P/VP < 0.85)</span>"
            else:
                status = "<span class='badge-amber'>🔵 Regular</span>"

            rows_html += f"""
            <tr>
                <td><b>{row['Ticker']}</b></td>
                <td><span style='color:#94a3b8;'>{row['Empresa']}</span></td>
                <td>{formatar_moeda_br(row['Preço (R$)'])}</td>
                <td>{row['P/VP'] if row['P/VP'] > 0 else 'N/A'}</td>
                <td>{row['P/L'] if row['P/L'] > 0 else 'N/A'}</td>
                <td style='color:#86bc25; font-weight:600;'>{row['DY (%)']:.2f}%</td>
                <td>{status}</td>
            </tr>
            """

        table_html = f"""
        <div class="deloitte-table-container">
            <table class="deloitte-table">
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Empresa</th>
                        <th>Preço (R$)</th>
                        <th>P/VP</th>
                        <th>P/L</th>
                        <th>DY (%)</th>
                        <th>Status do Bot</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)

# ------------------------------------------
# 3. TELA PÍLULAS DE CONHECIMENTO
# ------------------------------------------
elif st.session_state.aba_ativa == "pilulas":
    st.subheader("💡 Diretrizes & Mapeamento de Conceitos")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="metric-card" style="margin-bottom: 15px;">
            <h4 style="color:#86bc25; margin-top:0;">1. O que é P/VP?</h4>
            <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5;">
                <b>Preço sobre Valor Patrimonial</b>. Métrica fundamentalista que indica se o ativo está sendo negociado abaixo do seu valor contábil.
            </p>
        </div>
        <div class="metric-card">
            <h4 style="color:#ef4444; margin-top:0;">2. Perigo das Penny Stocks</h4>
            <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5;">
                Ativos cotados abaixo de R$ 1,00 apresentam volatilidade atípica e risco de agrupamento compulsório. Exige alocação marginal de capital.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="metric-card" style="margin-bottom: 15px;">
            <h4 style="color:#86bc25; margin-top:0;">3. Fear & Greed Index</h4>
            <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5;">
                Métrica quantitativa de sentimento de mercado. Períodos de pavor generalizado costumam oferecer pontos de entrada com assimetria favorável.
            </p>
        </div>
        <div class="metric-card">
            <h4 style="color:#f59e0b; margin-top:0;">4. Assimetria de Risco Construtiva</h4>
            <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5;">
                Estratégia de portfólio onde a máxima perda é rigidamente delimitada em relação ao potencial multiplicador de ganho.
            </p>
        </div>
        """, unsafe_allow_html=True)
