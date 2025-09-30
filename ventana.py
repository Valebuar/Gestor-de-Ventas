import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from conexion.BasededatosAdmonventasBD import DatabaseConnection, DATABASE_CONFIG

# Nuevas importaciones
import pandas as pd
from PIL import Image, ImageTk
import os
import shutil
from tkcalendar import DateEntry


db = DatabaseConnection(**DATABASE_CONFIG)

class SistemaVentas:
    def __init__(self, root):
        self.root = root

        self.root.title("Sistema de Gestión de Ventas - admonventas")
        self.root.geometry("1200x800")
        self.root.iconbitmap("favicon.ico")
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
        self.carrito = []
        self.total_venta = 0
        self.ruta_imagen_producto = None # Para guardar la ruta de la imagen seleccionada

        # Crear directorio para imágenes si no existe
        os.makedirs("imagenes_productos", exist_ok=True)
        
        # Registrar funciones de validación
        self.vcmd_integer = (self.root.register(self.validate_integer), '%P')
        self.vcmd_float = (self.root.register(self.validate_float), '%P')

    def crear_interfaz(self):
      
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        self.frame_clientes = ttk.Frame(self.notebook)
        self.frame_productos = ttk.Frame(self.notebook)
        self.frame_categorias = ttk.Frame(self.notebook)
        self.frame_ventas = ttk.Frame(self.notebook)
        self.frame_detalle_ventas = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_clientes, text='Clientes')
        self.notebook.add(self.frame_productos, text='Productos')
        self.notebook.add(self.frame_categorias, text='Categorías')
        self.notebook.add(self.frame_ventas, text='Realizar Venta')
        self.notebook.add(self.frame_detalle_ventas, text='Historial Ventas')

        self.configurar_pestaña_clientes()
        self.configurar_pestaña_productos()
        self.configurar_pestaña_categorias()
        self.configurar_pestaña_ventas()
        self.configurar_pestaña_detalle_ventas()
        self.cargar_datos_iniciales()

    def cargar_datos_iniciales(self):
        self.cargar_clientes_desde_bd()
        self.cargar_productos_desde_bd()
        self.cargar_categorias_desde_bd()
        self.cargar_clientes_combo()
        self.cargar_productos_combo()

    # ========== MÉTODOS PARA CLIENTES ==========
    
    def validate_integer(self, P):
        """Valida que la entrada sea un número entero."""
        return P.isdigit() or P == ""

    def validate_float(self, P):
        """Valida que la entrada sea un número flotante."""
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    def configurar_pestaña_clientes(self):
        frame = ttk.Frame(self.frame_clientes)

        frame.pack(fill='both', expand=True, padx=10, pady=10)
        frame_form = ttk.LabelFrame(frame, text="Registrar Cliente", style='Dark.TLabelframe')
        frame_form.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_nombre_cliente = ttk.Entry(frame_form, width=30)
        self.entry_nombre_cliente.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Correo:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entry_correo_cliente = ttk.Entry(frame_form, width=30)
        self.entry_correo_cliente.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.entry_telefono_cliente = ttk.Entry(frame_form, width=30, validate="key", validatecommand=self.vcmd_integer)
        self.entry_telefono_cliente.grid(row=2, column=1, padx=5, pady=5)

        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(frame_botones, text="Guardar Cliente", command=self.guardar_cliente_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Actualizar Cliente", command=self.actualizar_cliente_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar Cliente", command=self.eliminar_cliente_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Limpiar Campos", command=self.limpiar_campos_cliente).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Exportar a Excel", command=self.exportar_clientes_excel).pack(side='left', padx=5)

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
        try:
            for item in self.tree_clientes.get_children():
                self.tree_clientes.delete(item)
            from modelos.cliente import Cliente
            clientes = Cliente.obtener_todos()
            for cliente in clientes:
                self.tree_clientes.insert('', 'end', values=(cliente.cliente_id, cliente.nombre, cliente.correo, cliente.telefono))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los clientes: {e}")

    def guardar_cliente_bd(self):
        try:
            from modelos.cliente import Cliente
            nombre = self.entry_nombre_cliente.get()
            correo = self.entry_correo_cliente.get()
            telefono = self.entry_telefono_cliente.get()
            if not nombre:
                messagebox.showwarning("Advertencia", "El nombre es obligatorio")
                return
            if Cliente.insertar(nombre, correo, telefono):
                messagebox.showinfo("Éxito", "Cliente guardado correctamente")
                self.limpiar_campos_cliente()
                self.cargar_clientes_desde_bd()
                self.cargar_clientes_combo()
            else:
                messagebox.showerror("Error", "No se pudo guardar el cliente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el cliente: {e}")

    def seleccionar_cliente_bd(self, event):
        seleccion = self.tree_clientes.selection()
        if seleccion:
            item = self.tree_clientes.item(seleccion[0])['values']
            self.entry_nombre_cliente.delete(0, tk.END); self.entry_nombre_cliente.insert(0, item[1])
            self.entry_correo_cliente.delete(0, tk.END); self.entry_correo_cliente.insert(0, item[2])
            self.entry_telefono_cliente.delete(0, tk.END); self.entry_telefono_cliente.insert(0, item[3])

    def actualizar_cliente_bd(self):
        try:
            from modelos.cliente import Cliente
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
            
            if Cliente.actualizar(cliente_id, nombre, correo, telefono):
                messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
                self.limpiar_campos_cliente()
                self.cargar_clientes_desde_bd()
                self.cargar_clientes_combo()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el cliente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el cliente: {e}")

    def eliminar_cliente_bd(self):
        try:
            from modelos.cliente import Cliente
            seleccion = self.tree_clientes.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
                return
            cliente_id = self.tree_clientes.item(seleccion[0])['values'][0]
            respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este cliente?")
            if respuesta:
                if Cliente.eliminar(cliente_id):
                    messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                    self.limpiar_campos_cliente()
                    self.cargar_clientes_desde_bd()
                    self.cargar_clientes_combo()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el cliente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el cliente: {e}")

    def limpiar_campos_cliente(self):
        self.entry_nombre_cliente.delete(0, tk.END)
        self.entry_correo_cliente.delete(0, tk.END)
        self.entry_telefono_cliente.delete(0, tk.END)
        self.tree_clientes.selection_remove(self.tree_clientes.selection())

    def exportar_clientes_excel(self):
        try:
            from modelos.cliente import Cliente
            clientes = Cliente.obtener_todos()
            if not clientes:
                messagebox.showinfo("Información", "No hay clientes para exportar.")
                return
            datos = [{'ID': c.cliente_id, 'Nombre': c.nombre, 'Correo': c.correo, 'Teléfono': c.telefono} for c in clientes]
            df = pd.DataFrame(datos)
            df.to_excel("reporte_clientes.xlsx", index=False, engine='openpyxl')
            messagebox.showinfo("Éxito", "Reporte de clientes exportado a 'reporte_clientes.xlsx'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")

    # ========== MÉTODOS PARA PRODUCTOS ==========

    def configurar_pestaña_productos(self):
        frame = ttk.Frame(self.frame_productos)

        frame.pack(fill='both', expand=True, padx=10, pady=10)
        frame_form = ttk.LabelFrame(frame, text="Registrar Producto", style='Dark.TLabelframe')
        frame_form.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_nombre_producto = ttk.Entry(frame_form, width=30)
        self.entry_nombre_producto.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Precio:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entry_precio_producto = ttk.Entry(frame_form, width=30, validate="key", validatecommand=self.vcmd_float)
        self.entry_precio_producto.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Stock:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.entry_stock_producto = ttk.Entry(frame_form, width=30, validate="key", validatecommand=self.vcmd_integer)
        self.entry_stock_producto.grid(row=2, column=1, padx=5, pady=5)

        # Nuevos widgets para la imagen
        ttk.Button(frame_form, text="Seleccionar Imagen", command=self.seleccionar_imagen_producto).grid(row=0, column=2, padx=5, pady=5)
        self.canvas_imagen = tk.Canvas(frame_form, width=150, height=150, bg="white", relief="solid")
        self.canvas_imagen.grid(row=0, column=3, rowspan=3, padx=10, pady=5)

        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=3, column=0, columnspan=4, pady=10)

        ttk.Button(frame_botones, text="Guardar Producto", command=self.guardar_producto_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Actualizar Producto", command=self.actualizar_producto_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar Producto", command=self.eliminar_producto_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Limpiar Campos", command=self.limpiar_campos_producto).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Exportar a Excel", command=self.exportar_productos_excel).pack(side='left', padx=5)

        frame_tree = ttk.LabelFrame(frame, text="Productos Registrados", style='Dark.TLabelframe')
        frame_tree.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree_productos = ttk.Treeview(frame_tree, columns=("ID", "Nombre", "Precio", "Stock", "Imagen"), show='headings', style='Dark.Treeview')
        self.tree_productos.heading("ID", text="ID")
        self.tree_productos.heading("Nombre", text="Nombre")
        self.tree_productos.heading("Precio", text="Precio")
        self.tree_productos.heading("Stock", text="Stock")
        self.tree_productos.column("ID", width=50)
        self.tree_productos.column("Nombre", width=150)
        self.tree_productos.column("Precio", width=100)
        self.tree_productos.column("Stock", width=80)
        self.tree_productos.column("Imagen", width=0, stretch=tk.NO) # Ocultar columna de imagen


        scrollbar = ttk.Scrollbar(frame_tree, orient='vertical', command=self.tree_productos.yview)
        self.tree_productos.configure(yscrollcommand=scrollbar.set)
        self.tree_productos.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.tree_productos.bind('<<TreeviewSelect>>', self.seleccionar_producto_bd)

    def cargar_productos_desde_bd(self):
        try:
            from modelos.producto import Producto
            for item in self.tree_productos.get_children():
                self.tree_productos.delete(item)
            productos = Producto.obtener_todos()
            for producto in productos:
                self.tree_productos.insert('', 'end', values=(producto.producto_id, producto.nombre, producto.precio, producto.stock, producto.imagen or ''))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los productos: {e}")

    def guardar_producto_bd(self):
        try:
            from modelos.producto import Producto
            nombre = self.entry_nombre_producto.get()
            precio = self.entry_precio_producto.get()
            stock = self.entry_stock_producto.get()
            if not nombre or not precio or not stock:
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
                return
            if Producto.insertar(nombre, precio, stock, self.ruta_imagen_producto):
                messagebox.showinfo("Éxito", "Producto guardado correctamente")
                self.limpiar_campos_producto()
                self.cargar_productos_desde_bd()
                self.ruta_imagen_producto = None # Limpiar la ruta después de guardar
                self.cargar_productos_combo()
            else:
                messagebox.showerror("Error", "No se pudo guardar el producto")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el producto: {e}")

    def seleccionar_producto_bd(self, event):
        seleccion = self.tree_productos.selection()
        if seleccion:
            item = self.tree_productos.item(seleccion[0])['values']
            self.entry_nombre_producto.delete(0, tk.END); self.entry_nombre_producto.insert(0, item[1])
            self.entry_precio_producto.delete(0, tk.END); self.entry_precio_producto.insert(0, item[2])
            self.entry_stock_producto.delete(0, tk.END); self.entry_stock_producto.insert(0, item[3])
            self.ruta_imagen_producto = item[4]
            self.mostrar_imagen_producto(self.ruta_imagen_producto)

    def mostrar_imagen_producto(self, ruta_imagen):
        self.canvas_imagen.delete("all")
        if ruta_imagen and os.path.exists(ruta_imagen):
            img = Image.open(ruta_imagen)
            img.thumbnail((150, 150))
            self.img_tk = ImageTk.PhotoImage(img)
            self.canvas_imagen.create_image(75, 75, image=self.img_tk)

    def actualizar_producto_bd(self):
        try:
            from modelos.producto import Producto
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

            # Lógica para determinar qué imagen guardar
            ruta_imagen_existente = self.tree_productos.item(seleccion[0])['values'][4]
            imagen_a_guardar = self.ruta_imagen_producto if self.ruta_imagen_producto != ruta_imagen_existente else ruta_imagen_existente

            if Producto.actualizar(producto_id, nombre, precio, stock, imagen_a_guardar):
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                self.limpiar_campos_producto()
                self.cargar_productos_desde_bd()
                # self.ruta_imagen_producto se limpia en limpiar_campos_producto()
                self.cargar_productos_combo()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el producto")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el producto: {e}")

    def eliminar_producto_bd(self):
        try:
            from modelos.producto import Producto
            seleccion = self.tree_productos.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
                return
            producto_id = self.tree_productos.item(seleccion[0])['values'][0]
            respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este producto?")
            if respuesta:
                if Producto.eliminar(producto_id):
                    messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                    self.limpiar_campos_producto()
                    self.cargar_productos_desde_bd()
                    self.cargar_productos_combo()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el producto")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")

    def limpiar_campos_producto(self):
        self.entry_nombre_producto.delete(0, tk.END)
        self.entry_precio_producto.delete(0, tk.END)
        self.entry_stock_producto.delete(0, tk.END)
        self.canvas_imagen.delete("all")
        self.ruta_imagen_producto = None
        self.tree_productos.selection_remove(self.tree_productos.selection())

    def seleccionar_imagen_producto(self):
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar imagen de producto",
            filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.gif")]
        )
        if ruta_archivo:
            nombre_archivo = os.path.basename(ruta_archivo)
            ruta_destino = os.path.join("imagenes_productos", nombre_archivo)
            shutil.copy(ruta_archivo, ruta_destino)
            self.ruta_imagen_producto = ruta_destino
            self.mostrar_imagen_producto(self.ruta_imagen_producto)

    def exportar_productos_excel(self):
        try:
            from modelos.producto import Producto
            productos = Producto.obtener_todos()
            if not productos:
                messagebox.showinfo("Información", "No hay productos para exportar.")
                return
            datos = [{'ID': p.producto_id, 'Nombre': p.nombre, 'Precio': p.precio, 'Stock': p.stock} for p in productos]
            df = pd.DataFrame(datos)
            df.to_excel("reporte_productos.xlsx", index=False, engine='openpyxl')
            messagebox.showinfo("Éxito", "Reporte de productos exportado a 'reporte_productos.xlsx'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")

    # ========== MÉTODOS PARA CATEGORÍAS ==========

    def configurar_pestaña_categorias(self):
        frame = ttk.Frame(self.frame_categorias)

        frame.pack(fill='both', expand=True, padx=10, pady=10)
        frame_form = ttk.LabelFrame(frame, text="Registrar Categoría", style='Dark.TLabelframe')
        frame_form.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_nombre_categoria = ttk.Entry(frame_form, width=30)
        self.entry_nombre_categoria.grid(row=0, column=1, padx=5, pady=5)

        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(frame_botones, text="Guardar Categoría", command=self.guardar_categoria_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Actualizar Categoría", command=self.actualizar_categoria_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar Categoría", command=self.eliminar_categoria_bd).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Limpiar Campo", command=self.limpiar_campos_categoria).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Exportar a Excel", command=self.exportar_categorias_excel).pack(side='left', padx=5)

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
        try:
            from modelos.categoria import Categoria
            for item in self.tree_categorias.get_children():
                self.tree_categorias.delete(item)
            categorias = Categoria.obtener_todos()
            for categoria in categorias:
                self.tree_categorias.insert('', 'end', values=(categoria.categoria_id, categoria.nombre))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las categorías: {e}")

    def guardar_categoria_bd(self):
        try:
            from modelos.categoria import Categoria
            nombre = self.entry_nombre_categoria.get()
            if not nombre:
                messagebox.showwarning("Advertencia", "El nombre es obligatorio")
                return
            if Categoria.insertar(nombre):
                messagebox.showinfo("Éxito", "Categoría guardada correctamente")
                self.limpiar_campos_categoria()
                self.cargar_categorias_desde_bd()
            else:
                messagebox.showerror("Error", "No se pudo guardar la categoría")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la categoría: {e}")
            
    def seleccionar_categoria_bd(self, event):
        seleccion = self.tree_categorias.selection()
        if seleccion:
            item = self.tree_categorias.item(seleccion[0])['values']
            self.entry_nombre_categoria.delete(0, tk.END)
            self.entry_nombre_categoria.insert(0, item[1])

    def actualizar_categoria_bd(self):
        try:
            from modelos.categoria import Categoria
            seleccion = self.tree_categorias.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione una categoría para actualizar")
                return
            categoria_id = self.tree_categorias.item(seleccion[0])['values'][0]
            nombre = self.entry_nombre_categoria.get()
            if not nombre:
                messagebox.showwarning("Advertencia", "El nombre es obligatorio")
                return
            if Categoria.actualizar(categoria_id, nombre):
                messagebox.showinfo("Éxito", "Categoría actualizada correctamente")
                self.limpiar_campos_categoria()
                self.cargar_categorias_desde_bd()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la categoría")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la categoría: {e}")

    def eliminar_categoria_bd(self):
        try:
            from modelos.categoria import Categoria
            seleccion = self.tree_categorias.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione una categoría para eliminar")
                return
            categoria_id = self.tree_categorias.item(seleccion[0])['values'][0]
            respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta categoría?")
            if respuesta:
                if Categoria.eliminar(categoria_id):
                    messagebox.showinfo("Éxito", "Categoría eliminada correctamente")
                    self.limpiar_campos_categoria()
                    self.cargar_categorias_desde_bd()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la categoría")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la categoría: {e}")

    def limpiar_campos_categoria(self):
        self.entry_nombre_categoria.delete(0, tk.END)
        self.tree_categorias.selection_remove(self.tree_categorias.selection())

    def exportar_categorias_excel(self):
        try:
            from modelos.categoria import Categoria
            categorias = Categoria.obtener_todos()
            if not categorias:
                messagebox.showinfo("Información", "No hay categorías para exportar.")
                return
            datos = [{'ID': c.categoria_id, 'Nombre': c.nombre} for c in categorias]
            df = pd.DataFrame(datos)
            df.to_excel("reporte_categorias.xlsx", index=False, engine='openpyxl')
            messagebox.showinfo("Éxito", "Reporte de categorías exportado a 'reporte_categorias.xlsx'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")

    # ========== MÉTODOS PARA VENTAS ==========

    def configurar_pestaña_ventas(self):

        frame_principal = ttk.Frame(self.frame_ventas)
        frame_principal.pack(fill='both', expand=True, padx=10, pady=10)
        frame_izquierdo = ttk.LabelFrame(frame_principal, text="Seleccionar Productos", style='Dark.TLabelframe')
        frame_izquierdo.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        frame_derecho = ttk.LabelFrame(frame_principal, text="Carrito de Compra", style='Dark.TLabelframe')
        frame_derecho.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        ttk.Label(frame_izquierdo, text="Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.combo_cliente = ttk.Combobox(frame_izquierdo, width=30)
        self.combo_cliente.grid(row=0, column=1, padx=5, pady=5)
        self.cargar_clientes_combo()

        ttk.Label(frame_izquierdo, text="Producto:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.combo_producto = ttk.Combobox(frame_izquierdo, width=30)
        self.combo_producto.grid(row=1, column=1, padx=5, pady=5)
        self.combo_producto.bind('<<ComboboxSelected>>', self.actualizar_info_producto)
        self.cargar_productos_combo()

        self.frame_info_producto = ttk.LabelFrame(frame_izquierdo, text="Información del Producto")
        self.frame_info_producto.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='we')

        ttk.Label(self.frame_info_producto, text="Precio:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.label_precio = ttk.Label(self.frame_info_producto, text="$0.00")
        self.label_precio.grid(row=0, column=1, padx=5, pady=2, sticky='w')

        ttk.Label(self.frame_info_producto, text="Stock:").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.label_stock = ttk.Label(self.frame_info_producto, text="0")
        self.label_stock.grid(row=1, column=1, padx=5, pady=2, sticky='w')

        ttk.Label(frame_izquierdo, text="Cantidad:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.spin_cantidad = tk.Spinbox(frame_izquierdo, from_=1, to=100, width=10)
        self.spin_cantidad.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        ttk.Button(frame_izquierdo, text="Agregar al Carrito", command=self.agregar_al_carrito).grid(row=4, column=0, columnspan=2, pady=10)
        self.tree_carrito = ttk.Treeview(frame_derecho, columns=('Producto', 'Cantidad', 'Precio', 'Subtotal'), show='headings', style='Dark.Treeview')

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

        frame_total = ttk.Frame(frame_derecho)
        frame_total.pack(fill='x', pady=10)

        ttk.Label(frame_total, text="TOTAL:", font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        self.label_total = ttk.Label(frame_total, text="$0.00", font=('Arial', 12, 'bold'))
        self.label_total.pack(side='left', padx=5)

        frame_botones_carrito = ttk.Frame(frame_derecho)
        frame_botones_carrito.pack(side='right', fill='y', padx=10, pady=10)

        ttk.Button(frame_botones_carrito, text="Quitar Producto", command=self.quitar_del_carrito, width=20).pack(pady=5)
        ttk.Button(frame_botones_carrito, text="Limpiar Carrito", command=self.limpiar_carrito, width=20).pack(pady=5)
        ttk.Button(frame_botones_carrito, text="Realizar Venta", command=self.realizar_venta, style='Accent.TButton', width=20).pack(pady=5)

    def configurar_pestaña_detalle_ventas(self):
        frame_principal = ttk.Frame(self.frame_detalle_ventas)

        frame_principal.pack(fill='both', expand=True, padx=10, pady=10)
        frame_filtros = ttk.LabelFrame(frame_principal, text="Filtros")
        frame_filtros.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame_filtros, text="Fecha desde:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_fecha_desde = DateEntry(frame_filtros, width=12, date_pattern='y-mm-dd',
                                           background='#003366', foreground='white', borderwidth=2)
        self.entry_fecha_desde.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_filtros, text="Fecha hasta:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_fecha_hasta = DateEntry(frame_filtros, width=12, date_pattern='y-mm-dd',
                                           background='#003366', foreground='white', borderwidth=2)
        self.entry_fecha_hasta.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(frame_filtros, text="Buscar", command=self.cargar_ventas).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(frame_filtros, text="Exportar a Excel", command=self.exportar_ventas_excel).grid(row=0, column=5, padx=5, pady=5)
        frame_tree = ttk.LabelFrame(frame_principal, text="Ventas Realizadas", style='Dark.TLabelframe')
        frame_tree.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree_ventas = ttk.Treeview(frame_tree, columns=('ID', 'Fecha', 'Cliente', 'Total'), show='headings', style='Dark.Treeview')
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
        self.tree_ventas.bind('<<TreeviewSelect>>', self.mostrar_detalle_venta)

        frame_detalle = ttk.LabelFrame(frame_principal, text="Detalle de Venta", style='Dark.TLabelframe')
        frame_detalle.pack(fill='x', padx=5, pady=5)

        self.tree_detalle_venta = ttk.Treeview(frame_detalle, columns=('Producto', 'Cantidad', 'Precio', 'Subtotal'), show='headings', style='Dark.Treeview')
        self.tree_detalle_venta.heading('Producto', text='Producto')
        self.tree_detalle_venta.heading('Cantidad', text='Cantidad')
        self.tree_detalle_venta.heading('Precio', text='Precio Unit.')
        self.tree_detalle_venta.heading('Subtotal', text='Subtotal')

        for col in ('Producto', 'Cantidad', 'Precio', 'Subtotal'):
            self.tree_detalle_venta.column(col, width=120)
        self.tree_detalle_venta.pack(fill='x')
        self.cargar_ventas()

    def cargar_clientes_combo(self):
        try:
            from modelos.cliente import Cliente
            clientes = Cliente.obtener_todos()
            self.combo_cliente['values'] = [f"{c.cliente_id} - {c.nombre}" for c in clientes]
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los clientes: {e}")

    def cargar_productos_combo(self):
        try:
            from modelos.producto import Producto
            productos = [p for p in Producto.obtener_todos() if p.stock > 0]
            self.productos_disponibles = {f"{p.producto_id} - {p.nombre}": (p.producto_id, p.nombre, p.precio, p.stock) for p in productos}
            self.combo_producto['values'] = list(self.productos_disponibles.keys())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los productos: {e}")

    def actualizar_info_producto(self, event=None):
        seleccion = self.combo_producto.get()
        if seleccion in self.productos_disponibles:
            info = self.productos_disponibles[seleccion]
            self.label_precio.config(text=f"${info[2]:.2f}")
            self.label_stock.config(text=str(info[3]))

    def agregar_al_carrito(self):
        seleccion = self.combo_producto.get()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        info = self.productos_disponibles[seleccion]
        producto_id, nombre, precio, stock = info
        cantidad = int(self.spin_cantidad.get())

        if cantidad > stock:
            messagebox.showwarning("Stock Insuficiente", f"Solo hay {stock} unidades disponibles.")
            return

        # Verificar si el producto ya está en el carrito para actualizar la cantidad
        for item in self.carrito:
            if item['producto_id'] == producto_id:
                item['cantidad'] += cantidad
                self.actualizar_carrito()
                return

        self.carrito.append({'producto_id': producto_id, 'nombre': nombre, 'cantidad': cantidad, 'precio': precio})
        self.actualizar_carrito()

    def actualizar_carrito(self):
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        
        self.total_venta = 0
        for item in self.carrito:
            subtotal = item['cantidad'] * item['precio']
            self.tree_carrito.insert('', 'end', values=(item['nombre'], item['cantidad'], f"${item['precio']:.2f}", f"${subtotal:.2f}"))
            self.total_venta += subtotal
        
        self.label_total.config(text=f"${self.total_venta:.2f}")

    def quitar_del_carrito(self):
        seleccion = self.tree_carrito.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto del carrito para quitar.")
            return
        
        item_seleccionado = self.tree_carrito.item(seleccion[0])['values'][0]
        self.carrito = [item for item in self.carrito if item['nombre'] != item_seleccionado]
        self.actualizar_carrito()

    def limpiar_carrito(self):
        self.carrito = []
        self.actualizar_carrito()

    def realizar_venta(self):
        try:
            from modelos.venta import Venta
            from modelos.detalle_venta import DetalleVenta
            if not self.carrito:
                messagebox.showwarning("Advertencia", "El carrito está vacío")
                return
            if not self.combo_cliente.get():
                messagebox.showwarning("Advertencia", "Seleccione un cliente")
                return
            
            cliente_id = int(self.combo_cliente.get().split(' - ')[0])
            if Venta.insertar(cliente_id, self.total_venta):
                venta_id = Venta.obtener_ultima_id()
                for item in self.carrito:
                    DetalleVenta.insertar(venta_id, item['producto_id'], item['cantidad'], item['precio'])
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
        try:
            from modelos.venta import Venta
            for item in self.tree_ventas.get_children():
                self.tree_ventas.delete(item)
            fecha_desde = self.entry_fecha_desde.get()
            fecha_hasta = self.entry_fecha_hasta.get()
            ventas = Venta.obtener_todas(fecha_desde, fecha_hasta)
            for venta in ventas:
                self.tree_ventas.insert('', 'end', values=venta)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las ventas: {e}")

    def exportar_ventas_excel(self):
        try:
            fecha_desde = self.entry_fecha_desde.get()
            fecha_hasta = self.entry_fecha_hasta.get()
            from modelos.venta import Venta
            ventas = Venta.obtener_todas(fecha_desde, fecha_hasta)
            if not ventas:
                messagebox.showinfo("Información", "No hay ventas en el rango de fechas seleccionado.")
                return
            df = pd.DataFrame(ventas, columns=['ID Venta', 'Fecha', 'Cliente', 'Total'])
            df.to_excel("reporte_ventas.xlsx", index=False, engine='openpyxl')
            messagebox.showinfo("Éxito", "Reporte de ventas exportado a 'reporte_ventas.xlsx'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")

    def mostrar_detalle_venta(self, event):
        try:
            from modelos.detalle_venta import DetalleVenta
            seleccion = self.tree_ventas.selection()
            if not seleccion:
                return
            venta_id = self.tree_ventas.item(seleccion[0])['values'][0]
            for item in self.tree_detalle_venta.get_children():
                self.tree_detalle_venta.delete(item)
            detalles = DetalleVenta.obtener_por_venta(venta_id)
            for detalle in detalles:
                self.tree_detalle_venta.insert('', 'end', values=detalle)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el detalle: {e}")
            
    def __del__(self):
        # ...existing code...
        pass
