import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def carregar_dataframe(arquivo_csv):
    # Carregar o arquivo CSV em um DataFrame
    return pd.read_csv(arquivo_csv)


def inicializar_driver():
    # Inicializar o driver do Microsoft Edge
    driver = webdriver.Edge()
    driver.maximize_window()
    return driver


def pesquisar_descricao_simplificada(driver, nome_produto):
    # Acessar o site e realizar a pesquisa
    url = f'https://www.bing.com/search?q=Descricao+completa+do+produto+{nome_produto}'
    driver.get(url)
    time.sleep(3)  # Não precisa mais que 3s

    # Clicar no botão
    botao_bing = driver.find_element(
        By.XPATH, '//*[@id="chat_upsell_bubble_icon"]')
    time.sleep(2)  # Não precisa mais que 2s
    botao_bing.click()

    try:
        # Aguardar até que a div com a classe "ac-textBlock" esteja visível (não precisa mais que 30s)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="ac-textBlock"]/p'))
        )
        # Executar JavaScript para obter o texto do elemento
        resposta_element = driver.find_element(
            By.XPATH, '//div[@class="ac-textBlock"]/p[1]')
        resposta = driver.execute_script(
            'return arguments[0].textContent;', resposta_element)
        resposta = resposta.strip()
    except:
        resposta = "Resposta não encontrada após aguardar."

    return resposta


def atualizar_dataframe_com_respostas(df, respostas):
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

    df = carregar_dataframe(arquivo_csv)
    driver = inicializar_driver()

    respostas = []
    for nome_produto in df['nome']:
        resposta = pesquisar_descricao_simplificada(driver, nome_produto)
        respostas.append(resposta)

    atualizar_dataframe_com_respostas(df, respostas)
    salvar_dataframe_para_csv(df, 'ExampleProduct_updated.csv')
    fechar_driver(driver)


if __name__ == "__main__":
    main()
