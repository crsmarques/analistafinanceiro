import streamlit as st
import requests
import pandas as pd
import yfinance as yf

# ==========================================
# CONFIGURAÇÃO INICIAL DA PÁGINA & THEME
# ==========================================
st.set_page_config(
    page_title="Analista de Bolso | Terminal Financeiro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS para Padrão Fintech Dark Moderno Profundo
st.markdown("""
<style>
    /* Reset e Fundo Dark Profundo */
    .stApp {
        background-color: #0b0e14 !important;
        color: #e2e8f0 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Ocultar barra lateral e footers */
    [data-testid="stSidebar"] { display: none !important; }
    footer { visibility: hidden !important; }
    header { visibility: hidden !important; }

    /* Container Principal */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 1400px;
    }

    /* Header e Banner Superior */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, #141824 0%, #1e2333 100%);
        padding: 1.25rem 2rem;
        border-radius: 16px;
        border: 1px solid #2d3548;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .app-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .app-subtitle {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 4px;
    }

    /* Badge do Perfil */
    .profile-badge {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Botões Agrupados de Navegação (Pill Style) */
    div.stButton > button {
        width: 100%;
        height: 42px;
        background-color: #141824 !important;
        color: #94a3b8 !important;
        border: 1px solid #2d3548 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:hover {
        background-color: #1e2333 !important;
        color: #ffffff !important;
        border-color: #3b82f6 !important;
    }
    div.stButton > button:focus {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
    }

    /* Cards Finanças / Métricas */
    .metric-card {
        background-color: #141824;
        border: 1px solid #2d3548;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .metric-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 8px;
        font-weight: 600;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    /* Status Badges */
    .status-green {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-amber {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-red {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Cards Informativos */
    .info-card {
        background-color: #141824;
        border: 1px solid #2d3548;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }
    .info-card-blue { border-left: 4px solid #3b82f6; }
    .info-card-green { border-left: 4px solid #10b981; }
    .info-card-red { border-left: 4px solid #ef4444; }

    /* TABELA CUSTOMIZADA TOTALMENTE DARK */
    .dark-table-container {
        background-color: #141824;
        border: 1px solid #2d3548;
        border-radius: 14px;
        overflow-x: auto;
        padding: 10px;
        margin-top: 10px;
    }
    .dark-table {
        width: 100%;
        border-collapse: collapse;
        color: #e2e8f0;
        font-size: 0.9rem;
    }
    .dark-table th {
        background-color: #1e2333;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        padding: 12px 16px;
        text-align: left;
        border-bottom: 1px solid #2d3548;
    }
    .dark-table td {
        padding: 14px 16px;
        border-bottom: 1px solid #1e2333;
    }
    .dark-table tr:hover {
        background-color: #1a1f2e;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER TOP BAR (FINTECH STYLE)
# ==========================================
st.markdown("""
<div class="app-header">
    <div>
        <div class="app-title">⚡ Analista de Bolso</div>
        <div class="app-subtitle">Terminal de Inteligência Financeira & Análises Quantitativas</div>
    </div>
    <div class="profile-badge">
        🎯 Scanner Diário de Oportunidades
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# GERENCIAMENTO DE ESTADO E NAVEGAÇÃO COMPACTA
# ==========================================
if 'aba_ativa' not in st.session_state:
    st.session_state.aba_ativa = "cripto"

# Agrupando os botões no centro/esquerda em colunas menores
col_nav_1, col_nav_2, col_nav_3, _ = st.columns([1.2, 1.2, 1.5, 3])

with col_nav_1:
    if st.button("🪙 Cripto"):
        st.session_state.aba_ativa = "cripto"

with col_nav_2:
    if st.button("📈 Ações B3"):
        st.session_state.aba_ativa = "acoes"

with col_nav_3:
    if st.button("💡 Pílulas de conhecimento"):
        st.session_state.aba_ativa = "pilulas"

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# ==========================================
# FUNÇÕES DE COLETA DE DADOS (APIs)
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
        params = {
            'vs_currency': 'brl',
            'order': 'market_cap_desc',
            'per_page': 25,
            'page': 1,
            'sparkline': 'false',
            'price_change_percentage': '24h'
        }
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
            return {
                'last_price': float(res['lastPrice']),
                'high': float(res['highPrice']),
                'low': float(res['lowPrice']),
                'change_pct': float(res['priceChangePercent'])
            }
    except Exception:
        pass
    
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
        res = requests.get(url, timeout=5).json()
        md = res['market_data']
        return {
            'last_price': float(md['current_price']['brl']),
            'high': float(md['high_24h']['brl']),
            'low': float(md['low_24h']['brl']),
            'change_pct': float(md['price_change_percentage_24h'])
        }
    except Exception:
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
# CONTEÚDO DAS TELAS
# ==========================================

# ------------------------------------------
# TELA 1: CRIPTO
# ------------------------------------------
if st.session_state.aba_ativa == "cripto":
    fg_val, fg_status = get_fear_and_greed()
    btc_data = get_btc_data()

    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Sentimento Mercado (Fear & Greed)</div>
            <div class="metric-value">{fg_val} <span style="font-size: 1rem; color: #94a3b8;">/100</span></div>
            <div style="margin-top: 8px;">
                <span class="{ 'status-red' if fg_val <= 30 else 'status-amber' if fg_val <= 60 else 'status-green' }">{fg_status.upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        btc_price = f"R$ {btc_data['last_price']:,.2f}" if btc_data['last_price'] > 0 else "N/A"
        btc_var = f"{btc_data['change_pct']:+.2f}%"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Bitcoin (BTC/BRL)</div>
            <div class="metric-value" style="font-size: 1.4rem;">{btc_price}</div>
            <div style="margin-top: 8px;">
                <span class="{ 'status-green' if btc_data['change_pct'] >= 0 else 'status-red' }">{btc_var} (24h)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        btc_high = f"R$ {btc_data['high']:,.2f}" if btc_data['high'] > 0 else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Máxima 24h (BTC)</div>
            <div class="metric-value" style="font-size: 1.4rem;">{btc_high}</div>
            <div style="margin-top: 8px;"><span class="status-amber">Topo Diário</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        btc_low = f"R$ {btc_data['low']:,.2f}" if btc_data['low'] > 0 else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Mínima 24h (BTC)</div>
            <div class="metric-value" style="font-size: 1.4rem;">{btc_low}</div>
            <div style="margin-top: 8px;"><span class="status-amber">Suporte Diário</span></div>
        </div>
        """, unsafe_allow_html=True)

    if fg_val <= 30:
        st.markdown("""
        <div class="info-card info-card-green">
            <h4 style="margin:0; color:#10b981;">💡 Análise do Bot: Mercado em Medo Extremo</h4>
            <p style="margin-top:6px; margin-bottom:0; color:#cbd5e1; font-size:0.9rem;">
                Historicamente, compras fracionadas durante períodos de pânico geram as maiores assimetrias de retorno no médio/longo prazo. Evite alavancagem.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("📊 Top Criptomoedas & Sinais Quant")
    df_crypto = get_coingecko_top_cryptos()
    
    if not df_crypto.empty:
        def gerar_sinal(row):
            var = row.get('price_change_percentage_24h', 0) or 0
            if var < -6.0:
                return "<span class='status-green'>🟢 Oportunidade (Queda)</span>"
            elif var > 10.0:
                return "<span class='status-red'>🔴 Esticado</span>"
            else:
                return "<span class='status-amber'>🟡 Neutro</span>"

        rows_html = ""
        for _, row in df_crypto.iterrows():
            var = row.get('price_change_percentage_24h', 0) or 0
            var_color = "#10b981" if var >= 0 else "#ef4444"
            sinal = gerar_sinal(row)
            
            rows_html += f"""
            <tr>
                <td><b>{row['name']}</b></td>
                <td><span style='color:#94a3b8;'>{row['symbol'].upper()}</span></td>
                <td>R$ {row['current_price']:,.2f}</td>
                <td style='color:{var_color}; font-weight:600;'>{var:+.2f}%</td>
                <td>R$ {row['market_cap']:,.0f}</td>
                <td>{sinal}</td>
            </tr>
            """

        table_html = f"""
        <div class="dark-table-container">
            <table class="dark-table">
                <thead>
                    <tr>
                        <th>Ativo</th>
                        <th>Símbolo</th>
                        <th>Preço (R$)</th>
                        <th>Variação 24h</th>
                        <th>Cap. Mercado</th>
                        <th>Análise Quant</th>
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
# TELA 2: AÇÕES B3 (COM PAINEL DE FILTROS)
# ------------------------------------------
elif st.session_state.aba_ativa == "acoes":
    st.markdown("""
    <div class="info-card info-card-blue">
        <h4 style="margin:0; color:#60a5fa;">🔎 Monitor de Ações da B3 com Filtros Customizados</h4>
        <p style="margin-top:6px; margin-bottom:0; color:#cbd5e1; font-size:0.9rem;">
            Ajuste os parâmetros abaixo para encontrar Penny Stocks, empresas descontadas (P/VP < 1.0) ou pagadoras de dividendos.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # PAINEL DE FILTROS DINÂMICOS
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        preco_max = st.slider("Preço Máximo da Ação (R$):", 1.0, 100.0, 50.0)
    with col_f2:
        pvp_max = st.slider("P/VP Máximo (Desconto):", 0.2, 3.0, 1.5)
    with col_f3:
        filtro_categoria = st.selectbox("Categoria:", ["Todas", "Penny Stocks (< R$ 2.00)", "Descontadas (P/VP < 0.85)", "Dividendos"])
    with col_f4:
        busca_ticker = st.text_input("Buscar Ticker / Nome:", "").upper()

    # Lista ampliada de tickers para escaneamento
    tickers_b3 = [
        "ENJU3", "BHIA3", "OIBR3", "CASH3", "VIVR3", 
        "BBAS3", "PETR4", "VALE3", "ITSA4", "WEGE3", 
        "MGLU3", "LREN3", "USIM5", "CSNA3", "CMIN3"
    ]
    
    with st.spinner("Escaneando mercado B3..."):
        df_stocks = get_b3_stocks(tickers_b3)

    if not df_stocks.empty:
        # APLICANDO FILTROS
        df_filtered = df_stocks.copy()
        
        # Filtro de Preço
        df_filtered = df_filtered[df_filtered['Preço (R$)'] <= preco_max]
        
        # Filtro de P/VP
        df_filtered = df_filtered[df_filtered['P/VP'] <= pvp_max]
        
        # Filtro de Categoria
        if filtro_categoria == "Penny Stocks (< R$ 2.00)":
            df_filtered = df_filtered[df_filtered['Preço (R$)'] < 2.0]
        elif filtro_categoria == "Descontadas (P/VP < 0.85)":
            df_filtered = df_filtered[(df_filtered['P/VP'] > 0) & (df_filtered['P/VP'] < 0.85)]
        elif filtro_categoria == "Dividendos":
            df_filtered = df_filtered[df_filtered['DY (%)'] > 5.0]

        # Filtro por Busca de Texto
        if busca_ticker:
            df_filtered = df_filtered[
                df_filtered['Ticker'].str.contains(busca_ticker) | 
                df_filtered['Empresa'].str.upper().str.contains(busca_ticker)
            ]

        # Renderização da Tabela Dark
        rows_html = ""
        for _, row in df_filtered.iterrows():
            preco = row['Preço (R$)']
            pvp = row['P/VP']
            
            if preco < 2.0:
                status = "<span class='status-red'>⚡ Penny Stock</span>"
            elif 0 < pvp < 0.85:
                status = "<span class='status-green'>🟢 Descontada (P/VP < 0.85)</span>"
            else:
                status = "<span class='status-amber'>🔵 Acompanhar</span>"

            rows_html += f"""
            <tr>
                <td><b>{row['Ticker']}</b></td>
                <td><span style='color:#94a3b8;'>{row['Empresa']}</span></td>
                <td>R$ {row['Preço (R$)']:.2f}</td>
                <td>{row['P/VP'] if row['P/VP'] > 0 else 'N/A'}</td>
                <td>{row['P/L'] if row['P/L'] > 0 else 'N/A'}</td>
                <td style='color:#10b981;'>{row['DY (%)']:.2f}%</td>
                <td>{status}</td>
            </tr>
            """

        if rows_html == "":
            st.warning("Nenhuma ação encontrada com os filtros selecionados. Tente aumentar o preço máximo ou o P/VP.")
        else:
            table_html = f"""
            <div class="dark-table-container">
                <table class="dark-table">
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
# TELA 3: PÍLULAS DE CONHECIMENTO
# ------------------------------------------
elif st.session_state.aba_ativa == "pilulas":
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("""
        <div class="info-card info-card-blue">
            <span class="status-amber">Análise Fundamentalista</span>
            <h3 style="color:#ffffff; margin-top:10px;">1. O que é P/VP?</h3>
            <p style="color:#94a3b8; font-size:0.9rem; line-height:1.6;">
                P/VP é o <b>Preço dividido pelo Valor Patrimonial</b>. Um P/VP de 0.8 significa que você compra R$ 1,00 de patrimônio por R$ 0,80. É a métrica nº 1 para achar barganhas.
            </p>
        </div>
        <div class="info-card info-card-red">
            <span class="status-red">Gestão de Risco</span>
            <h3 style="color:#ffffff; margin-top:10px;">2. Perigo das Penny Stocks</h3>
            <p style="color:#94a3b8; font-size:0.9rem; line-height:1.6;">
                Ações abaixo de R$ 1,00 sofrem pressão para <b>agrupamento</b>. O valor que você possui não muda no agrupamento, mas a ação ganha margem para cair mais. Coloque no máximo 1% do capital.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p2:
        st.markdown("""
        <div class="info-card info-card-green">
            <span class="status-green">Mercado Cripto</span>
            <h3 style="color:#ffffff; margin-top:10px;">3. Fear & Greed Index</h3>
            <p style="color:#94a3b8; font-size:0.9rem; line-height:1.6;">
                Mede o sentimento do mercado. Comprar na euforia (Greed) costuma gerar prejuízos. Comprar gradativamente no pavor (Fear) gera assimetrias gigantescas.
            </p>
        </div>
        <div class="info-card info-card-blue">
            <span class="status-amber">Estratégia Quant</span>
            <h3 style="color:#ffffff; margin-top:10px;">4. Assimetria Positiva</h3>
            <p style="color:#94a3b8; font-size:0.9rem; line-height:1.6;">
                Buscar investimentos onde seu risco máximo é perder R$ 200, mas o ganho potencial é virar R$ 1.500+. Você não precisa acertar todas, apenas ganhar grande nas certas.
            </p>
        </div>
        """, unsafe_allow_html=True)
