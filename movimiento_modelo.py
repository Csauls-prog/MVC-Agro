from mysql.connector import Error
from modelos.conexion import obtener_conexion


def stock_total(codigo):
    conexion = obtener_conexion()
    if conexion is None:
        return 0
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT COALESCE(SUM(cantidad), 0) FROM inventario "
                       "WHERE codigo_producto = %s", (codigo,))
        return int(cursor.fetchone()[0])
    except Error as e:
        print(f"Error al consultar existencias: {e}")
        return 0
    finally:
        conexion.close()


def registrar_salida(codigo, cantidad, motivo, usuario):
    """Descuenta del lote que vence primero (FEFO). Todo en una transacción.
    Devuelve (ok, mensaje)."""
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No se pudo conectar a la base de datos."
    try:
        cursor = conexion.cursor()
        # FOR UPDATE bloquea esos lotes mientras dura la transacción.
        cursor.execute(
            "SELECT id_inventario, cantidad FROM inventario "
            "WHERE codigo_producto = %s AND cantidad > 0 "
            "ORDER BY fecha_vencimiento IS NULL, fecha_vencimiento, fecha, id_inventario "
            "FOR UPDATE", (codigo,))
        lotes = cursor.fetchall()
        disponible = sum(cant for _, cant in lotes)
        if cantidad > disponible:
            conexion.rollback()
            return False, f"Existencias insuficientes: hay {disponible} disponible(s)."
        pendiente = cantidad
        for id_inventario, cant in lotes:
            if pendiente == 0:
                break
            tomar = min(cant, pendiente)
            cursor.execute("UPDATE inventario SET cantidad = cantidad - %s "
                           "WHERE id_inventario = %s", (tomar, id_inventario))
            pendiente -= tomar
        cursor.execute("DELETE FROM inventario WHERE codigo_producto = %s AND cantidad = 0",
                       (codigo,))
        cursor.execute(
            "INSERT INTO movimientos (codigo_producto, tipo, cantidad, motivo, usuario) "
            "VALUES (%s, 'SALIDA', %s, %s, %s)", (codigo, cantidad, motivo, usuario))
        conexion.commit()
        return True, "Salida registrada."
    except Error as e:
        conexion.rollback()
        print(f"Error al registrar la salida: {e}")
        return False, "No se pudo registrar la salida."
    finally:
        conexion.close()