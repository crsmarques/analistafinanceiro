import streamlit as st
import requests
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# ==========================================
# CONFIGURAÇÃO INICIAL DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Analista de Bolso",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e222d; padding: 15px; border-radius: 10px; border: 1px solid #2a2e39; }
    .pill-card { background-color: #1e222d; padding: 20px; border-radius: 12px; border-left: 5px solid #10b981; margin-bottom: 15px; }
    .risk-card { background-color: #1e222d; padding: 20px; border-radius: 12px; border-left: 5px solid #ef4444; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNÇÕES DE COLETA DE DADOS (APIs)
# ==========================================

@st.cache_data(ttl=300)
def get_fear_and_greed():
    """Busca o Crypto Fear & Greed Index"""
    try:
        url = "https://api.alternative.me/fng/?limit=1"
        res = requests.get(url, timeout=5).json()
        val = int(res['data'][0]['value'])
        status = res['data'][0]['value_classification']
        return val, status
    except Exception:
        return 50, "Neutro (Offline)"

@st.cache_data(ttl=300)
def get_coingecko_top_cryptos():
    """Busca as top criptos do mercado via CoinGecko API"""
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
            return pd.DataFrame(res.json())
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_binance_ticker(symbol="BTCBRL"):
    """Busca dados em tempo real da Binance API pública"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        res = requests.get(url, timeout=5).json()
        return {
            'last_price': float(res['lastPrice']),
            'high': float(res['highPrice']),
            'low': float(res['lowPrice']),
            'change_pct': float(res['priceChangePercent']),
            'volume': float(res['volume'])
        }
    except Exception:
        return None

@st.cache_data(ttl=600)
def get_b3_stock_data(tickers):
    """Busca dados das Ações B3 via yfinance"""
    results = []
    for symbol in tickers:
        try:
            ticker_formatted = f"{symbol}.SA" if not symbol.endswith(".SA") else symbol
            t = yf.Ticker(ticker_formatted)
            info = t.info
            
            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
            pvp = info.get('priceToBook') or 0.0
            pl = info.get('trailingPE') or 0.0
            dy = (info.get('dividendYield') or 0.0) * 100
            name = info.get('shortName') or symbol

            results.append({
                'Ticker': symbol.replace(".SA", ""),
                'Nome': name,
                'Preço (R$)': round(price, 2),
                'P/VP': round(pvp, 2) if pvp else "N/A",
                'P/L': round(pl, 2) if pl else "N/A",
                'DY (%)': round(dy, 2) if dy else 0.0
            })
        except Exception:
            continue
    return pd.DataFrame(results)

# ==========================================
# BARRA LATERAL (NAVEGAÇÃO)
# ==========================================
st.sidebar.title("⚡ Analista de Bolso")
st.sidebar.caption("Seu Copiloto de Investimentos Inteligente")

opcao_menu = st.sidebar.radio(
    "Menu Principais:",
    ["🪙 Criptomoedas & Alertas", "📈 Ações B3 & Penny Stocks", "💡 Pílulas de Aprendizado", "🛡️ Calculadora de Risco (R$ 10k)"]
)

st.sidebar.divider()
st.sidebar.info("**Perfil:** Agressivo Consciente\n\n**Foco:** Preservação de Capital + Assimetria de Risco")

# ==========================================
# ABA 1: CRIPTOMOEDAS & ALERTAS
# ==========================================
if opcao_menu == "🪙 Criptomoedas & Alertas":
    st.title("🪙 Mercado de Criptomoedas & Alertas Quant")
    st.write("Análise em tempo real integrada às APIs CoinGecko, Binance e Alternative.me.")

    fg_val, fg_status = get_fear_and_greed()
    
    col_fg1, col_fg2 = st.columns([1, 2])
    with col_fg1:
        st.metric(label="Sentimento do Mercado (Fear & Greed)", value=f"{fg_val}/100", delta=fg_status)
    
    with col_fg2:
        if fg_val <= 25:
            st.error("🔴 **MEDO EXTREMO:** Pânico no mercado. Zona histórica de oportunidade para compras fracionadas.")
        elif fg_val <= 45:
            st.warning("🟡 **MEDO:** Investidores receosos. Boa hora para analisar projetos sólidos descontados.")
        elif fg_val <= 60:
            st.info("⚪ **NEUTRO:** Mercado sem tendência definida. Siga o plano sem empolgação.")
        else:
            st.success("🟢 **GANÂNCIA / EUFORIA:** Cuidado com compras no topo! Bom momento para proteger lucros.")

    st.divider()

    st.subheader("⚡ Bitcoin em Tempo Real (Binance)")
    btc_data = get_binance_ticker("BTCBRL")
    if btc_data:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"R$ {btc_data['last_price']:,.2f}", f"{btc_data['change_pct']:.2f}% (24h)")
        c2.metric("Mínima 24h", f"R$ {btc_data['low']:,.2f}")
        c3.metric("Máxima 24h", f"R$ {btc_data['high']:,.2f}")
        c4.metric("Volume 24h", f"{btc_data['volume']:,.2f} BTC")

    st.divider()

    st.subheader("📊 Top 20 Criptos & Análise Automática de Sinal")
    df_crypto = get_coingecko_top_cryptos()
    
    if not df_crypto.empty:
        def sinal_crypto(row):
            var_24h = row.get('price_change_percentage_24h', 0) or 0
            if var_24h < -7.0:
                return "🟢 Oportunidade (Queda Forte)"
            elif var_24h > 12.0:
                return "🔴 Risco (Esticou no Curto Prazo)"
            else:
                return "🟡 Neutro / Acompanhar"

        df_crypto['Sinal Automático'] = df_crypto.apply(sinal_crypto, axis=1)
        
        df_show = df_crypto[['name', 'symbol', 'current_price', 'price_change_percentage_24h', 'market_cap', 'Sinal Automático']].copy()
        df_show.columns = ['Moeda', 'Símbolo', 'Preço (R$)', 'Variação 24h (%)', 'Cap. Mercado (R$)', 'Análise da Ferramenta']
        df_show['Símbolo'] = df_show['Símbolo'].str.upper()

        st.dataframe(
            df_show.style.format({
                'Preço (R$)': 'R$ {:,.2f}',
                'Variação 24h (%)': '{:+.2f}%',
                'Cap. Mercado (R$)': 'R$ {:,.0f}'
            }),
            use_container_width=True,
            height=400
        )

# ==========================================
# ABA 2: AÇÕES B3 & PENNY STOCKS
# ==========================================
elif opcao_menu == "📈 Ações B3 & Penny Stocks":
    st.title("📈 Monitor de Ações da B3 & Penny Stocks")
    st.write("Filtro diário de múltiplos de valuation e ações baratas/turnarounds.")

    tickers_monitor = ["ENJU3", "BHIA3", "OIBR3", "CASH3", "VIVR3", "BBAS3", "PETR4", "VALE3", "ITSA4"]
    
    with st.spinner("Buscando cotações atualizadas na B3..."):
        df_stocks = get_b3_stock_data(tickers_monitor)

    if not df_stocks.empty:
        def classificar_acao(row):
            pvp = row['P/VP']
            preco = row['Preço (R$)']
            
            if preco < 2.0:
                return "⚡ Penny Stock / Risco Extremo"
            elif isinstance(pvp, (int, float)) and pvp > 0 and pvp < 0.85:
                return "🟢 Descontada (P/VP < 0.85)"
            else:
                return "🔵 Acompanhar / Dividendos"

        df_stocks['Status do App'] = df_stocks.apply(classificar_acao, axis=1)
        st.dataframe(df_stocks, use_container_width=True)

        st.divider()
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.markdown("""
            <div class="risk-card">
                <h4>⚠️ Alerta de Penny Stocks (ENJU3, OIBR3)</h4>
                <p>Ações na casa dos centavos possuem volatilidade extrema e dependem de reestruturações. Mantenha no máximo 1% a 2% da sua carteira aqui.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_a2:
            st.markdown("""
            <div class="pill-card">
                <h4>🛡️ Âncoras de Carteira (BBAS3, ITSA4)</h4>
                <p>Empresas consolidadas que geram lucros e pagam dividendos. Elas protegem seu patrimônio enquanto você busca assimetria nas apostas maiores.</p>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# ABA 3: PÍLULAS DE APRENDIZADO DIÁRIO
# ==========================================
elif opcao_menu == "💡 Pílulas de Aprendizado":
    st.title("💡 Pílulas Diárias de Mercado Financeiro")

    pilulas = [
        {
            "titulo": "1. O que é P/VP e como usar?",
            "categoria": "Análise Fundamentalista",
            "conteudo": "Preço sobre Valor Patrimonial. Se o P/VP é 0,80, você está comprando R$ 1,00 de patrimônio por R$ 0,80. É um indicador clássico de desconto em ações e FIIs."
        },
        {
            "titulo": "2. O Risco do Agrupamento de Ações",
            "categoria": "Gestão de Risco",
            "conteudo": "Quando uma ação fica abaixo de R$ 1,00 por muito tempo, a B3 obriga o agrupamento (ex: 10 ações viram 1). O valor total que você possui continua igual, mas o ativo ganha espaço para continuar caindo."
        },
        {
            "titulo": "3. O Conceito de Assimetria de Risco",
            "categoria": "Estratégia quantitativa",
            "conteudo": "Assimetria positiva é quando seu risco de perda é fixo e conhecido (ex: perder R$ 200), mas seu potencial de ganho é exponencial (ex: virar R$ 2.000). A chave para acelerar patrimônio é buscar assimetria."
        }
    ]

    for p in pilulas:
        st.markdown(f"""
        <div class="pill-card">
            <span style="background-color: #10b981; color: white; padding: 3px 8px; border-radius: 5px; font-size: 12px;">{p['categoria']}</span>
            <h3 style="margin-top: 10px; color: #f8fafc;">{p['titulo']}</h3>
            <p style="color: #94a3b8; font-size: 16px;">{p['conteudo']}</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# ABA 4: CALCULADORA DE RISCO (R$ 10K)
# ==========================================
elif opcao_menu == "🛡️ Calculadora de Risco (R$ 10k)":
    st.title("🛡️ Calculadora de Gestão de Risco (R$ 10.000)")
    patrimonio = st.number_input("Capital Total (R$):", value=10000.0, step=500.0)

    pct_reserva = st.slider("1. Reserva de Segurança (107% CDI) %:", 50, 95, 85)
    pct_fii = st.slider("2. Ações / FIIs de Renda %:", 5, 30, 10)
    pct_risco = st.slider("3. Assimetria (Cripto / Penny Stocks) %:", 1, 15, 5)

    if (pct_reserva + pct_fii + pct_risco) == 100:
        val_res = patrimonio * (pct_reserva / 100)
        val_fii = patrimonio * (pct_fii / 100)
        val_ris = patrimonio * (pct_risco / 100)

        c1, c2, c3 = st.columns(3)
        c1.metric("1. Segurança (Renda Fixa)", f"R$ {val_res:,.2f}")
        c2.metric("2. Proteção (Dividendos)", f"R$ {val_fii:,.2f}")
        c3.metric("3. Assimetria (Alto Risco)", f"R$ {val_ris:,.2f}")

        fig = go.Figure(data=[go.Pie(
            labels=['Renda Fixa (107% CDI)', 'Ações/FIIs', 'Cripto/Penny Stocks'],
            values=[val_res, val_fii, val_ris],
            hole=.4,
            marker_colors=['#10b981', '#3b82f6', '#ef4444']
        )])
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("A soma das porcentagens precisa fechar em exatamente 100%!")