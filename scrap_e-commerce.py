from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import requests
import pandas as pd
from datetime import datetime as dt
import time

def scrap(search):
    #MERCADOLIBRE
    def Datos_Mercado_libre(link = 'https://www.mercadolibre.com.co/', busqueda = None):
        try:
            rq = requests.get(link)
            if rq.status_code == 200:
                #INICIO DEL DRIVER----------------------------------------------------------------------------->
                options = webdriver.ChromeOptions()
                options.add_argument('--incognito')
                driver = webdriver.Chrome(executable_path=r'./chromedriver.exe',options=options)
                driver.get(link)
                search_input = driver.find_element_by_xpath('//input[@class = "nav-search-input"]')
                search_botton = driver.find_element_by_xpath('//button[@class = "nav-search-btn"]')
                search_input.send_keys(busqueda)
                search_botton.click()
                delay = 10
                try:
                    wait_element = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
                        (By.XPATH, '//div[@class = "nav-bounds nav-bounds-with-cart nav-bounds-with-cp"]')))

                    info_products = {'Nom_producto': [],
                                     'Precio_COP': [],
                                     'Envío_gratis': [],
                                     'Vendedor': [],
                                     'Más_vendido': [],
                                     'Promocionado': [],
                                     'Estado': []}
                    cuerpo = driver.find_element_by_xpath('.//div[@class = "ui-search"]')

                    #FUNCIONES--------------------------------------------------------------------------------->

                    #funcion para validar si existe un elemento
                    def check_exists_by_xpath(element, xpath):
                        try:
                            element.find_element_by_xpath(xpath)
                        except NoSuchElementException:
                            return False
                        return True

                    #funcion que toma los elementos xpath para extraer los datos (se usa en las 2 funciones de extraccion)
                    def diccionario(product_list):
                        for product in product_list:
                            nom_product = product.find_element_by_xpath('.//h2[@class = "ui-search-item__title" or "ui-search-item__title ui-search-item__group__element"]')
                            info_products['Nom_producto'].append(nom_product.text)
                            precio_cop = int((product.find_element_by_xpath('.//div[@class = "ui-search-price ui-search-price--size-medium ui-search-item__group__element"]//span[@class = "price-tag-fraction"]').text).replace('.', ''))
                            info_products['Precio_COP'].append(precio_cop)
                            funcion = check_exists_by_xpath(product,'.//p[@class = "ui-search-item__shipping ui-search-item__shipping--free"]')
                            if funcion:
                                info_products['Envío_gratis'].append(True)
                            else:
                                info_products['Envío_gratis'].append(False)
                            funcion = check_exists_by_xpath(product,'.//p[@class = "ui-search-official-store-label ui-search-item__group__element ui-search-color--GRAY"]')
                            if funcion:
                                vendedor = product.find_element_by_xpath('.//p[@class = "ui-search-official-store-label ui-search-item__group__element ui-search-color--GRAY"]')
                                info_products['Vendedor'].append(vendedor.text)
                            else:
                                info_products['Vendedor'].append('Vista no disponible')
                            funcion = check_exists_by_xpath(product,'.//span[@class = "ui-search-styled-label ui-search-item__highlight-label__text"]')
                            if funcion:
                                info_products['Más_vendido'].append(True)
                            else:
                                info_products['Más_vendido'].append(False)
                            funcion = check_exists_by_xpath(product,'.//span[@class = "ui-search-item__ad-label ui-search-item__ad-label--blue"]')
                            if funcion:
                                info_products['Promocionado'].append(True)
                            else:
                                info_products['Promocionado'].append(False)
                            funcion = check_exists_by_xpath(product,'.//span[@class = "ui-search-item__group__element ui-search-item__details"]')
                            if funcion:
                                info_products['Estado'].append('Usado')
                            else:
                                info_products['Estado'].append('Nuevo')

                    #funcion si los elementos aparecen en forma visible de lista
                    def extractor_pagina_lista():
                        try:
                            wait_element_p = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
                                (By.XPATH, '//section[@class = "ui-search-results ui-search-results--without-disclaimer"]')))

                        except TimeoutException as e:
                            print(f'La página ha tardado en cargar los elementos necesarios para la extracción: {e}')

                        print(f'Carga correcta de la pagina {driver.current_url}'.center(50, '*'))
                        product_list = driver.find_elements_by_xpath('.//li[@class = "ui-search-layout__item"]')
                        diccionario(product_list)

                    #funcion si los elementos aparecen en forma visible de bloque
                    def extractor_pagina_bloques():
                        try:
                            wait_element_p = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
                                (By.XPATH, '//section[@class = "ui-search-results ui-search-results--without-disclaimer"]')))

                        except TimeoutException as e:
                            print(f'La página ha tardado en cargar los elementos necesarios para la extracción: {e}')

                        print(f'Carga correcta de la pagina {driver.current_url}'.center(50, '*'))
                        product_list = driver.find_elements_by_xpath('.//div[@class = "ui-search-result__content-wrapper"]')
                        diccionario(product_list)

                    #FIN DEL BLOQUE DE FUNCIONES--------------------------------------------------------------->

                    #VALIDACIONES NECESARIAS PARA SELECCIONAR LA FUNCION A UTILIZAR---------------------------->
                    funcion = check_exists_by_xpath(cuerpo,'.//li[@class = "andes-pagination__page-count"]')
                    if not funcion:
                        funcion = check_exists_by_xpath(cuerpo, './/ol[@class = "ui-search-layout ui-search-layout--grid"]')
                        if funcion:
                            extractor_pagina_bloques()
                        else:
                            extractor_pagina_lista()
                    else:
                        funcion = check_exists_by_xpath(cuerpo, './/ol[@class = "ui-search-layout ui-search-layout--grid"]')
                        if funcion:
                            counter = int((cuerpo.find_element_by_xpath('.//li[@class = "andes-pagination__page-count"]').text).replace("de ", ""))
                            wait_element_loop = 1
                            while wait_element_loop <= counter:
                                extractor_pagina_bloques()
                                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                wait_element_loop += 1
                                if wait_element_loop < counter:
                                    driver.find_element_by_xpath('//li[@class = "andes-pagination__button andes-pagination__button--next"]/a[@class = "andes-pagination__link ui-search-link"]').click()
                        else:
                            counter = int((cuerpo.find_element_by_xpath('.//li[@class = "andes-pagination__page-count"]').text).replace("de ", ""))
                            wait_element_loop = 1
                            while wait_element_loop <= counter:
                                extractor_pagina_lista()
                                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                wait_element_loop += 1
                                if wait_element_loop < counter:
                                    driver.find_element_by_xpath('//li[@class = "andes-pagination__button andes-pagination__button--next"]/a[@class = "andes-pagination__link ui-search-link"]').click()
                    #FIN DEL BLOQUE DE VALIDACIONES------------------------------------------------------------>

                    #CREACION DE DATAFRAME PARA RETORNAR CSV--------------------------------------------------->
                    df = pd.DataFrame(info_products)
                    now = dt.now()
                    fecha = f'{now.day}_{now.month}_{now.year}_{now.hour}'


                except TimeoutException as e:
                    print(f'La página ha tardado en cargar los elementos necesarios para la extracción: {e}')

                driver.close()
                return df.to_csv(f'{fecha}_Busqueda_MercadoLibre__{busqueda}.csv', index=False, encoding='utf-8')
                #CIERRE DEL DRIVER----------------------------------------------------------------------------->

        except Exception as e:
            print(f"Error: {e}")

    #LINIO
    def Datos_Linio(link = 'https://www.linio.com.co/', busqueda = None):
        try:
            rq = requests.get(link)
            if rq.status_code == 200:
                #INICIO DEL DRIVER----------------------------------------------------------------------------->
                options = webdriver.ChromeOptions()
                options.add_argument('--incognito')
                driver = webdriver.Chrome(executable_path=r'./chromedriver.exe',options=options)
                driver.get(link)
                search_input = driver.find_element_by_xpath('//input[@class = "form-control"]')
                search_botton = driver.find_element_by_xpath('//button[@class = "btn btn-primary btn-search"]')
                search_input.send_keys(busqueda)
                search_botton.click()
                delay = 10
                try:
                    wait_element = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
                        (By.XPATH, '//nav[@id = "subheader-navbar"]')))

                    info_products = {'Nom_producto': [],
                                     'Precio_COP': [],
                                     'Envío_gratis': [],
                                     'Promocionado': []}
                    cuerpo = driver.find_element_by_xpath('.//div[@class = "wrapper wrapper-catalog container-fluid "]')

                    #FUNCIONES--------------------------------------------------------------------------------->

                    #funcion para validar si existe un elemento
                    def check_exists_by_xpath(element, xpath):
                        try:
                            element.find_element_by_xpath(xpath)
                        except NoSuchElementException:
                            return False
                        return True
                    #funcion que toma los elementos xpath para extraer los datos (se usa en las 2 funciones de extraccion)
                    def diccionario(product_list):
                        for product in product_list:
                            nom_product = product.find_element_by_xpath('.//span[@class = "title-section"]')
                            info_products['Nom_producto'].append(nom_product.text)
                            precio_cop = int((product.find_element_by_xpath('.//span[@class = "price-main-md"]').text).replace('$', '').replace('.', ''))
                            info_products['Precio_COP'].append(precio_cop)
                            funcion = check_exists_by_xpath(product,'.//div[@class = "badge-pill-free-shipping badge-text-refactor"]')
                            if funcion:
                                info_products['Envío_gratis'].append(True)
                            else:
                                info_products['Envío_gratis'].append(False)
                            funcion = check_exists_by_xpath(product,'.//span[@class = "sponsored-text"]')
                            if funcion:
                                info_products['Promocionado'].append(True)
                            else:
                                info_products['Promocionado'].append(False)

                    #funcion si los elementos aparecen en forma visible de bloque
                    def extractor_pagina_bloques():
                        try:
                            wait_element_p = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
                                (By.XPATH, '//div[@class = "switchable-product-container row catalog-product-sm-container"]')))

                        except TimeoutException as e:
                            print(f'La página ha tardado en cargar los elementos necesarios para la extracción: {e}')

                        print(f'Carga correcta de la pagina {driver.current_url}'.center(50, '*'))
                        product_list = driver.find_elements_by_xpath('.//div[@class = "detail-container"]')
                        diccionario(product_list)

                    #VALIDACIONES NECESARIAS PARA SELECCIONAR LA FUNCION A UTILIZAR---------------------------->
                    funcion = check_exists_by_xpath(cuerpo,'.//span[@class = "pagination-text"]')
                    if not funcion:
                        extractor_pagina_bloques()
                    else:
                        pagina_actual = cuerpo.find_element_by_xpath('.//li[@class = "page-item  active"]/a[@class = "page-link"]').text
                        counter = int((cuerpo.find_element_by_xpath('.//span[@class = "pagination-text"]').text).replace(f"Página {pagina_actual} de ", ""))
                        wait_element_loop = 1
                        while wait_element_loop <= counter:
                            extractor_pagina_bloques()
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.80);")
                            wait_element_loop += 1
                            if wait_element_loop < counter:
                                driver.find_element_by_xpath('//a[@class = "page-link page-link-icon"]').click()

                    #FIN DEL BLOQUE DE VALIDACIONES------------------------------------------------------------>

                    # CREACION DE DATAFRAME PARA RETORNAR CSV-------------------------------------------------->
                    df = pd.DataFrame(info_products)
                    now = dt.now()
                    fecha = f'{now.day}_{now.month}_{now.year}_{now.hour}'


                except TimeoutException as e:
                    print(f'La página ha tardado en cargar los elementos necesarios para la extracción: {e}')
                driver.close()
                return df.to_csv(f'{fecha}_Busqueda_Linio__{busqueda}.csv', index=False, encoding='utf-8')
                # CIERRE DEL DRIVER----------------------------------------------------------------------------->
        except Exception as e:
            print(f"Error: {e}")

    Datos_Mercado_libre(busqueda = search)
    time.sleep(5)
    Datos_Linio(busqueda = search)
    time.sleep(5)


lista_de_busqueda = ['teclado mouse']

for busqueda in lista_de_busqueda:
    scrap(busqueda)