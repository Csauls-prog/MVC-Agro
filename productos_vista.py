import re
from datetime import date
from tkinter import ttk, messagebox
import customtkinter as ctk

from vistas.componentes import titulo_vista, tarjeta
from vistas.tema import ACENTO as VERDE, ACENTO_HOVER as VERDE_OSCURO, FUENTE


class ProductosVista(ctk.CTkFrame):
    def __init__(self, padre, controlador, al_volver):
        super().__init__(padre, fg_color="transparent")
        self.ctrl = controlador
        self.al_volver = al_volver
        self._construir()
        self.limpiar()
        self.refrescar()

    # ---------- construcción de la ventana ----------
    def _entrada(self, padre, texto, fila, columna, ancho=150):
        ctk.CTkLabel(padre, text=texto, font=(FUENTE, 11, "bold")).grid(
            row=fila * 2, column=columna, sticky="w", padx=8, pady=(10, 0))
        entrada = ctk.CTkEntry(padre, width=ancho)
        entrada.grid(row=fila * 2 + 1, column=columna, padx=8, pady=(2, 0), sticky="w")
        return entrada

    def _combo(self, padre, texto, fila, columna, valores, ancho=150):
        ctk.CTkLabel(padre, text=texto, font=(FUENTE, 11, "bold")).grid(
            row=fila * 2, column=columna, sticky="w", padx=8, pady=(10, 0))
        combo = ctk.CTkComboBox(padre, values=valores, width=ancho, state="readonly",
                                button_color=VERDE, button_hover_color=VERDE_OSCURO)
        combo.grid(row=fila * 2 + 1, column=columna, padx=8, pady=(2, 0), sticky="w")
        return combo

    def _solo_patron(self, entrada, patron):
        """Bloquea las teclas que harían que el texto deje de cumplir el patrón."""
        validar = (self.register(lambda nuevo: re.fullmatch(patron, nuevo) is not None), "%P")
        entrada._entry.configure(validate="key", validatecommand=validar)

    def _boton(self, padre, texto, color, hover, comando, lado="left", ancho=120):
        ctk.CTkButton(padre, text=texto, width=ancho, fg_color=color, hover_color=hover,
                      font=(FUENTE, 12, "bold"), command=comando).pack(side=lado, padx=(0, 8))

    def _construir(self):
        titulo_vista(self, "Gestión de productos", "Catálogo, ingresos y bajas · solo administrador")

        # Formulario
        form = tarjeta(self)
        form.pack(fill="x", padx=20, pady=(14, 6))
        self.e_codigo = self._entrada(form, "CÓDIGO", 0, 0, 130)
        self.e_descripcion = self._entrada(form, "DESCRIPCIÓN", 0, 1, 300)
        self.c_unidad = self._combo(form, "UNIDAD DE MEDIDA", 0, 2, self.ctrl.UNIDADES)
        self.c_presentacion = self._combo(form, "PRESENTACIÓN", 0, 3, self.ctrl.PRESENTACIONES)
        self.e_precio = self._entrada(form, "PRECIO (Q)", 1, 0, 130)
        self.c_estado = self._combo(form, "ESTADO", 1, 1, self.ctrl.ESTADOS, 150)
        self.e_fecha = self._entrada(form, "FECHA (AAAA-MM-DD)", 1, 2)
        self.e_stock = self._entrada(form, "STOCK MÍNIMO", 1, 3)
        self.e_cantidad = self._entrada(form, "CANTIDAD A INGRESAR", 2, 0, 130)
        self.e_vencimiento = self._entrada(form, "VENCIMIENTO (OPCIONAL)", 2, 1, 150)
        self._solo_patron(self.e_precio, r"\d{0,8}(\.\d{0,2})?")
        self._solo_patron(self.e_stock, r"\d{0,6}")
        self._solo_patron(self.e_cantidad, r"\d{0,6}")

        # Botones
        botones = ctk.CTkFrame(self, fg_color="transparent")
        botones.pack(fill="x", padx=20, pady=(10, 4))
        self._boton(botones, "AGREGAR", VERDE, VERDE_OSCURO, self.agregar, ancho=100)
        self._boton(botones, "MODIFICAR", "#F9A825", "#F57F17", self.modificar, ancho=105)
        self._boton(botones, "ELIMINAR", "#C62828", "#8E0000", self.eliminar, ancho=100)
        self._boton(botones, "BUSCAR", "#1565C0", "#0D47A1", self.buscar, ancho=85)
        self._boton(botones, "REGISTRAR INGRESO", "#00838F", "#006064",
                    self.registrar_ingreso, ancho=170)
       # self._boton(botones, "REGISTRAR SALIDA", "#EF6C00", "#E65100",
      #              self.registrar_salida, ancho=160)
        self._boton(botones, "LIMPIAR", "#9E9E9E", "#757575", self.limpiar, ancho=90)

        # Barra inferior (se empaqueta antes que la tabla para que nunca se recorte)
        inferior = ctk.CTkFrame(self, fg_color="transparent")
        inferior.pack(side="bottom", fill="x", padx=20, pady=(0, 14))
        self._boton(inferior, "CERRAR", "#9E9E9E", "#757575", self.al_volver, lado="right")
        ctk.CTkLabel(inferior, text="Rojo: cantidad bajo el stock mínimo   ·   "
                                    "Gris: producto inactivo",
                     font=(FUENTE, 11), text_color="#616161").pack(side="left")

        # Tabla
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=26, font=(FUENTE, 10))
        estilo.configure("Treeview.Heading", font=(FUENTE, 10, "bold"),
                         background=VERDE, foreground="white")
        estilo.map("Treeview.Heading", background=[("active", VERDE_OSCURO)])
        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.pack(fill="both", expand=True, padx=20, pady=8)
        columnas = (("codigo", "CÓDIGO", 80), ("descripcion", "DESCRIPCIÓN", 220),
                    ("unidad", "UNIDAD", 85), ("presentacion", "PRESENTACIÓN", 95),
                    ("precio", "PRECIO", 85), ("estado", "ESTADO", 75),
                    ("fecha", "FECHA", 85), ("stock", "MÍN.", 55),
                    ("cantidad", "CANTIDAD", 80))
        self.tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas],
                                  show="headings", selectmode="browse", height=6)
        for clave, texto, ancho in columnas:
            self.tabla.heading(clave, text=texto)
            self.tabla.column(clave, width=ancho, anchor="center")
        self.tabla.tag_configure("inactivo", foreground="#9E9E9E")
        self.tabla.tag_configure("bajo", foreground="#C62828")
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    # ---------- utilidades del formulario ----------
    def _campos(self):
        """Los 8 campos del producto (la cantidad y el vencimiento van aparte)."""
        return (self.e_codigo.get(), self.e_descripcion.get(), self.c_unidad.get(),
                self.c_presentacion.get(), self.e_precio.get(), self.c_estado.get(),
                self.e_fecha.get(), self.e_stock.get())

    def _poner(self, entrada, valor):
        entrada.delete(0, "end")
        entrada.insert(0, str(valor))

    def _cargar(self, fila):
        codigo, descripcion, unidad, presentacion, precio, estado, fecha, stock = fila
        self._poner(self.e_codigo, codigo)
        self._poner(self.e_descripcion, descripcion)
        self.c_unidad.set(unidad)
        self.c_presentacion.set(presentacion)
        self._poner(self.e_precio, precio)
        self.c_estado.set(estado)
        self._poner(self.e_fecha, fecha)
        self._poner(self.e_stock, stock)
        self._reiniciar_ingreso()  # al cargar un producto no se arrastra una cantidad vieja

    def _reiniciar_ingreso(self):
        self._poner(self.e_cantidad, 0)
        self.e_vencimiento.delete(0, "end")

    def _al_seleccionar(self, _evento):
        seleccion = self.tabla.selection()
        if seleccion:
            fila = self.ctrl.obtener(self.tabla.item(seleccion[0], "values")[0])
            if fila:
                self._cargar(fila)

    def _avisar(self, ok, mensaje):
        if ok:
            messagebox.showinfo("Productos", mensaje, parent=self)
        else:
            messagebox.showwarning("Productos", mensaje, parent=self)

    # ---------- acciones ----------
    def refrescar(self):
        self.tabla.delete(*self.tabla.get_children())
        for f in self.ctrl.listar():
            cantidad = int(f[8])
            if f[5] == "INACTIVO":
                tags = ("inactivo",)
            elif cantidad < f[7]:
                tags = ("bajo",)
            else:
                tags = ()
            self.tabla.insert("", "end", tags=tags,
                              values=(f[0], f[1], f[2], f[3], f"Q {f[4]:,.2f}",
                                      f[5], f[6], f[7], cantidad))

    def limpiar(self):
        for entrada in (self.e_codigo, self.e_descripcion, self.e_precio):
            entrada.delete(0, "end")
        self.c_unidad.set(self.ctrl.UNIDADES[0])
        self.c_presentacion.set(self.ctrl.PRESENTACIONES[0])
        self.c_estado.set("ACTIVO")
        self._poner(self.e_fecha, date.today().isoformat())
        self._poner(self.e_stock, 0)
        self._reiniciar_ingreso()
        self.tabla.selection_remove(self.tabla.selection())

    def agregar(self):
        ok, mensaje = self.ctrl.agregar(self._campos(), self.e_cantidad.get(),
                                        self.e_vencimiento.get())
        self._avisar(ok, mensaje)
        if ok:
            self.limpiar()
            self.refrescar()

    def modificar(self):
        ok, mensaje = self.ctrl.modificar(*self._campos())
        self._avisar(ok, mensaje)
        if ok:
            self.refrescar()

    def registrar_ingreso(self):
        ok, mensaje = self.ctrl.registrar_ingreso(self.e_codigo.get(), self.e_cantidad.get(),
                                                  self.e_vencimiento.get())
        self._avisar(ok, mensaje)
        if ok:
            self._reiniciar_ingreso()
            self.refrescar()


            
    def registrar_salida(self):
        codigo = self.e_codigo.get().strip()
        if not codigo:
            self._avisar(False, "Ingrese o seleccione el código del producto.")
            return
        producto = self.ctrl.obtener(codigo)
        if producto is None:
            self._avisar(False, "No existe un producto con ese código.")
            return
       # SalidaVista(self, self.mov_ctrl, producto, self.refrescar)



    def eliminar(self):
        codigo = self.e_codigo.get().strip()
        if not codigo:
            self._avisar(False, "Ingrese o seleccione el código del producto.")
            return
        if not messagebox.askyesno("Confirmar",
                                   f"¿Dar de baja el producto {codigo.upper()}?", parent=self):
            return
        ok, mensaje = self.ctrl.eliminar(codigo)
        self._avisar(ok, mensaje)
        if ok:
            self.limpiar()
            self.refrescar()

    def buscar(self):
        codigo = self.e_codigo.get().strip()
        if not codigo:
            self._avisar(False, "Escriba un código para buscar.")
            return
        fila = self.ctrl.obtener(codigo)
        if fila:
            self._cargar(fila)
        else:
            self._avisar(False, "No existe un producto con ese código.")