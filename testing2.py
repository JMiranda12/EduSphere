import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Database connection parameters
db_config = {
    'dbname': 'edusphereDB',
    'user': 'masteradmin',
    'password': 'adminadmin',
    'host': 'eduspheredb.c5km4ii2op0l.eu-west-3.rds.amazonaws.com',
    'port': '5432'
}

def connect_db(config):
    conn = psycopg2.connect(**config)
    return conn

def insert_teacher_data(cursor, data):
    insert_query = """
    INSERT INTO teachers (full_name, date_of_birth, email, address, website, study_area)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    cursor.execute(insert_query, (
        data['name'], data['birth'], data['email'], data['address'], data['website'], data['study_area']
    ))
    return cursor.fetchone()[0]

def insert_education_data(cursor, teacher_id, education_data):
    insert_query = """
    INSERT INTO education (teacher_id, start_year, end_year, status, degree, university, thesis)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for edu in education_data:
        cursor.execute(insert_query, (
            teacher_id, edu['Start Year'], edu['End Year'], edu['Status'], edu['Degree'], edu['University'], edu['Thesis']
        ))

def insert_publications_data(cursor, teacher_id, publications_data):
    insert_query = """
    INSERT INTO publications (teacher_id, publication_type, authors, title, link)
    VALUES (%s, %s, %s, %s, %s)
    """
    for pub in publications_data:
        cursor.execute(insert_query, (
            teacher_id, pub['Type'], pub['Authors'], pub['Title'], pub['Link']
        ))

# Scrape the data
url = "https://www.cienciavitae.pt/portal/EA12-D62F-C930"
driver = webdriver.Firefox()
driver.get(url)
time.sleep(4)

# Personal Details
data = {}
data['name'] = driver.find_element(by=By.XPATH, value="/html/body/div[3]/main/section/div[1]/div/div/div[1]/div/div[2]").text
data['birth'] = driver.find_element(by=By.XPATH, value="/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/dl[1]/dd[2]").text
data['email'] = driver.find_element(by=By.XPATH, value="/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/ul[2]").text
data['address'] = driver.find_element(by=By.XPATH, value="/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/ul[3]/li").text
data['website'] = driver.find_element(by=By.XPATH, value="/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/ul[4]/li").text
data['study_area'] = driver.find_element(by=By.XPATH, value="/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/ul[5]/li").text

# Education
education_data = []
table = driver.find_element(By.XPATH, "/html/body/div[3]/main/section/div[3]/div/div/div[2]/div/div/table")
rows = table.find_elements(By.TAG_NAME, "tr")[1:]

for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    year_and_status = cells[0].text.split("\n")
    year_range = year_and_status[0].split(" - ")
    start_year = int(year_range[0])
    end_year = int(year_range[1]) if len(year_range) > 1 else None
    status = year_and_status[1] if len(year_and_status) >= 2 else None
    degree_university_thesis = cells[1].text.split("\n")
    degree = degree_university_thesis[0]
    university = degree_university_thesis[1] if len(degree_university_thesis) > 1 else None
    thesis = degree_university_thesis[2] if len(degree_university_thesis) > 2 else None
    education_data.append({'Start Year': start_year, 'End Year': end_year, 'Status': status, 'Degree': degree, 'University': university, 'Thesis': thesis})

# Publications
publications_data = []
publication_table = driver.find_element(By.XPATH, "/html/body/div[3]/main/section/div[6]/div/div/div[2]/div/div")
rows = publication_table.find_elements(By.TAG_NAME, "tr")

for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) > 1:
        publication_type = cells[0].text
        publications = cells[1].find_elements(By.TAG_NAME, "li")
        for publication in publications:
            publication_text = publication.text
            split_text = publication_text.split('"')
            if len(split_text) > 1:
                authors, title = split_text[0].strip(), split_text[1].strip()
            else:
                authors, title = split_text[0].strip(), None
            print("Type:", publication_type)
            print(f"Authors: {authors}\nTitle: {title}\n")
            try:
                link_element = publication.find_element(By.TAG_NAME, "a")
                link = link_element.get_attribute("href")
                print("Link:", link)
            except:
                link = None
                print("No link available")
            publications_data.append({'Type': publication_type, 'Authors': authors, 'Title': title, 'Link': link})
            print()

# Close the WebDriver
driver.quit()

# Connect to the database and insert data
conn = connect_db(db_config)
cursor = conn.cursor()

# Insert teacher data
teacher_id = insert_teacher_data(cursor, data)

# Insert education data
insert_education_data(cursor, teacher_id, education_data)

# Insert publications data
insert_publications_data(cursor, teacher_id, publications_data)

# Commit the transaction and close the connection
conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully.")
