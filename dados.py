import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import seaborn as sns

# Carregando os DataFrames
df_clientes = pd.read_csv("Brazilian E-Commerce Public Dataset by Olist/olist_customers_dataset.csv")
df_geolocalizacao = pd.read_csv("Brazilian E-Commerce Public Dataset by Olist/olist_geolocation_dataset.csv")
df_itens_pedidos = pd.read_csv("Brazilian E-Commerce Public Dataset by Olist/olist_order_items_dataset.csv")
df_pagamentos_pedidos = pd.read_csv("Brazilian E-Commerce Public Dataset by Olist/olist_order_payments_dataset.csv")
df_avaliacoes_pedido = pd.read_csv("Brazilian E-Commerce Public Dataset by Olist/olist_order_reviews_dataset.csv")
df_pedidos = pd.read_csv("Brazilian E-Commerce Public Dataset by Olist/olist_orders_dataset.csv")
df_produtos = pd.read_csv("Brazilian E-Commerce Public Dataset by Olist/olist_products_dataset.csv")
df_vendedores = pd.read_csv("Brazilian E-Commerce Public Dataset by Olist/olist_sellers_dataset.csv")
df_traducao_categoria = pd.read_csv("Brazilian E-Commerce Public Dataset by Olist/product_category_name_translation.csv")

# Tratando valores ausentes
df_pedidos['order_approved_at'].fillna('data indisponível', inplace=True)
df_pedidos['order_delivered_carrier_date'].fillna('data indisponível', inplace=True)
df_pedidos['order_delivered_customer_date'].fillna('data indisponível', inplace=True)
df_avaliacoes_pedido['review_comment_message'].fillna('sem comentários', inplace=True)

# 1 - Análise de Performance de Vendas
print('1. Análise de Performance de Vendas')
print('\na. Volume de Vendas por Categoria: Identificar quais categorias de produtos têm o maior volume de vendas e em quais períodos (mensal, trimestral)')

# Convertendo as colunas de datas para o tipo datetime
df_pedidos['order_approved_at'] = pd.to_datetime(df_pedidos['order_approved_at'], errors='coerce')

# Extraindo o mês e o trimestre do timestamp de aprovação do pedido
df_pedidos['order_month'] = df_pedidos['order_approved_at'].dt.to_period('M')
df_pedidos['order_quarter'] = df_pedidos['order_approved_at'].dt.to_period('Q')

# Mesclando os DataFrames para obter informações sobre os produtos e datas dos pedidos
merged_df = pd.merge(df_itens_pedidos, df_pedidos, on='order_id', how='inner')
merged_df = pd.merge(merged_df, df_produtos, on='product_id', how='inner')

# Agrupando os dados por mês e categoria de produto e calculando o volume de vendas, média e mediana
volume_vendas_por_categoria_e_mes = merged_df.groupby(['order_month', 'product_category_name'])[['order_id', 'order_approved_at']].count().reset_index()
volume_vendas_por_categoria_e_mes['volume_vendas'] = volume_vendas_por_categoria_e_mes['order_id']
volume_vendas_por_categoria_e_mes['media_vendas'] = volume_vendas_por_categoria_e_mes['order_approved_at'].mean()
volume_vendas_por_categoria_e_mes['mediana_vendas'] = volume_vendas_por_categoria_e_mes['order_approved_at'].median()

# Agrupando os dados por trimestre e categoria de produto e calculando o volume de vendas, média e mediana
volume_vendas_por_categoria_e_trimestre = merged_df.groupby(['order_quarter', 'product_category_name'])[['order_id', 'order_approved_at']].count().reset_index()
volume_vendas_por_categoria_e_trimestre['volume_vendas'] = volume_vendas_por_categoria_e_trimestre['order_id']
volume_vendas_por_categoria_e_trimestre['media_vendas'] = volume_vendas_por_categoria_e_trimestre['order_approved_at'].mean()
volume_vendas_por_categoria_e_trimestre['mediana_vendas'] = volume_vendas_por_categoria_e_trimestre['order_approved_at'].median()

# Filtrando apenas as top 10 categorias para cada período
top_10_categorias_mes = volume_vendas_por_categoria_e_mes.groupby('product_category_name')['volume_vendas'].sum().nlargest(10).index
volume_vendas_por_categoria_e_mes = volume_vendas_por_categoria_e_mes[volume_vendas_por_categoria_e_mes['product_category_name'].isin(top_10_categorias_mes)]

top_10_categorias_trimestre = volume_vendas_por_categoria_e_trimestre.groupby('product_category_name')['volume_vendas'].sum().nlargest(10).index
volume_vendas_por_categoria_e_trimestre = volume_vendas_por_categoria_e_trimestre[volume_vendas_por_categoria_e_trimestre['product_category_name'].isin(top_10_categorias_trimestre)]

# Gerar cores sólidas para todos os períodos de tempo únicos
all_periods = set(volume_vendas_por_categoria_e_mes['order_month']) | set(volume_vendas_por_categoria_e_trimestre['order_quarter'])
cores = dict(zip(all_periods, sns.color_palette("husl", len(all_periods))))

# Gráfico Mensal
plt.figure(figsize=(12, 6))
ax = sns.barplot(
  x="product_category_name",
  y="volume_vendas",
  hue="order_month",
  data=volume_vendas_por_categoria_e_mes,
  palette=cores
)

# Personalizando o gráfico
plt.xlabel("Categoria de Produto")
plt.ylabel("Volume de Vendas")
plt.title("Top 10 Volume de Vendas por Categoria de Produto Mensal", fontweight='bold')
plt.xticks(rotation=90)
plt.legend(title=r"$\bf{Ano\ e\ Mês}$", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Exibindo o gráfico
plt.show()

# Gráfico Trimestral
plt.figure(figsize=(12, 6))
ax = sns.barplot(
  x="product_category_name",
  y="volume_vendas",
  hue="order_quarter",
  data=volume_vendas_por_categoria_e_trimestre,
  palette=cores
)

# Personalizando o gráfico
plt.xlabel("Categoria de Produto")
plt.ylabel("Volume de Vendas")
plt.title("Top 10 Volume de Vendas por Categoria de Produto Trimestral", fontweight='bold')
plt.xticks(rotation=90)
plt.legend(title=r"$\bf{Trimestre}$", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Exibindo o gráfico
plt.show()

# 2 - Análise de Logística
print('2. Análise de Logística')
print('\na. Prazos de Entrega: Calcular o tempo médio de entrega e identificar atrasos nas entregas.')

# Definindo funções
def carregar_dados():
 #   df_pedidos = pd.read_csv('olist_orders_dataset.csv')
  #  df_clientes = pd.read_csv('olist_customers_dataset.csv')
    return df_pedidos, df_clientes

def preprocessar_dados(df_pedidos):
    try:
        for col in ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_approved_at', 'order_delivered_carrier_date']:
            df_pedidos[col] = pd.to_datetime(df_pedidos[col], errors='coerce')
    except Exception as e:
        print("Erro ao converter datas:", e)

    data_media_entrega = df_pedidos['order_delivered_customer_date'].dropna().mean()
    df_pedidos['order_delivered_customer_date'].fillna(data_media_entrega, inplace=True)

    return df_pedidos

def analisar_logistica(df_pedidos, df_clientes):
    df_pedidos['tempo_entrega'] = df_pedidos['order_delivered_customer_date'] - df_pedidos['order_purchase_timestamp']
    df_pedidos['tempo_entrega_dias'] = df_pedidos['tempo_entrega'].dt.days

    tempo_medio_entrega = df_pedidos[df_pedidos['order_delivered_customer_date'].notnull()]['tempo_entrega'].mean()
    dias = tempo_medio_entrega.days  # Extrair apenas o número de dias do tempo médio de entrega

    print("Tempo Médio de Entrega:", int(dias), "dias")

    df_pedidos_completo = pd.merge(df_pedidos, df_clientes, how='left', on='customer_id')

    df_pedidos_por_estado = df_pedidos_completo.groupby('customer_state')['tempo_entrega_dias'].mean().sort_values(ascending=False)
    print("\nTempo médio de entrega por estado:")
    for estado, tempo_entrega in df_pedidos_por_estado.items():
        print(estado, int(tempo_entrega), "dias")

    plot_tempo_medio_entrega(df_pedidos_por_estado)

def plot_tempo_medio_entrega(df_pedidos_por_estado):
    plt.figure(figsize=(10,6))
    df_pedidos_por_estado.plot(kind='bar')
    plt.title('Tempo Médio de Entrega por Estado', fontweight='bold')
    plt.xlabel('Estado')
    plt.ylabel('Tempo Médio de Entrega (em dias)')
    plt.show()

# Carregando dados
df_pedidos, df_clientes = carregar_dados()
df_pedidos = preprocessar_dados(df_pedidos)
analisar_logistica(df_pedidos, df_clientes)

# Identificando os fatores que influenciam os atrasos nas entregas
def identificar_fatores_atrasos(df_pedidos, df_clientes):
    # Mesclar df_pedidos com df_clientes para obter o estado do cliente
    df_pedidos_completo = pd.merge(df_pedidos, df_clientes, on='customer_id', how='left')

    # Filtrar pedidos com atraso em Roraima
    pedidos_rr_atrasados = df_pedidos_completo[(df_pedidos_completo['order_status'] == 'delivered') &
                                                (df_pedidos_completo['customer_state'] == 'RR') &
                                                (df_pedidos_completo['order_delivered_customer_date'] > df_pedidos_completo['order_estimated_delivery_date'])]

    # Exibir informações detalhadas dos pedidos com atraso em Roraima
    print("Detalhes dos pedidos com atraso em Roraima:")
    print("-" * 60)
    print(pedidos_rr_atrasados)
    print("-" * 60)

# Carregando os dados dos clientes
#df_clientes = pd.read_csv('olist_customers_dataset.csv')

# Carregando os dados dos pedidos
#df_pedidos = pd.read_csv('olist_orders_dataset.csv')

# Realizando a análise de identificação de fatores de atrasos
identificar_fatores_atrasos(df_pedidos, df_clientes)


# 3 - Análise de Satisfação do Cliente
print('3. Análise de Satisfação do Cliente')
print('\na. Avaliações de Produtos: Analisar a distribuição das avaliações dos produtos e identificar os produtos com as melhores e piores avaliações')

# Fundindo os DataFrames
avaliacoes_itens_fundidos = pd.merge(df_avaliacoes_pedido, df_itens_pedidos, on='order_id', how='inner')

# Calculando a média das avaliações de cada produto
media_avaliacoes_produto = avaliacoes_itens_fundidos.groupby('product_id')['review_score'].mean().reset_index()

# Classificando os produtos com base na média das avaliações
produtos_classificados = media_avaliacoes_produto.sort_values(by='review_score', ascending=False)

print("Estatísticas das Avaliações dos Produtos:")
print(produtos_classificados['review_score'].describe())

print("\nProdutos com as Melhores Avaliações:")
print(produtos_classificados.head(10))

print("\nProdutos com as Piores Avaliações:")
print(produtos_classificados.tail(10))

# Gráfico de barras das avaliações médias dos produtos (Top 10 produtos com melhores avaliações)
plt.figure(figsize=(10, 6))
plt.bar(produtos_classificados['product_id'].head(10), produtos_classificados['review_score'].head(10), color='blue')
plt.xlabel('ID do Produto')
plt.ylabel('Avaliação Média')
plt.title('Top 10 Produtos com Melhores Avaliações', fontweight='bold')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# Gráfico de barras das avaliações médias dos produtos (Top 10 produtos com piores avaliações)
plt.figure(figsize=(10, 6))
plt.bar(produtos_classificados['product_id'].tail(10), produtos_classificados['review_score'].tail(10), color='red')
plt.xlabel('ID do Produto')
plt.ylabel('Avaliação Média')
plt.title('Top 10 Produtos com Piores Avaliações', fontweight='bold')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# 4 - Análise Financeira
print('4. Análise Financeira')

# a. Análise de Lucratividade por Categoria
print('\na. Análise de Lucratividade por Categoria: Calcular a lucratividade de diferentes categorias de produtos, levando em conta o custo dos produtos e o preço de venda.')

# Função para calcular a lucratividade por categoria de produto
def calcular_lucratividade_por_categoria(merged_df):
    # Calculando o custo total de cada categoria de produto
    custo_por_categoria = merged_df.groupby('product_category_name')['price'].sum().reset_index()
    custo_por_categoria.columns = ['product_category_name', 'custo_total']

    # Calculando o preço total de venda de cada categoria de produto
    preco_por_categoria = merged_df.groupby('product_category_name')['freight_value'].sum().reset_index()
    preco_por_categoria.columns = ['product_category_name', 'preco_total']

    # Calculando a lucratividade de cada categoria de produto
    lucratividade_por_categoria = pd.merge(custo_por_categoria, preco_por_categoria, on='product_category_name', how='inner')
    lucratividade_por_categoria['lucro'] = lucratividade_por_categoria['preco_total'] - lucratividade_por_categoria['custo_total']

    # Ordenando por lucratividade da maior para a menor
    lucratividade_por_categoria = lucratividade_por_categoria.sort_values(by='lucro', ascending=False)

    return lucratividade_por_categoria.head(10)

# Função para imprimir a tabela de lucratividade por categoria
def imprimir_tabela_lucratividade(lucratividade_por_categoria):
    print("\nLucratividade por Categoria de Produto (da maior para a menor):")
    print(lucratividade_por_categoria)

# Função para plotar o gráfico de barras da lucratividade por categoria de produto
def plotar_grafico_lucratividade(lucratividade_por_categoria):
    # Selecionar apenas as top 10 categorias
    top_10_categorias = lucratividade_por_categoria.head(10)

    plt.figure(figsize=(12, 8))
    plt.bar(top_10_categorias['product_category_name'], top_10_categorias['lucro'], color='orange')
    plt.xlabel('Categoria de Produto', fontsize=14)
    plt.ylabel('Lucro', fontsize=14)
    plt.title('Top 10 Categorias de Produto com Base na Lucratividade', fontsize=16, fontweight='bold')
    plt.xticks(rotation=90)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# Padronizar os nomes das categorias de produto, se necessário
merged_df['product_category_name'] = merged_df['product_category_name'].str.lower()

# Calcular a lucratividade por categoria
lucratividade_por_categoria = calcular_lucratividade_por_categoria(merged_df)

# Imprimir a tabela de lucratividade por categoria
imprimir_tabela_lucratividade(lucratividade_por_categoria)

# Exibindo o gráfico de barras da lucratividade por categoria de produto
plotar_grafico_lucratividade(lucratividade_por_categoria)

# 5 - Análise de Marketing
print('5. Análise de Marketing')
print('\na. Análise de Conversão de Vendas: Estudar a taxa de conversão de vendas com base em diferentes fontes de tráfego (orgânico, pago, social, etc.).')

# Filtrando transações concluídas
transacoes_concluidas = df_pedidos[df_pedidos['order_status'] == 'delivered']

# Adicionando a coluna 'payment_type' ao DataFrame `transacoes_concluidas`
transacoes_concluidas = pd.merge(transacoes_concluidas, df_pagamentos_pedidos[['order_id', 'payment_type']], on='order_id', how='inner')

# Agrupando as transações concluídas por tipo de pagamento
grupo_transacoes_concluidas = transacoes_concluidas.groupby('payment_type')

# Calculando o número de transações concluídas para cada tipo de pagamento
total_transacoes_concluidas = grupo_transacoes_concluidas.size().reset_index(name='transacoes_concluidas')

# Calculando o número total de transações concluídas
total_transacoes = total_transacoes_concluidas['transacoes_concluidas'].sum()

# Calculando a taxa de conversão de vendas para cada tipo de pagamento
total_transacoes_concluidas['taxa_conversao'] = (total_transacoes_concluidas['transacoes_concluidas'] / total_transacoes) * 100

print("\nTaxa de Conversão de Vendas por Tipo de Pagamento:")
# Arredondando a taxa de conversão para uma casa decimal antes de imprimir
total_transacoes_concluidas['taxa_conversao'] = total_transacoes_concluidas['taxa_conversao'].round(1)
print(total_transacoes_concluidas[['payment_type', 'taxa_conversao']])

# Cores
cores = ['lightblue', 'lightgreen', 'lightcoral', 'lightskyblue']

# Destaque
explode = (0.1, 0, 0, 0)

# Exibindo gráfico
plt.figure(figsize=(10, 6))
wedges, texts, autotexts = plt.pie(total_transacoes_concluidas['taxa_conversao'],
                                   labels=total_transacoes_concluidas['payment_type'],
                                   autopct='%1.1f%%',
                                   startangle=140,
                                   colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'],
                                   explode=(0.05, 0.05, 0.05, 0.05), # ajuste do destaque
                                   shadow=True,
                                   textprops=dict(fontweight='bold'))

plt.setp(autotexts, size=10, weight='bold')

plt.title('Distribuição da Taxa de Conversão de Vendas por Tipo de Pagamento', fontweight='bold')
plt.axis('equal')

# Adicionando legenda fora do gráfico
plt.legend(loc='center left', labels=total_transacoes_concluidas['payment_type'], fontsize='small')
plt.tight_layout()
plt.show()