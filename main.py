# importar as bibliotecas
import streamlit as st
import pandas as pd
import yfinance as yf

from tornado.autoreload import start


# criar as funções de carregamento de dados
    # Cotações do Itau - ITUB4 - 2010 a 2024
@st.cache_data
def carregar_dados(empresas):
    texto_tickers = ' '.join(empresas) # join: juntar todas as listas passadas entre parênteses com o separador utilizado entre aspas simples
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(period='1d', start='2010-01-01', end='2024-07-01') # Posso colocar a data final como hoje ou a última data do arquivo, automaticamente?
    cotacoes_acao = cotacoes_acao['Close'] # Para selecionar 1 única coluna e retornar como dataframe e retornar como tabela que tenha índicesde datas e a coluna Close, passar com 2 [[]]
    return cotacoes_acao

@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv('IBOV - Copia.csv', sep=';')
    tickers = list(base_tickers['Código'])
    tickers = [item + '.SA' for item in tickers]
    return tickers

acoes = carregar_tickers_acoes()
dados = carregar_dados(acoes)
# Criar a interface do streamlit
st.title('''App de Ações
O gráfico abaixo representa a evolução do preço das ações ao longo dos anos
''') # markdown - formato de edição de texto simples

# preparar as visualizações = filtros
st.sidebar.header('Filtros')

lista_acoes = st.sidebar.multiselect('Escolha as ações para visualizar', dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: 'Close'})

# filtro de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider('Selecione o período', min_value=data_inicial, max_value=data_final,
                                   value=(data_inicial, data_final))
dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

# criar o gráfico
st.line_chart(dados)

# calculo de performance

texto_performance_ativos = ""

if len(lista_acoes)==0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes)==1:
    dados = dados.rename(columns={'Close': acao_unica})

carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)

for i, acao in enumerate(lista_acoes): # para cada ativo dentro da minha lista de ações
    performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] -1 # valor_final do ativo / pelo valor inicial_ativo -1 // i.loc permite localizar de acordo com a posição dele em uma lista de uma base de dados de pandas. Se for índice 0, está pegando o primeiro item e assim sucessivamente, se for -1, quer dizer que é o último número da coluna.
    performance_ativo = float(performance_ativo)

    carteira[i] = carteira[i] * (1 + performance_ativo)
    
    if performance_ativo > 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n {acao}: :green[{performance_ativo:.1%}]"
    elif performance_ativo < 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n {acao}: :red[{performance_ativo:.1%}]"
    else:
        texto_performance_ativos = texto_performance_ativos + f"  \n {acao}: {performance_ativo:.1%}"

total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira / total_inicial_carteira - 1

if performance_carteira > 0:
    texto_performance_carteira = f"Performance da carteira com todos os ativos: :green[{performance_carteira:.1%}]"
elif performance_ativo < 0:
    texto_performance_carteira = f"Performance da carteira com todos os ativos: :red[{performance_carteira:.1%}]"
else:
    texto_performance_carteira = f"Performance da carteira com todos os ativos: {performance_carteira:.1%}"

st.write(f"\n"
         f"### Performance dos Ativos\n"
         f"Essa foi a performance de cada ativo no período selecionado:\n"
         f"\n"
         f"{texto_performance_ativos}\n"
         
         f"{texto_performance_carteira}\n"
         )