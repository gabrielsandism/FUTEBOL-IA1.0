"""
Football Scanner AI - Streamlit Online Version
Run: streamlit run app.py
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from config.settings import settings
from backend.providers import get_provider
from backend.core.engine.rule_engine import rule_engine
from backend.services.monitor_service import MonitorService
from backend.services.backtest_service import BacktestService

# Page config
st.set_page_config(
    page_title="⚽ Football Scanner AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state
if "monitor" not in st.session_state:
    st.session_state.monitor = MonitorService()
if "backtest" not in st.session_state:
    st.session_state.backtest = BacktestService()
if "last_update" not in st.session_state:
    st.session_state.last_update = None


# ─── Sidebar Navigation ────────────────────────────────────────────────────────
st.sidebar.title("⚽ Football Scanner AI")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navegação",
    ["Dashboard", "Partidas", "Regras", "Alertas", "Backtest", "Estatísticas"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.info(
    f"""
    **Provider:** {settings.sports_api_provider}
    
    **Modo DB:** {settings.db_mode}
    
    **Intervalo:** {settings.rule_engine_interval}s
    """
)


# ─── Helper Functions ──────────────────────────────────────────────────────────
async def fetch_data():
    """Fetch live data from provider and evaluate rules."""
    monitor = st.session_state.monitor
    try:
        await monitor._cycle()
        st.session_state.last_update = datetime.utcnow()
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")


def refresh_button():
    """Refresh button."""
    if st.button("🔄 Atualizar Agora"):
        asyncio.run(fetch_data())
        st.rerun()


# ─── DASHBOARD ─────────────────────────────────────────────────────────────────
if page == "Dashboard":
    st.title("⚽ Dashboard em Tempo Real")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎮 Partidas Ao Vivo",
            len(st.session_state.monitor._live_matches),
        )
    
    with col2:
        alerts = st.session_state.monitor.get_alerts()
        st.metric(
            "🔔 Alertas Ativos",
            len([a for a in alerts if not a["is_dismissed"]]),
        )
    
    with col3:
        rules = rule_engine.get_rules_info()
        st.metric(
            "📋 Regras Ativas",
            len([r for r in rules if r["is_active"]]),
        )
    
    with col4:
        st.metric(
            "📊 Total de Avaliações",
            st.session_state.monitor._total_evaluations,
        )
    
    st.markdown("---")
    refresh_button()
    
    # Matches
    st.subheader("Partidas em Andamento")
    matches = st.session_state.monitor.get_live_matches()
    
    if matches:
        for m in matches:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{m['home_team']}** vs **{m['away_team']}**")
                    st.caption(f"{m['league']} • {m['minute']}'")
                with col2:
                    st.metric("Placar", f"{m['home_score']} - {m['away_score']}")
                with col3:
                    if m["active_alerts"] > 0:
                        st.warning(f"🔴 {m['active_alerts']} alertas")
                    for rule in m["alert_rules"]:
                        st.caption(f"📍 {rule}")
    else:
        st.info("Nenhuma partida ao vivo no momento.")
    
    # Recent Alerts
    st.subheader("Alertas Recentes")
    alerts = st.session_state.monitor.get_alerts()
    
    if alerts:
        for alert in alerts[:10]:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**[{alert['rule_code']}]** {alert['title']}")
                    st.caption(alert["message"][:200] + "...")
                    st.text(f"{alert['home_team']} vs {alert['away_team']} • {alert['minute']}' • {alert['score']}")
                with col2:
                    if st.button("✕", key=f"dismiss_{alert['id']}"):
                        st.session_state.monitor.dismiss_alert(alert["id"])
                        st.rerun()
    else:
        st.info("Sem alertas ativos.")


# ─── PARTIDAS ─────────────────────────────────────────────────────────────────
elif page == "Partidas":
    st.title("🏟️ Partidas Ao Vivo")
    refresh_button()
    
    matches = st.session_state.monitor.get_live_matches()
    
    if not matches:
        st.info("Nenhuma partida ao vivo.")
    else:
        for m in matches:
            with st.expander(f"{m['home_team']} vs {m['away_team']} ({m['minute']}')"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Time da Casa**")
                    st.write(m['home_team'])
                with col2:
                    st.write(f"**Placar**")
                    st.write(f"# {m['home_score']} - {m['away_score']}")
                with col3:
                    st.write(f"**Time Visitante**")
                    st.write(m['away_team'])
                
                st.divider()
                st.caption(f"**Liga:** {m['league']}")
                st.caption(f"**Minuto:** {m['minute']}'")
                st.caption(f"**Status:** {m['status']}")
                
                if m["alert_rules"]:
                    st.warning(f"**Regras Ativas:** {', '.join(m['alert_rules'])}")


# ─── REGRAS ────────────────────────────────────────────────────────────────────
elif page == "Regras":
    st.title("📋 Gerenciamento de Regras")
    
    rules = rule_engine.get_rules_info()
    
    for rule in rules:
        with st.expander(f"**[{rule['rule_code']}]** {rule['name']}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Descrição:** {rule['description']}")
                st.write(f"**Categoria:** {rule['category']}")
                st.write(f"**Versão:** {rule['version']}")
                st.write(f"**Prioridade:** {rule['priority']}/10")
            
            with col2:
                new_state = st.checkbox(
                    "Ativa",
                    value=rule["is_active"],
                    key=f"rule_{rule['rule_code']}",
                )
                if new_state != rule["is_active"]:
                    rule_engine.set_rule_active(rule["rule_code"], new_state)
                    st.success("Atualizado!")
                    st.rerun()
            
            if rule["parameters"]:
                st.write("**Parâmetros:**")
                for k, v in rule["parameters"].items():
                    st.caption(f"• {k}: {v}")


# ─── ALERTAS ──────────────────────────────────────────────────────────────────
elif page == "Alertas":
    st.title("🔔 Alertas Ativos")
    refresh_button()
    
    alerts = st.session_state.monitor.get_alerts()
    
    if not alerts:
        st.info("Sem alertas ativos.")
    else:
        st.write(f"**Total:** {len(alerts)} alertas")
        
        for alert in alerts:
            with st.container(border=True):
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    priority_emoji = "🔴" if alert["priority"] >= 8 else "🟡" if alert["priority"] >= 6 else "🔵"
                    st.write(f"{priority_emoji} **[{alert['rule_code']}]** {alert['title']}")
                    st.write(alert["message"])
                    st.caption(f"{alert['home_team']} vs {alert['away_team']} • {alert['league']} • {alert['minute']}' • {alert['score']}")
                    st.caption(f"Criado: {datetime.fromisoformat(alert['created_at']).strftime('%H:%M:%S')}")
                
                with col2:
                    col_d, col_x = st.columns(2)
                    with col_d:
                        if st.button("✓", key=f"read_{alert['id']}", help="Marcar como lido"):
                            st.session_state.monitor.mark_read(alert['id'])
                            st.rerun()
                    with col_x:
                        if st.button("✕", key=f"dismiss_{alert['id']}", help="Dispensar"):
                            st.session_state.monitor.dismiss_alert(alert['id'])
                            st.rerun()


# ─── BACKTEST ──────────────────────────────────────────────────────────────────
elif page == "Backtest":
    st.title("📊 Módulo de Backtest")
    
    st.warning(
        "⚠️ **Importante:** O backtest apresenta hipóteses estatísticas com base em dados históricos. "
        "As taxas de ocorrência indicam padrões observados — não garantias de resultado futuro."
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        limit = st.slider("Partidas a analisar", min_value=10, max_value=100, value=50, step=10)
    with col2:
        run_btn = st.button("▶ Executar Backtest", use_container_width=True)
    
    if run_btn:
        with st.spinner("Processando..."):
            result = asyncio.run(st.session_state.backtest.run(limit=limit))
        
        st.success(f"✓ Backtest concluído | {result['matches_analyzed']} partidas analisadas")
        st.divider()
        
        for rule in result["rules"]:
            with st.expander(f"**[{rule['rule_code']}]** {rule['rule_name']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Taxa de Ocorrência",
                        f"{rule['occurrence_rate_pct']}%",
                        f"{rule['occurrences']} / {rule['sample_size']}",
                    )
                
                with col2:
                    st.write(f"**Categoria:** {rule['category']}")
                    st.write(f"**Amostra:** {rule['sample_size']} partidas")
                
                if rule["top_leagues"]:
                    st.write("**Melhores Ligas:**")
                    for league in rule["top_leagues"]:
                        st.caption(f"• {league['league']}: {league['occurrences']}x")
                
                st.caption(rule["note"])


# ─── ESTATÍSTICAS ────────────────────────────────────────────────────────────
elif page == "Estatísticas":
    st.title("📈 Estatísticas do Sistema")
    
    refresh_button()
    
    stats = st.session_state.monitor.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Provider", stats["provider"])
    with col2:
        st.metric("Avaliações Totais", stats["total_evaluations"])
    with col3:
        st.metric("Alertas Gerados", stats["total_alerts_generated"])
    with col4:
        st.metric("Partidas Vivas", stats["live_matches"])
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Configuração**")
        st.write(f"• Intervalo: {stats['interval_seconds']}s")
        st.write(f"• Alertas ativos: {stats['active_alerts']}")
        st.write(f"• Regras ativas: {stats['active_rules']}")
    
    with col2:
        st.write("**Última Atualização**")
        if stats["last_update"]:
            last = datetime.fromisoformat(stats["last_update"])
            elapsed = datetime.utcnow() - last
            st.write(f"• {last.strftime('%H:%M:%S')}")
            st.write(f"• {elapsed.seconds} segundos atrás")
        else:
            st.write("• Aguardando primeira atualização")


# ─── Footer ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.caption("Football Scanner AI v1.0.0 | 2026")
st.sidebar.caption("Sistema de análise estatística de partidas de futebol")
