from controladores import sesion
from modelos import panel_modelo

DIAS_VENCIMIENTO = 60


def obtener_datos():
    """Reúne todo lo que muestra el panel. Devuelve None si no hay sesión."""
    if sesion.usuario_actual is None:
        return None
    return {
        "productos_activos": panel_modelo.productos_activos(),
        "valor_inventario": panel_modelo.valor_inventario(),
        "valores": panel_modelo.valor_por_producto(),
        "por_vencer": panel_modelo.lotes_por_vencer(DIAS_VENCIMIENTO),
        "bajo_minimo": panel_modelo.bajo_stock_minimo(),
    }