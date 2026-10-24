import re
from controladores import sesion
from modelos import movimiento_modelo, producto_modelo

MOTIVOS_SALIDA = ["Venta", "Uso en campo", "Merma", "Producto vencido", "Otro"]


def stock_actual(codigo):
    return movimiento_modelo.stock_total(codigo.strip().upper())


def obtener_producto(codigo):
    if sesion.usuario_actual is None:
        return None
    return producto_modelo.obtener(codigo.strip().upper())


def registrar_salida(codigo, cantidad, motivo):
    if sesion.usuario_actual is None:
        return False, "Sesión no válida."
    codigo = codigo.strip().upper()
    if not codigo:
        return False, "Ingrese o seleccione el código del producto."
    cantidad = cantidad.strip()
    if not re.fullmatch(r"\d{1,6}", cantidad) or int(cantidad) <= 0:
        return False, "La cantidad debe ser un número entero mayor que 0."
    if motivo not in MOTIVOS_SALIDA:
        return False, "Seleccione un motivo válido."
    producto = producto_modelo.obtener(codigo)
    if producto is None:
        return False, "No existe un producto con ese código."
    ok, mensaje = movimiento_modelo.registrar_salida(
        codigo, int(cantidad), motivo, sesion.usuario_actual["usuario"])
    if ok:
        mensaje = f"Salida de {int(cantidad)} {producto[2].lower()} registrada para {codigo}."
    return ok, mensaje