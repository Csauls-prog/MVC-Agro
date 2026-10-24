import bcrypt
from mysql.connector import Error
from modelos.conexion import obtener_conexion


def crear_usuario(usuario, password, rol="VENDEDOR"):
    conexion = obtener_conexion()
    if conexion is None:
        return False
    hash_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO usuarios (usuario, password, rol) VALUES (%s, %s, %s)",
            (usuario, hash_pw.decode("utf-8"), rol),
        )
        conexion.commit()
        return True
    except Error as e:
        print(f"Error al crear usuario: {e}")
        return False
    finally:
        conexion.close()


def validar_credenciales(usuario, password):
    conexion = obtener_conexion()
    if conexion is None:
        return None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT password, rol FROM usuarios WHERE usuario = %s AND estado = 'ACTIVO'",
            (usuario,),
        )
        fila = cursor.fetchone()
        if fila and bcrypt.checkpw(password.encode("utf-8"), fila[0].encode("utf-8")):
            return {"usuario": usuario, "rol": fila[1]}
        return None
    except Error as e:
        print(f"Error al validar credenciales: {e}")
        return None
    finally:
        conexion.close()


def existe_usuario(usuario):
    conexion = obtener_conexion()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT 1 FROM usuarios WHERE usuario = %s", (usuario,))
        return cursor.fetchone() is not None
    except Error as e:
        print(f"Error al buscar usuario: {e}")
        return False
    finally:
        conexion.close()


def listar_usuarios(estado=None):
    conexion = obtener_conexion()
    if conexion is None:
        return []
    try:
        cursor = conexion.cursor()
        sql = "SELECT id_usuario, usuario, rol, estado FROM usuarios"
        parametros = ()
        if estado:
            sql += " WHERE estado = %s"
            parametros = (estado,)
        cursor.execute(sql + " ORDER BY id_usuario", parametros)
        return cursor.fetchall()
    except Error as e:
        print(f"Error al listar usuarios: {e}")
        return []
    finally:
        conexion.close()


def cambiar_estado(id_usuario, nuevo_estado):
    conexion = obtener_conexion()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE usuarios SET estado = %s WHERE id_usuario = %s",
                       (nuevo_estado, id_usuario))
        conexion.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error al cambiar estado: {e}")
        return False
    finally:
        conexion.close()