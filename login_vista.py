import customtkinter as ctk

VERDE = "#2E7D32"
VERDE_OSCURO = "#1B5E20"
FUENTE = "Segoe UI"


class LoginVista(ctk.CTk):
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        ctk.set_appearance_mode("light")
        self.title("AgriInsumos - Acceso al sistema")
        self.geometry("420x540")
        self.resizable(False, False)
        self._construir()
        self.bind("<Return>", lambda evento: self.aceptar())

    def _construir(self):
        encabezado = ctk.CTkFrame(self, fg_color=VERDE, corner_radius=0, height=120)
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)
        ctk.CTkLabel(encabezado, text="AgroInsumos", text_color="white",
                     font=(FUENTE, 32, "bold")).pack(pady=(26, 0))
        ctk.CTkLabel(encabezado, text="Sistema de Control · Agroquímicos",
                     text_color="#C8E6C9", font=(FUENTE, 13)).pack()

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=40, pady=30)

        ctk.CTkLabel(cuerpo, text="USUARIO", anchor="w",
                     font=(FUENTE, 12, "bold")).pack(fill="x")
        self.entry_usuario = ctk.CTkEntry(cuerpo, height=40,
                                          placeholder_text="Ingrese su usuario")
        self.entry_usuario.pack(fill="x", pady=(4, 16))

        ctk.CTkLabel(cuerpo, text="CONTRASEÑA", anchor="w",
                     font=(FUENTE, 12, "bold")).pack(fill="x")
        self.entry_password = ctk.CTkEntry(cuerpo, height=40, show="•",
                                           placeholder_text="Ingrese su contraseña")
        self.entry_password.pack(fill="x", pady=(4, 10))

        self.var_mostrar = ctk.BooleanVar()
        ctk.CTkCheckBox(cuerpo, text="Mostrar contraseña", variable=self.var_mostrar,
                        command=self._alternar_password, fg_color=VERDE,
                        hover_color=VERDE_OSCURO).pack(anchor="w")

        self.lbl_mensaje = ctk.CTkLabel(cuerpo, text="", text_color="#C62828",
                                        font=(FUENTE, 12))
        self.lbl_mensaje.pack(pady=12)

        ctk.CTkButton(cuerpo, text="ACEPTAR", height=42, fg_color=VERDE,
                      hover_color=VERDE_OSCURO, font=(FUENTE, 13, "bold"),
                      command=self.aceptar).pack(fill="x")
        ctk.CTkButton(cuerpo, text="CANCELAR", height=42, fg_color="#9E9E9E",
                      hover_color="#757575", font=(FUENTE, 13, "bold"),
                      command=self.destroy).pack(fill="x", pady=(10, 0))

    def _alternar_password(self):
        self.entry_password.configure(show="" if self.var_mostrar.get() else "•")

    def aceptar(self):
        ok, mensaje = self.controlador(self.entry_usuario.get(),
                                       self.entry_password.get())
        if ok:
            self.destroy()
        else:
            self.lbl_mensaje.configure(text=mensaje)
            self.entry_password.delete(0, "end")