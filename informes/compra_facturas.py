#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import popen

from gi.repository.Gtk import CellRendererText
from gi.repository.Gtk import ListStore

from reportlab.platypus import Paragraph as Par
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Table

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm

from clases.dialogos import dialogo_guardar
from clases.fechas import cadena_fecha
from clases.fechas import calendario
from clases.fechas import mysql_fecha
from clases.mensajes import error_permiso_archivo

from clases.listado import cabecera_style
from clases.listado import parrafo_bodytext
from clases.listado import tabla_celda_centrado
from clases.listado import tabla_celda_just_derecho
from clases.listado import tabla_celda_just_izquierdo
from clases.listado import tabla_celda_titulo
from clases.listado import tabla_style

from clases.operaciones import archivo
from clases.operaciones import celdas
from clases.operaciones import columnas
from clases.operaciones import conectar
from clases.operaciones import consultar
from clases.operaciones import combos_config
from clases.operaciones import objetos_set_sensitive


class informe_compra_facturas:

    def __init__(self, datos):
        self.datos_conexion = datos

        arch = archivo("informe_compra_facturas")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_title("Informes de Facturas de Compra")
        self.obj("ventana").set_modal(True)

        self.idTipoDoc = self.idTipoFact = self.idTotal = -1
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_prov_01"), self.obj("txt_prov_02")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_prov_03"), self.obj("cmb_prov_doc")

        self.obj("label8").set_visible(False)
        self.obj("txt_total_fin").set_visible(False)

        self.config_combo_total()
        combos_config(self.datos_conexion, self.obj("cmb_prov_doc"), "tipodocumentos", "idTipoDocumento")
        combos_config(self.datos_conexion, self.obj("cmb_tipo_fact"), "tipofacturas", "idTipoFactura")
        arch.connect_signals(self)

        self.on_chk_toggled(0)
        self.obj("ventana").show()

    def on_btn_aceptar_clicked(self, objeto):
        from informes.informes import informe_vista
        informe_vista(self, "Facturas de Compra")

    def on_btn_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_proveedor_clicked(self, objeto):
        from clases.llamadas import personas
        personas(self.datos_conexion, self, "idRolPersona = 3")

    def on_btn_fecha_ini_clicked(self, objeto):
        self.obj("txt_fecha_ini").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = calendario()

        if lista is not False:
            self.fecha_ini = lista[1]
            self.obj("txt_fecha_ini").set_text(lista[0])

    def on_btn_limpiar_fecha_ini_clicked(self, objeto):
        self.obj("txt_fecha_ini").set_text("")
        self.obj("txt_fecha_ini").grab_focus()

    def on_btn_fecha_fin_clicked(self, objeto):
        self.obj("txt_fecha_fin").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = calendario()

        if lista is not False:
            self.fecha_fin = lista[1]
            self.obj("txt_fecha_fin").set_text(lista[0])

    def on_btn_limpiar_fecha_fin_clicked(self, objeto):
        self.obj("txt_fecha_fin").set_text("")
        self.obj("txt_fecha_fin").grab_focus()

    def on_cmb_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if objeto == self.obj("cmb_prov_doc"):
            self.idTipoDoc = model[active][0]

        elif objeto == self.obj("cmb_tipo_fact"):
            self.idTipoFact = model[active][0]

        elif objeto == self.obj("cmb_total"):
            self.idTotal = model[active][0]

            if self.idTotal == 1:
                self.obj("label8").set_visible(True)
                self.obj("txt_total_fin").set_visible(True)
            else:
                self.obj("label8").set_visible(False)
                self.obj("txt_total_fin").set_visible(False)

    def on_chk_toggled(self, objeto):
        # Proveedor
        lista = [self.obj("txt_prov_01"), self.obj("txt_prov_02"), self.obj("btn_proveedor"),
            self.obj("txt_prov_03"), self.obj("cmb_prov_doc")]

        if self.obj("chk_01").get_active():
            objetos_set_sensitive(lista, True)
            self.obj("cmb_prov_doc").set_active(0)
            self.obj("txt_prov_01").grab_focus()
        else:
            objetos_set_sensitive(lista, False)
            self.obj("cmb_prov_doc").set_active(-1)
            self.obj("txt_prov_01").set_text("")
            self.obj("txt_prov_02").set_text("")
            self.obj("txt_prov_03").set_text("")

        # Tipo de Factura
        lista = [self.obj("cmb_tipo_fact")]

        if self.obj("chk_02").get_active():
            objetos_set_sensitive(lista, True)
            self.obj("cmb_tipo_fact").set_active(0)
        else:
            objetos_set_sensitive(lista, False)
            self.obj("cmb_tipo_fact").set_active(-1)

        # Fecha de Expedicion
        lista = [self.obj("txt_fecha_ini"), self.obj("btn_fecha_ini"),
            self.obj("btn_limpiar_fecha_ini"), self.obj("txt_fecha_fin"),
            self.obj("btn_fecha_fin"), self.obj("btn_limpiar_fecha_fin")]

        if self.obj("chk_03").get_active():
            objetos_set_sensitive(lista, True)
            self.obj("txt_fecha_ini").grab_focus()
        else:
            objetos_set_sensitive(lista, False)
            self.obj("txt_fecha_ini").set_text("")
            self.obj("txt_fecha_fin").set_text("")

        # Total
        lista = [self.obj("cmb_total"), self.obj("txt_total_ini"),
            self.obj("txt_total_fin")]

        if self.obj("chk_04").get_active():
            objetos_set_sensitive(lista, True)
            self.obj("cmb_total").set_active(0)
            self.obj("txt_total_ini").grab_focus()
        else:
            objetos_set_sensitive(lista, False)
            self.obj("cmb_total").set_active(-1)
            self.obj("txt_total_ini").set_value(0)
            self.obj("txt_total_fin").set_value(0)

    def config_combo_total(self):
        lista = ListStore(int, str)
        self.obj("cmb_total").set_model(lista)

        cell = CellRendererText()
        self.obj("cmb_total").pack_start(cell, True)
        self.obj("cmb_total").add_attribute(cell, 'text', 1)

        lista.append([1, "Entre"])
        lista.append([2, "Mayor que..."])
        lista.append([3, "Mayor o igual que..."])
        lista.append([4, "Menor que..."])
        lista.append([5, "Menor o igual que..."])

##### Ventana de Vista Previa ##########################################

    def config_grilla(self, grilla):
        celda0 = celdas(0.5)
        celda1 = celdas(0.0)
        celda2 = celdas(1.0)

        col0 = columnas("Nro. Timbrado", celda0, 0, True, 100, 200)
        col0.set_sort_column_id(0)
        col1 = columnas("Nro. Factura", celda0, 1, True, 100, 200)
        col1.set_sort_column_id(1)
        col2 = columnas("Fecha de Expedición", celda0, 2, True, 150, 200)
        col2.set_sort_column_id(2)
        col3 = columnas("Tipo de Factura", celda0, 3, True, 100, 150)
        col3.set_sort_column_id(3)
        col4 = columnas("Nro. Doc. Prov.", celda0, 4, True, 100, 150)
        col4.set_sort_column_id(4)
        col5 = columnas("Proveedor", celda1, 5, True, 100, 250)
        col5.set_sort_column_id(5)
        col6 = columnas("Total", celda2, 6, True, 100, 150)
        col6.set_sort_column_id(6)

        lista = [col0, col1, col2, col3, col4, col5, col6]
        for columna in lista:
            grilla.append_column(columna)

        grilla.set_rules_hint(True)
        grilla.set_search_column(1)
        grilla.set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, str, str, str, str, float)
        grilla.set_model(lista)
        grilla.show()

    def cargar_grilla(self, grilla, barraestado):
        condicion = ""

        if self.obj("chk_01").get_active():
            condicion += "idProveedor = " + self.obj("txt_prov_01").get_text()

        if self.obj("chk_02").get_active():
            if len(condicion) > 0:
                condicion += " AND "
            condicion += "idTipoFactura = " + str(self.idTipoFact)

        if self.obj("chk_03").get_active():
            if len(condicion) > 0:
                condicion += " AND "
            condicion += "Fecha BETWEEN '" + self.fecha_ini + "'" + \
                " AND '" + self.fecha_fin + "'"

        if self.obj("chk_04").get_active():
            if len(condicion) > 0:
                condicion += " AND "
            condicion += "Total "
            total = str(self.obj("txt_total_ini").get_value())

            if self.idTotal == 1:  # Entre
                condicion += "> " + total + \
                " AND Total < " + str(self.obj("txt_total_fin").get_value())
            elif self.idTotal == 2:  # Mayor que
                condicion += "> " + total
            elif self.idTotal == 3:  # Mayor o igual que
                condicion += ">= " + total
            elif self.idTotal == 4:  # Menor que
                condicion += "< " + total
            elif self.idTotal == 5:  # Menor o igual que
                condicion += "<= " + total

        if self.obj("rad_confirmadas").get_active():
            if len(condicion) > 0:
                condicion += " AND "
            condicion += "Confirmado = 1"

        # Obtener datos de Facturas de Compra
        conexion = conectar(self.datos_conexion)
        cursor = consultar(conexion, "NroTimbrado, NroFactura, " +
            "Fecha, TipoFactura, NroDocProveedor, RazonSocial, Total",
            "facturacompras_s", " WHERE " + condicion)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        lista = grilla.get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], mysql_fecha(datos[i][2]),
                datos[i][3], datos[i][4], datos[i][5], datos[i][6]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        barraestado.push(0, cant)

    def preparar_pdf(self, grilla):
        datos = grilla.get_model()
        cant = len(datos)

        ubicacion_archivo = dialogo_guardar("Facturas de Compra")

        if ubicacion_archivo is not None:
            # Si no tiene la terminación .pdf se le agrega
            if ubicacion_archivo[-4:].lower() != ".pdf":
                ubicacion_archivo += ".pdf"

            story = []
            cabecera = cabecera_style()
            parrafo = parrafo_bodytext()
            head = tabla_celda_titulo()
            body_ce = tabla_celda_centrado()
            body_iz = tabla_celda_just_izquierdo()
            body_de = tabla_celda_just_derecho()

            story.append(Par("Facturas de Compra", cabecera))
            story.append(Spacer(0, 20))

            if self.obj("chk_01").get_active():  # Proveedor
                story.append(Par("Facturas del Proveedor <b>" +
                self.obj("txt_prov_02").get_text() + "</b>", parrafo))

            if self.obj("chk_02").get_active():  # Tipo de Factura
                model = self.obj("cmb_tipo_fact").get_model()
                active = self.obj("cmb_tipo_fact").get_active()
                story.append(Par("<b>" + model[active][1] + "</b>", parrafo))

            if self.obj("chk_03").get_active():  # Fecha
                story.append(Par("Facturas expedidas entre el " +
                "<b>" + cadena_fecha(self.fecha_ini) + "</b> y el " +
                "<b>" + cadena_fecha(self.fecha_fin) + "</b>", parrafo))

            if self.obj("chk_04").get_active():  # Total
                if self.idTotal == 1:  # Entre
                    tipo, segundo = "entre", " y <b>" + \
                    str(self.obj("txt_total_fin").get_value()) + "</b>"
                elif self.idTotal == 2:  # Mayor que
                    tipo, segundo = "mayor que", ""
                elif self.idTotal == 3:  # Mayor o igual que
                    tipo, segundo = "mayor o igual que", ""
                elif self.idTotal == 4:  # Menor que
                    tipo, segundo = "menor que", ""
                elif self.idTotal == 5:  # Menor o igual que
                    tipo, segundo = "menor o igual que", ""
                story.append(Par("Facturas expedidas por un Monto " + tipo + " <b>" +
                str(self.obj("txt_total_ini").get_value()) + " </b>" + segundo, parrafo))

            story.append(Spacer(0, 20))

            lista = [[Par("Nro. Timbrado", head), Par("Nro. Factura", head),
                Par("Fecha", head), Par("Tipo de Factura", head),
                Par("Nro. Doc. Prov.", head), Par("Proveedor", head), Par("Total", head)]]

            for i in range(0, cant):
                lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][1], body_ce),
                    Par(datos[i][2], body_ce), Par(datos[i][3], body_ce), Par(datos[i][4], body_ce),
                    Par(datos[i][5], body_iz), Par(str(datos[i][6]), body_de)])

            tabla = Table(lista, [100, 100, 150, 100, 100, 125, 75])
            tabla = tabla_style(tabla)
            story.append(tabla)

            doc = SimpleDocTemplate(
                ubicacion_archivo,
                pagesize=landscape(A4),
                leftMargin=3 * cm,  # Margen Izquierdo
                rightMargin=3 * cm,  # Margen Derecho
                topMargin=2.5 * cm,  # Margen Superior
                bottomMargin=2.5 * cm,  # Margen Inferior
                allowSplitting=1,
                title="Facturas de Compra",
                author="Sistema Distribuidora"
            )

            try:  # Generar Archivo
                doc.build(story)
                popen(ubicacion_archivo)
            except PermissionError as e:
                error_permiso_archivo(str(e))
