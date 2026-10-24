usuario_actual = None  # {'usuario': ..., 'rol': ...}


def iniciar(datos):
    global usuario_actual
    usuario_actual = datos


def cerrar():
    global usuario_actual
    usuario_actual = None