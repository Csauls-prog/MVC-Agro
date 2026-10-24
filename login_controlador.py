from modelos.usuario_modelo import validar_credenciales
from controladores import sesion


def iniciar_sesion(usuario, password):
    usuario = usuario.strip()
    if not usuario or not password:
        return False, "Ingrese usuario y contraseña."
    if len(usuario) > 50 or len(password.encode("utf-8")) > 72:
        return False, "Los datos ingresados no son válidos."
    datos = validar_credenciales(usuario, password)
    if datos is None:
        return False, "Usuario o contraseña incorrectos."
    sesion.iniciar(datos)
    return True, "Acceso concedido."