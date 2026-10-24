import re
from tkinter import messagebox
import customtkinter as ctk

VERDE = "#2E7D32"
VERDE_OSCURO = "#1B5E20"
FUENTE = "Segoe UI"


class SalidaVista(ctk.CTkToplevel):
    def __init__(self, padre, controlador, producto, al_terminar):
        super().__init__(padre.winfo_toplevel())
        self.padre = padre
        self.ctrl = controlador
        self.producto = producto
        self.al_terminar = al_terminar
        self.title("EMPRESA - Registrar salida")
        self.resizable(False, False)
        self.transient(padre.winfo_toplevel())
        self.after(150, self.grab_set)
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self._construir()
        self._actualizar_stock()

    def _construir(self):
        enc = ctk.CTkFrame(self, fg_color=VERDE, corner_radius=0, height=70)
        enc.pack(fill="x")
        enc.pack_propagate(False)
        ctk.CTkLabel(enc, text="REGISTRAR SALIDA", text_color="white",
                     font=(FUENTE, 20, "bold")).pack(expand=True)

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=30, pady=20)
        ctk.CTkLabel(cuerpo, text=f"{self.producto[0]} · {self.producto[1]}",
                     font=(FUENTE, 13, "bold"), wraplength=320,
                     justify="left").pack(anchor="w")
        self.lbl_stock = ctk.CTkLabel(cuerpo, text="", font=(FUENTE, 12))
        self.lbl_stock.pack(anchor="w", pady=(2, 14))

        ctk.CTkLabel(cuerpo, text="CANTIDAD A DESCARGAR",
                     font=(FUENTE, 11, "bold")).pack(anchor="w")
        self.e_cantidad = ctk.CTkEntry(cuerpo, width=320)
        self.e_cantidad.pack(anchor="w", pady=(2, 12))
        validar = (self.register(lambda nuevo: re.fullmatch(r"\d{0,6}", nuevo) is not None),
                   "%P")
        self.e_cantidad._entry.configure(validate="key", validatecommand=validar)

        ctk.CTkLabel(cuerpo, text="MOTIVO", font=(FUENTE, 11, "bold")).pack(anchor="w")
        self.c_motivo = ctk.CTkComboBox(cuerpo, values=self.ctrl.MOTIVOS_SALIDA, width=320,
                                        state="readonly", button_color=VERDE,
                                        button_hover_color=VERDE_OSCURO)
        self.c_motivo.set(self.ctrl.MOTIVOS_SALIDA[0])
        self.c_motivo.pack(anchor="w", pady=(2, 18))

        botones = ctk.CTkFrame(cuerpo, fg_color="transparent")
        botones.pack(anchor="w")
        ctk.CTkButton(botones, text="REGISTRAR SALIDA", width=170, fg_color="#EF6C00",
                      hover_color="#E65100", font=(FUENTE, 12, "bold"),
                      command=self.registrar).pack(side="left", padx=(0, 8))
        ctk.CTkButton(botones, text="CANCELAR", width=120, fg_color="#9E9E9E",
                      hover_color="#757575", font=(FUENTE, 12, "bold"),
                      command=self._cerrar).pack(side="left")

    def _actualizar_stock(self):
        disponible = self.ctrl.stock_actual(self.producto[0])
        self.lbl_stock.configure(text=f"Disponible: {disponible:,} {self.producto[2].lower()}")

    def registrar(self):
        ok, mensaje = self.ctrl.registrar_salida(self.producto[0], self.e_cantidad.get(),
                                                 self.c_motivo.get())
        if ok:
            messagebox.showinfo("Salidas", mensaje, parent=self)
            self.al_terminar()
            self._cerrar()
        else:
            messagebox.showwarning("Salidas", mensaje, parent=self)
            self._actualizar_stock()

    def _cerrar(self):
        self.destroy()
       