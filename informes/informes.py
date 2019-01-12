#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from clases.operaciones import archivo


class informe_vista:

    def __init__(self, v_or, titulo):
        self.origen = v_or

        arch = archivo("informes")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(750, 500)
        self.obj("ventana").set_title("Informes de " + titulo)
        self.obj("ventana").set_modal(True)
        self.obj("label").set_text(titulo)

        self.origen.config_grilla(self.obj("grilla"))
        self.origen.cargar_grilla(self.obj("grilla"), self.obj("barraestado"))

        #if len(self.obj("grilla").get_model()) == 0:  # No hay registros
        #    self.obj("btn_pdf_tab").set_sensitive(False)

        arch.connect_signals(self)
        self.obj("ventana").show()

    def on_btn_modificar_tab_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_pdf_tab_clicked(self, objeto):
        self.origen.preparar_pdf(self.obj("grilla"))

    def on_btn_cancelar_tab_clicked(self, objeto):
        self.origen.obj("ventana").destroy()
        self.obj("ventana").destroy()
