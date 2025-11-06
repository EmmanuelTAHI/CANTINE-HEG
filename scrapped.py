from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

url = "https://heg.ci/"

print(f"Tentative d'acces au site {url} avec Selenium...")
print("Configuration du navigateur Chrome en mode headless...")

# Configuration de Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Mode headless (pas de fenêtre)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

driver = None

try:
    # Créer le driver Chrome avec gestion automatique du driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Exécuter un script pour masquer le fait que c'est une automation
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    print("Navigation vers le site...")
    driver.get(url)

    # Attendre que la page se charge (attendre qu'un élément soit présent)
    print("Attente du chargement de la page...")
    time.sleep(5)  # Attendre 5 secondes pour que le contenu dynamique se charge

    # Récupérer le titre de la page
    page_title = driver.title
    current_url = driver.current_url

    # Récupérer le HTML source
    html_content = driver.page_source

    print(f"[OK] Acces reussi au site!")
    print(f"URL actuelle: {current_url}")
    print(f"Titre de la page: {page_title}")
    print(f"Taille du contenu HTML: {len(html_content)} caracteres")

    # Parser le HTML avec BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Extraire des informations utiles
    site_data = {
        "url": current_url,
        "title": page_title if page_title else "Aucun titre",
        "timestamp": datetime.now().isoformat(),
        "html_content": html_content,
        "meta_tags": {},
        "links": [],
        "images": [],
        "text_content": soup.get_text(strip=True)[
            :5000
        ],  # Premiers 5000 caractères du texte
    }

    # Extraire les meta tags
    for meta in soup.find_all("meta"):
        if meta.get("name"):
            site_data["meta_tags"][meta.get("name")] = meta.get("content", "")
        elif meta.get("property"):
            site_data["meta_tags"][meta.get("property")] = meta.get("content", "")

    # Extraire les liens
    for link in soup.find_all("a", href=True):
        link_text = link.get_text(strip=True)
        if link_text or link["href"]:
            site_data["links"].append(
                {"text": link_text[:100], "href": link["href"]}  # Limiter la longueur
            )

    # Extraire les images
    for img in soup.find_all("img", src=True):
        site_data["images"].append({"alt": img.get("alt", ""), "src": img["src"]})

    # Sauvegarder le contenu complet dans un fichier
    with open("site_content.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    # Sauvegarder les métadonnées dans un fichier JSON (sans le HTML complet pour économiser l'espace)
    metadata_to_save = {**site_data}
    metadata_to_save["html_content"] = ""  # Ne pas sauvegarder le HTML dans le JSON
    with open("site_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_to_save, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*80}")
    print(f"[OK] Contenu sauvegarde dans 'site_content.html'")
    print(f"[OK] Metadonnees sauvegardees dans 'site_metadata.json'")
    print(f"\n{'='*80}")
    print(f"RESUME DU SITE:")
    print(f"{'='*80}")
    print(f"Titre: {site_data['title']}")
    print(f"Nombre de liens trouves: {len(site_data['links'])}")
    print(f"Nombre d'images trouvees: {len(site_data['images'])}")
    print(f"Nombre de meta tags: {len(site_data['meta_tags'])}")
    print(f"\nApercu du texte (premiers 1000 caracteres):")
    print(f"{'='*80}\n")
    try:
        # Essayer d'afficher le texte en gérant l'encodage
        text_preview = (
            site_data["text_content"][:1000]
            .encode("utf-8", errors="ignore")
            .decode("utf-8", errors="ignore")
        )
        print(text_preview)
    except:
        print(
            "(Texte non affichable dans la console, mais sauvegarde dans les fichiers)"
        )
    print(f"\n{'='*80}")
    print(f"Premiers liens trouves:")
    for i, link in enumerate(site_data["links"][:10], 1):
        try:
            link_text = (
                link["text"][:50]
                .encode("utf-8", errors="ignore")
                .decode("utf-8", errors="ignore")
            )
            print(f"{i}. {link_text} -> {link['href']}")
        except:
            print(f"{i}. [lien] -> {link['href']}")

except Exception as e:
    print(f"[ERREUR] Erreur lors de l'acces au site: {e}")
    import traceback

    traceback.print_exc()

finally:
    # Fermer le navigateur
    if driver:
        print("\nFermeture du navigateur...")
        driver.quit()
        print("Navigateur ferme.")
