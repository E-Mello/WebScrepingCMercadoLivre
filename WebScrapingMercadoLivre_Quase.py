import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import os
import time


def carregar_dataframe(arquivo_csv):
    # Carregar o arquivo CSV em um DataFrame
    return pd.read_csv(arquivo_csv)


def inicializar_driver():
    # Inicializar o driver do Microsoft Edge
    driver = webdriver.Edge()
    driver.maximize_window()
    return driver


def acessar_site(driver):
    # Acessar o site Bard do Google
    url = 'https://www.mercadolivre.com.br/'
    driver.get(url)
    time.sleep(3)  # Não precisa mais que 3s para carregar a página


def pesquisar_e_acessar_produto(driver, nome_produto, produtos_nao_encontrados):
    # Acessar o site Mercado Livre e realizar a pesquisa
    url = f'https://lista.mercadolivre.com.br/{nome_produto}'
    driver.get(url)
    time.sleep(3)  # Aguardar a página carregar

    try:
        # Aguardar até que a lista de produtos seja visível
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'ol.ui-search-layout'))
        )

        # Tokenize o nome do produto
        tokens = set(nome_produto.lower().split())

        # Encontrar todos os elementos <li> dentro da <ol>
        product_items = driver.find_elements(
            By.CSS_SELECTOR, 'ol.ui-search-layout li.ui-search-layout__item')

        # Procurar um link que corresponda ao nome do produto
        for item in product_items:
            try:
                title_element = item.find_element(
                    By.CSS_SELECTOR, 'h2.ui-search-item__title')
                title = title_element.text.lower()

                # Tokenize o texto do título do produto
                title_tokens = set(title.split())

                # Verificar se pelo menos 70% dos tokens do nome do produto estão no título do produto
                common_tokens = tokens.intersection(title_tokens)
                if len(common_tokens) / len(tokens) >= 0.7:
                    # Se pelo menos 70% das palavras-chave do nome do produto estiverem no título, acessar o link
                    link_element = item.find_element(
                        By.CSS_SELECTOR, 'a.ui-search-link')
                    link_element.click()
                    return True
            except NoSuchElementException:
                # Caso o elemento h2 não seja encontrado, continue para o próximo item
                continue

        # Se nenhum link correspondente for encontrado, você pode tratar essa situação como quiser
        produtos_nao_encontrados.append(nome_produto)
        print(f"Produto '{nome_produto}' não encontrado.")
    except TimeoutException:
        # Trate a exceção se a lista de produtos não for encontrada
        produtos_nao_encontrados.append(nome_produto)
        print("Lista de produtos não encontrada.")

    return False


def coletar_informacoes_do_produto(driver):
    try:
        # Aguardar até que a seção de informações do produto seja visível
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.ui-pdp-description'))
        )

        # Coletar a descrição do produto
        descricao_element = driver.find_element(
            By.CSS_SELECTOR, '.ui-pdp-description__content')
        descricao = descricao_element.text.strip()

        # Coletar o link da imagem
        imagem_element = driver.find_element(
            By.CSS_SELECTOR, 'figure.ui-pdp-gallery__figure img.ui-pdp-image')
        link_imagem = imagem_element.get_attribute("src")

        return {
            'descricao': descricao,
            'link_imagem': link_imagem,
        }
    except TimeoutException:
        # Trate a exceção se a seção de informações do produto não for encontrada
        print("Seção de informações do produto não encontrada.")
        return {
            'descricao': "Informações não encontradas",
            'link_imagem': "N/A",
        }


def atualizar_dataframe_com_respostas(df, respostas):
    # Adicione respostas vazias para produtos não encontrados
    respostas.extend([''] * (len(df) - len(respostas)))
    # Atualizar a coluna 'descricao' no DataFrame
    df['descricao'] = respostas


def salvar_dataframe_para_csv(df, arquivo_csv):
    # Salvar o DataFrame atualizado de volta no arquivo CSV
    df.to_csv(arquivo_csv, index=False)


def fechar_driver(driver):
    # Fechar o navegador
    driver.quit()


def main():
    arquivo_csv = 'ExampleProduct.csv'
    arquivo_csv_nao_encontrados = 'ProdutosNaoEncontrados.csv'

    df = carregar_dataframe(arquivo_csv)
    driver = inicializar_driver()
    acessar_site(driver)
    respostas = []
    links_imagens = []
    produtos_nao_encontrados = []

    try:
        for nome_produto in df['nome']:
            produto_encontrado = pesquisar_e_acessar_produto(
                driver, nome_produto, produtos_nao_encontrados)
            if produto_encontrado:
                informacoes_produto = coletar_informacoes_do_produto(driver)
                respostas.append(informacoes_produto['descricao'])
                links_imagens.append(informacoes_produto['link_imagem'])
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")

    atualizar_dataframe_com_respostas(df, respostas)
    # Certifique-se de que a lista `links_imagens` tenha o mesmo comprimento que o DataFrame
    links_imagens.extend([''] * (len(df) - len(links_imagens)))
    df['link_imagem'] = links_imagens
    salvar_dataframe_para_csv(df, 'ExampleProduct_updated.csv')

    # Verifique se há produtos não encontrados
    if produtos_nao_encontrados:
        # Salve os produtos não encontrados em um arquivo CSV
        pd.DataFrame({'Produto Não Encontrado': produtos_nao_encontrados}).to_csv(
            arquivo_csv_nao_encontrados, index=False)

    fechar_driver(driver)


if __name__ == "__main__":
    main()
