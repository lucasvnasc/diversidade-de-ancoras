#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="Índice de Diversidade de Texto Âncora",
    page_icon="🔗",
    layout="wide",
)

st.title("Análise de diversidade de texto âncora")
st.markdown("""Esta ferramenta calcula o índice de diversidade dos textos âncoras usados nos links internos de cada página. Para isso, utiliza o Índice Herfindahl-Hirschman (IHH), que varia de 0 a 1. Quanto mais próximo de 1, menos diverso são, quanto mais próximo de 0, mais diverso é. Índice de diversidade abaixo de 0,15 tendem a ser considerados bons.""")

arquivo_links = st.file_uploader("Escolha o arquivo CSV de inlinks", type="csv")

if arquivo_links is not None:
    try:
        dados = pd.read_csv(arquivo_links)
        colunas_necessarias = ['From', 'To', 'Link Position', 'Anchor Text']
        if not all(col in dados.columns for col in colunas_necessarias):
            st.error(f"O arquivo não possui todas as colunas necessárias ou possuem nomes diferentes:{colunas_necessarias}")
        else:
            with st.spinner(text="Carregando dados..."):
                dados = dados.dropna(subset=['Anchor Text'])
                dados['Anchor Text'] = dados['Anchor Text'].astype(str).str.lower()
                grupo = dados.groupby(['To', 'Anchor Text']).size().reset_index(name='Contagem')
                ancoras_por_url = grupo.groupby('To')['Contagem'].sum().reset_index(name='Links_Unicos')
                indice_diversidade = []
                progress_bar = st.progress(0)
                total_iterations = len(ancoras_por_url)
                for i, (url, total_anchors) in enumerate(ancoras_por_url[['To','Contagem']].values):
                    dados_url = grupo[grupo['To'] == url]
                    contribuicoes = [(count / total_anchors) ** 2 for count in dados_url['Contagem']]
                    indice_diversidade = sum(constribuicoes)
                    indice_diversidade_resultado.append({'URL': url, 'Links Unicos': total_anchors, 'Índice de Diversidade': indice_diversidade})
                    if i % 100 == 0:
                        progress_bar.progress((i + 1) / total_iterations)
                progress_bar.progress(100)

                resultado_df = pd.DataFrame(indice_diversidade_resultado)
                resultado_df.sort_values(by='Links Unicos', ascending=False, inplace=True)

                st.success("Índice calculado")
                st.subheader("Pré-visualização dos Dados")
                csv_buffer = resultado_df.to_scv(index=False).enconde('utf-8')

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

