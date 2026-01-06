import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CS Intelligence 2026", layout="wide")

# CORREÇÃO DO ESTILO (CSS)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Dashboard de CS - Gestão de Fidelidade")
st.markdown("---")

# Inicializar a base de dados na memória
if 'dados_cs' not in st.session_state:
    st.session_state.dados_cs = pd.DataFrame(columns=[
        "Empresa", "Evento", "Cota", "Valor", "Participou"
    ])

# --- BARRA LATERAL: ENTRADA DE DADOS ---
with st.sidebar:
    st.header("📝 Nova Entrada")
    with st.form("form_entrada", clear_on_submit=True):
        empresa = st.text_input("Nome da Empresa")
        evento = st.selectbox("Evento", ["IoT", "TBEN", "SCECWB", "Outros Eventos"])
        cota = st.selectbox("Cota", ["Aliance", "Global", "Local", "Event", "Exhibitor"])
        valor = st.number_input("Valor do Patrocínio (R$)", min_value=0.0)
        confirmado = st.checkbox("Confirmado (Conta para Fidelidade)")
        
        if st.form_submit_button("Adicionar Dados"):
            if empresa:
                nova_linha = pd.DataFrame([{
                    "Empresa": empresa, "Evento": evento, "Cota": cota, 
                    "Valor": valor, "Participou": "Sim" if confirmado else "Não"
                }])
                st.session_state.dados_cs = pd.concat([st.session_state.dados_cs, nova_linha], ignore_index=True)
                st.success(f"Empresa {empresa} adicionada!")
            else:
                st.error("Digite o nome da empresa.")

    st.markdown("---")
    if st.button("🗑️ Limpar Tudo"):
        st.session_state.dados_cs = pd.DataFrame(columns=["Empresa", "Evento", "Cota", "Valor", "Participou"])
        st.rerun()

# --- DASHBOARD PRINCIPAL ---
df = st.session_state.dados_cs

if not df.empty:
    # 1. Cálculos de Inteligência
    resumo_fid = []
    for emp in df['Empresa'].unique():
        # Conta pontos apenas para quem "Participou == Sim"
        pontos = len(df[(df['Empresa'] == emp) & (df['Participou'] == "Sim")])
        
        if pontos >= 8: cat = "💎 Platinum"
        elif pontos >= 4: cat = "🥇 Gold"
        elif pontos >= 2: cat = "🥈 Silver"
        else: cat = "🥉 Bronze"
        
        resumo_fid.append({"Empresa": emp, "Pontos": pontos, "Categoria": cat})
    
    df_fid = pd.DataFrame(resumo_fid)

    # 2. Métricas Rápidas
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Empresas", len(df['Empresa'].unique()))
    m2.metric("Receita Total", f"R$ {df['Valor'].sum():,.2f}")
    m3.metric("Registros no App", len(df))

    st.markdown("### 🏆 Análise de Fidelidade")
    
    col_tab, col_graf = st.columns([1, 1])
    
    with col_tab:
        st.write("**Ranking por Pontuação**")
        st.dataframe(df_fid.sort_values("Pontos", ascending=False), hide_index=True, use_container_width=True)
    
    with col_graf:
        st.write("**Saúde da Carteira**")
        fig_pie = px.pie(df_fid, names='Categoria', hole=0.4, 
                         color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("### 📋 Histórico Completo")
    st.dataframe(df, use_container_width=True)
    
    # Botão para baixar em CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Exportar Relatório (CSV)", data=csv, file_name="relatorio_cs.csv", mime="text/csv")

else:
    st.info("👋 Bem-vindo! Comece adicionando os dados das empresas no menu lateral para visualizar o ranking e os gráficos.")
