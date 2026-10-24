import re
from datetime import date, datetime
from controladores import sesion
from modelos import inventario_modelo


def buscar(codigo, descripcion, fecha):
    """Devuelve (filas, mensaje). 'filas' es None si hubo un error."""
    if sesion.usuario_actual is None:
        return None, "Sesión no válida."
    codigo = codigo.strip().upper()
    descripcion = descripcion.strip()
    fecha = fecha.strip()
    if codigo and not re.fullmatch(r"[A-Z0-9-]{1,20}", codigo):
        return None, "Código no válido."
    if len(descripcion) > 150:
        return None, "La descripción es demasiado larga."
    fecha_d = None
    if fecha:
        try:
            fecha_d = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return None, "La fecha debe tener el formato AAAA-MM-DD."
    filas = inventario_modelo.buscar(codigo or None, descripcion or None, fecha_d)
    if filas is None:
        return None, "No se pudo consultar la base de datos."
    return filas, f"{len(filas)} registro(s) encontrado(s)."


def resumen(filas):
    """Devuelve (cantidad_total, valor_total) de los registros mostrados."""
    cantidad_total = sum(f[3] for f in filas)
    valor_total = sum(f[3] * f[6] for f in filas)
    return cantidad_total, valor_total


def estado_vencimiento(vencimiento, dias=60):
    """Devuelve 'vencido', 'proximo' o None según la fecha de vencimiento."""
    if vencimiento is None:
        return None
    hoy = date.today()
    if vencimiento < hoy:
        return "vencido"
    if (vencimiento - hoy).days <= dias:
        return "proximo"
    return None