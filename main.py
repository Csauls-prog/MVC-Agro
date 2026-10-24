from vistas.login_vista import LoginVista
from vistas.panel_vista import PanelVista
from controladores.login_controlador import iniciar_sesion
from controladores.menu_controlador import crear_vista
from controladores.panel_controlador import obtener_datos
from controladores import sesion


def main():
    while True:
        LoginVista(iniciar_sesion).mainloop()
        if not sesion.usuario_actual:
            break  # canceló el login
        panel = PanelVista(sesion.usuario_actual, crear_vista, obtener_datos)
        panel.mainloop()
        sesion.cerrar()
        if not panel.cerro_sesion:
            break  # cerró la ventana con la X: termina el programa


if __name__ == "__main__":
    main()