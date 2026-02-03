import flet as ft
import requests
from bs4 import BeautifulSoup
import re

def main(page: ft.Page):
    page.title = "CALCIO PREMIUM MOBILE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    
    status_text = ft.Text("Seleziona una partita", color="#F5FF00", size=16)

    def apri_nel_player(url_m3u8):
        # Questo comando forza Android ad aprire il video con il miglior player installato (VLC, MX Player o quello di serie)
        # È il modo più sicuro per evitare lo schermo nero su Android 13
        page.launch_url(url_m3u8)
        status_text.value = "Link inviato al player esterno!"
        page.update()

    def estrai_e_apri(url_partita):
        status_text.value = "Bypass in corso... attendi..."
        page.update()
        try:
            h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            r = requests.get(url_partita, headers=h, timeout=10)
            
            # Cerchiamo l'iframe
            iframe = re.search(r'src="([^"]+dishtrainer\.net/[^"]+)"', r.text)
            if iframe:
                embed_url = iframe.group(1)
                if embed_url.startswith("//"): embed_url = "https:" + embed_url
                
                # Entriamo nell'iframe per il link finale
                r2 = requests.get(embed_url, headers={'Referer': url_partita, 'User-Agent': h['User-Agent']})
                m3u8 = re.search(r'(https?://[^\s\'"]+\.m3u8\?s=[^\s\'"&]+&e=[0-9]+)', r2.text)
                
                if m3u8:
                    final_link = m3u8.group(1).replace("&amp;", "&")
                    # INVIO AL PLAYER ESTERNO
                    apri_nel_player(final_link)
                else:
                    status_text.value = "Streaming non ancora disponibile."
            else:
                status_text.value = "Canale non trovato."
        except Exception as e:
            status_text.value = f"Errore: {e}"
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
                        content=ft.Text(f"▶ {nome}", size=16, weight="bold"),
                        padding=20,
                        bgcolor="#1a1a1a",
                        border_radius=12,
                        on_click=lambda e, u=full_url: estrai_e_apri(u)
                    )
                )
            status_text.value = "Lista Partite Aggiornata"
            page.update()
        except:
            status_text.value = "Errore connessione al sito."
            page.update()

    page.add(
        ft.Text("CALCIO PREMIUM", size=30, color="#F5FF00", font_family="Impact"),
        status_text,
        ft.Divider(color="#333333"),
        lista_partite
    )
    
    carica_lista()

ft.app(target=main)
