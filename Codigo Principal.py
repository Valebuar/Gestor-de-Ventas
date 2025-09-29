import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from BasededatosAdmonventasBD import DatabaseConnection
from BasededatosAdmonventasBD import DATABASE_CONFIG
import mysql.connector

# Crear instancia de conexión usando la configuración importada
db = DatabaseConnection(**DATABASE_CONFIG)

if db.connect():
    print("Conexión exitosa")
else:
    print("No se pudo conectar a la base de datos")

class SistemaVentas:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Ventas - admonventas")
        self.root.geometry("1200x800")

        # Definir el estilo para la interfaz
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TFrame', background='#e3f0ff')
        self.style.configure('TLabel', background="#ffffff", foreground='#003366', font=('Arial', 11))
        self.style.configure('TButton', background='#cce4ff', foreground='#003366', font=('Arial', 11, 'bold'))
        self.style.configure('Accent.TButton', background='#003366', foreground='white', font=('Arial', 11, 'bold'))
        self.style.configure('TNotebook', background='#e3f0ff')
        self.style.configure('TNotebook.Tab', background='#cce4ff', foreground='#003366', font=('Arial', 11, 'bold'))
        self.style.configure('Dark.TLabelframe', background='#b3d1f7', bordercolor="#6ba3dc")
        self.style.configure('Dark.TLabelframe.Label', background='#003366', foreground='white', font=('Arial', 11, 'bold'))
        self.style.configure('Dark.Treeview', background='#b3d1f7', fieldbackground='#b3d1f7', foreground='#003366', font=('Arial', 11))
        self.root.configure(bg='#e3f0ff')
        
        # Variables para ventas
        self.carrito = []
        self.total_venta = 0
        
    
    def crear_interfaz(self):
        """Función para crear la interfaz gráfica principal"""
        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear frames para cada pestaña
        self.frame_clientes = ttk.Frame(self.notebook)
        self.frame_productos = ttk.Frame(self.notebook)
        self.frame_categorias = ttk.Frame(self.notebook)
        self.frame_ventas = ttk.Frame(self.notebook)
        self.frame_detalle_ventas = ttk.Frame(self.notebook)
        
        # Añadir pestañas al notebook
        self.notebook.add(self.frame_clientes, text='Clientes')
        self.notebook.add(self.frame_productos, text='Productos')
        self.notebook.add(self.frame_categorias, text='Categorías')
        self.notebook.add(self.frame_ventas, text='Realizar Venta')
        self.notebook.add(self.frame_detalle_ventas, text='Historial Ventas')
        
        # Configurar cada pestaña
        self.configurar_pestaña_clientes()
        self.configurar_pestaña_productos()
        self.configurar_pestaña_categorias()
        self.configurar_pestaña_ventas()
        self.configurar_pestaña_detalle_ventas()
        
        # Cargar datos iniciales desde la base de datos
        self.cargar_datos_iniciales()

    def cargar_datos_iniciales(self):
        """Cargar datos iniciales desde la base de datos"""
        self.cargar_clientes_desde_bd()
        self.cargar_productos_desde_bd()
        self.cargar_categorias_desde_bd()
        self.cargar_clientes_combo()
        self.cargar_productos_combo()

     # ========== MÉTODOS PARA CLIENTES ==========

    def configurar_pestaña_clientes(self):
        """Formulario para la pestaña de clientes"""
        frame = ttk.Frame(self.frame_clientes)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Frame del formulario
        frame_form = ttk.LabelFrame(frame, text="Registrar Cliente", style='Dark.TLabelframe')
        frame_form.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_nombre_cliente = ttk.Entry(frame_form, width=30)
        self.entry_nombre_cliente.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Correo:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entry_correo_cliente = ttk.Entry(frame_form, width=30)
        self.entry_correo_cliente.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.entry_telefono_cliente = ttk.Entry(frame_form, width=30)
        self.entry_telefono_cliente.grid(row=2, column=1, padx=5, pady=5)

        # Frame de botones
        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(frame_botones, text="Guardar Cliente", command=self.guardar_cliente_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Actualizar Cliente", command=self.actualizar_cliente_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar Cliente", command=self.eliminar_cliente_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Limpiar Campos", command=self.limpiar_campos_cliente).pack(side='left', padx=5)

        # Treeview para mostrar clientes
        frame_tree = ttk.LabelFrame(frame, text="Clientes Registrados", style='Dark.TLabelframe')
        frame_tree.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree_clientes = ttk.Treeview(frame_tree, columns=("ID", "Nombre", "Correo", "Teléfono"), show='headings', style='Dark.Treeview')
        self.tree_clientes.heading("ID", text="ID")
        self.tree_clientes.heading("Nombre", text="Nombre")
        self.tree_clientes.heading("Correo", text="Correo")
        self.tree_clientes.heading("Teléfono", text="Teléfono")
        
        self.tree_clientes.column("ID", width=50)
        self.tree_clientes.column("Nombre", width=150)
        self.tree_clientes.column("Correo", width=150)
        self.tree_clientes.column("Teléfono", width=100)

        scrollbar = ttk.Scrollbar(frame_tree, orient='vertical', command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscrollcommand=scrollbar.set)
        
        self.tree_clientes.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.tree_clientes.bind('<<TreeviewSelect>>', self.seleccionar_cliente_bd)

    def cargar_clientes_desde_bd(self):
        """Cargar clientes desde la base de datos usando DatabaseConnection"""
        try:
            for item in self.tree_clientes.get_children():
                self.tree_clientes.delete(item)
            clientes = db.fetch_all("SELECT * FROM Clientes")
            for cliente in clientes:
                self.tree_clientes.insert('', 'end', values=cliente)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los clientes: {e}")

    def guardar_cliente_bd(self):
        """Guardar cliente en la base de datos usando DatabaseConnection"""
        try:
            nombre = self.entry_nombre_cliente.get()
            correo = self.entry_correo_cliente.get()
            telefono = self.entry_telefono_cliente.get()

            if not nombre:
                messagebox.showwarning("Advertencia", "El nombre es obligatorio")
                return

            query = "INSERT INTO Clientes (nombre, correo, telefono) VALUES (%s, %s, %s)"
            if db.execute_query(query, (nombre, correo, telefono)):
                messagebox.showinfo("Éxito", "Cliente guardado correctamente")
                self.limpiar_campos_cliente()
                self.cargar_clientes_desde_bd()
                self.cargar_clientes_combo()
            else:
                messagebox.showerror("Error", "No se pudo guardar el cliente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el cliente: {e}")

    def seleccionar_cliente_bd(self, event):
        """Seleccionar cliente del treeview"""
        seleccion = self.tree_clientes.selection()
        if seleccion:
            item = self.tree_clientes.item(seleccion[0])
            valores = item['values']
            
            self.entry_nombre_cliente.delete(0, tk.END)
            self.entry_nombre_cliente.insert(0, valores[1])
            
            self.entry_correo_cliente.delete(0, tk.END)
            self.entry_correo_cliente.insert(0, valores[2] if valores[2] else "")
            
            self.entry_telefono_cliente.delete(0, tk.END)
            self.entry_telefono_cliente.insert(0, valores[3] if valores[3] else "")

    def actualizar_cliente_bd(self):
        """Actualizar cliente en la base de datos usando DatabaseConnection"""
        try:
            seleccion = self.tree_clientes.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un cliente para actualizar")
                return

            cliente_id = self.tree_clientes.item(seleccion[0])['values'][0]
            nombre = self.entry_nombre_cliente.get()
            correo = self.entry_correo_cliente.get()
            telefono = self.entry_telefono_cliente.get()

            if not nombre:
                messagebox.showwarning("Advertencia", "El nombre es obligatorio")
                return

            query = "UPDATE Clientes SET nombre=%s, correo=%s, telefono=%s WHERE cliente_id=%s"
            if db.execute_query(query, (nombre, correo, telefono, cliente_id)):
                messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
                self.limpiar_campos_cliente()
                self.cargar_clientes_desde_bd()
                self.cargar_clientes_combo()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el cliente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el cliente: {e}")

    def eliminar_cliente_bd(self):
        """Eliminar cliente de la base de datos usando DatabaseConnection"""
        try:
            seleccion = self.tree_clientes.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
                return

            cliente_id = self.tree_clientes.item(seleccion[0])['values'][0]

            respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este cliente?")
            if respuesta:
                query = "DELETE FROM Clientes WHERE cliente_id=%s"
                if db.execute_query(query, (cliente_id,)):
                    messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                    self.limpiar_campos_cliente()
                    self.cargar_clientes_desde_bd()
                    self.cargar_clientes_combo()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el cliente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el cliente: {e}")

    def limpiar_campos_cliente(self):
        """Limpiar campos del formulario de clientes"""
        self.entry_nombre_cliente.delete(0, tk.END)
        self.entry_correo_cliente.delete(0, tk.END)
        self.entry_telefono_cliente.delete(0, tk.END)

 # ========== MÉTODOS PARA PRODUCTOS ==========

    def configurar_pestaña_productos(self):
        """Formulario para la pestaña de productos"""
        frame = ttk.Frame(self.frame_productos)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Frame del formulario
        frame_form = ttk.LabelFrame(frame, text="Registrar Producto", style='Dark.TLabelframe')
        frame_form.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_nombre_producto = ttk.Entry(frame_form, width=30)
        self.entry_nombre_producto.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Precio:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entry_precio_producto = ttk.Entry(frame_form, width=30)
        self.entry_precio_producto.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Stock:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.entry_stock_producto = ttk.Entry(frame_form, width=30)
        self.entry_stock_producto.grid(row=2, column=1, padx=5, pady=5)

        # Frame de botones
        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(frame_botones, text="Guardar Producto", command=self.guardar_producto_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Actualizar Producto", command=self.actualizar_producto_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar Producto", command=self.eliminar_producto_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Limpiar Campos", command=self.limpiar_campos_producto).pack(side='left', padx=5)

        # Treeview para mostrar productos
        frame_tree = ttk.LabelFrame(frame, text="Productos Registrados", style='Dark.TLabelframe')
        frame_tree.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree_productos = ttk.Treeview(frame_tree, columns=("ID", "Nombre", "Precio", "Stock"), show='headings', style='Dark.Treeview')
        self.tree_productos.heading("ID", text="ID")
        self.tree_productos.heading("Nombre", text="Nombre")
        self.tree_productos.heading("Precio", text="Precio")
        self.tree_productos.heading("Stock", text="Stock")
        
        self.tree_productos.column("ID", width=50)
        self.tree_productos.column("Nombre", width=150)
        self.tree_productos.column("Precio", width=100)
        self.tree_productos.column("Stock", width=80)

        scrollbar = ttk.Scrollbar(frame_tree, orient='vertical', command=self.tree_productos.yview)
        self.tree_productos.configure(yscrollcommand=scrollbar.set)
        
        self.tree_productos.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.tree_productos.bind('<<TreeviewSelect>>', self.seleccionar_producto_bd)

    def cargar_productos_desde_bd(self):
        """Cargar productos desde la base de datos usando DatabaseConnection"""
        try:
            for item in self.tree_productos.get_children():
                self.tree_productos.delete(item)
            productos = db.fetch_all("SELECT * FROM Productos")
            for producto in productos:
                self.tree_productos.insert('', 'end', values=producto)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los productos: {e}")

    def guardar_producto_bd(self):
        """Guardar producto en la base de datos usando DatabaseConnection"""
        try:
            nombre = self.entry_nombre_producto.get()
            precio = self.entry_precio_producto.get()
            stock = self.entry_stock_producto.get()

            if not nombre or not precio or not stock:
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
                return

            query = "INSERT INTO Productos (nombre, precio, stock) VALUES (%s, %s, %s)"
            if db.execute_query(query, (nombre, float(precio), int(stock))):
                messagebox.showinfo("Éxito", "Producto guardado correctamente")
                self.limpiar_campos_producto()
                self.cargar_productos_desde_bd()
                self.cargar_productos_combo()
            else:
                messagebox.showerror("Error", "No se pudo guardar el producto")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el producto: {e}")

    def seleccionar_producto_bd(self, event):
        """Seleccionar producto del treeview"""
        seleccion = self.tree_productos.selection()
        if seleccion:
            item = self.tree_productos.item(seleccion[0])
            valores = item['values']
            
            self.entry_nombre_producto.delete(0, tk.END)
            self.entry_nombre_producto.insert(0, valores[1])
            
            self.entry_precio_producto.delete(0, tk.END)
            self.entry_precio_producto.insert(0, str(valores[2]))
            
            self.entry_stock_producto.delete(0, tk.END)
            self.entry_stock_producto.insert(0, str(valores[3]))

    def actualizar_producto_bd(self):
        """Actualizar producto en la base de datos usando DatabaseConnection"""
        try:
            seleccion = self.tree_productos.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un producto para actualizar")
                return

            producto_id = self.tree_productos.item(seleccion[0])['values'][0]
            nombre = self.entry_nombre_producto.get()
            precio = self.entry_precio_producto.get()
            stock = self.entry_stock_producto.get()

            if not nombre or not precio or not stock:
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
                return

            query = "UPDATE Productos SET nombre=%s, precio=%s, stock=%s WHERE producto_id=%s"
            if db.execute_query(query, (nombre, float(precio), int(stock), producto_id)):
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                self.limpiar_campos_producto()
                self.cargar_productos_desde_bd()
                self.cargar_productos_combo()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el producto")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el producto: {e}")

    def eliminar_producto_bd(self):
        """Eliminar producto de la base de datos usando DatabaseConnection"""
        try:
            seleccion = self.tree_productos.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
                return

            producto_id = self.tree_productos.item(seleccion[0])['values'][0]

            respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este producto?")
            if respuesta:
                query = "DELETE FROM Productos WHERE producto_id=%s"
                if db.execute_query(query, (producto_id,)):
                    messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                    self.limpiar_campos_producto()
                    self.cargar_productos_desde_bd()
                    self.cargar_productos_combo()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el producto")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")

    def limpiar_campos_producto(self):
        """Limpiar campos del formulario de productos"""
        self.entry_nombre_producto.delete(0, tk.END)
        self.entry_precio_producto.delete(0, tk.END)
        self.entry_stock_producto.delete(0, tk.END)

# ========== MÉTODOS PARA CATEGORÍAS ==========

    def configurar_pestaña_categorias(self):
        """Formulario para la pestaña de categorías"""
        frame = ttk.Frame(self.frame_categorias)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Frame del formulario
        frame_form = ttk.LabelFrame(frame, text="Registrar Categoría", style='Dark.TLabelframe')
        frame_form.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_nombre_categoria = ttk.Entry(frame_form, width=30)
        self.entry_nombre_categoria.grid(row=0, column=1, padx=5, pady=5)

        # Frame de botones
        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(frame_botones, text="Guardar Categoría", command=self.guardar_categoria_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Actualizar Categoría", command=self.actualizar_categoria_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar Categoría", command=self.eliminar_categoria_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Limpiar Campo", command=self.limpiar_campos_categoria).pack(side='left', padx=5)

        # Treeview para mostrar categorías
        frame_tree = ttk.LabelFrame(frame, text="Categorías Registradas", style='Dark.TLabelframe')
        frame_tree.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree_categorias = ttk.Treeview(frame_tree, columns=("ID", "Nombre"), show='headings', style='Dark.Treeview')
        self.tree_categorias.heading("ID", text="ID")
        self.tree_categorias.heading("Nombre", text="Nombre")
        
        self.tree_categorias.column("ID", width=50)
        self.tree_categorias.column("Nombre", width=200)

        scrollbar = ttk.Scrollbar(frame_tree, orient='vertical', command=self.tree_categorias.yview)
        self.tree_categorias.configure(yscrollcommand=scrollbar.set)
        
        self.tree_categorias.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.tree_categorias.bind('<<TreeviewSelect>>', self.seleccionar_categoria_bd)

    def cargar_categorias_desde_bd(self):
        """Cargar categorías desde la base de datos usando DatabaseConnection"""
        try:
            for item in self.tree_categorias.get_children():
                self.tree_categorias.delete(item)
            categorias = db.fetch_all("SELECT * FROM Categorias")
            for categoria in categorias:
                self.tree_categorias.insert('', 'end', values=categoria)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las categorías: {e}")

    def guardar_categoria_bd(self):
        """Guardar categoría en la base de datos usando DatabaseConnection"""
        try:
            nombre = self.entry_nombre_categoria.get()

            if not nombre:
                messagebox.showwarning("Advertencia", "El nombre es obligatorio")
                return

            query = "INSERT INTO Categorias (nombre) VALUES (%s)"
            if db.execute_query(query, (nombre,)):
                messagebox.showinfo("Éxito", "Categoría guardada correctamente")
                self.limpiar_campos_categoria()
                self.cargar_categorias_desde_bd()
            else:
                messagebox.showerror("Error", "No se pudo guardar la categoría")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la categoría: {e}")

    def seleccionar_categoria_bd(self, event):
        """Seleccionar categoría del treeview"""
        seleccion = self.tree_categorias.selection()
        if seleccion:
            item = self.tree_categorias.item(seleccion[0])
            valores = item['values']
            
            self.entry_nombre_categoria.delete(0, tk.END)
            self.entry_nombre_categoria.insert(0, valores[1])

    def actualizar_categoria_bd(self):
        """Actualizar categoría en la base de datos usando DatabaseConnection"""
        try:
            seleccion = self.tree_categorias.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione una categoría para actualizar")
                return

            categoria_id = self.tree_categorias.item(seleccion[0])['values'][0]
            nombre = self.entry_nombre_categoria.get()

            if not nombre:
                messagebox.showwarning("Advertencia", "El nombre es obligatorio")
                return

            query = "UPDATE Categorias SET nombre=%s WHERE categoria_id=%s"
            if db.execute_query(query, (nombre, categoria_id)):
                messagebox.showinfo("Éxito", "Categoría actualizada correctamente")
                self.limpiar_campos_categoria()
                self.cargar_categorias_desde_bd()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la categoría")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la categoría: {e}")

    def eliminar_categoria_bd(self):
        """Eliminar categoría de la base de datos usando DatabaseConnection"""
        try:
            seleccion = self.tree_categorias.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione una categoría para eliminar")
                return

            categoria_id = self.tree_categorias.item(seleccion[0])['values'][0]

            respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta categoría?")
            if respuesta:
                query = "DELETE FROM Categorias WHERE categoria_id=%s"
                if db.execute_query(query, (categoria_id,)):
                    messagebox.showinfo("Éxito", "Categoría eliminada correctamente")
                    self.limpiar_campos_categoria()
                    self.cargar_categorias_desde_bd()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la categoría")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la categoría: {e}")

    def limpiar_campos_categoria(self):
        """Limpiar campo del formulario de categorías"""
        self.entry_nombre_categoria.delete(0, tk.END)

# ========== MÉTODOS PARA VENTAS ==========
# (Los métodos de ventas se mantienen igual que en tu código original)

    def configurar_pestaña_ventas(self):
        """Configurar la pestaña para realizar ventas"""
        # Frame principal dividido en dos partes
        frame_principal = ttk.Frame(self.frame_ventas)
        frame_principal.pack(fill='both', expand=True, padx=10, pady=10)
        # Frame izquierdo - Selección de productos
        frame_izquierdo = ttk.LabelFrame(frame_principal, text="Seleccionar Productos", style='Dark.TLabelframe')
        frame_izquierdo.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        # Frame derecho - Carrito y datos de venta
        frame_derecho = ttk.LabelFrame(frame_principal, text="Carrito de Compra", style='Dark.TLabelframe')
        frame_derecho.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        # ========== FRAME IZQUIERDO - SELECCIÓN ========== 
        # Cliente
        ttk.Label(frame_izquierdo, text="Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.combo_cliente = ttk.Combobox(frame_izquierdo, width=30)
        self.combo_cliente.grid(row=0, column=1, padx=5, pady=5)
        self.cargar_clientes_combo()
        # Producto
        ttk.Label(frame_izquierdo, text="Producto:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.combo_producto = ttk.Combobox(frame_izquierdo, width=30)
        self.combo_producto.grid(row=1, column=1, padx=5, pady=5)
        self.combo_producto.bind('<<ComboboxSelected>>', self.actualizar_info_producto)
        self.cargar_productos_combo()
        # Información del producto seleccionado
        self.frame_info_producto = ttk.LabelFrame(frame_izquierdo, text="Información del Producto")
        self.frame_info_producto.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='we')
        ttk.Label(self.frame_info_producto, text="Precio:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.label_precio = ttk.Label(self.frame_info_producto, text="$0.00")
        self.label_precio.grid(row=0, column=1, padx=5, pady=2, sticky='w')
        ttk.Label(self.frame_info_producto, text="Stock:").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.label_stock = ttk.Label(self.frame_info_producto, text="0")
        self.label_stock.grid(row=1, column=1, padx=5, pady=2, sticky='w')
        # Cantidad
        ttk.Label(frame_izquierdo, text="Cantidad:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.spin_cantidad = tk.Spinbox(frame_izquierdo, from_=1, to=100, width=10)
        self.spin_cantidad.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        # Botón agregar al carrito
        ttk.Button(frame_izquierdo, text="Agregar al Carrito", 
                    command=self.agregar_al_carrito).grid(row=4, column=0, columnspan=2, pady=10)
        # ========== FRAME DERECHO - CARRITO ========== 
        # Treeview para el carrito
        self.tree_carrito = ttk.Treeview(frame_derecho, 
                    columns=('Producto', 'Cantidad', 'Precio', 'Subtotal'), 
                    show='headings', style='Dark.Treeview')
        self.tree_carrito.heading('Producto', text='Producto')
        self.tree_carrito.heading('Cantidad', text='Cantidad')
        self.tree_carrito.heading('Precio', text='Precio Unit.')
        self.tree_carrito.heading('Subtotal', text='Subtotal')
        self.tree_carrito.column('Producto', width=150)
        self.tree_carrito.column('Cantidad', width=80)
        self.tree_carrito.column('Precio', width=100)
        self.tree_carrito.column('Subtotal', width=100)
        scrollbar_carrito = ttk.Scrollbar(frame_derecho, orient='vertical', command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=scrollbar_carrito.set)
        self.tree_carrito.pack(fill='both', expand=True)
        scrollbar_carrito.pack(side='right', fill='y')
        # Total
        frame_total = ttk.Frame(frame_derecho)
        frame_total.pack(fill='x', pady=10)
        ttk.Label(frame_total, text="TOTAL:", font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        self.label_total = ttk.Label(frame_total, text="$0.00", font=('Arial', 12, 'bold'))
        self.label_total.pack(side='left', padx=5)
        # Botones del carrito alineados verticalmente a la derecha
        frame_botones_carrito = ttk.Frame(frame_derecho)
        frame_botones_carrito.pack(side='right', fill='y', padx=10, pady=10)
        ttk.Button(frame_botones_carrito, text="Quitar Producto", command=self.quitar_del_carrito, width=20).pack(pady=5)
        ttk.Button(frame_botones_carrito, text="Limpiar Carrito", command=self.limpiar_carrito, width=20).pack(pady=5)
        ttk.Button(frame_botones_carrito, text="Realizar Venta", command=self.realizar_venta, style='Accent.TButton', width=20).pack(pady=5)

    def configurar_pestaña_detalle_ventas(self):
        """Configurar la pestaña para ver el historial de ventas"""
        frame_principal = ttk.Frame(self.frame_detalle_ventas)
        frame_principal.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame para filtros
        frame_filtros = ttk.LabelFrame(frame_principal, text="Filtros")
        frame_filtros.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Fecha desde:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_fecha_desde = ttk.Entry(frame_filtros, width=12)
        self.entry_fecha_desde.grid(row=0, column=1, padx=5, pady=5)
        self.entry_fecha_desde.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(frame_filtros, text="Fecha hasta:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_fecha_hasta = ttk.Entry(frame_filtros, width=12)
        self.entry_fecha_hasta.grid(row=0, column=3, padx=5, pady=5)
        self.entry_fecha_hasta.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(frame_filtros, text="Buscar", 
                    command=self.cargar_ventas).grid(row=0, column=4, padx=5, pady=5)
        
        # Treeview para ventas
        frame_tree = ttk.LabelFrame(frame_principal, text="Ventas Realizadas", style='Dark.TLabelframe')
        frame_tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.tree_ventas = ttk.Treeview(frame_tree, 
                            columns=('ID', 'Fecha', 'Cliente', 'Total'), 
                            show='headings', style='Dark.Treeview')
        self.tree_ventas.heading('ID', text='ID Venta')
        self.tree_ventas.heading('Fecha', text='Fecha')
        self.tree_ventas.heading('Cliente', text='Cliente')
        self.tree_ventas.heading('Total', text='Total')
        self.tree_ventas.column('ID', width=80)
        self.tree_ventas.column('Fecha', width=150)
        self.tree_ventas.column('Cliente', width=200)
        self.tree_ventas.column('Total', width=100)
        scrollbar_ventas = ttk.Scrollbar(frame_tree, orient='vertical', command=self.tree_ventas.yview)
        self.tree_ventas.configure(yscrollcommand=scrollbar_ventas.set)
        self.tree_ventas.pack(side='left', fill='both', expand=True)
        scrollbar_ventas.pack(side='right', fill='y')
        # Bind para mostrar detalles
        self.tree_ventas.bind('<<TreeviewSelect>>', self.mostrar_detalle_venta)
        # Treeview para detalle de venta seleccionada
        frame_detalle = ttk.LabelFrame(frame_principal, text="Detalle de Venta", style='Dark.TLabelframe')
        frame_detalle.pack(fill='x', padx=5, pady=5)
        
        self.tree_detalle_venta = ttk.Treeview(frame_detalle, 
                            columns=('Producto', 'Cantidad', 'Precio', 'Subtotal'), 
                            show='headings', style='Dark.Treeview')
        self.tree_detalle_venta.heading('Producto', text='Producto')
        self.tree_detalle_venta.heading('Cantidad', text='Cantidad')
        self.tree_detalle_venta.heading('Precio', text='Precio Unit.')
        self.tree_detalle_venta.heading('Subtotal', text='Subtotal')
        for col in ('Producto', 'Cantidad', 'Precio', 'Subtotal'):
            self.tree_detalle_venta.column(col, width=120)
        self.tree_detalle_venta.pack(fill='x')
        # Cargar ventas iniciales
        self.cargar_ventas()

    def cargar_clientes_combo(self):
        """Cargar clientes en el combobox usando DatabaseConnection"""
        try:
            clientes = db.fetch_all("SELECT cliente_id, nombre FROM Clientes")
            self.combo_cliente['values'] = [f"{cliente[0]} - {cliente[1]}" for cliente in clientes]
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los clientes: {e}")

    def cargar_productos_combo(self):
        """Cargar productos en el combobox usando DatabaseConnection"""
        try:
            productos = db.fetch_all("SELECT producto_id, nombre, precio, stock FROM Productos WHERE stock > 0")
            self.productos_disponibles = {f"{prod[0]} - {prod[1]}": prod for prod in productos}
            self.combo_producto['values'] = list(self.productos_disponibles.keys())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los productos: {e}")

    def actualizar_info_producto(self, event=None):
        """Actualizar la información del producto seleccionado"""
        producto_seleccionado = self.combo_producto.get()
        if producto_seleccionado in self.productos_disponibles:
            producto = self.productos_disponibles[producto_seleccionado]
            self.label_precio.config(text=f"${producto[2]:.2f}")
            self.label_stock.config(text=f"{producto[3]}")
            self.spin_cantidad.config(to=producto[3])

    def agregar_al_carrito(self):
        """Agregar producto al carrito de compras"""
        try:
            # Validar selección de producto
            producto_seleccionado = self.combo_producto.get()
            if not producto_seleccionado:
                messagebox.showwarning("Advertencia", "Seleccione un producto")
                return
            
            # Validar selección de cliente
            if not self.combo_cliente.get():
                messagebox.showwarning("Advertencia", "Seleccione un cliente")
                return
            
            # Obtener datos del producto
            producto = self.productos_disponibles[producto_seleccionado]
            producto_id = producto[0]
            nombre_producto = producto_seleccionado.split(' - ')[1]
            precio = producto[2]
            stock = producto[3]
            
            # Validar cantidad
            cantidad = int(self.spin_cantidad.get())
            if cantidad <= 0:
                messagebox.showwarning("Advertencia", "La cantidad debe ser mayor a 0")
                return
            
            if cantidad > stock:
                messagebox.showwarning("Advertencia", "No hay suficiente stock disponible")
                return
            
            # Calcular subtotal
            subtotal = precio * cantidad
            
            # Agregar al carrito
            item_carrito = {
                'producto_id': producto_id,
                'nombre': nombre_producto,
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': subtotal
            }
            
            # Verificar si el producto ya está en el carrito
            for item in self.carrito:
                if item['producto_id'] == producto_id:
                    item['cantidad'] += cantidad
                    item['subtotal'] = item['precio'] * item['cantidad']
                    break
            else:
                self.carrito.append(item_carrito)
            
            # Actualizar interfaz
            self.actualizar_carrito()
            
            # Limpiar selección
            self.combo_producto.set('')
            self.label_precio.config(text="$0.00")
            self.label_stock.config(text="0")
            self.spin_cantidad.delete(0, tk.END)
            self.spin_cantidad.insert(0, "1")
            
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar al carrito: {e}")

    def actualizar_carrito(self):
        """Actualizar la visualización del carrito"""
        # Limpiar treeview
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        
        # Calcular total
        self.total_venta = 0
        
        # Agregar items al treeview
        for item in self.carrito:
            self.tree_carrito.insert('', 'end', values=(
                item['nombre'],
                item['cantidad'],
                f"${item['precio']:.2f}",
                f"${item['subtotal']:.2f}"
            ))
            self.total_venta += item['subtotal']
        
        # Actualizar total
        self.label_total.config(text=f"${self.total_venta:.2f}")

    def quitar_del_carrito(self):
        """Quitar producto seleccionado del carrito"""
        seleccion = self.tree_carrito.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto del carrito")
            return
        
        # Obtener índice del item seleccionado
        index = self.tree_carrito.index(seleccion[0])
        
        # Remover del carrito
        if 0 <= index < len(self.carrito):
            self.carrito.pop(index)
        
        # Actualizar interfaz
        self.actualizar_carrito()

    def limpiar_carrito(self):
        """Limpiar todo el carrito"""
        self.carrito.clear()
        self.actualizar_carrito()

    def realizar_venta(self):
        """Procesar la venta completa usando DatabaseConnection"""
        try:
            if not self.carrito:
                messagebox.showwarning("Advertencia", "El carrito está vacío")
                return
            if not self.combo_cliente.get():
                messagebox.showwarning("Advertencia", "Seleccione un cliente")
                return
            cliente_id = int(self.combo_cliente.get().split(' - ')[0])
            # 1. Insertar venta
            query_venta = "INSERT INTO Ventas (cliente_id, total) VALUES (%s, %s)"
            if db.execute_query(query_venta, (cliente_id, self.total_venta)):
                # Obtener el ID de la venta recién creada
                venta_id = db.fetch_all("SELECT MAX(venta_id) FROM Ventas")[0][0]
                # 2. Insertar detalles de venta y actualizar stock
                for item in self.carrito:
                    query_detalle = "INSERT INTO DetalleVentas (venta_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)"
                    db.execute_query(query_detalle, (venta_id, item['producto_id'], item['cantidad'], item['precio']))
                    query_update_stock = "UPDATE Productos SET stock = stock - %s WHERE producto_id = %s"
                    db.execute_query(query_update_stock, (item['cantidad'], item['producto_id']))
                messagebox.showinfo("Éxito", f"Venta realizada correctamente!\nNúmero de venta: {venta_id}\nTotal: ${self.total_venta:.2f}")
                self.limpiar_carrito()
                self.cargar_productos_combo()
                self.cargar_ventas()
                self.cargar_productos_desde_bd()
            else:
                messagebox.showerror("Error", "No se pudo registrar la venta")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la venta: {e}")

    def cargar_ventas(self):
        """Cargar el historial de ventas usando DatabaseConnection"""
        try:
            for item in self.tree_ventas.get_children():
                self.tree_ventas.delete(item)
            fecha_desde = self.entry_fecha_desde.get()
            fecha_hasta = self.entry_fecha_hasta.get()
            query = """
            SELECT v.venta_id, v.fecha, c.nombre, v.total 
            FROM Ventas v 
            INNER JOIN Clientes c ON v.cliente_id = c.cliente_id 
            WHERE DATE(v.fecha) BETWEEN %s AND %s 
            ORDER BY v.fecha DESC
            """
            ventas = db.fetch_all(query, (fecha_desde, fecha_hasta))
            for venta in ventas:
                self.tree_ventas.insert('', 'end', values=venta)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las ventas: {e}")

    def mostrar_detalle_venta(self, event):
        """Mostrar el detalle de la venta seleccionada usando DatabaseConnection"""
        try:
            seleccion = self.tree_ventas.selection()
            if not seleccion:
                return
            venta_id = self.tree_ventas.item(seleccion[0])['values'][0]
            for item in self.tree_detalle_venta.get_children():
                self.tree_detalle_venta.delete(item)
            query = """
            SELECT p.nombre, dv.cantidad, dv.precio_unitario, (dv.cantidad * dv.precio_unitario) as subtotal
            FROM DetalleVentas dv
            INNER JOIN Productos p ON dv.producto_id = p.producto_id
            WHERE dv.venta_id = %s
            """
            detalles = db.fetch_all(query, (venta_id,))
            for detalle in detalles:
                self.tree_detalle_venta.insert('', 'end', values=detalle)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el detalle: {e}")

    def __del__(self):
        """Destructor para cerrar la conexión"""
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

def main():
    root = tk.Tk()
    app = SistemaVentas(root)
    app.crear_interfaz()
    root.mainloop()

if __name__ == "__main__":
    main()