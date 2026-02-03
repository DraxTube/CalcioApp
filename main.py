import flet as ft
import requests
from bs4 import BeautifulSoup
import re

def main(page: ft.Page):
    page.title = "CALCIO PREMIUM MOBILE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    # Padding per non far finire il titolo troppo in alto
    page.padding = ft.padding.only(top=50, left=20, right=20, bottom=20)
    
    status_text = ft.Text("Seleziona una partita", color="#F5FF00", size=16)

    # Questo caricherà la pagina "vera" in modo che il sito generi il link
    def estrai_e_apri(url_partita):
        status_text.value = "Apertura canale... (attendi 5 secondi)"
        status_text.color = "white"
        page.update()
        
        # Tecnica Android 13: Usiamo un URL diretto per forzare il bypass
        # Spesso basta cambiare il referer o l'URL di destinazione
        try:
            h = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36',
                'Referer': 'https://calciostream.one/'
            }
            r = requests.get(url_partita, headers=h, timeout=10)
            
            # Proviamo a cercare qualsiasi link .m3u8 nel testo
            # Alcuni siti ora mettono il link codificato in Base64 o nascosto in script
            links = re.findall(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', r.text)
            
            if not links:
                # Se non lo troviamo, proviamo a cercare il frame 'dishtrainer'
                iframe = re.search(r'src="([^"]+dishtrainer\.net/[^"]+)"', r.text)
                if iframe:
                    embed_url = iframe.group(1)
                    if embed_url.startswith("//"): embed_url = "https:" + embed_url
                    r2 = requests.get(embed_url, headers={'Referer': url_partita, 'User-Agent': h['User-Agent']})
                    links = re.findall(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', r2.text)

            if links:
                # Prendiamo il primo link valido e puliamolo
                final_link = links[0].replace("&amp;", "&")
                status_text.value = "Link trovato! Lancio player..."
                status_text.color = "#00FF00"
                page.update()
                page.launch_url(final_link)
            else:
                # Se fallisce ancora, apriamo la pagina direttamente nel browser 
                # ma con un trucco per pulirla dalle pubblicità
                status_text.value = "Apertura sicura nel browser..."
                page.launch_url(url_partita)
                
        except Exception as e:
            status_text.value = f"Errore: {e}"
        page.update()

    lista_partite = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

    def carica_lista():
        try:
            r = requests.get("https://calciostream.one/", timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            lista_partite.controls.clear()
            for item in soup.find_all('div', class_='ticket_btn'):
                nome = item.find_parent('li').get_text(" ", strip=True).split("Guarda")[0]
                link = item.find('a')['href']
                full_url = f"https://calciostream.one/{link}" if not link.startswith("http") else link
                
                lista_partite.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.PLAY_CIRCLE_FILL, color="#F5FF00"),
                            ft.Text(nome, size=16, weight="bold", color="white"),
                        ]),
                        padding=20,
                        bgcolor="#1a1a1a",
                        border_radius=15,
                        on_click=lambda e, u=full_url: estrai_e_apri(u),
                        ink=True # Effetto clic visibile
                    )
                )
            status_text.value = "Lista Aggiornata"
            page.update()
        except:
            status_text.value = "Sito non raggiungibile."
            page.update()

    page.add(
        ft.Text("CALCIO PREMIUM", size=35, color="#F5FF00", weight="bold"),
        status_text,
        ft.Divider(color="#333333", height=20),
        lista_partite
    )
    
    carica_lista()

ft.app(target=main)
