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
        self.nav = origen

        arch = Op.archivo("rrhh_aguinaldos")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        self.obj("ventana").set_title("Creando Registro de Aguinaldo")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_01_2").set_max_length(12)
        self.obj("txt_02").set_max_length(10)
        self.obj("txt_05").set_max_length(100)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código del Aguinaldo")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Empleado cuyo Aguinaldo es registrado"))
        self.obj("txt_01_1").set_tooltip_text("Nombre y Apellido del Empleado")
        self.obj("txt_01_2").set_tooltip_text("Ingrese el Nro. de Documento del Empleado")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el Contrato del Empleado seleccionado"))
        self.obj("txt_02_1").set_tooltip_text("Cargo del Empleado dentro de la Empresa")
        self.obj("txt_02_2").set_tooltip_text("Salario Mensual del Empleado")
        self.obj("txt_03").set_tooltip_text(Mens.usar_boton("el Monto en base al cual será calculado el Aguinaldo"))
        self.obj("txt_04").set_tooltip_text("Monto a pagar como Aguinaldo")
        self.obj("txt_05").set_tooltip_text("Ingrese cualquier información adicional con respecto al Aguinaldo del Empleado")
        self.obj("txt_02").grab_focus()

        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_01_2"), self.obj("cmb_tipo_doc")
        self.txt_cod_cnt, self.txt_crg_cnt, self.txt_sal_cnt = self.obj("txt_02"), \
            self.obj("txt_02_1"), self.obj("txt_02_2")

        self.idPersona, self.borrar_contrato, self.idTipoDoc = None, not edit, -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")
        arch.connect_signals(self)

        self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
            self.nav.tabla + "_s", self.nav.campoid))
        self.obj("cmb_tipo_doc").set_active(0)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        cont = self.obj("txt_02").get_text()
        monto = self.obj("txt_04").get_text()

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        # Crear encabezado de Comprobante de Pago
        comp = Op.nuevoid(self.nav.datos_conexion, "comprobantepagos_s", "NroComprobante")
        sql = comp + ", " + cont + ", '" + str(date.today()) + "', " + \
            "'" + str(date.today()) + "', NULL, 1"
        Op.insertar(conexion, "comprobantepagos", sql)

        # Crear detalle de Comprobante de Pago (3 - Aguinaldo)
        sql = comp + ", 1, 3, " + monto + ", 1, NULL"
        Op.insertar(conexion, "comprobantepagos_detalles", sql)
        conexion.commit()

        # Agregar-Modificar registro de Aguinaldo
        cod = self.obj("txt_00").get_text()
        obs = self.obj("txt_05").get_text()
        obs = "NULL" if len(obs) == 0 else "'" + obs + "'"

        sql = cod + ", " + cont + ", " + comp + ", " + monto + ", " + obs
        Op.insertar(conexion, self.nav.tabla, sql)

        conexion.commit()
        conexion.close()  # Finaliza la conexión

        # Generar Comprobante de Pago
        from informes.rrhh_comprobantes import genera_comprobante_pago
        genera_comprobante_pago(self.nav.datos_conexion, comp)

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_empleado_clicked(self, objeto):
        from clases.llamadas import empleados
        empleados(self.nav.datos_conexion, self)

    def on_btn_contrato_clicked(self, objeto):
        condicion = None if len(self.obj("txt_01").get_text()) == 0 \
        else "idEmpleado = " + self.obj("txt_01").get_text()

        from clases.llamadas import contratos
        contratos(self.nav.datos_conexion, self, condicion)

    def on_btn_consulta_clicked(self, objeto):
        cont = self.obj("txt_02").get_text()

        if len(cont) > 0:
            conexion = Op.conectar(self.nav.datos_conexion)

            # Obtener monto total cobrado durante el presente año
            cursor = Op.consultar(conexion, "IFNULL(SUM(TotalPagar), 0)", "comprobantepagos_s",
                " WHERE (YEAR(FechaHoraExp) = YEAR(NOW())) AND (NroContrato = " + cont + ")")
            datos = cursor.fetchall()
            cant = cursor.rowcount

            if datos[0][0] == 0:
                Mens.informa_generico("Revise los datos",
                    "No se han encontrado registros de pagos realizados\n" +
                    "al Empleado relacionado al Contrato Nro. " + cont)
                total = Decimal(0.00)
            else:
                total = round(Decimal(datos[0][0]))
            self.obj("txt_03").set_text(str(total))

            # Cálculo del Aguinaldo
            monto = round(total / 12)
            self.obj("txt_04").set_text(str(monto))
        else:
            self.obj("barraestado").push(0, "Seleccione un Contrato primero, luego podrá consultar.")

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_01_2").get_text()) == 0 or len(self.obj("txt_02").get_text()) == 0 \
        or len(self.obj("txt_03").get_text()) == 0 or len(self.obj("txt_04").get_text()) == 0 \
        or self.idTipoDoc == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Cód. de Empleado", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Nro. de Contrato", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_04"), "Monto de Aguinaldo", self.obj("barraestado"), False):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar").set_sensitive(estado)

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
                elif objeto == self.obj("txt_03"):
                    self.on_btn_consulta_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
            tipo = "un Empleado"
        elif objeto == self.obj("txt_02"):
            tipo = "un Contrato"
        elif objeto == self.obj("txt_03"):
            tipo = "el Monto en base al cual será calculado el Aguinaldo"
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
                self.obj("txt_02_2").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                if Op.comprobar_numero(int, objeto, "Código", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion,
                        self.nav.tabla + "_s", self.nav.campoid, valor,
                        objeto, self.obj("btn_guardar"), self.obj("barraestado"),
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
                    cursor = Op.consultar(conexion, "idEmpleado, Cargo, SalarioMensual, Vigente",
                        "contratos_s", " WHERE NroContrato = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        if datos[0][3] == 1:
                            self.obj("txt_01").set_text(str(datos[0][0]))
                            self.obj("txt_02_1").set_text(datos[0][1])
                            self.obj("txt_02_2").set_text(str(round(datos[0][2])))

                            self.obj("barraestado").push(0, "")
                            self.borrar_contrato = False
                            self.focus_out_event(self.obj("txt_01"), 0)
                        else:
                            objeto.grab_focus()
                            self.obj("btn_guardar").set_sensitive(False)
                            self.obj("barraestado").push(0, "El Contrato seleccionado ya no se encuentra vigente.")
                    else:
                        objeto.grab_focus()
                        self.obj("btn_guardar").set_sensitive(False)
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
            self.obj("btn_guardar").set_sensitive(False)
            objeto.grab_focus()
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_01_2") if objeto == self.obj("txt_01") else self.obj("txt_01")
            otro.set_text("")
            self.obj("txt_01_1").set_text("")


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
    col6.set_sort_column_id(18)  # Para ordenarse usa la fila 18
    col7 = Op.columnas("Edad", celda0, 7, True, 100, 200)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Cargo", celda1, 8, True, 150)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Nro. de Comprobante", celda0, 9, True, 100, 200)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Fecha de Expedición", celda0, 10, True, 200)
    col10.set_sort_column_id(19)  # Para ordenarse usa la fila 19
    col11 = Op.columnas("Monto Total", celda2, 11, True, 100, 200)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Monto del Aguinaldo", celda2, 12, True, 100, 200)
    col12.set_sort_column_id(12)
    col13 = Op.columnas("Fecha de Modificación", celda0, 13, True, 200)
    col13.set_sort_column_id(20)  # Para ordenarse usa la fila 20
    col14 = Op.columnas("Observaciones", celda1, 14, True, 200)
    col14.set_sort_column_id(14)
    col15 = Op.columnas("Alias de Usuario", celda1, 15, True, 100, 200)
    col15.set_sort_column_id(15)
    col16 = Op.columnas("Nro. Documento", celda0, 16, True, 100, 200)
    col16.set_sort_column_id(16)
    col17 = Op.columnas("Nombre de Usuario", celda1, 17, True, 200)
    col17.set_sort_column_id(17)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8,
        col9, col10, col11, col12, col13, col14, col15, col16, col17]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(5)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 5)

    lista = ListStore(int, int, int, str, str, str, str, int, str,
        int, str, float, float, str, str, str, str, str, str, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar in ("FechaHora", "FechaHoraExp", "FechaNacimiento"):
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, "idAguinaldo, NroContrato, idEmpleado, " +
        "idTipoDocumento, NroDocumento, NombreApellido, FechaNacimiento, " +
        "Edad, Cargo, NroComprobante, FechaHoraExp, MontoTotal, Aguinaldo, " +
        "FechaHora, Observaciones, Alias, NroDocUsuario, NombreUsuario",
        self.tabla + "_s", opcion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        fechanac = "" if datos[i][6] is None else Cal.mysql_fecha(datos[i][6])
        fechacomp = "" if datos[i][10] is None else Cal.mysql_fecha_hora(datos[i][10])
        fechaexp = "" if datos[i][13] is None else Cal.mysql_fecha_hora(datos[i][13])

        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], datos[i][5], fechanac, datos[i][7], datos[i][8],
            datos[i][9], fechacomp, datos[i][11], datos[i][12], fechaexp,
            datos[i][14], datos[i][15], datos[i][16], datos[i][17],
            str(datos[i][6]), str(datos[i][10]), str(datos[i][13])])

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
    elif idcolumna == 18:
        col, self.campo_buscar = "Fecha de Nacimiento, desde", "FechaNacimiento"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 7:
        col = self.campo_buscar = "Edad"
    elif idcolumna == 8:
        col = self.campo_buscar = "Cargo"
    elif idcolumna == 9:
        col, self.campo_buscar = "Nro. de Comprobante", "NroComprobante"
    elif idcolumna == 19:
        col, self.campo_buscar = "Fecha de Expedición, desde", "FechaHoraExp"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 11:
        col, self.campo_buscar = "Monto Total", "MontoTotal"
    elif idcolumna == 12:
        col, self.campo_buscar = "Monto de Aguinaldo", "Aguinaldo"
    elif idcolumna == 20:
        col, self.campo_buscar = "Fecha de Modificación, desde", "FechaHora"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 14:
        col = self.campo_buscar = "Observaciones"
    elif idcolumna == 15:
        col, self.campo_buscar = "Alias de Usuario", "Alias"
    elif idcolumna == 16:
        col, self.campo_buscar = "Nro. Documento", "NroDocUsuario"
    elif idcolumna == 17:
        col, self.campo_buscar = "Nombre de Usuario", "NombreUsuario"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 5)
    valor2 = str(seleccion.get_value(iterador, 12))
    valor3 = seleccion.get_value(iterador, 15)
    valor4 = str(seleccion.get_value(iterador, 9))

    eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
        "\nCódigo: " + valor0 + "\nNombre y Apellido: " + valor1 +
        "\nMonto: " + valor2 + "\nUsuario Responsable: " + valor3)

    self.obj("grilla").get_selection().unselect_all()
    self.obj("barraestado").push(0, "")

    if eleccion:
        conexion = Op.conectar(self.datos_conexion)
        Op.eliminar(conexion, self.tabla, valor0)

        eleccion = Mens.pregunta_anular("Se ha eliminado el Aguinaldo seleccionado." +
            "\n¿Desea anular el Comprobante de Pago asociado a este?")
        if eleccion:
            Op.anular(conexion, "comprobantepagos", valor4)

        conexion.commit()
        conexion.close()  # Finaliza la conexión
        cargar_grilla(self)


def listar_grilla(self):
    pass


def seleccion(self):
    pass
