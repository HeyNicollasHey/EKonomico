
import pandas as pd
import plotly.express as px

def lerdados():
    dados = pd.read_csv('dados.csv')
    return dados

def analyze_sales(produto):
    dados = lerdados()

    # Filtrar os dados para o produto específico
    dados_produto = dados[dados['nome_produto'] == produto]

    # Converter a coluna 'data_compra' para o tipo datetime
    dados_produto['data_compra'] = pd.to_datetime(dados_produto['data_compra'])

    # Extrair o mês e o ano da data de compra
    dados_produto['Mes'] = dados_produto['data_compra'].dt.to_period('M')

    # Calcular a quantidade de vendas por mês
    vendas_por_mes = dados_produto.groupby('Mes').size().reset_index(name='Quantidade_Vendas')

    # Gerar o gráfico de barras
    fig = px.bar(vendas_por_mes, x='Mes', y='Quantidade_Vendas', title=f'Quantidade de Vendas de {produto} por Mês')

    return fig.to_html(full_html=False)