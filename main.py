import flet as ft
import requests
from bs4 import BeautifulSoup
import re

def main(page: ft.Page):
    page.title = "CALCIO PREMIUM AUTOMATIC"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = ft.padding.only(top=50, left=20, right=20, bottom=20)
    
    status_label = ft.Text("Seleziona una partita", color="#aaaaaa", size=14)

    def avvia_flusso_automatico(url_partita):
        status_label.value = "Sincronizzazione... Lancio VLC in corso"
        status_label.color = "#F5FF00"
        page.update()

        try:
            # Headers identici al tuo file test.py (PC)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://calciostream.one/'
            }
            
            r = requests.get(url_partita, headers=headers, timeout=15)
            # Cerchiamo l'iframe proprio come fa Playwright su PC
            iframe_match = re.search(r'src="([^"]+dishtrainer\.net/[^"]+)"', r.text)
            
            if iframe_match:
                embed_url = iframe_match.group(1)
                if embed_url.startswith("//"): embed_url = "https:" + embed_url
                
                # TRUCCO PER L'AUTOMAZIONE:
                # Invece di lanciare l'URL normale, usiamo il protocollo per VLC
                # Questo è l'equivalente del tuo self.lancia_ffplay(link)
                vlc_intent = f"intent:{embed_url}#Intent;package=org.videolan.vlc;scheme=https;end"
                
                status_label.value = "FLUSSO INVIATO A VLC!"
                status_label.color = "#00FF00"
                page.update()
                
                # Lancio automatico
                page.launch_url(vlc_intent)
            else:
                status_label.value = "Link non trovato. Riprova."
        except Exception as e:
            status_label.value = f"Errore: {e}"
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
                        padding=20, bgcolor="#1a1a1a", border_radius=12,
                        on_click=lambda e, u=full_url: avvia_flusso_automatico(u)
                    )
                )
            page.update()
        except:
            status_label.value = "Errore connessione."
            page.update()

    page.add(
        ft.Text("CALCIO AUTOMATIC", size=35, color="#F5FF00", weight="bold"),
        status_label,
        ft.Divider(color="#333333", height=20),
        scroll_list
    )
    
    carica_lista()

ft.app(target=main)
