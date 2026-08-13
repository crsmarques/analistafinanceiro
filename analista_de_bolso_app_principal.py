import streamlit as st
import requests
import pandas as pd
import yfinance as yf

# ==========================================
# CONFIGURAÇÃO DA PÁGINA & TEMA
# ==========================================
st.set_page_config(
    page_title="Analista de Bolso | Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS limpo e sem hacks quebrados de HTML
st.markdown("""
<style>
    /* Reset Geral & Fundo Escuro */
    .stApp {
        background-color: #0b0e14 !important;
        color: #f1f5f9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Ocultar elementos desnecessários */
    [data-testid="stSidebar"] { display: none !important; }
    footer { visibility: hidden !important; }
    header { visibility: hidden !important; }

    /* Container Principal */
    .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 1350px;
    }

    /* Header Principal */
    .top-header {
        background: linear-gradient(135deg, #141824 0%, #1e2333 100%);
        border: 1px solid #2d3548;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    .top-header h2 { margin: 0; font-size: 1.4rem; color: #ffffff; }
    .top-header p { margin: 2px 0 0 0; font-size: 0.85rem; color: #94a3b8; }

    /* Estilização dos Inputs e Filtros */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div {
        background-color: #141824 !important;
        border: 1px solid #2d3548 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    input { color: #ffffff !important; }

    /* Cards de Métricas */
    .metric-card {
        background-color: #141824;
        border: 1px solid #2d3548;
        border-radius: 12px;
        padding: 1rem 1.25rem;
    }
    .metric-label { font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; }
    .metric-val { font-size: 1.5rem; font-weight: 700; color: #ffffff; margin: 4px 0; }
    
    /* Status Badges */
    .badge-green { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }
    .badge-amber { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }
    .badge-red { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }

    /* Estilização da Tabela Nativa */
    div[data-testid="stDataFrame"] {
        background-color: #141824;
        border: 1px solid #2d3548;
        border-radius: 12px;
        padding: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER
# ==========================================
st.markdown("""
<div class="top-header">
    <div>
        <h2>⚡ Analista de Bolso</h2>
        <p>Terminal de Inteligência Financeira & Análises Quantitativas</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# NAVEGAÇÃO DE TOPO (RADIO HORIZONTAL NATIVO)
# ==========================================
aba_selecionada = st.radio(
    label="Menu de Navegação",
    options=["🪙 Cripto", "📈 Ações B3", "💡 Pílulas de conhecimento"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# ==========================================
# APIS E DADOS
# ==========================================
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
def get_coingecko_top_cryptos():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {'vs_currency': 'brl', 'order': 'market_cap_desc', 'per_page': 20, 'page': 1, 'sparkline': 'false', 'price_change_percentage': '24h'}
        res = requests.get(url, params=params, timeout=8)
        if res.status_code == 200:
            return pd.DataFrame(res.json())
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_btc_data():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCBRL"
        res = requests.get(url, timeout=5).json()
        if 'lastPrice' in res:
            return {'last_price': float(res['lastPrice']), 'high': float(res['highPrice']), 'low': float(res['lowPrice']), 'change_pct': float(res['priceChangePercent'])}
    except Exception:
        pass
    return {'last_price': 0.0, 'high': 0.0, 'low': 0.0, 'change_pct': 0.0}

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
                'Preço (R$)': round(price, 2),
                'P/VP': round(pvp, 2),
                'P/L': round(pl, 2),
                'DY (%)': round(dy, 2)
            })
        except Exception:
            continue
    return pd.DataFrame(results)

# ==========================================
# TELAS
# ==========================================

# 1. TELA CRIPTO
if aba_selecionada == "🪙 Cripto":
    fg_val, fg_status = get_fear_and_greed()
    btc_data = get_btc_data()

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
        btc_price = f"R$ {btc_data['last_price']:,.2f}" if btc_data['last_price'] > 0 else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Bitcoin (BTC/BRL)</div>
            <div class="metric-val">{btc_price}</div>
            <span class="badge-green">{btc_data['change_pct']:+.2f}% 24h</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        btc_high = f"R$ {btc_data['high']:,.2f}" if btc_data['high'] > 0 else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Máxima 24h</div>
            <div class="metric-val">{btc_high}</div>
            <span class="badge-amber">Topo</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        btc_low = f"R$ {btc_data['low']:,.2f}" if btc_data['low'] > 0 else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Mínima 24h</div>
            <div class="metric-val">{btc_low}</div>
            <span class="badge-amber">Suporte</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Top Criptomoedas (CoinGecko)")
    
    df_crypto = get_coingecko_top_cryptos()
    if not df_crypto.empty:
        df_show = df_crypto[['name', 'symbol', 'current_price', 'price_change_percentage_24h', 'market_cap']].copy()
        df_show.columns = ['Moeda', 'Símbolo', 'Preço (R$)', 'Variação 24h (%)', 'Cap. Mercado (R$)']
        df_show['Símbolo'] = df_show['Símbolo'].str.upper()

        st.dataframe(
            df_show.style.format({
                'Preço (R$)': 'R$ {:,.2f}',
                'Variação 24h (%)': '{:+.2f}%',
                'Cap. Mercado (R$)': 'R$ {:,.0f}'
            }),
            use_container_width=True,
            height=450
        )

# 2. TELA AÇÕES B3
elif aba_selecionada == "📈 Ações B3":
    st.subheader("🔎 Monitor de Ações B3")

    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        preco_max = st.slider("Preço Máximo (R$):", 1.0, 100.0, 50.0)
    with col2:
        pvp_max = st.slider("P/VP Máximo:", 0.2, 3.0, 1.5)
    with col3:
        categoria = st.selectbox("Categoria:", ["Todas", "Penny Stocks (< R$ 2.00)", "Descontadas (P/VP < 0.85)"])
    with col4:
        busca = st.text_input("Buscar Ticker / Empresa:").upper()

    tickers_b3 = ["ENJU3", "BHIA3", "OIBR3", "CASH3", "VIVR3", "BBAS3", "PETR4", "VALE3", "ITSA4", "WEGE3"]
    
    with st.spinner("Carregando B3..."):
        df_stocks = get_b3_stocks(tickers_b3)

    if not df_stocks.empty:
        df_filtered = df_stocks.copy()
        df_filtered = df_filtered[df_filtered['Preço (R$)'] <= preco_max]
        df_filtered = df_filtered[df_filtered['P/VP'] <= pvp_max]

        if categoria == "Penny Stocks (< R$ 2.00)":
            df_filtered = df_filtered[df_filtered['Preço (R$)'] < 2.0]
        elif categoria == "Descontadas (P/VP < 0.85)":
            df_filtered = df_filtered[(df_filtered['P/VP'] > 0) & (df_filtered['P/VP'] < 0.85)]

        if busca:
            df_filtered = df_filtered[
                df_filtered['Ticker'].str.contains(busca) | 
                df_filtered['Empresa'].str.upper().str.contains(busca)
            ]

        def indicar_status(row):
            if row['Preço (R$)'] < 2.0:
                return "⚡ Penny Stock"
            elif 0 < row['P/VP'] < 0.85:
                return "🟢 Descontada"
            return "🔵 Normal"

        df_filtered['Status Bot'] = df_filtered.apply(indicar_status, axis=1)

        st.dataframe(
            df_filtered.style.format({
                'Preço (R$)': 'R$ {:.2f}',
                'P/VP': '{:.2f}',
                'P/L': '{:.2f}',
                'DY (%)': '{:.2f}%'
            }),
            use_container_width=True,
            height=400
        )

# 3. TELA PÍLULAS DE CONHECIMENTO
elif aba_selecionada == "💡 Pílulas de conhecimento":
    st.subheader("💡 Conceitos Essenciais de Mercado")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("""
        <div class="metric-card" style="margin-bottom: 15px;">
            <h4 style="color:#60a5fa; margin-top:0;">1. O que é P/VP?</h4>
            <p style="color:#cbd5e1; font-size:0.9rem;">
                <b>Preço sobre Valor Patrimonial</b>. P/VP menor que 1.0 indica que a ação está sendo negociada abaixo do valor dos bens da empresa.
            </p>
        </div>
        <div class="metric-card">
            <h4 style="color:#ef4444; margin-top:0;">2. Perigo das Penny Stocks</h4>
            <p style="color:#cbd5e1; font-size:0.9rem;">
                Ações baratas (< R$ 1,00) têm alta volatilidade e risco de agrupamento. Trate com gestão de risco estrita.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="metric-card" style="margin-bottom: 15px;">
            <h4 style="color:#10b981; margin-top:0;">3. Fear & Greed Index</h4>
            <p style="color:#cbd5e1; font-size:0.9rem;">
                Mede a emoção do mercado. Períodos de Medo Extremo tendem a ser melhores momentos para compras graduais.
            </p>
        </div>
        <div class="metric-card">
            <h4 style="color:#f59e0b; margin-top:0;">4. Assimetria de Risco</h4>
            <p style="color:#cbd5e1; font-size:0.9rem;">
                Buscar operações onde você arrisca pouco para buscar multiplicações expressivas de capital.
            </p>
        </div>
        """, unsafe_allow_html=True)
