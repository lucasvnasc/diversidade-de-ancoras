import streamlit as st
import pandas as pd

# Configuração da página deve ser a primeira linha executável
st.set_page_config(
    page_title="Audit de Texto Âncora (IHH)",
    page_icon="🔗",
    layout="wide"
)

# --- CSS PERSONALIZADO (Opcional, para dar um polimento extra) ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO COM CACHE (Para performance) ---
@st.cache_data
def processar_dados(arquivo):
    # Lógica de processamento isolada para ganhar velocidade
    dados = pd.read_csv(arquivo)
    
    # Filtros
    dados = dados[dados['From'] != dados['To']]
    dados = dados[dados['Link Position'] == 'Content']
    dados = dados.dropna(subset=['Anchor Text'])
    dados['Anchor Text'] = dados['Anchor Text'].astype(str).str.lower()
    
    grupo = dados.groupby(['To', 'Anchor Text']).size().reset_index(name='Contagem')
    ancoras_por_url = grupo.groupby('To')['Contagem'].sum().reset_index(name='Links_Unicos')
    
    resultados = []
    
    # Loop de cálculo
    # Nota: Em pandas puro seria mais rápido que 'for', mas mantive sua lógica para clareza
    for url, total_anchors in ancoras_por_url[['To','Links_Unicos']].values:
        dados_url = grupo[grupo['To'] == url]
        contribuicoes = [(count / total_anchors) ** 2 for count in dados_url['Contagem']]
        ihh = sum(contribuicoes)
        resultados.append({
            'URL': url, 
            'Links Totais': total_anchors, 
            'IHH Score': ihh,
            'Status': 'Otimizado' if ihh < 0.2 else ('Atenção' if ihh < 0.5 else 'Perigoso')
        })
        
    df = pd.DataFrame(resultados)
    df.sort_values(by='Links Totais', ascending=False, inplace=True)
    return df

# --- BARRA LATERAL (Controles) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2620/2620581.png", width=50) # Ícone ilustrativo
    st.title("Configurações")
    arquivo_links = st.file_uploader("📂 Carregar 'inlinks.csv'", type="csv", help="Exporte este arquivo do Screaming Frog ou similar.")
    
    st.divider()
    st.markdown("### ℹ️ Como interpretar")
    st.info("""
    **IHH Score:**
    - 🟢 **< 0.15:** Ótima diversidade (Seguro)
    - 🟡 **0.15 - 0.5:** Diversidade Média
    - 🔴 **> 0.5:** Baixa diversidade (Risco de Spam)
    """)

# --- ÁREA PRINCIPAL ---
st.title("🔗 Auditoria de Diversidade de Âncora")
st.markdown("Analise o risco de *over-optimization* (sobre-otimização) dos seus textos âncora internos.")

if arquivo_links is not None:
    try:
        # Chama a função de processamento com loading automático
        with st.spinner('Calculando métricas complexas...'):
            df_resultado = processar_dados(arquivo_links)

        # --- DASHBOARD DE MÉTRICAS (Resumo visual) ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Páginas Analisadas", len(df_resultado))
        with col2:
            media_ihh = df_resultado['IHH Score'].mean()
            st.metric("IHH Médio do Site", f"{media_ihh:.3f}", delta_color="inverse")
        with col3:
            paginas_risco = len(df_resultado[df_resultado['IHH Score'] > 0.5])
            st.metric("Páginas em Risco (>0.5)", paginas_risco, delta="-High Risk", delta_color="inverse")

        st.divider()

        # --- FILTROS INTERATIVOS ---
        filtro_status = st.multiselect(
            "Filtrar por Status:",
            options=['Otimizado', 'Atenção', 'Perigoso'],
            default=['Atenção', 'Perigoso'] # Já vem filtrado no que importa
        )
        
        # Aplicando filtro
        df_view = df_resultado[df_resultado['Status'].isin(filtro_status)]

        # --- TABELA INTERATIVA (Dataframe turbinado) ---
        st.subheader("📋 Detalhamento por URL")
        
        st.dataframe(
            df_view,
            use_container_width=True,
            column_config={
                "URL": st.column_config.LinkColumn("Destination URL"),
                "IHH Score": st.column_config.ProgressColumn(
                    "Risco (IHH)",
                    help="Quanto maior a barra, menor a diversidade",
                    format="%.3f",
                    min_value=0,
                    max_value=1,
                ),
                "Links Totais": st.column_config.NumberColumn("Qtd. Backlinks"),
            },
            hide_index=True
        )

        # --- BOTÃO DE DOWNLOAD ---
        st.download_button(
            label="📥 Baixar Relatório Completo",
            data=df_resultado.to_csv(index=False).encode('utf-8'),
            file_name="auditoria_ancoras_seo.csv",
            mime="text/csv",
            type="primary"
        )

    except Exception as e:
        st.error(f"Erro ao processar arquivo. Verifique se as colunas 'From', 'To', 'Link Position' e 'Anchor Text' existem.")
        with st.expander("Ver detalhes do erro"):
            st.write(e)

else:
    # Estado inicial (Vazio)
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h3>👈 Comece fazendo upload do arquivo na barra lateral</h3>
    </div>
    """, unsafe_allow_html=True)
