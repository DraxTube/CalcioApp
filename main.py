import flet as ft
import requests
from bs4 import BeautifulSoup
import re

def main(page: ft.Page):
    page.title = "CALCIO PREMIUM"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = ft.padding.only(top=60, left=20, right=20, bottom=20)
    
    status_text = ft.Text("Seleziona una partita", color="#F5FF00", size=16)

    # Questa funzione fa quello che faceva il PC: lancia il link con gli headers giusti
    def avvia_flusso(url_finale):
        status_text.value = "Link intercettato! Apertura..."
        status_text.color = "#00FF00"
        page.update()
        # Lanciamo l'URL: Android 13 chiederà con cosa aprirlo (Scegli VLC!)
        page.launch_url(url_finale)

    def estrai_e_clicca(url_partita):
        status_text.value = "Sincronizzazione (come su PC)..."
        status_text.color = "#F5FF00"
        page.update()
        
        try:
            # Simuliamo esattamente il browser del PC
            h = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://calciostream.one/'
            }
            
            # 1. Prendiamo la pagina della partita
            r = requests.get(url_partita, headers=h, timeout=15)
            
            # 2. Cerchiamo l'iframe (l'embed di dishtrainer)
            iframe_match = re.search(r'src="([^"]+dishtrainer\.net/[^"]+)"', r.text)
            
            if iframe_match:
                embed_url = iframe_match.group(1)
                if embed_url.startswith("//"): embed_url = "https:" + embed_url
                
                # 3. Invece di Playwright, "inganniamo" il server chiedendo il link m3u8 direttamente
                # con il Referer della pagina partita (che è quello che fa sbloccare il video)
                h['Referer'] = url_partita
                r2 = requests.get(embed_url, headers=h, timeout=15)
                
                # Cerchiamo il link col token (s=...)
                m3u8_match = re.search(r'(https?://[^\s\'"]+\.m3u8\?s=[^\s\'"&]+&e=[0-9]+)', r2.text)
                
                if m3u8_match:
                    avvia_flusso(m3u8_match.group(1).replace("&amp;", "&"))
                else:
                    # Se non lo trova, apriamo l'embed direttamente (funziona come piano B)
                    status_text.value = "Apertura sorgente diretta..."
                    page.launch_url(embed_url)
            else:
                status_text.value = "Sito protetto. Provo apertura browser..."
                page.launch_url(url_partita)
                
        except Exception as e:
            status_text.value = f"Errore: {e}"
        page.update()

    lista_partite = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)

    def carica_lista():
        try:
            # HEADERS POTENZIATI PER EVITARE "SITO NON RAGGIUNGIBILE"
            h = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            r = requests.get("https://calciostream.one/", headers=h, timeout=20)
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
                            ft.Icon(ft.icons.LIVE_TV, color="#F5FF00"),
                            ft.Text(nome.upper(), size=14, weight="bold")
                        ]),
                        padding=20,
                        bgcolor="#1a1a1a",
                        border_radius=12,
                        on_click=lambda e, u=full_url: estrai_e_clicca(u)
                    )
                )
            status_text.value = "Lista Partite Caricata"
            page.update()
        except:
            status_text.value = "Sito non raggiungibile dall'App. Riprova."
            page.update()

    page.add(
        ft.Text("CALCIO PREMIUM", size=32, color="#F5FF00", weight="bold"),
        status_text,
        ft.Divider(color="#333333"),
        lista_partite
    )
    
    carica_lista()

ft.app(target=main)
