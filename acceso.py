#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import main_quit
from clases.operaciones import archivo
from clases.operaciones import conectar


class acceso:

    def __init__(self, permisos):
        # Verificar los permisos del Usuario (ventana principal)
        self.verificar_permisos = permisos

        arch = archivo("acceso")
        self.obj = arch.get_object

        vent = self.obj("ventana")
        vent.set_title("Acceso de Usuarios")
        vent.set_position(1)
        vent.set_modal(True)
        vent.show()

        self.obj("btn_entrar").set_sensitive(False)
        self.entrar = False

        self.obj("txt_alias").set_max_length(16)
        self.obj("txt_clave").set_max_length(50)
        self.obj("txt_alias").set_text("")
        self.obj("txt_clave").set_text("")
        self.obj("txt_alias").grab_focus()

        arch.connect_signals({
            'verificacion': self.verificacion,
            'on_btn_entrar_clicked': self.on_btn_entrar_clicked,
            'on_btn_salir_clicked': self.on_btn_salir_clicked,
            'on_ventana_hide': self.on_btn_salir_clicked
        })

    def verificacion(self, objeto):
        if len(self.obj("txt_alias").get_text()) == 0 \
        or len(self.obj("txt_clave").get_text()) == 0:
            self.obj("btn_entrar").set_sensitive(False)
        else:
            self.obj("btn_entrar").set_sensitive(True)

    def on_btn_entrar_clicked(self, objeto):
        alias = self.obj("txt_alias").get_text()
        clave = self.obj("txt_clave").get_text()

        datos_conexion = [alias, clave]
        conexion = conectar(datos_conexion)

        if conexion is not False:
            conexion.close()  # Finaliza la conexión
            self.entrar = True
            self.verificar_permisos(self.obj("ventana"), datos_conexion)
        else:
            self.obj("barraestado").push(0, "Alias o Contraseña equivocada.")
            self.obj("txt_clave").set_text("")
            self.obj("txt_clave").grab_focus()

    def on_btn_salir_clicked(self, objeto):
        if not self.entrar:
            main_quit()  # Si no se obtuvo acceso
