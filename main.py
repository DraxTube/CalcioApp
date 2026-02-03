import flet as ft
import requests
from bs4 import BeautifulSoup
import re
import time

def main(page: ft.Page):
    page.title = "CALCIO PREMIUM"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = ft.padding.only(top=50, left=20, right=20, bottom=20)
    
    status_text = ft.Text("Seleziona una partita", color="#F5FF00", size=16)

    # Questa funzione emula il comportamento di "avvia_bypass_veloce" del PC
    def avvia_bypass_android(url_partita):
        status_text.value = "Sincronizzazione flusso... (Attendi)"
        status_text.color = "#F5FF00"
        page.update()

        # Su Android 13, per bypassare i blocchi, la cosa più efficace è 
        # simulare un browser che carica l'embed direttamente.
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Motorola)'}
            response = requests.get(url_partita, headers=headers, timeout=10)
            
            # Cerchiamo l'ID dell'embed (es. /embed/7.php)
            match = re.search(r'src="([^"]+dishtrainer\.net/[^"]+)"', response.text)
            
            if match:
                embed_url = match.group(1)
                if embed_url.startswith("//"): embed_url = "https:" + embed_url
                
                # Invece di Playwright, apriamo l'embed in una WebView del telefono
                # che è l'unico modo per far generare il token s= al server
                status_text.value = "Flusso attivato! Lancio player..."
                status_text.color = "#00FF00"
                page.update()
                
                # Lanciamo l'URL dell'embed: Android 13 lo aprirà nel player 
                # o nel browser di sistema che estrarrà il video correttamente
                page.launch_url(embed_url)
            else:
                status_text.value = "Sorgente non trovata al momento."
                page.update()
                
        except Exception as e:
            status_text.value = f"Errore di rete: {e}"
            page.update()

    lista_partite = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=12)

    def carica_lista():
        try:
            # Usiamo un timeout più lungo per evitare "Sito non raggiungibile"
            h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            r = requests.get("https://calciostream.one/", headers=h, timeout=15)
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, 'html.parser')
            lista_partite.controls.clear()
            
            for item in soup.find_all('div', class_='ticket_btn'):
                nome = item.find_parent('li').get_text(" ", strip=True).split("Guarda")[0]
                link = item.find('a')['href']
                full_url = f"https://calciostream.one/{link}" if not link.startswith("http") else link
                
                lista_partite.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.PLAY_ARROW_ROUNDED, color="#F5FF00"),
                            ft.Text(nome, size=16, weight="bold")
                        ]),
                        padding=20,
                        bgcolor="#1a1a1a",
                        border_radius=15,
                        on_click=lambda e, u=full_url: avvia_bypass_android(u)
                    )
                )
            status_text.value = "Lista Aggiornata"
            page.update()
        except Exception as e:
            status_text.value = "Sito non raggiungibile (Verifica connessione)"
            page.update()

    page.add(
        ft.Text("CALCIO PREMIUM", size=32, color="#F5FF00", weight="bold"),
        status_text,
        ft.Divider(color="#333333", height=30),
        lista_partite
    )
    
    carica_lista()

ft.app(target=main)
