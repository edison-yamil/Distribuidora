#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date
from decimal import Decimal
from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen):
        self.editando = edit
        self.nav = origen

        arch = Op.archivo("rrhh_descuentos")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(800, 600)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Descuentos")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_01_2").set_max_length(12)
        self.obj("txt_02").set_max_length(10)
        self.obj("txt_03").set_max_length(10)

        self.obj("txt_i_04").set_max_length(12)
        self.obj("txt_i_05").set_max_length(12)
        self.obj("txt_d_01").set_max_length(10)
        self.obj("txt_d_03").set_max_length(12)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código del Descuento")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Empleado afectado por el Descuento"))
        self.obj("txt_01_1").set_tooltip_text("Nombre y Apellido del Empleado")
        self.obj("txt_01_2").set_tooltip_text("Ingrese el Nro. de Documento del Empleado")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el Contrato del Empleado seleccionado"))
        self.obj("txt_02_1").set_tooltip_text("Cargo del Empleado dentro de la Empresa")
        self.obj("txt_02_2").set_tooltip_text("Salario Mensual del Empleado")
        self.obj("txt_03").set_tooltip_text(Mens.usar_boton("la Sanción que provoca el Descuento"))
        self.obj("txt_03_1").set_tooltip_text("Duración de la Sanción que provoca el Descuento")
        self.obj("txt_04").set_tooltip_text("Ingrese cualquier información adicional con respecto al Descuento")
        self.obj("txt_02").grab_focus()

        self.obj("txt_i_02").set_tooltip_text(Mens.usar_boton("la Fecha de Inicio del cobro de los Descuentos"))
        self.obj("txt_i_04").set_tooltip_text("Ingrese el Monto Descontar por Periodo")
        self.obj("txt_i_05").set_tooltip_text("Ingrese el Monto Total a Descontar")

        self.obj("txt_d_01").set_tooltip_text("Ingrese el Código del cobro")
        self.obj("txt_d_02").set_tooltip_text(Mens.usar_boton("la Fecha del cobro del Descuento"))
        self.obj("txt_d_03").set_tooltip_text("Ingrese el Monto a Descontar")

        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_01_2"), self.obj("cmb_tipo_doc")
        self.txt_cod_cnt, self.txt_crg_cnt, self.txt_sal_cnt = self.obj("txt_02"), \
            self.obj("txt_02_1"), self.obj("txt_02_2")
        self.txt_cod_snc, self.txt_per_snc = self.obj("txt_03"), self.obj("txt_03_1")

        self.idPersona, self.borrar_contrato = None, not edit
        self.idTipoDoc = self.idMotivoDescuento = self.idPeriodoPago = -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_motivo"), "motivodescuentos", "idMotivoDescuento")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_periodo"), "periodopagos", "idPeriodoPago")

        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            idcont = str(seleccion.get_value(iterador, 1))
            idemp = str(seleccion.get_value(iterador, 2))
            cargo = seleccion.get_value(iterador, 8)
            salario = str(seleccion.get_value(iterador, 9))
            motivo = seleccion.get_value(iterador, 10)
            idsancion = seleccion.get_value(iterador, 12)
            obs = seleccion.get_value(iterador, 17)

            idsancion = "" if idsancion is None else idsancion
            obs = "" if obs is None else obs

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(idemp)
            self.obj("txt_02").set_text(idcont)
            self.obj("txt_02_1").set_text(cargo)
            self.obj("txt_02_2").set_text(salario)
            self.obj("txt_03").set_text(idsancion)
            self.obj("txt_04").set_text(obs)

            # Asignación de Motivo en Combo
            model, i = self.obj("cmb_motivo").get_model(), 0
            while model[i][0] != motivo: i += 1
            self.obj("cmb_motivo").set_active(i)

            self.focus_out_event(self.obj("txt_01"), 0)
            self.focus_out_event(self.obj("txt_03"), 0)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))
            self.obj("cmb_tipo_doc").set_active(0)
            self.obj("cmb_motivo").set_active(0)
            self.editando_sancion = False

        self.conexion = Op.conectar(self.nav.datos_conexion)
        self.principal_guardado = True
        self.sancion_modificado = False

        self.config_grilla_descuentos()
        self.cargar_grilla_descuentos()

        self.estadoedicion(False)
        self.estadoguardar(self.editando)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_principal_descuentos()
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

    def on_btn_sancion_clicked(self, objeto):
        from clases.llamadas import sanciones
        sanciones(self.nav.datos_conexion, self)

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_01_2").get_text()) == 0 or len(self.obj("txt_02").get_text()) == 0 \
        or self.idTipoDoc == -1 or self.idMotivoDescuento == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Cód. de Descuento", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Cód. de Empleado", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Cód. de Contrato", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.principal_guardado = False
        self.estadoguardar(estado)

    def verificacion_sancion(self, objeto):
        self.sancion_modificado = True

        if len(self.obj("txt_03").get_text()) > 0:
            if Op.comprobar_numero(int, self.obj("txt_03"), "Cód. de Sanción", self.obj("barraestado")):
                self.verificacion(0)
            else:
                self.estadoguardar(False)

    def on_cmb_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            if objeto == self.obj("cmb_tipo_doc"):
                self.idTipoDoc = model[active][0]
                self.focus_out_event(self.obj("txt_01_2"), 0)  # Nro. Documento

            elif objeto == self.obj("cmb_motivo"):
                self.idMotivoDescuento = model[active][0]
        else:
            if objeto == self.obj("cmb_tipo_doc"):
                tipo = "Tipos de Documentos"
            elif objeto == self.obj("cmb_motivo"):
                tipo = "Motivos de Descuento"
            self.obj("barraestado").push(0, "No existen registros de " + tipo + " en el Sistema.")

    def on_notebook_change_current_page(self, objeto):
        self.verificacion_descuento(0)
        print("Cambiando Tipo de Carga de Datos")

    def on_notebook_focus_in_event(self, objeto, evento):
        self.verificacion_descuento(0)

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
                    self.on_btn_empleado_clicked(0)
                elif objeto == self.obj("txt_02"):
                    self.on_btn_contrato_clicked(0)
                elif objeto == self.obj("txt_03"):
                    self.on_btn_sancion_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
            tipo = " Empleado"
        elif objeto == self.obj("txt_02"):
            tipo = " Contrato"
        elif objeto == self.obj("txt_03"):
            tipo = "a Sanción"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un" + tipo + ".")

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

            elif objeto == self.obj("txt_03"):  # Código de Sanción
                self.obj("txt_03_1").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) and \
                Op.comprobar_numero(int, objeto, "Código", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion,
                        self.nav.tabla + "_s", self.nav.campoid, valor,
                        objeto, self.estadoguardar, self.obj("barraestado"),
                        "El Código introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Empleado", self.obj("barraestado")):
                    self.buscar_empleados(objeto, "idPersona", valor, "Cód. de Empleado")

            elif objeto == self.obj("txt_01_2"):
                self.buscar_empleados(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + str(self.idTipoDoc) + "'", "Nro. de Documento")

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Nro. de Contrato", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "idEmpleado, Cargo, Salario, Vigente",
                        "contratos_s", " WHERE NroContrato = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        if datos[0][3] == 1:
                            self.obj("txt_01").set_text(str(datos[0][0]))
                            self.obj("txt_02_1").set_text(datos[0][1])
                            self.obj("txt_02_2").set_text(str(datos[0][2]))

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

            elif objeto == self.obj("txt_03"):
                if Op.comprobar_numero(int, objeto, "Cód. de Sanción", self.obj("barraestado")):
                    if len(self.obj("txt_02").get_text()) == 0:
                        condicion = busq = ""
                    else:
                        condicion = " para este Contrato"
                        busq = " AND NroContrato = " + self.obj("txt_02").get_text()

                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "FechaInicio, FechaFin",
                        "sanciones_s", " WHERE idSancion = " + valor + busq)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        ini = Cal.mysql_fecha(datos[i][0])
                        fin = Cal.mysql_fecha(datos[i][1])

                        self.obj("txt_03_1").set_text("Desde " + ini + " hasta " + fin)
                        self.obj("barraestado").push(0, "")
                    else:
                        objeto.grab_focus()
                        self.estadoguardar(False)
                        self.obj("barraestado").push(0, "El Cód. de Sanción no es válido" + condicion + ".")

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

                if self.borrar_contrato:  # Debe indicarse otro Contrato
                    self.obj("txt_02").set_text("")
                    self.obj("txt_02_1").set_text("")
                    self.obj("txt_02_2").set_text("")
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

    def guardar_principal_descuentos(self):
        if not self.principal_guardado:
            desc = self.obj("txt_00").get_text()  # idDescuento
            cont = self.obj("txt_02").get_text()  # NroContrato

            obs = self.obj("txt_04").get_text()
            obs = "NULL" if len(obs) == 0 else "'" + obs + "'"

            sql = desc + ", " + cont + ", " + str(self.idMotivoDescuento) + ", " + obs

            if not self.editando:
                Op.insertar(self.conexion, self.nav.tabla, sql)
            else:
                Op.modificar(self.conexion, self.nav.tabla, self.cond + ", " + sql)

            self.cond = desc  # Nuevo idDescuento original
            self.principal_guardado = self.editando = True

            if self.sancion_modificado:
                sancion = self.obj("txt_03").get_text()
                if len(sancion) == 0:
                    if self.editando_sancion:
                        Op.eliminar(self.conexion, "descuentos_sanciones",
                            desc + ", " + sancion)
                        self.editando_sancion = False
                else:
                    sql = desc + ", " + sancion
                    if not self.editando_sancion:
                        Op.insertar(self.conexion, "descuentos_sanciones", sql)
                    else:
                        Op.modificar(self.conexion, "descuentos_sanciones", sql)
                    self.editando_sancion = True

                self.sancion_modificado = False

    def estadoguardar(self, estado):
        self.obj("buttonbox_abm").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)

        # Obligatoriamente debe poseer un Monto de Descuento para poder Guardar
        estado = True if estado and len(self.obj("grilla").get_model()) > 0 else False
        self.obj("btn_guardar").set_sensitive(estado)

    def estadoedicion(self, estado):
        self.obj("vbox1").set_visible(not estado)
        self.obj("btn_cancelar").set_sensitive(not estado)

        self.obj("notebook").set_visible(estado)
        self.obj("buttonbox_descuento").set_visible(estado)

##### Descuentos #######################################################

    def config_grilla_descuentos(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(1.0)

        col0 = Op.columnas("Código", celda0, 0, True, 200, 300)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Monto de Descuento", celda1, 1, True, 200, 300)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Fecha", celda0, 2, True, 200)
        col2.set_sort_column_id(3)  # Para ordenarse usa la fila 3

        lista = [col0, col1, col2]
        for columna in lista:
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(0)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, float, str, str)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_descuentos(self):
        cursor = Op.consultar(self.conexion, "idCobro, Monto, FechaCobro",
            "descuentos_periodocobros", " WHERE idDescuento = " +
            self.obj("txt_00").get_text() + " ORDER BY idCobro")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        monto = 0.0

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            monto += datos[i][1]

            lista.append([datos[i][0], datos[i][1],
                Cal.mysql_fecha(datos[i][2]), str(datos[i][2])])

        self.obj("txt_total").set_text(str(monto))
        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_clicked(self, objeto):
        self.editando_descuento = False
        self.funcion_descuentos()

    def on_btn_modificar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.cond_descuento = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Cobros. Luego presione Modificar.")
        else:
            self.editando_descuento = True
            self.funcion_descuentos()

    def on_btn_eliminar_clicked(self, objeto):
        self.guardar_principal_descuentos()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            cod = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Cobros. Luego presione Eliminar.")
        else:
            desc = self.obj("txt_00").get_text()
            monto = str(seleccion.get_value(iterador, 1))
            fecha = seleccion.get_value(iterador, 2)

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\nCódigo: " + cod +
                "\nMonto: " + monto + "\nFecha de Cobro: " + fecha)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "descuentos_periodocobros", desc + ", " + cod)
                self.cargar_grilla_descuentos()

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_clicked(0)

##### Agregar-Modificar Descuentos #####################################

    def funcion_descuentos(self):
        self.guardar_principal_descuentos()

        if self.editando_descuento:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            monto = str(seleccion.get_value(iterador, 1))
            fecha = seleccion.get_value(iterador, 2)
            self.fecha = seleccion.get_value(iterador, 3)

            self.obj("txt_d_01").set_text(self.cond_descuento)
            self.obj("txt_d_02").set_text(fecha)
            self.obj("txt_d_03").set_text(monto)

            self.obj("notebook").set_current_page(1)
            self.obj("notebook").set_show_tabs(False)
        else:
            self.obj("notebook").set_current_page(0)
            self.obj("notebook").set_show_tabs(True)
            self.obj("cmb_periodo").set_active(0)

        self.estadoedicion(True)
        self.estadoguardar(False)

        self.obj("btn_guardar_descuento").set_sensitive(False)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

    def on_btn_guardar_descuento_clicked(self, objeto):
        self.guardar_principal_descuentos()
        desc = self.obj("txt_00").get_text()

        if self.obj("notebook").get_current_page() == 0:
            ini = int(Op.nuevoid(self.conexion, "descuentos_periodocobros" +
                " WHERE idDescuento = " + desc, "idCobro"))

            cant = self.obj("txt_i_01").get_value_as_int()
            monto = str(round(Decimal(self.obj("txt_i_04").get_text()), 2))

            # Valores Iniciales
            if self.idPeriodoPago == 1:  # Mensual
                dia_desc = self.obj("txt_i_03").get_value_as_int()
                longitud_grilla = len(self.obj("grilla").get_model())

                if longitud_grilla == 0:  # Vacía
                    fecha = date.today()
                else:
                    # Buscar la última fecha registrada
                    cursor = Op.consultar(self.conexion, "MAX(FechaCobro)",
                        "descuentos_periodocobros", " WHERE idDescuento = " + desc)
                    fecha = cursor.fetchall()[0][0]

                anho = fecha.strftime("%Y")
                mes = fecha.strftime("%m")
                dia = fecha.strftime("%d")

                if longitud_grilla == 0:  # Vacía
                    if dia_desc < int(dia):  # Puede cobrarse hoy
                        mes, anho = Cal.mes_mas_uno(mes, anho)
                else:
                    if dia_desc <= int(dia):
                        mes, anho = Cal.mes_mas_uno(mes, anho)

                dia = Op.cadenanumeros(dia_desc, 2)
            else:
                if self.idPeriodoPago == 2:  # Quincenal
                    periodo = 14
                elif self.idPeriodoPago == 3:  # Semanal
                    periodo = 7
                elif self.idPeriodoPago == 4:  # Diario
                    periodo = 1

                anho = self.fecha_inicial[0:4]
                mes = self.fecha_inicial[5:7]
                dia = self.fecha_inicial[8:10]

            # Carga de Datos
            for i in range(0, cant):
                if int(mes) == 2:
                    # Años bisiestos: 1900, (2000), 2100, 2200, 2300, (2400), 2500
                    if int(anho) % 4 == 0:  # Es Múltiplo de 4
                        dia_max = 29
                        if int(anho) % 100 == 0:  # Pero NO es múltiplo de 100
                            if int(anho) % 400 != 0:  # Excepto si es múltiplo de 400
                                dia_max = 28
                    else:
                        dia_max = 28
                elif int(mes) in (4, 6, 9, 11):
                    dia_max = 30
                else:
                    dia_max = 31

                if self.idPeriodoPago == 1:  # Mensual
                    if int(dia) > dia_max:
                        dia = str(dia_max)

                fecha = "'" + anho + "-" + mes + "-" + dia + "'"

                sql = desc + ", " + str(ini) + ", " + monto + ", " + fecha
                Op.insertar(self.conexion, "descuentos_periodocobros", sql)
                ini += 1

                # Modifica valores para proxima cuota
                if self.idPeriodoPago == 1:  # Mensual
                    dia = Op.cadenanumeros(int(dia_desc), 2)
                    mes, anho = Cal.mes_mas_uno(mes, anho)
                else:
                    dia = str(int(dia) + periodo)
                    if int(dia) > dia_max:
                        dia = str(int(dia) - dia_max)
                        mes, anho = Cal.mes_mas_uno(mes, anho)

        else:
            cod = self.obj("txt_d_01").get_text()
            monto = self.obj("txt_d_03").get_text()

            sql = desc + ", " + cod + ", " + monto + ", '" + str(self.fecha) + "'"

            if not self.editando_descuento:
                Op.insertar(self.conexion, "descuentos_periodocobros", sql)
            else:
                Op.modificar(self.conexion, "descuentos_periodocobros",
                    self.cond_descuento + ", " + sql)

        self.cargar_grilla_descuentos()
        self.on_btn_cancelar_descuento_clicked(0)

    def on_btn_cancelar_descuento_clicked(self, objeto):
        self.estadoedicion(False)
        self.estadoguardar(True)

        self.obj("txt_i_01").set_value(2)
        self.obj("cmb_periodo").set_active(-1)
        self.obj("txt_i_02").set_text("")
        self.obj("txt_i_03").set_value(1)
        self.obj("txt_i_04").set_text("")
        self.obj("txt_i_05").set_text("")

        self.obj("txt_d_01").set_text("")
        self.obj("txt_d_02").set_text("")
        self.obj("txt_d_03").set_text("")

    def verificacion_descuento(self, objeto):
        page = self.obj("notebook").get_current_page()

        if page == 0:  # Montos Iguales
            if len(self.obj("txt_i_04").get_text()) == 0 \
            or len(self.obj("txt_i_05").get_text()) == 0 or self.idPeriodoPago == -1:
                estado = False
            else:
                if Op.comprobar_numero(float, self.obj("txt_i_04"), "Monto Descontar por Periodo", self.obj("barraestado")) \
                and Op.comprobar_numero(float, self.obj("txt_i_05"), "Monto Total a Descontar", self.obj("barraestado")):
                    if self.idPeriodoPago != 1:  # NO Mensual
                        if len(self.obj("txt_i_02").get_text()) == 0:
                            estado = False
                        else:
                            estado = True
                    else:
                        estado = True

        else:  # Montos Personalizados
            if len(self.obj("txt_d_01").get_text()) == 0 or len(self.obj("txt_d_02").get_text()) == 0 \
            or len(self.obj("txt_d_03").get_text()) == 0:
                estado = False
            else:
                if Op.comprobar_numero(int, self.obj("txt_d_01"), "Cód. de Descuento", self.obj("barraestado")) \
                and Op.comprobar_numero(float, self.obj("txt_d_03"), "Monto de Cuota", self.obj("barraestado")):
                    estado = True
                else:
                    estado = False

        self.obj("btn_guardar_descuento").set_sensitive(estado)

    def on_descuento_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_i_02"):
                    self.on_btn_primer_dia_clicked(0)
                elif objeto == self.obj("txt_d_02"):
                    self.on_btn_fecha_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.on_descuento_focus_out_event(objeto, 0)

    def on_descuento_focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_i_02"):
            tipo = "Fecha del Primer Descuento"
        elif objeto == self.obj("txt_d_02"):
            tipo = "Fecha del Descuento"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar la " + tipo + ".")

    def on_descuento_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
        else:
            if objeto == (self.obj("txt_i_02"), self.obj("txt_d_02")):
                self.obj("barraestado").push(0, "")

            elif objeto == self.obj("txt_i_04"):
                if Op.comprobar_numero(float, objeto, "Monto a Descontar por Periodo", self.obj("barraestado")):
                    cant = self.obj("txt_i_01").get_value_as_int()
                    total = round(Decimal(valor), 2) * cant
                    self.obj("txt_i_05").set_text(str(total))
                    self.obtener_porcentaje(valor, self.obj("txt_i_porc"))

            elif objeto == self.obj("txt_i_05"):
                if Op.comprobar_numero(float, objeto, "Monto Total a Descontar", self.obj("barraestado")):
                    cant = self.obj("txt_i_01").get_value_as_int()
                    monto = round(Decimal(valor), 2) / cant
                    self.obj("txt_i_04").set_text(str(round(monto, 2)))
                    self.obtener_porcentaje(monto, self.obj("txt_i_porc"))

            elif objeto == self.obj("txt_d_01"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando_descuento or valor != self.cond_descuento) and \
                Op.comprobar_numero(int, objeto, "Cód. de Descuento", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion,
                        "descuentos_periodocobros", "idCobro", valor +
                        " AND idDescuento = " + self.obj("txt_00").get_text(), objeto,
                        self.obj("btn_guardar_descuento"), self.obj("barraestado"),
                        "El Cód. de Descuento introducido ya ha sido registado.")

            elif objeto == self.obj("txt_d_03"):
                if Op.comprobar_numero(float, objeto, "Monto de Cuota", self.obj("barraestado")):
                    self.obtener_porcentaje(valor, self.obj("txt_d_porc"))

    def obtener_porcentaje(self, valor, label):
        salario = Decimal(self.obj("txt_02_2").get_text())
        if salario > 0:
            porc = round(Decimal(valor) * 100 / salario, 2)
            label.set_text(str(porc) + "% del Salario Mensual")
        else:
            label.set_text("")

##### Montos de Descuentos Iguales #####################################

    def on_btn_primer_dia_clicked(self, objeto):
        self.obj("txt_i_02").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_i_02").set_text(lista[0])
            self.fecha_inicial = lista[1]

    def on_btn_limpiar_primer_dia_clicked(self, objeto):
        self.obj("txt_i_02").set_text("")
        self.obj("txt_i_02").grab_focus()

    def on_cmb_periodo_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            self.idPeriodoPago = model[active][0]

            estado = False if self.idPeriodoPago == 1 else True
            self.obj("hbox13").set_visible(estado)  # Primer Día NO se usa en Mensual
            self.obj("hbox14").set_visible(not estado)

            self.verificacion_descuento(0)
        else:
            self.obj("barraestado").push(0, "No existen registros de Periodos de Pago en el Sistema.")

##### Montos de Descuentos Personalizados ##############################

    def on_btn_fecha_clicked(self, objeto):
        self.obj("txt_d_02").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_d_02").set_text(lista[0])
            self.fecha = lista[1]

    def on_btn_limpiar_fecha_clicked(self, objeto):
        self.obj("txt_d_02").set_text("")
        self.obj("txt_d_02").grab_focus()


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)
    celda2 = Op.celdas(1.0)

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
    col6.set_sort_column_id(21)  # Para ordenarse usa la fila 21
    col7 = Op.columnas("Edad", celda0, 7, True, 100, 200)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Cargo", celda1, 8, True, 150)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Salario Mensual", celda2, 9, True, 100, 200)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Cód. Motivo", celda0, 10, True, 100, 200)
    col10.set_sort_column_id(10)
    col11 = Op.columnas("Motivo de Descuento", celda1, 11, True, 200)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Cód. de Sanción", celda0, 12, True, 100, 200)
    col12.set_sort_column_id(22)  # Para ordenarse usa la fila 22 (entero)
    col13 = Op.columnas("Cód. Motivo", celda0, 13, True, 100, 200)
    col13.set_sort_column_id(23)  # Para ordenarse usa la fila 23 (entero)
    col14 = Op.columnas("Motivo de Sanción", celda0, 14, True, 200)
    col14.set_sort_column_id(14)
    col15 = Op.columnas("Total a Descontar", celda2, 15, True, 100, 200)
    col15.set_sort_column_id(15)
    col16 = Op.columnas("Fecha de Modificación", celda0, 16, True, 200)
    col16.set_sort_column_id(24)  # Para ordenarse usa la fila 24
    col17 = Op.columnas("Observaciones", celda1, 17, True, 200)
    col17.set_sort_column_id(17)
    col18 = Op.columnas("Alias de Usuario", celda1, 18, True, 100, 200)
    col18.set_sort_column_id(18)
    col19 = Op.columnas("Nro. Documento", celda0, 19, True, 100, 200)
    col19.set_sort_column_id(19)
    col20 = Op.columnas("Nombre de Usuario", celda1, 20, True, 200)
    col20.set_sort_column_id(20)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10,
        col11, col12, col13, col14, col15, col16, col17, col18, col19, col20]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(5)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 5)

    lista = ListStore(int, int, int, str, str, str, str, int, str, float, int, str,
        str, str, str, float, str, str, str, str, str, str, int, int, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar in ("FechaHora", "FechaNacimiento"):
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, "idDescuento, NroContrato, idEmpleado, " +
        "idTipoDocumento, NroDocumento, NombreApellido, FechaNacimiento, " +
        "Edad, Cargo, SalarioMensual, idMotivoDescuento, MotivoDescuento, " +
        "idSancion, idMotivoSancion, MotivoSancion, TotalCobrar, FechaHora, " +
        "Observaciones, Alias, NroDocUsuario, NombreUsuario",
        self.tabla + "_s", opcion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        fechanac = "" if datos[i][6] is None else Cal.mysql_fecha(datos[i][6])
        sancion = "" if datos[i][12] is None else str(datos[i][11])
        motivosancion = "" if datos[i][13] is None else str(datos[i][12])
        fecha = "" if datos[i][16] is None else Cal.mysql_fecha_hora(datos[i][15])

        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], datos[i][5], fechanac, datos[i][7], datos[i][8],
            datos[i][9], datos[i][10], datos[i][11], sancion, motivosancion,
            datos[i][14], datos[i][15], fecha, datos[i][17], datos[i][18],
            datos[i][19], datos[i][20], str(datos[i][6]), datos[i][12],
            datos[i][13], str(datos[i][16])])

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
    elif idcolumna == 21:
        col, self.campo_buscar = "Fecha de Nacimiento, desde", "FechaNacimiento"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 7:
        col = self.campo_buscar = "Edad"
    elif idcolumna == 8:
        col = self.campo_buscar = "Cargo"
    elif idcolumna == 9:
        col, self.campo_buscar = "Salario Mensual", "SalarioMensual"
    elif idcolumna == 10:
        col, self.campo_buscar = "Cód. de Motivo de Descuento", "idMotivoDescuento"
    elif idcolumna == 12:
        col, self.campo_buscar = "Motivo de Descuento", "MotivoDescuento"
    elif idcolumna == 22:
        col, self.campo_buscar = "Cód. de Sanción", "idSancion"
    elif idcolumna == 23:
        col, self.campo_buscar = "Cód. de Motivo de Sanción", "idMotivoSancion"
    elif idcolumna == 14:
        col, self.campo_buscar = "Motivo de Sanción", "MotivoSancion"
    elif idcolumna == 15:
        col, self.campo_buscar = "Total a Descontar", "TotalCobrar"
    elif idcolumna == 24:
        col, self.campo_buscar = "Fecha de Modificación, desde", "FechaHora"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 17:
        col = self.campo_buscar = "Observaciones"
    elif idcolumna == 18:
        col, self.campo_buscar = "Alias de Usuario", "Alias"
    elif idcolumna == 19:
        col, self.campo_buscar = "Nro. Documento", "NroDocUsuario"
    elif idcolumna == 20:
        col, self.campo_buscar = "Nombre de Usuario", "NombreUsuario"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 5)
    valor2 = seleccion.get_value(iterador, 11)
    valor3 = seleccion.get_value(iterador, 16)
    valor4 = seleccion.get_value(iterador, 18)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
        "\nCódigo: " + valor0 + "\nNombre y Apellido: " + valor1 +
        "\nMotivo: " + valor2 + "\nFecha de Modificación: " + valor3 +
        "\nUsuario Responsable: " + valor4)

    self.obj("grilla").get_selection().unselect_all()
    self.obj("barraestado").push(0, "")

    if eleccion:
        conexion = Op.conectar(self.datos_conexion)
        Op.eliminar(conexion, self.tabla, valor0)
        conexion.commit()
        conexion.close()  # Finaliza la conexión
        cargar_grilla(self)


def listar_grilla(self):
    pass


def seleccion(self):
    pass
