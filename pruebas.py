import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
import mysql.connector

# Declaración global para los datos de conexión
host = ""
user = ""
password = ""
database = ""

listacampos = []
tablaactual = ""
identificador_seleccionado = 0
columna_id = ""

def obtener_datos_conexion():
    global host, user, password, database
    
    # Crear ventana emergente para ingresar datos
    def guardar_datos():
        global host, user, password, database  # Cambiado de nonlocal a global
        host = entry_host.get()
        user = entry_user.get()
        password = entry_password.get()
        database = entry_database.get()
        
        # Validar que todos los campos estén completos
        if not host or not user or not password or not database:
            messagebox.showerror("Error", "Por favor, ingrese todos los datos.")
        else:
            root.quit()  # Terminar el bucle de eventos de la ventana

    # Crear ventana principal para la entrada de datos
    root = tk.Tk()
    root.title("Datos de Conexión a la Base de Datos")
    
    ttk.Label(root, text="Host").grid(row=0, column=0, padx=10, pady=5)
    entry_host = ttk.Entry(root, width=30)
    entry_host.grid(row=0, column=1, padx=10, pady=5)
    
    ttk.Label(root, text="Usuario").grid(row=1, column=0, padx=10, pady=5)
    entry_user = ttk.Entry(root, width=30)
    entry_user.grid(row=1, column=1, padx=10, pady=5)
    
    ttk.Label(root, text="Contraseña").grid(row=2, column=0, padx=10, pady=5)
    entry_password = ttk.Entry(root, show="*", width=30)
    entry_password.grid(row=2, column=1, padx=10, pady=5)
    
    ttk.Label(root, text="Base de Datos").grid(row=3, column=0, padx=10, pady=5)
    entry_database = ttk.Entry(root, width=30)
    entry_database.grid(row=3, column=1, padx=10, pady=5)
    
    ttk.Button(root, text="Aceptar", command=guardar_datos).grid(row=4, column=0, columnspan=2, pady=10)
    
    root.mainloop()  # Mantener la ventana activa

def actualizaRegistro():
    global tablaactual, identificador_seleccionado, columna_id, listacampos, columnas
    
    if not identificador_seleccionado:
        messagebox.showerror("Error", "Por favor, selecciona un registro para actualizar.")
        return
    
    valores = [campo.get() for campo in listacampos]
    if any(valor.strip() == '' for valor in valores):
        messagebox.showerror("Error", "Por favor, rellena todos los campos.")
        return
    
    try:
        set_clause = ", ".join([f"{col[0]} = %s" for col in columnas[1:]])
        peticion = f"UPDATE {tablaactual} SET {set_clause} WHERE {columna_id} = %s"
        valores.append(identificador_seleccionado)
        cursor.execute(peticion, valores)
        conexion.commit()
        messagebox.showinfo("Éxito", "Registro actualizado correctamente.")
        seleccionaTabla(tablaactual)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"No se pudo actualizar el registro: {err}")

def eliminaRegistro():
    global tablaactual, identificador_seleccionado, columna_id
    
    if not identificador_seleccionado:
        messagebox.showerror("Error", "Por favor, selecciona un registro para eliminar.")
        return
    
    confirmacion = messagebox.askyesno("Confirmar eliminación", 
                                       f"¿Estás seguro de que quieres eliminar el registro con ID {identificador_seleccionado}?")
    if not confirmacion:
        return
    
    try:
        peticion = f"DELETE FROM {tablaactual} WHERE {columna_id} = %s;"
        cursor.execute(peticion, (identificador_seleccionado,))
        conexion.commit()
        messagebox.showinfo("Éxito", "El registro ha sido eliminado correctamente.")
        seleccionaTabla(tablaactual)
        identificador_seleccionado = 0
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"No se pudo eliminar el registro: {err}")

def clickEnArbol(event):
    global identificador_seleccionado, listacampos
    elemento = arbol.identify('item', event.x, event.y)
    if elemento:
        arbol.selection_set(elemento)
        valores = arbol.item(elemento, 'values')
        if valores:
            identificador_seleccionado = valores[0]
            for i, campo in enumerate(listacampos):
                campo.delete(0, tk.END)
                campo.insert(0, valores[i+1])
        else:
            identificador_seleccionado = 0
    else:
        identificador_seleccionado = 0

def insertaBaseDatos():
    global listacampos, tablaactual, columnas
    if not tablaactual:
        messagebox.showerror("Error", "Por favor, selecciona una tabla primero.")
        return
    
    valores = [campo.get() for campo in listacampos]
    if any(valor.strip() == '' for valor in valores):
        messagebox.showerror("Error", "Por favor, rellena todos los campos.")
        return
    
    try:
        placeholders = ', '.join(['%s'] * len(valores))
        peticion = f"INSERT INTO {tablaactual} ({', '.join(col[0] for col in columnas[1:])}) VALUES ({placeholders})"
        cursor.execute(peticion, valores)
        conexion.commit()
        messagebox.showinfo("Éxito", "Registro insertado correctamente.")
        seleccionaTabla(tablaactual)
        for campo in listacampos:
            campo.delete(0, tk.END)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"No se pudo insertar el registro: {err}")

def ajustar_columnas(event):
    for col in arbol['columns']:
        arbol.column(col, width=tk.font.Font().measure(arbol.heading(col)['text']) + 20)
    
    for item in arbol.get_children():
        for i, value in enumerate(arbol.item(item)['values']):
            col_w = tk.font.Font().measure(str(value)) + 20
            if arbol.column(arbol['columns'][i], width=None) < col_w:
                arbol.column(arbol['columns'][i], width=col_w)

def seleccionaTabla(mitabla):
    global listacampos, tablaactual, columnas, columna_id
    tablaactual = mitabla
    
    for widget in contieneformulario.winfo_children():
        widget.destroy()
    
    cursor.execute(f"SHOW COLUMNS FROM {mitabla}")
    columnas = cursor.fetchall()
    listacampos = []
    
    columna_id = columnas[0][0]
    
    ttk.Label(contieneformulario, text=f"{columna_id} (Auto)", style="TLabel").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    
    for i, columna in enumerate(columnas[1:], start=1):
        ttk.Label(contieneformulario, text=columna[0], style="TLabel").grid(row=i, column=0, padx=5, pady=5, sticky="w")
        campo = ttk.Entry(contieneformulario, style="TEntry", width=30)
        campo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        listacampos.append(campo)
    
    ttk.Button(contieneformulario, text="Insertar", command=insertaBaseDatos, style="success.TButton").grid(row=len(columnas), column=0, padx=5, pady=5, sticky="ew")
    ttk.Button(contieneformulario, text="Actualizar", command=actualizaRegistro, style="info.TButton").grid(row=len(columnas), column=1, padx=5, pady=5, sticky="ew")
    
    for elemento in arbol.get_children():
        arbol.delete(elemento)
    
    arbol['columns'] = [col[0] for col in columnas]
    arbol['show'] = 'headings'
    
    for col in arbol['columns']:
        arbol.heading(col, text=col)
    
    cursor.execute(f"SELECT * FROM {mitabla}")
    filas = cursor.fetchall()
    
    for fila in filas:
        arbol.insert('', 'end', values=fila)

try:
    obtener_datos_conexion()  # Llama a la función para obtener los datos de conexión

    # Intentar conectar a la base de datos
    conexion = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    
    cursor = conexion.cursor()
    
    # Crear la ventana principal de la aplicación
    raiz = tk.Tk()
    Style(theme='cosmo')
    raiz.title("Gestor de Base de Datos")
    raiz.geometry("1200x700")
    
    marco_principal = ttk.Frame(raiz, padding="10")
    marco_principal.pack(fill=tk.BOTH, expand=True)
    
    marco_superior = ttk.Frame(marco_principal)
    marco_superior.pack(fill=tk.BOTH, expand=True)
    
    contienetablas = ttk.LabelFrame(marco_superior, text="Tablas en la BBDD", padding="10")
    contienetablas.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
    
    cursor.execute("SHOW TABLES IN " + database)
    tablas = cursor.fetchall()
    for tabla in tablas:
        ttk.Button(contienetablas, text=tabla[0], style="info.TButton", width=15, command=lambda t=tabla[0]: seleccionaTabla(t)).pack(pady=5)

    contienedatos = ttk.LabelFrame(marco_superior, text="Datos en mi sistema", padding="10")
    contienedatos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    marco_arbol = ttk.Frame(contienedatos)
    marco_arbol.pack(fill=tk.BOTH, expand=True)
    
    arbol = ttk.Treeview(marco_arbol)
    arbol.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    arbol.bind('<Button-1>', clickEnArbol)
    arbol.bind('<Configure>', ajustar_columnas)

    scrollbar_y = ttk.Scrollbar(marco_arbol, orient="vertical", command=arbol.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    scrollbar_x = ttk.Scrollbar(contienedatos, orient="horizontal", command=arbol.xview)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    
    arbol.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    ttk.Button(contienedatos, text="Eliminar registro seleccionado", command=eliminaRegistro, style="danger.TButton").pack(pady=10)

    marco_inferior = ttk.Frame(marco_principal, padding="10")
    marco_inferior.pack(fill=tk.X, pady=(10, 0))

    contieneformulario = ttk.LabelFrame(marco_inferior, text="Formulario de inserción/actualización", padding="10")
    contieneformulario.pack(fill=tk.X)

    if tablas:
        seleccionaTabla(tablas[0][0])

    raiz.mainloop()  # Mantiene la ventana principal activa

except Exception as e:
    messagebox.showerror("Error inesperado", f"Ha ocurrido un error: {str(e)}")

finally:
    if 'conexion' in locals() and conexion.is_connected():
        cursor.close()
        conexion.close()
        print("Conexión a MySQL cerrada")

