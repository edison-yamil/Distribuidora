#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen):
        self.editando = edit
        self.nav = origen

        arch = Op.archivo("rrhh_vacaciones")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(800, 600)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Vacaciones")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_01_2").set_max_length(12)
        self.obj("txt_02").set_max_length(10)
        self.obj("txt_f_04").set_max_length(10)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código de la Vacación")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Empleado cuyas Vacaciones son registradas"))
        self.obj("txt_01_1").set_tooltip_text("Nombre y Apellido del Empleado")
        self.obj("txt_01_2").set_tooltip_text("Ingrese el Nro. de Documento del Empleado")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el Contrato del Empleado seleccionado"))
        self.obj("txt_02_1").set_tooltip_text("Cargo del Empleado dentro de la Empresa")
        self.obj("txt_03").set_tooltip_text("Fecha de Entrada del Empleado seleccionado")
        self.obj("txt_03_1").set_tooltip_text("Antigüedad del Empleado seleccionado")
        self.obj("txt_03_2").set_tooltip_text("Cantidad de Días de Vacaciones a que tiene derecho por Antigüedad")
        self.obj("txt_03_3").set_tooltip_text("Cantidad de Días Disponibles para ser Asignados")
        self.obj("txt_02").grab_focus()

        self.obj("txt_f_01").set_tooltip_text(Mens.usar_boton("la Fecha de Inicio de las Vacaciones del Empleado"))
        self.obj("txt_f_02").set_tooltip_text(Mens.usar_boton("la Fecha de Finalización de las Vacaciones del Empleado"))
        self.obj("txt_f_03").set_tooltip_text("Tiempo de Duración, en Días, de las Vacaciones del Empleado")
        self.obj("txt_f_04").set_tooltip_text(Mens.usar_boton("el Comprobante de Pago asociado a este Periodo de Vacaciones"))

        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_01_2"), self.obj("cmb_tipo_doc")
        self.txt_cod_cnt, self.txt_crg_cnt = self.obj("txt_02"), self.obj("txt_02_1")
        self.txt_cod_cmp = self.obj("txt_f_04")

        self.idPersona, self.borrar_contrato, self.idTipoDoc = None, not edit, -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")

        self.config_grilla_vacaciones()
        self.conexion = Op.conectar(self.nav.datos_conexion)

        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond_vac = str(seleccion.get_value(iterador, 0))
            self.cond_cont = str(seleccion.get_value(iterador, 1))
            idemp = str(seleccion.get_value(iterador, 2))
            cargo = seleccion.get_value(iterador, 8)

            self.obj("txt_00").set_text(self.cond_vac)
            self.obj("txt_01").set_text(idemp)
            self.obj("txt_02").set_text(self.cond_cont)
            self.obj("txt_02_1").set_text(cargo)

            self.focus_out_event(self.obj("txt_01"), 0)
            self.cargar_grilla_vacaciones()
            self.estadoguardar(True)
        else:
            self.obj("cmb_tipo_doc").set_active(0)
            self.estadoguardar(False)

        self.principal_guardado = True
        self.estadoedicion(False)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_principal_vacaciones()
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def on_btn_empleado_clicked(self, objeto):
        from clases.llamadas import empleados
        empleados(self.nav.datos_conexion, self)

    def on_btn_contrato_clicked(self, objeto):
        condicion = None if len(self.obj("txt_01").get_text()) == 0 \
        else "idEmpleado = " + self.obj("txt_01").get_text()

        from clases.llamadas import contratos
        contratos(self.nav.datos_conexion, self, condicion)

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_01_2").get_text()) == 0 or len(self.obj("txt_02").get_text()) == 0 \
        or self.idTipoDoc == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Código de Vacación", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Código de Empleado", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Código de Contrato", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.principal_guardado = False
        self.estadoguardar(estado)

    def on_cmb_tipo_doc_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            self.idTipoDoc = model[active][0]
            self.focus_out_event(self.obj("txt_01_2"), 0)  # Nro. Documento
        else:
            self.obj("barraestado").push(0, "No existen registros de Tipos de Documentos en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
                    self.on_btn_empleado_clicked(0)
                elif objeto == self.obj("txt_02"):
                    self.on_btn_contrato_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
            tipo = "Empleado"
        elif objeto == self.obj("txt_02"):
            tipo = "Contrato"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un " + tipo + ".")

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
            if objeto == self.obj("txt_00"):
                contrato = self.obj("txt_02").get_text()

                if len(contrato) > 0  and Op.comprobar_numero(int,
                objeto, "Código", self.obj("barraestado")):
                    # Al editar, comprueba que los valores son diferentes del original
                    busq = "" if not self.editando else " AND " + \
                        "(" + self.nav.campoid + " <> " + self.cond_vac + \
                        " OR NroContrato <> " + self.cond_cont + ")"

                    Op.comprobar_unique(self.nav.datos_conexion,
                        self.nav.tabla + "_s", self.nav.campoid, valor +
                        " AND NroContrato = " + contrato + busq, objeto,
                        self.estadoguardar, self.obj("barraestado"),
                        "El Código introducido ya ha sido registado para este Contrato.")

            elif objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Empleado", self.obj("barraestado")):
                    self.buscar_empleados(objeto, "idPersona", valor, "Cód. de Empleado")

            elif objeto == self.obj("txt_01_2"):
                self.buscar_empleados(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + str(self.idTipoDoc) + "'", "Nro. de Documento")

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Nro. de Contrato", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "idEmpleado, Cargo, Vigente",
                        "contratos_s", " WHERE NroContrato = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        if datos[0][2] == 1:
                            self.obj("txt_01").set_text(str(datos[0][0]))
                            self.obj("txt_02_1").set_text(datos[0][1])

                            # Nuevo Código de Vacaciones
                            self.obj("txt_00").set_text(Op.nuevoid(self.conexion,
                                self.nav.tabla + "_s WHERE NroContrato = " + valor,
                                self.nav.campoid))

                            self.obj("barraestado").push(0, "")
                            self.borrar_contrato = False
                            self.focus_out_event(self.obj("txt_01"), 0)
                        else:
                            objeto.grab_focus()
                            self.estadoguardar(False)
                            self.obj("barraestado").push(0, "El Contrato seleccionado ya no se encuentra vigente.")
                    else:
                        objeto.grab_focus()
                        self.estadoguardar(False)
                        self.obj("barraestado").push(0, "El Nro. de Contrato no es válido.")

    def buscar_empleados(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.nav.datos_conexion)
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

                # Buscar Antigüedad
                conexion = Op.conectar(self.nav.datos_conexion)
                cursor = Op.consultar(conexion, "MAX(Fecha)", "entradas_s",
                    " WHERE idEmpleado = " + self.idPersona)
                datos = cursor.fetchall()
                conexion.close()  # Finaliza la conexión

                if datos[0][0] is not None:
                    self.obj("txt_03").set_text(Cal.mysql_fecha(datos[0][0]))
                    antig, letras = Cal.antiguedad(str(datos[0][0]))
                    dias = Cal.vacaciones(antig)

                    self.obj("txt_03_1").set_text(letras)
                    self.obj("txt_03_2").set_text(str(dias))
                else:
                    self.obj("txt_03").set_text("Aún no ha sido registrada la Entrada del Empleado")
                    self.obj("txt_03_1").set_text("")
                    self.obj("txt_03_2").set_text("")

                if self.borrar_contrato:  # Debe indicarse otro Contrato
                    self.obj("txt_02").set_text("")
                    self.obj("txt_02_1").set_text("")
                else:
                    self.borrar_contrato = True

                self.obj("barraestado").push(0, "")
                self.verificacion(0)

        else:
            self.idPersona = valor
            self.estadoguardar(False)
            objeto.grab_focus()
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_01_2") if objeto == self.obj("txt_01") else self.obj("txt_01")
            otro.set_text("")
            self.obj("txt_01_1").set_text("")

            self.obj("txt_03").set_text("")
            self.obj("txt_03_1").set_text("")
            self.obj("txt_03_2").set_text("")
            self.obj("txt_03_3").set_text("")

    def guardar_principal_vacaciones(self):
        if not self.principal_guardado:
            v0 = self.obj("txt_00").get_text()  # idVacacion
            v1 = self.obj("txt_02").get_text()  # NroContrato

            sql = v0 + ", " + v1

            if not self.editando:
                Op.insertar(self.conexion, self.nav.tabla, sql)
            else:
                Op.modificar(self.conexion, self.nav.tabla,
                    self.cond_vac + ", " + self.cond_cont + ", " + sql)

            self.cond_vac = v0  # Nuevo idVacacion original
            self.cond_cont = v1  # Nuevo NroContrato original
            self.principal_guardado = self.editando = True

    def estadoguardar(self, estado):
        self.obj("buttonbox_abm").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)

        # Obligatoriamente debe poseer un Periodo seleccionado para poder Guardar
        estado = True if estado and len(self.obj("grilla").get_model()) > 0 else False
        self.obj("btn_guardar").set_sensitive(estado)

    def estadoedicion(self, estado):
        self.obj("vbox1").set_sensitive(not estado)
        self.obj("btn_cancelar").set_sensitive(not estado)

        self.obj("vbox2").set_visible(estado)
        self.obj("buttonbox_fecha").set_visible(estado)

##### Periodos de Vacaciones ###########################################

    def config_grilla_vacaciones(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(1.0)

        col0 = Op.columnas("Código", celda0, 0, True, 100, 200)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Fecha de Inicio", celda0, 1, True, 200)
        col1.set_sort_column_id(6)  # Para ordenarse usa la fila 6
        col2 = Op.columnas("Fecha de Finalización", celda0, 2, True, 200)
        col2.set_sort_column_id(7)  # Para ordenarse usa la fila 7
        col3 = Op.columnas("Cantidad de Días", celda1, 3, True, 100, 200)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Nro. de Comprobante", celda1, 4, True, 100, 200)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Fecha de Expedición", celda0, 5, True, 200)
        col5.set_sort_column_id(8)  # Para ordenarse usa la fila 8

        lista = [col0, col1, col2, col3, col4, col5]
        for columna in lista:
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(0)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, str, int, str, str, str, str, str)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_vacaciones(self):
        cursor = Op.consultar(self.conexion, "idToma, FechaInicio, FechaFin, " +
            "CantDias, NroComprobante, FechaHoraExp", "vacacionestomadas_s",
            " WHERE idVacacion = " + self.obj("txt_00").get_text() +
            " AND NroContrato = " + self.obj("txt_02").get_text() +
            " ORDER BY idToma")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        maximo = int(self.obj("txt_03_2").get_text())
        dias = 0  # Cantidad de Días asignados

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            comprobante = "" if datos[i][4] is None else str(datos[i][4])
            fechaexp = "" if datos[i][5] is None else Cal.mysql_fecha_hora(datos[i][5])
            dias += datos[i][3]

            lista.append([datos[i][0], Cal.mysql_fecha(datos[i][1]),
                Cal.mysql_fecha(datos[i][2]), datos[i][3], comprobante,
                fechaexp, str(datos[i][1]), str(datos[i][2]), str(datos[i][5])])

        self.obj("txt_03_3").set_text(str(maximo - dias))
        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_clicked(self, objeto):
        self.editando_fecha = False
        self.funcion_fechas()

    def on_btn_modificar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.cond_fecha = self.idToma = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Periodos de Vacaciones. Luego presione Modificar.")
        else:
            self.editando_fecha = True
            self.funcion_fechas()

    def on_btn_eliminar_clicked(self, objeto):
        self.guardar_principal_vacaciones()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            toma = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Periodos de Vacaciones. Luego presione Eliminar.")
        else:
            vac = self.obj("txt_00").get_text()
            cont = self.obj("txt_02").get_text()
            ini = seleccion.get_value(iterador, 1)
            fin = seleccion.get_value(iterador, 2)
            dias = str(seleccion.get_value(iterador, 3))

            eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
                "\nCódigo: " + toma + "\nFecha de Inicio: " + ini +
                "\nFecha de Finalización: " + fin +
                "\nCantidad de Días: " + dias)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "vacacionestomadas", vac + ", " + cont + ", " + toma)
                self.cargar_grilla_vacaciones()

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_clicked(0)

##### Agregar-Modificar Periodos de Vacaciones #########################

    def funcion_fechas(self):
        self.guardar_principal_vacaciones()
        self.pago_modificado = False

        if self.editando_fecha:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            ini = seleccion.get_value(iterador, 1)
            fin = seleccion.get_value(iterador, 2)
            dias = str(seleccion.get_value(iterador, 3))
            comp = seleccion.get_value(iterador, 4)

            self.fechaini = seleccion.get_value(iterador, 6)
            self.fechafin = seleccion.get_value(iterador, 7)

            self.obj("txt_f_01").set_text(ini)
            self.obj("txt_f_02").set_text(fin)
            self.obj("txt_f_03").set_text(dias)

            if len(comp) == 0:
                self.editando_pago = False
            else:
                self.editando_pago = True
                self.obj("txt_f_04").set_text(comp)

        else:
            self.idToma = Op.nuevoid(self.conexion, "vacacionestomadas_s" +
                " WHERE idVacacion = " + self.obj("txt_00").get_text() +
                " AND NroContrato = " + self.obj("txt_02").get_text(), "idToma")
            self.editando_pago = False

        self.estadoedicion(True)
        self.estadoguardar(False)

        self.obj("btn_guardar_fecha").set_sensitive(False)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

    def on_btn_guardar_fecha_clicked(self, objeto):
        self.guardar_principal_vacaciones()

        vac = self.obj("txt_00").get_text()
        cont = self.obj("txt_02").get_text()

        sql = vac + ", " + cont + ", " + self.idToma + ", " + \
            "'" + self.fechaini + "', '" + self.fechafin + "'"

        if not self.editando_fecha:
            Op.insertar(self.conexion, "vacacionestomadas", sql)
        else:
            Op.modificar(self.conexion, "vacacionestomadas", self.cond_fecha + ", " + sql)

        if self.pago_modificado:
            pago = self.obj("txt_f_04").get_text()
            if len(pago) == 0:
                if self.editando_pago:
                    Op.eliminar(self.conexion, "vacaciones_comprpagos",
                        vac + ", " + cont + ", " + self.idToma)
            else:
                sql = vac + ", " + cont + ", " + self.idToma + ", " + pago
                if not self.editando_pago:
                    Op.insertar(self.conexion, "vacaciones_comprpagos", sql)
                else:
                    Op.modificar(self.conexion, "vacaciones_comprpagos", sql)

        self.cargar_grilla_vacaciones()
        self.on_btn_cancelar_fecha_clicked(0)

    def on_btn_cancelar_fecha_clicked(self, objeto):
        self.estadoedicion(False)
        self.estadoguardar(True)

        self.obj("txt_f_01").set_text("")
        self.obj("txt_f_02").set_text("")
        self.obj("txt_f_03").set_text("")
        self.obj("txt_f_04").set_text("")

    def on_btn_comprobante_clicked(self, objeto):
        from clases.llamadas import comprobantepagos
        comprobantepagos(self.nav.datos_conexion, self)

    def on_btn_fecha_ini_clicked(self, objeto):
        self.obj("txt_f_01").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_f_01").set_text(lista[0])
            self.fechaini = lista[1]

    def on_btn_limpiar_fecha_ini_clicked(self, objeto):
        self.obj("txt_f_01").set_text("")
        self.obj("txt_f_01").grab_focus()

    def on_btn_fecha_fin_clicked(self, objeto):
        self.obj("txt_f_02").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_f_02").set_text(lista[0])
            self.fechafin = lista[1]

    def on_btn_limpiar_fecha_fin_clicked(self, objeto):
        self.obj("txt_f_02").set_text("")
        self.obj("txt_f_02").grab_focus()

    def verificacion_fecha(self, objeto):
        if len(self.obj("txt_f_01").get_text()) == 0 or len(self.obj("txt_f_02").get_text()) == 0:
            estado = False
        else:
            estado = True
        self.obj("btn_guardar_fecha").set_sensitive(estado)

    def verificacion_pago(self, objeto):
        self.pago_modificado = True

        if len(self.obj("txt_f_04").get_text()) > 0:
            if Op.comprobar_numero(int, self.obj("txt_f_04"), "Nro. Comprobante de Pago", self.obj("barraestado")):
                self.verificacion_fecha(0)
            else:
                self.obj("btn_guardar_fecha").set_sensitive(False)

    def on_fecha_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_f_01"):
                    self.on_btn_fecha_ini_clicked(0)
                elif objeto == self.obj("txt_f_02"):
                    self.on_btn_fecha_fin_clicked(0)
                elif objeto == self.obj("txt_f_04"):
                    self.on_btn_comprobante_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.on_fecha_focus_out_event(objeto, 0)

    def on_fecha_focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_f_01"):
            tipo = "a Fecha de Inicio de las Vacaciones del Empleado"
        elif objeto == self.obj("txt_f_02"):
            tipo = "a Fecha de Finalización de las Vacaciones del Empleado"
        elif objeto == self.obj("txt_f_04"):
            tipo = " Comprobante de Pago asociado a este Periodo de Vacaciones"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un" + tipo + ".")

    def on_fecha_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
        else:
            if objeto in (self.obj("txt_f_01"), self.obj("txt_f_02")):
                if len(self.obj("txt_f_01").get_text()) > 0 \
                and len(self.obj("txt_f_02").get_text()) > 0:
                    if Op.compara_fechas(self.nav.datos_conexion,
                    "'" + self.fechaini + "'", ">", "'" + self.fechafin + "'"):
                        self.obj("btn_guardar_fecha").set_sensitive(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "La Fecha de Inicio del Periodo de Vacaciones NO puede ser posterior a la de Finalización.")
                    else:
                        # Cálculo de la Cantidad de Días
                        dias = str(Cal.cantidad_dias(self.fechaini, self.fechafin))
                        self.obj("txt_f_03").set_text(dias)
                        self.obj("barraestado").push(0, "")

            elif objeto == self.obj("txt_f_04"):
                if Op.comprobar_numero(int, objeto, "Nro. de Comprobante de Pago", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "NroComprobante",
                        "comprobantepagos_s", " WHERE NroComprobante = " +
                        valor + " AND Confirmado = 1")
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("barraestado").push(0, "")
                        self.verificacion(0)
                    else:
                        objeto.grab_focus()
                        self.obj("btn_guardar_fecha").set_sensitive(False)
                        self.obj("barraestado").push(0, "El Nro. de Comprobante de Pago no es válido.")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)

    col0 = Op.columnas("Código", celda0, 0, True, 100, 200)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Nro. Contrato", celda0, 1, True, 100, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Cód. Empleado", celda0, 2, True, 100, 200)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Tipo Doc. Identidad", celda0, 3, True, 100, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Nro. Doc. Identidad", celda0, 4, True, 100, 200)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Nombre y Apellido", celda1, 5, True, 200)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Fecha de Nacimiento", celda0, 6, True, 200)
    col6.set_sort_column_id(16)  # Para ordenarse usa la fila 16
    col7 = Op.columnas("Edad", celda0, 7, True, 100, 200)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Cargo", celda1, 8, True, 150)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Fecha de Entrada", celda0, 9, True, 200)
    col9.set_sort_column_id(17)  # Para ordenarse usa la fila 17
    col10 = Op.columnas("Antigüedad", celda0, 10, True, 100, 200)
    col10.set_sort_column_id(10)
    col11 = Op.columnas("Días Asignados", celda0, 11, True, 100, 200)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Fecha de Modificación", celda0, 12, True, 200)
    col12.set_sort_column_id(18)  # Para ordenarse usa la fila 18
    col13 = Op.columnas("Alias de Usuario", celda1, 13, True, 100, 200)
    col13.set_sort_column_id(13)
    col14 = Op.columnas("Nro. Documento", celda0, 14, True, 100, 200)
    col14.set_sort_column_id(14)
    col15 = Op.columnas("Nombre de Usuario", celda1, 15, True, 200)
    col15.set_sort_column_id(15)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9,
        col10, col11, col12, col13, col14, col15]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(5)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 5)

    lista = ListStore(int, int, int, str, str, str, str, int, str,
        str, int, int, str, str, str, str, str, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar in ("FechaNacimiento", "FechaEntrada", "FechaHora"):
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, "idVacacion, NroContrato, idEmpleado, " +
        "idTipoDocumento, NroDocumento, NombreApellido, FechaNacimiento, " +
        "Edad, Cargo, FechaEntrada, Antiguedad, DiasTomados, FechaHora, " +
        "Alias, NroDocUsuario, NombreUsuario", self.tabla + "_s",
        opcion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        fechanac = "" if datos[i][6] is None else Cal.mysql_fecha(datos[i][6])
        fechaent = "" if datos[i][9] is None else Cal.mysql_fecha(datos[i][9])
        fechaexp = "" if datos[i][12] is None else Cal.mysql_fecha_hora(datos[i][12])

        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], datos[i][5], fechanac, datos[i][7], datos[i][8],
            fechaent, datos[i][10], datos[i][11], fechaexp, datos[i][13],
            datos[i][14], datos[i][15], str(datos[i][6]), str(datos[i][9]),
            str(datos[i][12])])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Código", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "Nro. Contrato", "NroContrato"
    elif idcolumna == 2:
        col, self.campo_buscar = "Cód. Empleado", "idEmpleado"
    elif idcolumna == 3:
        col, self.campo_buscar = "Tipo Doc. Identidad", "idTipoDocumento"
    elif idcolumna == 4:
        col, self.campo_buscar = "Nro. Doc. Identidad", "NroDocumento"
    elif idcolumna == 5:
        col, self.campo_buscar = "Nombre y Apellido", "NombreApellido"
    elif idcolumna == 16:
        col, self.campo_buscar = "Fecha de Nacimiento, desde", "FechaNacimiento"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 7:
        col = self.campo_buscar = "Edad"
    elif idcolumna == 8:
        col = self.campo_buscar = "Cargo"
    elif idcolumna == 17:
        col, self.campo_buscar = "Fecha de Entrada, desde", "FechaEntrada"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 10:
        col, self.campo_buscar = "Antigüedad", "Antiguedad"
    elif idcolumna == 11:
        col, self.campo_buscar = "Días Asignados", "DiasTomados"
    elif idcolumna == 18:
        col, self.campo_buscar = "Fecha de Modificación, desde", "FechaHora"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 13:
        col, self.campo_buscar = "Alias de Usuario", "Alias"
    elif idcolumna == 14:
        col, self.campo_buscar = "Nro. Documento", "NroDocUsuario"
    elif idcolumna == 15:
        col, self.campo_buscar = "Nombre de Usuario", "NombreUsuario"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 5)
    valor2 = seleccion.get_value(iterador, 9)
    valor3 = str(seleccion.get_value(iterador, 11))
    valor4 = seleccion.get_value(iterador, 13)
    valor5 = str(seleccion.get_value(iterador, 1))

    eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
        "\nCódigo: " + valor0 + "\nNombre y Apellido: " + valor1 +
        "\nFecha de Entrada: " + valor2 + "\nDías Asignados: " + valor3 +
        "\nUsuario Responsable: " + valor4)

    self.obj("grilla").get_selection().unselect_all()
    self.obj("barraestado").push(0, "")

    if eleccion:
        conexion = Op.conectar(self.datos_conexion)
        Op.eliminar(conexion, self.tabla, valor0 + ", " + valor5)
        conexion.commit()
        conexion.close()  # Finaliza la conexión
        cargar_grilla(self)


def listar_grilla(self):
    pass


def seleccion(self):
    pass
