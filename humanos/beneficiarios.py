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

        arch = Op.archivo("rrhh_beneficiarios")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(500, 550)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de " + self.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)   # Código
        self.obj("txt_00_2").set_max_length(12)   # Nro. Doc. (Empleado)
        self.obj("txt_01").set_max_length(10)   # Código
        self.obj("txt_01_2").set_max_length(12)   # Nro. Doc. (Familiar)
        self.obj("txt_02").set_max_length(100)   # Observaciones

        self.obj("txt_00").set_tooltip_text(Mens.usar_boton("el Empleado cotizante en IPS"))
        self.obj("txt_00_1").set_tooltip_text("Nombre y Apellido del Empleado")
        self.obj("txt_00_2").set_tooltip_text("Ingrese el Nro. de Documento del Empleado")
        self.obj("txt_00_3").set_tooltip_text("Número de Seguro (en IPS) del Empleado")
        self.obj("txt_00_4").set_tooltip_text("Identificador del Asegurado en IPS")
        self.obj("txt_00_5").set_tooltip_text("Sexo del Empleado")
        self.obj("txt_00_6").set_tooltip_text("Nacionalidad del Empleado")
        self.obj("txt_00_7").set_tooltip_text("Estado Civil del Empleado")
        self.obj("txt_00_8").set_tooltip_text("Fecha de Nacimiento del Empleado")
        self.obj("txt_00_9").set_tooltip_text("Lugar de Nacimiento del Empleado")
        self.obj("txt_00_10").set_tooltip_text("Dirección Actual del Empleado")
        self.obj("txt_00_11").set_tooltip_text("Barrio de la Dirección del Empleado")
        self.obj("txt_00_12").set_tooltip_text("Ciudad o Distrito de la Dirección del Empleado")
        self.obj("txt_00_13").set_tooltip_text("Teléfono Laboral del Empleado")
        self.obj("txt_00_14").set_tooltip_text("Teléfono Particular del Empleado")
        self.obj("txt_00_15").set_tooltip_text("Número de Celular del Empleado")
        self.obj("txt_00_16").set_tooltip_text("Dirección de Correo Electrónico del Empleado")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Familiar beneficiado por el Seguro"))
        self.obj("txt_01_1").set_tooltip_text("Nombre y Apellido del Familiar")
        self.obj("txt_01_2").set_tooltip_text("Ingrese el Nro. de Documento del Familiar")
        self.obj("txt_01_3").set_tooltip_text("Fecha de Nacimiento del Familiar")
        self.obj("txt_01_4").set_tooltip_text("Sexo del Familiar")
        self.obj("txt_02").set_tooltip_text("Ingrese una Observación relativa al Beneficiario")

        self.idTipoDocEmpleado = self.idTipoDocFamiliar = self.idTipoParentesco = -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc_emp"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc_ben"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_parentesco"), "tipoparentescos", "idTipoParentesco")

        self.config_grilla_beneficiarios()
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond_empleado = str(seleccion.get_value(iterador, 0))

            self.obj("txt_00").set_text(self.cond_empleado)
            self.focus_out_event(self.obj("txt_00"), 0)

            self.cargar_grilla_beneficiarios()
            self.estadoguardar(True)
        else:
            self.obj("cmb_tipo_doc_emp").set_active(0)
            self.obj("cmb_tipo_doc_ben").set_active(0)
            self.obj("cmb_parentesco").set_active(0)
            self.estadoguardar(False)

        self.conexion = Op.conectar(self.nav.datos_conexion)
        self.estadoedicion(False)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def on_btn_expedir_clicked(self, objeto):
        pass

    def on_btn_empleado_clicked(self, objeto):
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_00"), self.obj("txt_00_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_00_2"), self.obj("cmb_tipo_doc_emp")

        from clases.llamadas import empleados
        empleados(self.nav.datos_conexion, self)

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_00_2").get_text()) == 0 \
        or self.idTipoDocEmpleado == -1:
            estado = False
        else:
            estado = Op.comprobar_numero(int, self.obj("txt_00"),
                "Código de Empleado", self.obj("barraestado"))
        self.estadoguardar(estado)

    def on_cmb_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            if objeto == self.obj("cmb_tipo_doc_emp"):
                self.idTipoDocEmpleado = model[active][0]
                self.focus_out_event(self.obj("txt_00_2"), 0)  # Nro. Documento

            elif objeto == self.obj("cmb_tipo_doc_ben"):
                self.idTipoDocFamiliar = model[active][0]
                self.focus_out_event(self.obj("txt_01_2"), 0)  # Nro. Documento

            elif objeto == self.obj("cmb_parentesco"):
                self.idTipoParentesco = model[active][0]
        else:
            if objeto in (self.obj("cmb_tipo_doc_emp"), self.obj("cmb_tipo_doc_ben")):
                tipo = "Tipos de Documentos"
            elif objeto == self.obj("cmb_parentesco"):
                tipo = "Tipos de Parentesco"
            self.obj("barraestado").push(0, "No existen registros de " + tipo + " en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto in (self.obj("txt_00"), self.obj("txt_00_2")):
                    self.on_btn_empleado_clicked(0)
                elif objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
                    self.on_btn_familiar_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_00"), self.obj("txt_00_2")):
            tipo = "Empleado"
        elif objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
            tipo = "Familiar Beneficiario"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un " + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_00"):  # Código de Empleado
                self.obj("txt_00_2").set_text("")
            elif objeto == self.obj("txt_01"):  # Código de Beneficiario
                self.obj("txt_01_2").set_text("")

            if objeto == self.obj("txt_00") or (objeto == self.obj("txt_00_2") \
            and len(self.obj("txt_00").get_text()) == 0):
                self.limpiar_empleado()

            if objeto == self.obj("txt_01") or (objeto == self.obj("txt_01_2") \
            and len(self.obj("txt_01").get_text()) == 0):
                self.obj("txt_01_1").set_text("")
                self.obj("txt_01_3").set_text("")
                self.obj("txt_01_4").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                if Op.comprobar_numero(int, objeto, "Cód. de Empleado", self.obj("barraestado")):
                    self.buscar_empleado(objeto, "idPersona", valor, "Cód. de Empleado")

            elif objeto == self.obj("txt_00_2"):
                self.buscar_empleado(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDocEmpleado + "'",
                    "Nro. de Documento del Empleado")

            elif objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Beneficiario", self.obj("barraestado")):
                    self.buscar_familiar(objeto, "idPersona", valor, "Cód. de Beneficiario")

            elif objeto == self.obj("txt_01_2"):
                self.buscar_familiar(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDocFamiliar + "'",
                    "Nro. de Documento del Beneficiario")

    def buscar_empleado(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, "idPersona, RazonSocial, NroDocumento, " +
            "idTipoDocumento, NroSeguroIPS, idAsegurado, Genero, Nacionalidad, " +
            "EstadoCivil, FechaNacimiento, LugarNacimiento", "personas_s",
            " WHERE " + campo + " = " + valor + " AND Empleado = 1")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        if cant > 0:
            nro_seg = "" if datos[0][4] is None else datos[0][4]
            id_aseg = "" if datos[0][5] is None else datos[0][5]

            self.obj("txt_00").set_text(str(datos[0][0]))
            self.obj("txt_00_1").set_text(datos[0][1])
            self.obj("txt_00_2").set_text(datos[0][2])
            self.obj("txt_00_3").set_text(nro_seg)
            self.obj("txt_00_4").set_text(id_aseg)
            self.obj("txt_00_5").set_text(datos[0][6])
            self.obj("txt_00_6").set_text(datos[0][7])
            self.obj("txt_00_7").set_text(datos[0][8])
            self.obj("txt_00_8").set_text(Cal.mysql_fecha(datos[0][9]))
            self.obj("txt_00_9").set_text(datos[0][10])

            # Asignación de Tipo de Documento en Combo
            model, i = self.obj("cmb_tipo_doc_emp").get_model(), 0
            while model[i][0] != datos[0][3]: i += 1
            self.obj("cmb_tipo_doc_emp").set_active(i)

            # Buscar Dirección Actual
            cursor = Op.consultar(conexion, "CONCAT(Direccion, " +
                "IFNULL(CONCAT(' Nº ', NroCasa), '')), " +
                "Barrio, Ciudad", "personas_direcciones_s",
                " WHERE idPersona = " + self.obj("txt_00").get_text())
            datos = cursor.fetchall()

            if cursor.rowcount > 0:
                self.obj("txt_00_10").set_text(datos[0][0])
                self.obj("txt_00_11").set_text(datos[0][1])  # Barrio
                self.obj("txt_00_12").set_text(datos[0][2])  # Ciudad

            # Buscar Teléfono Laboral (2)
            cursor = Op.consultar(conexion, "Descripcion", "personas_mediocontactos_s",
                " WHERE idPersona = " + self.obj("txt_00").get_text() +
                " AND idTipoMedioContacto = 2")
            datos = cursor.fetchall()

            if cursor.rowcount > 0:
                medio = "" if len(datos[0][0]) == 0 else datos[0][0]
                self.obj("txt_00_13").set_text(medio)

            # Buscar Teléfono Particular (1)
            cursor = Op.consultar(conexion, "Descripcion", "personas_mediocontactos_s",
                " WHERE idPersona = " + self.obj("txt_00").get_text() +
                " AND idTipoMedioContacto = 1")
            datos = cursor.fetchall()

            if cursor.rowcount > 0:
                medio = "" if len(datos[0][0]) == 0 else datos[0][0]
                self.obj("txt_00_14").set_text(medio)

            # Buscar Teléfono Móvil o Celular (3)
            cursor = Op.consultar(conexion, "Descripcion", "personas_mediocontactos_s",
                " WHERE idPersona = " + self.obj("txt_00").get_text() +
                " AND idTipoMedioContacto = 3")
            datos = cursor.fetchall()

            if cursor.rowcount > 0:
                medio = "" if len(datos[0][0]) == 0 else datos[0][0]
                self.obj("txt_00_15").set_text(medio)

            # Buscar Correo Electrónico (4)
            cursor = Op.consultar(conexion, "Descripcion", "personas_mediocontactos_s",
                " WHERE idPersona = " + self.obj("txt_00").get_text() +
                " AND idTipoMedioContacto = 4")
            datos = cursor.fetchall()

            if cursor.rowcount > 0:
                medio = "" if len(datos[0][0]) == 0 else datos[0][0]
                self.obj("txt_00_16").set_text(medio)

            # Verificar si el Empleado ya fue registrado
            cursor = Op.consultar(conexion, "idEmpleado", "beneficiarios_s",
                " WHERE idEmpleado = " + self.obj("txt_00").get_text())
            datos = cursor.fetchall()
            cant = cursor.rowcount

            conexion.close()  # Finaliza la conexión

            if cant > 0:
                if len(self.obj("grilla").get_model()) > 0:  # Ya hay datos cargados
                    eleccion = Mens.pregunta_generico("¿Qué Desea?",
                        "Este Empleado ya posee familiares beneficiados con el Seguro de IPS")

            # - Si hay datos cargados preguntar si desea vincularlos al empleado actual o eliminarlos
            # - - modificar o eliminar (se usa condicion)

            self.cond_empleado = self.obj("txt_00").get_text()
            self.cargar_grilla_beneficiarios()

            self.obj("barraestado").push(0, "")
            self.verificacion(0)

        else:
            conexion.close()  # Finaliza la conexión

            objeto.grab_focus()
            self.estadoguardar(False)
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_00_2") if objeto == self.obj("txt_00") else self.obj("txt_00")
            otro.set_text("")
            self.limpiar_empleado()

    def buscar_familiar(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, "idPersona, RazonSocial, NroDocumento, " +
            "idTipoDocumento, FechaNacimiento, Genero", "personas_s",
            " WHERE " + campo + " = " + valor + " AND Empleado <> 1 " +
            "AND Empresa <> 1")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            self.obj("txt_01").set_text(str(datos[0][0]))
            self.obj("txt_01_1").set_text(datos[0][1])
            self.obj("txt_01_2").set_text(datos[0][2])
            self.obj("txt_01_3").set_text(Cal.mysql_fecha(datos[0][4]))
            self.obj("txt_01_4").set_text(datos[0][5])

            # Asignación de Tipo de Documento en Combo
            model, i = self.obj("cmb_tipo_doc_ben").get_model(), 0
            while model[i][0] != datos[0][3]: i += 1
            self.obj("cmb_tipo_doc_ben").set_active(i)

            self.obj("barraestado").push(0, "")
            self.verificacion_benef(0)

            # Verificar que no se haya regitrado ya como Beneficiario por el Empleado actual
            if Op.comprobar_unique(self.conexion, "beneficiarios_s",
                "idFamiliar", self.obj("txt_01").get_text() +
                " AND idEmpleado = " + self.obj("txt_00").get_text(),
                self.obj("txt_01"), self.obj("btn_guardar_benef"), self.obj("barraestado"),
                "El Familiar introducido ya ha sido registado."):

                # Si no encuentra coincidencias verifica si está registrado por otro Empleado
                Op.comprobar_unique(self.nav.datos_conexion, "beneficiarios_s",
                    "idFamiliar", valor, self.obj("txt_00"),
                    self.obj("btn_guardar_benef"), self.obj("barraestado"),
                    "El Familiar introducido ha sido registado por otro Empleado.")

        else:
            objeto.grab_focus()
            self.obj("btn_guardar_benef").set_sensitive(False)
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_01_2") if objeto == self.obj("txt_01") else self.obj("txt_01")
            otro.set_text("")

            self.obj("txt_01_1").set_text("")
            self.obj("txt_01_3").set_text("")
            self.obj("txt_01_4").set_text("")

    def limpiar_empleado(self):
        self.obj("txt_00_1").set_text("")
        self.obj("txt_00_3").set_text("")
        self.obj("txt_00_4").set_text("")
        self.obj("txt_00_5").set_text("")
        self.obj("txt_00_6").set_text("")
        self.obj("txt_00_7").set_text("")
        self.obj("txt_00_8").set_text("")
        self.obj("txt_00_9").set_text("")
        self.obj("txt_00_10").set_text("")
        self.obj("txt_00_11").set_text("")
        self.obj("txt_00_12").set_text("")
        self.obj("txt_00_13").set_text("")
        self.obj("txt_00_14").set_text("")
        self.obj("txt_00_15").set_text("")
        self.obj("txt_00_16").set_text("")

    def estadoguardar(self, estado):
        self.obj("buttonbox_abm").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)

        # Obligatoriamente debe poseer Beneficiarios para poder Guardar
        estado = True if estado and len(self.obj("grilla").get_model()) > 0 else False

        self.obj("btn_guardar").set_sensitive(estado)
        self.obj("btn_expedir").set_sensitive(estado)

    def estadoedicion(self, estado):
        self.obj("vbox1").set_visible(not estado)
        self.obj("btn_cancelar").set_sensitive(not estado)

        self.obj("vbox2").set_visible(estado)
        self.obj("buttonbox_benef").set_visible(estado)

##### Beneficiarios ####################################################

    def config_grilla_beneficiarios(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)

        col0 = Op.columnas("Cód. Familiar", celda0, 0, True, 100, 200)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Tipo Doc. Identidad", celda0, 1, True, 100, 200)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Nro. Doc. Identidad", celda0, 2, True, 100, 200)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Nombre y Apellido", celda1, 3, True, 250)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Fecha de Nacimiento", celda1, 4, True, 200)
        col4.set_sort_column_id(11)  # Para ordenarse usa la fila 11
        col5 = Op.columnas("Edad", celda0, 5, True, 100, 200)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Cód. Género", celda0, 6, True, 100, 200)
        col6.set_sort_column_id(6)
        col7 = Op.columnas("Género", celda1, 7, True, 150)
        col7.set_sort_column_id(7)
        col8 = Op.columnas("Cód. Tipo Parent.", celda0, 8, True, 100, 200)
        col8.set_sort_column_id(8)
        col9 = Op.columnas("Tipo de Parentesco", celda1, 9, True, 150)
        col9.set_sort_column_id(9)
        col10 = Op.columnas("Observaciones", celda1, 10, True, 200)
        col10.set_sort_column_id(10)

        lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(3)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, str, str, str, int, str, str, int, str, str, str)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_beneficiarios(self):
        cursor = Op.consultar(self.conexion, "idFamiliar, idTipoDocFamiliar, " +
            "NroDocFamiliar, NombreApellidoFamiliar, FechaNacFamiliar, " +
            "EdadFamiliar, idGeneroFamiliar, GeneroFamiliar, " +
            "idTipoParentesco, TipoParentesco, Observaciones", self.nav.tabla + "_s",
            " WHERE idEmpleado = " + self.obj("txt_00").get_text() +
            " ORDER BY idFamiliar")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2],
                datos[i][3], Cal.mysql_fecha(datos[i][4]), datos[i][5],
                datos[i][6], datos[i][7], datos[i][8], datos[i][9],
                datos[i][10], str(datos[i][4])])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_clicked(self, objeto):
        self.editando_beneficiario = False
        self.funcion_beneficiarios()

    def on_btn_modificar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.cond_beneficiario = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Beneficiarios. Luego presione Modificar.")
        else:
            self.editando_beneficiario = True
            self.funcion_beneficiarios()

    def on_btn_eliminar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            fam = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Beneficiarios. Luego presione Eliminar.")
        else:
            emp = self.obj("txt_00").get_text()
            nomb = seleccion.get_value(iterador, 3)
            edad = str(seleccion.get_value(iterador, 5))
            par = seleccion.get_value(iterador, 9)

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Cód. Familiar: " + fam + "\nNombre y Apellido: " + nomb +
                "\nEdad: " + edad + "\nParentesco: " + par)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, self.nav.tabla, emp + ", " + fam)
                self.cargar_grilla_beneficiarios()

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_clicked(0)

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla").set_search_column(i)

##### Agregar-Modificar Beneficiarios ##################################

    def funcion_beneficiarios(self):
        if self.editando_beneficiario:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            par = seleccion.get_value(iterador, 3)
            obs = seleccion.get_value(iterador, 4)
            obs = "" if obs is None else obs

            self.obj("txt_01").set_text(self.cond_beneficiario)
            self.obj("txt_02").set_text(obs)

            # Asignación de Tipo de Medio de Contacto en Combo
            model, i = self.obj("cmb_parentesco").get_model(), 0
            while model[i][0] != par: i += 1
            self.obj("cmb_parentesco").set_active(i)

            self.focus_out_event(self.obj("txt_01"), 0)
        else:
            self.obj("cmb_parentesco").set_active(0)

        self.estadoedicion(True)
        self.estadoguardar(False)

        self.obj("btn_guardar_benef").set_sensitive(False)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

    def on_btn_guardar_benef_clicked(self, objeto):
        emp = self.obj("txt_00").get_text()
        ben = self.obj("txt_01").get_text()
        obs = self.obj("txt_02").get_text()
        obs = "NULL" if len(obs) == 0 else "'" + obs + "'"

        sql = emp + ", " + ben + ", " + str(self.idTipoParentesco) + ", " + obs
        if not self.editando_beneficiario:
            Op.insertar(self.conexion, self.nav.tabla, sql)
        else:
            Op.modificar(self.conexion, self.nav.tabla,
                emp + ", " + self.cond_beneficiario + ", " + sql)

        self.cond_empleado = self.obj("txt_00").get_text()
        self.cargar_grilla_beneficiarios()
        self.on_btn_cancelar_benef_clicked(0)

    def on_btn_cancelar_benef_clicked(self, objeto):
        self.estadoedicion(False)
        self.estadoguardar(True)

        self.obj("txt_01").set_text("")
        self.obj("txt_01_1").set_text("")
        self.obj("txt_01_2").set_text("")
        self.obj("cmb_parentesco").set_active(-1)
        self.obj("txt_01_3").set_text("")
        self.obj("txt_01_4").set_text("")
        self.obj("txt_02").set_text("")

    def on_btn_familiar_clicked(self, objeto):
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_01_2"), self.obj("cmb_tipo_doc_ben")

        from clases.llamadas import personas
        personas(self.nav.datos_conexion, self, "Empleado <> 1 AND Empresa <> 1")

    def verificacion_benef(self, objeto):
        if len(self.obj("txt_01").get_text()) == 0 or len(self.obj("txt_01_2").get_text()) == 0 \
        or self.idTipoDocFamiliar == -1 or self.idTipoParentesco == -1:
            estado = False
        else:
            estado = Op.comprobar_numero(int, self.obj("txt_01"),
                "Código de Familiar", self.obj("barraestado"))
        self.obj("btn_guardar_benef").set_sensitive(estado)


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)

    col0 = Op.columnas("Cód. Empleado", celda0, 0, True, 100, 200)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Tipo Doc. Identidad", celda0, 1, True, 100, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Nro. Doc. Identidad", celda0, 2, True, 100, 200)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Nombre y Apellido", celda1, 3, True, 250)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Nro. Seguro IPS", celda0, 4, True, 150)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("ID Asegurado", celda0, 5, True, 150)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Cód. Familiar", celda0, 6, True, 100, 200)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Tipo Doc. Identidad", celda0, 7, True, 100, 200)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Nro. Doc. Identidad", celda0, 8, True, 100, 200)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Nombre y Apellido", celda1, 9, True, 250)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Fecha de Nacimiento", celda1, 10, True, 200)
    col10.set_sort_column_id(17)  # Para ordenarse usa la fila 17
    col11 = Op.columnas("Edad", celda0, 11, True, 100, 200)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Cód. Género", celda0, 12, True, 100, 200)
    col12.set_sort_column_id(12)
    col13 = Op.columnas("Género", celda1, 13, True, 150)
    col13.set_sort_column_id(13)
    col14 = Op.columnas("Cód. Tipo Parent.", celda0, 14, True, 100, 200)
    col14.set_sort_column_id(14)
    col15 = Op.columnas("Tipo de Parentesco", celda1, 15, True, 150)
    col15.set_sort_column_id(15)
    col16 = Op.columnas("Observaciones", celda1, 16, True, 200)
    col16.set_sort_column_id(16)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9,
        col10, col11, col12, col13, col14, col15, col16]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(3)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 3)

    lista = ListStore(int, str, str, str, str, str, int, str, str, str,
        str, int, str, str, int, str, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar == "FechaNacFamiliar":
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, "idEmpleado, idTipoDocEmpleado, " +
        "NroDocEmpleado, NombreApellidoEmpleado, NroSeguroIPS, idAsegurado, " +
        "idFamiliar, idTipoDocFamiliar, NroDocFamiliar, NombreApellidoFamiliar, " +
        "FechaNacFamiliar, EdadFamiliar, idGeneroFamiliar, GeneroFamiliar, " +
        "idTipoParentesco, TipoParentesco, Observaciones", self.tabla + "_s",
        opcion + " ORDER BY idFamiliar, idEmpleado")
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], datos[i][5], datos[i][6], datos[i][7], datos[i][8],
            datos[i][9], Cal.mysql_fecha(datos[i][10]), datos[i][11],
            datos[i][12], datos[i][13], datos[i][14], datos[i][15],
            datos[i][16], str(datos[i][10])])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Cód. Empleado", "idEmpleado"
    elif idcolumna == 1:
        col, self.campo_buscar = "Tipo Doc. Identidad", "idTipoDocEmpleado"
    elif idcolumna == 2:
        col, self.campo_buscar = "Nro. Doc. Identidad", "NroDocEmpleado"
    elif idcolumna == 3:
        col, self.campo_buscar = "Nombre y Apellido", "NombreApellidoEmpleado"
    elif idcolumna == 4:
        col, self.campo_buscar = "Nro. Seguro IPS", "NroSeguroIPS"
    elif idcolumna == 5:
        col, self.campo_buscar = "ID Asegurado", "idAsegurado"
    elif idcolumna == 6:
        col, self.campo_buscar = "Cód. Familiar", "idFamiliar"
    elif idcolumna == 7:
        col, self.campo_buscar = "Tipo Doc. Identidad", "idTipoDocFamiliar"
    elif idcolumna == 8:
        col, self.campo_buscar = "Nro. Doc. Identidad", "NroDocFamiliar"
    elif idcolumna == 9:
        col, self.campo_buscar = "Nombre y Apellido", "NombreApellidoFamiliar"
    elif idcolumna == 17:
        col, self.campo_buscar = "Fecha de Nacimiento", "FechaNacFamiliar"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 11:
        col, self.campo_buscar = "Edad", "EdadFamiliar"
    elif idcolumna == 12:
        col, self.campo_buscar = "Cód. Género", "idGeneroFamiliar"
    elif idcolumna == 13:
        col, self.campo_buscar = "Género", "GeneroFamiliar"
    elif idcolumna == 14:
        col, self.campo_buscar = "Cód. Tipo Parent.", "idTipoParentesco"
    elif idcolumna == 15:
        col, self.campo_buscar = "Tipo de Parentesco", "TipoParentesco"
    elif idcolumna == 16:
        col = self.campo_buscar = "Observaciones"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 3)
    valor2 = str(seleccion.get_value(iterador, 6))
    valor3 = seleccion.get_value(iterador, 9)
    valor4 = seleccion.get_value(iterador, 15)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n\nCód. Empleado: " + valor0 +
        "\nNombre y Apellido: " + valor1 + "\nCód. Familiar: " + valor2 +
        "\nNombre y Apellido: " + valor3 + "\nParentesco: " + valor4)

    self.obj("grilla").get_selection().unselect_all()
    self.obj("barraestado").push(0, "")

    if eleccion:
        conexion = Op.conectar(self.datos_conexion)
        Op.eliminar(conexion, self.tabla, valor0 + ", " + valor2)
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

    lista = [[Par("Empleado", head), Par("Beneficiario", head), Par("Edad", head), Par("Parentesco", head)]]
    for i in range(0, cant):
        lista.append([Par(str(datos[i][3]), body_ce), Par(datos[i][9], body_ce),
            Par(datos[i][11], body_iz), Par(datos[i][15], body_iz)])

    listado.listado(self.titulo, lista, [125, 125, 75, 100], A4)


def seleccion(self):
    pass
