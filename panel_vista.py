from datetime import date
from tkinter import messagebox
import customtkinter as ctk
from vistas import tema
import traceback

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


class PanelVista(ctk.CTk):
    def __init__(self, datos_sesion, crear_vista, obtener_datos):
        super().__init__()
        self.datos_sesion = datos_sesion
        self.crear_vista = crear_vista
        self.obtener_datos = obtener_datos
        self.cerro_sesion = False
        self.vista_actual = None
        self.botones_nav = {}
        ctk.set_appearance_mode("light")
        self.title(f"{tema.EMPRESA} - Sistema de control")
        self.configure(fg_color=tema.FONDO)
        self._construir()
        self._mostrar("panel")
        try:
            self.update_idletasks()
            self.eval("tk::PlaceWindow . center")
        except Exception:
            pass

    # ---------- construcción ----------
    def _nav(self, padre, clave, texto, habilitado):
        boton = ctk.CTkButton(
            padre, text=texto, anchor="w", height=40, corner_radius=10,
            fg_color="transparent",
            hover_color=tema.ACENTO_HOVER if habilitado else tema.OSCURO,
            text_color="white", text_color_disabled="#5E7C70",
            state="normal" if habilitado else "disabled",
            font=(tema.FUENTE, 13), command=lambda: self._mostrar(clave))
        boton.pack(fill="x", padx=14, pady=2)
        self.botones_nav[clave] = boton

    def _tarjeta_kpi(self, padre, titulo, columna):
        tarjeta = ctk.CTkFrame(padre, fg_color=tema.TARJETA, corner_radius=14,
                               border_width=1, border_color=tema.BORDE,
                               width=165, height=92)
        tarjeta.grid(row=0, column=columna, sticky="nsew",
                     padx=(0 if columna == 0 else 14, 0))
        tarjeta.pack_propagate(False)
        padre.grid_columnconfigure(columna, weight=1)
        ctk.CTkLabel(tarjeta, text=titulo, text_color=tema.TEXTO_SUAVE,
                     font=(tema.FUENTE, 10, "bold")).pack(anchor="w", padx=16, pady=(14, 0))
        valor = ctk.CTkLabel(tarjeta, text="-", text_color=tema.TEXTO,
                             font=(tema.FUENTE, 26, "bold"))
        valor.pack(anchor="w", padx=16, pady=(2, 0))
        return valor

    def _tarjeta(self, padre, titulo, columna, peso):
        tarjeta = ctk.CTkFrame(padre, fg_color=tema.TARJETA, corner_radius=14,
                               border_width=1, border_color=tema.BORDE)
        tarjeta.grid(row=0, column=columna, sticky="nsew",
                     padx=(0 if columna == 0 else 14, 0))
        padre.grid_columnconfigure(columna, weight=peso)
        ctk.CTkLabel(tarjeta, text=titulo, text_color=tema.TEXTO,
                     font=(tema.FUENTE, 14, "bold")).pack(anchor="w", padx=18, pady=(16, 8))
        cuerpo = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        return cuerpo

    def _construir(self):
        rol = self.datos_sesion["rol"]
        es_admin = rol == "ADMIN"

        # Barra lateral (el pie se empaqueta primero para que nunca se recorte)
        lateral = ctk.CTkFrame(self, fg_color=tema.OSCURO, corner_radius=0, width=210)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        pie = ctk.CTkFrame(lateral, fg_color="transparent")
        pie.pack(side="bottom", fill="x", padx=22, pady=22)
        ctk.CTkLabel(pie, text=self.datos_sesion["usuario"], text_color="white",
                     font=(tema.FUENTE, 13, "bold")).pack(anchor="w")
        ctk.CTkLabel(pie, text=f"Rol: {rol}", text_color=tema.TEXTO_CLARO,
                     font=(tema.FUENTE, 11)).pack(anchor="w", pady=(0, 10))
        ctk.CTkButton(pie, text="CERRAR SESIÓN", height=36, fg_color="transparent",
                      border_width=1, border_color=tema.TEXTO_CLARO, text_color="white",
                      hover_color=tema.OSCURO_HOVER, font=(tema.FUENTE, 12, "bold"),
                      command=self._cerrar_sesion).pack(fill="x")
        ctk.CTkLabel(lateral, text=tema.EMPRESA, text_color="white",
                     font=(tema.FUENTE, 22, "bold")).pack(anchor="w", padx=22, pady=(28, 0))
        ctk.CTkLabel(lateral, text="Control de agroquímicos", text_color=tema.TEXTO_CLARO,
                     font=(tema.FUENTE, 11)).pack(anchor="w", padx=22, pady=(0, 26))
        self._nav(lateral, "panel", "Panel general", True)
        self._nav(lateral, "inventario", "Inventario de productos", True)
        self._nav(lateral, "productos", "Productos", es_admin)
        self._nav(lateral, "usuarios", "Usuarios", es_admin)

        # Área de contenido: tamaño fijo para que la ventana no "salte" al cambiar de pantalla
        principal = ctk.CTkFrame(self, fg_color="transparent")
        principal.pack(side="left", fill="both", expand=True, padx=32, pady=28)
        self.contenedor = ctk.CTkFrame(principal, fg_color="transparent",
                                       width=940, height=620)
        self.contenedor.pack(fill="both", expand=True)
        self.contenedor.pack_propagate(False)
        self.vista_panel = self._construir_panel(self.contenedor)

    def _construir_panel(self, padre):
        marco = ctk.CTkFrame(padre, fg_color="transparent")
        cabecera = ctk.CTkFrame(marco, fg_color="transparent")
        cabecera.pack(fill="x")
        ctk.CTkLabel(cabecera, text="Panel general", text_color=tema.TEXTO,
                     font=(tema.FUENTE, 26, "bold")).pack(anchor="w")
        hoy = date.today()
        ctk.CTkLabel(cabecera, text=f"{hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}",
                     text_color=tema.TEXTO_SUAVE, font=(tema.FUENTE, 12)).pack(anchor="w")
        ctk.CTkButton(cabecera, text="ACTUALIZAR", width=110, height=32,
                      fg_color=tema.ACENTO, hover_color=tema.ACENTO_HOVER,
                      font=(tema.FUENTE, 12, "bold"), command=self.refrescar
                      ).place(relx=1.0, rely=0.0, anchor="ne")

        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(fill="x", pady=(18, 14))
        self.kpi = {
            "activos": self._tarjeta_kpi(fila, "PRODUCTOS ACTIVOS", 0),
            "valor": self._tarjeta_kpi(fila, "VALOR DEL INVENTARIO", 1),
            "bajo": self._tarjeta_kpi(fila, "BAJO STOCK MÍNIMO", 2),
            "vencer": self._tarjeta_kpi(fila, "LOTES POR VENCER", 3),
        }

        inferior = ctk.CTkFrame(marco, fg_color="transparent")
        inferior.pack(fill="both", expand=True)
        inferior.grid_rowconfigure(0, weight=1)
        self.cuerpo_valores = self._tarjeta(inferior, "Valor por producto (Q)", 0, 3)
        self.cuerpo_alertas = self._tarjeta(inferior, "Alertas", 1, 2)
        return marco

    # ---------- navegación ----------
    def _mostrar(self, clave):
        nueva = None
        if clave != "panel":
            try:
                nueva = self.crear_vista(clave, self.contenedor,
                                         lambda: self._mostrar("panel"))
            except Exception as error:
                traceback.print_exc()
                messagebox.showerror("Error", f"No se pudo abrir el módulo:\n{error}")
                return
            if nueva is None:
                messagebox.showerror("Acceso denegado",
                                     "No tiene permiso para acceder a este módulo.")
                return
        if self.vista_actual is not None:
            self.vista_actual.destroy()
            self.vista_actual = None
        self.vista_panel.pack_forget()
        if nueva is None:
            self.vista_panel.pack(fill="both", expand=True)
            self.refrescar()
        else:
            nueva.pack(fill="both", expand=True)
            self.vista_actual = nueva
        for nombre, boton in self.botones_nav.items():
            activo = nombre == clave
            boton.configure(fg_color=tema.ACENTO if activo else "transparent",
                            font=(tema.FUENTE, 13, "bold" if activo else "normal"))
    def _cerrar_sesion(self):
        self.cerro_sesion = True
        self.destroy()

    # ---------- datos del panel ----------
    def refrescar(self):
        datos = self.obtener_datos()
        if datos is None:
            return
        bajo, vencer = datos["bajo_minimo"], datos["por_vencer"]
        self.kpi["activos"].configure(text=str(datos["productos_activos"]))
        self.kpi["valor"].configure(text=f"Q {datos['valor_inventario']:,.0f}")
        self.kpi["bajo"].configure(text=str(len(bajo)),
                                   text_color=tema.ALERTA if bajo else tema.TEXTO)
        self.kpi["vencer"].configure(text=str(len(vencer)),
                                     text_color=tema.AVISO if vencer else tema.TEXTO)
        self._pintar_valores(datos["valores"])
        self._pintar_alertas(vencer, bajo)

    def _limpiar(self, contenedor):
        for hijo in contenedor.winfo_children():
            hijo.destroy()

    def _pintar_valores(self, valores):
        self._limpiar(self.cuerpo_valores)
        if not valores:
            ctk.CTkLabel(self.cuerpo_valores, text="Aún no hay existencias registradas.",
                         text_color=tema.TEXTO_SUAVE).pack(anchor="w")
            return
        maximo = float(max(v[1] for v in valores)) or 1.0
        for descripcion, valor in valores:
            fila = ctk.CTkFrame(self.cuerpo_valores, fg_color="transparent")
            fila.pack(fill="x", pady=4)
            ctk.CTkLabel(fila, text=descripcion[:24], width=170, anchor="w",
                         text_color=tema.TEXTO, font=(tema.FUENTE, 12)).pack(side="left")
            barra = ctk.CTkProgressBar(fila, width=170, height=10,
                                       progress_color=tema.ACENTO, fg_color="#ECE8DC")
            barra.set(float(valor) / maximo)
            barra.pack(side="left", padx=8)
            ctk.CTkLabel(fila, text=f"{valor:,.0f}", width=60, anchor="e",
                         text_color=tema.TEXTO_SUAVE, font=(tema.FUENTE, 12)).pack(side="left")

    def _linea_alerta(self, izquierda, derecha, color):
        fila = ctk.CTkFrame(self.cuerpo_alertas, fg_color="transparent")
        fila.pack(fill="x", pady=3)
        ctk.CTkLabel(fila, text=izquierda, anchor="w", text_color=tema.TEXTO,
                     font=(tema.FUENTE, 12)).pack(side="left")
        ctk.CTkLabel(fila, text=derecha, anchor="e", text_color=color,
                     font=(tema.FUENTE, 12, "bold")).pack(side="right")

    def _titulo_alerta(self, texto):
        ctk.CTkLabel(self.cuerpo_alertas, text=texto, text_color=tema.TEXTO_SUAVE,
                     font=(tema.FUENTE, 10, "bold")).pack(anchor="w", pady=(8, 2))

    def _pintar_alertas(self, por_vencer, bajo_minimo):
        self._limpiar(self.cuerpo_alertas)
        if not por_vencer and not bajo_minimo:
            ctk.CTkLabel(self.cuerpo_alertas, text="Sin alertas por ahora.",
                         text_color=tema.TEXTO_SUAVE).pack(anchor="w")
            return
        if por_vencer:
            self._titulo_alerta("POR VENCER (60 DÍAS)")
            for codigo, descripcion, vence, _cantidad in por_vencer[:4]:
                vencido = vence < date.today()
                self._linea_alerta(f"{codigo} · {descripcion[:20]}",
                                   vence.strftime("%d/%m/%Y") + (" (vencido)" if vencido else ""),
                                   tema.ALERTA if vencido else tema.AVISO)
        if bajo_minimo:
            self._titulo_alerta("BAJO STOCK MÍNIMO")
            for codigo, descripcion, total, minimo in bajo_minimo[:4]:
                self._linea_alerta(f"{codigo} · {descripcion[:20]}",
                                   f"{int(total)} de {minimo}", tema.ALERTA)