from mysql.connector import Error
from modelos.conexion import obtener_conexion

# Constante fija del programa (nunca viene del usuario), por eso es seguro en el SQL.
COLUMNAS = ("codigo, descripcion, unidad_medida, presentacion, "
            "precio, estado, fecha_registro, stock_minimo")


def _leer(sql, parametros=(), uno=False):
    conexion = obtener_conexion()
    if conexion is None:
        return None if uno else []
    try:
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        return cursor.fetchone() if uno else cursor.fetchall()
    except Error as e:
        print(f"Error de lectura: {e}")
        return None if uno else []
    finally:
        conexion.close()


def _escribir(sql, parametros):
    conexion = obtener_conexion()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        conexion.commit()
        return True
    except Error as e:
        print(f"Error de escritura: {e}")
        return False
    finally:
        conexion.close()


def existe(codigo):
    return _leer("SELECT 1 FROM productos WHERE codigo = %s", (codigo,), uno=True) is not None


def obtener(codigo):
    return _leer(f"SELECT {COLUMNAS} FROM productos WHERE codigo = %s", (codigo,), uno=True)


def listar():
    """Productos con su cantidad total (suma de todos sus ingresos en inventario)."""
    return _leer(
        "SELECT p.codigo, p.descripcion, p.unidad_medida, p.presentacion, p.precio, "
        "p.estado, p.fecha_registro, p.stock_minimo, COALESCE(SUM(i.cantidad), 0) "
        "FROM productos p LEFT JOIN inventario i ON i.codigo_producto = p.codigo "
        "GROUP BY p.codigo, p.descripcion, p.unidad_medida, p.presentacion, p.precio, "
        "p.estado, p.fecha_registro, p.stock_minimo ORDER BY p.codigo")


def agregar_con_existencias(datos, cantidad, fecha, vencimiento, usuario):
    """Guarda el producto, su primer ingreso y el movimiento en UNA transacción."""
    conexion = obtener_conexion()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute(
            f"INSERT INTO productos ({COLUMNAS}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            datos)
        if cantidad > 0:
            cursor.execute(
                "INSERT INTO inventario (codigo_producto, cantidad, fecha, fecha_vencimiento) "
                "VALUES (%s, %s, %s, %s)", (datos[0], cantidad, fecha, vencimiento))
            cursor.execute(
                "INSERT INTO movimientos (codigo_producto, tipo, cantidad, motivo, usuario) "
                "VALUES (%s, 'ENTRADA', %s, 'Ingreso inicial', %s)",
                (datos[0], cantidad, usuario))
        conexion.commit()
        return True
    except Error as e:
        conexion.rollback()
        print(f"Error al agregar producto: {e}")
        return False
    finally:
        conexion.close()


def registrar_ingreso(codigo, cantidad, fecha, vencimiento, usuario):
    conexion = obtener_conexion()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO inventario (codigo_producto, cantidad, fecha, fecha_vencimiento) "
            "VALUES (%s, %s, %s, %s)", (codigo, cantidad, fecha, vencimiento))
        cursor.execute(
            "INSERT INTO movimientos (codigo_producto, tipo, cantidad, motivo, usuario) "
            "VALUES (%s, 'ENTRADA', %s, 'Ingreso de mercadería', %s)",
            (codigo, cantidad, usuario))
        conexion.commit()
        return True
    except Error as e:
        conexion.rollback()
        print(f"Error al registrar el ingreso: {e}")
        return False
    finally:
        conexion.close()

def actualizar(datos):
    codigo, descripcion, unidad, presentacion, precio, estado, fecha, stock = datos
    return _escribir(
        "UPDATE productos SET descripcion = %s, unidad_medida = %s, presentacion = %s, "
        "precio = %s, estado = %s, fecha_registro = %s, stock_minimo = %s WHERE codigo = %s",
        (descripcion, unidad, presentacion, precio, estado, fecha, stock, codigo))


def cambiar_estado(codigo, estado):
    return _escribir("UPDATE productos SET estado = %s WHERE codigo = %s", (estado, codigo))