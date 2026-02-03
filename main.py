import flet as ft
import requests
from bs4 import BeautifulSoup
import re

def main(page: ft.Page):
    page.title = "CALCIO PREMIUM AUTOMATIC"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0

    # Label di stato
    status_label = ft.Text(" Seleziona una partita", color="#aaaaaa", size=14)
    
    # Contenitore per la lista
    lista_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    
    # Contenitore per il Video (WebView)
    video_view = ft.Column(visible=False, expand=True)

    def torna_alla_lista(e):
        video_view.visible = False
        lista_view.visible = True
        status_label.visible = True
        page.update()

    def avvia_video(url_partita):
        status_label.value = " Ricerca flusso in corso..."
        page.update()
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://calciostream.one/'
            }
            r = requests.get(url_partita, headers=headers, timeout=10)
            iframe_match = re.search(r'src="([^"]+dishtrainer\.net/[^"]+)"', r.text)
            
            if iframe_match:
                embed_url = iframe_match.group(1)
                if embed_url.startswith("//"): embed_url = "https:" + embed_url
                
                # Puliamo e carichiamo la WebView
                video_view.controls.clear()
                video_view.controls.append(
                    ft.Container(
                        content=ft.ElevatedButton("CHIUDI E TORNA ALLA LISTA", on_click=torna_alla_lista, bgcolor="red", color="white"),
                        padding=10
                    )
                )
                # Creiamo la WebView (questo caricherà il video direttamente)
                wv = ft.HtmlView(f'<iframe src="{embed_url}" style="width:100%; height:100%; border:none;"></iframe>', expand=True)
                video_view.controls.append(wv)
                
                lista_view.visible = False
                status_label.visible = False
                video_view.visible = True
            else:
                status_label.value = " Errore: Link non trovato"
        except Exception as e:
            status_label.value = f" Errore: {e}"
        page.update()

    # Caricamento lista
    def carica_lista():
        try:
            r = requests.get("https://calciostream.one/", timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.find_all('div', class_='ticket_btn'):
                link = item.find('a')['href']
                nome = item.find_parent('li').get_text(" ", strip=True).split("Guarda")[0]
                full_url = f"https://calciostream.one/{link}" if not link.startswith("http") else link
                
                lista_view.controls.append(
                    ft.Container(
                        content=ft.Text(f"▶ {nome.upper()}", size=16, weight="bold"),
                        padding=20, bgcolor="#1a1a1a", border_radius=10,
                        on_click=lambda e, u=full_url: avvia_video(u)
                    )
                )
            page.update()
        except:
            status_label.value = " Errore caricamento lista"
            page.update()

    page.add(
        ft.Container(content=ft.Text(" CALCIO AUTOMATIC", size=30, color="#F5FF00", weight="bold"), padding=20),
        status_label,
        lista_view,
        video_view
    )
    carica_lista()

ft.app(target=main)
