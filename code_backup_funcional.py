import pyautogui
import time
import keyring
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import winsound
import datetime
import win32gui
import win32con
import time

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración del WebDriver
service = Service("./chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument(r"user-data-dir=C:\Users\jcarl\AppData\Local\Google\Chrome\User Data")
options.add_argument("--profile-directory=Profile 1")
options.add_argument("--disable-features=UseSurfaceLayerForVideo")
options.add_argument("--disable-background-timer-throttling")
options.add_argument("--disable-backgrounding-occluded-windows")
options.add_argument("--disable-renderer-backgrounding")
options.add_argument("--force-renderer-accessibility")



def keep_chrome_visible_but_not_foreground():
    time.sleep(1)  # Esperar a que la ventana abra
    def enum_windows_callback(hwnd, window_list):
        if "chrome" in win32gui.GetWindowText(hwnd).lower():
            window_list.append(hwnd)

    window_list = []
    win32gui.EnumWindows(enum_windows_callback, window_list)

    if window_list:
        hwnd = window_list[0]
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)  # Restaurar sin traer al frente


try:
    driver = webdriver.Chrome(service=service, options=options)
    keep_chrome_visible_but_not_foreground()

    """     
    second_monitor_width = 1920
    second_monitor_height = 1080

    driver.set_window_position(-second_monitor_width, 0)
    driver.set_window_size(second_monitor_width, second_monitor_height) """

except Exception as e:
    logging.critical(f"❌ Error al iniciar el WebDriver: {e}")
    exit(1)

# Palabras clave de interés y exclusión
KEYWORDS_OF_INTEREST = [
    "DevOps", "DevSecOps", "Cyber Security", "Pentesting", "Red Team", 
    "Malware Development", "Reverse Engineering", "Python", "Golang", "C", 
    "Bash", "PowerShell", "Linux", "Linux Administrator", "Cloud", "AWS", 
    "IBM Cloud", "Infrastructure Security", "SIEM", "Threat Hunting", 
    "Incident Response", "Automation", "CI/CD", "Jenkins", "GitHub Actions", 
    "Terraform", "Docker", "Kubernetes", "FastAPI", "Flask", "Selenium", 
    "Filebase", "IPFS", "Firewalls", "Networking", "OSINT", "Memory Management", 
    "Windows API", "Process Manipulation", "Hooking Techniques", "WAF"
]

KEYWORDS_EXCLUDE = [
    "híbrido", "presencial", ".NET", "Java", "Vue", "Laravel", "Swift", "PHP", 
    "CodeIgniter", "React", "Angular", "Frontend", "UI/UX", "Diseñador", 
    "Soporte Técnico", "Helpdesk", "Junior", "Aprendiz", "Testing Manual", 
    "QA Manual", "Scrum Master", "Project Manager", "Marketing", "Ventas", "Desconocida", "Desconocido",
    "OpenShift", "OpenStack", "GCP", "Druid"
]

SEARCH_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4183233586&f_AL=true&f_JT=F&f_TPR=r604800&f_WT=2&geoId=105646813&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD&keywords=DevOps%20Backend%20Developer%20Python%20Cloud%20AWS%20Kubernetes%20Docker%20Cyber%20Security%20CI/CD%20Infrastructure%20as%20Code"


LINKEDIN_EMAIL = keyring.get_password("linkedin", "email")
LINKEDIN_PASSWORD = keyring.get_password("linkedin", "password")

if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
    logging.critical("⚠️ No se encontraron credenciales de LinkedIn en Keyring.")
    exit(1)

def beep():
    winsound.Beep(700, 500)

def login_linkedin():
    logging.info("🔑 Iniciando sesión en LinkedIn...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
    driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD + Keys.RETURN)
    time.sleep(5)

    if "Vamos a hacer una comprobación rápida de seguridad" in driver.page_source:
        logging.warning("⚠️ Comprobación de seguridad. Esperando 10 segundos.")
        beep()
        time.sleep(10)

    if "checkpoint" in driver.current_url:
        logging.error("❌ Verificación adicional requerida.")
        exit(1)

    logging.info("✅ Inicio de sesión exitoso.")


def check_linkedin_feed():
    """ Verifica si LinkedIn ya está logueado accediendo a /feed """
    driver.get("https://www.linkedin.com/feed")
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        logging.info("✅ LinkedIn cargó correctamente. Omitiendo login.")
        return True
    except TimeoutException:
        logging.warning("⚠️ LinkedIn no cargó en 5s. Ejecutando login.")
        return False


XPATH_JOB_CARDS = "//div[contains(@class, 'job-card-container')]"
XPATH_JOB_TITLE = ".//a[contains(@class, 'job-card-list__title--link')]"
XPATH_COMPANY_NAME = ".//div[contains(@class, 'artdeco-entity-lockup__subtitle')]//span"
XPATH_JOB_LOCATION = ".//ul[contains(@class, 'job-card-container__metadata-wrapper')]//li"
XPATH_ALREADY_APPLIED_ICON = "//div[contains(@class, 'jobs-s-apply--fadein')]//li-icon[@type='success-pebble-icon']"
XPATH_EASY_APPLY_BUTTON = "//button[contains(@class, 'jobs-apply-button')]"
XPATH_NEXT_STEP_BUTTON = "//button[@aria-label='Continue to next step']"
XPATH_REVIEW_APPLICATION_BUTTON = "//button[@aria-label='Review your application']"
XPATH_SUBMIT_APPLICATION_BUTTON = "//button[@aria-label='Submit application']"
XPATH_DISMISS_MODAL_BUTTON = "//button[@aria-label='Dismiss']"
XPATH_DISCARD_APPLICATION_BUTTON = "//button[@data-control-name='discard_application_confirm_btn' and contains(., 'Discard')]"
XPATH_MODAL_DISMISS_BUTTON = "//button[contains(@class, 'artdeco-modal__dismiss')]"
XPATH_APPLICATION_MODAL_CONTENT = "//div[contains(@class, 'jobs-easy-apply-modal__content')]"


def apply_to_jobs():
    logging.info("🔍 Buscando ofertas de trabajo...")
    driver.get(SEARCH_URL)
    time.sleep(5)

    applied_jobs = []
    current_page = 1

    while True:
        logging.info(f"📄 Procesando página {current_page}...")
        time.sleep(3)

        #job_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'job-card-container')]")
        job_cards = driver.find_elements(By.XPATH, XPATH_JOB_CARDS)
        if not job_cards:
            logging.warning("⚠️ No se encontraron trabajos en esta página.")
            break

        for index, job in enumerate(job_cards):
            # --- OBTENER DATOS DE LA OFERTA ---
            try:
                #job_title_element = job.find_elements(By.XPATH, ".//a[contains(@class, 'job-card-list__title--link')]")
                job_title_element = job.find_elements(By.XPATH, XPATH_JOB_TITLE)
                job_title = job_title_element[0].text if job_title_element else "Desconocido"
            except NoSuchElementException:
                job_title = "Desconocido"

            try:
                #empresa_element = job.find_elements(By.XPATH, ".//div[contains(@class, 'artdeco-entity-lockup__subtitle')]//span")
                empresa_element = job.find_elements(By.XPATH, XPATH_COMPANY_NAME)
                empresa = empresa_element[0].text if empresa_element else "Desconocida"
            except NoSuchElementException:
                empresa = "Desconocida"

            try:
                #ciudad_element = job.find_elements(By.XPATH, ".//ul[contains(@class, 'job-card-container__metadata-wrapper')]//li")
                ciudad_element = job.find_elements(By.XPATH, XPATH_JOB_LOCATION)
                ciudad = ciudad_element[0].text if ciudad_element else "Desconocida"
            except NoSuchElementException:
                ciudad = "Desconocida"

            logging.info(f"🔎 Revisando oferta: {job_title} en {empresa} ({ciudad}) Url: ({driver.current_url})")

            # --- FILTRAR POR KEYWORDS ---
            if not any(keyword.lower() in job_title.lower() for keyword in KEYWORDS_OF_INTEREST) or \
               any(exclude.lower() in job_title.lower() for exclude in KEYWORDS_EXCLUDE):
                logging.info(f"🚫 Oferta descartada (no coincide con intereses o contiene términos excluidos): {job_title}")
                continue

            # --- HACER CLIC EN LA OFERTA ---
            try:
                driver.execute_script("arguments[0].scrollIntoView();", job)

                try:
                    modal = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@data-test-modal-id, 'data-test-easy-apply-discard-confirmation')]"))
                    )
                    close_button = modal.find_element(By.XPATH, "//button[@aria-label='Dismiss']")
                    close_button.click()
                    logging.info("⚠️ Modal detectado y cerrado.")
                    time.sleep(2)  # Pequeña pausa para asegurar el cierre del modal
                except TimeoutException:
                    logging.info("✅ No se detectó ningún modal de confirmación.")                
                job.click()
                time.sleep(3)
            except NoSuchElementException:
                logging.warning("No se pudo hacer clic en la oferta.")
                continue

            # --- COMPROBAR SI YA SE HA SOLICITADO (success-pebble-icon) ---
            # Esperamos hasta 5s. Si no aparece, interpretamos que no está
            try:
                solicitado_label = WebDriverWait(driver, 5).until(
                    
                    #EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'jobs-s-apply--fadein')]//li-icon[@type='success-pebble-icon']"))
                    
                    EC.presence_of_element_located((By.XPATH, XPATH_ALREADY_APPLIED_ICON ))
                    
                )
                # Si entra aquí, es que SÍ lo encontró
                logging.info("ℹ️ Oferta ya solicitada. Pasando a la siguiente.")
                continue  # Salta a la siguiente oferta
            except TimeoutException:
                # No está el ícono -> Podemos continuar con la solicitud
                solicitado_label = None

            # --- BUSCAR EL BOTÓN 'SOLICITUD SENCILLA' ---
            logging.info("🔎 Buscando botón 'Solicitud sencilla'...")
            try:
                easy_apply_button = WebDriverWait(driver, 5).until(
                    #EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'jobs-apply-button')]"))
                    EC.presence_of_element_located((By.XPATH, XPATH_EASY_APPLY_BUTTON))
                )
            except TimeoutException:
                logging.warning("⚠️ No se encontró el botón de 'Solicitud sencilla'. Pasando a la siguiente oferta.")
                continue

            # Verificar visibilidad
            if not easy_apply_button.is_displayed():
                logging.warning("⚠️ El botón 'Solicitud sencilla' está en el DOM, pero no es visible.")
                driver.execute_script("arguments[0].scrollIntoView();", easy_apply_button)
                time.sleep(1)

            # Intentar hacer clic
            try:
                easy_apply_button.click()
                logging.info(f"✅ Aplicando a: {job_title}")
            except Exception as e:
                logging.warning(f"⚠️ Click normal fallido, intentando con JavaScript: {e}")
                driver.execute_script("arguments[0].click();", easy_apply_button)
                logging.info(f"✅ Aplicando a: {job_title} (con JavaScript)")

            # --- RELLENAR FORMULARIO ---
            # En caso de que haya varios pasos:
            for _ in range(3):
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        #EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Continue to next step']"))
                        EC.element_to_be_clickable((By.XPATH, XPATH_NEXT_STEP_BUTTON))
                    )
                    next_button.click()
                    logging.info("➡️ Pulsado botón 'Siguiente'.")
                    time.sleep(2)
                except TimeoutException:
                    logging.info("ℹ️ No más botones 'Siguiente'.")
                    break

            try:
                review_button = WebDriverWait(driver, 5).until(
                    #EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Review your application']"))
                    EC.element_to_be_clickable((By.XPATH, XPATH_REVIEW_APPLICATION_BUTTON))
                )
                review_button.click()
                logging.info("🔎 Pulsado botón 'Revisar'.")
                time.sleep(2)
            except TimeoutException:
                logging.warning("⚠️ No se encontró botón 'Revisar'.")
                try:
                    send_button = WebDriverWait(driver, 5).until(
                            #EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Submit application']"))
                            EC.element_to_be_clickable((By.XPATH, XPATH_SUBMIT_APPLICATION_BUTTON))

                    )
                    send_button.click()
                    time.sleep(1)  # Esperar 1 segundo

                    dismiss_button = WebDriverWait(driver, 5).until(
                        #EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']"))
                        EC.element_to_be_clickable((By.XPATH, XPATH_DISMISS_MODAL_BUTTON))
                    )
                    dismiss_button.click()
                    logging.info("ℹ️ Cerrado el modal de confirmación.")
                except TimeoutException:
                    logging.warning("⚠️ No encontré el botón 'Enviar solicitud'. Pasando a la siguiente.")
                    try:
                        time.sleep(1)  # Esperar 1 segundo
                        dismiss_button = WebDriverWait(driver, 5).until(
                            #EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']"))
                            EC.element_to_be_clickable((By.XPATH, XPATH_DISMISS_MODAL_BUTTON))
                        )
                        dismiss_button.click()
                        logging.info("ℹ️ Cerrado el modal de confirmación.")
                    except:
                        logging.warning("⚠️ No encontré el botón 'Enviar solicitud'. Pasando a la siguiente.")

                    continue
            # Si hay preguntas adicionales, descartar
            if "Preguntas adicionales" in driver.page_source or "Additional Questions" in driver.page_source:
                
                beep()
                

                """
                close_modal_button = driver.find_element(By.XPATH, "//button[contains(@class, 'artdeco-modal__dismiss')]")
                close_modal_button.click()
                time.sleep(2)

                discard_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-control-name='discard_application_confirm_btn' and contains(., 'Discard')]"))
                )
                discard_button.click()
                logging.info("✅ Formulario descartado.") """
                logging.warning("⚠️ Encontrado 'Preguntas adicionales'. Abriendo en nueva pestaña.")

                # Abrir la oferta en otra pestaña
                job_url = driver.current_url
                driver.execute_script(f"window.open('{job_url}');")
                extra_tabs = 0
                extra_tabs += 1
                driver.switch_to.window(driver.window_handles[0])

                try:
                    #close_modal_button = driver.find_element(By.XPATH, "//button[@aria-label='Dismiss']")
                    close_modal_button = driver.find_element(By.XPATH, XPATH_DISMISS_MODAL_BUTTON)
                    close_modal_button.click()
                    time.sleep(2)

                    discard_button = WebDriverWait(driver, 5).until(
                        #EC.element_to_be_clickable((By.XPATH, "//button[@data-control-name='discard_application_confirm_btn' and contains(., 'Discard')]"))
                        EC.element_to_be_clickable((By.XPATH, XPATH_DISCARD_APPLICATION_BUTTON))
                    )
                    discard_button.click()
                    logging.info("✅ Formulario descartado.")
                except NoSuchElementException:
                    logging.warning("⚠️ No se pudo cerrar el modal correctamente.")

                continue

            # Scroll final si es necesario
            if "Información de contacto" or "Contact information" in driver.page_source:
                #modal = driver.find_element(By.XPATH, "//div[contains(@class, 'jobs-easy-apply-modal__content')]")
                modal = driver.find_element(By.XPATH, XPATH_APPLICATION_MODAL_CONTENT)
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
                time.sleep(1)

            # Encontrar y hacer clic en 'Enviar solicitud'
            try:
                send_button = WebDriverWait(driver, 5).until(
                        #EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Submit application']"))
                        EC.element_to_be_clickable((By.XPATH, XPATH_SUBMIT_APPLICATION_BUTTON))

                )
                send_button.click()
                time.sleep(1)  # Esperar 1 segundo

                dismiss_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']"))
                )
                dismiss_button.click()
                logging.info("ℹ️ Cerrado el modal de confirmación.")
            except TimeoutException:
                logging.warning("⚠️ No encontré el botón 'Enviar solicitud'. Pasando a la siguiente.")
                try:
                    time.sleep(1)  # Esperar 1 segundo
                    dismiss_button = WebDriverWait(driver, 5).until(
                        #EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']"))
                        EC.element_to_be_clickable((By.XPATH, XPATH_DISMISS_MODAL_BUTTON))
                    )
                    dismiss_button.click()
                    logging.info("ℹ️ Cerrado el modal de confirmación.")
                except:
                    logging.warning("⚠️ No encontré el botón 'Enviar solicitud'. Pasando a la siguiente.")

                continue

            # --- REGISTRO DE LA SOLICITUD ---
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f"[OK] 📨 [{timestamp}] Solicitud enviada para {job_title} en {empresa} ({ciudad}).")
            applied_jobs.append({'job_title': job_title, 'empresa': empresa, 'ciudad': ciudad, 'timestamp': timestamp})

            with open("applied_jobs_log.txt", "a", encoding="utf-8") as file:
                file.write(f"[OK] - {timestamp} - {job_title} en {empresa} ({ciudad}) - Url: {job_url}\n")

            time.sleep(3)

        # --- TRATAR EL FIN DE PÁGINA ---
        try:
            current_page += 1
            next_page_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[@aria-label='Page {current_page}']"))
            )
            next_page_btn.click()
            logging.info(f"➡️ Pasando a la página {current_page}.")
            time.sleep(3)
        except TimeoutException:
            logging.info("✅ No hay más páginas disponibles.")
            break
    logging.info(f"✅ Aplicaciones completadas: {len(applied_jobs)}")
    for job in applied_jobs:
        logging.info(f"- Aplicado a: {job['job_title']} en {job['empresa']} ({job['ciudad']}) a las {job['timestamp']}. Url: {job_url}")

    return applied_jobs

def main():
    check_linkedin_feed()
    #login_linkedin()
    apply_to_jobs()
    input("Presiona Enter para cerrar el navegador, revisa todas las pestañas abiertas antes de cerrar...")
    driver.quit()
    logging.info("🚀 Proceso finalizado correctamente.")

if __name__ == "__main__":
    main()
