from mysql.connector import Error
from modelos.conexion import obtener_conexion


def _consultar(sql, parametros=()):
    conexion = obtener_conexion()
    if conexion is None:
        return []
    try:
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        return cursor.fetchall()
    except Error as e:
        print(f"Error al consultar el panel: {e}")
        return []
    finally:
        conexion.close()


def productos_activos():
    filas = _consultar("SELECT COUNT(*) FROM productos WHERE estado = 'ACTIVO'")
    return int(filas[0][0]) if filas else 0


def valor_inventario():
    filas = _consultar(
        "SELECT COALESCE(SUM(i.cantidad * p.precio), 0) "
        "FROM inventario i JOIN productos p ON p.codigo = i.codigo_producto")
    return filas[0][0] if filas else 0


def valor_por_producto(limite=7):
    return _consultar(
        "SELECT p.descripcion, SUM(i.cantidad * p.precio) AS valor "
        "FROM inventario i JOIN productos p ON p.codigo = i.codigo_producto "
        "GROUP BY p.codigo, p.descripcion ORDER BY valor DESC LIMIT %s", (limite,))


def lotes_por_vencer(dias):
    """Lotes que vencen dentro de 'dias' días o que ya vencieron."""
    return _consultar(
        "SELECT p.codigo, p.descripcion, i.fecha_vencimiento, i.cantidad "
        "FROM inventario i JOIN productos p ON p.codigo = i.codigo_producto "
        "WHERE i.fecha_vencimiento IS NOT NULL "
        "AND i.fecha_vencimiento <= DATE_ADD(CURDATE(), INTERVAL %s DAY) "
        "ORDER BY i.fecha_vencimiento", (dias,))


def bajo_stock_minimo():
    return _consultar(
        "SELECT p.codigo, p.descripcion, COALESCE(SUM(i.cantidad), 0), p.stock_minimo "
        "FROM productos p LEFT JOIN inventario i ON i.codigo_producto = p.codigo "
        "WHERE p.estado = 'ACTIVO' "
        "GROUP BY p.codigo, p.descripcion, p.stock_minimo "
        "HAVING COALESCE(SUM(i.cantidad), 0) < p.stock_minimo ORDER BY p.codigo")