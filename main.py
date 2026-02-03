import flet as ft
import requests
from bs4 import BeautifulSoup
import re

def main(page: ft.Page):
    page.title = "CALCIO PREMIUM MOBILE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = ft.padding.only(top=50, left=20, right=20, bottom=20)
    
    status_label = ft.Text("Seleziona una partita", color="#aaaaaa", size=14)

    def apri_con_vlc(url_partita):
        status_label.value = "Ricerca link... attendi"
        status_label.color = "#F5FF00"
        page.update()

        try:
            # Usiamo gli stessi Header che funzionano sul tuo PC
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://calciostream.one/'
            }
            
            r = requests.get(url_partita, headers=headers, timeout=15)
            # Cerchiamo l'embed come fa lo script PC
            iframe_match = re.search(r'src="([^"]+dishtrainer\.net/[^"]+)"', r.text)
            
            if iframe_match:
                embed_url = iframe_match.group(1)
                if embed_url.startswith("//"): embed_url = "https:" + embed_url
                
                status_label.value = "FLUSSO TROVATO! Lancio in corso..."
                status_label.color = "#00FF00"
                page.update()
                
                # Questo comando apre il link nel browser del Motorola. 
                # Se hai VLC, il video partirà o ti chiederà di usarlo.
                page.launch_url(embed_url)
            else:
                status_label.value = "Link non trovato. Riprova."
                status_label.color = "orange"
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
                        padding=20, bgcolor="#1a1a1a", border_radius=10,
                        on_click=lambda e, u=full_url: apri_con_vlc(u)
                    )
                )
            page.update()
        except:
            status_label.value = "Sito non raggiungibile."
            page.update()

    page.add(
        ft.Text("DIRETTA TV MOBILE", size=35, color="#F5FF00", weight="bold"),
        status_label,
        ft.Divider(color="#333333", height=20),
        scroll_list
    )
    
    carica_lista()

ft.app(target=main)
