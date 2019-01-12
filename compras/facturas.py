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

        arch = Op.archivo("compra_facturas")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(870, 650)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de " + self.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("btn_lotes").set_tooltip_text(
        "Presione este botón para registrar los Lotes de los Ítems seleccionados")
        self.obj("btn_cuentas").set_tooltip_text(
        "Presione este botón para registrar las Cuentas a Pagar de las Facturas a Crédito")
        self.obj("btn_confirmar").set_tooltip_text(
        "Presione este botón para Guardar el registro y/o Confirmarlo\n" +
        "Una Factura confirmada no podrá ser Modificada o Eliminada con posterioridad\n" +
        "Por lo tanto, compruebe que los datos están todos correctos")

        self.obj("txt_00").set_max_length(15)
        self.obj("txt_01").set_max_length(10)

        self.obj("txt_00").set_tooltip_text("Ingrese el Número de " + self.nav.titulo)
        self.obj("txt_01").set_tooltip_text("Ingrese el Número de Timbrado de la Factura")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("la Fecha de expedición de la Factura"))
        self.obj("txt_03").set_tooltip_text(Mens.usar_boton("al Proveedor de los ítems"))
        self.obj("txt_03_1").set_tooltip_text("Razón Social del Proveedor")
        self.obj("txt_03_2").set_tooltip_text("Ingrese el Nro. de Documento de Identidad del Proveedor")
        self.obj("txt_03_3").set_tooltip_text("Dirección principal del Proveedor")
        self.obj("txt_03_4").set_tooltip_text("Teléfono principal del Proveedor")
        self.obj("txt_00").grab_focus()

        self.idTipoFact = self.idTipoDoc = -1
        self.txt_nro_ord, self.txt_fch_ord = self.obj("txt_orden"), self.obj("txt_fecha")
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_03"), self.obj("txt_03_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_03_2"), self.obj("cmb_tipo_doc")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_03_3"), self.obj("txt_03_4")

        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_fact"), "tipofacturas", "idTipoFactura")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")
        arch.connect_signals(self)

        self.conexion = Op.conectar(self.nav.datos_conexion)
        self.config_grilla_detalles()

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond_timb = str(seleccion.get_value(iterador, 0))
            self.cond_fact = seleccion.get_value(iterador, 1)
            fecha = seleccion.get_value(iterador, 2)
            tipo = seleccion.get_value(iterador, 7)
            resp = seleccion.get_value(iterador, 13)
            conf = seleccion.get_value(iterador, 14)

            idper = str(seleccion.get_value(iterador, 16))
            tipodoc = seleccion.get_value(iterador, 17)
            ruc = seleccion.get_value(iterador, 3)
            nombre = seleccion.get_value(iterador, 4)
            direc = seleccion.get_value(iterador, 5)
            telef = seleccion.get_value(iterador, 6)

            direc = "" if direc is None else direc
            telef = "" if telef is None else telef

            self.obj("txt_00").set_text(self.cond_fact)
            self.obj("txt_01").set_text(self.cond_timb)
            self.obj("txt_02").set_text(fecha)
            self.obj("txt_03").set_text(idper)
            self.obj("txt_03_1").set_text(nombre)
            self.obj("txt_03_2").set_text(ruc)
            self.obj("txt_03_3").set_text(direc)
            self.obj("txt_03_4").set_text(telef)

            # Asignación de Tipo de Documento en Combo
            model, i = self.obj("cmb_tipo_doc").get_model(), 0
            while model[i][0] != tipodoc: i += 1
            self.obj("cmb_tipo_doc").set_active(i)

            # Asignación de Tipo de Factura en Combo
            model, i = self.obj("cmb_tipo_fact").get_model(), 0
            while model[i][0] != tipo: i += 1
            self.obj("cmb_tipo_fact").set_active(i)

            self.cargar_grilla_detalles()
            self.obj("notebook").set_current_page(1)

            if conf != 1:
                self.fecha = seleccion.get_value(iterador, 15)
                self.estadoguardar(True)
                self.encabezado_guardado = True

                orden = seleccion.get_value(iterador, 18)
                fecha = seleccion.get_value(iterador, 19)

                if orden is not None:
                    self.obj("txt_orden").set_text(orden)
                    self.obj("txt_fecha").set_text(fecha)
                    self.orden_guardada = self.editando_orden = True
                else:
                    self.orden_guardada = self.editando_orden = False
            else:
                self.obj("notebook").set_show_tabs(False)
                self.obj("box1").set_sensitive(False)
                self.obj("box2").set_sensitive(False)
                self.obj("notebook").set_sensitive(False)
                self.obj("grilla").set_sensitive(False)
                self.obj("box4").set_sensitive(False)
                self.obj("hbox16").set_sensitive(False)

                Mens.no_puede_modificar_eliminar_anular(1,
                    "Seleccionó:\n\nNro. de Factura: " + self.cond_fact +
                    "\n\nNro. de Timbrado: " + self.cond_timb +
                    "\nFecha: " + fecha + "\nResponsable: " + resp +
                    "\n\nEsta Factura de Compra ya ha sido Confirmada." +
                    "\nSolo puede modificar Facturas pendientes de confirmación.")
        else:
            self.obj("cmb_tipo_fact").set_active(0)
            self.obj("cmb_tipo_doc").set_active(0)

            self.estadoguardar(False)
            self.encabezado_guardado = self.orden_guardada = self.editando_orden = False

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

    def on_btn_confirmar_clicked(self, objeto):
        self.encabezado_guardado = False
        self.guardar_encabezado("1")
        self.guardar_cerrar()

    def on_btn_cuentas_clicked(self, objeto):
        self.guardar_encabezado()

        if self.idTipoFact == 2:  # Factura a Crédito
            self.conexion.commit()
            self.obj("barraestado").push(0, "La Factura ha sido Guardada.")

            # Datos -> Nro. Factura, Nro. Timbrado y Total
            datos = [self.obj("txt_00").get_text(), self.obj("txt_01").get_text(),
                self.obj("txt_total").get_text()]

            from compras.cuotas import cuotas
            cuotas(self.nav.datos_conexion, "cuentaspagar", datos, self.conexion)
        else:
            self.obj("barraestado").push(0, "Solamente las Facturas a Crédito poseen Cuentas a Pagar.")

    def on_btn_lotes_clicked(self, objeto):
        self.guardar_encabezado()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            detalle = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un Ítem de la lista. Luego presione Registrar Lotes.")
        else:
            fact = self.obj("txt_00").get_text()
            timb = self.obj("txt_01").get_text()

            item = str(seleccion.get_value(iterador, 9))
            cant = seleccion.get_value(iterador, 2)

            buscar = "NroTimbrado = " + timb + " AND NroFactura" + \
                " = '" + fact + "' AND idDetalle = " + detalle
            guardar = timb + ", '" + fact + "', " + detalle

            from compras.lotes import lotes
            lotes(self.conexion, self.nav.datos_conexion, self.nav.tabla, cant, item, buscar, guardar)

    def on_btn_fecha_clicked(self, objeto):
        self.obj("txt_02").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_02").set_text(lista[0])
            self.fecha = lista[1]

    def on_btn_proveedor_clicked(self, objeto):
        from clases.llamadas import personas
        personas(self.nav.datos_conexion, self, "idRolPersona = 3")

    def on_btn_orden_clicked(self, objeto):
        # Si ya se ha elegido una orden anterior, pregunta si esta seguro de
        # querer eliminar todos los registros agregados a la Factura de Compra
        eleccion = True if len(self.obj("txt_orden").get_text()) == 0 \
        else Mens.pregunta_generico("¿Está seguro?",
        "Elegir OTRA ORDEN modificará los registros de ítems de la Factura actual.")

        if eleccion:
            proveedor = self.obj("txt_03").get_text()
            condicion = None if len(proveedor) == 0 else "idProveedor = " + proveedor

            from clases.llamadas import ordencompras
            ordencompras(self.nav.datos_conexion, self, condicion)

    def on_btn_limpiar_orden_clicked(self, objeto):
        self.guardar_encabezado()

        if len(self.obj("txt_orden").get_text()) > 0:
            eleccion = Mens.pregunta_generico("¿Está seguro?",
                "Ha elegido eliminar la relación entre la Orden de Compra\n" +
                "previamente seleccionada y la Factura actual.")

            if eleccion:
                fact = self.obj("txt_00").get_text()
                timb = self.obj("txt_01").get_text()

                Op.eliminar(self.conexion, self.nav.tabla + "_ordenes", timb + ", '" + fact + "'")

                self.obj("txt_orden").set_text("")
                self.obj("txt_fecha").set_text("")
                self.editando_orden = self.orden_guardada = False

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0 or self.idTipoFact == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_01"), "Nro. de Timbrado", self.obj("barraestado")):
                if len(self.obj("txt_03").get_text()) == 0:
                    estado = True
                else:
                    estado = Op.comprobar_numero(int, self.obj("txt_03"),
                        "Cód. de Proveedor", self.obj("barraestado"))
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
                self.focus_out_event(self.obj("txt_03_2"), 0)
            elif objeto == self.obj("cmb_tipo_fact"):
                self.idTipoFact = model[active][0]
            self.verificacion(0)
        else:
            if objeto == self.obj("cmb_tipo_doc"):
                tipo = "Tipos de Documentos de Identidad"
            elif objeto == self.obj("cmb_tipo_fact"):
                tipo = "Tipos de Factura"
            self.obj("barraestado").push(0, "No existen registros de " + tipo + " en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_02"):
                    self.on_btn_fecha_clicked(0)
                elif objeto in (self.obj("txt_03"), self.obj("txt_03_2")):
                    self.on_btn_proveedor_clicked(0)
                elif objeto == self.obj("txt_orden"):
                    self.on_btn_orden_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_02"):
            tipo = "a Fecha de Expedición"
        elif objeto in (self.obj("txt_03"), self.obj("txt_03_2")):
            tipo = " Proveedor"
        elif objeto == self.obj("txt_orden"):
            tipo = "a Orden de Compra"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un" + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")

            if objeto == self.obj("txt_03"):  # Código de Proveedor
                self.obj("txt_03_1").set_text("")
                self.obj("txt_03_2").set_text("")
                self.obj("txt_03_3").set_text("")
                self.obj("txt_03_4").set_text("")

            elif objeto == self.obj("txt_03_2") \
            and len(self.obj("txt_03").get_text()) == 0:  # Nro. Documento de Proveedor
                self.obj("txt_03_1").set_text("")
                self.obj("txt_03_3").set_text("")
                self.obj("txt_03_4").set_text("")
        else:
            if objeto in (self.obj("txt_00"), self.obj("txt_01")):
                fact = self.obj("txt_00").get_text()
                timb = self.obj("txt_01").get_text()

                if len(timb) > 0 and len(fact) > 0 and Op.comprobar_numero(int,
                self.obj("txt_01"), "Nro. de Timbrado", self.obj("barraestado")):
                    # Al editar, comprueba que los valores son diferentes del original
                    busq = "" if not self.editando else " AND " + \
                        "(NroTimbrado <> " + self.cond_timb + " OR" + \
                        " NroFactura <> '" + self.cond_fact + "')"

                    Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                        "NroFactura", "'" + fact + "' AND NroTimbrado = " + timb + busq,
                        objeto, self.estadoguardar, self.obj("barraestado"),
                        "La Factura de Compra introducida ya ha sido registada.")

            elif objeto == self.obj("txt_02"):
                if Op.compara_fechas(self.nav.datos_conexion, "'" + self.fecha + "'", ">=", "NOW()"):
                    self.estadoguardar(False)
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "La Fecha de expedición de la Factura NO puede estar en el Futuro.")
                else:
                    self.obj("barraestado").push(0, "")

            elif objeto == self.obj("txt_orden"):
                self.obj("barraestado").push(0, "")

            elif objeto == self.obj("txt_03"):
                if Op.comprobar_numero(int, objeto, "Cód. de Proveedor", self.obj("barraestado")):
                    self.buscar_proveedores(objeto, "idPersona", valor, "Cód. de Proveedor")

            elif objeto == self.obj("txt_03_2"):
                self.buscar_proveedores(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDoc + "'", "Nro. de Documento")

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

            self.obj("txt_03").set_text(str(datos[0][0]))
            self.obj("txt_03_1").set_text(datos[0][1])
            self.obj("txt_03_2").set_text(datos[0][2])
            self.obj("txt_03_3").set_text(direc)
            self.obj("txt_03_4").set_text(telef)

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

            otro = self.obj("txt_03_2") if objeto == self.obj("txt_03") else self.obj("txt_03")
            otro.set_text("")

            self.obj("txt_03_1").set_text("")
            self.obj("txt_03_3").set_text("")
            self.obj("txt_03_4").set_text("")

    def guardar_encabezado(self, confirmado="0"):
        # Si el encabezado no ha sido registrado
        if not self.encabezado_guardado:
            fact = self.obj("txt_00").get_text()
            timb = self.obj("txt_01").get_text()
            prov = self.obj("txt_03").get_text()

            sql = timb + ", '" + fact + "', " + prov + ", " + \
                str(self.idTipoFact) + ", '" + self.fecha + "'"

            if not self.editando:
                Op.insertar(self.conexion, self.nav.tabla, sql)
            else:
                Op.modificar(self.conexion, self.nav.tabla,
                    self.cond_timb + ", '" + self.cond_fact + "', " + sql + ", " + confirmado)

            self.encabezado_guardado = self.editando = True
            self.cond_timb = timb
            self.cond_fact = fact

    def cargar_item_orden(self):
        self.guardar_encabezado()

        fact = self.obj("txt_00").get_text()
        timb = self.obj("txt_01").get_text()
        orden = self.obj("txt_orden").get_text()

        # Eliminando Items de la Orden anterior
        datos = self.obj("grilla").get_model()
        cant = len(datos)
        if cant > 0:  # Si existen ítems registrados en la Factura, los elimina
            for i in range(0, cant):
                Op.eliminar(self.nav.conexion, self.nav.tabla + "_detalles",
                timb + ", '" + fact + "', " + str(datos[i][0]))

        # Obteniendo Items desde Orden seleccionada
        cursor = Op.consultar(self.nav.conexion, "idItem, Cantidad, PrecioAcordado, Porcentaje",
        "ordencompras_detalles_s", " WHERE NroOrdenCompra = " + orden)
        datos = cursor.fetchall()
        cant = cursor.rowcount

        # Cargando Items desde Orden seleccionada
        for i in range(0, cant):
            Op.insertar(self.nav.conexion, self.nav.tabla + "_detalles",
            timb + ", '" + fact + "', " + str(datos[i][0]) + ", " +
            str(datos[i][1]) + ", " + str(datos[i][2]) + ", " + str(datos[i][3]))

        self.cargar_grilla_detalles()
        self.estadoguardar(True)

    def guardar_cerrar(self):
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def estadoguardar(self, estado):
        self.obj("hbox10").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)

        # Para elegir Items debe haber elegido el Proveedor
        items = True if estado and len(self.obj("txt_03").get_text()) > 0 else False
        self.obj("buttonbox_abm").set_sensitive(items)

        # Obligatoriamente debe poseer un detalle para poder Guardar
        guardar = True if estado and len(self.obj("grilla").get_model()) > 0 else False

        self.obj("btn_lotes").set_sensitive(guardar)
        self.obj("btn_cuentas").set_sensitive(guardar)
        self.obj("btn_confirmar").set_sensitive(guardar)
        self.obj("btn_guardar").set_sensitive(guardar)

##### Ítems ############################################################

    def config_grilla_detalles(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Cód.", celda0, 0, True, 50, 100)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Nombre", celda1, 1, True, 200, 400)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Cantidad", celda2, 2, True, 100, 150)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Precio Unitario", celda2, 3, True, 100, 150)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Porc. Desc.", celda2, 4, True, 100, 150)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Monto Desc.", celda2, 5, True, 100, 150)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Exentas", celda2, 6, True, 100, 150)
        col6.set_sort_column_id(6)
        col7 = Op.columnas("Gravadas 5%", celda2, 7, True, 100, 150)
        col7.set_sort_column_id(7)
        col8 = Op.columnas("Gravadas 10%", celda2, 8, True, 100, 150)
        col8.set_sort_column_id(8)

        lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(1)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, float, float, float, float, float, float, float, int)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_detalles(self):
        fact = self.obj("txt_00").get_text()
        timb = self.obj("txt_01").get_text()

        # Cargar campos de Totales y Liquidación del IVA
        cursor = Op.consultar(self.conexion, "TotalDescuento, SubTotalExenta, " +
            "SubTotalGravada5, SubTotalGravada10, Total, TotalLiquidacionIVA5, " +
            "TotalLiquidacionIVA10, TotalLiquidacionIVA", self.nav.tabla + "_s",
            " WHERE NroTimbrado = " + timb + " AND NroFactura = '" + fact + "'")
        datos = cursor.fetchall()

        self.obj("txt_descuento").set_text(str(datos[0][0]))
        self.obj("txt_exenta").set_text(str(datos[0][1]))
        self.obj("txt_iva5").set_text(str(datos[0][2]))
        self.obj("txt_iva10").set_text(str(datos[0][3]))
        self.obj("txt_total").set_text(str(datos[0][4]))
        self.obj("txt_liq_iva5").set_text(str(datos[0][5]))
        self.obj("txt_liq_iva10").set_text(str(datos[0][6]))
        self.obj("txt_total_liq_iva").set_text(str(datos[0][7]))

        # Cargar los Detalles de la Factura
        cursor = Op.consultar(self.conexion, "idDetalle, Nombre, Cantidad, " +
            "PrecioCompra, PorcDescuento, MontoDescuento, Exenta, Gravada5, " +
            "Gravada10, idItem", self.nav.tabla + "_detalles_s",
            " WHERE NroTimbrado = " + timb + " AND NroFactura = '" + fact + "'" +
            " ORDER BY idDetalle")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2],
                datos[i][3], datos[i][4], datos[i][5], datos[i][6],
                datos[i][7], datos[i][8], datos[i][9]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_clicked(self, objeto):
        self.guardar_encabezado()

        from compras.items import funcion_items
        funcion_items(False, self)

    def on_btn_modificar_clicked(self, objeto):
        self.guardar_encabezado()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Modificar.")
        else:
            from compras.items import funcion_items
            funcion_items(True, self)

    def on_btn_eliminar_clicked(self, objeto):
        self.guardar_encabezado()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            detalle = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Eliminar.")
        else:
            fact = self.obj("txt_00").get_text()
            timb = self.obj("txt_01").get_text()

            item = str(seleccion.get_value(iterador, 9))
            nomb = seleccion.get_value(iterador, 1)
            cant = str(seleccion.get_value(iterador, 2))
            precio = str(seleccion.get_value(iterador, 3))

            eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
                "\nCód. Ítem: " + item + "\nNombre: " + nomb +
                "\nCantidad: " + cant + "\nPrecio Unitario: " + precio)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                # Buscar datos del movimiento en tabla Inventario
                cursor = Op.consultar(self.conexion, "idMovimiento", self.nav.tabla + "_inventario_s",
                    " WHERE NroTimbrado = " + timb + " AND " + self.nav.campoid + " = '" + fact + "'" +
                    " AND idDetalle = " + detalle + " AND idItem = " + item)
                mov = str(cursor.fetchall()[0][0])

                # Eliminar datos en tabla que relaciona el movimiento con tabla Inventario
                Op.eliminar(self.conexion, self.nav.tabla + "_inventario",
                    timb + ", '" + fact + "', " + detalle + ", " + item + ", " + mov)

                # Eliminar datos del movimiento en tabla Inventario
                Op.eliminar(self.conexion, "inventario", item + ", " + mov)

                # Eliminar datos del movimiento en tabla Detalles
                Op.eliminar(self.conexion, self.nav.tabla + "_detalles",
                    timb + ", '" + fact + "', " + detalle)

                self.cargar_grilla_detalles()
                self.estadoguardar(True)

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_clicked(0)

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla").set_search_column(i)


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)
    celda2 = Op.celdas(1.0)

    col0 = Op.columnas("Nro. Timbrado", celda0, 0, True, 100, 200)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Nro. Factura", celda0, 1, True, 100, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Fecha de Compra", celda0, 2, True, 200)
    col2.set_sort_column_id(15)  # Para ordenarse usa la fila 15
    col3 = Op.columnas("RUC Proveedor", celda0, 3, True, 100, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Razón Social", celda1, 4, True, 200)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Dirección", celda1, 5, True, 300)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Teléfono", celda1, 6, True, 100, 200)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Cód. Tipo Factura", celda0, 7, True, 100, 200)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Tipo de Factura", celda1, 8, True, 150, 250)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Total a Pagar", celda2, 9, True, 150, 250)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Total Liquidación de IVA", celda2, 10, True, 150, 250)
    col10.set_sort_column_id(10)
    col11 = Op.columnas("Alias de Usuario", celda1, 11, True, 100, 200)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Nro. Documento", celda0, 12, True, 100, 200)
    col12.set_sort_column_id(12)
    col13 = Op.columnas("Nombre de Usuario", celda1, 13, True, 200, 300)
    col13.set_sort_column_id(13)
    col14 = Op.columna_active("Confirmado", 14)
    col14.set_sort_column_id(14)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col14)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 1)

    lista = ListStore(int, str, str, str, str, str, str, int, str,
        float, float, str, str, str, bool, str, int, str, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar == "Fecha":
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    if self.obj("rad_act").get_active() or self.obj("rad_ina").get_active():
        confirmado = "1" if self.obj("rad_act").get_active() else "0"
        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += "Confirmado = " + confirmado

    condicion = ""
    if len(self.condicion) > 0:
        condicion = " WHERE " + self.condicion if len(opcion) == 0 \
        else " AND " + self.condicion

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, "NroTimbrado, NroFactura, Fecha, " +
        "NroDocProveedor, RazonSocial, DireccionPrincipal, TelefonoPrincipal, " +
        "idTipoFactura, TipoFactura, Total, TotalLiquidacionIVA, " +
        "Alias, NroDocUsuario, NombreApellido, Confirmado, idProveedor, " +
        "idTipoDocProveedor, NroOrdenCompra, FechaHoraOrden",
        self.tabla + "_s", opcion + condicion + " ORDER BY Fecha DESC")
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        orden = "" if datos[i][17] is None else str(datos[i][17])
        fecha = "" if datos[i][18] is None else Cal.mysql_fecha(datos[i][18])

        lista.append([datos[i][0], datos[i][1], Cal.mysql_fecha(datos[i][2]),
            datos[i][3], datos[i][4], datos[i][5], datos[i][6], datos[i][7],
            datos[i][8], datos[i][9], datos[i][10], datos[i][11], datos[i][12],
            datos[i][13], datos[i][14], str(datos[i][2]), datos[i][15],
            datos[i][16], orden, fecha])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Nro. de Timbrado", "NroTimbrado"
    elif idcolumna == 1:
        col, self.campo_buscar = "Nro. de Factura", "NroFactura"
    elif idcolumna == 15:
        col, self.campo_buscar = "Fecha de Compra", "Fecha"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 3:
        col, self.campo_buscar = "RUC Proveedor", "NroDocProveedor"
    elif idcolumna == 4:
        col, self.campo_buscar = "Razón Social", "RazonSocial"
    elif idcolumna == 5:
        col, self.campo_buscar = "Dirección", "DireccionPrincipal"
    elif idcolumna == 6:
        col, self.campo_buscar = "Teléfono", "TelefonoPrincipal"
    elif idcolumna == 7:
        col, self.campo_buscar = "Cód. Tipo Factura", "idTipoFactura"
    elif idcolumna == 8:
        col, self.campo_buscar = "Tipo de Factura", "TipoFactura"
    elif idcolumna == 9:
        col, self.campo_buscar = "Total a Pagar", "Total"
    elif idcolumna == 10:
        col, self.campo_buscar = "Total Liquidación de IVA", "TotalLiquidacionIVA"
    elif idcolumna == 11:
        col, self.campo_buscar = "Alias de Usuario", "Alias"
    elif idcolumna == 12:
        col, self.campo_buscar = "Nro. Documento", "NroDocUsuario"
    elif idcolumna == 13:
        col, self.campo_buscar = "Nombre de Usuario", "NombreApellido"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = seleccion.get_value(iterador, 1)
    valor1 = str(seleccion.get_value(iterador, 0))
    valor2 = seleccion.get_value(iterador, 2)
    valor3 = seleccion.get_value(iterador, 4)
    valor4 = str(seleccion.get_value(iterador, 9))
    valor5 = str(seleccion.get_value(iterador, 10))
    valor6 = seleccion.get_value(iterador, 13)
    confirmado = seleccion.get_value(iterador, 14)

    mensaje = "Seleccionó:\n\nNro. de Factura: " + valor0 + "\nNro. de Timbrado: " + valor1 + \
        "\nFecha: " + valor2 + "\nProveedor: " + valor3 + "\nTotal a Pagar: " + valor4 + \
        "\nTotal Liq. del IVA: " + valor5 + "\nResponsable: " + valor6

    if confirmado != 1:
        eleccion = Mens.pregunta_borrar(mensaje)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        if eleccion:
            conexion = Op.conectar(self.datos_conexion)

            # Modificar Cantidades de Lotes afectados
            cursor = Op.consultar(conexion, "NroLote, idItem, Cantidad",
                self.tabla + "_lotes_s", " WHERE NroTimbrado = " + valor1 +
                " AND NroFactura = '" + valor0 + "' ORDER BY idItem")
            datos = cursor.fetchall()
            cant = cursor.rowcount

            self.obj("barraestado").push(0, "Se han encontrado " + str(cant) + " Lotes a Modificar.")

            for i in range(0, cant):
                cursor = Op.consultar(conexion, "Cantidad",
                    "lotes", " WHERE NroLote = '" + datos[i][0] + "'" +
                    " AND idItem = " + str(datos[i][1]))
                cant_lote = cursor.fetchall()[0][0] - datos[i][2]

                Op.modificar(conexion, "lotes_cantidad",
                    "'" + datos[i][0] + "', " + str(datos[i][1]) + ", " + str(cant_lote))

                self.obj("barraestado").push(0, "Modificando el Lote " +
                "Nº " + str(i + 1) + " de " + str(cant) + ".")

            # Eliminar Factura de Compra
            Op.eliminar(conexion, self.tabla, valor1 + ", '" + valor0 + "'")
            conexion.commit()

            conexion.close()  # Finaliza la conexión
            cargar_grilla(self)
    else:
        Mens.no_puede_modificar_eliminar_anular(2, mensaje +
        "\n\nEsta Factura de Compra ya ha sido Confirmada." +
        "\nSolo puede eliminar Facturas pendientes de confirmación.")


def listar_grilla(self):
    from clases import listado
    from reportlab.platypus import Paragraph as Par
    from reportlab.lib.pagesizes import A4

    datos = self.obj("grilla").get_model()
    cant = len(datos)

    head = listado.tabla_celda_titulo()
    body_ce = listado.tabla_celda_centrado()
    body_iz = listado.tabla_celda_just_izquierdo()

    lista = [[Par("Nro. de Factura", head), Par("Fecha de Elaboración", head),
    Par("Alias de Usuario", head), Par("Nombre", head)]]
    for i in range(0, cant):
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][2], body_ce),
        Par(datos[i][12], body_ce), Par(str(datos[i][13]), body_iz)])

    listado.listado(self.titulo, lista, [100, 125, 75, 150], A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        timb = seleccion.get_value(iterador, 1)
        fact = str(seleccion.get_value(iterador, 0))

        idper = seleccion.get_value(iterador, 16)
        tipodoc = seleccion.get_value(iterador, 17)
        ruc = seleccion.get_value(iterador, 3)
        nombre = seleccion.get_value(iterador, 4)
        direc = seleccion.get_value(iterador, 5)
        telef = seleccion.get_value(iterador, 6)

        direc = "" if valor5 is None else valor5
        telef = "" if valor6 is None else valor6

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

        # Datos de la Factura de Compra
        self.origen.nro_timb = timb
        self.origen.txt_nro_fact.set_text(fact)
        self.origen.txt_fec_fact.set_text(fact)

        self.on_btn_salir_clicked(0)
    except:
        pass
