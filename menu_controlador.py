from controladores import (sesion, usuarios_controlador, producto_controlador,
                           inventario_controlador, movimiento_controlador)
from vistas.usuarios_vista import UsuariosVista
from vistas.productos_vista import ProductosVista
from vistas.inventario_vista import InventarioVista


def _es_admin():
    return sesion.usuario_actual is not None and sesion.usuario_actual["rol"] == "ADMIN"


def crear_vista(clave, contenedor, al_volver):
    """Crea la pantalla pedida dentro del contenedor, o devuelve None si no hay permiso."""
    if clave == "usuarios" and _es_admin():
        return UsuariosVista(contenedor, usuarios_controlador, al_volver)
    if clave == "productos" and _es_admin():
        return ProductosVista(contenedor, producto_controlador, al_volver)
    if clave == "inventario" and sesion.usuario_actual is not None:
        return InventarioVista(contenedor, inventario_controlador,
                               movimiento_controlador, al_volver)
    return None