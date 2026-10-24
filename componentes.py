import customtkinter as ctk
from vistas import tema


def titulo_vista(padre, titulo, subtitulo):
    caja = ctk.CTkFrame(padre, fg_color="transparent")
    caja.pack(fill="x", pady=(0, 10))
    ctk.CTkLabel(caja, text=titulo, text_color=tema.TEXTO,
                 font=(tema.FUENTE, 24, "bold")).pack(anchor="w")
    ctk.CTkLabel(caja, text=subtitulo, text_color=tema.TEXTO_SUAVE,
                 font=(tema.FUENTE, 12)).pack(anchor="w")


def tarjeta(padre):
    return ctk.CTkFrame(padre, fg_color=tema.TARJETA, corner_radius=14,
                        border_width=1, border_color=tema.BORDE)