#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date
from time import strftime
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op

class asistencias:

    def __init__(self, datos):
        self.datos_conexion = datos

        arch = Op.archivo("rrhh_asistencias")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)
        self.obj("ventana").set_title("Asistencias")

        self.obj("btn_nuevo").set_tooltip_text("Presione este botón para registrar una Nueva Asistencia")
        self.obj("btn_guardar").set_tooltip_text("Presione este botón para Guardar la Asistencia")
        self.obj("btn_cancelar").set_tooltip_text("Presione este botón para Cancelar la operación")
        self.obj("btn_salir").set_tooltip_text("Presione este botón para Salir de la ventana")

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_00_2").set_max_length(12)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_02").set_max_length(100)

        self.obj("txt_00").set_tooltip_text(Mens.usar_boton("el Empleado cuyo Reposo es registrado"))
        self.obj("txt_00_1").set_tooltip_text("Nombre y Apellido del Empleado")
        self.obj("txt_00_2").set_tooltip_text("Ingrese el Nro. de Documento del Empleado")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Contrato del Empleado seleccionado"))
        self.obj("txt_01_1").set_tooltip_text("Cargo del Empleado dentro de la Empresa")
        self.obj("txt_02").set_tooltip_text("Ingrese una Observación")

        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_00"), self.obj("txt_00_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_00_2"), self.obj("cmb_tipo_doc")
        self.txt_cod_cnt, self.txt_crg_cnt = self.obj("txt_01"), self.obj("txt_01_1")

        self.idPersona, self.borrar_contrato, self.idTipoDoc = None, True, -1
        Op.combos_config(self.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")

        arch.connect_signals(self)

        self.limpiarcampos()
        self.obj("entrada").set_active(True)

        self.on_btn_nuevo_clicked(0)
        self.obj("ventana").show()

    def on_btn_nuevo_clicked(self, objeto):
        self.estadoedicion(True)
        self.obj("cmb_tipo_doc").set_active(0)
        self.obj("txt_01").grab_focus()  # Contrato
        self.obj("btn_guardar").set_sensitive(False)
        self.obj("lbl_fecha").set_text(Cal.mysql_fecha(date.today()))
        self.obj("lbl_hora").set_text(strftime('%H:%M:%S'))

    def on_btn_guardar_clicked(self, objeto):
        cont = self.obj("txt_01").get_text()
        obs = self.obj("txt_02").get_text()

        obs = "NULL" if len(obs) == 0 else "'" + obs + "'"
        est = "1" if self.obj("entrada").get_active() else "0"

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.datos_conexion)

        Op.insertar(conexion, "asistencias",
            cont + ", " + est + ", " + self.puntual + ", " + obs)

        conexion.commit()
        conexion.close()  # Finaliza la conexión

        self.on_btn_cancelar_clicked(0)

    def on_btn_cancelar_clicked(self, objeto):
        self.estadoedicion(False)
        self.limpiarcampos()

    def on_btn_salir_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_empleado_clicked(self, objeto):
        from clases.llamadas import empleados
        empleados(self.datos_conexion, self)

    def on_btn_contrato_clicked(self, objeto):
        condicion = None if len(self.obj("txt_00").get_text()) == 0 \
        else "idEmpleado = " + self.obj("txt_00").get_text()

        from clases.llamadas import contratos
        contratos(self.datos_conexion, self, condicion)

    def on_cmb_tipo_doc_changed(self, objeto):
        model = self.obj("cmb_tipo_doc").get_model()
        active = self.obj("cmb_tipo_doc").get_active()

        if active > -1:
            self.idTipoDoc = model[active][0]
            self.focus_out_event(self.obj("txt_00_2"), 0)  # Nro. Documento
        else:
            self.obj("barraestado").push(0, "No existen registros de Tipos de Documentos en el Sistema.")

    def on_rad_toggled(self, objeto):
        if len(self.obj("txt_01").get_text()) > 0 and len(self.obj("txt_01_1").get_text()) > 0:
            self.buscar_horarios()  # Solo cuando el contrato ya ha sido seleccionado

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Cód. de Empleado", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Nro. de Contrato", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar").set_sensitive(estado)

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK: # Tecla CTRL en combinación
            if evento.keyval == 65293: # Presionando Enter
                if objeto == self.obj("txt_00"):
                    self.on_btn_funcionario_clicked(0)
                elif objeto == self.obj("txt_01"):
                    self.on_btn_contrato_clicked(0)
        elif evento.keyval == 65293: # Presionando Enter
            self.focus_out_event(objeto,0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_00"), self.obj("txt_00_2")):
            tipo = "Empleado"
        elif objeto == self.obj("txt_01"):
            tipo = "Contrato"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un " + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")

            if objeto == self.obj("txt_00"):  # Código de Empleado
                self.idPersona == None
                self.obj("txt_00_1").set_text("")
                self.obj("txt_00_2").set_text("")

            elif objeto == self.obj("txt_00_2") \
            and len(self.obj("txt_00").get_text()) == 0:  # Nro. Documento de Empleado
                self.obj("txt_00_1").set_text("")

            elif objeto == self.obj("txt_01"):  # Número de Contrato
                self.obj("txt_01_1").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                if Op.comprobar_numero(int, objeto, "Cód. de Empleado", self.obj("barraestado")):
                    self.buscar_empleados(objeto, "idPersona", valor, "Cód. de Empleado")

            elif objeto == self.obj("txt_00_2"):
                self.buscar_empleados(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + str(self.idTipoDoc) + "'", "Nro. de Documento")

            elif objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Nro. de Contrato", self.obj("barraestado")):
                    conexion = Op.conectar(self.datos_conexion)
                    cursor = Op.consultar(conexion, "idEmpleado, Cargo, Vigente",
                        "contratos_s", " WHERE NroContrato = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        if datos[0][2] == 1:
                            self.obj("txt_00").set_text(str(datos[0][0]))
                            self.obj("txt_01_1").set_text(datos[0][1])

                            self.obj("barraestado").push(0, "")
                            self.borrar_contrato = False
                            self.focus_out_event(self.obj("txt_00"), 0)  # idEmpleado
                            self.buscar_horarios()
                        else:
                            objeto.grab_focus()
                            self.estadoguardar(False)
                            self.obj("barraestado").push(0, "El Contrato seleccionado ya no se encuentra vigente.")
                    else:
                        objeto.grab_focus()
                        self.estadoguardar(False)
                        self.obj("barraestado").push(0, "El Nro. de Contrato no es válido.")

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

                self.obj("txt_00").set_text(self.idPersona)
                self.obj("txt_00_1").set_text(datos[0][1])
                self.obj("txt_00_2").set_text(datos[0][2])

                # Asignación de Tipo de Documento en Combo
                model, i = self.obj("cmb_tipo_doc").get_model(), 0
                while model[i][0] != datos[0][3]: i += 1
                self.obj("cmb_tipo_doc").set_active(i)

                if self.borrar_contrato:  # Debe indicarse otro Contrato
                    self.obj("txt_01").set_text("")
                    self.obj("txt_01_1").set_text("")
                else:
                    self.borrar_contrato = True

                self.obj("barraestado").push(0, "")
                self.verificacion(0)

        else:
            self.idPersona = valor
            self.estadoguardar(False)
            objeto.grab_focus()
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_00_2") if objeto == self.obj("txt_00") else self.obj("txt_00")
            otro.set_text("")
            self.obj("txt_00_1").set_text("")

    def estadoedicion(self, estado):
        self.obj("btn_nuevo").set_sensitive(not estado)
        self.obj("btn_guardar").set_sensitive(estado)
        self.obj("btn_cancelar").set_sensitive(estado)
        self.obj("btn_salir").set_sensitive(not estado)

        self.obj("btn_empleado").set_sensitive(estado)
        self.obj("btn_contrato").set_sensitive(estado)

        self.obj("txt_00").set_sensitive(estado)
        self.obj("txt_00_1").set_sensitive(estado)
        self.obj("txt_00_2").set_sensitive(estado)
        self.obj("cmb_tipo_doc").set_sensitive(estado)
        self.obj("txt_01").set_sensitive(estado)
        self.obj("txt_01_1").set_sensitive(estado)
        self.obj("txt_02").set_sensitive(estado)
        self.obj("entrada").set_sensitive(estado)
        self.obj("salida").set_sensitive(estado)

    def limpiarcampos(self):
        self.obj("txt_00").set_text("")
        self.obj("txt_00_1").set_text("")
        self.obj("txt_00_2").set_text("")
        self.obj("cmb_tipo_doc").set_active(-1)
        self.obj("txt_01").set_text("")
        self.obj("txt_01_1").set_text("")
        self.obj("txt_02").set_text("")

    def buscar_horarios(self):
        dia = Cal.dia_hoy_letras()
        self.puntual = "1"

        # Búsqueda de Horarios del Contrato
        nrocontrato = self.obj("txt_01").get_text()
        est = "HoraEntrada" if self.obj("entrada").get_active() else "HoraSalida"

        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, est, "horarios_s", " WHERE " +
            "NroContrato = " + nrocontrato + " AND Dia = '" + dia + "'" +
            " ORDER BY " + est)
        horas = cursor.fetchall()
        cant = cursor.rowcount

        if cant == 0:
            self.obj("barraestado").push(0, "No ha sido encontrado el Horario para este Día y Contrato.")
        else:
            est = "1" if self.obj("entrada").get_active() else "0"
            observacion = ""

            # Obtiene los registros de Asistencias del Empleado
            cursor = Op.consultar(conexion, "Hora", "asistencias_s",
                "WHERE NroContrato = " + nrocontrato + " " +
                "AND Fecha = DATE_FORMAT(NOW(), '%Y-%m-%d') " +
                "AND Entrada = " + est + " ORDER BY Hora")
            asist = cursor.fetchall()
            cant = cursor.rowcount

            if self.obj("entrada").get_active():
                try:
                    hora_ent = str(horas[cant][0])

                    # Incluye un periodo de tolerancia de 5 minutos
                    if Op.compara_fechas(self.datos_conexion,
                    "ADDTIME('" + hora_ent + "', '00:05:00')", ">", "DATE_FORMAT(NOW(), '%T'"):
                        observacion = "Llegada Puntual (" + hora_ent + ")"
                    else:
                        observacion = "Llegada Tardía (" + hora_ent + ")"
                        self.puntual = "0"
                except:
                    self.obj("salida").set_active(True)

            else: # Salida
                try:
                    hora_sal = str(horas[cant][0])

                    if Op.compara_fechas(self.datos_conexion,
                    "'" + hora_sal + "'", ">", "DATE_FORMAT(NOW(), '%T'"):
                        observacion = "Salida Temprana (" + hora_sal + ")"
                        self.puntual = "0"
                    else:
                        observacion = "Salida Puntual (" + hora_sal + ")"
                except:
                    self.obj("barraestado").push(0, "Tanto las Entradas como las Salidas " + \
                    "para este Contrato por este Día ya han sido registradas.")

            conexion.close()  # Finaliza la conexión
            self.obj("txt_02").set_text(observacion)
