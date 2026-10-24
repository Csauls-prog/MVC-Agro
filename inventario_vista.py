from tkinter import ttk, messagebox
import customtkinter as ctk
from vistas.salida_vista import SalidaVista

from vistas.componentes import titulo_vista, tarjeta
from vistas.tema import ACENTO as VERDE, ACENTO_HOVER as VERDE_OSCURO, FUENTE


class InventarioVista(ctk.CTkFrame):
    def __init__(self, padre, controlador, mov_controlador, al_volver):
        super().__init__(padre, fg_color="transparent")
        self.ctrl = controlador
        self.mov_ctrl = mov_controlador
        self.al_volver = al_volver
        self._construir()
        for entrada in (self.e_codigo, self.e_descripcion, self.e_fecha):
            entrada.bind("<Return>", lambda _evento: self.buscar())
        self.limpiar()

    def _campo(self, padre, texto, columna, ancho):
        ctk.CTkLabel(padre, text=texto, font=(FUENTE, 11, "bold")).grid(
            row=0, column=columna, sticky="w", padx=8, pady=(10, 0))
        entrada = ctk.CTkEntry(padre, width=ancho)
        entrada.grid(row=1, column=columna, padx=8, pady=(2, 10), sticky="w")
        return entrada

    def _boton(self, padre, texto, color, hover, comando, ancho=130):
        ctk.CTkButton(padre, text=texto, width=ancho, fg_color=color, hover_color=hover,
                      font=(FUENTE, 12, "bold"), command=comando).pack(side="left", padx=(0, 8))

    def _construir(self):
        titulo_vista(self, "Inventario de productos", "Consulta, reportes y salidas")

        # Filtros
        filtros = tarjeta(self)
        filtros.pack(fill="x", padx=20, pady=(14, 4))
        self.e_codigo = self._campo(filtros, "CÓDIGO", 0, 150)
        self.e_descripcion = self._campo(filtros, "DESCRIPCIÓN", 1, 300)
        self.e_fecha = self._campo(filtros, "FECHA (AAAA-MM-DD)", 2, 170)
        ctk.CTkLabel(self, text="Deje los filtros vacíos y pulse BUSCAR para listar todo. "
                                "Si llena CÓDIGO y FECHA, se aplican a la vez.",
                     font=(FUENTE, 11), text_color="#616161").pack(anchor="w", padx=22)

        # Botones
        botones = tarjeta(self)
        botones.pack(fill="x", padx=20, pady=(8, 4))
        self._boton(botones, "BUSCAR", VERDE, VERDE_OSCURO, self.buscar)
        self._boton(botones, "LIMPIAR", "#F9A825", "#F57F17", self.limpiar)
        self._boton(botones, "REGISTRAR SALIDA", "#EF6C00", "#E65100",
                    self.registrar_salida, ancho=170)
        self._boton(botones, "CANCELAR", "#9E9E9E", "#757575", self.al_volver)

        # Barra inferior (se empaqueta antes que la tabla para que nunca se recorte)
        inferior = ctk.CTkFrame(self, fg_color="transparent")
        inferior.pack(side="bottom", fill="x", padx=20, pady=(0, 12))
        self.lbl_resumen = ctk.CTkLabel(inferior, text="", font=(FUENTE, 12, "bold"))
        self.lbl_resumen.pack(anchor="w")
        ctk.CTkLabel(inferior, text="Naranja: vence en 60 días o menos   ·   "
                                    "Rojo: ya vencido",
                     font=(FUENTE, 11), text_color="#616161").pack(anchor="w")

        # Tabla
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=26, font=(FUENTE, 10))
        estilo.configure("Treeview.Heading", font=(FUENTE, 10, "bold"),
                         background=VERDE, foreground="white")
        estilo.map("Treeview.Heading", background=[("active", VERDE_OSCURO)])
        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.pack(fill="both", expand=True, padx=20, pady=8)
        columnas = (("codigo", "CÓDIGO", 80), ("fecha", "FECHA", 90),
                    ("descripcion", "DESCRIPCIÓN", 230), ("cantidad", "CANTIDAD", 80),
                    ("presentacion", "PRESENTACIÓN", 100), ("unidad", "UNIDAD MEDIDA", 105),
                    ("precio", "PRECIO", 90), ("vencimiento", "VENCIMIENTO", 100))
        self.tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas],
                                  show="headings", selectmode="browse", height=9)
        for clave, texto, ancho in columnas:
            self.tabla.heading(clave, text=texto)
            self.tabla.column(clave, width=ancho, anchor="center")
        self.tabla.tag_configure("vencido", foreground="#C62828")
        self.tabla.tag_configure("proximo", foreground="#EF6C00")
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

    def buscar(self):
        filas, mensaje = self.ctrl.buscar(self.e_codigo.get(), self.e_descripcion.get(),
                                          self.e_fecha.get())
        if filas is None:
            messagebox.showwarning("Inventario", mensaje, parent=self)
            return
        self._mostrar(filas)

    def _mostrar(self, filas):
        self.tabla.delete(*self.tabla.get_children())
        for f in filas:
            estado = self.ctrl.estado_vencimiento(f[7])
            self.tabla.insert("", "end", tags=(estado,) if estado else (),
                              values=(f[0], f[1], f[2], f[3], f[4], f[5],
                                      f"Q {f[6]:,.2f}", f[7] if f[7] else "—"))
        if filas:
            cantidad, valor = self.ctrl.resumen(filas)
            self.lbl_resumen.configure(
                text=f"{len(filas)} registro(s)   ·   Cantidad total: {cantidad:,}   ·   "
                     f"Valor del inventario: Q {valor:,.2f}")
        else:
            self.lbl_resumen.configure(text="No se encontraron registros con esos criterios.")

    def limpiar(self):
        for entrada in (self.e_codigo, self.e_descripcion, self.e_fecha):
            entrada.delete(0, "end")
        self.tabla.delete(*self.tabla.get_children())
        self.lbl_resumen.configure(text="Pulse BUSCAR para consultar el inventario.")

    def registrar_salida(self):
        seleccion = self.tabla.selection()
        if seleccion:
            codigo = str(self.tabla.item(seleccion[0], "values")[0])
        else:
            codigo = self.e_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Inventario", "Seleccione un registro de la tabla "
                                   "o escriba el código del producto.", parent=self)
            return
        producto = self.mov_ctrl.obtener_producto(codigo)
        if producto is None:
            messagebox.showwarning("Inventario", "No existe un producto con ese código.",
                                   parent=self)
            return
        SalidaVista(self, self.mov_ctrl, producto, self._tras_salida)

    def _tras_salida(self):
        if self.tabla.get_children():
            self.buscar()  # actualiza la tabla con los mismos filtros