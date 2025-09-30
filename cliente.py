from conexion.BasededatosAdmonventasBD import DatabaseConnection, DATABASE_CONFIG

db = DatabaseConnection(**DATABASE_CONFIG)

class Cliente:
    def __init__(self, cliente_id, nombre, correo, telefono):
        self.cliente_id = cliente_id
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @staticmethod
    def obtener_todos():
        try:
            clientes = db.fetch_all("SELECT * FROM Clientes")
            return [Cliente(*c) for c in clientes]
        except Exception as e:
            return []

    @staticmethod
    def insertar(nombre, correo, telefono):
        query = "INSERT INTO Clientes (nombre, correo, telefono) VALUES (%s, %s, %s)"
        return db.execute_query(query, (nombre, correo, telefono))

    @staticmethod
    def actualizar(cliente_id, nombre, correo, telefono):
        query = "UPDATE Clientes SET nombre=%s, correo=%s, telefono=%s WHERE cliente_id=%s"
        return db.execute_query(query, (nombre, correo, telefono, cliente_id))

    @staticmethod
    def eliminar(cliente_id):
        query = "DELETE FROM Clientes WHERE cliente_id=%s"
        return db.execute_query(query, (cliente_id,))
