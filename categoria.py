from conexion.BasededatosAdmonventasBD import DatabaseConnection, DATABASE_CONFIG

db = DatabaseConnection(**DATABASE_CONFIG)

class Categoria:
    def __init__(self, categoria_id, nombre):
        self.categoria_id = categoria_id
        self.nombre = nombre

    @staticmethod
    def obtener_todos():
        try:
            categorias = db.fetch_all("SELECT * FROM Categorias")
            return [Categoria(*c) for c in categorias]
        except Exception as e:
            return []

    @staticmethod
    def insertar(nombre):
        query = "INSERT INTO Categorias (nombre) VALUES (%s)"
        return db.execute_query(query, (nombre,))

    @staticmethod
    def actualizar(categoria_id, nombre):
        query = "UPDATE Categorias SET nombre=%s WHERE categoria_id=%s"
        return db.execute_query(query, (nombre, categoria_id))

    @staticmethod
    def eliminar(categoria_id):
        query = "DELETE FROM Categorias WHERE categoria_id=%s"
        return db.execute_query(query, (categoria_id,))
