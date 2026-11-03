# 📌 Dynamic Wallpaper To-Do

Un'applicazione desktop minimale, ultraleggera e silenziosa per Windows che integra la tua lista delle cose da fare direttamente sullo sfondo del desktop in tempo reale.

Nessun widget invasivo, nessun consumo superfluo di RAM: il demone vive nella tray di sistema e stampa i task in formato PNG lossless direttamente sopra il tuo wallpaper abituale, adattandosi dinamicamente alla luminosità dell'immagine.

---

## ✨ Funzionalità principali

- **Zero distrazioni:** gira invisibile in background nell'area di notifica (System Tray).
- **Inserimento rapido stile console (`Alt + N`):** barra flottante minimale con focus immediato della tastiera per aggiungere al volo task senza toccare il mouse.
- **Task Manager grafico (`Alt + P`):**
  - Modifica rapida *inline* con doppio clic (testo e data).
  - Limite di 16 caratteri sul campo data/info per garantire un layout sempre pulito.
  - Selezione multipla (`Ctrl + clic` / `Shift + clic`) ed eliminazione rapida con `Canc`.
  - Checkbox per completare le attività con indicatore colorato.
  - Pulsante dedicato **"Salva ed Applica"** con rendering asincrono per prevenire conflitti o blocchi del desktop.
- **Rendering grafico avanzato:**
  - **DPI-Aware:** cattura la risoluzione nativa e scala font, margini e checkbox in modo proporzionale.
  - **Margini simmetrici:** distanza calcolata al millimetro per essere equispaziata dai bordi superiore e destro dello schermo.
  - **Card semitrasparente opzionale:** rettangolo satinato attivabile con un clic per garantire leggibilità assoluta su qualsiasi sfondo.
  - **Palette dinamica:** modalità automatica basata sulla luminosità reale dell'area sottostante o selezione manuale tra **Tema Scuro** (card scura, testo bianco) e **Tema Chiaro** (card bianca opale, testo antracite).
  - **Backup non distruttivo:** rileva e conserva lo sfondo originale di Windows; svuotando la lista, il wallpaper torna pulito.

---

## 🚀 Guida rapida all'uso (con file `.exe`)

Non serve avere Python installato. Se hai scaricato o compilato `main.exe`, segui questi passaggi:

### 1. Primo avvio
1. Posiziona `main.exe` in una cartella dedicata a tua scelta (es. `C:\Programmi\WallpaperToDo` o in una cartella nei Documenti).
   > *Nota:* l'eseguibile salverà nella stessa cartella il file `tasks.json` e la cache delle immagini. Mantienilo in una cartella dedicata per evitare disordine.
2. Fai doppio clic su `main.exe`.
3. L'applicazione si avvierà in background: comparirà un'icona quadrata scura con una spunta verde nella **barra di sistema (System Tray)**, in basso a destra vicino all'orologio di Windows.

### 2. Scorciatoie e controlli

| Scorciatoia / Azione | Descrizione |
|---|---|
| `Alt + N` | Apre la barra rapida al centro dello schermo. Digita il task e premi `Invio` per applicarlo subito al desktop. Premi `Esc` per annullare. |
| `Alt + P` | Apre il Manager completo delle attività. |
| **Doppio clic sull'icona Tray** | Apre rapidamente il Manager delle attività. |
| **Tasto destro sull'icona Tray** | Mostra il menu contestuale con opzioni rapide e il tasto **Esci** per arrestare l'app. |

---

### 3. Come usare il Manager (`Alt + P`)

1. **Configurazione superiore:**
   - **Titolo:** definisce l'intestazione dei tuoi task (es. `Progetti`, `Priorità`). I due punti finali sono gestiti automaticamente.
   - **Tema:** seleziona tra *Auto*, *Tema Scuro* o *Tema Chiaro*.
   - **Sfondo scheda:** spunta per attivare o disattivare il rettangolo semitrasparente dietro i task.
2. **Gestione dei task:**
   - Clicca su **"+ Nuovo Task"** per aggiungere una riga vuota.
   - Fai **doppio clic** sulla colonna del testo per modificarlo direttamente nella riga.
   - Fai **doppio clic** sulla colonna *Data/Info* (max 16 caratteri) per impostare una scadenza o una nota breve.
   - Fai doppio clic sulla colonna *Stato* per contrassegnare il task come completato `[x]`.
   - Per eliminare uno o più task: selezionali (supporta anche `Ctrl + clic` o `Shift + clic`) e premi il tasto `Canc` o il pulsante **"Elimina selezionati"**.
3. **Salvataggio e chiusura:**
   - Clicca **"Salva ed Applica"** in alto a destra: la configurazione verrà salvata e il wallpaper si aggiornerà in background.
   - Per chiudere il manager premi `Esc` o clicca sulla `X` in alto a destra.

---

## ⚡ Avvio automatico con Windows

Per fare in modo che l'applicazione si avvii da sola ad ogni accensione del PC:

1. Premi la combinazione di tasti **`Win + R`** per aprire la finestra *Esegui*.
2. Digita:
   ```text
   shell:startup
   ```
   e premi **Invio**.
3. Clicca col tasto destro sul file `main.exe` e scegli **Crea collegamento**.
4. Sposta il collegamento appena creato all'interno della cartella *Startup* aperta al punto 2.

---

## 🛠️ Esecuzione e compilazione da sorgente (Python)

Se preferisci avviare il codice sorgente o compilare il file binario in autonomia:

### Requisiti
- Python 3.10 o versioni successive
- Windows 10 o 11

### Installazione dipendenze
```bash
pip install pillow keyboard pystray pyinstaller
```

### Avvio da terminale
```bash
python main.py
```

### Compilazione in singolo eseguibile `.exe` senza console
```bash
pyinstaller --noconsole --onefile main.py
```
Il file generato sarà disponibile all'interno della cartella `dist/main.exe`.

---

## 📁 Struttura del progetto

```text
├── main.py               # Entry point: demone in background, hotkey globali e tray icon
├── manager_gui.py        # GUI Tkinter per la gestione completa delle attività
├── quick_input.py        # Finestra flottante minimale per l'inserimento rapido (Alt + N)
├── storage.py            # Gestione persistenza JSON (tasks.json) e configurazioni
└── wallpaper_engine.py   # Motore grafico Pillow, scaling DPI e integrazione API Win32
```

---

## 📄 Licenza

Distribuito sotto licenza MIT. Libero per utilizzi personali e modifiche.