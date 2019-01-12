#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from decimal import Decimal
from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen, contr=None):
        self.editando = edit
        self.contrato = contr  # Está creando desde Contratos
        self.nav = origen

        arch = Op.archivo("rrhh_vendedores")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(500, 550)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Vendedores")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_02").set_max_length(10)
        self.obj("txt_02_2").set_max_length(12)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código del Vendedor")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Contrato del Vendedor"))
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el Vendedor con quien se celebró el Contrato"))
        self.obj("txt_02_1").set_tooltip_text("Nombre y Apellido del Vendedor")
        self.obj("txt_02_2").set_tooltip_text("Ingrese el Nro. de Documento del Vendedor")
        self.obj("txt_02_3").set_tooltip_text("Dirección Principal del Vendedor")
        self.obj("txt_02_4").set_tooltip_text("Teléfono del Vendedor")

        self.txt_cod_cnt, self.idTipoDoc = self.obj("txt_01"), -1
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_02"), self.obj("txt_02_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_02_2"), self.obj("cmb_tipo_doc")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_02_3"), self.obj("txt_02_4")

        self.txt_cod_it = self.obj("txt_it_00")
        self.txt_bar_it, self.txt_nom_it = self.obj("txt_it_00_1"), self.obj("txt_it_00_2")
        self.txt_cod_pres, self.txt_des_pres = self.obj("txt_it_00_3"), self.obj("txt_it_00_4")

        self.idPersona, self.borrar_contrato, self.idTipoDoc = None, not edit, -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            contrato = str(seleccion.get_value(iterador, 1))
            empleado = str(seleccion.get_value(iterador, 2))
            tipodoc = seleccion.get_value(iterador, 3)
            nrodoc = seleccion.get_value(iterador, 4)
            nombre = seleccion.get_value(iterador, 5)
            direccion = seleccion.get_value(iterador, 6)
            telefono = seleccion.get_value(iterador, 7)

            direccion = "" if direccion is None else direccion
            telefono = "" if telefono is None else telefono

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(contrato)
            self.obj("txt_02").set_text(empleado)
            self.obj("txt_02_1").set_text(nombre)
            self.obj("txt_02_2").set_text(nrodoc)
            self.obj("txt_02_3").set_text(direccion)
            self.obj("txt_02_4").set_text(telefono)

            # Asignación de Tipo de Documento en Combo
            model, i = self.obj("cmb_tipo_doc").get_model(), 0
            while model[i][0] != tipodoc: i += 1
            self.obj("cmb_tipo_doc").set_active(i)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                "vendedores_s", "idVendedor"))
            self.obj("cmb_tipo_doc").set_active(0)

        self.conexion = Op.conectar(self.nav.datos_conexion)
        self.principal_guardado = True

        self.estadoedicion(False)
        self.config_grilla_categorias()
        self.cargar_grilla_categorias()
        self.config_grilla_items()
        self.cargar_grilla_items()

        if self.contrato is None:
            self.nav.obj("grilla").get_selection().unselect_all()
            self.nav.obj("barraestado").push(0, "")
        else:
            # Datos del Contrato del Empleado
            self.obj("txt_01").set_text(self.contrato)
            self.focus_out_event(self.obj("txt_01"), 0)

            # No puede cambiar el Empleado ni el Contrato
            self.obj("vbox1").set_sensitive(False)

        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_principal_vendedores()
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()

        if self.contrato is None:
            cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def on_btn_contrato_clicked(self, objeto):
        condicion = None if len(self.obj("txt_02").get_text()) == 0 \
        else "idEmpleado = " + self.obj("txt_02").get_text()

        from clases.llamadas import contratos
        contratos(self.nav.datos_conexion, self, condicion)

    def on_btn_empleado_clicked(self, objeto):
        from clases.llamadas import empleados
        empleados(self.nav.datos_conexion, self)

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Nro. de Contrato", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Cód. de Empleado", self.obj("barraestado")):
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
            self.focus_out_event(self.obj("txt_02_2"), 0)
        else:
            self.obj("barraestado").push(0, "No existen registros de Tipos de Documentos de Identidad en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_01"):
                    self.on_btn_contrato_clicked(0)
                elif objeto in (self.obj("txt_02"), self.obj("txt_02_2")):
                    self.on_btn_empleado_clicked(0)
                elif objeto == self.obj("txt_ct_00"):
                    self.on_btn_categoria_clicked(0)
                elif objeto in (self.obj("txt_it_00"), self.obj("txt_it_00_1")):
                    self.on_btn_item_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_01"):
            tipo = " Contrato"
        elif objeto in (self.obj("txt_02"), self.obj("txt_02_2")):
            tipo = " Empleado"
        elif objeto == self.obj("txt_ct_00"):
            tipo = "a Categoría"
        elif objeto in (self.obj("txt_it_00"), self.obj("txt_it_00_1")):
            tipo = " Ítem"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un" + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_02"):  # Código de Empleado
                self.obj("txt_02_2").set_text("")

            elif objeto == self.obj("txt_ct_00"):  # Código de Categoría
                self.obj("txt_ct_00_1").set_text("")
            elif objeto == self.obj("txt_it_00"):  # Código de Ítem
                self.obj("txt_it_00_1").set_text("")

            if objeto == self.obj("txt_02") or (objeto == self.obj("txt_02_2") \
            and len(self.obj("txt_02").get_text()) == 0):
                self.obj("txt_02_1").set_text("")
                self.obj("txt_02_3").set_text("")
                self.obj("txt_02_4").set_text("")

            if objeto == self.obj("txt_it_00") or (objeto == self.obj("txt_it_00_1") \
            and len(self.obj("txt_it_00").get_text()) == 0):
                self.obj("txt_02_1").set_text("")
                self.obj("txt_02_3").set_text("")
                self.obj("txt_02_4").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) and \
                Op.comprobar_numero(int, objeto, "Código", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion, "vendedores_s",
                        "idVendedor", valor, self.obj("txt_00"),
                        self.estadoedicion, self.obj("barraestado"),
                        "El Código introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Nro. de Contrato", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "idEmpleado, Vigente",
                        "contratos_s", " WHERE NroContrato = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        if datos[0][1] == 1:
                            self.obj("txt_02").set_text(str(datos[0][0]))

                            self.obj("barraestado").push(0, "")
                            self.borrar_contrato = False
                            self.focus_out_event(self.obj("txt_02"), 0)
                        else:
                            objeto.grab_focus()
                            self.estadoguardar(False)
                            self.obj("barraestado").push(0, "El Contrato seleccionado ya no se encuentra vigente.")
                    else:
                        objeto.grab_focus()
                        self.estadoguardar(False)
                        self.obj("barraestado").push(0, "El Nro. de Contrato no es válido.")

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Cód. de Empleado", self.obj("barraestado")):
                    self.buscar_empleados(objeto, "idPersona", valor, "Cód. de Empleado")

            elif objeto == self.obj("txt_02_2"):
                self.buscar_empleados(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDoc + "'", "Nro. de Documento")

            elif objeto == self.obj("txt_ct_00"):
                if Op.comprobar_numero(int, objeto, "Cód. de Categoría", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "Descripcion",
                        "categorias_s", " WHERE idCategoria = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("txt_ct_00_1").set_text(datos[0][0])
                        self.obj("barraestado").push(0, "")
                        self.on_categoria_changed(0)
                    else:
                        objeto.grab_focus()
                        self.obj("btn_guardar_categoria").set_sensitive(False)
                        self.obj("barraestado").push(0, "El Cód. de Categoría no es válido.")
                        self.obj("txt_ct_00_1").set_text("")

            elif objeto == self.obj("txt_it_00"):
                if Op.comprobar_numero(int, objeto, "Cód. de Ítem", self.obj("barraestado")):
                    self.buscar_items(objeto, "idItem", valor, "Ítem")

            elif objeto == self.obj("txt_it_00_1"):
                self.buscar_items(objeto, "CodigoBarras", "'" + valor + "'", "Barras")

    def buscar_empleados(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, "idPersona, RazonSocial, NroDocumento, " +
            "idTipoDocumento, DireccionPrincipal, TelefonoPrincipal", "personas_s",
            " WHERE " + campo + " = " + valor + " AND Empleado = 1")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            # Si aún no se ha seleccionado o es diferente del anterior
            if self.idPersona is None or self.idPersona != str(datos[0][0]):
                self.idPersona = str(datos[0][0])

                direc = "" if datos[0][4] is None else datos[0][4]
                telef = "" if datos[0][5] is None else datos[0][5]

                self.obj("txt_02").set_text(self.idPersona)
                self.obj("txt_02_1").set_text(datos[0][1])
                self.obj("txt_02_2").set_text(datos[0][2])
                self.obj("txt_02_3").set_text(direc)
                self.obj("txt_02_4").set_text(telef)

                # Asignación de Tipo de Documento en Combo
                model, i = self.obj("cmb_tipo_doc").get_model(), 0
                while model[i][0] != datos[0][3]: i += 1
                self.obj("cmb_tipo_doc").set_active(i)

                if self.borrar_contrato:  # Debe indicarse otro Contrato
                    self.obj("txt_01").set_text("")
                else:
                    self.borrar_contrato = True

                self.obj("barraestado").push(0, "")
                self.verificacion(0)

        else:
            self.idPersona = valor
            objeto.grab_focus()
            self.estadoguardar(False)
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_02_2") if objeto == self.obj("txt_02") else self.obj("txt_02")
            otro.set_text("")

            self.obj("txt_02_1").set_text("")
            self.obj("txt_02_3").set_text("")
            self.obj("txt_02_4").set_text("")

    def buscar_items(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, "idItem, CodigoBarras, Nombre, " +
            "idPresentacion, Presentacion, idCategoria, Categoria, PrecioCosto",
            "items_s I", " WHERE " + campo + " = " + valor)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            codbar = "" if datos[0][1] is None else datos[0][1]

            self.obj("txt_it_00").set_text(str(datos[0][0]))
            self.obj("txt_it_00_1").set_text(codbar)
            self.obj("txt_it_00_2").set_text(datos[0][2])
            self.obj("txt_it_00_3").set_text(str(datos[0][3]))
            self.obj("txt_it_00_4").set_text(datos[0][4])
            self.obj("txt_it_00_5").set_text(str(datos[0][5]))
            self.obj("txt_it_00_6").set_text(datos[0][6])
            self.obj("txt_it_01").set_text(str(datos[0][7]))

            # Buscar Precios de Venta
            self.on_cmb_it_02_changed(0)

        else:
            objeto.grab_focus()
            self.obj("btn_guardar_item").set_sensitive(False)
            self.obj("barraestado").push(0, "El Código de " + nombre + " no es válido.")

            otro = self.obj("txt_it_00_1") if objeto == self.obj("txt_it_00") else self.obj("txt_it_00")
            otro.set_text("")

            self.obj("txt_it_00_2").set_text("")
            self.obj("txt_it_00_3").set_text("")
            self.obj("txt_it_00_4").set_text("")
            self.obj("txt_it_00_5").set_text("")
            self.obj("txt_it_00_6").set_text("")

    def guardar_principal_vendedores(self):
        if not self.principal_guardado:
            vend = self.obj("txt_00").get_text()
            cont = self.obj("txt_01").get_text()

            sql = vend + ", " + cont
            if not self.editando:
                Op.insertar(self.conexion, "vendedores", sql)
            else:
                Op.modificar(self.conexion, "vendedores", self.cond + ", " + sql)

            self.cond = vend  # Nuevo idVendedor original
            self.principal_guardado = self.editando = True

    def estadoguardar(self, estado):
        self.obj("notebook").set_sensitive(estado)
        self.obj("btn_guardar").set_sensitive(estado)

    def estadoedicion(self, estado):
        self.obj("vbox1").set_visible(not estado)
        self.obj("buttonbox").set_sensitive(not estado)

        self.obj("vbox2").set_visible(estado)
        self.obj("buttonbox_categoria_com").set_visible(estado)
        self.obj("buttonbox_categoria_abm").set_sensitive(not estado)
        self.obj("grilla_categorias").set_sensitive(not estado)

        self.obj("vbox3").set_visible(estado)
        self.obj("buttonbox_item_com").set_visible(estado)
        self.obj("buttonbox_item_abm").set_sensitive(not estado)
        self.obj("grilla_items").set_sensitive(not estado)

##### Categorías #######################################################

    def config_grilla_categorias(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Categoría", celda1, 1, True, 150)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Impuesto", celda1, 2, True, 150)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Porcentaje", celda2, 3, True, 100, 150)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Porc. Comisión", celda2, 4, True, 100, 150)
        col4.set_sort_column_id(4)

        lista = [col0, col1, col2, col3, col4]
        for columna in lista:
            self.obj("grilla_categorias").append_column(columna)

        self.obj("grilla_categorias").set_rules_hint(True)
        self.obj("grilla_categorias").set_search_column(2)
        self.obj("grilla_categorias").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, str, float, float)
        self.obj("grilla_categorias").set_model(lista)
        self.obj("grilla_categorias").show()

    def cargar_grilla_categorias(self):
        cursor = Op.consultar(self.conexion, "idCategoria, Categoria, " +
            "Impuesto, Porcentaje, PorcComision", "vendedorcomisioncategorias_s",
            " WHERE idVendedor = " + self.obj("txt_00").get_text() +
            " GROUP BY idCategoria ORDER BY idCategoria")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla_categorias").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1],
                datos[i][2], datos[i][3], datos[i][4]])

        cant = str(cant) + " item encontrado." if cant == 1 \
            else str(cant) + " items encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_categoria_clicked(self, objeto):
        self.editando_categoria = False
        self.funcion_categorias()

    def on_btn_modificar_categoria_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla_categorias").get_selection().get_selected()
            self.cond_categoria = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Categorías. Luego presione Modificar.")
        else:
            self.editando_categoria = True
            self.funcion_categorias()

    def on_btn_eliminar_categoria_clicked(self, objeto):
        self.guardar_principal_vendedores()

        try:
            seleccion, iterador = self.obj("grilla_categorias").get_selection().get_selected()
            valor0 = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Categorías. Luego presione Eliminar.")
        else:
            vend = self.obj("txt_00").get_text()
            valor1 = seleccion.get_value(iterador, 1)
            valor2 = seleccion.get_value(iterador, 4)

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Cód. de Categoría: " + valor0 + "\nDescripción: " + valor1 +
                "\nPorc. Comisión: " + valor2)

            self.obj("grilla_categorias").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "vendedorcomisioncategorias",
                    vend + ", " + valor0)
                self.cargar_grilla_categorias()

    def on_grilla_categorias_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_categoria_clicked(0)

    def on_grilla_categorias_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_categoria_clicked(0)

##### Agregar-Modificar Categorías #####################################

    def funcion_categorias(self):
        self.guardar_principal_vendedores()

        if self.editando_categoria:
            seleccion, iterador = self.obj("grilla_categorias").get_selection().get_selected()
            des = seleccion.get_value(iterador, 1)
            com = seleccion.get_value(iterador, 4)

            self.obj("txt_ct_00").set_text(self.cond_categoria)
            self.obj("txt_ct_00_1").set_text(des)
            self.obj("txt_ct_01").set_value(com)

        self.obj("notebook").set_show_tabs(False)
        self.estadoedicion(True)

        self.obj("btn_guardar_categoria").set_sensitive(False)
        self.obj("grilla_categorias").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

    def on_btn_guardar_categoria_clicked(self, objeto):
        self.guardar_principal_vendedores()

        vend = self.obj("txt_00").get_text()
        cat = self.obj("txt_ct_00").get_text()
        com = str(round(self.obj("txt_ct_01").get_value(), 2))

        sql = vend + ", " + cat + ", " + com
        if not self.editando_categoria:
            Op.insertar(self.conexion, "vendedorcomisioncategorias", sql)
        else:
            Op.modificar(self.conexion, "vendedorcomisioncategorias",
                self.cond_categoria + ", " + sql)

        self.cargar_grilla_categorias()
        self.cargar_grilla_items()
        self.on_btn_cancelar_categoria_clicked(0)

    def on_btn_cancelar_categoria_clicked(self, objeto):
        self.obj("notebook").set_show_tabs(True)
        self.estadoedicion(False)

        self.obj("txt_ct_00").set_text("")
        self.obj("txt_ct_00_1").set_text("")
        self.obj("txt_ct_01").set_value(1.0)

    def on_btn_categoria_clicked(self, objeto):
        self.txt_cod_cat, self.txt_des_cat = self.obj("txt_ct_00"), self.obj("txt_ct_00_1")

        from clases.llamadas import categorias
        categorias(self.nav.datos_conexion, self)

    def on_categoria_changed(self, objeto):
        if len(self.obj("txt_ct_00").get_text()) == 0:
            estado = False
        else:
            estado = Op.comprobar_numero(int, self.obj("txt_ct_00"),
                "Código de Categoría", self.obj("barraestado"))
        self.obj("btn_guardar_categoria").set_sensitive(estado)

##### Ítems ############################################################

    def config_grilla_items(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Código de Barras", celda0, 1, True, 100, 150)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Nombre", celda1, 2, True, 220, 300)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Descripción", celda1, 3, True, 200, 300)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Cód. Cat.", celda0, 4, True, 100, 150)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Categoría", celda1, 5, True, 150)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Impuesto", celda1, 6, True, 150)
        col6.set_sort_column_id(6)
        col7 = Op.columnas("Porcentaje", celda2, 7, True, 100, 150)
        col7.set_sort_column_id(7)
        col8 = Op.columnas("Cód. Pres.", celda0, 8, True, 100, 150)
        col8.set_sort_column_id(8)
        col9 = Op.columnas("Presentación", celda1, 9, True, 150)
        col9.set_sort_column_id(9)
        col10 = Op.columnas("Precio de Costo", celda2, 10, True, 100, 150)
        col10.set_sort_column_id(10)
        col11 = Op.columnas("Porc. Comisión", celda2, 11, True, 100, 150)
        col11.set_sort_column_id(11)

        lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11]
        for columna in lista:
            self.obj("grilla_items").append_column(columna)

        self.obj("grilla_items").set_rules_hint(True)
        self.obj("grilla_items").set_search_column(2)
        self.obj("grilla_items").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, str, str, int, str, str, float, int, str, float, float)
        self.obj("grilla_items").set_model(lista)
        self.obj("grilla_items").show()

    def cargar_grilla_items(self):
        cursor = Op.consultar(self.conexion, "idItem, CodigoBarras, " +
            "Nombre, Descripcion, idCategoria, Categoria, Impuesto, " +
            "Porcentaje, idPresentacion, Presentacion, PrecioCosto, " +
            "PorcComision", "vendedorcomisionitems_s",
            " WHERE idVendedor = " + self.obj("txt_00").get_text() +
            " ORDER BY idItem")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        cantidad = cant

        lista = self.obj("grilla_items").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
                datos[i][4], datos[i][5], datos[i][6], datos[i][7], datos[i][8],
                datos[i][9], datos[i][10], datos[i][11]])

        # Datos de Items agrupados por Categorías
        cursor = Op.consultar(self.conexion, "idItem, CodigoBarras, " +
            "Nombre, Descripcion, idCategoria, Categoria, Impuesto, " +
            "Porcentaje, idPresentacion, Presentacion, PrecioCosto, " +
            "PorcComision", "vendedorcomisioncategorias_s",
            " WHERE idVendedor = " + self.obj("txt_00").get_text() +
            " ORDER BY idItem")
        datos_cat = cursor.fetchall()
        cant_cat = cursor.rowcount

        for i in range(0, cant_cat):
            agregar = True
            for x in range(0, cant):
                if datos_cat[i][0] == datos[x][0]:
                    agregar = False
                    break

            if agregar:  # Agrega si no secargó individualmente
                lista.append([datos_cat[i][0], datos_cat[i][1], datos_cat[i][2],
                    datos_cat[i][3], datos_cat[i][4], datos_cat[i][5],
                    datos_cat[i][6], datos_cat[i][7], datos_cat[i][8],
                    datos_cat[i][9], datos_cat[i][10], datos_cat[i][11]])
                cantidad += 1

        cant = str(cantidad) + " item encontrado." if cantidad == 1 \
            else str(cantidad) + " items encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_item_clicked(self, objeto):
        self.editando_item = False
        self.funcion_items()

    def on_btn_modificar_item_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla_items").get_selection().get_selected()
            self.cond_item = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Items. Luego presione Modificar.")
        else:
            self.editando_item = True
            self.funcion_items()

    def on_btn_eliminar_item_clicked(self, objeto):
        self.guardar_principal_vendedores()

        try:
            seleccion, iterador = self.obj("grilla_items").get_selection().get_selected()
            valor0 = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Items. Luego presione Eliminar.")
        else:
            vend = self.obj("txt_00").get_text()
            valor1 = seleccion.get_value(iterador, 2)
            valor2 = seleccion.get_value(iterador, 5)
            valor3 = seleccion.get_value(iterador, 9)
            valor4 = seleccion.get_value(iterador, 11)

            # Verificar si se registró el Ítem individualmente
            cursor = Op.consultar(self.conexion, "idItem", "vendedorcomisionitems_s",
                " WHERE idVendedor = " + self.obj("txt_00").get_text())
            datos = cursor.fetchall()
            cant = cursor.rowcount

            if cant > 0:
                eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                    "Cód. de Ítem: " + valor0 + "\nNombre: " + valor1 +
                    "\nCategoría: " + valor2 + "\nPresentación: " + valor3 +
                    "\nPorc. Comisión: " + valor4)

                self.obj("grilla_items").get_selection().unselect_all()
                self.obj("barraestado").push(0, "")

                if eleccion:
                    Op.eliminar(self.conexion, "vendedorcomisionitems",
                        vend + ", " + valor0)
                    self.cargar_grilla_items()

            else:
                Mens.error_generico("No se ha podido eliminar el registro",
                "El porcentaje de comisión del Ítem seleccionado ha sido \n" +
                "establecido por la Categoría a la que pertenece.\n\n" +
                "Si desea un porcentaje distinto para este ítem en particular,\n" +
                "haga clic en Modificar, y establezca el valor manualmente.")

    def on_grilla_items_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_item_clicked(0)

    def on_grilla_items_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_item_clicked(0)

##### Agregar-Modificar Ítems ##########################################

    def funcion_items(self):
        self.guardar_principal_vendedores()

        if self.editando_item:
            seleccion, iterador = self.obj("grilla_items").get_selection().get_selected()
            com = seleccion.get_value(iterador, 11)
            self.obj("txt_it_03").set_value(com)

            self.obj("txt_it_00").set_text(self.cond_item)
            self.focus_out_event(self.obj("txt_it_00"), 0)

            # Verificar si se registró el Ítem individualmente
            cursor = Op.consultar(self.conexion, "idItem", "vendedorcomisionitems_s",
                " WHERE idVendedor = " + self.obj("txt_00").get_text())
            datos = cursor.fetchall()
            cant = cursor.rowcount

            if not cant > 0:
                self.editando_item = False

        self.obj("notebook").set_show_tabs(False)
        self.estadoedicion(True)

        self.obj("btn_guardar_item").set_sensitive(False)
        self.obj("grilla_items").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

    def on_btn_guardar_item_clicked(self, objeto):
        self.guardar_principal_vendedores()

        vend = self.obj("txt_00").get_text()
        item = self.obj("txt_it_00").get_text()
        com = str(round(self.obj("txt_it_03").get_value(), 2))

        sql = vend + ", " + item + ", " + com
        if not self.editando_item:
            Op.insertar(self.conexion, "vendedorcomisionitems", sql)
        else:
            Op.modificar(self.conexion, "vendedorcomisionitems",
                self.cond_item + ", " + sql)

        self.cargar_grilla_items()
        self.on_btn_cancelar_item_clicked(0)

    def on_btn_cancelar_item_clicked(self, objeto):
        self.obj("notebook").set_show_tabs(True)
        self.estadoedicion(False)

        self.obj("txt_it_00").set_text("")
        self.obj("txt_it_00_1").set_text("")
        self.obj("txt_it_00_2").set_text("")
        self.obj("txt_it_00_3").set_text("")
        self.obj("txt_it_00_4").set_text("")
        self.obj("txt_it_00_5").set_text("")
        self.obj("txt_it_00_6").set_text("")
        self.obj("txt_it_01").set_text("")
        self.obj("cmb_it_02").set_model(None)
        self.obj("txt_it_03").set_value(1.0)
        self.obj("txt_it_04").set_text("")

    def on_btn_item_clicked(self, objeto):
        self.txt_cod_cat, self.txt_des_cat = self.obj("txt_it_00_5"), self.obj("txt_it_00_6")

        from clases.llamadas import items
        items(self.nav.datos_conexion, self)

    def on_item_changed(self, objeto):
        if len(self.obj("txt_it_00").get_text()) == 0:
            estado = False
        else:
            estado = Op.comprobar_numero(int, self.obj("txt_it_00"),
                "Código de Ítem", self.obj("barraestado"))
        self.obj("btn_guardar_item").set_sensitive(estado)

    def on_cmb_it_02_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            costo = Decimal(self.obj("txt_it_01").get_text())
            venta = Decimal(model[active][0])

            # Cálculo del porcentaje de utilidad
            utilidad = venta - costo
            porc_uti = round(utilidad * 100 / venta, 2)
            self.obj("txt_it_04").set_text(str(porc_uti))

    def cmb_it_02_config(self):
        lista = ListStore(int, str, float)
        objeto.set_model(lista)

        cell = CellRendererText()
        objeto.pack_start(cell, True)
        objeto.add_attribute(cell, 'text', 2)

        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, "*", tabla, " ORDER BY " + cod)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()

        lista.clear()
        for i in range(0, cant):
            listafila = [datos[i][0], datos[i][1]]
            if tabla in ("ajustemotivos", "impuestos"):
                listafila.append(datos[i][2])
            if tabla == "turnos":
                listafila.extend([str(datos[i][2]), str(datos[i][3])])
            lista.append(listafila)


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)

    col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Nro. Contrato", celda0, 1, True, 100, 150)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Cód. Empleado", celda0, 2, True, 100, 150)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Tipo Doc. Identidad", celda0, 3, True, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Nro. Doc. Identidad", celda0, 4, True, 200)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Nombre y Apellido", celda1, 5, True, 150)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Dirección", celda1, 6, True, 250)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Teléfono", celda1, 7, True, 250)
    col7.set_sort_column_id(7)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(5)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 5)

    lista = ListStore(int, int, int, str, str, str, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
    " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", NroContrato, " +
        "idEmpleado, idTipoDocumento, NroDocumento, NombreApellido, " +
        "DireccionPrincipal, TelefonoPrincipal", self.tabla + "_s",
        opcion + " ORDER BY " + self.campoid)
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
    elif idcolumna == 6:
        col, self.campo_buscar = "Dirección Principal", "DireccionPrincipal"
    elif idcolumna == 7:
        col, self.campo_buscar = "Teléfono Principal", "TelefonoPrincipal"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = str(seleccion.get_value(iterador, 1))
    valor2 = seleccion.get_value(iterador, 4)
    valor3 = seleccion.get_value(iterador, 5)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n\nCódigo: " + valor0 +
        "\nNro. Contrato: " + valor1 + "\nNro. Documento: " + valor2 +
        "\nEmpleado: " + valor3)

    self.obj("grilla").get_selection().unselect_all()
    self.obj("barraestado").push(0, "")

    if eleccion:
        conexion = Op.conectar(self.datos_conexion)
        Op.eliminar(conexion, self.tabla, valor0)
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
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][4], body_ce), Par(datos[i][5], body_iz)])

    listado.listado(self.titulo, lista, [100, 100, 200], A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = seleccion.get_value(iterador, 5)
        valor2 = seleccion.get_value(iterador, 6)
        valor3 = seleccion.get_value(iterador, 7)

        valor2 = "" if valor2 is None else valor2
        valor3 = "" if valor3 is None else valor3

        self.origen.txt_cod_vnd.set_text(valor0)
        self.origen.txt_nom_vnd.set_text(valor1)

        try:  # Dirección Principal
            self.origen.txt_dir_vnd.set_text(valor2)
        except:
            pass

        try:  # Telefono Principal
            self.origen.txt_tel_vnd.set_text(valor3)
        except:
            pass

        self.on_btn_salir_clicked(0)
    except:
        pass
