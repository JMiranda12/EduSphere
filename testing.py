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


# EDUCATION 
table = driver.find_element(By.XPATH, "/html/body/div[3]/main/section/div[3]/div/div/div[2]/div/div/table")

# Initialize an empty list to store the data
table_data = []

# Parse the table
rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Exclude the first row (header)
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    
    # Extract year and status information from the first cell
    year_and_status = cells[0].text.split("\n")
    if len(year_and_status) >= 2:
        year = year_and_status[0]
        status = year_and_status[1]
    else:
        year = year_and_status[0]
        status = None
    
    # Extract degree, university, and thesis information from the second cell
    degree_university_thesis = cells[1].text.split("\n")
    degree = degree_university_thesis[0]
    university = degree_university_thesis[1] if len(degree_university_thesis) > 1 else None
    thesis = degree_university_thesis[2] if len(degree_university_thesis) > 2 else None
    
    # Append the data to the table_data list
    table_data.append({'Year': year, 'Status': status, 'Degree': degree, 'University': university, 'Thesis': thesis})

# Print the scraped data
for row_data in table_data:
    print(row_data)

# PUBLICAÇÕES

# Locate the publication history table
publication_table = driver.find_element(By.XPATH, "/html/body/div[3]/main/section/div[6]/div/div/div[2]/div/div")

# Find all rows in the table
rows = publication_table.find_elements(By.TAG_NAME, "tr")

# Iterate over each row
for row in rows:
    # Find the cells in the row
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) > 1:  # Check if the row has at least two cells
        # Extract data from the cells
        publication_type = cells[0].text
        publications = cells[1].find_elements(By.TAG_NAME, "li")
        for publication in publications:
            # Extract details of each publication
            publication_text = publication.text
            # Split the publication text into authors and title 
            authors, title = publication_text.split('"')[0].strip(), publication_text.split('"')[1].strip()
            print("Type:", publication_type)
            print(f"Authors: {authors}\nTitle: {title}\n")
            # Try to find a link for the publication
            try:
                link_element = publication.find_element(By.TAG_NAME, "a")
                link = link_element.get_attribute("href")
                print("Link:", link)
            except:
                print("No link available")
            # Print a blank line for separation
            print()


# Quit the WebDriver
driver.quit()