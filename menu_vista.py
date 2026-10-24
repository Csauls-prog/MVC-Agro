"""

import customtkinter as ctk

VERDE = "#2E7D32"
VERDE_OSCURO = "#1B5E20"
FUENTE = "Segoe UI"


class MenuVista(ctk.CTk):
    def __init__(self, datos_sesion, acciones):
        super().__init__()
        self.datos = datos_sesion
        self.acciones = acciones
        self.cerro_sesion = False
        ctk.set_appearance_mode("light")
        self.title("EMPRESA - Menú principal")
        self.geometry("520x620")
        self.resizable(False, False)
        self._construir()

    def _construir(self):
        encabezado = ctk.CTkFrame(self, fg_color=VERDE, corner_radius=0, height=140)
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)
        ctk.CTkLabel(encabezado, text="EMPRESA", text_color="white",
                     font=(FUENTE, 32, "bold")).pack(pady=(24, 0))
        ctk.CTkLabel(encabezado, text="MENÚ PRINCIPAL", text_color="#C8E6C9",
                     font=(FUENTE, 13)).pack()
        ctk.CTkLabel(encabezado,
                     text=f"Sesión: {self.datos['usuario']} · {self.datos['rol']}",
                     text_color="white", font=(FUENTE, 12)).pack(pady=(8, 0))

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=40, pady=25)

        es_admin = self.datos["rol"] == "ADMIN"
        self._opcion(cuerpo, "USUARIOS",
                     "Gestión de usuarios y roles (solo administrador)", "usuarios", es_admin)
        self._opcion(cuerpo, "PRODUCTOS",
                     "Catálogo, ingresos y bajas (solo administrador)", "productos", es_admin)
        self._opcion(cuerpo, "INVENTARIO DE PRODUCTOS",
                     "Consulta, reportes y salidas", "inventario", True)

        ctk.CTkButton(cuerpo, text="CERRAR SESIÓN", height=42, fg_color="#9E9E9E",
                      hover_color="#757575", font=(FUENTE, 13, "bold"),
                      command=self._cerrar_sesion).pack(fill="x", pady=(18, 0))

    def _opcion(self, padre, titulo, detalle, clave, habilitada):
        ctk.CTkButton(
            padre, text=f"{titulo}\n{detalle}", height=80, anchor="w",
            fg_color=VERDE if habilitada else "#BDBDBD",
            hover_color=VERDE_OSCURO, text_color_disabled="#F5F5F5",
            font=(FUENTE, 14, "bold"),
            state="normal" if habilitada else "disabled",
            command=lambda: self.acciones[clave](self),
        ).pack(fill="x", pady=8)

    def _cerrar_sesion(self):
        self.cerro_sesion = True
        self.destroy()

        """