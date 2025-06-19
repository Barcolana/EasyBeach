import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os

FILE_STABILIMENTI = "stabilimenti.json"
FILE_PRENOTAZIONI = "prenotazioni.json"

class EasyBeachGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EasyBeach - Prenotazioni")
        self.root.geometry("1200x700")

        self.stabilimenti = self.carica_stabilimenti()
        self.prenotazioni = self.carica_prenotazioni()

        self.stab_selezionato_var = tk.StringVar(value=self.stabilimenti[0]['ragione_sociale'] if self.stabilimenti else "")
        self.anno_selezionato_var = tk.IntVar(value=datetime.today().year)
        self.search_cliente_var = tk.StringVar()

        self.crea_layout()
        self.aggiorna_tabella()

    def carica_stabilimenti(self):
        if os.path.exists(FILE_STABILIMENTI):
            with open(FILE_STABILIMENTI, "r") as f:
                return json.load(f)
        return []

    def carica_prenotazioni(self):
        if os.path.exists(FILE_PRENOTAZIONI):
            with open(FILE_PRENOTAZIONI, "r") as f:
                return json.load(f)
        return {}

    def crea_layout(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        sidebar = ttk.Frame(main, padding=10)
        sidebar.pack(side="left", fill="y")

        ttk.Label(sidebar, text="Seleziona Stabilimento").pack(anchor="w")
        self.stab_menu = ttk.OptionMenu(sidebar, self.stab_selezionato_var, self.stab_selezionato_var.get(), *[s["ragione_sociale"] for s in self.stabilimenti], command=lambda _: self.aggiorna_tabella())
        self.stab_menu.pack(fill="x")

        ttk.Button(sidebar, text="Aggiungi Stabilimento", command=self.apri_aggiungi_stabilimento).pack(fill="x", pady=5)

        ttk.Label(sidebar, text="Seleziona Anno").pack(anchor="w", pady=5)
        anni = [datetime.today().year + i for i in range(5)]
        ttk.OptionMenu(sidebar, self.anno_selezionato_var, self.anno_selezionato_var.get(), *anni, command=lambda _: self.aggiorna_tabella()).pack(fill="x")

        ttk.Label(sidebar, text="Cerca Cliente").pack(anchor="w", pady=5)
        ttk.Entry(sidebar, textvariable=self.search_cliente_var).pack(fill="x")
        ttk.Button(sidebar, text="Filtra", command=self.aggiorna_tabella).pack(fill="x", pady=5)
        ttk.Button(sidebar, text="Reset ricerca", command=self.reset_ricerca).pack(fill="x", pady=5)

        ttk.Button(sidebar, text="Inserisci Cliente", command=self.apri_inserisci_cliente).pack(fill="x", pady=5)
        ttk.Button(sidebar, text="Rimuovi Cliente", command=self.apri_rimuovi_cliente).pack(fill="x", pady=5)

        right = ttk.Frame(main, padding=10)
        right.pack(side="right", fill="both", expand=True)

        ttk.Label(right, text="Situazione Prenotazioni", font=("Arial", 14, "bold")).pack()

        tree_frame = ttk.Frame(right)
        tree_frame.pack(fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("data", "ombrelloni", "cabine", "clienti"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        self.tree.heading("data", text="Data")
        self.tree.heading("ombrelloni", text="Ombrelloni")
        self.tree.heading("cabine", text="Cabine")
        self.tree.heading("clienti", text="Clienti")

        self.tree.column("data", width=100)
        self.tree.column("ombrelloni", width=120)
        self.tree.column("cabine", width=120)
        self.tree.column("clienti", width=400)

        self.tree.pack(fill="both", expand=True)
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

    def aggiorna_tabella(self):
        self.tree.delete(*self.tree.get_children())

        rs = self.stab_selezionato_var.get()
        stab = next((s for s in self.stabilimenti if s['ragione_sociale'] == rs), None)
        if not stab:
            return

       #aggiornato il calendario con date più lunghe

        oggi = datetime.today()
        anno = self.anno_selezionato_var.get()

        # Calcolo la data finale come il min tra 31 dicembre anno selezionato e oggi + 365 giorni
        end_date_anno = datetime(anno, 12, 31)
        end_date_max = oggi + timedelta(days=730)

        end_date = min(end_date_anno, end_date_max)
        giorni = (end_date - oggi).days + 1


        filtro_cliente = self.search_cliente_var.get().strip().lower()

        for i in range(giorni):
            giorno = oggi + timedelta(days=i)
            giorno_str = giorno.strftime("%Y-%m-%d")
            key = f"{rs}|{giorno_str}"
            pren = self.prenotazioni.get(key, {})

            cabine_disp = stab['cabine'] - pren.get("cabine", 0)
            ombrelloni_disp = stab['ombrelloni'] - pren.get("ombrelloni", 0)
            clienti = pren.get("clienti", [])

            if filtro_cliente and not any(filtro_cliente in c.lower() for c in clienti):
                continue

            clienti_str = ", ".join(clienti) if clienti else "Nessun cliente"
            self.tree.insert("", "end", values=(giorno.strftime("%d/%m/%Y"), ombrelloni_disp, cabine_disp, clienti_str))

    def reset_ricerca(self):
        self.search_cliente_var.set("")
        self.aggiorna_tabella()

    def apri_aggiungi_stabilimento(self):
        win = tk.Toplevel(self.root)
        win.title("Aggiungi Stabilimento")
        win.geometry("400x250")

        ttk.Label(win, text="Ragione Sociale:").pack(pady=5)
        ragione_var = tk.StringVar()
        ttk.Entry(win, textvariable=ragione_var).pack(fill="x", padx=10)

        ttk.Label(win, text="Numero Ombrelloni:").pack(pady=5)
        ombrelloni_var = tk.IntVar()
        ttk.Entry(win, textvariable=ombrelloni_var).pack(fill="x", padx=10)

        ttk.Label(win, text="Numero Cabine:").pack(pady=5)
        cabine_var = tk.IntVar()
        ttk.Entry(win, textvariable=cabine_var).pack(fill="x", padx=10)

        def salva_stabilimento():
            ragione = ragione_var.get().strip()
            omb = ombrelloni_var.get()
            cab = cabine_var.get()

            if not ragione or omb <= 0 or cab < 0:
                messagebox.showerror("Errore", "Inserisci dati validi.")
                return

            if any(s['ragione_sociale'] == ragione for s in self.stabilimenti):
                messagebox.showwarning("Attenzione", "Stabilimento già presente.")
                return

            nuovo_stab = {"ragione_sociale": ragione, "ombrelloni": omb, "cabine": cab}
            self.stabilimenti.append(nuovo_stab)

            with open(FILE_STABILIMENTI, "w") as f:
                json.dump(self.stabilimenti, f, indent=4)

            self.aggiorna_menu_stabilimenti()
            self.stab_selezionato_var.set(ragione)
            self.aggiorna_tabella()
            win.destroy()

        ttk.Button(win, text="Salva", command=salva_stabilimento).pack(pady=15)

    def aggiorna_menu_stabilimenti(self):
        menu = self.stab_menu["menu"]
        menu.delete(0, "end")
        for stab in self.stabilimenti:
            label = stab["ragione_sociale"]
            menu.add_command(label=label, command=lambda value=label: [self.stab_selezionato_var.set(value), self.aggiorna_tabella()])

    def apri_inserisci_cliente(self):
        win = tk.Toplevel(self.root)
        win.title("Inserisci Cliente")
        win.geometry("400x350")

        # Ottieni data selezionata dalla tabella se c'è, altrimenti oggi
        data_selezionata = datetime.today()
        selezione = self.tree.focus()
        if selezione:
            valori = self.tree.item(selezione, "values")
            if valori:
                try:
                    data_selezionata = datetime.strptime(valori[0], "%d/%m/%Y")
                except ValueError:
                    pass  # formato non valido, rimane oggi

        ttk.Label(win, text="Data (YYYY-MM-DD):").pack(pady=5)
        data_var = tk.StringVar(value=data_selezionata.strftime("%Y-%m-%d"))
        ttk.Entry(win, textvariable=data_var).pack(fill="x", padx=10)

        ttk.Label(win, text="Nome Cliente:").pack(pady=5)
        cliente_var = tk.StringVar()
        ttk.Entry(win, textvariable=cliente_var).pack(fill="x", padx=10)

        ttk.Label(win, text="Ombrelloni da Prenotare:").pack(pady=5)
        ombrelloni_var = tk.IntVar(value=1)
        ttk.Entry(win, textvariable=ombrelloni_var).pack(fill="x", padx=10)

        ttk.Label(win, text="Cabine da Prenotare:").pack(pady=5)
        cabine_var = tk.IntVar(value=0)
        ttk.Entry(win, textvariable=cabine_var).pack(fill="x", padx=10)

        def salva_cliente():
            data = data_var.get().strip()
            cliente = cliente_var.get().strip()
            omb = ombrelloni_var.get()
            cab = cabine_var.get()

            if not cliente or not data or omb < 0 or cab < 0:
                messagebox.showerror("Errore", "Inserisci dati validi.")
                return

            try:
                data_obj = datetime.strptime(data, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Errore", "Data non valida. Usa YYYY-MM-DD.")
                return

            rs = self.stab_selezionato_var.get()
            stab = next((s for s in self.stabilimenti if s['ragione_sociale'] == rs), None)
            if not stab:
                messagebox.showerror("Errore", "Stabilimento non trovato.")
                return

            key = f"{rs}|{data}"
            pren = self.prenotazioni.get(key, {"ombrelloni": 0, "cabine": 0, "clienti": []})

            disp_omb = stab["ombrelloni"] - pren["ombrelloni"]
            disp_cab = stab["cabine"] - pren["cabine"]

            if omb > disp_omb or cab > disp_cab:
                messagebox.showerror("Errore", f"Disponibilità insufficiente:\nOmbrelloni disponibili: {disp_omb}\nCabine disponibili: {disp_cab}")
                return

            pren["ombrelloni"] += omb
            pren["cabine"] += cab
            pren["clienti"].append(cliente)
            self.prenotazioni[key] = pren

            with open(FILE_PRENOTAZIONI, "w") as f:
                json.dump(self.prenotazioni, f, indent=4)

            self.aggiorna_tabella()
            messagebox.showinfo("Successo", "Cliente inserito correttamente.")
            win.destroy()

        ttk.Button(win, text="Salva Cliente", command=salva_cliente).pack(pady=15)

    def apri_rimuovi_cliente(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona una riga dalla tabella.")
            return

        valori = self.tree.item(selected, "values")
        if not valori:
            return

        data_str = valori[0]  # formato "gg/mm/aaaa"
        data_obj = datetime.strptime(data_str, "%d/%m/%Y")
        data_iso = data_obj.strftime("%Y-%m-%d")
        rs = self.stab_selezionato_var.get()
        key = f"{rs}|{data_iso}"

        pren = self.prenotazioni.get(key)
        if not pren or not pren.get("clienti"):
            messagebox.showinfo("Info", "Nessun cliente da rimuovere.")
            return

        # Finestra popup
        win = tk.Toplevel(self.root)
        win.title("Rimuovi Cliente")
        win.geometry("350x250")

        ttk.Label(win, text="Seleziona cliente da rimuovere:").pack(pady=10)

        cliente_var = tk.StringVar()
        clienti = pren["clienti"]
        menu = ttk.OptionMenu(win, cliente_var, clienti[0], *clienti)
        menu.pack(pady=5)

        def conferma_rimozione():
            cliente = cliente_var.get()
            if cliente not in pren["clienti"]:
                messagebox.showerror("Errore", "Cliente non trovato.")
                return

            pren["clienti"].remove(cliente)

            # Riduci prenotazioni di 1 ombrellone come default (modificabile)
            if pren["ombrelloni"] > 0:
                pren["ombrelloni"] -= 1
            if pren["cabine"] > 0:
                pren["cabine"] -= 0  # opzionale, o aggiungi checkbox per selezionare

            # Se nessun cliente rimane, rimuovi la chiave
            if not pren["clienti"]:
                del self.prenotazioni[key]
            else:
                self.prenotazioni[key] = pren

            with open(FILE_PRENOTAZIONI, "w") as f:
                json.dump(self.prenotazioni, f, indent=4)

            self.aggiorna_tabella()
            win.destroy()

        ttk.Button(win, text="Conferma Rimozione", command=conferma_rimozione).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = EasyBeachGUI(root)
    root.mainloop()

