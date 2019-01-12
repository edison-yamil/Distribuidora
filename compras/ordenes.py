#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date
from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen):
        self.editando = edit
        self.nav = origen

        arch = Op.archivo("compra_ordenes")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(650, 600)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de " + self.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.estadoedicion(True)
        self.estadoguardar(False)
        self.estadoitem(False)
        self.config_grilla_items()

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_01_2").set_max_length(12)
        self.obj("txt_02").set_max_length(10)

        self.obj("txt_00").set_tooltip_text("Ingrese el Número de " + self.nav.titulo)
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("al Proveedor de los ítems"))
        self.obj("txt_01_1").set_tooltip_text("Razón Social del Proveedor")
        self.obj("txt_01_2").set_tooltip_text("Nro. de Documento de Identidad del Proveedor")
        self.obj("txt_01_3").set_tooltip_text("Dirección principal del Proveedor")
        self.obj("txt_01_4").set_tooltip_text("Teléfono principal del Proveedor")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("un Pedido de Compra para cargar la Orden"))
        self.obj("txt_00").grab_focus()

        self.obj("txt_it_01").set_max_length(10)
        self.obj("txt_it_01_1").set_max_length(40)
        self.obj("txt_it_02").set_max_length(14)
        self.obj("txt_it_03").set_max_length(14)
        self.obj("txt_it_05").set_max_length(100)

        self.obj("txt_it_01").set_tooltip_text("Ingrese el Código del Ítem")
        self.obj("txt_it_01_1").set_tooltip_text("Ingrese el Código de Barras del Ítem")
        self.obj("txt_it_01_2").set_tooltip_text("Descripción del Ítem")
        self.obj("txt_it_01_3").set_tooltip_text("Presentación del Ítem")
        self.obj("txt_it_01_4").set_tooltip_text("Categoría del Ítem")
        self.obj("txt_it_02").set_tooltip_text("Ingrese la Cantidad de Ítems")
        self.obj("txt_it_03").set_tooltip_text("Ingrese el Precio Acordado del Ítem")
        self.obj("txt_it_04").set_tooltip_text("Ingrese el Porcentaje de Descuento Acordado")
        self.obj("txt_it_05").set_tooltip_text("Ingrese una Observación sobre el Ítems")

        self.idFormaPago = self.idTipoDoc = -1
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_01_2"), self.obj("cmb_tipo_doc")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_01_3"), self.obj("txt_01_4")
        self.txt_nro_ped = self.obj("txt_02")

        self.txt_cod_it = self.obj("txt_it_01")
        self.txt_bar_it, self.txt_nom_it = self.obj("txt_it_01_1"), self.obj("txt_it_01_2")
        self.txt_des_pres, self.txt_des_cat = self.obj("txt_it_01_3"), self.obj("txt_it_01_4")

        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_pago"), "formapagos", "idFormaPago")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            fecha = seleccion.get_value(iterador, 1)[0:-9]  # Quita la Hora
            ruc = seleccion.get_value(iterador, 2)
            nombre = seleccion.get_value(iterador, 3)
            direc = seleccion.get_value(iterador, 4)
            telef = seleccion.get_value(iterador, 5)
            pago = seleccion.get_value(iterador, 7)
            resp = seleccion.get_value(iterador, 11)
            aprob = seleccion.get_value(iterador, 12)

            idper = str(seleccion.get_value(iterador, 14))
            tipodoc = str(seleccion.get_value(iterador, 15))
            pedido = str(seleccion.get_value(iterador, 16))

            direc = "" if direc is None else direc
            telef = "" if telef is None else telef

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_fecha").set_text(fecha)
            self.obj("txt_01").set_text(idper)
            self.obj("txt_01_1").set_text(nombre)
            self.obj("txt_01_2").set_text(ruc)
            self.obj("txt_01_2").set_text(direc)
            self.obj("txt_01_3").set_text(telef)
            self.obj("txt_02").set_text(pedido)

            # Asignación de Tipo de Documento en Combo
            model, i = self.obj("cmb_tipo_doc").get_model(), 0
            while model[i][0] != tipodoc: i += 1
            self.obj("cmb_tipo_doc").set_active(i)

            # Asignación de Forma de Pago en Combo
            model, i = self.obj("cmb_pago").get_model(), 0
            while model[i][0] != pago: i += 1
            self.obj("cmb_pago").set_active(i)

            if aprob != 1:
                self.obj("btn_aprobar").set_sensitive(True)
                self.obj("btn_rechazar").set_sensitive(True)
            else:
                self.obj("hbox1").set_sensitive(False)
                self.obj("vbox1").set_sensitive(False)
                self.obj("vbox3").set_sensitive(False)
                self.obj("hbox16").set_sensitive(False)
                self.obj("grilla").set_sensitive(False)
                self.obj("hbox18").set_sensitive(False)

                Mens.no_puede_modificar_eliminar_anular(1,
                    "Seleccionó:\n\nNro. de Orden: " + self.cond +
                    "\nFecha: " + fecha + "\nResponsable: " + resp +
                    "\n\nEsta Orden de Compra ya ha sido Aprobada." +
                    "\nSolo puede modificar Órdenes pendientes de aprobación.")

            self.encabezado_guardado = True
            self.editando_pedido = True if len(pedido) > 0 else False
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))
            self.obj("txt_fecha").set_text(Cal.mysql_fecha(date.today()))

            self.obj("cmb_tipo_doc").set_active(0)
            self.obj("cmb_pago").set_active(0)
            self.encabezado_guardado = self.editando_pedido = False

        self.pedido_guardado = True
        self.conexion = Op.conectar(self.nav.datos_conexion)
        self.cargar_grilla_items()

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_encabezado()
        self.guardar_cerrar()

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def on_btn_aprobar_clicked(self, objeto):
        self.encabezado_guardado = False
        self.guardar_encabezado("1")

        # Generar Orden en formato PDF
        orden = self.obj("txt_00").get_text()
        proveedor = [self.obj("txt_01_2").get_text(), self.obj("txt_01_1").get_text(),
            self.obj("txt_01_3").get_text(), self.obj("txt_01_4").get_text()]

        # Obtención de los datos de la Tabla, los detalles de la Orden
        datos = self.obj("grilla").get_model()
        cant = len(datos)

        from clases.listado import tabla_celda_titulo
        from clases.listado import tabla_celda_centrado
        from clases.listado import tabla_celda_just_izquierdo
        from clases.listado import tabla_celda_just_derecho
        from informes.compra_ordenes import genera_orden_compra
        from reportlab.platypus import Paragraph as Par

        head = tabla_celda_titulo()
        body_ce = tabla_celda_centrado()
        body_iz = tabla_celda_just_izquierdo()
        body_de = tabla_celda_just_derecho()

        lista = [[Par("Cód. Ítem", head), Par("Código de Barras", head),
            Par("Nombre", head), Par("Cantidad", head)]]
        for i in range(0, cant):
            codbar = "" if datos[i][1] is None else datos[i][1]
            lista.append([Par(str(datos[i][0]), body_ce), Par(codbar, body_iz),
                Par(datos[i][2], body_ce), Par(str(datos[i][5]), body_de)])

        # Obtención de la Forma de Pago del Combo de Pago
        model = self.obj("cmb_pago").get_model()
        active = self.obj("cmb_pago").get_active()
        pago = model[active][1]

        datos = [orden, proveedor, pago, lista]
        genera_orden_compra(datos)
        self.guardar_cerrar()

    def on_btn_rechazar_clicked(self, objeto):
        orden = self.obj("txt_00").get_text()
        eleccion = Mens.pregunta_borrar(
            "Rechazar una Orden de Compra la eliminará del registro de Órdenes.")

        if eleccion:
            Op.eliminar(self.conexion, self.nav.tabla, orden)
            self.guardar_cerrar()

    def on_btn_proveedor_clicked(self, objeto):
        from clases.llamadas import personas
        personas(self.nav.datos_conexion, self, "idRolPersona = 3")

    def on_btn_pedido_clicked(self, objeto):
        # Si ya se ha elegido un pedido anterior, pregunta si esta seguro,
        # ya que se modificarán los registros agregados a la Orden de Compra
        eleccion = True if len(self.obj("txt_02").get_text()) == 0 \
        else Mens.pregunta_generico("¿Está seguro?",
        "Elegir OTRO PEDIDO modificará los registros de ítems de la Orden actual.")

        if eleccion:
            from clases.llamadas import pedidocompras
            pedidocompras(self.nav.datos_conexion, self)

    def on_btn_limpiar_pedido_clicked(self, objeto):
        self.guardar_encabezado()

        if len(self.obj("txt_02").get_text()) > 0:
            eleccion = Mens.pregunta_generico("¿Está seguro?",
                "Ha elegido eliminar la relación entre el Pedido\n" +
                "previamente seleccionado y la Orden actual.")

            if eleccion:
                orden = self.obj("txt_00").get_text()
                Op.eliminar(self.conexion, "ordencompras_pedidos", orden)
                self.obj("txt_02").set_text("")
                self.editando_pedido = self.pedido_guardado = False

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 \
        or len(self.obj("txt_01").get_text()) == 0 or self.idFormaPago == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Nro. de Orden", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Cód. de Proveedor", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.encabezado_guardado = False
        self.estadoguardar(estado)

    def on_cmb_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            if objeto == self.obj("cmb_tipo_doc"):
                self.idTipoDoc = model[active][0]
                self.focus_out_event(self.obj("txt_01_2"), 0)
            elif objeto == self.obj("cmb_pago"):
                self.idFormaPago = model[active][0]
            self.verificacion(0)
        else:
            if objeto == self.obj("cmb_tipo_doc"):
                tipo = "Tipos de Documentos de Identidad"
            elif objeto == self.obj("cmb_pago"):
                tipo = "Formas de Pago"
            self.obj("barraestado").push(0, "No existen registros de " + tipo + " en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_01"):
                    self.on_btn_proveedor_clicked(0)
                elif objeto == self.obj("txt_02"):
                    self.on_btn_pedido_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
            tipo = "Proveedor"
        elif objeto == self.obj("txt_02"):
            tipo = "Pedido de Compra"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un " + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            if objeto == self.obj("txt_01"):
                self.obj("txt_01_1").set_text("")
                self.obj("txt_01_2").set_text("")
                self.obj("txt_01_3").set_text("")
                self.obj("txt_01_4").set_text("")
            self.obj("barraestado").push(0, "")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) and \
                Op.comprobar_numero(int, objeto, "Nro. de Orden", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                        "NroOrdenCompra", valor, objeto, self.estadoguardar, self.obj("barraestado"),
                        "El Nro. de Orden de Compra introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Proveedor", self.obj("barraestado")):
                    self.buscar_proveedores(objeto, "idPersona", valor, "Cód. de Proveedor")

            elif objeto == self.obj("txt_01_2"):
                self.buscar_proveedores(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDoc + "'", "Nro. de Documento")

            elif objeto == self.obj("txt_02"):
                self.obj("barraestado").push(0, "")

    def buscar_proveedores(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, "idPersona, RazonSocial, NroDocumento, " +
            "idTipoDocumento, DireccionPrincipal, TelefonoPrincipal", "personas_s",
            " WHERE " + campo + " = " + valor + " AND idRolPersona = 3")
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

    def guardar_encabezado(self, aprobado="0"):
        # Si el encabezado no ha sido registrado
        if not self.encabezado_guardado:
            orden = self.obj("txt_00").get_text()
            prov = self.obj("txt_01").get_text()
            pedido = self.obj("txt_01").get_text()

            sql = orden + ", " + prov + ", " + str(self.idFormaPago)

            if not self.editando:
                Op.insertar(self.conexion, self.nav.tabla, sql)
            else:
                Op.modificar(self.conexion, self.nav.tabla, self.cond + ", " + sql + ", " + aprobado)

            self.obj("txt_fecha").set_text(Cal.mysql_fecha(date.today()))
            self.cond = orden  # Nuevo Nro. Orden original
            self.encabezado_guardado = self.editando = True

            if not self.pedido_guardado:
                sql = orden + ", " + pedido

                if not self.editando_pedido:
                    Op.insertar(self.conexion, "ordencompras_pedidos", sql)
                else:
                    Op.modificar(self.conexion, "ordencompras_pedidos", sql)

                self.editando_pedido = True

    def cargar_item_pedido(self):
        self.pedido_guardado = False
        self.guardar_encabezado()

        orden = self.obj("txt_00").get_text()
        pedido = self.obj("txt_02").get_text()

        # Eliminando Items del Pedido anterior
        datos = self.obj("grilla").get_model()
        cant = len(datos)
        if cant > 0:  # Si existen ítems registrados en la Orden, los elimina
            for i in range(0, cant):
                Op.eliminar(self.conexion, "ordencompras_detalles",
                    orden + ", " + str(datos[i][0]))

        # Obteniendo Items desde Pedido seleccionado
        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, "idItem, Cantidad",
            "pedidocompras_detalles_s", " WHERE NroPedidoCompra = " + pedido)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        # Cargando Items desde Pedido seleccionado
        for i in range(0, cant):
            Op.insertar(self.conexion, "ordencompras_detalles", orden + ", " +
                str(datos[i][0]) + ", " + str(datos[i][1]) + ", NULL, NULL, NULL")

        self.cargar_grilla_items()
        self.verificacion(0)

    def guardar_cerrar(self):
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def estadoedicion(self, estado):
        self.obj("txt_00").set_sensitive(estado)
        self.obj("vbox1").set_visible(estado)
        self.obj("btn_cancelar").set_sensitive(estado)

    def estadoguardar(self, estado):
        self.obj("hbox9").set_sensitive(estado)
        self.obj("hbuttonbox_abm").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)

        # Obligatoriamente debe poseer un detalle para poder Guardar
        guardar = True if estado and len(self.obj("grilla").get_model()) > 0 else False

        self.obj("btn_guardar").set_sensitive(guardar)
        self.obj("btn_aprobar").set_sensitive(guardar)
        self.obj("btn_rechazar").set_sensitive(guardar)

##### Ítems ############################################################

    def config_grilla_items(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Cód. Ítem", celda0, 0, True, 100, 200)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Código de Barras", celda0, 1, True, 150, 250)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Nombre", celda1, 2, True, 150, 300)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Categoría", celda1, 3, True, 150, 300)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Presentacion", celda1, 4, True, 150, 300)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Cantidad", celda2, 5, True, 100, 150)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Precio Unitario", celda2, 6, True, 150, 300)
        col6.set_sort_column_id(6)
        col7 = Op.columnas("% Desc.", celda2, 7, True, 100, 150)
        col7.set_sort_column_id(7)
        col8 = Op.columnas("Descuento", celda2, 8, True, 100, 150)
        col8.set_sort_column_id(8)
        col9 = Op.columnas("Sub Total", celda2, 9, True, 100, 150)
        col9.set_sort_column_id(9)
        col10 = Op.columnas("Observaciones", celda1, 10, True, 150, 300)
        col10.set_sort_column_id(10)

        lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(1)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, str, str, str, float, float, float, float, float, str)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_items(self):
        cursor = Op.consultar(self.conexion, "idItem, CodigoBarras, Nombre, " +
            "Categoria, Presentacion, Cantidad, PrecioAcordado, PorcDescuento, " +
            "MontoDescuento, SubTotal, Observaciones", "ordencompras_detalles_s",
            " WHERE NroOrdenCompra = " + self.obj("txt_00").get_text() + " ORDER BY idItem")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        total = 0.0
        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2],
                datos[i][3], datos[i][4], datos[i][5], datos[i][6],
                datos[i][7], datos[i][8], datos[i][9], datos[i][10]])
            total += datos[i][9]

        self.obj("txt_total").set_text(str(total))

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_clicked(self, objeto):
        self.editando_item = False
        self.funcion_item()

    def on_btn_modificar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Modificar.")
        else:
            self.editando_item = True
            self.funcion_item()

    def on_btn_eliminar_clicked(self, objeto):
        self.guardar_encabezado()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            item = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Eliminar.")
        else:
            pedido = self.obj("txt_00").get_text()
            codbar = seleccion.get_value(iterador, 1)
            nomb = seleccion.get_value(iterador, 2)
            cant = str(seleccion.get_value(iterador, 5))

            codbar = "" if codbar is None else codbar

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Código de Barras: " + codbar + "\nNombre: " + nomb +
                "\nCantidad: " + cant + " unidades")

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "ordencompras_detalles", pedido + ", " + item)
                self.cargar_grilla_items()

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_clicked(0)

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla").set_search_column(i)

##### Agregar-Modificar Ítems ##########################################

    def estadoitem(self, estado):
        self.obj("vbox3").set_visible(estado)
        self.obj("hbuttonbox_item").set_visible(estado)

    def funcion_item(self):
        self.guardar_encabezado()

        if self.editando_item:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.cond_item = str(seleccion.get_value(iterador, 0))
            bar = seleccion.get_value(iterador, 1)
            nomb = seleccion.get_value(iterador, 2)
            cat = seleccion.get_value(iterador, 3)
            pres = seleccion.get_value(iterador, 4)
            cant = str(seleccion.get_value(iterador, 5))
            precio = str(seleccion.get_value(iterador, 6))
            desc = seleccion.get_value(iterador, 7)
            obs = seleccion.get_value(iterador, 10)

            bar = "" if bar is None else bar
            obs = "" if obs is None else obs

            self.obj("txt_it_01").set_text(self.cond_item)
            self.obj("txt_it_01_1").set_text(bar)
            self.obj("txt_it_01_2").set_text(nomb)
            self.obj("txt_it_01_3").set_text(pres)
            self.obj("txt_it_01_4").set_text(cat)
            self.obj("txt_it_02").set_text(cant)
            self.obj("txt_it_03").set_text(precio)
            self.obj("txt_it_04").set_value(desc)
            self.obj("txt_it_05").set_text(obs)

        self.obj("btn_guardar_item").set_sensitive(False)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        self.estadoedicion(False)
        self.estadoguardar(False)
        self.estadoitem(True)

    def on_btn_guardar_item_clicked(self, objeto):
        self.guardar_encabezado()

        orden = self.obj("txt_00").get_text()
        item = self.obj("txt_it_01").get_text()
        cant = self.obj("txt_it_02").get_text()
        precio = self.obj("txt_it_03").get_text()
        desc = self.obj("txt_it_04").get_value()
        obs = self.obj("txt_it_05").get_text()

        precio = "NULL" if len(precio) == 0 or float(precio) == 0 else precio
        desc = "NULL" if desc == 0 else str(desc)
        obs = "NULL" if len(obs) == 0 else "'" + obs + "'"

        sql = orden + ", " + item + ", " + cant + ", " + precio + ", " + desc + ", " + obs
        if not self.editando_item:
            Op.insertar(self.conexion, "ordencompras_detalles", sql)
        else:
            Op.modificar(self.conexion, "ordencompras_detalles",
                self.cond_item + ", " + sql)

        self.cargar_grilla_items()
        self.on_btn_cancelar_item_clicked(0)

    def on_btn_cancelar_item_clicked(self, objeto):
        self.estadoedicion(True)
        self.estadoguardar(True)
        self.estadoitem(False)

        self.obj("txt_it_01").set_text("")
        self.obj("txt_it_01_1").set_text("")
        self.obj("txt_it_01_2").set_text("")
        self.obj("txt_it_01_3").set_text("")
        self.obj("txt_it_01_4").set_text("")
        self.obj("txt_it_02").set_text("")
        self.obj("txt_it_03").set_text("")

    def on_btn_item_clicked(self, objeto):
        from clases.llamadas import items
        items(self.nav.datos_conexion, self)

    def verificacion_item(self, objeto):
        if len(self.obj("txt_it_01").get_text()) == 0 or len(self.obj("txt_it_02").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_it_01"), "Código de Ítems", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_it_02"), "Cantidad de Ítems", self.obj("barraestado")):
                if len(self.obj("txt_it_03").get_text()) == 0:
                    estado = True
                else:
                    estado = Op.comprobar_numero(float, self.obj("txt_it_03"),
                        "Precio Unitario Acordado", self.obj("barraestado"))
            else:
                estado = False
        self.obj("btn_guardar_item").set_sensitive(estado)

    def on_item_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_item_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.on_item_focus_out_event(objeto, 0)

    def on_item_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un Ítem.")

    def on_item_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
        else:
            if objeto == self.obj("txt_it_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Ítem", self.obj("barraestado")):
                    self.buscar_item(objeto, "idItem", valor, "Ítem")

            elif objeto == self.obj("txt_it_01_1"):
                self.buscar_item(objeto, "CodigoBarras", "'" + valor + "'", "Barras")

            if objeto == self.obj("txt_it_02"):
                Op.comprobar_numero(float, objeto, "Cantidad de Ítems", self.obj("barraestado"))

            elif objeto == self.obj("txt_it_03"):
                Op.comprobar_numero(float, objeto, "Precio Unitario Acordado", self.obj("barraestado"))

    def buscar_item(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, "idItem, CodigoBarras, Nombre, " +
            "Presentacion, Categoria", "items_s", " WHERE " + campo + " = " + valor)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            codbar = "" if datos[0][1] is None else datos[0][1]
            present = "" if datos[0][3] is None else datos[0][3]
            categ = "" if datos[0][4] is None else datos[0][4]

            self.obj("txt_it_01").set_text(str(datos[0][0]))
            self.obj("txt_it_01_1").set_text(codbar)
            self.obj("txt_it_01_2").set_text(datos[0][2])
            self.obj("txt_it_01_3").set_text(present)
            self.obj("txt_it_01_4").set_text(categ)

            Op.comprobar_unique(self.nav.datos_conexion, "pedidocompras_detalles_s",
                "idItem", str(datos[0][0]) + " AND NroPedidoCompra = " + self.obj("txt_00").get_text(),
                self.obj("txt_it_01"), self.obj("btn_guardar_item"), self.obj("barraestado"),
                "El Ítem introducido ya ha sido registado en este Pedido.")
        else:
            objeto.grab_focus()
            self.obj("btn_guardar_item").set_sensitive(False)
            self.obj("barraestado").push(0, "El Código de " + nombre + " no es válido.")

            otro = self.obj("txt_it_01_1") if objeto == self.obj("txt_it_01") else self.obj("txt_it_01")
            otro.set_text("")

            self.obj("txt_it_01_2").set_text("")
            self.obj("txt_it_01_3").set_text("")
            self.obj("txt_it_01_4").set_text("")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)
    celda2 = Op.celdas(1.0)

    col0 = Op.columnas("Número", celda0, 0, True, 100, 200)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Fecha de Elaboración", celda0, 1, True, 225, 250)
    col1.set_sort_column_id(13)  # Para ordenarse usa la fila 13
    col2 = Op.columnas("RUC Proveedor", celda0, 2, True, 100, 200)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Razón Social", celda1, 3, True, 200, 300)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Dirección", celda1, 4, True, 300, 700)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Teléfono", celda1, 5, True, 100, 150)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Cantidad de Ítems", celda2, 6, True, 100, 200)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Cód. Forma Pago", celda0, 7, True, 100, 200)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Forma de Pago", celda1, 8, True, 150, 250)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Alias de Usuario", celda1, 9, True, 100, 200)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Nro. Documento", celda0, 10, True, 100, 200)
    col10.set_sort_column_id(10)
    col11 = Op.columnas("Nombre de Usuario", celda1, 11, True, 200, 300)
    col11.set_sort_column_id(11)
    col12 = Op.columna_active("Aprobado", 12)
    col12.set_sort_column_id(12)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col12)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 13)

    lista = ListStore(int, str, str, str, str, str, int, int, str, str, str, str, bool,
        str, int, str, int)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar == "FechaHora":
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    if self.obj("rad_act").get_active() or self.obj("rad_ina").get_active():
        aprobado = "1" if self.obj("rad_act").get_active() else "0"
        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += "Aprobado = " + aprobado

    condicion = ""
    if len(self.condicion) > 0:
        condicion = " WHERE " + self.condicion if len(opcion) == 0 \
        else " AND " + self.condicion

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", FechaHora, " +
        "NroDocProveedor, RazonSocial, DireccionPrincipal, TelefonoPrincipal, CantItems, " +
        "idFormaPago, FormaPago, Alias, NroDocUsuario, NombreApellido, Aprobado, " +
        "idProveedor, idTipoDocProveedor, NroPedidoCompra", self.tabla + "_s",
        opcion + condicion + " ORDER BY FechaHora DESC")
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], Cal.mysql_fecha_hora(datos[i][1]),
            datos[i][2], datos[i][3], datos[i][4], datos[i][5], datos[i][6],
            datos[i][7], datos[i][8], datos[i][9], datos[i][10], datos[i][11],datos[i][12],
            str(datos[i][1]), datos[i][13], datos[i][14], datos[i][15]])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Nro. de Orden", self.campoid
    elif idcolumna == 13:
        col, self.campo_buscar = "Fecha de Elaboración", "FechaHora"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 2:
        col, self.campo_buscar = "RUC Proveedor", "NroDocProveedor"
    elif idcolumna == 3:
        col, self.campo_buscar = "Razón Social", "RazonSocial"
    elif idcolumna == 4:
        col, self.campo_buscar = "Dirección", "DireccionPrincipal"
    elif idcolumna == 5:
        col, self.campo_buscar = "Teléfono", "TelefonoPrincipal"
    elif idcolumna == 6:
        col, self.campo_buscar = "Cantidad de Ítems", "CantItems"
    elif idcolumna == 7:
        col, self.campo_buscar = "Cód. Forma Pago", "idFormaPago"
    elif idcolumna == 8:
        col, self.campo_buscar = "Forma de Pago", "FormaPago"
    elif idcolumna == 9:
        col, self.campo_buscar = "Alias de Usuario", "Alias"
    elif idcolumna == 10:
        col, self.campo_buscar = "Nro. Documento", "NroDocUsuario"
    elif idcolumna == 11:
        col, self.campo_buscar = "Nombre de Usuario", "NombreApellido"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 1)[0:-9]
    valor2 = seleccion.get_value(iterador, 1)[-8:]
    valor3 = seleccion.get_value(iterador, 11)
    aprobado = seleccion.get_value(iterador, 12)

    mensaje = "Seleccionó:\n\nNro. de Orden: " + valor0 + \
        "\nFecha: " + valor1 + "\nHora: " + valor2 + "\nResponsable: " + valor3

    if aprobado != 1:
        eleccion = Mens.pregunta_borrar(mensaje)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        if eleccion:
            conexion = Op.conectar(self.datos_conexion)
            Op.eliminar(conexion, self.tabla, valor0)
            conexion.commit()
            conexion.close()  # Finaliza la conexión
            cargar_grilla(self)
    else:
        Mens.no_puede_modificar_eliminar_anular(2, mensaje +
        "\n\nEsta Orden de Compra ya ha sido Aprobada." +
        "\nSolo puede eliminar Órdenes pendientes de aprobación.")


def listar_grilla(self):
    from clases import listado
    from reportlab.platypus import Paragraph as Par
    from reportlab.lib.pagesizes import A4

    datos = self.obj("grilla").get_model()
    cant = len(datos)

    head = listado.tabla_celda_titulo()
    body_ce = listado.tabla_celda_centrado()
    body_iz = listado.tabla_celda_just_izquierdo()

    lista = [[Par("Nro. de Orden", head), Par("Fecha de Elaboración", head),
    Par("Alias de Usuario", head), Par("Nombre", head)]]
    for i in range(0, cant):
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][1], body_ce),
        Par(datos[i][9], body_ce), Par(str(datos[i][11]), body_iz)])

    listado.listado(self.titulo, lista, [70, 125, 75, 150], A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        orden = str(seleccion.get_value(iterador, 0))
        fecha = seleccion.get_value(iterador, 1)

        idper = str(seleccion.get_value(iterador, 14))
        tipodoc = seleccion.get_value(iterador, 15)
        ruc = seleccion.get_value(iterador, 2)
        nombre = seleccion.get_value(iterador, 3)
        direc = seleccion.get_value(iterador, 4)
        telef = seleccion.get_value(iterador, 5)

        direc = "" if valor4 is None else valor4
        telef = "" if valor5 is None else valor5

        # Datos del Proveedor
        self.origen.txt_cod_per.set_text(idper)
        self.origen.txt_nro_doc.set_text(ruc)
        self.origen.txt_rzn_scl.set_text(nombre)
        self.origen.txt_dir_per.set_text(direc)
        self.origen.txt_tel_per.set_text(telef)

        # Combo que indica el Tipo de Documento de Identidad
        model, i = self.origen.cmb_tip_doc.get_model(), 0
        while model[i][0] != tipodoc: i += 1
        self.origen.cmb_tip_doc.set_active(i)

        # Datos de la Orden de Compra
        self.origen.txt_nro_ord.set_text(orden)
        self.origen.txt_fch_ord.set_text(fecha)
        self.origen.cargar_item_orden()

        self.on_btn_salir_clicked(0)
    except:
        pass
