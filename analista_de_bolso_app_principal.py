import streamlit as st
import requests
import pandas as pd
import yfinance as yf

# ==========================================
# CONFIGURAÇÃO DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Analista de Bolso | Executive Terminal",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS limpa
st.markdown("""
<style>
    /* Ocultar elementos nativos desnecessários */
    [data-testid="stSidebar"] { display: none !important; }
    footer { visibility: hidden !important; }
    header { visibility: hidden !important; }

    .block-container {
        padding: 1.5rem 2.5rem !important;
        max-width: 1350px;
    }

    /* Header Executive Deloitte Standard */
    .deloitte-header {
        background: #161b22;
        border-left: 4px solid #86bc25;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
    }
    .deloitte-title { font-size: 1.3rem; font-weight: 700; color: #ffffff; margin: 0; }
    .deloitte-title span { color: #86bc25; }
    .deloitte-subtitle { font-size: 0.8rem; color: #8b949e; margin-top: 2px; }

    /* Métricas */
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1rem;
    }
    .metric-label { font-size: 0.7rem; text-transform: uppercase; color: #8b949e; font-weight: 600; letter-spacing: 0.05em; }
    .metric-val { font-size: 1.4rem; font-weight: 700; color: #ffffff; margin: 4px 0; }
    
    .badge-green { background: rgba(134, 188, 37, 0.15); color: #86bc25; border: 1px solid rgba(134, 188, 37, 0.4); padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .badge-amber { background: rgba(210, 153, 34, 0.15); color: #d29922; border: 1px solid rgba(210, 153, 34, 0.4); padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .badge-red { background: rgba(248, 81, 73, 0.15); color: #f85149; border: 1px solid rgba(248, 81, 73, 0.4); padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("""
<div class="deloitte-header">
    <div>
        <div class="deloitte-title">Analista de Bolso <span>.</span></div>
        <div class="deloitte-subtitle">Terminal de Inteligência Financeira & Valuation Quantitativo</div>
    </div>
    <div>
        <span class="badge-green">DELOITTE & GARTNER STANDARD</span>
    </div>
</div>
""", unsafe_allow_html=True)

# NAVEGAÇÃO DE TOPO
if 'aba_ativa' not in st.session_state:
    st.session_state.aba_ativa = "cripto"

c1, c2, c3, _ = st.columns([1.2, 1.2, 1.5, 4])

with c1:
    if st.button("🪙 Mercado Cripto", use_container_width=True):
        st.session_state.aba_ativa = "cripto"

with c2:
    if st.button("📈 Ações B3", use_container_width=True):
        st.session_state.aba_ativa = "acoes"

with c3:
    if st.button("💡 Pílulas de Conhecimento", use_container_width=True):
        st.session_state.aba_ativa = "pilulas"

st.markdown("<br>", unsafe_allow_html=True)

# FUNÇÕES AUXILIARES
def formatar_moeda(valor):
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

def formatar_cap(valor):
    try:
        if valor >= 1_000_000_000:
            return f"R$ {valor / 1_000_000_000:,.2f}".replace(".", ",") + " Bi"
        elif valor >= 1_000_000:
            return f"R$ {valor / 1_000_000:,.2f}".replace(".", ",") + " Mi"
        return formatar_moeda(valor)
    except Exception:
        return "R$ 0,00"

@st.cache_data(ttl=300)
def get_fear_and_greed():
    try:
        url = "https://api.alternative.me/fng/?limit=1"
        res = requests.get(url, timeout=5).json()
        return int(res['data'][0]['value']), res['data'][0]['value_classification']
    except Exception:
        return 50, "Neutro"

@st.cache_data(ttl=300)
def get_criptos():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {'vs_currency': 'brl', 'order': 'market_cap_desc', 'per_page': 20, 'page': 1, 'sparkline': 'false'}
        res = requests.get(url, params=params, timeout=8).json()
        df = pd.DataFrame(res)
        
        btc = df[df['symbol'] == 'btc'].iloc[0] if not df[df['symbol'] == 'btc'].empty else None
        return df, btc
    except Exception:
        return pd.DataFrame(), None

@st.cache_data(ttl=600)
def get_b3(tickers):
    dados = []
    for t_code in tickers:
        try:
            info = yf.Ticker(f"{t_code}.SA").info
            dados.append({
                'Ticker': t_code,
                'Empresa': info.get('shortName', t_code),
                'Preço': info.get('currentPrice') or info.get('regularMarketPrice') or 0.0,
                'P/VP': round(info.get('priceToBook') or 0.0, 2),
                'P/L': round(info.get('trailingPE') or 0.0, 2),
                'DY (%)': round((info.get('dividendYield') or 0.0) * 100, 2)
            })
        except Exception:
            continue
    return pd.DataFrame(dados)

# CONTEÚDO
if st.session_state.aba_ativa == "cripto":
    fg_val, fg_status = get_fear_and_greed()
    df_c, btc = get_criptos()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Fear & Greed</div><div class="metric-val">{fg_val}/100</div><span class="badge-amber">{fg_status.upper()}</span></div>', unsafe_allow_html=True)
    with m2:
        p_btc = formatar_moeda(btc['current_price']) if btc is not None else "N/A"
        v_btc = btc['price_change_percentage_24h'] if btc is not None else 0
        b_class = "badge-green" if v_btc >= 0 else "badge-red"
        st.markdown(f'<div class="metric-card"><div class="metric-label">Bitcoin (BTC)</div><div class="metric-val">{p_btc}</div><span class="{b_class}">{v_btc:+.2f}% 24h</span></div>', unsafe_allow_html=True)
    with m3:
        h_btc = formatar_moeda(btc['high_24h']) if btc is not None else "N/A"
        st.markdown(f'<div class="metric-card"><div class="metric-label">Máxima 24h</div><div class="metric-val">{h_btc}</div><span class="badge-amber">Topo</span></div>', unsafe_allow_html=True)
    with m4:
        l_btc = formatar_moeda(btc['low_24h']) if btc is not None else "N/A"
        st.markdown(f'<div class="metric-card"><div class="metric-label">Mínima 24h</div><div class="metric-val">{l_btc}</div><span class="badge-amber">Suporte</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Panorama Cripto Global")

    if not df_c.empty:
        df_show = pd.DataFrame({
            'Moeda': df_c['name'],
            'Símbolo': df_c['symbol'].str.upper(),
            'Preço (R$)': df_c['current_price'].apply(formatar_moeda),
            'Variação 24h': df_c['price_change_percentage_24h'].apply(lambda x: f"{x:+.2f}%"),
            'Cap. Mercado': df_c['market_cap'].apply(formatar_cap)
        })
        st.dataframe(df_show, use_container_width=True, hide_index=True, height=450)

elif st.session_state.aba_ativa == "acoes":
    st.subheader("🔎 Monitor de Ações B3")

    f1, f2, f3 = st.columns([1.5, 1.5, 2])
    with f1:
        p_max = st.slider("Preço Máximo (R$):", 1.0, 100.0, 50.0)
    with f2:
        pvp_max = st.slider("P/VP Máximo:", 0.2, 3.0, 1.5)
    with f3:
        busca = st.text_input("Buscar Ticker / Empresa:").upper()

    tickers = ["ENJU3", "BHIA3", "OIBR3", "CASH3", "VIVR3", "BBAS3", "PETR4", "VALE3", "ITSA4", "WEGE3"]
    df_b3 = get_b3(tickers)

    if not df_b3.empty:
        df_f = df_b3[(df_b3['Preço'] <= p_max) & (df_b3['P/VP'] <= pvp_max)].copy()
        if busca:
            df_f = df_f[df_f['Ticker'].str.contains(busca) | df_f['Empresa'].str.upper().str.contains(busca)]

        df_f['Status Bot'] = df_f.apply(lambda r: "⚡ Penny Stock" if r['Preço'] < 2.0 else ("🟢 Descontada" if 0 < r['P/VP'] < 0.85 else "🔵 Regular"), axis=1)
        df_f['Preço (R$)'] = df_f['Preço'].apply(formatar_moeda)
        df_f['DY (%)'] = df_f['DY (%)'].apply(lambda x: f"{x:.2f}%")

        st.dataframe(df_f[['Ticker', 'Empresa', 'Preço (R$)', 'P/VP', 'P/L', 'DY (%)', 'Status Bot']], use_container_width=True, hide_index=True, height=400)

elif st.session_state.aba_ativa == "pilulas":
    st.subheader("💡 Pílulas de Conhecimento Executive")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown('<div class="metric-card" style="margin-bottom:12px;"><h4 style="color:#86bc25;margin:0;">1. O que é P/VP?</h4><p style="color:#8b949e;font-size:0.85rem;margin-top:6px;">Preço sobre Valor Patrimonial. P/VP < 1.0 indica ativo negociado com desconto sobre o patrimônio líquido contábil.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><h4 style="color:#f85149;margin:0;">2. Riscos de Penny Stocks</h4><p style="color:#8b949e;font-size:0.85rem;margin-top:6px;">Ações abaixo de R$ 1,00 possuem volatilidade extrema e risco de agrupamento compulsório. Mantenha gestão de risco rígida.</p></div>', unsafe_allow_html=True)
    with p2:
        st.markdown('<div class="metric-card" style="margin-bottom:12px;"><h4 style="color:#86bc25;margin:0;">3. Fear & Greed Index</h4><p style="color:#8b949e;font-size:0.85rem;margin-top:6px;">Indicador quantitativo de sentimento. Momentos de Medo Extremo oferecem assimetria histórica favorável para aportes fracionados.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><h4 style="color:#d29922;margin:0;">4. Assimetria de Risco</h4><p style="color:#8b949e;font-size:0.85rem;margin-top:6px;">Buscar operações onde o risco de perda é delimitado e conhecido, com potencial multiplicador de ganho substancial.</p></div>', unsafe_allow_html=True)
