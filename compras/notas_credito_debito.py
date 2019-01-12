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

        arch = Op.archivo("compra_notas_credito_debito")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(760, 600)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de " + self.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("btn_lotes").set_tooltip_text(
        "Presione este botón para registrar los Lotes de los Ítems seleccionados")
        self.obj("btn_confirmar").set_tooltip_text(
        "Presione este botón para Guardar el registro y/o Confirmarlo\n" +
        "Las " + self.nav.titulo + " confirmadas no podrán ser Modificadas o Eliminadas con posterioridad\n" +
        "Por lo tanto, compruebe que los datos están todos correctos")

        self.obj("txt_00").set_max_length(15)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_04").set_max_length(10)
        self.obj("txt_04_2").set_max_length(12)

        self.obj("txt_00").set_tooltip_text("Ingrese el Número de la Nota actual")
        self.obj("txt_01").set_tooltip_text("Ingrese el Número de Timbrado de la Nota actual")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("la Fecha de expedición de la Nota actual"))
        self.obj("txt_03").set_tooltip_text(Mens.usar_boton("la Factura modificada por la Nota actual"))
        self.obj("txt_03_1").set_tooltip_text("Fecha de Expedición de la Factura seleccionada")
        self.obj("txt_04").set_tooltip_text(Mens.usar_boton("al Proveedor de los ítems"))
        self.obj("txt_04_1").set_tooltip_text("Razón Social del Proveedor")
        self.obj("txt_04_2").set_tooltip_text("Ingrese el Nro. de Documento de Identidad del Proveedor")
        self.obj("txt_04_3").set_tooltip_text("Dirección principal del Proveedor")
        self.obj("txt_04_4").set_tooltip_text("Teléfono principal del Proveedor")
        self.obj("txt_00").grab_focus()

        self.nro_timb = -1
        self.txt_nro_fact, self.txt_fec_fact = self.obj("txt_03"), self.obj("txt_03_1")
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_04"), self.obj("txt_04_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_04_2"), self.obj("cmb_tipo_doc")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_04_3"), self.obj("txt_04_4")

        self.idTipoDoc = -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")

        self.estadoguardar(False)
        self.config_grilla_detalles()
        self.conexion = Op.conectar(self.nav.datos_conexion)

        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond_timb = str(seleccion.get_value(iterador, 0))
            self.cond_nro = seleccion.get_value(iterador, 1)

            self.fecha = seleccion.get_value(iterador, 18)
            fecha = seleccion.get_value(iterador, 2)

            self.nro_timb = seleccion.get_value(iterador, 3)
            fact = seleccion.get_value(iterador, 4)
            fecha_fact = seleccion.get_value(iterador, 17)

            idpro = str(seleccion.get_value(iterador, 15))
            tipodoc = seleccion.get_value(iterador, 16)
            nrodoc = seleccion.get_value(iterador, 5)
            nombre = seleccion.get_value(iterador, 6)
            direc = seleccion.get_value(iterador, 7)
            telef = seleccion.get_value(iterador, 8)

            resp = seleccion.get_value(iterador, 13)
            conf = seleccion.get_value(iterador, 14)

            direc = "" if direc is None else direc
            telef = "" if telef is None else telef

            self.obj("txt_00").set_text(self.cond_nro)
            self.obj("txt_01").set_text(self.cond_timb)
            self.obj("txt_02").set_text(fecha)
            self.obj("txt_03").set_text(fact)
            self.obj("txt_03_1").set_text(fecha_fact)
            self.obj("txt_04").set_text(idpro)
            self.obj("txt_04_1").set_text(nombre)
            self.obj("txt_04_2").set_text(ruc)
            self.obj("txt_04_3").set_text(direc)
            self.obj("txt_04_4").set_text(telef)

            # Asignación de Tipo de Documento en Combo
            model, i = self.obj("cmb_tipo_doc").get_model(), 0
            while model[i][0] != tipodoc: i += 1
            self.obj("cmb_tipo_doc").set_active(i)

            self.cargar_grilla_detalles()

            if conf != 1:
                self.estadoguardar(True)
                self.encabezado_guardado = True
            else:
                self.obj("vbox1").set_sensitive(False)
                self.obj("vbox2").set_sensitive(False)
                self.obj("buttonbox_abm").set_sensitive(False)
                self.obj("grilla").set_sensitive(False)
                self.obj("vbox3").set_sensitive(False)
                self.obj("hbox14").set_sensitive(False)

                Mens.no_puede_modificar_eliminar_anular(1,
                    "Seleccionó:\n\nNro. de Nota: " + self.cond_nro +
                    "\n\nNro. de Timbrado: " + self.cond_timb +
                    "\nFecha: " + fecha + "\nResponsable: " + resp +
                    "\n\nLa presente Nota ya ha sido Confirmada." +
                    "\nSolo puede modificar Notas pendientes de confirmación.")
        else:
            self.obj("cmb_tipo_doc").set_active(0)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_encabezado_notas()
        self.guardar_cerrar()

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def on_btn_confirmar_clicked(self, objeto):
        self.encabezado_guardado = False
        self.guardar_encabezado_notas("1")
        self.guardar_cerrar()

    def on_btn_lotes_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            item = str(seleccion.get_value(iterador, 0))
            cant = seleccion.get_value(iterador, 2)
        except:
            self.obj("barraestado").push(0, "Seleccione un Ítem de la lista. Luego presione Registrar Lotes.")
        else:
            self.guardar_encabezado_notas()
            nro = self.obj("txt_00").get_text()
            timb = self.obj("txt_01").get_text()

            buscar = "NroTimbrado = " + timb + " AND " + self.nav.campoid + " = '" + nro + "'"
            guardar = timb + ", '" + nro + "'"

            from lotes import lotes
            lotes(self.nav.datos_conexion, self.nav.tabla, cant, item, buscar, guardar)

    def on_btn_fecha_clicked(self, objeto):
        self.obj("txt_02").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_02").set_text(lista[0])
            self.fecha = lista[1]

    def on_btn_limpiar_fecha_clicked(self, objeto):
        self.obj("txt_02").set_text("")
        self.obj("txt_02").grab_focus()

    def on_btn_factura_clicked(self, objeto):
        condicion = None if len(self.obj("txt_04").get_text()) == 0 \
        else "idProveedor = " + self.obj("txt_04").get_text()

        from clases.llamadas import facturacompras
        facturacompras(self.nav.datos_conexion, self, condicion)

    def on_btn_proveedor_clicked(self, objeto):
        from clases.llamadas import personas
        personas(self.nav.datos_conexion, self, "idRolPersona = 3")

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0 or len(self.obj("txt_03").get_text()) == 0 \
        or len(self.obj("txt_04").get_text()) == 0 or len(self.obj("txt_04_2").get_text()) == 0 \
        or self.idTipoDoc == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_01"), "Nro. de Timbrado", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_04"), "Cód. de Proveedor", self.obj("barraestado")):
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
            self.focus_out_event(self.obj("txt_04_2"), 0)  # Nro. Documento
        else:
            self.obj("barraestado").push(0, "No existen registros de Tipos de Documentos en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_02"):
                    self.on_btn_fecha_clicked(0)
                elif objeto == self.obj("txt_03"):
                    self.on_btn_factura_clicked(0)
                elif objeto in (self.obj("txt_04"), self.obj("txt_04_2")):
                    self.on_btn_proveedor_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_02"):
            tipo = "a Fecha de Expedición"
        elif objeto == self.obj("txt_03"):
            tipo = "a Factura de Compra"
        elif objeto in (self.obj("txt_04"), self.obj("txt_04_2")):
            tipo = " Proveedor"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un" + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")

            if objeto == self.obj("txt_04"):  # Código de Proveedor
                self.obj("txt_04_1").set_text("")
                self.obj("txt_04_2").set_text("")
                self.obj("txt_04_3").set_text("")
                self.obj("txt_04_4").set_text("")

            elif objeto == self.obj("txt_04_2") \
            and len(self.obj("txt_04").get_text()) == 0:  # Nro. Documento de Proveedor
                self.obj("txt_04_1").set_text("")
                self.obj("txt_04_3").set_text("")
                self.obj("txt_04_4").set_text("")

        else:
            if objeto in (self.obj("txt_00"), self.obj("txt_01")):
                nro = self.obj("txt_00").get_text()
                timb = self.obj("txt_01").get_text()

                if len(timb) > 0 and len(nro) > 0 and Op.comprobar_numero(int,
                self.obj("txt_01"), "Nro. de Timbrado", self.obj("barraestado")):
                    # Al editar, comprueba que los valores son diferentes del original
                    busq = "" if not self.editando else " AND " + \
                    "(NroTimbrado <> " + timb + " OR " + self.nav.campoid + " <> '" + nro + "')"

                    Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                    self.nav.campoid, "'" + nro + "' AND NroTimbrado = " + timb + busq,
                    objeto, self.estadoguardar, self.obj("barraestado"),
                    "El Nro. de Nota y el Timbrado introducidos ya han sido registados.")

            elif objeto == self.obj("txt_02"):
                if Op.compara_fechas(self.nav.datos_conexion, "'" + self.fecha + "'", ">=", "NOW()"):
                    self.estadoguardar(False)
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "La Fecha de Expedición de la Nota NO puede estar en el Futuro.")
                else:
                    self.obj("barraestado").push(0, "")

            elif objeto == self.obj("txt_03"):
                self.obj("barraestado").push(0, "")

            elif objeto == self.obj("txt_04"):
                if Op.comprobar_numero(int, objeto, "Cód. de Proveedor", self.obj("barraestado")):
                    self.buscar_proveedores(objeto, "idPersona", valor, "Cód. de Proveedor")

            elif objeto == self.obj("txt_04_2"):
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

            self.obj("txt_04").set_text(str(datos[0][0]))
            self.obj("txt_04_1").set_text(datos[0][1])
            self.obj("txt_04_2").set_text(datos[0][2])
            self.obj("txt_04_3").set_text(direc)
            self.obj("txt_04_4").set_text(telef)

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

            otro = self.obj("txt_04_2") if objeto == self.obj("txt_04") else self.obj("txt_04")
            otro.set_text("")

            self.obj("txt_04_1").set_text("")
            self.obj("txt_04_3").set_text("")
            self.obj("txt_04_4").set_text("")

    def guardar_encabezado_notas(self, confirmado="0"):
        # Si el encabezado no ha sido registrado
        if not self.encabezado_guardado:
            nro = self.obj("txt_00").get_text()
            timb = self.obj("txt_01").get_text()
            fact = self.obj("txt_02").get_text()

            sql = timb + ", '" + nro + "', " + str(self.nro_timb) + ", " + \
                "'" + fact + "', '" + self.fecha + "'"

            if not self.editando:
                Op.insertar(self.conexion, self.nav.tabla, sql)
            else:
                Op.modificar(self.conexion, self.nav.tabla, self.cond_timb +
                    ", '" + self.cond_nro + "', " + sql + ", " + confirmado)

            self.cond_timb = timb  # Nuevo NroTimbrado original
            self.cond_nro = nro  # Nuevo NroNota original
            self.encabezado_guardado = self.editando = True

    def guardar_cerrar(self):
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def estadoguardar(self, estado):
        self.obj("buttonbox_abm").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)

        # Obligatoriamente debe poseer un detalle para poder Guardar
        guardar = True if estado and len(self.obj("grilla").get_model()) > 0 else False

        self.obj("btn_lotes").set_sensitive(guardar)
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
        col4 = Op.columnas("Exentas", celda2, 4, True, 100, 150)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Gravadas 5%", celda2, 5, True, 100, 150)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Gravadas 10%", celda2, 6, True, 100, 150)
        col6.set_sort_column_id(6)

        lista = [col0, col1, col2, col3, col4, col5, col6]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(1)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, float, float, float, float, float, int)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_detalles(self):
        nota = self.obj("txt_00").get_text()
        timb = self.obj("txt_01").get_text()

        # Cargar campos de Totales y Liquidación del IVA
        cursor = Op.consultar(self.conexion, "TotalDescuento, SubTotalExenta, " +
            "SubTotalGravada5, SubTotalGravada10, Total, TotalLiquidacionIVA5, " +
            "TotalLiquidacionIVA10, TotalLiquidacionIVA", self.nav.tabla + "_s",
            " WHERE NroTimbrado = " + timb + " AND " + self.nav.campoid + " = '" + nota + "'")
        datos = cursor.fetchall()

        self.obj("txt_descuento").set_text(str(datos[0][0]))
        self.obj("txt_exenta").set_text(str(datos[0][1]))
        self.obj("txt_iva5").set_text(str(datos[0][2]))
        self.obj("txt_iva10").set_text(str(datos[0][3]))
        self.obj("txt_total").set_text(str(datos[0][4]))
        self.obj("txt_liq_iva5").set_text(str(datos[0][5]))
        self.obj("txt_liq_iva10").set_text(str(datos[0][6]))
        self.obj("txt_total_liq_iva").set_text(str(datos[0][7]))

        # Cargar los Detalles de la Nota de Crédito
        cursor = Op.consultar(self.conexion, "idDetalle, Nombre, Cantidad, " +
            "PrecioCompra, Exenta, Gravada5, Gravada10, idItem",
            self.nav.tabla + "_detalles_s", " WHERE NroTimbrado = " + timb +
            " AND " + self.nav.campoid + " = '" + nota + "' ORDER BY idDetalle")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2],
            datos[i][3], datos[i][4], datos[i][5], datos[i][6], datos[i][7]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_clicked(self, objeto):
        self.guardar_encabezado_notas()

        from compras.items import funcion_items
        funcion_items(False, self)

    def on_btn_modificar_clicked(self, objeto):
        self.guardar_encabezado_notas()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Modificar.")
        else:
            from compras.items import funcion_items
            funcion_items(True, self)

    def on_btn_eliminar_clicked(self, objeto):
        self.guardar_encabezado_notas()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            detalle = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Eliminar.")
        else:
            nota = self.obj("txt_00").get_text()
            timb = self.obj("txt_01").get_text()

            item = str(seleccion.get_value(iterador, 9))
            nomb = seleccion.get_value(iterador, 1)
            cant = str(seleccion.get_value(iterador, 2))
            precio = str(seleccion.get_value(iterador, 3))

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Cód. Ítem: " + item + "\nNombre: " + nomb +
                "\nCantidad: " + cant + "\nPrecio Unitario: " + precio)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                #self.eliminar_factura_lote(item)

                Op.eliminar(self.conexion, self.nav.tabla + "_detalles",
                    timb + ", '" + nota + "', " + item)
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
    col1 = Op.columnas("Nro. Nota", celda0, 1, True, 100, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Fecha de Expedición", celda0, 2, True, 200)
    col2.set_sort_column_id(18)  # Para ordenarse usa la fila 18
    col3 = Op.columnas("Nro. Timbrado Fact.", celda0, 3, True, 100, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Nro. Factura", celda0, 4, True, 100, 200)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("RUC Proveedor", celda0, 5, True, 100, 200)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Razón Social", celda1, 6, True, 200)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Dirección", celda1, 7, True, 300)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Teléfono", celda1, 8, True, 100, 200)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Total", celda2, 9, True, 150, 250)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Total Liquidación de IVA", celda2, 10, True, 150, 250)
    col10.set_sort_column_id(10)
    col11 = Op.columnas("Alias de Usuario", celda1, 11, True, 100, 200)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Nro. Documento", celda0, 12, True, 100, 200)
    col12.set_sort_column_id(12)
    col13 = Op.columnas("Nombre de Usuario", celda1, 13, True, 200)
    col13.set_sort_column_id(13)
    col14 = Op.columna_active("Confirmado", 14)
    col14.set_sort_column_id(14)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8,
        col9, col10, col11, col12, col13]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col14)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 1)

    lista = ListStore(int, str, str, int, str, str, str, str, str,
        float, float, str, str, str, bool, int, str, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar == "Fecha":
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " = '" + self.fecha + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    if self.obj("rad_act").get_active() or self.obj("rad_ina").get_active():
        confirmado = "1" if self.obj("rad_act").get_active() else "0"
        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += "Confirmado = " + confirmado

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, "NroTimbrado, " + self.campoid + ", " +
        "Fecha, NroTimbradoFact, NroFactura, NroDocProveedor, RazonSocial, " +
        "DireccionPrincipal, TelefonoPrincipal, Total, TotalLiquidacionIVA, " +
        "Alias, NroDocUsuario, NombreApellido, Confirmado, idProveedor, " +
        "idTipoDocProveedor, FechaFact", self.tabla + "_s", opcion +
        " ORDER BY Fecha DESC")
    datos = cursor.fetchall()
    cant = cursor.rowcount

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], datos[i][1], Cal.mysql_fecha(datos[i][2]),
            datos[i][3], datos[i][4], datos[i][5], datos[i][6], datos[i][7],
            datos[i][8], datos[i][9], datos[i][10], datos[i][11], datos[i][12],
            datos[i][13], datos[i][14], datos[i][15], datos[i][16],
            Cal.mysql_fecha(datos[i][17]), str(datos[i][2])])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Nro. de Timbrado", "NroTimbrado"
    elif idcolumna == 1:
        col, self.campo_buscar = "Nro. de Nota", self.campoid
    elif idcolumna == 18:
        col, self.campo_buscar = "Fecha de Expedición", "Fecha"
        self.obj("txt_buscar").set_editable(False)
        self.obj("btn_buscar").set_visible(True)
    elif idcolumna == 3:
        col, self.campo_buscar = "Nro. de Timbrado de Factura", "NroTimbradoFact"
    elif idcolumna == 4:
        col, self.campo_buscar = "Nro. de Factura", "NroFactura"
    elif idcolumna == 5:
        col, self.campo_buscar = "RUC Proveedor", "NroDocProveedor"
    elif idcolumna == 6:
        col, self.campo_buscar = "Razón Social", "RazonSocial"
    elif idcolumna == 7:
        col, self.campo_buscar = "Dirección", "DireccionPrincipal"
    elif idcolumna == 8:
        col, self.campo_buscar = "Teléfono", "TelefonoPrincipal"
    elif idcolumna == 9:
        col = self.campo_buscar = "Total"
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
    valor3 = seleccion.get_value(iterador, 6)
    valor4 = str(seleccion.get_value(iterador, 9))
    valor5 = str(seleccion.get_value(iterador, 10))
    valor6 = seleccion.get_value(iterador, 13)
    confirmado = seleccion.get_value(iterador, 14)

    mensaje = "Seleccionó:\n\nNro. de Nota: " + valor0 + \
        "\nNro. de Timbrado: " + valor1 + "\nFecha: " + valor2 + \
        "\nProveedor: " + valor3 + "\nTotal: " + valor4 + \
        "\nTotal Liq. del IVA: " + valor5 + "\nResponsable: " + valor6

    if confirmado != 1:
        eleccion = Mens.pregunta_borrar(mensaje)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        if eleccion:
            conexion = Op.conectar(self.datos_conexion)
            Op.eliminar(conexion, self.tabla, valor1 + ", '" + valor0 + "'")
            conexion.commit()
            conexion.close()  # Finaliza la conexión
            cargar_grilla(self)
    else:
        Mens.no_puede_modificar_eliminar_anular(2, mensaje +
            "\n\nLa Nota seleccionada ya ha sido Confirmada." +
            "\nSolo puede eliminar Notas pendientes de confirmación.")


def listar_grilla(self):
    from clases import listado
    from reportlab.platypus import Paragraph as Par
    from reportlab.lib.pagesizes import A4

    datos = self.obj("grilla").get_model()
    cant = len(datos)

    head = listado.tabla_celda_titulo()
    body_ce = listado.tabla_celda_centrado()
    body_iz = listado.tabla_celda_just_izquierdo()

    lista = [[Par("Nro. de Nota", head), Par("Fecha de Expedición", head),
    Par("Alias de Usuario", head), Par("Nombre", head)]]
    for i in range(0, cant):
        lista.append([Par(datos[i][1], body_ce), Par(datos[i][2], body_iz),
        Par(datos[i][12], body_ce), Par(datos[i][13], body_iz)])

    listado.listado(self.titulo, lista, [100, 125, 75, 150], A4)


def seleccion(self):
    pass
