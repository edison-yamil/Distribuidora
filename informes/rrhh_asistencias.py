#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import popen

from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType

from clases.dialogos import dialogo_guardar
from clases.mensajes import error_permiso_archivo

from clases.listado import listado
from clases.listado import cabecera_style
from clases.listado import tabla_celda_centrado
from clases.listado import tabla_celda_just_izquierdo
from clases.listado import tabla_celda_just_derecho
from clases.listado import tabla_celda_titulo
from clases.listado import tabla_style

from reportlab.platypus import Paragraph as Par
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Table

from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import cm

from clases import fechas as Cal
from clases import operaciones as Op


class informe_asistencias:

    def __init__(self, datos):
        self.datos_conexion = datos

        arch = Op.archivo("informe_asistencias")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)
        self.obj("ventana").set_title("Informes de Asistencias")

        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_01_2"), self.obj("cmb_tipo_doc")
        self.txt_cod_cnt, self.txt_crg_cnt = self.obj("txt_02"), self.obj("txt_02_1")

        self.idPersona, self.borrar_contrato, self.idTipoDoc = None, True, -1
        Op.combos_config(self.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")

        arch.connect_signals(self)

        self.desactiva_empleado()
        self.obj("btn_aceptar").set_sensitive(False)
        self.obj("ventana").show()

    def on_btn_aceptar_clicked(self, objeto):
        from informes.informes import informe_vista
        informe_vista(self, "Asistencias")

    def on_btn_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_empleado_clicked(self, objeto):
        from clases.llamadas import empleados
        empleados(self.datos_conexion, self)

    def on_btn_contrato_clicked(self, objeto):
        condicion = None if len(self.obj("txt_01").get_text()) == 0 \
        else "idEmpleado = " + self.obj("txt_01").get_text()

        from clases.llamadas import contratos
        contratos(self.datos_conexion, self, condicion)

    def on_btn_fecha_ini_clicked(self, objeto):
        self.obj("txt_03").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_03").set_text(lista[0])
            self.fechaini = lista[1]

    def on_btn_fecha_fin_clicked(self, objeto):
        self.obj("txt_04").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_04").set_text(lista[0])
            self.fechafin = lista[1]

    def verificacion(self, objeto):
        if len(self.obj("txt_03").get_text()) == 0 or len(self.obj("txt_04").get_text()) == 0:
            estado = False
        else:
            if self.obj("chk_empleado").get_active():
                if len(self.obj("txt_01").get_text()) == 0 or len(self.obj("txt_01_2").get_text()) == 0 \
                or len(self.obj("txt_02").get_text()) == 0 or self.idTipoDoc == -1:
                    estado = False
                else:
                    if Op.comprobar_numero(int, self.obj("txt_01"), "Cód. de Empleado", self.obj("barraestado")) \
                    and Op.comprobar_numero(int, self.obj("txt_02"), "Nro. de Contrato", self.obj("barraestado")):
                        estado = True
                    else:
                        estado = False
            else:
                estado = True

        self.obj("btn_aceptar").set_sensitive(estado)

    def on_cmb_tipo_doc_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            self.idTipoDoc = model[active][0]
            self.focus_out_event(self.obj("txt_01_2"), 0)  # Nro. Documento
        else:
            if self.obj("chk_empleado").get_active():
                self.obj("barraestado").push(0, "No existen registros " +
                    "de Tipos de Documentos en el Sistema.")

    def on_chk_empleado_toggled(self, objeto):
        if not self.obj("chk_empleado").get_active():
            self.desactiva_empleado()
        else:
            self.obj("cmb_tipo_doc").set_active(0)
            self.obj("vbox1").set_sensitive(True)
        self.verificacion(0)

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
                    self.on_btn_empleado_clicked(0)
                elif objeto == self.obj("txt_02"):
                    self.on_btn_contrato_clicked(0)
                elif objeto == self.obj("txt_03"):
                    self.on_btn_fecha_ini_clicked(0)
                elif objeto == self.obj("txt_04"):
                    self.on_btn_fecha_fin_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
            tipo = "un Empleado"
        elif objeto == self.obj("txt_02"):
            tipo = "un Contrato"
        elif objeto == self.obj("txt_03"):
            tipo = "la Fecha de Inicio del Periodo a examinar"
        elif objeto == self.obj("txt_04"):
            tipo = "la Fecha de Finalización del Periodo a examinar"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar " + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")

            if objeto == self.obj("txt_01"):  # Código de Empleado
                self.idPersona == None
                self.obj("txt_01_1").set_text("")
                self.obj("txt_01_2").set_text("")

            elif objeto == self.obj("txt_01_2") \
            and len(self.obj("txt_01").get_text()) == 0:  # Nro. Documento de Empleado
                self.obj("txt_01_1").set_text("")

            elif objeto == self.obj("txt_02"):  # Número de Contrato
                self.obj("txt_02_1").set_text("")
        else:
            if objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Empleado", self.obj("barraestado")):
                    self.buscar_empleados(objeto, "idPersona", valor, "Cód. de Empleado")

            elif objeto == self.obj("txt_01_2"):
                self.buscar_empleados(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + str(self.idTipoDoc) + "'", "Nro. de Documento")

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Nro. de Contrato", self.obj("barraestado")):
                    conexion = Op.conectar(self.datos_conexion)
                    cursor = Op.consultar(conexion, "idEmpleado, Cargo, Vigente",
                        "contratos_s", " WHERE NroContrato = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        if datos[0][2] == 1:
                            self.obj("txt_01").set_text(str(datos[0][0]))
                            self.obj("txt_02_1").set_text(datos[0][1])
                            self.obj("barraestado").push(0, "")

                            self.borrar_contrato = False
                            self.focus_out_event(self.obj("txt_01"), 0)
                        else:
                            objeto.grab_focus()
                            self.obj("btn_aceptar").set_sensitive(False)
                            self.obj("barraestado").push(0, "El Contrato seleccionado ya no se encuentra vigente.")
                    else:
                        objeto.grab_focus()
                        self.obj("btn_aceptar").set_sensitive(False)
                        self.obj("barraestado").push(0, "El Nro. de Contrato no es válido.")

            elif objeto == self.obj("txt_03"):
                if Op.compara_fechas(self.datos_conexion, "'" + self.fechaini + "'", ">", "NOW()"):
                    self.obj("btn_aceptar").set_sensitive(False)
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "La Fecha de Inicio del Periodo a examinar NO puede estar en el Futuro.")
                else:
                    self.comparar_fechas_periodo()

            elif objeto == self.obj("txt_04"):
                if Op.compara_fechas(self.datos_conexion, "'" + self.fechafin + "'", ">", "NOW()"):
                    self.obj("btn_aceptar").set_sensitive(False)
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "La Fecha de Finalización del Periodo a examinar NO puede estar en el Futuro.")
                else:
                    self.comparar_fechas_periodo()

    def buscar_empleados(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "idPersona, RazonSocial, " +
            "NroDocumento, idTipoDocumento", "personas_s",
            " WHERE " + campo + " = " + valor + " AND Empleado = 1")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            # Si aún no se ha seleccionado o es diferente del anterior
            if self.idPersona is None or self.idPersona != str(datos[0][0]):
                self.idPersona = str(datos[0][0])

                self.obj("txt_01").set_text(self.idPersona)
                self.obj("txt_01_1").set_text(datos[0][1])
                self.obj("txt_01_2").set_text(datos[0][2])

                # Asignación de Tipo de Documento en Combo
                model, i = self.obj("cmb_tipo_doc").get_model(), 0
                while model[i][0] != datos[0][3]: i += 1
                self.obj("cmb_tipo_doc").set_active(i)

                if self.borrar_contrato:  # Debe indicarse otro Contrato
                    self.obj("txt_02").set_text("")
                    self.obj("txt_02_1").set_text("")
                else:
                    self.borrar_contrato = True

                self.obj("barraestado").push(0, "")
                self.verificacion(0)

        else:
            self.idPersona = valor
            self.obj("btn_aceptar").set_sensitive(False)
            objeto.grab_focus()
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_01_2") if objeto == self.obj("txt_01") else self.obj("txt_01")
            otro.set_text("")
            self.obj("txt_01_1").set_text("")

    def comparar_fechas_periodo(self):
        if len(self.obj("txt_03").get_text()) > 0 and len(self.obj("txt_04").get_text()) > 0:
            if Op.compara_fechas(self.datos_conexion,
            "'" + self.fechaini + "'", ">", "'" + self.fechafin + "'"):
                self.obj("btn_aceptar").set_sensitive(False)
                objeto.grab_focus()
                self.obj("barraestado").push(0, "La Fecha de Inicio del Periodo a examinar NO puede ser posterior a la de Finalización.")
            else:
                self.obj("barraestado").push(0, "")

    def desactiva_empleado(self):
        self.obj("txt_01").set_text("")
        self.obj("txt_01_1").set_text("")
        self.obj("txt_01_2").set_text("")
        self.obj("txt_02").set_text("")
        self.obj("txt_02_1").set_text("")

        self.obj("cmb_tipo_doc").set_active(-1)
        self.obj("vbox1").set_sensitive(False)

##### Ventana de Vista Previa ##########################################

    def config_grilla(self, grilla):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)

        col0 = Op.columnas("Nro. Contrato", celda0, 0, True, 100, 200)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Cód. Empleado", celda0, 1, True, 100, 200)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Tipo Doc. Identidad", celda0, 2, True, 100, 200)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Nro. Doc. Identidad", celda0, 3, True, 100, 200)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Nombre y Apellido", celda1, 4, True, 200)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Cargo", celda1, 5, True, 150)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Fecha", celda0, 6, True, 200)
        col6.set_sort_column_id(12)  # Para ordenarse usa la fila 12
        col7 = Op.columnas("Hora", celda0, 7, True, 100, 200)
        col7.set_sort_column_id(7)
        col8 = Op.columnas("Estado", celda0, 8, True, 100, 200)
        col8.set_sort_column_id(8)
        col9 = Op.columnas("Puntualidad", celda0, 9, True, 100, 200)
        col9.set_sort_column_id(9)
        col10 = Op.columnas("Observaciones", celda1, 10, True, 200)
        col10.set_sort_column_id(10)
        col11 = Op.columnas("Usuario Responsable", celda1, 11, True, 100, 200)
        col11.set_sort_column_id(11)

        lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11]
        for columna in lista:
            grilla.append_column(columna)

        grilla.set_rules_hint(True)
        grilla.set_search_column(0)
        grilla.set_property('enable-grid-lines', 3)

        lista = ListStore(str, str, str, str, str, str, str, str, str, str, str, str, str)
        grilla.set_model(lista)
        grilla.show()

    def cargar_grilla(self, grilla, barraestado):
        opcion = "" if not self.obj("chk_empleado").get_active() else \
            " AND NroContrato = " + self.obj("txt_02").get_text()

        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "NroContrato, idEmpleado, " +
            "idTipoDocumento, NroDocumento, NombreApellido, Cargo, " +
            "Fecha, Hora, Entrada, Puntual, Observaciones, Alias",
            "asistencias_s", " WHERE Fecha BETWEEN '" + self.fechaini + "'" +
            " AND '" + self.fechafin + "'" + opcion + " ORDER BY Fecha, Hora")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        lista = grilla.get_model()
        lista.clear()

        for i in range(0, cant):
            estado = "Entrada" if datos[i][8] == 1 else "Salida"
            puntual = "Puntual" if datos[i][9] == 1 else ""
            obs = "" if datos[i][10] is None else datos[i][10]

            lista.append([str(datos[i][0]), str(datos[i][1]), datos[i][2],
                datos[i][3], datos[i][4], datos[i][5], Cal.mysql_fecha(datos[i][6]),
                str(datos[i][7]), estado, puntual, obs, datos[i][11],
                str(datos[i][6])])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        barraestado.push(0, cant)

    def preparar_pdf(self, grilla):
        head = tabla_celda_titulo()
        body_ce = tabla_celda_centrado(9)
        body_iz = tabla_celda_just_izquierdo(9)

        datos = grilla.get_model()
        cant = len(datos)

        if self.obj("chk_empleado").get_active():  # De un empleado específico
            encabezado = [self.obj("txt_01_1").get_text(), self.obj("txt_01_2").get_text(),
                self.obj("txt_02").get_text(), self.obj("txt_02_1").get_text()]

            lista = [[Par("Fecha", head), Par("Hora", head), Par("", head),
                Par("Observaciones", head), Par("Usuario", head)]]

            for i in range(0, cant):
                lista.append([Par(datos[i][6], body_iz), Par(datos[i][7], body_ce),
                    Par(datos[i][8], body_ce), Par(datos[i][10], body_iz),
                    Par(datos[i][11], body_iz)])

            genera_asistencia_empleado(encabezado, lista)

        else:
            lista = [[Par("Nro. Contrato", head), Par("Nro. C.I.", head),
                Par("Empleado", head), Par("Cargo", head),
                Par("Fecha", head), Par("Hora", head), Par("", head),
                Par("Observaciones", head), Par("Usuario", head)]]

            for i in range(0, cant):
                lista.append([Par(datos[i][0], body_ce), Par(datos[i][3], body_ce),
                    Par(datos[i][4], body_iz), Par(datos[i][5], body_iz),
                    Par(datos[i][6], body_iz), Par(datos[i][7], body_ce),
                    Par(datos[i][8], body_ce), Par(datos[i][10], body_iz),
                    Par(datos[i][11], body_iz)])

            listado("Asistencias", lista, [70, 70, 145, 70, 100, 70, 50, 120, 70], landscape(A4))


def genera_asistencia_empleado(datos, datos_tabla):
    ubicacion_archivo = dialogo_guardar("Asistencias")

    if ubicacion_archivo is not None:
        # Si no tiene la terminación .pdf se le agrega
        if ubicacion_archivo[-4:].lower() != ".pdf":
            ubicacion_archivo += ".pdf"

        story = []
        cabecera = cabecera_style()
        texto = tabla_celda_just_izquierdo()
        titulo = tabla_celda_just_derecho()

        parrafo = Par("Registro de Asistencias", cabecera)
        story.append(parrafo)
        story.append(Spacer(0, 20))

        # Generar encabezado
        tabla = Table([
            [Par("<b>Empleado:</b>", titulo), Par(datos[0], texto)],
            [Par("<b>Nro. C.I.:</b>", titulo), Par(datos[1], texto)],
            [Par("<b>Nro. Contrato:</b>", titulo), Par(datos[2], texto)],
            [Par("<b>Cargo:</b>", titulo), Par(datos[3], texto)]
        ], [100, 300])
        tabla.setStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Alineación de la Primera Columna
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),  # Alineación de Otras Columnas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación Vertical de la Tabla
            ('TOPPADDING', (0, 0), (-1, -1), 1),  # Espacio Arriba
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Espacio Abajo
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Izquierda
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Derecha
        ])
        story.append(tabla)
        story.append(Spacer(0, 20))

        # Generar Tabla de Asistencias
        tabla = Table(datos_tabla, [125, 75, 50, 175, 75])
        tabla = tabla_style(tabla)
        story.append(tabla)

        doc = SimpleDocTemplate(
            ubicacion_archivo,
            pagesize=A4,  # Tamaño de Página (landscape(A4) hoja horizontal)
            leftMargin=3 * cm,  # Margen Izquierdo
            rightMargin=3 * cm,  # Margen Derecho
            topMargin=2.5 * cm,  # Margen Superior
            bottomMargin=2.5 * cm,  # Margen Inferior
            allowSplitting=1,
            title="Registro de Asistencias",
            author="Sistema Distribuidora"
        )

        try:  # Generar Archivo
            doc.build(story)
            popen(ubicacion_archivo)
        except PermissionError as e:
            error_permiso_archivo(str(e))
