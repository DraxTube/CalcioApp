import flet as ft
import requests
from bs4 import BeautifulSoup
import re

def main(page: ft.Page):
    page.title = "CALCIO PREMIUM"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.window_resizable = False
    
    status_text = ft.Text("Caricamento lista...", color="#F5FF00")
    
    # Player video migliorato
    video_player = ft.Video(
        expand=True,
        autoplay=True,
        aspect_ratio=16/9,
        filter_quality=ft.FilterQuality.LOW, # Più veloce su mobile
    )

    def play_video(url_m3u8):
        try:
            video_player.src = url_m3u8
            video_player.http_headers = {
                "Referer": "https://dishtrainer.net/",
                "Origin": "https://dishtrainer.net",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36"
            }
            status_text.value = "Riproduzione avviata!"
            page.update()
        except Exception as e:
            status_text.value = f"Errore Player: {e}"
            page.update()

    def estrai_link(url_partita):
        status_text.value = "Analisi flusso... attendi..."
        page.update()
        try:
            h = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10)'}
            r = requests.get(url_partita, headers=h, timeout=10)
            
            # Cerchiamo l'iframe di dishtrainer
            iframe = re.search(r'src="([^"]+dishtrainer\.net/[^"]+)"', r.text)
            if iframe:
                embed_url = iframe.group(1)
                if embed_url.startswith("//"): embed_url = "https:" + embed_url
                
                # Entriamo nell'iframe
                r2 = requests.get(embed_url, headers={'Referer': url_partita, 'User-Agent': h['User-Agent']})
                # Cerchiamo il link m3u8 con il token
                m3u8 = re.search(r'(https?://[^\s\'"]+\.m3u8\?s=[^\s\'"&]+&e=[0-9]+)', r2.text)
                
                if m3u8:
                    final_link = m3u8.group(1).replace("&amp;", "&")
                    play_video(final_link)
                else:
                    status_text.value = "Flusso non ancora attivo."
            else:
                status_text.value = "Sorgente non trovata."
        except Exception as e:
            status_text.value = f"Errore connessione: {e}"
        page.update()

    lista_partite = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

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
                        content=ft.Text(nome, weight="bold"),
                        padding=15,
                        bgcolor="#1a1a1a",
                        border_radius=10,
                        on_click=lambda e, u=full_url: estrai_link(u)
                    )
                )
            status_text.value = "Lista aggiornata."
            page.update()
        except:
            status_text.value = "Errore nel caricamento lista."
            page.update()

    page.add(
        ft.Text("CALCIO PREMIUM", size=25, color="#F5FF00", weight="bold"),
        status_text,
        ft.Container(content=video_player, height=220, bgcolor="black", border_radius=10),
        ft.Divider(),
        lista_partite
    )
    
    carica_lista()

ft.app(target=main)
