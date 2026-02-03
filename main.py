import flet as ft
import requests
from bs4 import BeautifulSoup
import re

def main(page: ft.Page):
    page.title = "CALCIO PREMIUM MOBILE"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.bgcolor = "#000000"

    # Componente Video Player
    video_player = ft.Video(
        expand=True,
        autoplay=True,
        aspect_ratio=16/9,
    )

    status_text = ft.Text("Seleziona una partita", color="#F5FF00", size=16)

    def play_video(url_m3u8):
        # Qui applichiamo i famosi Headers che abbiamo scoperto su PC!
        video_player.src = url_m3u8
        video_player.http_headers = {
            "Referer": "https://dishtrainer.net/",
            "Origin": "https://dishtrainer.net",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
        }
        status_text.value = "Riproduzione in corso..."
        page.update()

    def carica_partite():
        try:
            h = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get("https://calciostream.one/", headers=h)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            partite_list.controls.clear()
            for item in soup.find_all('div', class_='ticket_btn'):
                link = item.find('a')['href']
                nome = item.find_parent('li').get_text(" ", strip=True).split("Guarda")[0]
                full_url = f"https://calciostream.one/{link}" if not link.startswith("http") else link
                
                partite_list.controls.append(
                    ft.Container(
                        content=ft.Text(f"LIVE: {nome}", color="white", weight="bold"),
                        padding=15,
                        bgcolor="#1a1a1a",
                        border_radius=10,
                        on_click=lambda e, u=full_url: estrai_e_gioca(u)
                    )
                )
            page.update()
        except Exception as ex:
            status_text.value = f"Errore: {ex}"
            page.update()

    def estrai_e_gioca(url_partita):
        status_text.value = "Estrazione link... attendi..."
        page.update()
        
        # Tecnica per Android: proviamo lo scraping diretto (Headers Bypass)
        try:
            h = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K)',
                'Referer': 'https://calciostream.one/'
            }
            res = requests.get(url_partita, headers=h)
            # Cerchiamo il frame di dishtrainer
            iframe_match = re.search(r'src="([^"]+dishtrainer\.net/embed/[^"]+)"', res.text)
            
            if iframe_match:
                iframe_url = iframe_match.group(1)
                if iframe_url.startswith('//'): iframe_url = 'https:' + iframe_url
                
                # Entriamo nel frame per prendere il link m3u8
                h['Referer'] = url_partita
                res_embed = requests.get(iframe_url, headers=h)
                m3u8_match = re.search(r'(https?://[^\s\'"]+\.m3u8\?s=[^\s\'"&]+&e=[0-9]+)', res_embed.text)
                
                if m3u8_match:
                    play_video(m3u8_match.group(1).replace("&amp;", "&"))
                else:
                    status_text.value = "Link dinamico non trovato. Riprova."
            else:
                status_text.value = "Streaming non trovato."
        except Exception as ex:
            status_text.value = f"Errore: {ex}"
        page.update()

    partite_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    page.add(
        ft.Text("CALCIO PREMIUM", font_family="Impact", size=30, color="#F5FF00"),
        status_text,
        ft.Divider(color="#333333"),
        ft.Container(content=video_player, height=250, bgcolor="black", border_radius=10),
        ft.Text("PARTITE DISPONIBILI:", size=14, weight="bold"),
        partite_list
    )

    carica_partite()

ft.app(target=main)
