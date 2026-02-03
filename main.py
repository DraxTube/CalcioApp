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

    # Contenitore per il video (inizialmente vuoto)
    video_container = ft.Column(visible=False, expand=True)

    def chiudi_video(e):
        video_container.visible = False
        scroll_list.visible = True
        status_label.value = "Seleziona una partita dalla lista"
        page.update()

    def avvia_bypass_android(url_partita):
        status_label.value = "Intercettazione flusso... attendi"
        status_label.color = "#F5FF00"
        page.update()

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://calciostream.one/'
            }
            
            r = requests.get(url_partita, headers=headers, timeout=15)
            iframe_match = re.search(r'src="([^"]+dishtrainer\.net/[^"]+)"', r.text)
            
            if iframe_match:
                embed_url = iframe_match.group(1)
                if embed_url.startswith("//"): embed_url = "https:" + embed_url
                
                status_label.value = "RIPRODUZIONE IN CORSO..."
                status_label.color = "#00FF00"
                
                # Sostituiamo il lancio esterno con una WebView interna per evitare errori
                video_container.controls.clear()
                video_container.controls.append(
                    ft.ElevatedButton("CHIUDI VIDEO / TORNA ALLA LISTA", on_click=chiudi_video, color="white", bgcolor="red")
                )
                video_container.controls.append(
                    ft.WebView(embed_url, expand=True)
                )
                
                scroll_list.visible = False
                video_container.visible = True
            else:
                status_label.value = "Sorgente non trovata. Riprova."
                status_label.color = "orange"
                
        except Exception as e:
            status_label.value = f"Errore: {e}"
            status_label.color = "red"
        page.update()

    scroll_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

    def carica_lista():
        try:
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
                        padding=20, bgcolor="#1a1a1a", border_radius=10,
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
        ft.Divider(color="#333333", height=20),
        scroll_list,
        video_container # Aggiungiamo il contenitore video alla pagina
    )
    
    carica_lista()

ft.app(target=main)
