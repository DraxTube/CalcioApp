import flet as ft
import requests
from bs4 import BeautifulSoup
import re

def main(page: ft.Page):
    page.title = "CALCIO PREMIUM MOBILE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    # Spostiamo tutto un po' più in basso per il Motorola
    page.padding = ft.padding.only(top=60, left=20, right=20, bottom=20)
    
    status_text = ft.Text("Seleziona una partita", color="#F5FF00", size=16)

    def lancia_video(url_m3u8):
        # Usiamo il trucco degli Headers anche nel lancio URL
        # VLC e i player moderni leggono questi parametri se passati correttamente
        status_text.value = "Link trovato! Apertura Player..."
        status_text.color = "#00FF00"
        page.update()
        page.launch_url(url_m3u8)

    def estrai_link_mobile(url_partita):
        status_text.value = "Bypass in corso... attendi..."
        status_text.color = "#F5FF00"
        page.update()
        
        try:
            # Simuliamo un browser mobile reale
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Motorola G32) AppleWebKit/537.36',
                'Referer': 'https://calciostream.one/'
            }
            
            # Passo 1: Entriamo nella pagina della partita
            r = requests.get(url_partita, headers=headers, timeout=10)
            
            # Passo 2: Cerchiamo l'iframe di dishtrainer (il cuore del video)
            iframe_match = re.search(r'src="([^"]+dishtrainer\.net/[^"]+)"', r.text)
            
            if iframe_match:
                embed_url = iframe_match.group(1)
                if embed_url.startswith("//"): embed_url = "https:" + embed_url
                
                # Passo 3: Entriamo nell'embed simulando la provenienza dalla partita
                headers['Referer'] = url_partita
                r2 = requests.get(embed_url, headers=headers, timeout=10)
                
                # Passo 4: Cerchiamo il link m3u8 con il token s= (come su PC)
                m3u8_match = re.search(r'(https?://[^\s\'"]+\.m3u8\?s=[^\s\'"&]+&e=[0-9]+)', r2.text)
                
                if m3u8_match:
                    final_link = m3u8_match.group(1).replace("&amp;", "&")
                    lancia_video(final_link)
                else:
                    # Se non lo troviamo, proviamo a lanciare l'embed direttamente
                    status_text.value = "Token non trovato, lancio embed diretto..."
                    page.launch_url(embed_url)
            else:
                status_text.value = "Sorgente video non trovata."
        except Exception as e:
            status_text.value = f"Errore: {e}"
        page.update()

    lista_partite = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)

    def carica_lista():
        try:
            h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            r = requests.get("https://calciostream.one/", headers=h, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            lista_partite.controls.clear()
            for item in soup.find_all('div', class_='ticket_btn'):
                nome = item.find_parent('li').get_text(" ", strip=True).split("Guarda")[0]
                link = item.find('a')['href']
                full_url = f"https://calciostream.one/{link}" if not link.startswith("http") else link
                
                lista_partite.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.PLAY_CIRCLE_OUTLINED, color="#F5FF00", size=30),
                            ft.Text(nome.upper(), size=14, weight="bold", color="white", max_lines=2)
                        ]),
                        padding=18,
                        bgcolor="#121212",
                        border_radius=12,
                        border=ft.border.all(1, "#333333"),
                        on_click=lambda e, u=full_url: estrai_link_mobile(u)
                    )
                )
            status_text.value = "Lista Partite Pronte"
            page.update()
        except:
            status_text.value = "Sito non raggiungibile (Check Connessione)"
            page.update()

    page.add(
        ft.Text("CALCIO PREMIUM", size=32, color="#F5FF00", weight="bold", font_family="Impact"),
        status_text,
        ft.Divider(color="#222222", height=20),
        lista_partite
    )
    
    carica_lista()

ft.app(target=main)
