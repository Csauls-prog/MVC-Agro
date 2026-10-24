from tkinter import ttk, messagebox
import customtkinter as ctk

from vistas.componentes import titulo_vista, tarjeta
from vistas.tema import ACENTO as VERDE, ACENTO_HOVER as VERDE_OSCURO, FUENTE

class UsuariosVista(ctk.CTkFrame):
    def __init__(self, padre, controlador, al_volver):
        super().__init__(padre, fg_color="transparent")
        self.ctrl = controlador
        self.al_volver = al_volver
        self._construir()
        self.refrescar()

    def _campo(self, padre, texto, columna, oculto=False):
        ctk.CTkLabel(padre, text=texto, font=(FUENTE, 11, "bold")).grid(
            row=0, column=columna, sticky="w", padx=8, pady=(10, 0))
        entrada = ctk.CTkEntry(padre, width=150, show="•" if oculto else "")
        entrada.grid(row=1, column=columna, padx=8, pady=(2, 0))
        return entrada

    def _construir(self):
        titulo_vista(self, "Administración de usuarios", "Altas, bajas y reporte de usuarios")

        # Formulario de alta
        form = tarjeta(self)
        form.pack(fill="x", padx=20, pady=(16, 8))
        self.e_usuario = self._campo(form, "USUARIO", 0)
        self.e_password = self._campo(form, "CONTRASEÑA", 1, oculto=True)
        self.e_confirmar = self._campo(form, "CONFIRMAR", 2, oculto=True)
        ctk.CTkLabel(form, text="ROL", font=(FUENTE, 11, "bold")).grid(
            row=0, column=3, sticky="w", padx=8, pady=(10, 0))
        self.menu_rol = ctk.CTkOptionMenu(form, values=["VENDEDOR", "ADMIN"], width=130,
                                          fg_color=VERDE, button_color=VERDE_OSCURO)
        self.menu_rol.grid(row=1, column=3, padx=8, pady=(2, 0))
        botones = ctk.CTkFrame(form, fg_color="transparent")
        botones.grid(row=2, column=0, columnspan=4, sticky="w", padx=8, pady=12)
        ctk.CTkButton(botones, text="AGREGAR", fg_color=VERDE, hover_color=VERDE_OSCURO,
                      command=self.agregar).pack(side="left", padx=(0, 8))
        ctk.CTkButton(botones, text="LIMPIAR", fg_color="#9E9E9E", hover_color="#757575",
                      command=self.limpiar).pack(side="left")

        # Filtro por estado
        filtro = ctk.CTkFrame(self, fg_color="transparent")
        filtro.pack(fill="x", padx=20)
        ctk.CTkLabel(filtro, text="Mostrar:", font=(FUENTE, 12, "bold")).pack(side="left")
        self.var_filtro = ctk.StringVar(value="TODOS")
        ctk.CTkSegmentedButton(filtro, values=["TODOS", "ACTIVO", "INACTIVO"],
                               variable=self.var_filtro, selected_color=VERDE,
                               selected_hover_color=VERDE_OSCURO,
                               command=lambda _: self.refrescar()).pack(side="left", padx=10)

                # Acciones sobre el usuario seleccionado (se empaquetan primero, abajo)
        acciones = ctk.CTkFrame(self, fg_color="transparent")
        acciones.pack(side="bottom", fill="x", padx=20, pady=(0, 16))
        ctk.CTkButton(acciones, text="DAR DE BAJA", fg_color="#C62828",
                      hover_color="#8E0000",
                      command=lambda: self.cambiar("INACTIVO")).pack(side="left")
        ctk.CTkButton(acciones, text="REACTIVAR", fg_color=VERDE,
                      hover_color=VERDE_OSCURO,
                      command=lambda: self.cambiar("ACTIVO")).pack(side="left", padx=8)
        ctk.CTkButton(acciones, text="CERRAR", fg_color="#9E9E9E", hover_color="#757575",
                      command=self.al_volver).pack(side="right")

        # Tabla de usuarios (reportería)
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=28, font=(FUENTE, 11))
        estilo.configure("Treeview.Heading", font=(FUENTE, 11, "bold"),
                         background=VERDE, foreground="white")
        estilo.map("Treeview.Heading", background=[("active", VERDE_OSCURO)])
        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.pack(fill="both", expand=True, padx=20, pady=10)
        self.tabla = ttk.Treeview(marco, columns=("id", "usuario", "rol", "estado"),
                                  show="headings", selectmode="browse", height=8)
        for col, texto, ancho in (("id", "ID", 60), ("usuario", "USUARIO", 260),
                                  ("rol", "ROL", 160), ("estado", "ESTADO", 160)):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor="center")
        self.tabla.tag_configure("inactivo", foreground="#9E9E9E")
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

    def refrescar(self):
        estado = self.var_filtro.get()
        self.tabla.delete(*self.tabla.get_children())
        for fila in self.ctrl.listar(None if estado == "TODOS" else estado):
            tags = ("inactivo",) if fila[3] == "INACTIVO" else ()
            self.tabla.insert("", "end", values=fila, tags=tags)

    def limpiar(self):
        for entrada in (self.e_usuario, self.e_password, self.e_confirmar):
            entrada.delete(0, "end")
        self.menu_rol.set("VENDEDOR")

    def agregar(self):
        ok, mensaje = self.ctrl.agregar(self.e_usuario.get(), self.e_password.get(),
                                        self.e_confirmar.get(), self.menu_rol.get())
        if ok:
            messagebox.showinfo("Usuarios", mensaje, parent=self)
            self.limpiar()
            self.refrescar()
        else:
            messagebox.showwarning("Usuarios", mensaje, parent=self)

    def cambiar(self, nuevo_estado):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Usuarios", "Seleccione un usuario de la tabla.",
                                   parent=self)
            return
        valores = self.tabla.item(seleccion[0], "values")
        ok, mensaje = self.ctrl.cambiar_estado(int(valores[0]), valores[1], nuevo_estado)
        if ok:
            self.refrescar()
        messagebox.showinfo("Usuarios", mensaje, parent=self) if ok else \
            messagebox.showwarning("Usuarios", mensaje, parent=self)