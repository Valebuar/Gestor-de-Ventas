import mysql.connector
from mysql.connector import Error
from tkinter import messagebox

# Configuración de conexión
DATABASE_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "admonventas"
}

# Clase de conexión a la base de datos
class DatabaseConnection:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = ""
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=3306,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            return True
        except Error as e:
            messagebox.showerror("Error de Conexión", f"Error al conectar con la base de datos: {e}")
            return False

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        try:
            if self.connection is None or not self.connection.is_connected():
                if not self.connect():
                    return False
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return True
        except Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al ejecutar consulta: {e}")
            return False

    def fetch_all(self, query, params=None):
        try:
            if self.connection is None or not self.connection.is_connected():
                if not self.connect():
                    return []
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al obtener datos: {e}")
            return []

    def create_tables(self):
        """Crear las tablas si no existen"""
        tablas = [
            '''CREATE TABLE IF NOT EXISTS Clientes (
                cliente_id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                telefono VARCHAR(15),
                direccion VARCHAR(150)
            )''',
            '''CREATE TABLE IF NOT EXISTS Productos (
                producto_id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                precio DECIMAL(10,2) NOT NULL,
                stock INT NOT NULL
            )''',
            '''CREATE TABLE IF NOT EXISTS Categorias (
                categoria_id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL,
                descripcion TEXT
            )''',
            '''CREATE TABLE IF NOT EXISTS Ventas (
                venta_id INT AUTO_INCREMENT PRIMARY KEY,
                cliente_id INT,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                total DECIMAL(10,2),
                FOREIGN KEY (cliente_id) REFERENCES Clientes(cliente_id)
            )''',
            '''CREATE TABLE IF NOT EXISTS DetalleVentas (
                detalle_id INT AUTO_INCREMENT PRIMARY KEY,
                venta_id INT,
                producto_id INT,
                cantidad INT NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES Ventas(venta_id),
                FOREIGN KEY (producto_id) REFERENCES Productos(producto_id)
            )'''
        ]
        if self.connection is None or not self.connection.is_connected():
            if not self.connect():
                return False
        for query in tablas:
            try:
                self.cursor.execute(query)
            except Error as e:
                messagebox.showerror("Error de Base de Datos", f"Error al crear tabla: {e}")
                return False
        self.connection.commit()
        return True

if __name__ == "__main__":
    db = DatabaseConnection(
        host=DATABASE_CONFIG["host"],
        user=DATABASE_CONFIG["user"],
        password=DATABASE_CONFIG["password"],
        database=DATABASE_CONFIG["database"]
    )
    if db.connect():
        if db.create_tables():
            print("Base de datos y tablas creadas correctamente.")
        else:
            print("Error al crear las tablas.")
        db.disconnect()
    else:
        print("No se pudo conectar a la base de datos.")
