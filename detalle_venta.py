from conexion.BasededatosAdmonventasBD import DatabaseConnection, DATABASE_CONFIG

db = DatabaseConnection(**DATABASE_CONFIG)

class DetalleVenta:
    def __init__(self, detalle_id, venta_id, producto_id, cantidad, precio_unitario):
        self.detalle_id = detalle_id
        self.venta_id = venta_id
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario

    @staticmethod
    def insertar(venta_id, producto_id, cantidad, precio_unitario):
        query = "INSERT INTO DetalleVentas (venta_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)"
        return db.execute_query(query, (venta_id, producto_id, cantidad, precio_unitario))

    @staticmethod
    def obtener_por_venta(venta_id):
        query = """
        SELECT p.nombre, dv.cantidad, dv.precio_unitario, (dv.cantidad * dv.precio_unitario) as subtotal
        FROM DetalleVentas dv
        INNER JOIN Productos p ON dv.producto_id = p.producto_id
        WHERE dv.venta_id = %s
        """
        return db.fetch_all(query, (venta_id,))
