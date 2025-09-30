from conexion.BasededatosAdmonventasBD import DatabaseConnection, DATABASE_CONFIG

db = DatabaseConnection(**DATABASE_CONFIG)

class Venta:
    def __init__(self, venta_id, cliente_id, fecha, total):
        self.venta_id = venta_id
        self.cliente_id = cliente_id
        self.fecha = fecha
        self.total = total

    @staticmethod
    def obtener_todas(fecha_desde=None, fecha_hasta=None):
        try:
            query = """
            SELECT v.venta_id, v.fecha, c.nombre, v.total 
            FROM Ventas v 
            INNER JOIN Clientes c ON v.cliente_id = c.cliente_id 
            """
            params = ()
            if fecha_desde and fecha_hasta:
                query += " WHERE DATE(v.fecha) BETWEEN %s AND %s ORDER BY v.fecha DESC"
                params = (fecha_desde, fecha_hasta)
            ventas = db.fetch_all(query, params)
            return ventas
        except Exception as e:
            return []

    @staticmethod
    def insertar(cliente_id, total):
        query = "INSERT INTO Ventas (cliente_id, total) VALUES (%s, %s)"
        return db.execute_query(query, (cliente_id, total))

    @staticmethod
    def obtener_ultima_id():
        query = "SELECT MAX(venta_id) FROM Ventas"
        result = db.fetch_all(query)
        return result[0][0] if result else None
