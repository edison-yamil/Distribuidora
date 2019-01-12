#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date
from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class pedidos:

    def __init__(self, datos, tab):
        self.datos_conexion = datos
        self.tabla = tab

        arch = Op.archivo("venta_pedidos")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(700, 600)
        self.obj("ventana").set_modal(True)

        self.obj("ventana").set_title("Notas de Pedido")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_01").set_tooltip_text("Ingrese el Número de Documento de Identidad del Cliente")
        self.obj("txt_01_1").set_tooltip_text("Nombre y Apellido o Razón Social del Cliente")
        self.obj("btn_cliente").set_tooltip_text("Presione este botón para buscar datos de un Cliente")

        self.obj("btn_nuevo_item").set_tooltip_text("Presione este botón para agregar un nuevo Item")
        self.obj("btn_modificar_item").set_tooltip_text("Presione este botón para modificar datos de un Item")
        self.obj("btn_eliminar_item").set_tooltip_text("Presione este botón para eliminar un Item")

        self.idTipoCliente, self.idTipoDoc = "1", -1
        Op.combos_config(self.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")

        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_01_2"), self.obj("cmb_tipo_doc")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_01_3"), self.obj("txt_01_4")
        self.txt_cod_vnd, self.txt_nom_vnd = self.obj("txt_02"), self.obj("txt_02_1")

        self.txt_cod_it, self.txt_bar_it, self.txt_nom_it = self.obj("txt_it_01"), \
            self.obj("txt_it_01_1"), self.obj("txt_it_01_2")
        self.txt_des_pres, self.txt_des_cat = self.obj("txt_it_01_3"), self.obj("txt_it_01_4")

        arch.connect_signals(self)

        self.obj("txt_00").set_text(Op.nuevoid(self.datos_conexion, self.tabla + "_s", "NroPedidoVenta"))
        self.obj("txt_fecha").set_text(Cal.mysql_fecha(date.today()))
        self.obj("cmb_tipo_doc").set_active(0)
        self.obj("txt_01").grab_focus()

        self.estadoitems(False)
        self.estadoguardar(False)
        self.editando = False

        self.conexion = Op.conectar(self.datos_conexion)
        self.config_grilla_detalles()

        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, par):
        self.guardar_encabezado()
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def on_btn_cancelar_clicked(self, par):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def on_btn_cliente_clicked(self, par):
        from clases.llamadas import personas
        personas(self.datos_conexion, self, "Cliente = 1")

    def on_btn_vendedor_clicked(self, par):
        from clases.llamadas import vendedores
        vendedores(self.datos_conexion, self)

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_01_2").get_text()) == 0 or self.idTipoDoc == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Nro. de Pedido", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Cód. de Cliente", self.obj("barraestado")):
                estado = True
            else:
                estado = False

        self.encabezado_guardado = False
        self.estadoguardar(estado)

    def on_cmb_tipo_doc_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            self.idTipoDoc = model[active][0]
            self.focus_out_event(self.obj("txt_01"), 0)
        else:
            self.obj("barraestado").push(0, "No existen registros de " +
            "Tipos de Documentos de Identidad en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_cliente_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un Cliente.")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")

            if objeto == self.obj("txt_01"):  # Código de Cliente
                self.obj("txt_01_1").set_text("")
                self.obj("txt_01_2").set_text("")
                self.obj("txt_01_3").set_text("")
                self.obj("txt_01_4").set_text("")

            elif objeto == self.obj("txt_01_2") \
            and len(self.obj("txt_01").get_text()) == 0:  # Nro. Documento de Cliente
                self.obj("txt_01_1").set_text("")
                self.obj("txt_01_3").set_text("")
                self.obj("txt_01_4").set_text("")

            elif objeto == self.obj("txt_02"):  # Código de Vendedor
                self.obj("txt_02_1").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                if Op.comprobar_numero(int, objeto, "Nro. de Pedido", self.obj("barraestado")):
                    Op.comprobar_unique(self.datos_conexion, self.tabla + "_s",
                        "NroPedidoVenta", valor, objeto, self.estadoguardar, self.obj("barraestado"),
                        "El Nro. de Pedido introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Cliente", self.obj("barraestado")):
                    self.buscar_clientes(objeto, "idPersona", valor, "Cód. de Cliente")

            elif objeto == self.obj("txt_01_2"):
                self.buscar_clientes(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDoc + "'", "Nro. de Documento")

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Cód. de Vendedor", self.obj("barraestado")):
                    conexion = Op.conectar(self.datos_conexion)
                    cursor = Op.consultar(conexion, "NombreApellido",
                        "vendedores_s", " WHERE idVendedor = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("txt_02_1").set_text(datos[0][0])
                        self.obj("barraestado").push(0, "")
                        self.verificacion(0)
                    else:
                        self.estadoguardar(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "El Cód. de Vendedor no es válido.")
                        self.obj("txt_02_1").set_text("")

    def buscar_clientes(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "idPersona, RazonSocial, NroDocumento, " +
            "idTipoDocumento, DireccionPrincipal, TelefonoPrincipal", "personas_s",
            " WHERE " + campo + " = " + valor + " AND Cliente = 1")
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

            # Buscar Tipo de Cliente y Vendedor
            conexion = Op.conectar(self.datos_conexion)
            cursor = Op.consultar(conexion, "idTipoCliente, idVendedor, " +
                "NombreApellido", "clientes_s", " WHERE idCliente = " + str(datos[0][0]))
            datos = cursor.fetchall()
            cant = cursor.rowcount
            conexion.close()  # Finaliza la conexión

            self.idTipoCliente = str(datos[0][0])
            self.obj("txt_02").set_text(str(datos[0][1]))
            self.obj("txt_02_1").set_text(datos[0][2])

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

    def guardar_encabezado(self):
        # Si el encabezado no ha sido registrado
        if not self.encabezado_guardado:
            nro = self.obj("txt_00").get_text()
            cli = self.obj("txt_01").get_text()
            ven = self.obj("txt_02").get_text()

            sql = nro + ", " + cli + ", " + ven
            if not self.editando:
                Op.insertar(self.conexion, self.tabla, sql)
            else:
                Op.modificar(self.conexion, self.tabla, self.cond_ped + ", " + sql)

            self.cond_ped = nro  # Nuevo idPedidoVenta original
            self.encabezado_guardado = self.editando = True

    def estadoguardar(self, estado):
        self.obj("hbuttonbox1").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)

        # Obligatoriamente debe poseer un detalle para poder Guardar
        guardar = True if estado and len(self.obj("grilla").get_model()) > 0 else False
        self.obj("btn_guardar").set_sensitive(guardar)

    def estadoitems(self, estado):
        self.obj("vbox2").set_sensitive(not estado)
        self.obj("btn_cancelar").set_sensitive(not estado)

        self.obj("vbox3").set_visible(estado)
        self.obj("hbuttonbox2").set_visible(estado)

##### Ítems ############################################################

    def config_grilla_detalles(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Código", celda0, 0, True, 90, 90)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Descripción", celda1, 1, True, 270)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Cantidad", celda2, 2, True, 100, 150)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Precio Unitario", celda2, 3, True, 135, 135)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("SubTotal", celda2, 4, True, 135, 135)
        col4.set_sort_column_id(4)

        lista = [col0, col1, col2, col3, col4]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(1)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, float, float, float, int)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_detalles(self):
        # Cargar campo Total
        cursor = Op.consultar(self.conexion, "Total", self.tabla + "_s",
            " WHERE NroPedidoVenta = " + self.obj("txt_00").get_text())
        self.obj("txt_total").set_text(str(cursor.fetchall()[0][0]))

        # Cargar los Detalles de la Factura
        cursor = Op.consultar(self.conexion, "idDetalle, Nombre, Cantidad, " +
            "Precio, SubTotal, idItem", self.tabla + "_detalles_s", " WHERE " +
            "NroPedidoVenta = " + self.obj("txt_00").get_text() + " ORDER BY idItem")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2],
                datos[i][3], datos[i][4], datos[i][5]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_item_clicked(self, par):
        self.editando_item = False
        self.funcion_items()

    def on_btn_modificar_item_clicked(self, par):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.cond_det = str(seleccion.get_value(iterador,0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Modificar.")
        else:
            self.editando_item = True
            self.funcion_items()

    def on_btn_eliminar_item_clicked(self, par):
        self.guardar_encabezado()
        nro = self.obj("txt_00").get_text()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            det = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Eliminar.")
        else:
            item = str(seleccion.get_value(iterador, 4))
            nomb = seleccion.get_value(iterador, 1)
            cant = str(seleccion.get_value(iterador, 2))
            precio = str(seleccion.get_value(iterador, 3))

            eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
                "\nCód. Ítem: " + item + "\nNombre: " + nomb +
                "\nCantidad: " + cant + "\nPrecio Unitario: " + precio)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, self.tabla + "_detalles", nro + ", " + det)
                self.cargar_grilla_detalles()
                self.estadoguardar(True)

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_item_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_item_clicked(0)

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla").set_search_column(i)

##### Agregar-Modificar Ítems ##########################################

    def funcion_items(self):
        self.guardar_encabezado()

        if self.editando_item:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            item = str(seleccion.get_value(iterador, 4))
            cant = str(seleccion.get_value(iterador, 2))
            precio = str(seleccion.get_value(iterador, 3))

            self.obj("txt_it_00").set_text(self.cond_det)
            self.obj("txt_it_01").set_text(item)
            self.on_item_focus_out_event(self.obj("txt_it_01"), 0)
            self.obj("txt_it_02").set_text(cant)
            self.obj("txt_it_03").set_text(precio)
        else:
            self.obj("txt_it_00").set_text(Op.nuevoid(self.conexion,
                "pedidoventas_detalles_s WHERE NroPedidoVenta = " +
                self.obj("txt_00").get_text(), "idDetalle"))

        self.obj("btn_guardar_item").set_sensitive(False)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        self.estadoguardar(False)
        self.estadoitems(True)

    def on_btn_guardar_item_clicked(self, objeto):
        self.guardar_encabezado()

        nro = self.obj("txt_00").get_text()
        det = self.obj("txt_it_00").get_text()
        item = self.obj("txt_it_01").get_text()
        cant = self.obj("txt_it_02").get_text()
        precio = self.obj("txt_it_03").get_text()

        sql = nro + ", " + det + ", " + item + ", " + cant + ", " + precio
        if not self.editando_item:
            Op.insertar(self.conexion, self.tabla + "_detalles", sql)
        else:
            Op.modificar(self.conexion, self.tabla + "_detalles", self.cond_det + ", " + sql)

        self.cargar_grilla_detalles()
        self.on_btn_cancelar_item_clicked(0)

    def on_btn_cancelar_item_clicked(self, objeto):
        self.obj("txt_it_00").set_text("")
        self.obj("txt_it_01").set_text("")
        self.obj("txt_it_01_1").set_text("")
        self.obj("txt_it_02").set_text("")
        self.obj("txt_it_03").set_text("")
        self.limpiar_items()

        self.estadoguardar(True)
        self.estadoitems(False)

    def on_btn_item_clicked(self, objeto):
        from clases.llamadas import items
        items(self.datos_conexion, self)

    def verificacion_item(self, objeto):
        if len(self.obj("txt_it_00").get_text()) == 0 or len(self.obj("txt_it_01").get_text()) == 0 \
        or len(self.obj("txt_it_02").get_text()) == 0 or len(self.obj("txt_it_03").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_it_00"), "Cód. de Detalle", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_it_01"), "Cód. de Ítem", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_it_02"), "Cantidad de Ítems", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_it_03"), "Precio Unitario", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar_item").set_sensitive(estado)

    def on_item_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_item_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def on_item_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un ítem.")

    def on_item_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")

            if objeto == self.obj("txt_it_01"):  # Código del Ítem
                self.obj("txt_it_01_1").set_text("")
                self.limpiar_items()
            elif objeto == self.obj("txt_it_01_1") and len(self.obj("txt_it_01").get_text()) == 0:
                self.obj("txt_it_01").set_text("")
                self.limpiar_items()
        else:
            if objeto == self.obj("txt_it_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond_det) and \
                Op.comprobar_numero(int, objeto, "Cód. de Detalle", self.obj("barraestado")):
                    Op.comprobar_unique(self.conexion, self.tabla + "_detalles_s",
                        "idDetalle", valor + " AND NroPedidoVenta = " + self.obj("txt_00").get_text(),
                        objeto, self.estadoguardar, self.obj("barraestado"),
                        "El Código introducido ya ha sido registado en este Pedido.")

            if objeto == self.obj("txt_it_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Ítem", self.obj("barraestado")):
                    self.buscar_items(objeto, valor, "Cód. de Ítem")

            elif objeto == self.obj("txt_it_01_1"):
                self.buscar_items(objeto, valor, "Código de Barras")

            elif objeto == self.obj("txt_it_02"):
                Op.comprobar_numero(float, objeto, "Cantidad de Ítems", self.obj("barraestado"))

            elif objeto == self.obj("txt_it_02"):
                Op.comprobar_numero(float, objeto, "Precio Unitario", self.obj("barraestado"))

    def buscar_items(self, objeto, valor, nombre):
        if objeto == self.obj("txt_it_01"):
            campo = "idItem"
        else:
            campo = "CodigoBarras"
            valor = "'" + valor + "'"

        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(self.conexion, "I.idItem, I.CodigoBarras, " +
            "I.Nombre, I.Presentacion, I.Categoria, IFNULL(P.PrecioVenta, 0)",
            "items_s I LEFT JOIN precios_s P ON ((I.idItem = P.idItem) " +
            "AND (P.idTipoCliente = " + self.idTipoCliente + "))",
            " WHERE I." + campo + " = " + valor)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            codbar = "" if datos[0][1] is None else datos[0][1]

            self.obj("txt_it_01").set_text(str(datos[0][0]))
            self.obj("txt_it_01_1").set_text(codbar)
            self.obj("txt_it_01_2").set_text(datos[0][2])
            self.obj("txt_it_01_3").set_text(datos[0][3])
            self.obj("txt_it_01_4").set_text(datos[0][4])

            self.obj("txt_it_03").set_text(str(datos[0][5]))  # Precio Unitario
            self.obj("barraestado").push(0, "")
        else:
            objeto.grab_focus()
            self.obj("btn_guardar_item").set_sensitive(False)
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_it_01_1") if objeto == self.obj("txt_it_01") else self.obj("txt_it_01")
            self.limpiar_items()
            otro.set_text("")

    def limpiar_items(self):
        self.obj("txt_it_01_2").set_text("")
        self.obj("txt_it_01_3").set_text("")  # Presentación
        self.obj("txt_it_01_4").set_text("")  # Categoría


class nota_pedido_buscar:

    def __init__(self, v_or):
        self.origen = v_or

        arch = Op.archivo("buscador")
        self.obj = arch.get_object

        self.obj("ventana").set_title("Seleccione una Nota de Pedido")
        self.obj("ventana").set_default_size(950, 350)
        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        self.config_grilla_buscar()
        self.cargar_grilla_buscar()

        arch.connect_signals(self)
        self.obj("ventana").show()

    def on_btn_busq_seleccionar_clicked(self, objeto):
        seleccion, iterador = self.obj("grilla_buscar").get_selection().get_selected()
        nota = str(seleccion.get_value(iterador, 0))
        self.origen.txt_nro_ped.set_text(nota)

        self.origen.cargar_item_nota_pedido()
        self.obj("ventana").destroy()

    def on_btn_busq_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_filtrar_clicked(self, objeto):
        self.cargar_grilla_buscar()

    def on_btn_buscar_clicked(self, objeto):
        if self.campo_buscar == "FechaHora":
            lista = Cal.calendario()

            if lista is not False:
                if objeto == self.obj("btn_buscar"):
                    self.fecha_ini = lista[1]
                    self.obj("txt_buscar").set_text(lista[0])

                    # Si no se seleccionó la fecha final
                    if len(self.obj("txt_buscar2").get_text()) == 0:
                        self.fecha_fin = lista[1]
                        self.obj("txt_buscar2").set_text(lista[0])

                else:  # btn_buscar2
                    self.fecha_fin = lista[1]
                    self.obj("txt_buscar2").set_text(lista[0])

                    # Si no se seleccionó la fecha inicial
                    if len(self.obj("txt_buscar").get_text()) == 0:
                        self.fecha_ini = lista[1]
                        self.obj("txt_buscar").set_text(lista[0])

    def on_grilla_buscar_row_activated(self, objeto, fila, col):
        self.on_btn_busq_seleccionar_clicked(0)

    def on_txt_buscar_key_press_event(self, objeto, evento):
        if evento.keyval == 65293:  # Presionando Enter
            self.on_btn_filtrar_clicked(0)

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla_buscar").set_search_column(i)

        self.obj("txt_buscar").set_editable(True)
        self.obj("hbox_fecha").set_visible(False)
        self.columna_buscar(i)

    def config_grilla_buscar(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Nro. Nota", celda0, 0, True, 100, 150)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Fecha de Pedido", celda0, 1, True, 225, 250)
        col1.set_sort_column_id(11)  # Para ordenarse usa la fila 11
        col2 = Op.columnas("Tipo Doc. Cliente", celda0, 2, True, 100, 200)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Nro. Doc. Cliente", celda0, 3, True, 100, 200)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Razón Social", celda1, 4, True, 200, 300)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Cantidad de Ítems", celda2, 5, True, 150, 250)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Total", celda2, 6, True, 150, 250)
        col6.set_sort_column_id(6)
        col7 = Op.columnas("Alias de Usuario", celda1, 7, True, 100, 200)
        col7.set_sort_column_id(7)
        col8 = Op.columnas("Nro. Documento", celda0, 8, True, 100, 200)
        col8.set_sort_column_id(8)
        col9 = Op.columnas("Nombre de Usuario", celda1, 9, True, 200, 300)
        col9.set_sort_column_id(9)

        lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla_buscar").append_column(columna)

        self.obj("grilla_buscar").set_rules_hint(True)
        self.obj("grilla_buscar").set_search_column(0)
        self.obj("grilla_buscar").set_property('enable-grid-lines', 3)

        self.obj("txt_buscar").set_editable(True)
        self.obj("hbox_fecha").set_visible(False)
        self.columna_buscar(0)

        lista = ListStore(int, str, str, str, str, float, float, str, str, str, int, str)
        self.obj("grilla_buscar").set_model(lista)
        self.obj("grilla_buscar").show()

    def cargar_grilla_buscar(self):
        if self.campo_buscar == "FechaHora":
            opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
            " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
        else:
            opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
            " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

        conexion = Op.conectar(self.origen.datos_conexion)
        cursor = Op.consultar(conexion, "NroPedidoVenta, FechaHora, " +
            "idTipoDocCliente, NroDocCliente, RazonSocial, CantItems, " +
            "Total, Alias, NroDocUsuario, NombreApellido, idCliente",
            "pedidoventas_s", opcion + " ORDER BY FechaHora DESC")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        lista = self.obj("grilla_buscar").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], Cal.mysql_fecha_hora(datos[i][1]),
                datos[i][2], datos[i][3], datos[i][4], datos[i][5], datos[i][6],
                datos[i][7], datos[i][8], datos[i][9], datos[i][10],
                str(datos[i][1])])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def columna_buscar(self, idcolumna):
        if idcolumna == 0:
            col, self.campo_buscar = "Nro. Nota", "NroPedidoVenta"
        elif idcolumna == 11:
            col, self.campo_buscar = "Fecha de Pedido", "FechaHora"
            self.obj("txt_buscar").set_editable(False)
            self.obj("hbox_fecha").set_visible(True)
        elif idcolumna == 2:
            col, self.campo_buscar = "Tipo Doc. Cliente", "idTipoDocCliente"
        elif idcolumna == 3:
            col, self.campo_buscar = "Nro. Doc. Cliente", "NroDocCliente"
        elif idcolumna == 4:
            col, self.campo_buscar = "Razón Social", "RazonSocial"
        elif idcolumna == 5:
            col, self.campo_buscar = "Cantidad de Ítems", "CantItems"
        elif idcolumna == 6:
            col, self.campo_buscar = "Total", "Total"
        elif idcolumna == 7:
            col, self.campo_buscar = "Alias de Usuario", "Alias"
        elif idcolumna == 8:
            col, self.campo_buscar = "Nro. Documento", "NroDocUsuario"
        elif idcolumna == 9:
            col, self.campo_buscar = "Nombre de Usuario", "NombreApellido"

        self.obj("label_buscar").set_text("Filtrar por " + col + ":")
