from conexion.BasededatosAdmonventasBD import DatabaseConnection, DATABASE_CONFIG

db = DatabaseConnection(**DATABASE_CONFIG)

class Producto:
    def __init__(self, producto_id, nombre, descripcion, precio, stock, imagen=None):
        self.producto_id = producto_id
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.stock = stock
        self.imagen = imagen

    @staticmethod
    def obtener_todos():
        try:
            productos = db.fetch_all("SELECT producto_id, nombre, descripcion, precio, stock, imagen FROM Productos")
            return [Producto(*p) for p in productos]
        except Exception as e:
            return []

    @staticmethod
    def insertar(nombre, precio, stock, imagen=None, descripcion=''):
        query = "INSERT INTO Productos (nombre, descripcion, precio, stock, imagen) VALUES (%s, %s, %s, %s, %s)"
        return db.execute_query(query, (nombre, descripcion, float(precio), int(stock), imagen))

    @staticmethod
    def actualizar(producto_id, nombre, precio, stock, imagen=None, descripcion=''):
        query = "UPDATE Productos SET nombre=%s, descripcion=%s, precio=%s, stock=%s, imagen=%s WHERE producto_id=%s"
        return db.execute_query(query, (nombre, descripcion, float(precio), int(stock), imagen, producto_id))

    @staticmethod
    def eliminar(producto_id):
        query = "DELETE FROM Productos WHERE producto_id=%s"
        return db.execute_query(query, (producto_id,))
