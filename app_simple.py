"""
Football Scanner AI - Streamlit Online Version (Self-Contained)
Rode com: streamlit run app_simple.py

SETUP ONLINE (Streamlit Cloud):
1. Vá para https://streamlit.io/cloud
2. Clique "Create app"
3. Cole ESTE código inteiro em app.py
4. Clique Deploy
"""

import streamlit as st
from datetime import datetime
import asyncio
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config.settings import settings
    from backend.providers import get_provider
    from backend.core.engine.rule_engine import rule_engine
    from backend.services.monitor_service import MonitorService
    from backend.services.backtest_service import BacktestService
    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚽ Football Scanner AI",
    page_icon="⚽",
    layout="wide",
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    .rule-active { color: #3fb950; }
    .rule-inactive { color: #f85149; }
    .alert-high { border-left: 4px solid #f85149; }
    .alert-medium { border-left: 4px solid #d29922; }
    .alert-low { border-left: 4px solid #58a6ff; }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "monitor" not in st.session_state:
    if HAS_BACKEND:
        st.session_state.monitor = MonitorService()
        st.session_state.backtest = BacktestService()
    st.session_state.last_update = None

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.title("⚽ Football Scanner AI")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Menu",
    ["🏠 Dashboard", "🏟️ Partidas", "📋 Regras", "🔔 Alertas", "📊 Backtest", "📈 Stats"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")

if HAS_BACKEND:
    st.sidebar.info(
        f"""
        **⚙️ Configuração**
        
        • Provider: `{settings.sports_api_provider}`
        • DB: `{settings.db_mode}`
        • Intervalo: `{settings.rule_engine_interval}s`
        • API: `football-data.org v4`
        """
    )
else:
    st.sidebar.warning("Backend não carregado. Configure requirements.txt")

st.sidebar.markdown("---")
st.sidebar.caption("v1.0.0 | 2026")

# ─── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_live_data():
    """Fetch and cache live data."""
    if not HAS_BACKEND:
        return {}, []
    try:
        asyncio.run(st.session_state.monitor._cycle())
        matches = st.session_state.monitor.get_live_matches()
        alerts = st.session_state.monitor.get_alerts()
        return matches, alerts
    except Exception as e:
        st.error(f"Erro: {e}")
        return [], []

# ─── PAGE: DASHBOARD ───────────────────────────────────────────────────────────

if "Dashboard" in page:
    st.title("⚽ Football Scanner AI — Dashboard")
    
    if not HAS_BACKEND:
        st.error("❌ Backend não disponível. Instale: `pip install -r requirements.txt`")
        st.stop()
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    matches, alerts = get_live_data()
    active_alerts = len([a for a in alerts if not a["is_dismissed"]])
    rules = rule_engine.get_rules_info()
    active_rules = len([r for r in rules if r["is_active"]])
    
    with col1:
        st.metric("🎮 Partidas", len(matches))
    with col2:
        st.metric("🔔 Alertas", active_alerts)
    with col3:
        st.metric("📋 Regras", active_rules)
    with col4:
        st.metric("📊 Avaliações", st.session_state.monitor._total_evaluations)
    
    st.divider()
    
    # Refresh
    if st.button("🔄 Atualizar Agora", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("### Partidas em Andamento")
    
    if matches:
        for m in matches:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{m['home_team']}** vs **{m['away_team']}**")
                    st.caption(f"{m['league']} • {m['minute']}'")
                
                with col2:
                    st.metric("Placar", f"{m['home_score']}-{m['away_score']}", label_visibility="collapsed")
                
                with col3:
                    if m["active_alerts"] > 0:
                        st.warning(f"🔴 {m['active_alerts']} alerta(s)")
                    if m["alert_rules"]:
                        for rule in m["alert_rules"][:3]:
                            st.caption(f"📍 {rule}")
    else:
        st.info("Nenhuma partida ao vivo.")
    
    st.markdown("### Alertas Recentes")
    
    if alerts:
        for alert in alerts[:8]:
            with st.container(border=True):
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    priority_emoji = "🔴" if alert["priority"] >= 8 else "🟡" if alert["priority"] >= 6 else "🔵"
                    st.write(f"{priority_emoji} **[{alert['rule_code']}]** {alert['title']}")
                    st.caption(alert["message"][:150] + "...")
                    st.caption(f"{alert['home_team']} vs {alert['away_team']} • {alert['minute']}' • {alert['score']}")
                
                with col2:
                    if st.button("✕", key=f"dismiss_{alert['id']}", help="Dispensar"):
                        st.session_state.monitor.dismiss_alert(alert["id"])
                        st.cache_data.clear()
                        st.rerun()
    else:
        st.info("Sem alertas ativos.")

# ─── PAGE: PARTIDAS ────────────────────────────────────────────────────────────

elif "Partidas" in page:
    st.title("🏟️ Partidas Ao Vivo")
    
    if not HAS_BACKEND:
        st.error("❌ Backend não disponível.")
        st.stop()
    
    if st.button("🔄 Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    matches, _ = get_live_data()
    
    if not matches:
        st.info("Nenhuma partida ao vivo no momento.")
    else:
        for m in matches:
            with st.expander(f"{m['home_team']} vs {m['away_team']} ({m['minute']}')"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Time da Casa**")
                    st.write(f"# {m['home_team']}")
                
                with col2:
                    st.write("**Placar**")
                    st.write(f"# {m['home_score']} - {m['away_score']}")
                
                with col3:
                    st.write("**Time Visitante**")
                    st.write(f"# {m['away_team']}")
                
                st.divider()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"**Liga:** {m['league']}")
                with col2:
                    st.caption(f"**Minuto:** {m['minute']}'")
                with col3:
                    st.caption(f"**Status:** {m['status']}")
                
                if m["alert_rules"]:
                    st.warning(f"**🚨 Regras Ativas:** {', '.join(m['alert_rules'])}")

# ─── PAGE: REGRAS ──────────────────────────────────────────────────────────────

elif "Regras" in page:
    st.title("📋 Gerenciamento de Regras")
    
    if not HAS_BACKEND:
        st.error("❌ Backend não disponível.")
        st.stop()
    
    rules = rule_engine.get_rules_info()
    
    for rule in rules:
        with st.expander(f"[{rule['rule_code']}] {rule['name']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(rule["description"])
                st.caption(f"📂 {rule['category']} • v{rule['version']} • ⭐ {rule['priority']}/10")
            
            with col2:
                status = "✅ Ativa" if rule["is_active"] else "❌ Inativa"
                st.metric("Status", status, label_visibility="collapsed")
            
            if rule["parameters"]:
                st.write("**Parâmetros:**")
                for k, v in rule["parameters"].items():
                    st.text(f"{k}: {v}")

# ─── PAGE: ALERTAS ────────────────────────────────────────────────────────────

elif "Alertas" in page:
    st.title("🔔 Alertas Ativos")
    
    if not HAS_BACKEND:
        st.error("❌ Backend não disponível.")
        st.stop()
    
    if st.button("🔄 Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    _, alerts = get_live_data()
    active = [a for a in alerts if not a["is_dismissed"]]
    
    if not active:
        st.info("Sem alertas ativos.")
    else:
        st.write(f"**Total:** {len(active)} alertas")
        
        for alert in active:
            with st.container(border=True):
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    priority_emoji = "🔴" if alert["priority"] >= 8 else "🟡" if alert["priority"] >= 6 else "🔵"
                    st.write(f"{priority_emoji} **[{alert['rule_code']}]** {alert['title']}")
                    st.write(alert["message"])
                    st.caption(f"{alert['home_team']} vs {alert['away_team']} • {alert['league']} • {alert['minute']}' • {alert['score']}")
                
                with col2:
                    if st.button("✕", key=f"dismiss_{alert['id']}"):
                        st.session_state.monitor.dismiss_alert(alert["id"])
                        st.cache_data.clear()
                        st.rerun()

# ─── PAGE: BACKTEST ────────────────────────────────────────────────────────────

elif "Backtest" in page:
    st.title("📊 Módulo de Backtest")
    
    if not HAS_BACKEND:
        st.error("❌ Backend não disponível.")
        st.stop()
    
    st.warning(
        "⚠️ O backtest apresenta **hipóteses estatísticas** com base em dados históricos. "
        "Não são previsões — são padrões observados."
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        limit = st.slider("Partidas a analisar", 10, 100, 50, 10)
    with col2:
        if st.button("▶ Executar", use_container_width=True):
            with st.spinner("Processando..."):
                result = asyncio.run(st.session_state.backtest.run(limit=limit))
            
            st.success(f"✓ {result['matches_analyzed']} partidas analisadas")
            st.divider()
            
            for rule in result["rules"]:
                with st.expander(f"[{rule['rule_code']}] {rule['rule_name']} — {rule['occurrence_rate_pct']}%"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Ocorrências", f"{rule['occurrences']}/{rule['sample_size']}")
                    with col2:
                        st.metric("Taxa", f"{rule['occurrence_rate_pct']}%")
                    
                    if rule["top_leagues"]:
                        st.write("**Melhores Ligas:**")
                        for lg in rule["top_leagues"]:
                            st.text(f"• {lg['league']}: {lg['occurrences']}x")

# ─── PAGE: STATS ───────────────────────────────────────────────────────────────

elif "Stats" in page:
    st.title("📈 Estatísticas")
    
    if not HAS_BACKEND:
        st.error("❌ Backend não disponível.")
        st.stop()
    
    if st.button("🔄 Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    stats = st.session_state.monitor.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Provider", stats["provider"])
    with col2:
        st.metric("Avaliações", stats["total_evaluations"])
    with col3:
        st.metric("Alertas Gerados", stats["total_alerts_generated"])
    with col4:
        st.metric("Partidas Vivas", stats["live_matches"])
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Configuração**")
        st.text(f"Intervalo: {stats['interval_seconds']}s")
        st.text(f"Alertas ativos: {stats['active_alerts']}")
        st.text(f"Regras ativas: {stats['active_rules']}")
    
    with col2:
        st.write("**Última Atualização**")
        if stats["last_update"]:
            last = datetime.fromisoformat(stats["last_update"])
            st.text(f"{last.strftime('%H:%M:%S')}")
        else:
            st.text("Aguardando primeira atualização")

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("⚽ Football Scanner AI v1.0.0 | Análise estatística de partidas de futebol | 2026")
