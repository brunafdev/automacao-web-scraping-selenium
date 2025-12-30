# ==============================================================================
# Autor: Bruna Ferreira | GitHub: @brunafdev
# Projeto: Web Scraping Dismatal (E-commerce Data Mining) #bfdev
# ==============================================================================

import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException

def iniciar_driver():
    """Configura e inicia uma instância 'headless' (sem interface gráfica) do Chrome."""
    print("--- Iniciando Sessão WebDriver ---")
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Roda em segundo plano
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(60)
        return driver
    except Exception as e:
        print(f"Erro crítico no Driver: {e}")
        return None

def descobrir_categorias(driver):
    """Mapeia dinamicamente todas as categorias do menu principal."""
    print("Mapeando categorias do site...")
    urls_map = []
    try:
        driver.get('https://www.dismatal.com.br/')
        time.sleep(3)
        
        # Seleciona os links do menu
        categorias = driver.find_elements(By.CSS_SELECTOR, 'div.caixaDepartamento > h3.departamento > a')
        
        for link in categorias:
            nome = link.get_attribute('title').strip()
            url = link.get_attribute('href')
            if nome and url:
                urls_map.append({'nome': nome, 'url': url})
        
        print(f"-> {len(urls_map)} categorias encontradas.")
        return urls_map
    except Exception as e:
        print(f"Erro ao mapear: {e}")
        return []

def extrair_produtos(soup, categoria):
    """Parser HTML: Extrai dados estruturados dos cards de produtos."""
    lista_produtos = []
    blocos = soup.select('ul[style]') # Seletor da loja
    
    for bloco in blocos:
        if not bloco.find('li', class_='dadosProduto'): continue
        try:
            nome = bloco.find('div', class_='nomeProd').h2.a.get_text(strip=True)
            link = bloco.find('div', class_='nomeProd').h2.a['href']
            codigo = bloco.find('div', class_='listaCod').get_text(strip=True)
            marca = bloco.find('div', class_='nomeMarca').get_text(strip=True)
            
            lista_produtos.append({
                'Categoria': categoria,
                'Produto': nome,
                'Marca': marca,
                'SKU': codigo,
                'URL': link
            })
        except AttributeError: continue
        
    return lista_produtos

# --- ETL ---
if __name__ == "__main__":
    driver = iniciar_driver()
    dados_totais = []

    if driver:
        categorias = descobrir_categorias(driver)
        
        for idx, cat in enumerate(categorias):
            tentativas = 3
            sucesso = False
            
            while tentativas > 0 and not sucesso:
                try:
                    print(f"Processando ({idx+1}/{len(categorias)}): {cat['nome']}")
                    driver.get(cat['url'])
                    time.sleep(2)
                    
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    produtos = extrair_produtos(soup, cat['nome'])
                    dados_totais.extend(produtos)
                    
                    # Paginação
                    paginacao = soup.find('div', id='paginacaoRodape')
                    if paginacao:
                        links_pag = paginacao.find_all('a', href=re.compile(r'/pag\d+'))
                        total_pags = max([int(re.search(r'pag(\d+)', a['href']).group(1)) for a in links_pag]) if links_pag else 1
                        
                        if total_pags > 1:
                            print(f"  -> Extraindo {total_pags} páginas adicionais...")
                            # Pega o ID
                            link_ex = paginacao.find('a', href=re.compile(r'/departamento/\d+'))
                            dept_id = re.search(r'/departamento/(\d+)', link_ex['href']).group(1)
                            
                            for p in range(2, total_pags + 1):
                                url_pag = f"https://www.dismatal.com.br/departamento/{dept_id}///pag{p}"
                                driver.get(url_pag)
                                time.sleep(1.5)
                                soup_pag = BeautifulSoup(driver.page_source, 'html.parser')
                                dados_totais.extend(extrair_produtos(soup_pag, cat['nome']))

                    sucesso = True

                except WebDriverException:
                    print("  -> Falha no navegador. Reiniciando...")
                    driver.quit()
                    driver = iniciar_driver()
                    tentativas -= 1
                except Exception as e:
                    print(f"  -> Erro genérico: {e}")
                    break
        
        driver.quit()

    # Exporta e Salva na Planilha
    if dados_totais:
        arquivo_saida = 'dataset_produtos_dismatal.xlsx'
        pd.DataFrame(dados_totais).to_excel(arquivo_saida, index=False)
        print(f"\n✅ Extração Concluída! {len(dados_totais)} produtos salvos em '{arquivo_saida}'")
    else:
        print("\n❌ Nenhum dado extraído.")

#bfdev