#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import exc_info
from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import mensajes as Mens
from clases import operaciones as Op


class usuarios:

    def __init__(self, datos):
        self.datos_conexion = datos

        arch = Op.archivo("usuarios")
        self.obj = arch.get_object

        self.obj("ventana").set_default_size(800, 500)
        self.obj("ventana").set_position(1)
        self.obj("ventana").set_title("Navegar - Usuarios del Sistema")

        arch.connect_signals(self)

        self.config_grilla()
        self.cargar_grilla()
        self.permisos_user()
        self.obj("ventana").show()

    def on_btn_nuevo_clicked(self, objeto):
        self.editando = False
        self.funcion_nuevo()

    def on_btn_modificar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un Usuario de la lista. Luego presione Modificar.")
        else:
            self.editando = True
            self.funcion_modificar()

    def on_btn_eliminar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            valor0 = str(seleccion.get_value(iterador, 0))  # Codigo
            valor1 = seleccion.get_value(iterador, 2)  # Nro. Doc.
            valor2 = seleccion.get_value(iterador, 3)  # Alias
        except:
            self.obj("barraestado").push(0, "Seleccione un Usuario de la lista. Luego presione Eliminar.")
        else:
            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Nro. Documento: " + valor1 + "\nAlias: " + valor2)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                conexion = Op.conectar(self.datos_conexion)
                try:
                    cursor = conexion.cursor()
                    Op.eliminar(conexion, "usuarios", valor0)
                    cursor.execute("DROP USER '" + valor2 + "'")
                    conexion.commit()
                except:
                    conexion.rollback()
                    Mens.no_puede_borrar()
                else:
                    self.cargar_grilla()
                finally:
                    conexion.close()  # Finaliza la conexión

    def on_btn_permiso_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            usuario = seleccion.get_value(iterador, 3)
        except:
            self.obj("barraestado").push(0, "Seleccione un Usuario de la lista. Luego presione Modificar Permisos.")
        else:
            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            from usuarios_permisos import permisos
            permisos(self.datos_conexion, usuario)

    def on_btn_grupo_clicked(self, objeto):
        from clases.llamadas import grupousuarios
        grupousuarios(self.datos_conexion)

    def on_btn_salir_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_grilla_row_activated(self, objeto, fila, col):
        if self.obj("btn_modificar").get_sensitive():
            self.on_btn_modificar_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if self.obj("btn_eliminar").get_sensitive():
            if evento.keyval == 65535:  # Presionando Suprimir (Delete)
                self.on_btn_eliminar_clicked(0)

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla").set_search_column(i)

    def config_grilla(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)

        col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Tipo Documento", celda1, 1, True, 125)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Nro. Doc.", celda0, 2, True, 100)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Alias", celda1, 3, True, 150)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Nombre y Apellido", celda1, 4, True, 250)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Ocupación o Cargo", celda1, 5, True, 150)
        col5.set_sort_column_id(5)

        lista = [col0, col1, col2, col3, col4, col5]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(1)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, str, str, str, str, int, str)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla(self):
        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "idUsuario, TipoDocumento, " +
            "NroDocumento, Alias, NombreApellido, Ocupacion, idPersona, " +
            "idTipoDocumento", "usuarios_s", " ORDER BY Alias")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
                datos[i][4], datos[i][5], datos[i][6], datos[i][7]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def permisos_user(self):
        self.obj("btn_nuevo").set_sensitive(False)
        self.obj("btn_modificar").set_sensitive(False)
        self.obj("btn_eliminar").set_sensitive(False)
        self.obj("btn_permiso").set_sensitive(False)
        self.obj("btn_grupo").set_sensitive(False)

        conexion = Op.conectar(self.datos_conexion)
        cursor = conexion.cursor()
        cursor.execute("SELECT ROUTINE_NAME FROM procedimientos_s")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        for i in range(0, cant):
            procedimiento = datos[i][0]
            if procedimiento == "usuarios_i":
                self.obj("btn_nuevo").set_sensitive(True)
                self.obj("btn_permiso").set_sensitive(True)
                Op.combos_config(self.datos_conexion,
                    self.obj("cmb_new_doc"), "tipodocumentos", "idTipoDocumento")

            elif procedimiento == "usuarios_u":
                self.obj("btn_modificar").set_sensitive(True)
                self.obj("btn_permiso").set_sensitive(True)
                Op.combos_config(self.datos_conexion,
                    self.obj("cmb_mod_doc"), "tipodocumentos", "idTipoDocumento")

            elif procedimiento == "usuarios_d":
                self.obj("btn_eliminar").set_sensitive(True)

        cursor.execute("SELECT TABLE_NAME FROM vistas_s")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        for i in range(0, cant):
            vista = datos[i][0]
            if vista == "grupousuarios_s":
                self.obj("btn_grupo").set_sensitive(True)

##### Ventana de Inserción de Usuarios #################################

    def funcion_nuevo(self):
        self.obj("nuevo").set_position(1)
        self.obj("nuevo").set_title("Creando Usuario")
        self.obj("nuevo").set_modal(True)

        self.obj("btn_guardar_new").set_tooltip_text("Presione este botón para Guardar el registro de Usuarios")
        self.obj("btn_cancelar_new").set_tooltip_text("Presione este botón para Cancelar la operación")
        self.obj("btn_persona_new").set_tooltip_text("Presione este botón para buscar un Funcionario")
        self.obj("btn_guardar_new").set_sensitive(False)

        self.idTipoDoc = None
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_new_per"), self.obj("txt_new_nomb")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_new_doc"), self.obj("cmb_new_doc")

        self.obj("txt_new_cod").set_max_length(10)
        self.obj("txt_new_per").set_max_length(10)
        self.obj("txt_new_doc").set_max_length(12)
        self.obj("txt_new_alias").set_max_length(16)
        self.obj("txt_new_pass").set_max_length(50)
        self.obj("txt_new_conf").set_max_length(50)

        self.obj("txt_new_cod").set_tooltip_text("Ingrese el Código del Usuario")
        self.obj("txt_new_per").set_tooltip_text("Ingrese el Código del Funcionario que corresponda")
        self.obj("txt_new_nomb").set_tooltip_text("Nombre y Apellido del Funcionario seleccionado")
        self.obj("txt_new_doc").set_tooltip_text("Ingrese el Nro. de Documento del Funcionario")
        self.obj("txt_new_alias").set_tooltip_text("Ingrese el Alias del Usuario")
        self.obj("txt_new_pass").set_tooltip_text("Ingrese la Contraseña del Usuario")
        self.obj("txt_new_conf").set_tooltip_text("Confirme la Contraseña del Usuario")

        self.obj("txt_new_cod").set_text(Op.nuevoid(self.datos_conexion, "usuarios_s", "idUsuario"))
        self.obj("txt_new_per").set_text("")
        self.obj("txt_new_nomb").set_text("")
        self.obj("txt_new_doc").set_text("")
        self.obj("cmb_new_doc").set_active(0)
        self.obj("txt_new_alias").set_text("")
        self.obj("txt_new_pass").set_text("")
        self.obj("txt_new_conf").set_text("")

        self.obj("txt_new_per").grab_focus()

        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")
        self.obj("nuevo").show()

    def on_btn_guardar_new_clicked(self, objeto):
        v0 = self.obj("txt_new_cod").get_text()  # Codigo
        v1 = self.obj("txt_new_per").get_text()  # Funcionario
        v2 = self.obj("txt_new_alias").get_text()  # Alias
        v3 = self.obj("txt_new_pass").get_text()  # Password
        v4 = self.obj("txt_new_conf").get_text()  # Password

        if v3 == v4:
            conexion = Op.conectar(self.datos_conexion)
            try:
                cursor = conexion.cursor()
                Op.insertar(conexion, "usuarios", v0 + ", " + v1 + ", '" + v2 + "'")

                # Crear Usuario
                cursor.execute("CREATE USER '" + v2 + "' IDENTIFIED BY '" + v3 + "'")
                # Dar permiso para vistas iniciales del sistema
                Op.concede_select(cursor, "tablas_s", v2)
                Op.concede_select(cursor, "vistas_s", v2)
                Op.concede_select(cursor, "procedimientos_s", v2)
                conexion.commit()

            except:
                print("Error: ", exc_info()[0])
                conexion.rollback()
                Mens.no_puede_guardar("Guardar",
                    "No ha sido posible crear el usuario solicitado.")
            else:
                self.cargar_grilla()
                self.on_btn_cancelar_new_clicked(0)

            finally:
                conexion.close()  # Finaliza la conexión

        else:
            self.obj("barraestado_new").push(0, "La Contraseña no coincide.")
            self.obj("txt_new_pass").set_text("")
            self.obj("txt_new_conf").set_text("")

    def on_btn_cancelar_new_clicked(self, objeto):
        self.obj("cmb_new_doc").set_active(-1)
        self.obj("nuevo").hide()

##### Ventana de Actualización de Usuarios y Contraseñas ###############

    def funcion_modificar(self):
        self.obj("modificar").set_position(1)
        self.obj("modificar").set_title("Actualizando Datos de Usuario")
        self.obj("modificar").set_modal(True)

        self.obj("btn_guardar_mod").set_tooltip_text("Presione este botón para Guardar el registro de Usuarios")
        self.obj("btn_cancelar_mod").set_tooltip_text("Presione este botón para Cancelar la operación")
        self.obj("btn_persona_mod").set_tooltip_text("Presione este botón para buscar un Funcionario")
        self.obj("btn_guardar_mod").set_sensitive(False)

        self.idTipoDoc = None
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_mod_per"), self.obj("txt_mod_nomb")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_mod_doc"), self.obj("cmb_mod_doc")

        self.obj("txt_mod_cod").set_max_length(10)
        self.obj("txt_mod_per").set_max_length(10)
        self.obj("txt_mod_doc").set_max_length(12)
        self.obj("txt_mod_alias").set_max_length(16)
        self.obj("txt_mod_pass").set_max_length(50)
        self.obj("txt_mod_conf").set_max_length(50)

        self.obj("txt_mod_cod").set_tooltip_text("Ingrese el Código del Usuario")
        self.obj("txt_mod_per").set_tooltip_text("Ingrese el Código del Funcionario que corresponda")
        self.obj("txt_mod_nomb").set_tooltip_text("Nombre y Apellido del Funcionario seleccionado")
        self.obj("txt_mod_doc").set_tooltip_text("Ingrese el Nro. de Documento del Funcionario")
        self.obj("txt_mod_alias").set_tooltip_text("Ingrese el Alias del Usuario")
        self.obj("txt_mod_pass").set_tooltip_text("Ingrese la Contraseña del Usuario")
        self.obj("txt_mod_conf").set_tooltip_text("Confirme la Contraseña del Usuario")

        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        self.cond = str(seleccion.get_value(iterador, 0))
        self.alias = seleccion.get_value(iterador, 3)

        self.pers_orig = seleccion.get_value(iterador, 6)  # Persona Original
        idper = str(seleccion.get_value(iterador, 6))
        nombre = seleccion.get_value(iterador, 4)
        nrodoc = seleccion.get_value(iterador, 2)
        tipodoc = seleccion.get_value(iterador, 7)

        # Asignación de Tipo de Documento en Combo
        model, i = self.obj("cmb_mod_doc").get_model(), 0
        while model[i][0] != tipodoc: i += 1
        self.obj("cmb_mod_doc").set_active(i)

        self.obj("txt_mod_cod").set_text(self.cond)
        self.obj("txt_mod_per").set_text(idper)
        self.obj("txt_mod_nomb").set_text(nombre)
        self.obj("txt_mod_doc").set_text(nrodoc)
        self.obj("txt_mod_alias").set_text(self.alias)
        self.obj("txt_mod_pass").set_text("")
        self.obj("txt_mod_conf").set_text("")

        self.obj("notebook").set_current_page(0)
        self.obj("txt_mod_alias").grab_focus()

        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")
        self.obj("modificar").show()

    def on_btn_guardar_mod_clicked(self, objeto):
        page = self.obj("notebook").get_current_page()
        conexion = Op.conectar(self.datos_conexion)
        cursor = conexion.cursor()

        if page == 0:
            # Guardar actualización de Alias
            v0 = self.obj("txt_mod_cod").get_text()
            v1 = self.obj("txt_mod_per").get_text()
            v2 = self.obj("txt_mod_alias").get_text()

            try:
                Op.modificar(conexion, "usuarios", self.cond + ", " +
                    v0 + ", " + v1 + ", '" + v2 + "'")

                if self.alias != v2:  # Renombrar Usuario
                    cursor.execute("RENAME USER '" + self.alias + "' TO '" + v2 + "'")
                    cursor.execute("FLUSH PRIVILEGES")
                conexion.commit()

            except:
                print("Error: ", exc_info()[0])
                conexion.rollback()
                Mens.no_puede_guardar("Modificar",
                    "No ha sido posible modificar el Usuario.")
            else:
                self.cargar_grilla()
                self.on_btn_cancelar_mod_clicked(0)

            finally:
                conexion.close()  # Finaliza la conexión
        else:
            # Guardar actualización de Contraseña
            v1 = self.obj("txt_mod_pass").get_text()  # Password
            v2 = self.obj("txt_mod_conf").get_text()  # Password

            if v1 == v2:
                try:
                    # Modificar Contraseña
                    cursor.execute("SET PASSWORD FOR '" + self.alias + "' = PASSWORD('" + v1 + "')")
                    conexion.commit()

                except:
                    print("Error: ", exc_info()[0])
                    conexion.rollback()
                    Mens.no_puede_guardar("Modificar",
                        "No ha sido posible modificar la Contraseña.")
                else:
                    self.on_btn_cancelar_mod_clicked(0)

                finally:
                    conexion.close()  # Finaliza la conexión

    def on_btn_cancelar_mod_clicked(self, objeto):
        self.obj("cmb_mod_doc").set_active(-1)
        self.obj("modificar").hide()

    def on_notebook_change_current_page(self, objeto):
        self.verificacion(0)

    def on_notebook_focus_in_event(self, objeto, evento):
        self.verificacion(0)

##### Métodos comunes de Inserción y Actualización de Usuarios #########

    def on_btn_persona_clicked(self, objeto):
        from clases.llamadas import personas
        personas(self.datos_conexion, self, "Empresa = 0")

    def verificacion(self, objeto):
        if self.editando:
            if self.obj("notebook").get_current_page() == 0:
                if len(self.obj("txt_mod_cod").get_text()) == 0 \
                or len(self.obj("txt_mod_per").get_text()) == 0 \
                or len(self.obj("txt_mod_doc").get_text()) == 0 \
                or len(self.obj("txt_mod_alias").get_text()) == 0 \
                or self.idTipoDoc is None:
                    estado = False
                else:
                    if Op.comprobar_numero(int, self.obj("txt_mod_cod"), "Código", self.obj("barraestado_mod")) \
                    and Op.comprobar_numero(int, self.obj("txt_mod_per"), "Cód. de Funcionario", self.obj("barraestado_mod")):
                        estado = True
                    else:
                        estado = False
            else:
                if len(self.obj("txt_mod_pass").get_text()) == 0 \
                or len(self.obj("txt_mod_conf").get_text()) == 0:
                    estado = False
                else:
                    estado = True
            self.obj("btn_guardar_mod").set_sensitive(estado)
        else:
            if len(self.obj("txt_new_cod").get_text()) == 0 \
            or len(self.obj("txt_new_per").get_text()) == 0 \
            or len(self.obj("txt_new_doc").get_text()) == 0 \
            or len(self.obj("txt_new_alias").get_text()) == 0 \
            or len(self.obj("txt_new_pass").get_text()) == 0 \
            or len(self.obj("txt_new_conf").get_text()) == 0 \
            or self.idTipoDoc is None:
                estado = False
            else:
                if Op.comprobar_numero(int, self.obj("txt_new_cod"), "Código", self.obj("barraestado_new")) \
                and Op.comprobar_numero(int, self.obj("txt_new_per"), "Cód. de Funcionario", self.obj("barraestado_new")):
                    estado = True
                else:
                    estado = False
            self.obj("btn_guardar_new").set_sensitive(estado)

    def on_cmb_tipo_doc_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            self.idTipoDoc = model[active][0]
            objeto = self.obj("txt_new_doc") if objeto == self.obj("cmb_new_doc") else self.obj("txt_mod_doc")
            self.focus_out_event(objeto, 0)
        else:
            self.obj("barraestado").push(0, "No existen registros de " +
                "Tipos de Documentos de Identidad en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_persona_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        mensaje = "Presione CTRL + Enter para Buscar un Funcionario."
        if self.editando:
            self.obj("barraestado_mod").push(0, mensaje)
        else:
            self.obj("barraestado_new").push(0, mensaje)

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")

            if objeto == self.obj("txt_new_per"):  # Nuevo idPersona
                self.obj("txt_new_nomb").set_text("")
                self.obj("txt_new_doc").set_text("")
            elif objeto == self.obj("txt_new_doc") and len(self.obj("txt_new_per").get_text()) == 0:
                self.obj("txt_new_nomb").set_text("")

            elif objeto == self.obj("txt_mod_per"):  # Modificar idPersona
                self.obj("txt_mod_nomb").set_text("")
                self.obj("txt_mod_doc").set_text("")
            elif objeto == self.obj("txt_mod_doc") and len(self.obj("txt_mod_per").get_text()) == 0:
                self.obj("txt_mod_nomb").set_text("")
        else:
            if objeto == self.obj("txt_new_cod"):
                self.comprobacion_codigo(objeto, valor, self.obj("barraestado_new"),
                    self.obj("btn_guardar_new"))

            elif objeto == self.obj("txt_mod_cod"):
                self.comprobacion_codigo(objeto, valor, self.obj("barraestado_mod"),
                    self.obj("btn_guardar_mod"))

            elif objeto == self.obj("txt_new_per"):
                if Op.comprobar_numero(int, objeto, "Cód. de Funcionario", self.obj("barraestado_new")):
                    self.buscar_personas(objeto, "idPersona", valor,
                        "Cód. de Funcionario", objeto, self.obj("txt_new_nomb"),
                        self.obj("txt_new_doc"), self.obj("cmb_new_doc"),
                        self.obj("barraestado_new"), self.obj("btn_guardar_new"))

            elif objeto == self.obj("txt_mod_per"):
                if Op.comprobar_numero(int, objeto, "Cód. de Funcionario", self.obj("barraestado_mod")):
                    self.buscar_personas(objeto, "idPersona", valor,
                        "Cód. de Funcionario", objeto, self.obj("txt_mod_nomb"),
                        self.obj("txt_mod_doc"), self.obj("cmb_mod_doc"),
                        self.obj("barraestado_mod"), self.obj("btn_guardar_mod"))

            elif objeto == self.obj("txt_new_doc"):
                self.buscar_personas(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDoc + "'",
                    "Nro. de Documento del Funcionario", self.obj("txt_new_per"),
                    self.obj("txt_new_nomb"), objeto, self.obj("cmb_new_doc"),
                    self.obj("barraestado_new"), self.obj("btn_guardar_new"))

            elif objeto == self.obj("txt_mod_doc"):
                self.buscar_personas(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDoc + "'",
                    "Nro. de Documento del Funcionario", self.obj("txt_mod_per"),
                    self.obj("txt_mod_nomb"), objeto, self.obj("cmb_mod_doc"),
                    self.obj("barraestado_mod"), self.obj("btn_guardar_mod"))

            elif objeto == self.obj("txt_new_alias"):
                self.comprobacion_alias(objeto, valor, self.obj("barraestado_new"),
                    self.obj("btn_guardar_new"))

            elif objeto == self.obj("txt_mod_alias"):
                self.comprobacion_alias(objeto, valor, self.obj("barraestado_mod"),
                    self.obj("btn_guardar_mod"))

    def comprobacion_codigo(self, objeto, valor, barraestado, boton):
        # Comprueba que no haya Códigos repetidos
        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "idUsuario",
            "usuarios_s", " WHERE idUsuario = " + valor)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            if not self.editando or self.cond != valor:
                objeto.grab_focus()
                boton.set_sensitive(False)
                barraestado.push(0, "El Código introducido ya ha sido registrado.")
            else:
                self.verificacion(0)
                barraestado.push(0, "")
        else:
            self.verificacion(0)
            barraestado.push(0, "")

    def comprobacion_alias(self, objeto, valor, barraestado, boton):
        # Comprueba que no haya Alias repetidos
        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "Alias",
            "usuarios_s", " WHERE Alias = '" + valor + "'")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            if not self.editando or self.alias != valor:
                objeto.grab_focus()
                boton.set_sensitive(False)
                barraestado.push(0, "El Alias introducido ya está siendo utilizado por otra Persona.")
            else:
                self.verificacion(0)
                barraestado.push(0, "")
        else:
            self.verificacion(0)
            barraestado.push(0, "")

    def buscar_personas(self, objeto, campo, valor, nombre, cod_per, rzn_scl, nro_doc, tip_doc, barraestado, btn_guardar):
        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "idPersona, RazonSocial, " +
            "NroDocumento, idTipoDocumento", "personas_s",
            " WHERE " + campo + " = " + valor)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            cod_per.set_text(str(datos[0][0]))
            rzn_scl.set_text(datos[0][1])
            nro_doc.set_text(datos[0][2])

            # Asignación de Tipo de Documento en Combo
            model, i = tip_doc.get_model(), 0
            while model[i][0] != datos[0][3]: i += 1
            tip_doc.set_active(i)

            barraestado.push(0, "")
            self.verificacion(0)

            # Si la persona seleccionada es diferente de la que se está modificando
            if not self.editando or datos[0][0] != self.pers_orig:
                conexion = Op.conectar(self.datos_conexion)
                cursor = Op.consultar(conexion, "Alias", "usuarios_s",
                    " WHERE idPersona = " + str(datos[0][0]))
                datos = cursor.fetchall()
                cant = cursor.rowcount
                conexion.close()  # Finaliza la conexión

                if cant > 0:
                    # Se permiten varios usuarios por persona
                    # Comunica que la persona ya posee un usuario
                    barraestado.push(0, "La persona seleccionada ya posee un " +
                        "usuario registrado (" + datos[0][0] + ").")

        else:
            btn_guardar.set_sensitive(False)
            objeto.grab_focus()
            barraestado.push(0, "El " + nombre + " no es válido.")

            otro = nro_doc if objeto == cod_per else cod_per
            otro.set_text("")
            rzn_scl.set_text("")
