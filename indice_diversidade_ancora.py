import streamlit as st
import pandas as pd
st.set_page_config(
    page_title="Índice de Diversidade de Texto Âncora",
    page_icon="🔗",
    layout="centered",
)
st.title("Análise de diversidade de texto âncora")
st.markdown("""Esta ferramenta calcula o índice de diversidade dos textos âncoras usados nos links internos de cada página usando o IHH.""")
arquivo_links = st.file_uploader("Escolha o arquivo CSV de inlinks", type="csv")
if arquivo_links is not None:
    try:
        dados = pd.read_csv(arquivo_links)
        colunas_necessarias = ['From', 'To', 'Link Position', 'Anchor Text'] 
        if not all(col in dados.columns for col in colunas_necessarias):
            st.error(f"O arquivo não possui todas as colunas necessárias: {colunas_necessarias}")
        else:
            with st.spinner(text="Carregando e calculando..."):
                dados = dados[dados['From'] != dados['To']]
                dados = dados[dados['Link Position'] == 'Content']
                dados = dados.dropna(subset=['Anchor Text'])
                dados['Anchor Text'] = dados['Anchor Text'].astype(str).str.lower()
                grupo = dados.groupby(['To', 'Anchor Text']).size().reset_index(name='Contagem')
                ancoras_por_url = grupo.groupby('To')['Contagem'].sum().reset_index(name='Links_Unicos')
                indice_diversidade_resultado = [] 
                progress_bar = st.progress(0)
                total_iterations = len(ancoras_por_url)
                
                for i, (url, total_anchors) in enumerate(ancoras_por_url[['To','Links_Unicos']].values):
                    dados_url = grupo[grupo['To'] == url]
                    contribuicoes = [(count / total_anchors) ** 2 for count in dados_url['Contagem']]
                    valor_ihh = sum(contribuicoes)
                    indice_diversidade_resultado.append({
                        'URL': url, 
                        'Links Unicos': total_anchors, 
                        'Índice de Diversidade': valor_ihh
                    })
                    if i % 100 == 0:
                        progress_bar.progress((i + 1) / total_iterations)
                progress_bar.progress(100)
                resultado_df = pd.DataFrame(indice_diversidade_resultado)
                resultado_df.sort_values(by='Links Unicos', ascending=False, inplace=True)
                st.success("Índice calculado com sucesso!")
                st.subheader("Pré-visualização dos Dados")
                st.dataframe(resultado_df, use_container_width=True)
                csv_buffer = resultado_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Baixar resultados",
                    data=csv_buffer,
                    file_name="indice-diversidade-texto-ancora.csv",
                    mime="text/csv",
                    type="primary"
                )
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
else:
    st.info("Aguardando upload do arquivo com links")
