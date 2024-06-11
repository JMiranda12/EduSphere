from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

#User insere o ID do ciencia vitae desejado
#id = input("Qual o ID do docente: ")

#Construtor do URL 
#url = f"https://www.cienciavitae.pt/portal/{id}"

url = "https://www.cienciavitae.pt/portal/EA12-D62F-C930"
driver = webdriver.Firefox()
driver.get(url)
time.sleep(4)

#Dados Pessoais

elem_name = driver.find_element(by = By.XPATH, value="/html/body/div[3]/main/section/div[1]/div/div/div[1]/div/div[2]")
print(elem_name.text)

elem_birth = driver.find_element(by = By.XPATH, value ="/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/dl[1]/dd[2]")
print(elem_birth.text)

elem_email = driver.find_element(by = By.XPATH, value = "/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/ul[2]")
print(elem_email.text)

elem_address = driver.find_element(by = By.XPATH, value = "/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/ul[3]/li")
print(elem_address.text)

elem_website = driver.find_element(by = By.XPATH, value = "/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/ul[4]/li")
print(elem_website.text)

elem_studyarea = driver.find_element(by = By.XPATH, value = "/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/ul[5]/li")
print(elem_studyarea.text)


time.sleep(5)



table = driver.find_element(By.XPATH, "/html/body/div[3]/main/section/div[3]/div/div/div[2]/div/div/table")


table_data = []


rows = table.find_elements(By.TAG_NAME, "tr")[1:]  
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    
    year_and_status = cells[0].text.split("\n")
    if len(year_and_status) >= 2:
        year = year_and_status[0]
        status = year_and_status[1]
    else:
        year = year_and_status[0]
        status = None
    
    degree_university_thesis = cells[1].text.split("\n")
    degree = degree_university_thesis[0]
    university = degree_university_thesis[1] if len(degree_university_thesis) > 1 else None
    thesis = degree_university_thesis[2] if len(degree_university_thesis) > 2 else None
    
    table_data.append({'Year': year, 'Status': status, 'Degree': degree, 'University': university, 'Thesis': thesis})


for row_data in table_data:
    print(row_data)

publication_table = driver.find_element(By.XPATH, "/html/body/div[3]/main/section/div[6]/div/div/div[2]/div/div")


rows = publication_table.find_elements(By.TAG_NAME, "tr")


for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) > 1:  
        publication_type = cells[0].text
        publications = cells[1].find_elements(By.TAG_NAME, "li")
        for publication in publications:
            publication_text = publication.text
            authors, title = publication_text.split('"')[0].strip(), publication_text.split('"')[1].strip()
            print("Type:", publication_type)
            print(f"Authors: {authors}\nTitle: {title}\n")
            try:
                link_element = publication.find_element(By.TAG_NAME, "a")
                link = link_element.get_attribute("href")
                print("Link:", link)
            except:
                print("No link available")
            print()


driver.quit()