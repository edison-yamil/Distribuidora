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

        arch = Op.archivo("rrhh_permisos")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de " + self.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_01_2").set_max_length(12)
        self.obj("txt_02").set_max_length(10)
        self.obj("txt_03").set_max_length(20)
        self.obj("txt_08").set_max_length(100)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código del Permiso")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Empleado cuyo Permiso es registrado"))
        self.obj("txt_01_1").set_tooltip_text("Nombre y Apellido del Empleado")
        self.obj("txt_01_2").set_tooltip_text("Ingrese el Nro. de Documento del Empleado")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el Contrato del Empleado seleccionado"))
        self.obj("txt_02_1").set_tooltip_text("Cargo del Empleado dentro de la Empresa")
        self.obj("txt_03").set_tooltip_text("Ingrese el Número de Expediente del MJT por el cual se comunica el Permiso")
        self.obj("txt_04").set_tooltip_text(Mens.usar_boton("la Fecha del Expediente del Permiso del MJT"))
        self.obj("txt_05").set_tooltip_text(Mens.usar_boton("la Fecha de Inicio del Permiso del Empleado"))
        self.obj("txt_06").set_tooltip_text(Mens.usar_boton("la Fecha de Finalización del Permiso del Empleado"))
        self.obj("txt_07").set_tooltip_text("Tiempo de Duración, en Días, del Permiso del Empleado")
        self.obj("txt_08").set_tooltip_text("Ingrese cualquier información adicional con respecto al Permiso del Empleado")
        self.obj("txt_02").grab_focus()

        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_01_2"), self.obj("cmb_tipo_doc")
        self.txt_cod_cnt, self.txt_crg_cnt = self.obj("txt_02"), self.obj("txt_02_1")

        self.idPersona, self.borrar_contrato = None, not edit
        self.idTipoDoc = self.idMotivoPermiso = -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_motivo"), "motivopermisos", "idMotivoPermiso")

        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            idcont = str(seleccion.get_value(iterador, 1))
            idemp = str(seleccion.get_value(iterador, 2))
            tipodoc = seleccion.get_value(iterador, 3)
            nrodoc = seleccion.get_value(iterador, 4)
            nombre = seleccion.get_value(iterador, 5)
            cargo = seleccion.get_value(iterador, 8)
            motivo = seleccion.get_value(iterador, 9)
            fini = seleccion.get_value(iterador, 11)
            ffin = seleccion.get_value(iterador, 12)
            dias = str(seleccion.get_value(iterador, 13))
            exp = seleccion.get_value(iterador, 14)
            fexp = seleccion.get_value(iterador, 15)

            obs = seleccion.get_value(iterador, 16)
            obs = "" if obs is None else obs

            self.fechaini = seleccion.get_value(iterador, 21)
            self.fechafin = seleccion.get_value(iterador, 22)
            self.fechaexp = seleccion.get_value(iterador, 23)

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(idemp)
            self.obj("txt_01_1").set_text(nombre)
            self.obj("txt_01_2").set_text(nrodoc)
            self.obj("txt_02").set_text(idcont)
            self.obj("txt_02_1").set_text(cargo)
            self.obj("txt_03").set_text(exp)
            self.obj("txt_04").set_text(fexp)
            self.obj("txt_05").set_text(fini)
            self.obj("txt_06").set_text(ffin)
            self.obj("txt_07").set_text(dias)
            self.obj("txt_08").set_text(obs)

            # Asignación de Tipo de Documento en Combo
            model, i = self.obj("cmb_tipo_doc").get_model(), 0
            while model[i][0] != tipodoc: i += 1
            self.obj("cmb_tipo_doc").set_active(i)

            # Asignación de Motivo en Combo
            model, i = self.obj("cmb_motivo").get_model(), 0
            while model[i][0] != motivo: i += 1
            self.obj("cmb_motivo").set_active(i)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))
            self.obj("cmb_tipo_doc").set_active(0)
            self.obj("cmb_motivo").set_active(0)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        cod = self.obj("txt_00").get_text()
        cont = self.obj("txt_02").get_text()
        exp = self.obj("txt_03").get_text()
        obs = self.obj("txt_08").get_text()
        obs = "NULL" if len(obs) == 0 else "'" + obs + "'"

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        sql = cod + ", " + cont + ", " + str(self.idMotivoPermiso) + ", " + \
            "'" + self.fechaini + "', '" + self.fechafin + "', " + \
            "'" + exp + "', '" + self.fechaexp + "', " + obs

        if not self.editando:
            Op.insertar(conexion, self.nav.tabla, sql)
        else:
            Op.modificar(conexion, self.nav.tabla, self.cond + ", " + sql)

        conexion.commit()
        conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_expedir_clicked(self, objeto):
        pass

    def on_btn_empleado_clicked(self, objeto):
        from clases.llamadas import empleados
        empleados(self.nav.datos_conexion, self)

    def on_btn_contrato_clicked(self, objeto):
        condicion = None if len(self.obj("txt_01").get_text()) == 0 \
        else "idEmpleado = " + self.obj("txt_01").get_text()

        from clases.llamadas import contratos
        contratos(self.nav.datos_conexion, self, condicion)

    def on_btn_fecha_expediente_clicked(self, objeto):
        self.obj("txt_04").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_04").set_text(lista[0])
            self.fechaexp = lista[1]

    def on_btn_limpiar_fecha_expediente_clicked(self, objeto):
        self.obj("txt_04").set_text("")
        self.obj("txt_04").grab_focus()

    def on_btn_fecha_ini_clicked(self, objeto):
        self.obj("txt_05").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_05").set_text(lista[0])
            self.fechaini = lista[1]

    def on_btn_limpiar_fecha_ini_clicked(self, objeto):
        self.obj("txt_05").set_text("")
        self.obj("txt_05").grab_focus()

    def on_btn_fecha_fin_clicked(self, objeto):
        self.obj("txt_06").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_06").set_text(lista[0])
            self.fechafin = lista[1]

    def on_btn_limpiar_fecha_fin_clicked(self, objeto):
        self.obj("txt_06").set_text("")
        self.obj("txt_06").grab_focus()

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_01_2").get_text()) == 0 or len(self.obj("txt_02").get_text()) == 0 \
        or len(self.obj("txt_03").get_text()) == 0 or len(self.obj("txt_04").get_text()) == 0 \
        or len(self.obj("txt_05").get_text()) == 0 or len(self.obj("txt_06").get_text()) == 0 \
        or self.idTipoDoc == -1 or self.idMotivoPermiso == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Cód. de Empleado", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Nro. de Contrato", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.estadoguardar(estado)

    def on_cmb_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            if objeto == self.obj("cmb_tipo_doc"):
                self.idTipoDoc = model[active][0]
                self.focus_out_event(self.obj("txt_01_2"), 0)  # Nro. Documento

            elif objeto == self.obj("cmb_motivo"):
                self.idMotivoPermiso = model[active][0]
        else:
            if objeto == self.obj("cmb_tipo_doc"):
                tipo = "Tipos de Documentos"
            elif objeto == self.obj("cmb_motivo"):
                tipo = "Motivos de Permiso"
            self.obj("barraestado").push(0, "No existen registros de " + tipo + " en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
                    self.on_btn_empleado_clicked(0)
                elif objeto == self.obj("txt_02"):
                    self.on_btn_contrato_clicked(0)
                elif objeto == self.obj("txt_04"):
                    self.on_btn_fecha_expediente_clicked(0)
                elif objeto == self.obj("txt_05"):
                    self.on_btn_fecha_ini_clicked(0)
                elif objeto == self.obj("txt_06"):
                    self.on_btn_fecha_fin_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
            tipo = "un Empleado"
        elif objeto == self.obj("txt_02"):
            tipo = "un Contrato"
        elif objeto == self.obj("txt_04"):
            tipo = "la Fecha del Expediente del MJT"
        elif objeto == self.obj("txt_05"):
            tipo = "la Fecha de Inicio del Periodo de Permiso"
        elif objeto == self.obj("txt_06"):
            tipo = "la Fecha de Finalización del Periodo de Permiso"
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
                            self.estadoguardar(False)
                            self.obj("barraestado").push(0, "El Contrato seleccionado ya no se encuentra vigente.")
                    else:
                        objeto.grab_focus()
                        self.estadoguardar(False)
                        self.obj("barraestado").push(0, "El Nro. de Contrato no es válido.")

            elif objeto == self.obj("txt_04"):
                self.obj("barraestado").push(0, "")

            elif objeto in (self.obj("txt_05"), self.obj("txt_06")):
                if len(self.obj("txt_05").get_text()) > 0 \
                and len(self.obj("txt_06").get_text()) > 0:
                    if Op.compara_fechas(self.nav.datos_conexion,
                    "'" + self.fechaini + "'", ">", "'" + self.fechafin + "'"):
                        self.estadoguardar(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "La Fecha de Inicio del Periodo de Permiso NO puede ser posterior a la de Finalización.")
                    else:
                        # Cálculo de la Cantidad de Días
                        dias = str(Cal.cantidad_dias(self.fechaini, self.fechafin))
                        self.obj("txt_07").set_text(dias)
                        self.obj("barraestado").push(0, "")

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

    def estadoguardar(self, estado):
        self.obj("btn_guardar").set_sensitive(estado)
        self.obj("btn_expedir").set_sensitive(estado)


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
    col6.set_sort_column_id(20)  # Para ordenarse usa la fila 20
    col7 = Op.columnas("Edad", celda0, 7, True, 100, 200)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Cargo", celda1, 8, True, 150)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Cód. Motivo", celda0, 9, True, 100, 200)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Motivo de Permiso", celda1, 10, True, 200)
    col10.set_sort_column_id(10)
    col11 = Op.columnas("Fecha de Inicio", celda0, 11, True, 200)
    col11.set_sort_column_id(21)  # Para ordenarse usa la fila 21
    col12 = Op.columnas("Fecha de Finalización", celda0, 12, True, 200)
    col12.set_sort_column_id(22)  # Para ordenarse usa la fila 22
    col13 = Op.columnas("Cantidad de Días", celda0, 13, True, 100, 200)
    col13.set_sort_column_id(13)
    col14 = Op.columnas("Nro. de Expediente", celda0, 14, True, 100, 200)
    col14.set_sort_column_id(14)
    col15 = Op.columnas("Fecha de Expediente", celda0, 15, True, 200)
    col15.set_sort_column_id(23)  # Para ordenarse usa la fila 23
    col16 = Op.columnas("Observaciones", celda1, 16, True, 200)
    col16.set_sort_column_id(16)
    col17 = Op.columnas("Alias de Usuario", celda1, 17, True, 100, 200)
    col17.set_sort_column_id(17)
    col18 = Op.columnas("Nro. Documento", celda0, 18, True, 100, 200)
    col18.set_sort_column_id(18)
    col19 = Op.columnas("Nombre de Usuario", celda1, 19, True, 200)
    col19.set_sort_column_id(19)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10,
        col11, col12, col13, col14, col15, col16, col17, col18, col19]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(5)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 5)

    lista = ListStore(int, int, int, str, str, str, str, int, str, int, str,
        str, str, int, str, str, str, str, str, str, str, str, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar in ("FechaInicio", "FechaFin", "FechaExpediente", "FechaNacimiento"):
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, "idPermiso, NroContrato, idEmpleado, " +
        "idTipoDocumento, NroDocumento, NombreApellido, FechaNacimiento, " +
        "Edad, Cargo, idMotivoPermiso, MotivoPermiso, FechaInicio, FechaFin, " +
        "CantDias, NroExpediente, FechaExpediente, Observaciones, " +
        "Alias, NroDocUsuario, NombreUsuario", self.tabla + "_s",
        opcion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        fechanac = "" if datos[i][6] is None else Cal.mysql_fecha(datos[i][6])
        fechaini = "" if datos[i][11] is None else Cal.mysql_fecha(datos[i][11])
        fechafin = "" if datos[i][12] is None else Cal.mysql_fecha(datos[i][12])
        fechaexp = "" if datos[i][15] is None else Cal.mysql_fecha(datos[i][15])

        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], datos[i][5], fechanac, datos[i][7], datos[i][8],
            datos[i][9], datos[i][10], fechaini, fechafin, datos[i][13],
            datos[i][14], fechaexp, datos[i][16], datos[i][17], datos[i][18], datos[i][19],
            str(datos[i][6]), str(datos[i][11]), str(datos[i][12]), str(datos[i][15])])

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
    elif idcolumna == 20:
        col, self.campo_buscar = "Fecha de Nacimiento, desde", "FechaNacimiento"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 7:
        col = self.campo_buscar = "Edad"
    elif idcolumna == 8:
        col = self.campo_buscar = "Cargo"
    elif idcolumna == 9:
        col, self.campo_buscar = "Cód. de Motivo de Permiso", "idMotivoPermiso"
    elif idcolumna == 10:
        col, self.campo_buscar = "Motivo de Permiso", "MotivoPermiso"
    elif idcolumna == 21:
        col, self.campo_buscar = "Fecha de Inicio, desde", "FechaInicio"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 22:
        col, self.campo_buscar = "Fecha de Finalización, desde", "FechaFin"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 13:
        col, self.campo_buscar = "Cantidad de Días", "CantDias"
    elif idcolumna == 14:
        col, self.campo_buscar = "Nro. de Expediente", "NroExpediente"
    elif idcolumna == 23:
        col, self.campo_buscar = "Fecha de Expediente, desde", "FechaExpediente"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 16:
        col = self.campo_buscar = "Observaciones"
    elif idcolumna == 17:
        col, self.campo_buscar = "Alias de Usuario", "Alias"
    elif idcolumna == 18:
        col, self.campo_buscar = "Nro. Documento", "NroDocUsuario"
    elif idcolumna == 19:
        col, self.campo_buscar = "Nombre de Usuario", "NombreUsuario"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 5)
    valor2 = seleccion.get_value(iterador, 11)
    valor3 = seleccion.get_value(iterador, 12)
    valor4 = seleccion.get_value(iterador, 17)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
        "\nCódigo: " + valor0 + "\nNombre y Apellido: " + valor1 +
        "\nFecha de Inicio: " + valor2 + "\nFecha de Finalización: " + valor3 +
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
