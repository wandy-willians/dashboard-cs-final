import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CS Intelligence 2026", layout="wide")

# Estilo para os cards de métricas
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_value=True)

st.title("🚀 Dashboard de CS - Gestão de Fidelidade")
st.markdown("---")

# Inicializar a base de dados na memória do navegador
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
                st.success("Adicionado!")
            else:
                st.error("Digite o nome da empresa.")

    if st.button("🗑️ Limpar Todos os Dados"):
        st.session_state.dados_cs = pd.DataFrame(columns=["Empresa", "Evento", "Cota", "Valor", "Participou"])
        st.rerun()

# --- DASHBOARD PRINCIPAL ---
df = st.session_state.dados_cs

if not df.empty:
    # 1. Cálculos de Inteligência
    resumo_fid = []
    for emp in df['Empresa'].unique():
        pontos = len(df[(df['Empresa'] == emp) & (df['Participou'] == "Sim")])
        if pontos >= 8: cat = "💎 Platinum"
        elif pontos >= 4: cat = "🥇 Gold"
        elif pontos >= 2: cat = "🥈 Silver"
        else: cat = "🥉 Bronze"
        resumo_fid.append({"Empresa": emp, "Pontos": pontos, "Categoria": cat})
    
    df_fid = pd.DataFrame(resumo_fid)

    # 2. Métricas de Topo
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Empresas", len(df['Empresa'].unique()))
    m2.metric("Receita Total", f"R$ {df['Valor'].sum():,.2f}")
    m3.metric("Eventos Registados", len(df))

    st.markdown("### 🏆 Ranking de Fidelidade")
    
    # Organizar Colunas: Tabela à esquerda, Gráfico à direita
    c_tab, c_graph = st.columns([1, 1])
    
    with c_tab:
        st.dataframe(df_fid.sort_values("Pontos", ascending=False), hide_index=True, use_container_width=True)
    
    with c_graph:
        fig_pie = px.pie(df_fid, names='Categoria', hole=0.4, title="Saúde da Carteira")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("### 📋 Histórico Detalhado")
    st.dataframe(df, use_container_width=True)
    
    # Botão para baixar em Excel (CSV)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descarregar Dados (CSV)", data=csv, file_name="relatorio_cs.csv", mime="text/csv")

else:
    st.warning("Aguardando entrada de dados no menu lateral para gerar as análises.")
