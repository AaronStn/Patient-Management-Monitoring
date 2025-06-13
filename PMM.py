# --- Creado por Aaron Setien ---
# --- Contacto: setiengomezaaron@gmail.com ---
# --- Github: https://github.com/AaronStn --- 

import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import timedelta
import random

# --- Configuración ---
excel_path = "usuarios_hospital.xlsx"

# --- Carga de hojas ---
df = pd.read_excel(excel_path, sheet_name="Pacientes")
df.columns = df.columns.str.strip().str.lower()

try:
    df_pruebas = pd.read_excel(excel_path, sheet_name="Pruebas")
    df_pruebas.columns = df_pruebas.columns.str.strip().str.lower()
    if 'id' not in df_pruebas.columns:
        df_pruebas['id'] = pd.Series(dtype=int)
except Exception:
    df_pruebas = pd.DataFrame(columns=["id", "nº historia", "código de cama", "valor", "fecha", "hora"])

zonas = df['zona'].unique()

# --- Interfaz ---
root = tk.Tk()
root.title("Pacientes por Cama")
root.geometry("1500x900")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# --- Pestaña 1: Pacientes y formulario ---
tab1 = tk.Frame(notebook)
notebook.add(tab1, text="🏥 Pacientes")

frame_izq = tk.Frame(tab1)
frame_izq.pack(side="left", fill="both", expand=True)

canvas = tk.Canvas(frame_izq)
scrollbar = tk.Scrollbar(frame_izq, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

CARD_BG = "#f0f0f0"
CARD_WIDTH = 220
MAX_COLUMNS = 5

# --- Panel lateral para mostrar pruebas ---
panel_pruebas = tk.Frame(tab1, width=400, bg="#ffffff", relief="sunken", bd=2)
panel_pruebas.pack(side="right", fill="y")

titulo_panel = tk.Label(panel_pruebas, text='🧪 Pruebas del paciente', bg='#ffffff', fg='#333366', font=("Arial", 12, "bold"))
titulo_panel.pack(pady=10)

info_paciente_label = tk.Label(
    panel_pruebas,
    text="",
    bg="#ffffff",
    fg="#000000",
    font=("Segoe UI", 10, "bold"),
    justify="left",
    anchor="w",
)
info_paciente_label.pack(padx=10, pady=(0, 5), anchor="w")

frame_scroll = tk.Frame(panel_pruebas, bg="#ffffff")
frame_scroll.pack(fill="both", expand=True, padx=10, pady=5)

canvas_pruebas = tk.Canvas(frame_scroll, bg="#ffffff", highlightthickness=0)
scrollbar_pruebas = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas_pruebas.yview)
pruebas_container = tk.Frame(canvas_pruebas, bg="#ffffff")

pruebas_container.bind("<Configure>", lambda e: canvas_pruebas.configure(scrollregion=canvas_pruebas.bbox("all")))
canvas_pruebas.create_window((0, 0), window=pruebas_container, anchor="nw")
canvas_pruebas.configure(yscrollcommand=scrollbar_pruebas.set)

canvas_pruebas.pack(side="left", fill="both", expand=True)
scrollbar_pruebas.pack(side="right", fill="y")

pruebas_container.update_idletasks()
canvas_pruebas.configure(scrollregion=canvas_pruebas.bbox("all"))

def mostrar_pruebas(historia, orden="Ascendente"):
    for widget in pruebas_container.winfo_children():
        widget.destroy()

    orden_var = tk.StringVar(value=orden)

    label_orden = tk.Label(
        pruebas_container,
        text="🗂️ Ordenar por fecha:",
        bg="#ffffff",
        font=("Segoe UI", 10, "bold")
    )
    label_orden.grid(row=0, column=0, sticky="w", padx=5, pady=5)

    orden_combo = ttk.Combobox(
        pruebas_container,
        textvariable=orden_var,
        values=["Fecha ascendente", "Fecha descendente", "Valor más alto", "Valor más bajo"],
        state="readonly",
        width=20
    )
    orden_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    # Callback para cambiar orden
    def recargar_orden(*args):
        mostrar_pruebas(historia, orden_var.get())

    orden_combo.bind("<<ComboboxSelected>>", recargar_orden)

    # Mostrar info paciente
    paciente = df[df["nº historia"].astype(str) == str(historia)]
    if not paciente.empty:
        fila = paciente.iloc[0]
        nombre = fila["nombre"]
        apellidos = fila["apellidos"]
        cama = fila["código de cama"]
        info_paciente_label.config(
            text=f"👤 {nombre} {apellidos} | 📄 Historia: {historia} \n🛏 Cama: {cama}"
        )
    else:
        info_paciente_label.config(text="Paciente no encontrado")
        return

    # Filtrar y ordenar pruebas
    pruebas = df_pruebas[df_pruebas["nº historia"].astype(str) == str(historia)].copy()
    pruebas["fecha"] = pd.to_datetime(pruebas["fecha"], errors="coerce")
    pruebas = pruebas.dropna(subset=["fecha"])

    orden = orden_var.get()

    if "Fecha" in orden:
        pruebas = pruebas.sort_values("fecha", ascending=("ascendente" in orden.lower()))
    elif "Valor" in orden:
        pruebas = pruebas.sort_values("valor", ascending=("bajo" in orden.lower()))

    if pruebas.empty:
        tk.Label(pruebas_container, text="⚠️ No hay pruebas registradas.", bg="#ffffff", fg="#666666",
                 font=("Segoe UI", 10)).grid(row=2, column=0, pady=10, columnspan=2)
    else:
        pruebas_container.columnconfigure(0, weight=1)
        pruebas_container.columnconfigure(1, weight=1)

    offset_fila = 2

    for i, (_, fila) in enumerate(pruebas.iterrows()):
        valor = fila['valor']
        color = "#2E7D32" if 70 <= valor <= 140 else "#C62828"

        fila_grid = (i // 2) + offset_fila
        columna_grid = i % 2

        tarjeta = tk.Frame(pruebas_container, bg="#f4f4f4", bd=1, relief="solid", width=170, height=80)
        tarjeta.grid(row=fila_grid, column=columna_grid, padx=5, pady=5, sticky="nsew")
        tarjeta.grid_propagate(False)

        tk.Label(tarjeta, text=f"📅 {fila['fecha'].strftime('%d/%m/%Y')}   ⏰ {fila['hora']}", bg="#f4f4f4",
                anchor="w", font=("Segoe UI", 9)).pack(anchor="w", padx=8, pady=(5, 0))
        tk.Label(tarjeta, text=f"📊 Valor: {valor}", bg="#f4f4f4", fg=color,
                anchor="w", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=(0, 5))


def resize_pruebas_container(event):
    canvas_pruebas.itemconfig("all", width=event.width)

canvas_pruebas.bind("<Configure>", resize_pruebas_container)

def crear_tarjeta(padre, fila):
    tarjeta = tk.Frame(padre, bg="#f0f4ff", bd=2, relief="ridge", padx=12, pady=10, width=CARD_WIDTH)
    tarjeta.grid_propagate(False)
    
    nombre_completo = f"{fila['nombre']} {fila['apellidos']}"
    tk.Label(tarjeta, text=nombre_completo, bg="#f0f4ff", fg="#1a237e",
             font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0,6))
    
    campos = [
        ("Código de cama", fila['código de cama']),
        ("Zona", fila['zona']),
        ("Edad", fila['edad']),
        ("Días ingresado", fila['días ingresado']),
        ("Nº Historia", fila['nº historia']),
        ("Sexo", fila['sexo'])
    ]
    for etiqueta, valor in campos:
        texto = f"{etiqueta}: {valor}"
        tk.Label(tarjeta, text=texto, bg="#f0f4ff", fg="#3a3a3a",
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=1)
    
    btn_pruebas = tk.Button(tarjeta, text="🔬 Ver pruebas", bg="#3949ab", fg="white",
                            font=("Segoe UI", 10, "bold"), relief="flat",
                            activebackground="#303f9f", cursor="hand2",
                            command=lambda: mostrar_pruebas(fila['nº historia']))
    btn_pruebas.pack(pady=(10, 0), fill="x")
    
    def on_enter(e):
        btn_pruebas['bg'] = '#303f9f'
    def on_leave(e):
        btn_pruebas['bg'] = '#3949ab'
    btn_pruebas.bind("<Enter>", on_enter)
    btn_pruebas.bind("<Leave>", on_leave)
    
    return tarjeta

# Frame para búsqueda rápida
frame_busqueda = tk.Frame(scrollable_frame)
frame_busqueda.pack(fill="x", padx=10, pady=(10, 5))

tk.Label(frame_busqueda, text="Buscar paciente (nombre o historia):", font=("Arial", 10)).pack(side="left")
entry_busqueda = tk.Entry(frame_busqueda, width=30)
entry_busqueda.pack(side="left", padx=5)

def mostrar_pacientes(filtro=""):
    for widget in scrollable_frame.winfo_children():
        if widget not in [frame_busqueda]:
            widget.destroy()

    filtro = filtro.lower().strip()

    for zona in zonas:
        pacientes_zona = df[df['zona'] == zona].copy()
        if filtro:
            pacientes_zona = pacientes_zona[
                pacientes_zona.apply(
                    lambda row: filtro in (row['nombre'] + " " + row['apellidos']).lower()
                    or filtro in str(row['nº historia']),
                    axis=1
                )
            ]
        if pacientes_zona.empty:
            continue

        tk.Label(scrollable_frame, text=f'🗂️Zona: {zona}', font=("Arial", 14, "bold")).pack(pady=(20, 5), anchor="w", padx=10)
        contenedor_zona = tk.Frame(scrollable_frame)
        contenedor_zona.pack(fill="x", padx=10)
        for i, (_, fila) in enumerate(pacientes_zona.iterrows()):
            fila_grid = i // MAX_COLUMNS
            col_grid = i % MAX_COLUMNS
            tarjeta = crear_tarjeta(contenedor_zona, fila)
            tarjeta.grid(row=fila_grid, column=col_grid, padx=5, pady=5)

def on_busqueda_keyrelease(event):
    mostrar_pacientes(entry_busqueda.get())

entry_busqueda.bind("<KeyRelease>", on_busqueda_keyrelease)

mostrar_pacientes()


for zona in zonas:
    tk.Label(scrollable_frame, text=f'🗂️Zona: {zona}', font=("Arial", 14, "bold")).pack(pady=(20, 5), anchor="w", padx=10)
    contenedor_zona = tk.Frame(scrollable_frame)
    contenedor_zona.pack(fill="x", padx=10)
    pacientes_zona = df[df['zona'] == zona].reset_index(drop=True)
    for i, (_, fila) in enumerate(pacientes_zona.iterrows()):
        fila_grid = i // MAX_COLUMNS
        col_grid = i % MAX_COLUMNS
        tarjeta = crear_tarjeta(contenedor_zona, fila)
        tarjeta.grid(row=fila_grid, column=col_grid, padx=5, pady=5)

def guardar_prueba():
    historia = entry_historia.get().strip()
    valor = entry_valor.get().strip()
    fecha = entry_fecha.get().strip()
    hora = entry_hora.get().strip()
    if not (historia and valor and fecha and hora):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    if historia not in df["nº historia"].astype(str).values:
        messagebox.showerror("Error", "Número de historia no encontrado.")
        return
    try:
        valor = int(valor)
    except ValueError:
        messagebox.showerror("Error", "El valor debe ser un número entero.")
        return
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        datetime.strptime(hora, "%H:%M")
    except ValueError:
        messagebox.showerror("Error", "Formato de fecha u hora inválido. Usa YYYY-MM-DD y HH:MM.")
        return
    fila_paciente = df[df["nº historia"].astype(str) == historia].iloc[0]
    cod_cama = fila_paciente["código de cama"]
    nuevo_id = 1 if df_pruebas.empty or df_pruebas['id'].dropna().empty else int(df_pruebas["id"].max()) + 1
    nueva_fila = {
        "id": nuevo_id,
        "nº historia": historia,
        "código de cama": cod_cama,
        "valor": valor,
        "fecha": fecha,
        "hora": hora
    }
    df_pruebas.loc[len(df_pruebas)] = nueva_fila
    with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="Pacientes", index=False)
        df_pruebas.to_excel(writer, sheet_name="Pruebas", index=False)
    messagebox.showinfo("Éxito", "Prueba guardada correctamente.")
    entry_historia.delete(0, tk.END)
    entry_valor.delete(0, tk.END)
    entry_fecha.delete(0, tk.END)
    entry_hora.delete(0, tk.END)

# --- Formulario para registrar pruebas ---
seccion_pruebas = tk.LabelFrame(scrollable_frame, text="Registrar nueva prueba", padx=10, pady=10, font=("Arial", 12, "bold"))
seccion_pruebas.pack(padx=10, pady=30, fill="x")

tk.Label(seccion_pruebas, text="🧾 Nº Historia:").grid(row=0, column=0, sticky="e")
tk.Label(seccion_pruebas, text=" 📊 Valor").grid(row=1, column=0, sticky="e")
tk.Label(seccion_pruebas, text="📅 Fecha (YYYY-MM-DD):").grid(row=2, column=0, sticky="e")
tk.Label(seccion_pruebas, text="⏰ Hora:").grid(row=3, column=0, sticky="e")

entry_historia = tk.Entry(seccion_pruebas, width=30)
entry_valor = tk.Entry(seccion_pruebas, width=30)
entry_fecha = tk.Entry(seccion_pruebas, width=30)
entry_hora = tk.Entry(seccion_pruebas, width=30)

entry_historia.grid(row=0, column=1, padx=5, pady=2)
entry_valor.grid(row=1, column=1, padx=5, pady=2)
entry_fecha.grid(row=2, column=1, padx=5, pady=2)
entry_hora.grid(row=3, column=1, padx=5, pady=2)

btn_guardar = tk.Button(seccion_pruebas, text="💾 Guardar prueba", command=guardar_prueba, bg="#4CAF50", fg="white")
btn_guardar.grid(row=4, column=0, columnspan=2, pady=10)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="left", fill="y")
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# --- Pestaña 2: Gráfica de pruebas ---
tab2 = tk.Frame(notebook)
notebook.add(tab2, text="📉 Gráfica")

frame_input = tk.Frame(tab2)
frame_input.pack(pady=(20, 10))

tk.Label(frame_input, text="Introduce Nº Historia:", font=("Arial", 11)).pack(side="left", padx=5)
entrada_historia_graf = tk.Entry(frame_input, width=20)
entrada_historia_graf.pack(side="left", padx=5)

tk.Label(frame_input, text="Fecha inicio (YYYY-MM-DD):", font=("Arial", 11)).pack(side="left", padx=5)
entrada_fecha_inicio = DateEntry(frame_input, width=12, background='darkblue',
                                foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
entrada_fecha_inicio.pack(side="left", padx=5)

tk.Label(frame_input, text="Fecha fin (YYYY-MM-DD):", font=("Arial", 11)).pack(side="left", padx=5)
entrada_fecha_fin = DateEntry(frame_input, width=12, background='darkblue',
                             foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
entrada_fecha_fin.pack(side="left", padx=5)

btn_graf = tk.Button(frame_input, text="Mostrar gráfica", command=lambda: mostrar_grafica(), bg="#1976D2", fg="white")
btn_graf.pack(side="left", padx=5)

frame_graf = tk.Frame(tab2)
frame_graf.pack(pady=20, fill="both", expand=True)

def mostrar_grafica():
    historia = entrada_historia_graf.get().strip()
    fecha_inicio = entrada_fecha_inicio.get().strip()
    fecha_fin = entrada_fecha_fin.get().strip()

    if historia == "":
        messagebox.showwarning("Atención", "Introduce un número de historia.")
        return

    pruebas = df_pruebas[df_pruebas["nº historia"].astype(str) == historia].copy()
    if pruebas.empty:
        messagebox.showinfo("Sin datos", "No hay pruebas registradas para este paciente.")
        return

    fechas_parseadas = pd.to_datetime(pruebas["fecha"], errors="coerce")
    pruebas = pruebas.drop(columns=["fecha"]).assign(fecha=fechas_parseadas)
    pruebas = pruebas.dropna(subset=["fecha"])

    if fecha_inicio and fecha_fin:
        try:
            fi = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            ff = datetime.strptime(fecha_fin, "%Y-%m-%d")
            pruebas = pruebas[(pruebas["fecha"] >= fi) & (pruebas["fecha"] <= ff)]
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Usa YYYY-MM-DD.")
            return

    if pruebas.empty:
        messagebox.showinfo("Sin datos", "No hay pruebas en el rango de fechas especificado.")
        return

    pruebas = pruebas.sort_values("fecha")
    fechas = pruebas["fecha"].dt.date
    valores = pruebas["valor"]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(fechas, valores, marker="o", linestyle="-", color="blue", label="Valor de prueba")
    ax.axhline(70, color="red", linestyle="--", linewidth=1, label="Límite inferior (70)")
    ax.axhline(140, color="red", linestyle="--", linewidth=1, label="Límite superior (140)")
    ax.axhspan(70, 140, facecolor="green", alpha=0.1, label="Rango normal")
    ax.axhspan(min(valores.min(), 0), 70, facecolor="red", alpha=0.1)
    ax.axhspan(140, valores.max() + 10, facecolor="red", alpha=0.1)
    ax.set_title(f"📈 Historial de pruebas - Historia {historia}")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Valor")
    ax.grid(True)
    fig.autofmt_xdate(rotation=45)
    ax.legend()

    for widget in frame_graf.winfo_children():
        widget.destroy()

    frame_izq = tk.Frame(frame_graf, width=1050)
    frame_der = tk.Frame(frame_graf, width=450)
    frame_izq.pack(side="left", fill="both", expand=True)
    frame_der.pack(side="right", fill="y")

    # Mostrar la gráfica
    canvas_fig = FigureCanvasTkAgg(fig, master=frame_izq)
    canvas_fig.draw()
    canvas_fig.get_tk_widget().pack(fill="both", expand=True)

    tree = ttk.Treeview(frame_der, columns=("Fecha", "Hora", "Valor"), show="headings", height=20)
    tree.heading("Fecha", text="Fecha")
    tree.heading("Hora", text="Hora")
    tree.heading("Valor", text="Valor")
    tree.column("Fecha", width=120, anchor="center")
    tree.column("Hora", width=80, anchor="center")
    tree.column("Valor", width=80, anchor="center")
    tree.pack(padx=10, pady=10, fill="y")

    tree.tag_configure("fuera_rango", foreground="red")

    for _, row in pruebas.iterrows():
        fecha_str = row["fecha"].strftime("%Y-%m-%d")
        hora_str = row["hora"]
        valor = row["valor"]
        valor_str = str(valor)

        tag = "fuera_rango" if valor < 70 or valor > 140 else ""
        tree.insert("", "end", values=(fecha_str, hora_str, valor_str), tags=(tag,))

import tkinter as tk
import pandas as pd

# --- Pestaña 3: Visión ---
tab3 = tk.Frame(notebook, bg="white")
notebook.add(tab3, text="🚀 Visión")

frame_zonas = tk.Frame(tab3, bg="white")
frame_zonas.pack(anchor="nw", padx=30, pady=20, fill="x")

df_pacientes = pd.read_excel("usuarios_hospital.xlsx", sheet_name="Pacientes")
df_pruebas = pd.read_excel("usuarios_hospital.xlsx", sheet_name="Pruebas")

zona_offset = {"GASSVVH": 100, "HEMSVVH": 200}

def color_por_valor(valor):
    try:
        valor = float(valor)
        if 60 <= valor <= 140:
            return "#96fe9e"
        else:
            return "#ee6d81"
    except:
        return "white"

def mostrar_info_paciente(paciente):
    historia = paciente["nº historia"]
    pruebas_paciente = df_pruebas[df_pruebas["nº historia"] == historia]

    popup = tk.Toplevel()
    popup.transient()
    popup.grab_set()
    popup.title("Información del paciente")
    popup.geometry("750x450+300+200")
    popup.configure(bg="white")
    popup.attributes("-topmost", True)

    contenedor = tk.Frame(popup, bg="white", padx=20, pady=20)
    contenedor.pack(fill="both", expand=True)

    # --- Panel de datos paciente ---
    panel_izq = tk.Frame(contenedor, bg="white", bd=1, relief="solid")
    panel_izq.pack(side="left", fill="y", padx=(0, 20), pady=5)

    tk.Label(panel_izq, text="Datos del Paciente", font=("Segoe UI", 12, "bold"),
             bg="white", pady=10).grid(row=0, column=0, columnspan=2)

    campos = [
        ("Nombre", paciente.get("nombre", "—")),
        ("Apellidos", paciente.get("apellidos", "—")),
        ("Sexo", paciente.get("sexo", "—")),
        ("Días ingresado", paciente.get("días ingresado", "—")),
        ("Nº Historia", paciente.get("nº historia", "—")),
        ("Código de cama", f'Hab. {paciente.get("habitacion")} / Cama {paciente.get("camahab")}')
    ]

    for i, (label, value) in enumerate(campos, start=1):
        tk.Label(panel_izq, text=label + ":", font=("Segoe UI", 10, "bold"),
                 bg="white", anchor="w", padx=10, pady=5).grid(row=i, column=0, sticky="w")
        tk.Label(panel_izq, text=value, font=("Segoe UI", 10),
                 bg="white", anchor="w", padx=10, pady=5).grid(row=i, column=1, sticky="w")

    # --- Panel de pruebas con scrollbar ---
    panel_der = tk.Frame(contenedor, bg="white", bd=1, relief="solid")
    panel_der.pack(side="left", fill="both", expand=True, pady=5)

    encabezado = tk.Frame(panel_der, bg="#1a237e")
    encabezado.pack(fill="x")

    cols = ["Valor", "Fecha", "Hora"]
    anchos = [10, 15, 10]

    for col, (text, ancho) in enumerate(zip(cols, anchos)):
        label = tk.Label(encabezado, text=text, font=("Segoe UI", 11, "bold"), fg="white",
                        bg="#1a237e", padx=5, pady=8, width=ancho, anchor="center", borderwidth=0)
        label.grid(row=0, column=col, sticky="nsew")

    for col in range(len(cols)):
        encabezado.grid_columnconfigure(col, weight=1)

    canvas = tk.Canvas(panel_der, bg="white", highlightthickness=0)
    scrollbar = tk.Scrollbar(panel_der, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    scroll_frame = tk.Frame(canvas, bg="white")
    scroll_frame_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    def on_canvas_configure(event):
        canvas.itemconfig(scroll_frame_id, width=event.width)

    canvas.bind("<Configure>", on_canvas_configure)
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    for col, ancho in enumerate(anchos):
        scroll_frame.grid_columnconfigure(col, weight=1, minsize=ancho*8)  # minsize ajustado

    if pruebas_paciente.empty:
        tk.Label(scroll_frame, text="No hay pruebas registradas.", bg="white",
                font=("Segoe UI", 10, "italic"), pady=10, anchor="center").grid(row=0, column=0, columnspan=3, sticky="nsew")
    else:
        for i, (_, prueba) in enumerate(pruebas_paciente.iterrows()):
            valor = prueba.get("valor", "—")
            fecha = prueba.get("fecha", "—")
            hora = prueba.get("hora", "—")

            tk.Label(scroll_frame, text=f"{valor}", font=("Segoe UI", 10), bg="white",
                    width=anchos[0], anchor="center", borderwidth=0).grid(row=i, column=0, padx=5, pady=4, sticky="nsew")

            tk.Label(scroll_frame, text=f"{fecha}", font=("Segoe UI", 10), bg="white",
                    width=anchos[1], anchor="center", borderwidth=0).grid(row=i, column=1, padx=(10,5), pady=4, sticky="nsew")

            tk.Label(scroll_frame, text=f"{hora}", font=("Segoe UI", 10), bg="white",
                    width=anchos[2], anchor="center", borderwidth=0).grid(row=i, column=2, padx=(10,5), pady=4, sticky="nsew")

    boton_frame = tk.Frame(popup, bg="white")
    boton_frame.pack(fill="x", pady=10)

    def ir_a_grafica():
        entrada_historia_graf.delete(0, tk.END)
        entrada_historia_graf.insert(0, str(paciente.get("nº historia", "")))
        notebook.select(tab2)
        popup.destroy()

    btn_grafica = tk.Button(boton_frame, text="Ver gráfica", font=("Segoe UI", 10, "bold"),
                            bg="#3949ab", fg="white", padx=15, pady=5,
                            activebackground="#5c6bc0", relief="flat",
                            command=ir_a_grafica)
    btn_grafica.pack(side="right", padx=(0, 15))

    btn_cerrar = tk.Button(boton_frame, text="Cerrar", font=("Segoe UI", 10, "bold"),
                        bg="#e53935", fg="white", padx=15, pady=5,
                        activebackground="#ef5350", relief="flat",
                        command=popup.destroy)
    btn_cerrar.pack(side="right", padx=(0, 10))


def crear_celda_valor(tabla, valor, paciente, fila, columna):
    texto = f"{valor:.2f}" if valor is not None else "—"
    color = color_por_valor(valor)
    celda = tk.Label(tabla, text=texto, font=("Segoe UI", 10), bg=color,
                     borderwidth=1, relief="solid", width=14, height=2)
    celda.grid(row=fila, column=columna, sticky="nsew")
    if valor is not None:
        celda.bind("<Button-1>", lambda e: mostrar_info_paciente(paciente))

def crear_tabla_zona(parent, zona, pacientes_zona):
    wrapper = tk.Frame(parent, bg="white")
    wrapper.pack(side="left", padx=30, anchor="n")

    tk.Label(wrapper, text=zona, font=("Segoe UI", 14, "bold"),
             bg="#1a237e", fg="white", pady=10, width=44).pack(fill="x", pady=(0, 5))

    tabla = tk.Frame(wrapper, bg="white", highlightbackground="#c5cae9", highlightthickness=1)
    tabla.pack()

    tk.Label(tabla, text="1", font=("Segoe UI", 11, "bold"), bg="#e8eaf6",
             width=28, height=3, borderwidth=1, relief="solid").grid(row=0, column=0, columnspan=2, sticky="nsew")
    tk.Label(tabla, text="2", font=("Segoe UI", 11, "bold"), bg="#e8eaf6",
             width=28, height=3, borderwidth=1, relief="solid").grid(row=0, column=2, columnspan=2, sticky="nsew")
    tk.Label(tabla, text="Habitación", font=("Segoe UI", 11, "bold"), bg="#e8eaf6",
             width=14, height=6, borderwidth=1, relief="solid").grid(row=0, column=4, rowspan=2, sticky="nsew")

    for i in range(4):
        label = "Min" if i % 2 == 0 else "Max"
        tk.Label(tabla, text=label, font=("Segoe UI", 10), bg="#f1f1f1",
                 width=14, height=2, borderwidth=1, relief="solid").grid(row=1, column=i, sticky="nsew")

    habitaciones = sorted(pacientes_zona["habitacion"].dropna().unique())
    for idx, hab in enumerate(habitaciones):
        fila = idx + 2

        camas = {
            1: pacientes_zona[(pacientes_zona["habitacion"] == hab) & (pacientes_zona["camahab"] == 1)],
            2: pacientes_zona[(pacientes_zona["habitacion"] == hab) & (pacientes_zona["camahab"] == 2)]
        }

        for camahab in [1, 2]:
            col_base = 0 if camahab == 1 else 2
            paciente = camas[camahab]

            if not paciente.empty:
                historia = paciente.iloc[0]["nº historia"]
                valores = df_pruebas[df_pruebas["nº historia"] == historia]["valor"]
                v_min = valores.min() if not valores.empty else None
                v_max = valores.max() if not valores.empty else None

                crear_celda_valor(tabla, v_min, paciente.iloc[0], fila, col_base)
                crear_celda_valor(tabla, v_max, paciente.iloc[0], fila, col_base + 1)

            else:
                tk.Label(tabla, text="Vacía", font=("Segoe UI", 10, "italic"), bg="#ffebee",
                         borderwidth=1, relief="solid", width=30, height=2).grid(row=fila, column=col_base, columnspan=2, sticky="nsew")

        tk.Label(tabla, text=str(int(hab)), font=("Segoe UI", 10), bg="#fafafa",
                 borderwidth=1, relief="solid", width=14, height=2).grid(row=fila, column=4, sticky="nsew")

# Crear tablas para cada zona
for zona in zona_offset:
    pacientes_zona = df_pacientes[df_pacientes["zona"] == zona]
    crear_tabla_zona(frame_zonas, zona, pacientes_zona)

root.mainloop()

# --- Creado por Aaron Setien ---
# --- Contacto: setiengomezaaron@gmail.com ---
# --- Github: https://github.com/AaronStn --- 