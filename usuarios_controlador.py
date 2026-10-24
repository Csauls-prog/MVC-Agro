import re
from controladores import sesion
from modelos import usuario_modelo


def _es_admin():
    return sesion.usuario_actual is not None and sesion.usuario_actual["rol"] == "ADMIN"


def listar(estado=None):
    if not _es_admin():
        return []
    return usuario_modelo.listar_usuarios(estado)


def agregar(usuario, password, confirmar, rol):
    if not _es_admin():
        return False, "No tiene permisos para esta acción."
    usuario = usuario.strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,50}", usuario):
        return False, "Usuario: de 3 a 50 caracteres (letras, números, _ . -)."
    if len(password) < 8 or len(password.encode("utf-8")) > 72:
        return False, "La contraseña debe tener entre 8 y 72 caracteres."
    if password != confirmar:
        return False, "Las contraseñas no coinciden."
    if rol not in ("ADMIN", "VENDEDOR"):
        return False, "Rol no válido."
    if usuario_modelo.existe_usuario(usuario):
        return False, "Ese usuario ya existe."
    if usuario_modelo.crear_usuario(usuario, password, rol):
        return True, "Usuario creado correctamente."
    return False, "No se pudo crear el usuario."


def cambiar_estado(id_usuario, nombre, nuevo_estado):
    if not _es_admin():
        return False, "No tiene permisos para esta acción."
    if nuevo_estado not in ("ACTIVO", "INACTIVO"):
        return False, "Estado no válido."
    if nombre == sesion.usuario_actual["usuario"] and nuevo_estado == "INACTIVO":
        return False, "No puede dar de baja su propio usuario."
    if usuario_modelo.cambiar_estado(id_usuario, nuevo_estado):
        return True, f"El usuario {nombre} ahora está {nuevo_estado}."
    return False, "No se pudo actualizar el usuario."