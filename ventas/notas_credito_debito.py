#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date
from decimal import Decimal
from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class notas_credito_debito:

    def __init__(self, datos, tit, tab, est, cja, num):
        self.datos_conexion = datos
        self.titulo = tit
        self.tabla = tab
        self.estab = est
        self.caja = cja
        self.numero = num

        arch = Op.archivo("venta_notas_credito_debito")
        self.obj = arch.get_object

        self.obj("ventana").set_default_size(800, 670)
        self.obj("ventana").set_position(1)
        self.obj("ventana").set_title("Notas de " + self.titulo + " por Ventas")
        self.obj("ventana").set_modal(True)
        self.obj("ventana").maximize()

        self.obj("labeltitulo").set_text("Notas de " + self.titulo + " por Ventas")
        '''self.obj("btn_nuevo").set_tooltip_text("Presione este botón para Crear una nueva Nota")
        self.obj("btn_anular").set_tooltip_text("Presione este botón para Anular una Nota")
        self.obj("btn_confirmar").set_tooltip_text("Presione este botón para Guardar la Nota actual")
        self.obj("btn_cancelar").set_tooltip_text("Presione este botón para Cancelar la Nota actual sin guardar los datos")
        self.obj("btn_salir").set_tooltip_text("Presione este botón para Cerrar esta ventana")

        self.obj("cmb_tipo_doc").set_tooltip_text("Seleccione el Tipo de Documento de Identidad del Cliente")

        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("la Factura que modifica esta Nota de Débito"))
        self.obj("txt_02_1").set_tooltip_text("Número de Timbrado de la Factura seleccionada")
        self.obj("txt_02_2").set_tooltip_text("Fecha de Expedición de la Factura seleccionada")
        self.obj("txt_03_1").set_tooltip_text("Ingrese el Número de Documento de Identidad del Cliente")
        self.obj("txt_03_2").set_tooltip_text("Nombre y Apellido o Razón Social del Cliente")
        self.obj("txt_03_3").set_tooltip_text("Dirección de la residencia del Cliente")
        self.obj("btn_cliente").set_tooltip_text("Presione este botón para buscar datos de un Cliente")

        self.obj("btn_nuevo_item").set_tooltip_text("Presione este botón para agregar un nuevo Ítem")
        self.obj("btn_modificar_item").set_tooltip_text("Presione este botón para modificar datos de un Ítem")
        self.obj("btn_eliminar_item").set_tooltip_text("Presione este botón para eliminar un Ítem")

        self.fact_nro = self.obj("txt_02")
        self.fact_timb, self.fact_fecha = self.obj("txt_02_1"), self.obj("txt_02_2")

        self.cod_per = self.idTipoDoc = -1
        self.tip_doc, self.nro_doc = self.obj("cmb_tipo_doc"), self.obj("txt_03_1")
        self.rzn_scl, self.dir_per = self.obj("txt_03_2"), self.obj("txt_03_3")

        self.cod_it, self.bar_it, self.nom_it = self.obj("txt_it_00"), self.obj("txt_it_00_1"), self.obj("txt_it_00_2")
        self.cod_pres, self.des_pres = self.obj("txt_it_00_3"), self.obj("txt_it_00_4")
        self.cod_cat, self.des_cat, self.por_cat = self.obj("txt_it_00_5"), self.obj("txt_it_00_6"), self.obj("txt_it_00_7")
        self.cost_it, self.vent_it = self.obj("txt_it_02_1"), self.obj("txt_it_02")'''

        Op.combos_config(self.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")
        #arch.connect_signals(self)

        self.permisos_user()
        self.estadoitems(False)
        self.estadoedicion(False)
        self.config_grilla_detalles()
        self.limpiarcampos()

        self.obj("ventana").show()
        self.buscar_nro_timbrado()

    def on_btn_nuevo_clicked(self, objeto):
        self.buscar_nro_nota_debito()
        self.encabezado_guardado = False
        self.editando = False
        self.estadoedicion(True)

        self.obj("cmb_tipo_doc").set_active(0)
        self.obj("txt_03_1").grab_focus()

    def on_btn_anular_clicked(self, objeto):
        self.funcion_anulacion()

    def on_btn_confirmar_clicked(self, objeto):
        self.conexion.commit()
        self.estadoedicion(False)
        self.limpiarcampos()

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.estadoedicion(False)
        self.limpiarcampos()

    def on_btn_salir_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_cliente_clicked(self, objeto):
        import navegador
        navegador.navegador(self.conexion, "personas", "idPersona", 3, "Personas (Buscar)", self)

    def on_btn_factura_clicked(self, objeto):
        nota = self.obj("txt_00_3").get_text()
        timb = self.obj("txt_01_1").get_text()
        datos = self.obj("grilla").get_model()
        cant = len(datos)

        eleccion = True if cant == 0 else Mens.pregunta_generico("¿Está seguro?",
        "Elegir una NUEVA FACTURA eliminará todos los registros actuales.")

        if eleccion:
            for i in range(0, cant):
                item = datos[i][0]
                self.eliminar_nota_lote(item)
                Op.eliminar(self.conexion, self.tabla + "_detalles",
                timb + ", " + nota + ", " + item)

            import venta_facturas
            venta_facturas.factura_buscar(self.conexion, self)

            if cant > 0:
                self.obj("barraestado").push(0, "Los Ítems de la Nota de Débito han sido Eliminados.")
                self.cargar_grilla_detalles()

    def on_btn_nuevo_item_clicked(self, objeto):
        self.editando_item = False
        self.funcion_items()

    def on_btn_modificar_item_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Modificar.")
        else:
            self.editando_item = True
            self.funcion_items()

    def on_btn_eliminar_item_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            item = str(seleccion.get_value(iterador, 0))
            nomb = seleccion.get_value(iterador, 1)
            cant = str(seleccion.get_value(iterador, 2))
            precio = str(seleccion.get_value(iterador, 3))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Eliminar.")
        else:
            nota = self.obj("txt_00_3").get_text()
            timb = self.obj("txt_01_1").get_text()

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
            "Cód. Ítem: " + item + "\nNombre: " + nomb +
            "\nCantidad: " + cant + " unidades\nPrecio Unitario: " + precio)
            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                self.eliminar_nota_lote(item)

                Op.eliminar(self.conexion, self.tabla + "_detalles",
                timb + ", " + nota + ", " + item)
                self.cargar_grilla_detalles()
                self.estadoguardar(True)

    def verificacion(self, objeto):
        if len(self.obj("txt_02").get_text()) == 0 or len(self.obj("txt_02_1").get_text()) == 0 \
        or len(self.obj("txt_03_1").get_text()) == 0 or self.cod_per < 0:
            estado = False
        else:
            self.encabezado_guardado = False
            estado = True
        self.estadoguardar(estado)

    def on_cmb_tipo_doc_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            self.idTipoDoc = model[active][0]
            self.on_cliente_focus_out_event(0, 0)
        else:
            self.obj("barraestado").push(0, "No existen registros " +
            "de Tipos de Documentos de Identidad en el Sistema.")

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_item_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_item_clicked(0)

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla").set_search_column(i)

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_02"):
                    self.on_btn_factura_clicked(0)
                elif objeto == self.obj("txt_03_1"):
                    self.on_btn_cliente_clicked(0)
        elif evento.keyval == 65293:
            if objeto == self.obj("txt_02"):
                self.on_factura_focus_out_event(objeto, 0)
            elif objeto == self.obj("txt_03_1"):
                self.on_cliente_focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_02"):
            tipo = "la Factura que modifica esta Nota de Débito"
        elif objeto == self.obj("txt_03_1"):
            tipo = "un Cliente"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar " + tipo + ".")

    def on_factura_focus_out_event(self, objeto, evento):
        if len(self.obj("txt_02").get_text()) == 0 or len(self.obj("txt_02_1").get_text()) == 0:
            self.obj("barraestado").push(0, "")
        else:
            fact = self.obj("txt_02").get_text()
            timb = self.obj("txt_02_1").get_text()

            cursor = Op.consultar(self.conexion, "FechaHora, idCliente, " +
            "idTipoDocCliente, NroDocCliente, RazonSocial, DireccionPrincipal", "facturaventas_s",
            " WHERE NroTimbrado = " + timb + " AND NroFactura = " + fact)

            if cursor.rowcount > 0:
                datos = cursor.fetchall()
                self.obj("txt_02_2").set_text(Cal.mysql_fecha_hora(datos[0][0]))

                # Asignación de Tipo de Documento en Combo
                model, i = self.obj("cmb_tipo_doc").get_model(), 0
                while model[i][0] != datos[0][2]: i += 1
                self.obj("cmb_tipo_doc").set_active(i)

                # Cliente de la Factura seleccionada
                self.cod_per = datos[0][1]
                self.obj("txt_03_1").set_text(datos[0][3])
                self.obj("txt_03_2").set_text(datos[0][4])
                direc = "" if datos[0][5] is None else datos[0][5]
                self.obj("txt_03_3").set_text(direc)

                self.obj("barraestado").push(0, "")
                self.verificacion(0)
            else:
                self.estadoguardar(False)
                self.obj("txt_02").grab_focus()
                self.obj("barraestado").push(0, "El Nro. Factura introducido no es válido (NO EXISTE).")
                self.obj("txt_02_2").set_text("")

    def on_cliente_focus_out_event(self, objeto, evento):
        valor = self.obj("txt_03_1").get_text()
        if len(valor) == 0:
            self.obj("txt_03_2").set_text("")
            self.obj("txt_03_3").set_text("")
            self.obj("barraestado").push(0, "")
        else:
            cursor = Op.consultar(self.conexion,
            "idPersona, RazonSocial, DireccionPrincipal", "personas_s",
            " WHERE idTipoDocumento = '" + self.idTipoDoc + "'" +
            " AND NroDocumento = '" + valor + "'")
            if cursor.rowcount > 0:
                datos = cursor.fetchall()
                self.cod_per = datos[0][0]

                self.obj("txt_03_2").set_text(datos[0][1])
                direc = "" if datos[0][2] is None else datos[0][2]
                self.obj("txt_03_3").set_text(direc)

                self.obj("barraestado").push(0, "")
                self.verificacion(0)
            else:
                self.estadoguardar(False)
                self.obj("txt_03_1").grab_focus()
                self.obj("barraestado").push(0, "El Nro. Documento del Cliente no es válido.")
                self.obj("txt_03_2").set_text("")
                self.obj("txt_03_3").set_text("")
                self.cod_per = -1

    def config_grilla_detalles(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Cód. Ítem", celda0, 0, True, 90, 90)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Descripción", celda1, 1, True, 270)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Cantidad", celda2, 2, True, 100, 150)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Precio Unitario", celda2, 3, True, 135, 135)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Exentas", celda2, 4, True, 135, 135)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Gravadas 5%", celda2, 5, True, 135, 135)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Gravadas 10%", celda2, 6, True, 135, 135)
        col6.set_sort_column_id(6)

        lista = [col0, col1, col2, col3, col4, col5, col6]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(1)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, float, float, float, float, float)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_detalles(self):
        # Cargar campos de Totales y Liquidación del IVA
        cursor = Op.consultar(self.conexion, "SubTotalExenta, SubTotalGravada5, " +
        "SubTotalGravada10, Total, TotalLiquidacionIVA5, TotalLiquidacionIVA10", self.tabla + "_s",
        " WHERE NroTimbrado = " + self.obj("txt_01_1").get_text() +
        " AND NroNotaDebito = " + self.obj("txt_00_3").get_text())
        datos = cursor.fetchall()

        self.obj("txt_exenta").set_text(str(datos[0][0]))
        self.obj("txt_iva5").set_text(str(datos[0][1]))
        self.obj("txt_iva10").set_text(str(datos[0][2]))
        self.obj("txt_total").set_text(str(datos[0][3]))
        self.obj("txt_liq_iva5").set_text(str(datos[0][4]))
        self.obj("txt_liq_iva10").set_text(str(datos[0][5]))

        # Cargar los Detalles de la Nota de Débito
        cursor = Op.consultar(self.conexion, "idItem, Nombre, Cantidad, " +
        "PrecioVenta, Exenta, Gravada5, Gravada10", self.tabla + "_detalles_s",
        " WHERE NroTimbrado = " + self.obj("txt_01_1").get_text() +
        " AND NroNotaDebito = " + self.obj("txt_00_3").get_text() + " ORDER BY idItem")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2],
            datos[i][3], datos[i][4], datos[i][5], datos[i][6]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def permisos_user(self):
        self.btn_nuevo = self.btn_anular = False

        conexion = Op.conectar(self.datos_conexion)
        cursor = conexion.cursor()
        cursor.execute("SELECT ROUTINE_NAME FROM procedimientos_s")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        for i in range(0, cant):
            procedimiento = datos[i][0]

            if procedimiento == self.tabla + "_i":
                self.btn_nuevo = True
            elif procedimiento == self.tabla + "_a":
                self.btn_anular = True

        self.obj("btn_nuevo").set_sensitive(self.btn_nuevo)
        self.obj("btn_anular").set_sensitive(self.btn_anular)

    def buscar_nro_timbrado(self):
        cursor = Op.consultar(self.conexion, "NroTimbrado, FechaVencimiento", "timbrados_s",
        " WHERE NroEstablecimiento = " + self.estab + " AND NroCaja = " + self.caja +
        " AND FechaVencimiento > NOW() AND idTipoDocumento = 3 AND Anulado <> 1 ORDER BY NroTimbrado")
        datos = cursor.fetchall()

        if cursor.rowcount > 0:
            # Datos del Timbrado
            self.obj("txt_01_1").set_text(str(datos[0][0]))
            self.obj("txt_01_2").set_text(Cal.mysql_fecha(datos[0][1]))
            # Datos del Punto de Expedición
            self.obj("txt_00_1").set_text(Op.cadenanumeros(self.estab, 3))
            self.obj("txt_00_2").set_text(Op.cadenanumeros(self.caja, 3))
        else:
            Mens.error_generico("¡ERROR!", "No se ha encontrado un Timbrado\npara este Punto de Expedición." +
            "\nConsulte al Administrador del Sistema.\n\nLa ventana de Nota de Débitos se cerrará.")
            self.obj("ventana").destroy()

    def buscar_nro_nota_debito(self):
        timb = self.obj("txt_01_1").get_text()

        cursor = Op.consultar(self.conexion, "NumeroInicio, NumeroFin",
        "timbrados_s", " WHERE NroTimbrado = " + timb + " AND " +
        "idTipoDocumento = 3 AND FechaVencimiento > NOW() AND Anulado <> 1")
        datos = cursor.fetchall()

        ini, fin = datos[0][0], datos[0][1]
        num_nota = Op.nuevoid(self.conexion, self.tabla + "_s WHERE NroTimbrado = " + timb, "NroNotaDebito")

        if int(num_nota) >= ini and int(num_nota) <= fin:
            self.obj("txt_00_3").set_text(Op.cadenanumeros(num_nota, 7))
        elif int(num_nota) < ini:
            self.obj("txt_00_3").set_text(Op.cadenanumeros(str(ini), 7))
        elif int(num_nota) > fin:
            Mens.error_generico("¡ERROR!", "El nuevo Número de Nota de Débito es mayor " +
            "al último número\npara el Timbrado asignado a este Punto de Expedición." +
            "\n\nHable con el Administrador par resolver el problema.")
            self.estadoedicion(False)
            self.limpiarcampos()

    def guardar_encabezado(self):
        # Si el encabezado no ha sido registrado
        if not self.encabezado_guardado:
            nota_nro = self.obj("txt_00_3").get_text()
            nota_timb = self.obj("txt_01_1").get_text()

            fact_nro = self.obj("txt_02").get_text()
            fact_timb = self.obj("txt_02_1").get_text()

            sql = nota_timb + ", " + nota_nro + ", " + fact_timb + ", " + fact_nro + \
            ", " + self.numero + ", " + self.estab + ", " + self.caja

            if not self.editando:
                Op.insertar(self.conexion, self.tabla, sql)
            else:
                Op.modificar(self.conexion, self.tabla,
                self.cond_timb + ", " + self.cond_nota + ", " + sql)

            self.encabezado_guardado = True
            self.editando = True
            self.cond_timb = nota_timb
            self.cond_nota = nota_nro

    def eliminar_nota_lote(self, item):
        nota = self.obj("txt_00_3").get_text()
        timb = self.obj("txt_01_1").get_text()

        # Seleccionar Lotes del item seleccionado
        cursor = Op.consultar(self.conexion, "NroLote, Cantidad",
        self.tabla + "_lotes_s", " WHERE NroTimbrado = " + timb +
        " AND NroNotaDebito = " + nota + " AND idItem = " + item)
        datos = cursor.fetchall()
        cant = cursor.rowcount

        self.obj("barraestado").push(0, "Se han encontrado " + str(cant) + " Lotes a Modificar.")

        for i in range(0, cant):
            cursor = Op.consultar(self.conexion, "Cantidad", "lotes",
            " WHERE NroLote = '" + datos[i][0] + "' AND idItem = " + item)
            cant_lote = cursor.fetchall()[0][0] - datos[i][1]

            Op.modificar(self.conexion, "lotes_cantidad",
            "'" + datos[i][0] + "', " + item + ", " + str(cant_lote))

            self.obj("barraestado").push(0, "Modificando el Lote Nº " + str(i + 1) + " de " + str(cant) + ".")

            # Eliminar Nota de Debito con Lotes
            Op.eliminar(self.conexion, self.tabla + "_lotes",
            timb + ", " + nota + ", '" + datos[i][0] + "', " + item)

    def limpiarcampos(self):
        self.obj("grilla").get_model().clear()
        self.obj("txt_00_4").set_text("19 de Marzo de 2015")
        #self.obj("txt_00_4").set_text(Cal.mysql_fecha(date.today()))

        self.obj("txt_00_1").set_text("001")
        self.obj("txt_00_2").set_text("001")
        self.obj("txt_00_3").set_text("")
        self.obj("txt_01_1").set_text("1000001")
        self.obj("txt_01_2").set_text("02 de Marzo de 2016")

        self.obj("txt_exenta").set_text("")
        self.obj("txt_iva5").set_text("")
        self.obj("txt_iva10").set_text("")
        self.obj("txt_total").set_text("")
        self.obj("txt_liq_iva5").set_text("")
        self.obj("txt_liq_iva10").set_text("")

        self.obj("cmb_tipo_doc").set_active(-1)
        self.obj("barraestado").push(0, "")

    def estadoedicion(self, estado):
        if self.btn_nuevo:
            self.obj("btn_nuevo").set_sensitive(not estado)
        if self.btn_anular:
            self.obj("btn_anular").set_sensitive(not estado)

        self.obj("btn_cancelar").set_sensitive(estado)
        self.obj("btn_salir").set_sensitive(not estado)

        self.estadoencabezado(estado)
        self.estadoguardar(False)

    def estadoencabezado(self, estado):
        self.obj("hbox1").set_sensitive(estado)
        self.obj("hbox4").set_sensitive(estado)

        self.obj("hbox7").set_sensitive(estado)
        self.obj("hbox10").set_sensitive(estado)
        self.obj("hbox11").set_sensitive(estado)

    def estadoguardar(self, estado):
        self.obj("hbuttonbox1").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)

        # Obligatoriamente debe poseer un detalle para poder Guardar
        guardar = True if estado and len(self.obj("grilla").get_model()) > 0 else False
        self.obj("btn_confirmar").set_sensitive(guardar)

##### Ventana de Inserción y Modificación de Ítems #####################

    def estadoitems(self, estado):
        self.obj("vbox1").set_visible(estado)
        self.obj("hbuttonbox2").set_visible(estado)
        self.obj("btn_cancelar").set_sensitive(not estado)

    def funcion_items(self):
        edit = "Agregar" if not self.editando_item else "Editar"
        self.obj("ventana").set_title(edit + " Registro de Ítem en la Nota de Débito")

        if self.editando_item:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.cond_item = str(seleccion.get_value(iterador, 0))
            cant = str(seleccion.get_value(iterador, 2))

            self.obj("txt_it_00").set_text(self.cond_item)
            self.obj("txt_it_01").set_text(cant)
            self.on_item_focus_out_event(self.obj("txt_it_00"), 0)

        self.obj("btn_guardar_item").set_sensitive(False)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        self.estadoencabezado(False)
        self.estadoguardar(False)
        self.estadoitems(True)

    def on_btn_guardar_item_clicked(self, objeto):
        self.guardar_encabezado()

        nota = self.obj("txt_00_3").get_text()
        timb = self.obj("txt_01_1").get_text()

        item = self.obj("txt_it_00").get_text()
        cant = self.obj("txt_it_01").get_text()
        costo = self.obj("txt_it_02_1").get_text()
        venta = self.obj("txt_it_02").get_text()
        iva = self.obj("txt_it_00_7").get_text()

        sql = timb + ", " + nota + ", " + item + ", " + \
        cant + ", " + costo + ", " + venta + ", " + iva

        if not self.editando_item:
            Op.insertar(self.conexion, self.tabla + "_detalles", sql)
        else:
            Op.modificar(self.conexion, self.tabla + "_detalles", self.cond_item + ", " + sql)

        self.cargar_grilla_detalles()
        self.on_btn_cancelar_item_clicked(0)

    def on_btn_cancelar_item_clicked(self, objeto):
        self.obj("txt_it_00").set_text("")
        self.obj("txt_it_00_1").set_text("")
        self.obj("txt_it_01").set_text("")
        self.obj("txt_it_02").set_text("")
        self.limpiar_items()

        self.obj("ventana").set_title("Notas de Débito por Ventas")
        self.estadoencabezado(True)
        self.estadoguardar(True)
        self.estadoitems(False)

    def on_btn_item_clicked(self, objeto):
        import navegador
        navegador.navegador(self.conexion, "items", "idItem", 3, "Ítems (Buscar)", self)

    def verificacion_item(self, objeto):
        if len(self.obj("txt_it_00").get_text()) == 0 or len(self.obj("txt_it_01").get_text()) == 0 \
        or len(self.obj("txt_it_02").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_it_00"), "Cód. de Ítem", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_it_01"), "Cantidad de Ítems", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar_item").set_sensitive(estado)

    def on_item_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_item_clicked(0)

    def on_item_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un ítem.")

    def on_item_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_it_00"):  # Código del Ítem
                self.obj("txt_it_00_1").set_text("")
                self.limpiar_items()
            elif objeto == self.obj("txt_it_00_1") and len(self.obj("txt_it_00").get_text()) == 0:
                self.obj("txt_it_00").set_text("")
                self.limpiar_items()
        else:
            if objeto == self.obj("txt_it_00"):
                if Op.comprobar_numero(int, objeto, "Cód. de Ítem", self.obj("barraestado")):
                    self.buscar_items(objeto, "idItem", valor, "Cód. de Ítem")

            elif objeto == self.obj("txt_it_00_1"):
                self.buscar_items(objeto, "CodigoBarras", "'" + valor + "'", "Código de Barras")

            elif objeto == self.obj("txt_it_01"):
                Op.comprobar_numero(float, objeto, "Cantidad de Ítems", self.obj("barraestado"))

    def buscar_items(self, objeto, campo, valor, nombre):
        cursor = Op.consultar(self.conexion, "idItem, CodigoBarras, Nombre, " +
        "idPresentacion, Presentacion, idCategoria, Categoria, Porcentaje, " +
        "PrecioVenta, PrecioCosto", "items_s", " WHERE " + campo + " = " + valor)

        if cursor.rowcount > 0:
            datos = cursor.fetchall()
            self.obj("txt_it_00").set_text(str(datos[0][0]))
            codbar = "" if datos[0][1] is None else datos[0][1]
            self.obj("txt_it_00_1").set_text(codbar)
            self.obj("txt_it_00_2").set_text(datos[0][2])
            self.obj("txt_it_00_3").set_text(str(datos[0][3]))
            self.obj("txt_it_00_4").set_text(datos[0][4])
            self.obj("txt_it_00_5").set_text(str(datos[0][5]))
            self.obj("txt_it_00_6").set_text(datos[0][6])
            self.obj("txt_it_00_7").set_text(str(datos[0][7]))

            self.obj("txt_it_02").set_text(str(datos[0][8]))
            self.obj("txt_it_02_1").set_text(str(datos[0][9]))

            # Cuando crea nuevo registro o, al editar, valor es diferente del original
            if not self.editando_item or str(datos[0][0]) != self.cond_item:
                self.guardar_encabezado()

                Op.comprobar_unique(self.conexion, self.tabla + "_detalles_s", "idItem",
                str(datos[0][0]) + " AND NroTimbrado = " + self.obj("txt_01_1").get_text() +
                " AND NroNotaDebito = " + self.obj("txt_00_3").get_text(),
                self.obj("txt_it_00"), self.obj("btn_guardar_item"), self.obj("barraestado"),
                "El Ítem introducido ya ha sido registrado en esta Nota de Débito.")
        else:
            objeto.grab_focus()
            self.obj("btn_guardar_item").set_sensitive(False)
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_it_00_1") if objeto == self.obj("txt_it_00") else self.obj("txt_it_00")
            self.limpiar_items()
            otro.set_text("")

    def limpiar_items(self):
        self.obj("txt_it_00_2").set_text("")
        self.obj("txt_it_00_3").set_text("")
        self.obj("txt_it_00_4").set_text("")
        self.obj("txt_it_00_5").set_text("")
        self.obj("txt_it_00_6").set_text("")
        self.obj("txt_it_00_7").set_text("")
        self.obj("txt_it_02").set_text("")
        self.obj("txt_it_02_1").set_text("")

##### Ventana de Anulación de Notas de Débito por Ventas ##############

    def funcion_anulacion(self):
        nota_debitos_anular(self.conexion)


class nota_debitos_anular:

    def __init__(self, con):
        self.conexion = con

        arch = Op.archivo("buscador")
        self.obj = arch.get_object

        self.obj("ventana").set_title("Seleccione una Nota de Débito")
        self.obj("ventana").set_default_size(950, 500)
        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        # Transforma boton Seleccionar en boton Anular
        self.obj("img_busq_seleccionar").set_property('stock', 'gtk-find-and-replace')
        self.obj("label_busq_seleccionar").set_text("Anular")
        self.obj("label_busq_cancelar").set_text("Salir")

        self.config_grilla_buscar()
        self.cargar_grilla_buscar()

        arch.connect_signals(self)
        self.obj("ventana").show()

    def on_btn_busq_seleccionar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla_buscar").get_selection().get_selected()
            timb = str(seleccion.get_value(iterador, 0))
            nota = str(seleccion.get_value(iterador, 1))
            fecha = seleccion.get_value(iterador, 2)
            cliente = seleccion.get_value(iterador, 7)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Anular.")
        else:
            # Anular Nota de Debito seleccionada
            eleccion = Mens.pregunta_anular("Seleccionó:\n\n" +
            "Nro. Timbrado: " + timb + "\nNro. Nota de Débito: " +  nota +
            "\nCliente: " + cliente + "\nFecha de Expedición: " + fecha)
            self.obj("grilla_buscar").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.anular(self.conexion, "notadebitoventas", timb + ", " + nota)
                self.conexion.commit()
                self.cargar_grilla_buscar()

    def on_btn_busq_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_buscar_clicked(self, objeto):
        if self.campo_buscar == "FechaHora":
            lista = Cal.calendario()

            if lista is not False:
                self.fecha = lista[1]
                self.obj("txt_buscar").set_text(lista[0])
                self.cargar_grilla_buscar()

    def on_grilla_buscar_row_activated(self, objeto, fila, col):
        self.on_btn_busq_seleccionar_clicked(0)

    def on_txt_buscar_key_press_event(self, objeto, evento):
        if evento.keyval == 65293:  # Presionando Enter
            self.cargar_grilla_buscar()

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla_buscar").set_search_column(i)

        self.obj("txt_buscar").set_editable(True)
        self.obj("btn_buscar").set_visible(False)
        self.columna_buscar(i)

    def config_grilla_buscar(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Nro. Timbrado", celda0, 0, True, 100, 150)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Nro. Nota de Débito", celda0, 1, True, 100, 150)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Fecha de Expedición", celda0, 2, True, 225, 250)
        col2.set_sort_column_id(15)
        col3 = Op.columnas("Nro. Timbrado", celda0, 3, True, 100, 150)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Nro. Factura", celda0, 4, True, 100, 150)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Tipo Doc. Cliente", celda0, 5, True, 100, 200)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Nro. Doc. Cliente", celda0, 6, True, 100, 200)
        col6.set_sort_column_id(6)
        col7 = Op.columnas("Razón Social", celda1, 7, True, 200, 300)
        col7.set_sort_column_id(7)
        col8 = Op.columnas("Dirección Principal", celda1, 8, True, 200, 500)
        col8.set_sort_column_id(8)
        col9 = Op.columnas("Total", celda2, 9, True, 150, 250)
        col9.set_sort_column_id(9)
        col10 = Op.columnas("Total Liq. IVA", celda2, 10, True, 150, 250)
        col10.set_sort_column_id(10)
        col11 = Op.columnas("Alias de Usuario", celda1, 11, True, 100, 200)
        col11.set_sort_column_id(11)
        col12 = Op.columnas("Nro. Documento", celda0, 12, True, 100, 200)
        col12.set_sort_column_id(12)
        col13 = Op.columnas("Nombre de Usuario", celda1, 13, True, 200, 300)
        col13.set_sort_column_id(13)
        col14 = Op.columna_active("Anulado", 14)
        col14.set_sort_column_id(14)

        lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla_buscar").append_column(columna)
        self.obj("grilla_buscar").append_column(col14)

        self.obj("grilla_buscar").set_rules_hint(True)
        self.obj("grilla_buscar").set_search_column(1)
        self.obj("grilla_buscar").set_property('enable-grid-lines', 3)
        self.columna_buscar(1)

        lista = ListStore(int, int, str, int, int, str, str, str, str,
        float, float, str, str, str, int, str, int)
        self.obj("grilla_buscar").set_model(lista)
        self.obj("grilla_buscar").show()

    def cargar_grilla_buscar(self):
        if self.campo_buscar == "FechaHora":
            opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
            " WHERE " + self.campo_buscar + " = '" + self.fecha + "%'"
        else:
            opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
            " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += "Anulado <> 1"

        cursor = Op.consultar(self.conexion, "NroTimbrado, NroNotaDebito, " +
        "FechaHora, NroTimbradoFact, NroFactura, idTipoDocCliente, NroDocCliente, " +
        "RazonSocial, DireccionPrincipal, Total, TotalLiquidacionIVA, " +
        "Alias, NroDocUsuario, NombreApellido, Anulado, idCliente",
        "notadebitoventas_s", opcion + " ORDER BY FechaHora DESC")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla_buscar").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], Cal.mysql_fecha_hora(datos[i][2]),
            datos[i][3], datos[i][4], datos[i][5], datos[i][6], datos[i][7], datos[i][8],
            datos[i][9], datos[i][10], datos[i][11], datos[i][12], datos[i][13], datos[i][14],
            datos[i][2], datos[i][15]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def columna_buscar(self, idcolumna):
        if idcolumna == 0:
            col, self.campo_buscar = "Nro. Timbrado", "NroTimbrado"
        elif idcolumna == 1:
            col, self.campo_buscar = "Nro. Nota de Débito", "NroNotaDebito"
        elif idcolumna == 15:
            col, self.campo_buscar = "Fecha de Expedición", "FechaHora"
            self.obj("txt_buscar").set_editable(False)
            self.obj("btn_buscar").set_visible(True)
        elif idcolumna == 3:
            col, self.campo_buscar = "Nro. Timbrado", "NroTimbradoFact"
        elif idcolumna == 4:
            col, self.campo_buscar = "Nro. Factura", "NroFactura"
        elif idcolumna == 5:
            col, self.campo_buscar = "Tipo Doc. Cliente", "idTipoDocCliente"
        elif idcolumna == 6:
            col, self.campo_buscar = "Nro. Documento (Cliente)", "NroDocCliente"
        elif idcolumna == 7:
            col, self.campo_buscar = "Razón Social", "RazonSocial"
        elif idcolumna == 8:
            col, self.campo_buscar = "Dirección Principal", "DireccionPrincipal"
        elif idcolumna == 9:
            col, self.campo_buscar = "Total", "Total"
        elif idcolumna == 10:
            col, self.campo_buscar = "Total Liq. IVA", "TotalLiquidacionIVA"
        elif idcolumna == 11:
            col, self.campo_buscar = "Alias de Usuario", "Alias"
        elif idcolumna == 12:
            col, self.campo_buscar = "Nro. Documento (Usuario)", "NroDocUsuario"
        elif idcolumna == 13:
            col, self.campo_buscar = "Nombre de Usuario", "NombreApellido"

        self.obj("label_buscar").set_text("Filtrar por " + col + ":")

