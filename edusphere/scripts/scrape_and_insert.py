import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

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
        data.get('name'), data.get('birth'), data.get('email'), data.get('address'), data.get('website'), data.get('study_area')
    ))
    return cursor.fetchone()[0]

def insert_education_data(cursor, teacher_id, education_data):
    insert_query = """
    INSERT INTO education (teacher_id, start_year, end_year, status, degree, university, thesis)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for edu in education_data:
        cursor.execute(insert_query, (
            teacher_id, edu.get('Start Year'), edu.get('End Year'), edu.get('Status'), edu.get('Degree'), edu.get('University'), edu.get('Thesis')
        ))

def insert_publications_data(cursor, teacher_id, publications_data):
    insert_query = """
    INSERT INTO publications (teacher_id, publication_type, authors, title, link)
    VALUES (%s, %s, %s, %s, %s)
    """
    for pub in publications_data:
        cursor.execute(insert_query, (
            teacher_id, pub.get('Type'), pub.get('Authors'), pub.get('Title'), pub.get('Link')
        ))


ciencia_id = sys.argv[1]
url = f"https://www.cienciavitae.pt/portal/{ciencia_id}"
driver = webdriver.Firefox()

try:
    driver.get(url)
    wait = WebDriverWait(driver, 10) 

    # Personal Details
    data = {}
    try:
        data['name'] = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/main/section/div[1]/div/div/div[1]/div/div[2]"))).text
    except:
        data['name'] = None

    try:
        data['birth'] = driver.find_element(By.XPATH, "/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/dl[1]/dd[2]").text
    except:
        data['birth'] = None

    try:
        data['email'] = driver.find_element(By.XPATH, "/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/ul[2]").text
    except:
        data['email'] = None

    try:
        data['address'] = driver.find_element(By.XPATH, "/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/ul[3]/li").text
    except:
        data['address'] = None

    try:
        ul_element = driver.find_element(By.XPATH, "/html/body/div[3]/main/section/div[2]/div/div/div[2]/div/div/ul[5]")
        li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
        if li_elements:
            study_areas = [li.text for li in li_elements]
            data['study_area'] = ', '.join(study_areas)
        else:
            data['study_area'] = ul_element.text
    except:
        data['study_area'] = None

    # Education
    education_data = []
    try:
        table = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/main/section/div[3]/div/div/div[2]/div/div/table")))
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            year_and_status = cells[0].text.split("\n")
            year_range = year_and_status[0].split(" - ")

           
            try:
                start_year = int(year_range[0])
            except ValueError:
                start_year = None
            
            try:
                end_year = int(year_range[1]) if len(year_range) > 1 else None
            except ValueError:
                end_year = None
            
            status = year_and_status[1] if len(year_and_status) >= 2 else None
            degree_university_thesis = cells[1].text.split("\n")
            degree = degree_university_thesis[0]
            university = degree_university_thesis[1] if len(degree_university_thesis) > 1 else None
            thesis = degree_university_thesis[2] if len(degree_university_thesis) > 2 else None
            education_data.append({'Start Year': start_year, 'End Year': end_year, 'Status': status, 'Degree': degree, 'University': university, 'Thesis': thesis})
    except Exception as e:
        print(f"Error extracting education data: {e}")

    # Publications
    publications_data = []
    try:
        publication_table = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/main/section/div[6]/div/div/div[2]/div/div")))
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
                    try:
                        link_element = publication.find_element(By.TAG_NAME, "a")
                        link = link_element.get_attribute("href")
                    except:
                        link = None
                    publications_data.append({'Type': publication_type, 'Authors': authors, 'Title': title, 'Link': link})
    except Exception as e:
        print(f"Error extracting publications data: {e}")

finally:
    driver.quit()


print(f"Extracted teacher data: {data}")
print(f"Extracted education data: {education_data}")
print(f"Extracted publications data: {publications_data}")


conn = connect_db(db_config)
cursor = conn.cursor()


teacher_id = insert_teacher_data(cursor, data)
print(f"Inserted teacher with ID: {teacher_id}")


if education_data:
    insert_education_data(cursor, teacher_id, education_data)
    print(f"Inserted education data for teacher ID: {teacher_id}")


if publications_data:
    insert_publications_data(cursor, teacher_id, publications_data)
    print(f"Inserted publications data for teacher ID: {teacher_id}")


# Commit the transaction and close the connection
conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully.")
