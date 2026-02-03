import flet as ft
import requests
from bs4 import BeautifulSoup
import re

def main(page: ft.Page):
    page.title = "CALCIO PREMIUM MOBILE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = ft.padding.only(top=50, left=20, right=20, bottom=20)
    
    status_label = ft.Text("Seleziona una partita dalla lista", color="#aaaaaa", size=14)

    def avvia_bypass_android(url_partita):
        status_label.value = "Intercettazione flusso... attendi"
        status_label.color = "#F5FF00"
        page.update()

        try:
            # Headers e logica derivati dal tuo test.py per PC
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://calciostream.one/'
            }
            
            r = requests.get(url_partita, headers=headers, timeout=15)
            # Cerchiamo l'iframe come fatto nello script PC
            iframe_match = re.search(r'src="([^"]+dishtrainer\.net/[^"]+)"', r.text)
            
            if iframe_match:
                embed_url = iframe_match.group(1)
                if embed_url.startswith("//"): embed_url = "https:" + embed_url
                
                status_label.value = "FLUSSO ATTIVATO!"
                status_label.color = "#00FF00"
                page.update()
                
                # MODIFICA CRITICA: Forziamo il sistema a lanciare l'intent per VLC/Player
                # web_window_name="_self" aiuta Android a capire che deve gestire il link esternamente
                page.launch_url(embed_url, web_window_name="_self")
            else:
                status_label.value = "Link non trovato. Riprova."
                status_label.color = "orange"
                
        except Exception as e:
            status_label.value = f"Errore: {e}"
            status_label.color = "red"
        page.update()

    scroll_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

    def carica_lista():
        try:
            # Caricamento lista con lo stesso stile del file PC
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            r = requests.get("https://calciostream.one/", headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            scroll_list.controls.clear()
            for item in soup.find_all('div', class_='ticket_btn'):
                link = item.find('a')['href']
                nome = item.find_parent('li').get_text(" ", strip=True).split("Guarda")[0]
                full_url = f"https://calciostream.one/{link}" if not link.startswith("http") else link
                
                scroll_list.controls.append(
                    ft.Container(
                        content=ft.Text(f"▶  {nome.upper()}", size=16, weight="bold", color="white"),
                        padding=20,
                        bgcolor="#1a1a1a",
                        border_radius=10,
                        on_click=lambda e, u=full_url: avvia_bypass_android(u)
                    )
                )
            page.update()
        except:
            status_label.value = "Sito non raggiungibile."
            page.update()

    page.add(
        ft.Text("DIRETTA TV MOBILE", size=40, color="#F5FF00", weight="bold", font_family="Impact"),
        status_label,
        ft.Divider(color="#333333", height=30),
        scroll_list
    )
    
    carica_lista()

ft.app(target=main)
