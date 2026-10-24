import re
from datetime import date, datetime
from decimal import Decimal
from controladores import sesion
from modelos import producto_modelo

UNIDADES = ["Libras", "Gramos", "Onzas", "Litros", "Unidades"]
PRESENTACIONES = ["Bolsa", "Sobre", "Frasco", "Galón", "Caja"]
ESTADOS = ["ACTIVO", "INACTIVO"]


def _hay_sesion():
    return sesion.usuario_actual is not None


def _es_admin():
    return _hay_sesion() and sesion.usuario_actual["rol"] == "ADMIN"


def _validar(codigo, descripcion, unidad, presentacion, precio, estado, fecha, stock):
    """Devuelve (datos, None) si todo es válido, o (None, mensaje_de_error)."""
    codigo = codigo.strip().upper()
    descripcion = descripcion.strip()
    if not re.fullmatch(r"[A-Z0-9-]{1,20}", codigo):
        return None, "Código: hasta 20 caracteres (letras, números y guion)."
    if not descripcion or len(descripcion) > 150:
        return None, "La descripción es obligatoria (máximo 150 caracteres)."
    if unidad not in UNIDADES:
        return None, "Seleccione una unidad de medida válida."
    if presentacion not in PRESENTACIONES:
        return None, "Seleccione una presentación válida."
    if not re.fullmatch(r"\d{1,8}(\.\d{1,2})?", precio.strip()):
        return None, "El precio debe ser un número (máximo 2 decimales)."
    if estado not in ESTADOS:
        return None, "Seleccione un estado válido."
    try:
        fecha_d = datetime.strptime(fecha.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None, "La fecha debe tener el formato AAAA-MM-DD."
    if not re.fullmatch(r"\d{1,6}", stock.strip()):
        return None, "El stock mínimo debe ser un número entero."
    datos = (codigo, descripcion, unidad, presentacion,
             Decimal(precio.strip()), estado, fecha_d, int(stock.strip()))
    return datos, None


def _validar_existencias(cantidad, vencimiento, obligatoria):
    """Devuelve ((cantidad, vencimiento), None) o (None, mensaje_de_error)."""
    cantidad = cantidad.strip()
    if not re.fullmatch(r"\d{1,6}", cantidad):
        return None, "La cantidad debe ser un número entero."
    cantidad_i = int(cantidad)
    if obligatoria and cantidad_i <= 0:
        return None, "La cantidad a ingresar debe ser mayor que 0."
    vencimiento = vencimiento.strip()
    venc = None
    if vencimiento:
        try:
            venc = datetime.strptime(vencimiento, "%Y-%m-%d").date()
        except ValueError:
            return None, "El vencimiento debe tener el formato AAAA-MM-DD."
        if venc < date.today():
            return None, "El vencimiento no puede ser anterior a hoy."
    return (cantidad_i, venc), None


def listar():
    return producto_modelo.listar() if _hay_sesion() else []


def obtener(codigo):
    if not _hay_sesion():
        return None
    return producto_modelo.obtener(codigo.strip().upper())


def agregar(campos, cantidad, vencimiento):
    if not _es_admin():
        return False, "Solo un administrador puede realizar esta acción."
    datos, error = _validar(*campos)
    if error:
        return False, error
    existencias, error = _validar_existencias(cantidad, vencimiento, obligatoria=False)
    if error:
        return False, error
    if producto_modelo.existe(datos[0]):
        return False, "Ya existe un producto con ese código."
    cantidad_i, venc = existencias
    usuario = sesion.usuario_actual["usuario"]
    if producto_modelo.agregar_con_existencias(datos, cantidad_i, date.today(), venc, usuario):
        return True, "Producto agregado correctamente."
    return False, "No se pudo agregar el producto."


def modificar(*campos):
    if not _es_admin():
            return False, "Solo un administrador puede realizar esta acción."
    datos, error = _validar(*campos)
    if error:
        return False, error
    if not producto_modelo.existe(datos[0]):
        return False, "No existe un producto con ese código. Use AGREGAR."
    if producto_modelo.actualizar(datos):
        return True, "Producto actualizado correctamente."
    return False, "No se pudo actualizar el producto."


def registrar_ingreso(codigo, cantidad, vencimiento):
    if not _es_admin():
            return False, "Solo un administrador puede realizar esta acción."
    codigo = codigo.strip().upper()
    if not codigo:
        return False, "Ingrese o seleccione el código del producto."
    existencias, error = _validar_existencias(cantidad, vencimiento, obligatoria=True)
    if error:
        return False, error
    producto = producto_modelo.obtener(codigo)
    if producto is None:
        return False, "No existe un producto con ese código."
    if producto[5] != "ACTIVO":
        return False, "No se pueden ingresar existencias a un producto INACTIVO."
    cantidad_i, venc = existencias    
    usuario = sesion.usuario_actual["usuario"]
    if producto_modelo.registrar_ingreso(codigo, cantidad_i, date.today(), venc, usuario):
        return True, f"Ingreso de {cantidad_i} registrado para {codigo}."
    return False, "No se pudo registrar el ingreso."


def eliminar(codigo):
    if not _es_admin():
        return False, "Solo un administrador puede dar de baja productos."
    codigo = codigo.strip().upper()
    if not producto_modelo.existe(codigo):
        return False, "No existe un producto con ese código."
    if producto_modelo.cambiar_estado(codigo, "INACTIVO"):
        return True, "Producto dado de baja (estado INACTIVO)."
    return False, "No se pudo dar de baja el producto."