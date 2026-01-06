import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página com tema definido
st.set_page_config(page_title="CS Intelligence Pro", layout="wide")

# CSS Customizado para evitar partes "invisíveis" e melhorar o visual
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; }
    h1, h2, h3 { color: #1E3A8A; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stDataFrame { background-color: white; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Inteligência de CS | Gestão de Fidelidade")
st.markdown("---")

# Inicializar base de dados
if 'dados_cs' not in st.session_state:
    st.session_state.dados_cs = pd.DataFrame(columns=[
        "Ano", "Empresa", "Evento", "Cota", "Valor", "Participou"
    ])

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📥 Entrada de Dados")
    with st.form("form_entrada", clear_on_submit=True):
        ano = st.selectbox("Ano de Participação", [2024, 2025, 2026, 2027])
        empresa = st.text_input("Nome da Empresa")
        evento = st.selectbox("Evento", ["IoT", "TBEN", "SCECWB", "Outros"])
        cota = st.selectbox("Cota", ["Aliance", "Global", "Local", "Event", "Exhibitor"])
        valor = st.number_input("Valor do Investimento (R$)", min_value=0.0, step=500.0)
        confirmado = st.checkbox("Participação Confirmada?", value=True)
        
        if st.form_submit_button("Registrar Participação"):
            if empresa:
                nova_linha = pd.DataFrame([{
                    "Ano": ano, "Empresa": empresa, "Evento": evento, 
                    "Cota": cota, "Valor": valor, "Participou": "Sim" if confirmado else "Não"
                }])
                st.session_state.dados_cs = pd.concat([st.session_state.dados_cs, nova_linha], ignore_index=True)
                st.success(f"Registrado: {empresa} ({ano})")
            else:
                st.error("Nome da empresa obrigatório.")

    st.markdown("---")
    if st.button("🗑️ Resetar App"):
        st.session_state.dados_cs = pd.DataFrame(columns=["Ano", "Empresa", "Evento", "Cota", "Valor", "Participou"])
        st.rerun()

# --- DASHBOARD ---
df = st.session_state.dados_cs

if not df.empty:
    # 1. Regras de Fidelidade Atualizadas
    resumo_fid = []
    for emp in df['Empresa'].unique():
        # Filtra participações confirmadas daquela empresa
        pontos = len(df[(df['Empresa'] == emp) & (df['Participou'] == "Sim")])
        
        if pontos >= 8: 
            cat = "💎 Platinum"
            cor = "#E5E4E2"
        elif pontos >= 4: 
            cat = "🥇 Gold"
            cor = "#FFD700"
        elif pontos >= 2: 
            cat = "🥈 Silver"
            cor = "#C0C0C0"
        else: 
            cat = "Abaixo do Ranking"
            cor = "#FFFFFF"
        
        resumo_fid.append({"Empresa": emp, "Pontos": pontos, "Categoria": cat})
    
    df_fid = pd.DataFrame(resumo_fid)

    # 2. Métricas Visuais
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Empresas Únicas", len(df['Empresa'].unique()))
    m2.metric("Receita Total", f"R$ {df['Valor'].sum():,.2f}")
    m3.metric("Participações", len(df[df['Participou'] == "Sim"]))
    m4.metric("Ticket Médio", f"R$ {df['Valor'].mean():,.2f}" if len(df)>0 else 0)

    st.markdown("### 🏆 Ranking de Fidelidade")
    c1, c2 = st.columns([1.2, 1])
    
    with c1:
        # Tabela formatada
        st.dataframe(
            df_fid.sort_values("Pontos", ascending=False), 
            hide_index=True, 
            use_container_width=True
        )
    
    with c2:
        # Gráfico de Rosca com as cores certas
        fig = px.pie(
            df_fid[df_fid['Categoria'] != "Abaixo do Ranking"], 
            names='Categoria', 
            hole=0.5,
            color='Categoria',
            color_discrete_map={
                "💎 Platinum": "#708090",
                "🥇 Gold": "#FFD700",
                "🥈 Silver": "#C0C0C0"
            }
        )
        fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔍 Histórico de Lançamentos")
    st.dataframe(df.sort_values("Ano", ascending=False), use_container_width=True)
    
    # Exportação
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Base de Dados (CSV)", data=csv, file_name="cs_data_export.csv")

else:
    st.info("💡 O dashboard aparecerá aqui assim que você registrar a primeira participação no menu lateral.")
