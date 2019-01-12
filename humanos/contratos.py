#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

        # Necesario para Vendedores
        self.datos_conexion = self.nav.datos_conexion

        arch = Op.archivo("rrhh_contratos")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Contratos")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))
        self.permiso_vendedores()

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_01_2").set_max_length(12)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código de Contrato")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Empleado con quien se celebró el Contrato"))
        self.obj("txt_01_2").set_tooltip_text("Ingrese el Nro. de Documento del Empleado")

        self.obj("txt_04").set_tooltip_text(Mens.usar_boton("la Fecha de Inicio de Actividades"))
        self.obj("txt_05").set_tooltip_text(Mens.usar_boton("la Fecha de Finalización de Actividades"))
        self.obj("txt_06").set_tooltip_text(Mens.usar_boton("la Fecha de Inicio del Periodo de Prueba"))
        self.obj("txt_07").set_tooltip_text(Mens.usar_boton("la Fecha de Finalización del Periodo de Prueba"))

        self.idTipoDoc = -1
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_01_2"), self.obj("cmb_tipo_doc")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_01_3"), self.obj("txt_01_4")

        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_cargo"), "cargos", "idCargo")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_contrato"), "tipocontratos", "idTipoContrato")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_periodo_pago"), "periodopagos", "idPeriodoPago")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_forma_pago"), "formapagos", "idFormaPago")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_salario"), "tiposalarios", "idTipoSalario")

        self.salariominimo = Op.obtener_salario_minimo(self.nav.datos_conexion)
        arch.connect_signals(self)

        self.obj("cmb_tipo_doc").set_active(0)
        self.obj("cmb_cargo").set_active(0)
        self.obj("cmb_tipo_contrato").set_active(0)
        self.obj("cmb_periodo_pago").set_active(0)
        self.obj("cmb_forma_pago").set_active(0)
        self.obj("cmb_tipo_salario").set_active(0)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            idper = str(seleccion.get_value(iterador, 1))
            tipodoc = seleccion.get_value(iterador, 2)
            nrodoc = seleccion.get_value(iterador, 3)
            nombre = seleccion.get_value(iterador, 4)
            direccion = seleccion.get_value(iterador, 6)
            telefono = seleccion.get_value(iterador, 7)

            direccion = "" if direccion is None else direccion
            telefono = "" if telefono is None else telefono

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(idper)
            self.obj("txt_01_1").set_text(nombre)
            self.obj("txt_01_2").set_text(nrodoc)
            self.obj("txt_01_3").set_text(direccion)
            self.obj("txt_01_4").set_text(telefono)

            # Asignación de Tipo de Documento en Combo
            model, i = self.obj("cmb_tipo_doc").get_model(), 0
            while model[i][0] != tipodoc: i += 1
            self.obj("cmb_tipo_doc").set_active(i)

            cargo = seleccion.get_value(iterador, 12)
            formapago = seleccion.get_value(iterador, 14)
            periodopago = seleccion.get_value(iterador, 16)
            tipocontrato = seleccion.get_value(iterador, 18)
            tiposalario = seleccion.get_value(iterador, 20)

            # Asignación de Cargo en Combo
            model, i = self.obj("cmb_cargo").get_model(), 0
            while model[i][0] != cargo: i += 1
            self.obj("cmb_cargo").set_active(i)

            # Asignación de Tipo de Contrato en Combo
            model, i = self.obj("cmb_tipo_contrato").get_model(), 0
            while model[i][0] != tipocontrato: i += 1
            self.obj("cmb_tipo_contrato").set_active(i)

            # Asignación de Periodo de Pago en Combo
            model, i = self.obj("cmb_periodo_pago").get_model(), 0
            while model[i][0] != periodopago: i += 1
            self.obj("cmb_periodo_pago").set_active(i)

            # Asignación de Forma de Pago en Combo
            model, i = self.obj("cmb_forma_pago").get_model(), 0
            while model[i][0] != formapago: i += 1
            self.obj("cmb_forma_pago").set_active(i)

            # Asignación de Tipo de Salario en Combo
            model, i = self.obj("cmb_tipo_salario").get_model(), 0
            while model[i][0] != tiposalario: i += 1
            self.obj("cmb_tipo_salario").set_active(i)

            # Salario
            minimo = True if seleccion.get_value(iterador, 34) == 1 else False
            cantsal = seleccion.get_value(iterador, 35)
            salario = str(seleccion.get_value(iterador, 24))

            self.obj("rad_minimo").set_active(minimo)
            if cantsal is not None:
                self.obj("txt_02").set_value(float(cantsal))
            self.obj("txt_03").set_text(salario)

            # Fechas
            fecha_ini = seleccion.get_value(iterador, 22)
            fecha_fin = seleccion.get_value(iterador, 23)
            prueba_ini = seleccion.get_value(iterador, 25)
            prueba_fin = seleccion.get_value(iterador, 26)

            self.obj("txt_04").set_text(fecha_ini)
            self.obj("txt_05").set_text(fecha_fin)
            self.obj("txt_06").set_text(prueba_ini)
            self.obj("txt_07").set_text(prueba_fin)

            self.fecha_ini = seleccion.get_value(iterador, 30)
            self.fecha_fin = seleccion.get_value(iterador, 31)
            self.prueba_ini = seleccion.get_value(iterador, 32)
            self.prueba_fin = seleccion.get_value(iterador, 33)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))

            self.obj("rad_minimo").set_active(True)
            self.fecha_ini = self.fecha_fin = self.prueba_ini = self.prueba_fin = None

        self.conexion = Op.conectar(self.nav.datos_conexion)
        self.principal_guardado = True

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_principal_contratos()
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def on_btn_horario_clicked(self, objeto):
        self.guardar_principal_contratos()

        from humanos.horarios import horarios
        horarios(self)

    def on_btn_vendedores_clicked(self, objeto):
        contrato = self.obj("txt_00").get_text()
        self.on_btn_guardar_clicked(0)

        from humanos.vendedores import funcion_abm
        funcion_abm(False, self, contrato)

    def on_btn_empleado_clicked(self, objeto):
        from clases.llamadas import empleados
        empleados(self.nav.datos_conexion, self)

    def on_btn_fecha_ini_clicked(self, objeto):
        self.obj("txt_04").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_04").set_text(lista[0])
            self.fecha_ini = lista[1]

    def on_btn_limpiar_fecha_ini_clicked(self, objeto):
        self.obj("txt_04").set_text("")
        self.fecha_ini = None

    def on_btn_fecha_fin_clicked(self, objeto):
        self.obj("txt_05").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_05").set_text(lista[0])
            self.fecha_fin = lista[1]

    def on_btn_limpiar_fecha_fin_clicked(self, objeto):
        self.obj("txt_05").set_text("")
        self.fecha_fin = None

    def on_btn_prueba_ini_clicked(self, objeto):
        self.obj("txt_06").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_06").set_text(lista[0])
            self.prueba_ini = lista[1]

    def on_btn_limpiar_prueba_ini_clicked(self, objeto):
        self.obj("txt_06").set_text("")
        self.prueba_ini = None

    def on_btn_prueba_fin_clicked(self, objeto):
        self.obj("txt_07").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_07").set_text(lista[0])
            self.prueba_fin = lista[1]

    def on_btn_limpiar_prueba_fin_clicked(self, objeto):
        self.obj("txt_07").set_text("")
        self.prueba_fin = None

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_04").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Cód. de Contrato", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Cód. de Empleado", self.obj("barraestado")):
                estado = True
            else:
                estado = False

        self.principal_guardado = False
        self.estadoedicion(estado)

    def on_txt_02_value_changed(self, objeto):
        cantidad = round(Decimal(self.obj("txt_02").get_value()), 2)
        salario = cantidad * self.salariominimo
        self.obj("txt_03").set_text(str(salario))

    def on_rad_toggled(self, objeto):
        estado = self.obj("rad_minimo").get_active()

        self.obj("txt_02").set_sensitive(estado)
        self.obj("txt_03").set_editable(not estado)
        self.obj("txt_03").set_property('can_focus', not estado)

        self.obj("txt_02").set_value(1.0)
        self.calculo_salario()

    def on_cmb_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            if objeto == self.obj("cmb_tipo_doc"):
                self.idTipoDoc = model[active][0]
                self.focus_out_event(self.obj("txt_01_2"), 0)
            elif objeto == self.obj("cmb_cargo"):
                self.idCargo = model[active][0]
            elif objeto == self.obj("cmb_tipo_contrato"):
                self.idTipoContrato = model[active][0]
            elif objeto == self.obj("cmb_periodo_pago"):
                self.idPeriodoPago = model[active][0]
                if self.idPeriodoPago != 1:  # No Mensual
                    self.obj("rad_personal").set_active(True)
                self.calculo_salario()
            elif objeto == self.obj("cmb_forma_pago"):
                self.idFormaPago = model[active][0]
            elif objeto == self.obj("cmb_tipo_salario"):
                self.idTipoSalario = model[active][0]
            self.verificacion(0)
        else:
            if objeto == self.obj("cmb_tipo_doc"):
                tipo = "Tipos de Documentos"
            elif objeto == self.obj("cmb_cargo"):
                tipo = "Cargos"
            elif objeto == self.obj("cmb_tipo_contrato"):
                tipo = "Tipos de Contratos"
            elif objeto == self.obj("cmb_periodo_pago"):
                tipo = "Periodos de Pago"
            elif objeto == self.obj("cmb_forma_pago"):
                tipo = "Formas de Pago"
            elif objeto == self.obj("cmb_tipo_salario"):
                tipo = "Tipos de Salario"
            self.obj("barraestado").push(0, "No existen registros de " + tipo + " en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
                    self.on_btn_empleado_clicked(0)
                elif objeto == self.obj("txt_04"):
                    self.on_btn_fecha_ini_clicked(0)
                elif objeto == self.obj("txt_05"):
                    self.on_btn_fecha_fin_clicked(0)
                elif objeto == self.obj("txt_06"):
                    self.on_btn_prueba_ini_clicked(0)
                elif objeto == self.obj("txt_07"):
                    self.on_btn_prueba_fin_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
            tipo = " Empleado"
        elif objeto == self.obj("txt_04"):
            tipo = "a Fecha de Inicio de Actividades"
        elif objeto == self.obj("txt_05"):
            tipo = "a Fecha de Finalización de Actividades"
        elif objeto == self.obj("txt_06"):
            tipo = "a Fecha de Inicio del Periodo de Prueba"
        elif objeto == self.obj("txt_07"):
            tipo = "a Fecha de Finalización del Periodo de Prueba"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un" + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_01"):  # Código de Empleado
                self.obj("txt_01_2").set_text("")
            elif objeto == self.obj("txt_01_2"):  # Nro. Documento de Empleado
                self.obj("txt_01").set_text("")

            if objeto == self.obj("txt_01") or (objeto == self.obj("txt_01_2") \
            and len(self.obj("txt_01").get_text()) == 0):
                self.obj("txt_01_1").set_text("")
                self.obj("txt_01_3").set_text("")
                self.obj("txt_01_4").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) and \
                Op.comprobar_numero(int, objeto, "Código", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion, "contratos_s",
                        self.nav.campoid, valor, self.obj("txt_00"),
                        self.estadoedicion, self.obj("barraestado"),
                        "El Código introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Empleado", self.obj("barraestado")):
                    self.buscar_empleados(objeto, "idPersona", valor, "Cód. de Empleado")

            elif objeto == self.obj("txt_01_2"):
                self.buscar_empleados(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDoc + "'", "Nro. de Documento")

            elif objeto in (self.obj("txt_04"), self.obj("txt_05")):
                if len(self.obj("txt_04").get_text()) > 0 and len(self.obj("txt_05").get_text()) > 0:
                    if Op.compara_fechas(self.nav.datos_conexion,
                    "'" + self.fecha_ini + "'", ">=", "'" + self.fecha_fin + "'"):
                        self.estadoedicion(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "La Fecha de Inicio NO puede ser posterior a la de Terminación.")
                    else:
                        self.obj("barraestado").push(0, "")

            elif objeto in (self.obj("txt_06"), self.obj("txt_07")):
                if len(self.obj("txt_06").get_text()) > 0 and len(self.obj("txt_07").get_text()) > 0:
                    if Op.compara_fechas(self.nav.datos_conexion,
                    "'" + self.prueba_ini + "'", ">=", "'" + self.prueba_fin + "'"):
                        self.estadoedicion(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "La Fecha de Inicio del Periodo de Prueba NO puede ser posterior a la de Terminación.")
                    else:
                        self.obj("barraestado").push(0, "")

    def buscar_empleados(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, "idPersona, RazonSocial, NroDocumento, " +
            "idTipoDocumento, DireccionPrincipal, TelefonoPrincipal", "personas_s",
            " WHERE " + campo + " = " + valor + " AND Empleado = 1")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            direc = "" if datos[0][4] is None else datos[0][4]
            telef = "" if datos[0][5] is None else datos[0][5]

            self.obj("txt_01").set_text(str(datos[0][0]))
            self.obj("txt_01_1").set_text(datos[0][1])
            self.obj("txt_01_2").set_text(datos[0][2])
            self.obj("txt_01_3").set_text(direc)
            self.obj("txt_01_4").set_text(telef)

            # Asignación de Tipo de Documento en Combo
            model, i = self.obj("cmb_tipo_doc").get_model(), 0
            while model[i][0] != datos[0][3]: i += 1
            self.obj("cmb_tipo_doc").set_active(i)

            self.obj("barraestado").push(0, "")
            self.verificacion(0)

        else:
            self.estadoguardar(False)
            objeto.grab_focus()
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_01_2") if objeto == self.obj("txt_01") else self.obj("txt_01")
            otro.set_text("")

            self.obj("txt_01_1").set_text("")
            self.obj("txt_01_3").set_text("")
            self.obj("txt_01_4").set_text("")

    def guardar_principal_contratos(self):
        if not self.principal_guardado:
            cod = self.obj("txt_00").get_text()
            emp = self.obj("txt_01").get_text()

            smin = "1" if self.obj("rad_minimo").get_active() else "0"
            cant = "NULL" if smin == "0" else str(round(self.obj("txt_02").get_value(), 2))
            sal = "NULL" if smin == "1" else  self.obj("txt_03").get_text()
            asist = "1" if self.obj("chk_asistencia").get_active() else "0"

            fecha_fin = "NULL" if self.fecha_fin is None else "'" + self.fecha_fin + "'"
            prueba_ini = "NULL" if self.prueba_ini is None else "'" + self.prueba_ini + "'"
            prueba_fin = "NULL" if self.prueba_fin is None else "'" + self.prueba_fin + "'"

            sql = cod + ", " + emp + ", " + str(self.idCargo) + ", " + \
                str(self.idFormaPago) + ", " + str(self.idPeriodoPago) + ", " + \
                str(self.idTipoContrato) + ", " + str(self.idTipoSalario) + ", " + \
                "'" + self.fecha_ini + "', " + fecha_fin + ", " + smin + ", " + \
                cant + ", " + sal + ", " + prueba_ini + ", " + prueba_fin + ", " + asist

            if not self.editando:
                Op.insertar(self.conexion, self.nav.tabla, sql)
            else:
                Op.modificar(self.conexion, self.nav.tabla, self.cond + ", " + sql)

            self.cond = cod  # Nuevo NroContrato original
            self.principal_guardado = self.editando = True

    def estadoedicion(self, estado):
        self.obj("buttonbox1").set_visible(estado)
        self.obj("btn_guardar").set_sensitive(estado)

    def calculo_salario(self):
        if self.idPeriodoPago == 4:  # Diario
            salario = self.salariominimo / 26
            self.obj("txt_03").set_text(str(round(salario, 2)))  # 70.156

        elif self.idPeriodoPago == 3:  # Semanal
            salario = self.salariominimo * 6 / 26
            self.obj("txt_03").set_text(str(round(salario, 2)))  # 420.936

        elif self.idPeriodoPago == 2:  # Quincenal
            salario = self.salariominimo * 12 / 26
            self.obj("txt_03").set_text(str(round(salario, 2)))  # 841.872

        else:  # Mensual
            self.obj("txt_03").set_text(str(self.salariominimo))  # 1.824.055

    def permiso_vendedores(self):
        self.obj("btn_vendedores").set_sensitive(False)

        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = conexion.cursor()
        cursor.execute("SELECT TABLE_NAME FROM vistas_s")
        dato_vista = cursor.fetchall()
        cant_vista = cursor.rowcount

        for i in range(0, cant_vista):
            vista = dato_vista[i][0]
            if vista == "vendedores_s":
                self.obj("btn_vendedores").set_sensitive(True)


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)
    celda2 = Op.celdas(1.0)

    col0 = Op.columnas("Número", celda0, 0, True, 75, 100)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Cód. Empleado", celda0, 1, True, 100, 150)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Tipo Doc. Identidad", celda0, 2, True, 200)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Nro. Doc. Identidad", celda0, 3, True, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Nombre y Apellido", celda1, 4, True, 150)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Edad", celda0, 5, True, 150)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Dirección", celda1, 6, True, 250)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Teléfono", celda1, 7, True, 250)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Cód. Tipo Seguro", celda0, 8, True, 150)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Tipo de Seguro", celda1, 9, True, 150, 200)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Nro. Seguro", celda0, 10, True, 150, 200)
    col10.set_sort_column_id(10)
    col11 = Op.columnas("ID Asegurado", celda0, 11, True, 150, 200)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Cód. Cargo", celda0, 12, True, 150, 200)
    col12.set_sort_column_id(12)
    col13 = Op.columnas("Cargo", celda1, 13, True, 150, 200)
    col13.set_sort_column_id(13)
    col14 = Op.columnas("Cód. Forma Pago", celda0, 14, True, 150, 200)
    col14.set_sort_column_id(14)
    col15 = Op.columnas("Forma de Pago", celda1, 15, True, 150, 200)
    col15.set_sort_column_id(15)
    col16 = Op.columnas("Cód. Periodo Pago", celda0, 16, True, 150, 200)
    col16.set_sort_column_id(16)
    col17 = Op.columnas("Periodo de Pago", celda1, 17, True, 150, 200)
    col17.set_sort_column_id(17)
    col18 = Op.columnas("Cód. Tipo Contrato", celda0, 18, True, 150, 200)
    col18.set_sort_column_id(18)
    col19 = Op.columnas("Tipo de Contrato", celda1, 19, True, 150, 200)
    col19.set_sort_column_id(19)
    col20 = Op.columnas("Cód. Tipo Salario", celda0, 20, True, 150, 200)
    col20.set_sort_column_id(20)
    col21 = Op.columnas("Tipo de Salario", celda1, 21, True, 150, 200)
    col21.set_sort_column_id(21)
    col22 = Op.columnas("Fecha de Inicio", celda0, 22, True, 150, 200)
    col22.set_sort_column_id(30)  # Para ordenarse usa la fila 30
    col23 = Op.columnas("Fecha de Término", celda0, 23, True, 150, 200)
    col23.set_sort_column_id(31)  # Para ordenarse usa la fila 31
    col24 = Op.columnas("Salario", celda2, 24, True, 150, 200)
    col24.set_sort_column_id(24)
    col25 = Op.columnas("Inicio de Periodo Prueba", celda0, 25, True, 150, 200)
    col25.set_sort_column_id(32)  # Para ordenarse usa la fila 32
    col26 = Op.columnas("Fin de Periodo Prueba", celda0, 26, True, 150, 200)
    col26.set_sort_column_id(33)  # Para ordenarse usa la fila 33
    col27 = Op.columnas("Alias de Usuario", celda1, 27, True, 100, 200)
    col27.set_sort_column_id(27)
    col28 = Op.columnas("Nombre de Usuario", celda1, 28, True, 200, 300)
    col28.set_sort_column_id(28)
    col29 = Op.columna_active("Anulado", 29)
    col29.set_sort_column_id(29)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10,
        col11, col12, col13, col14, col15, col16, col17, col18, col19, col20,
        col21, col22, col23, col24, col25, col26, col27, col28]

    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col29)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(4)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 4)

    lista = ListStore(int, int, str, str, str, int, str, str, int, str, str, str,
        int, str, int, str, int, str, int, str, int, str, str, str, float, str, str,
        str, str, int, str, str, str, str, int, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar in ("FechaFin", "FechaInicio", "PruebaFin", "PruebaInicio"):
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    if self.obj("rad_act").get_active() or self.obj("rad_ina").get_active():
        anulado = "1" if self.obj("rad_act").get_active() else "0"
        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += "Anulado = " + anulado

    condicion = ""
    if len(self.condicion) > 0:
        condicion = " WHERE " + self.condicion if len(opcion) == 0 \
        else " AND " + self.condicion

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", idEmpleado, idTipoDocumento, " +
        "NroDocumento, NombreApellido, Edad, DireccionPrincipal, TelefonoPrincipal, " +
        "idTipoSeguro, TipoSeguro, NroSeguroIPS, idAsegurado, idCargo, Cargo, " +
        "idFormaPago, FormaPago, idPeriodoPago, PeriodoPago, idTipoContrato, TipoContrato, " +
        "idTipoSalario, TipoSalario, FechaInicio, FechaFin, Salario, PruebaInicio, " +
        "PruebaFin, Alias, NombreApellidoUsuario, Anulado, SalarioMinimo, CantSalMinimo",
        self.tabla + "_s", opcion + condicion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        fechaini = Cal.mysql_fecha(datos[i][22])
        fechafin = Cal.mysql_fecha(datos[i][23]) if datos[i][23] is not None else ""
        pruebaini = Cal.mysql_fecha(datos[i][25]) if datos[i][25] is not None else ""
        pruebafin = Cal.mysql_fecha(datos[i][26]) if datos[i][26] is not None else ""

        ffin = None if datos[i][23] is None else str(datos[i][23])
        pini = None if datos[i][25] is None else str(datos[i][25])
        pfin = None if datos[i][26] is None else str(datos[i][26])
        cantsal = None if datos[i][31] is None else str(datos[i][31])

        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], datos[i][5], datos[i][6], datos[i][7], datos[i][8],
            datos[i][9], datos[i][10], datos[i][11], datos[i][12], datos[i][13],
            datos[i][14], datos[i][15], datos[i][16], datos[i][17], datos[i][18],
            datos[i][19], datos[i][20], datos[i][21], fechaini, fechafin,
            datos[i][24], pruebaini, pruebafin, datos[i][27], datos[i][28],
            datos[i][29], str(datos[i][22]), ffin, pini, pfin, datos[i][30], cantsal])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Número", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "Cód. Empleado", "idEmpleado"
    elif idcolumna == 2:
        col, self.campo_buscar = "Tipo Doc. Identidad", "idTipoDocumento"
    elif idcolumna == 3:
        col, self.campo_buscar = "Nro. Doc. Identidad", "NroDocumento"
    elif idcolumna == 4:
        col, self.campo_buscar = "Nombre y Apellido", "NombreApellido"
    elif idcolumna == 5:
        col = self.campo_buscar = "Edad"
    elif idcolumna == 6:
        col, self.campo_buscar = "Dirección Principal", "DireccionPrincipal"
    elif idcolumna == 7:
        col, self.campo_buscar = "Teléfono Principal", "TelefonoPrincipal"
    elif idcolumna == 8:
        col, self.campo_buscar = "Cód. Tipo Seguro", "idTipoSeguro"
    elif idcolumna == 9:
        col, self.campo_buscar = "Tipo de Seguro", "TipoSeguro"
    elif idcolumna == 10:
        col, self.campo_buscar = "Nro. Seguro", "NroSeguroIPS"
    elif idcolumna == 11:
        col, self.campo_buscar = "ID Asegurado", "idAsegurado"
    elif idcolumna == 12:
        col, self.campo_buscar = "Cód. Cargo", "idCargo"
    elif idcolumna == 13:
        col = self.campo_buscar = "Cargo"
    elif idcolumna == 14:
        col, self.campo_buscar = "Cód. Forma Pago", "idFormaPago"
    elif idcolumna == 15:
        col, self.campo_buscar = "Forma de Pago", "FormaPagoo"
    elif idcolumna == 16:
        col, self.campo_buscar = "Cód. Periodo Pago", "idPeriodoPago"
    elif idcolumna == 17:
        col, self.campo_buscar = "Periodo de Pago", "PeriodoPago"
    elif idcolumna == 18:
        col, self.campo_buscar = "Cód. Tipo Contrato", "idTipoContrato"
    elif idcolumna == 19:
        col, self.campo_buscar = "Tipo de Contrato", "TipoContrato"
    elif idcolumna == 20:
        col, self.campo_buscar = "Cód. Tipo Salario", "idTipoSalario"
    elif idcolumna == 21:
        col, self.campo_buscar = "Tipo de Salario", "TipoSalario"
    elif idcolumna == 30:
        col, self.campo_buscar = "Fecha de Inicio", "FechaInicio"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 31:
        col, self.campo_buscar = "Fecha de Término", "FechaFin"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 24:
        col = self.campo_buscar = "Salario"
    elif idcolumna == 32:
        col, self.campo_buscar = "Inicio de Periodo Prueba", "PruebaInicio"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 33:
        col, self.campo_buscar = "Fin de Periodo Prueba", "PruebaFin"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 27:
        col, self.campo_buscar = "Alias de Usuario", "Alias"
    elif idcolumna == 28:
        col, self.campo_buscar = "Nombre de Usuario", "NombreApellidoUsuario"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 4)
    valor2 = seleccion.get_value(iterador, 13)
    valor3 = str(seleccion.get_value(iterador, 24))

    eleccion = Mens.pregunta_anular("Seleccionó:\n\nNúmero: " + valor0 +
        "\nEmpleado: " + valor1 + "\nCargo: " + valor2 + "\nSalario: " + valor3)

    self.obj("grilla").get_selection().unselect_all()
    self.obj("barraestado").push(0, "")

    if eleccion:
        conexion = Op.conectar(self.datos_conexion)
        Op.anular(conexion, self.tabla, valor0)
        conexion.commit()
        conexion.close()  # Finaliza la conexión
        cargar_grilla(self)


def listar_grilla(self):
    from clases import listado
    from reportlab.platypus import Paragraph as Par
    from reportlab.lib.pagesizes import A4

    datos = self.obj("grilla").get_model()
    cant = len(datos)

    head = listado.tabla_celda_titulo()
    body_ce = listado.tabla_celda_centrado()
    body_iz = listado.tabla_celda_just_izquierdo()

    lista = [[Par("Número", head), Par("Nro. Documento", head), Par("Nombre y Apellido", head)]]
    for i in range(0, cant):
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][3], body_ce), Par(datos[i][4], body_iz)])

    listado.listado(self.titulo, lista, [100, 100, 200], A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        contrato = str(seleccion.get_value(iterador, 0))
        codempl = str(seleccion.get_value(iterador, 1))
        tipdoc = seleccion.get_value(iterador, 2)
        nrodoc = seleccion.get_value(iterador, 3)
        nombre = seleccion.get_value(iterador, 4)
        direc = seleccion.get_value(iterador, 6)
        telef = seleccion.get_value(iterador, 7)
        cargo = seleccion.get_value(iterador, 13)
        salario = seleccion.get_value(iterador, 24)

        direc = "" if direc is None else direc
        telef = "" if telef is None else telef

        self.origen.txt_cod_cnt.set_text(contrato)

        try:  # Cargo del Empleado
            self.origen.txt_crg_cnt.set_text(cargo)
        except:
            pass

        try:  # Salario del Empleado
            self.origen.txt_sal_cnt.set_text(salario)
        except:
            pass

        self.origen.txt_cod_per.set_text(codempl)
        self.origen.txt_rzn_scl.set_text(nombre)

        try:  # Combo que indica el Tipo de Documento de Identidad
            model, i = self.origen.cmb_tip_doc.get_model(), 0
            while model[i][0] != tipdoc: i += 1
            self.origen.cmb_tip_doc.set_active(i)
        except:
            pass

        try:  # Número de Documento de Identidad
            self.origen.txt_nro_doc.set_text(nrodoc)
        except:
            pass

        try:  # Dirección Principal
            self.origen.txt_dir_per.set_text(direc)
        except:
            pass

        try:  # Telefono Principal
            self.origen.txt_tel_per.set_text(telef)
        except:
            pass

        try:  # Se usa en Movimientos de Empleados
            self.origen.idPersona = valor0
        except:
            pass

        self.on_btn_salir_clicked(0)
    except:
        pass
