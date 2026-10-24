from mysql.connector import Error
from modelos.conexion import obtener_conexion



def buscar(codigo=None, descripcion=None, fecha=None):
    """Devuelve la lista de registros, o None si hubo un error de base de datos."""
    sql = ("SELECT p.codigo, i.fecha, p.descripcion, i.cantidad, p.presentacion, "
           "p.unidad_medida, p.precio, i.fecha_vencimiento "
           "FROM inventario i JOIN productos p ON p.codigo = i.codigo_producto")
    condiciones = []
    parametros = []
    if codigo:
        condiciones.append("p.codigo = %s")
        parametros.append(codigo)
    if descripcion:
        # Se escapan % y _ para que se busquen como texto y no como comodines.
        texto = descripcion.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        condiciones.append("p.descripcion LIKE %s")
        parametros.append(f"%{texto}%")
    if fecha:
        condiciones.append("i.fecha = %s")
        parametros.append(fecha)
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
    sql += " ORDER BY i.fecha DESC, p.codigo"

    conexion = obtener_conexion()
    if conexion is None:
        return None
    try:
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        return cursor.fetchall()
    except Error as e:
        print(f"Error al consultar el inventario: {e}")
        return None
    finally:
        conexion.close()