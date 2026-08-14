import streamlit as st
import requests
import pandas as pd
import yfinance as yf

# ==========================================
# CONFIGURAÇÃO DE PÁGINA & TEMA DELOITTE
# ==========================================
st.set_page_config(
    page_title="Analista de Bolso | Executive Terminal",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Corporate Dark Theme (Padrão Deloitte)
st.markdown("""
<style>
    /* Reset & Fundo Carvão Executivo */
    .stApp {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* Ocultar elementos padrão do Streamlit */
    [data-testid="stSidebar"] { display: none !important; }
    footer { visibility: hidden !important; }
    header { visibility: hidden !important; }

    .block-container {
        padding: 1.8rem 3rem !important;
        max-width: 1400px;
    }

    /* Banner Superior Deloitte Executive */
    .deloitte-header {
        background: #161b22;
        border-left: 4px solid #86bc25; /* Deloitte Green */
        border-radius: 8px;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .deloitte-title { font-size: 1.4rem; font-weight: 700; color: #ffffff; margin: 0; letter-spacing: -0.5px; }
    .deloitte-title span { color: #86bc25; }
    .deloitte-subtitle { font-size: 0.85rem; color: #8b949e; margin-top: 4px; }

    /* Estilização dos Botões da Top Navbar */
    div.stButton > button {
        width: 100%;
        height: 42px;
        background-color: #161b22 !important;
        color: #8b949e !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #21262d !important;
        color: #ffffff !important;
        border-color: #86bc25 !important;
    }
    div.stButton > button:focus {
        background-color: #86bc25 !important;
        color: #0d1117 !important;
        font-weight: 700 !important;
        border-color: #86bc25 !important;
    }

    /* Cards de Métricas Executive */
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1.1rem;
        margin-bottom: 1rem;
    }
    .metric-label { font-size: 0.72rem; text-transform: uppercase; color: #8b949e; font-weight: 600; letter-spacing: 0.08em; }
    .metric-val { font-size: 1.5rem; font-weight: 700; color: #ffffff; margin: 6px 0; }
    
    /* Status Badges Corporativas */
    .badge-green { background: rgba(134, 188, 37, 0.15); color: #86bc25; border: 1px solid rgba(134, 188, 37, 0.4); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .badge-amber { background: rgba(210, 153, 34, 0.15); color: #d29922; border: 1px solid rgba(210, 153, 34, 0.4); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .badge-red { background: rgba(248, 81, 73, 0.15); color: #f85149; border: 1px solid rgba(248, 81, 73, 0.4); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }

    /* Inputs escuros alinhados */
    div[data-baseweb="select"] > div, input {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #ffffff !important;
        border-radius: 6px !important;
    }

    /* ESTILIZAÇÃO COMPLETA DA TABELA DARK NATIVA */
    div[data-testid="stDataFrame"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        padding: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER
# ==========================================
st.markdown("""
<div class="deloitte-header">
    <div>
        <div class="deloitte-title">Analista de Bolso <span>.</span></div>
        <div class="deloitte-subtitle">Terminal de Inteligência Financeira, Valuation & Análises Quantitativas</div>
    </div>
    <div>
        <span class="badge-green">DELOITTE STANDARD UI</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# NAVEGAÇÃO DE TOPO (TAB NAVBAR INTEGRADAS)
# ==========================================
if 'aba_ativa' not in st.session_state:
    st.session_state.aba_ativa = "cripto"

c_nav1, c_nav2, c_nav3, _ = st.columns([1.3, 1.3, 1.8, 4])

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
# FUNÇÕES DE COLETA E FORMATAÇÃO DE DADOS
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
        df_display = df_crypto[['name', 'symbol', 'current_price', 'price_change_percentage_24h', 'market_cap']].copy()
        
        df_display['Moeda'] = df_display['name']
        df_display['Símbolo'] = df_display['symbol'].str.upper()
        df_display['Preço (R$)'] = df_display['current_price'].apply(formatar_moeda_br)
        df_display['Variação 24h'] = df_display['price_change_percentage_24h'].apply(lambda x: f"{x:+.2f}%")
        df_display['Cap. Mercado'] = df_display['market_cap'].apply(formatar_cap_mercado)

        df_show = df_display[['Moeda', 'Símbolo', 'Preço (R$)', 'Variação 24h', 'Cap. Mercado']]

        st.dataframe(
            df_show,
            use_container_width=True,
            height=480,
            hide_index=True
        )

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

        def indicar_status(row):
            if row['Preço (R$)'] < 2.0:
                return "⚡ Penny Stock / Risco"
            elif 0 < row['P/VP'] < 0.85:
                return "🟢 Descontada (P/VP < 0.85)"
            return "🔵 Sólida / Regular"

        df_filtered['Status Bot'] = df_filtered.apply(indicar_status, axis=1)

        df_filtered['Preço (R$)'] = df_filtered['Preço (R$)'].apply(formatar_moeda_br)
        df_filtered['DY (%)'] = df_filtered['DY (%)'].apply(lambda x: f"{x:.2f}%")

        st.dataframe(
            df_filtered[['Ticker', 'Empresa', 'Preço (R$)', 'P/VP', 'P/L', 'DY (%)', 'Status Bot']],
            use_container_width=True,
            height=420,
            hide_index=True
        )

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
            <p style="color:#8b949e; font-size:0.9rem; line-height:1.5;">
                <b>Preço sobre Valor Patrimonial</b>. Métrica fundamentalista que indica se o ativo está sendo negociado abaixo do seu valor contábil.
            </p>
        </div>
        <div class="metric-card">
            <h4 style="color:#f85149; margin-top:0;">2. Perigo das Penny Stocks</h4>
            <p style="color:#8b949e; font-size:0.9rem; line-height:1.5;">
                Ativos cotados abaixo de R$ 1,00 apresentam volatilidade atípica e risco de agrupamento compulsório. Exige alocação marginal de capital.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="metric-card" style="margin-bottom: 15px;">
            <h4 style="color:#86bc25; margin-top:0;">3. Fear & Greed Index</h4>
            <p style="color:#8b949e; font-size:0.9rem; line-height:1.5;">
                Métrica quantitativa de sentimento de mercado. Períodos de pavor generalizado costumam oferecer pontos de entrada com assimetria favorável.
            </p>
        </div>
        <div class="metric-card">
            <h4 style="color:#d29922; margin-top:0;">4. Assimetria de Risco Construtiva</h4>
            <p style="color:#8b949e; font-size:0.9rem; line-height:1.5;">
                Estratégia de portfólio onde a máxima perda é rigidamente delimitada em relação ao potencial multiplicador de ganho.
            </p>
        </div>
        """, unsafe_allow_html=True)
