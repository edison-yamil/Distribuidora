#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class lotes:

    def __init__(self, con, datos_con, tab, cant, item, buscar, guardar, sumar=None):
        self.conexion = con
        self.datos_conexion = datos_con
        self.tabla = tab
        self.maximo = self.disponible = cant
        self.cond_buscar = buscar
        self.cond_guardar = guardar
        self.idItem = item
        self.sumar = sumar

        cursor = self.conexion.cursor()
        cursor.execute("SAVEPOINT lotes")
        cursor.close()

        arch = Op.archivo("lotes")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(675, 600)
        self.obj("ventana").set_modal(True)

        self.obj("ventana").set_title("Lotes de Ítems")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_00_1").set_max_length(40)
        self.obj("txt_01").set_max_length(20)
        self.obj("txt_03").set_max_length(12)

        self.obj("txt_00").set_tooltip_text("Código de Ítem")
        self.obj("txt_00_1").set_tooltip_text("Código de Barras del Ítem")
        self.obj("txt_00_2").set_tooltip_text("Descripción del Ítem")
        self.obj("txt_00_3").set_tooltip_text("Cód. de Presentación del Ítem")
        self.obj("txt_00_4").set_tooltip_text("Presentación del Ítem")
        self.obj("txt_00_5").set_tooltip_text("Cód. de Categoría del Ítem")
        self.obj("txt_00_6").set_tooltip_text("Categoría del Ítem")
        self.obj("txt_00_7").set_tooltip_text("Porcentaje de IVA gravado al Ítem")

        mensaje = "" if self.tabla != "facturacompras" else " o Ingrese el Número de un NUEVO Lote"
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Nro. de Lote del Ítem" + mensaje))
        self.obj("txt_03").set_tooltip_text("Ingrese la Cantidad de Ítems")

        self.txt_cod_it, self.txt_bar_it, self.txt_nom_it = self.obj("txt_00"), \
            self.obj("txt_00_1"), self.obj("txt_00_2")
        self.txt_cod_pres, self.txt_des_pres = self.obj("txt_00_3"), self.obj("txt_00_4")
        self.txt_cod_cat, self.txt_des_cat, self.txt_por_imp = self.obj("txt_00_5"), \
            self.obj("txt_00_6"), self.obj("txt_00_7")

        self.fecha_venc = None
        self.txt_lote_nro, self.txt_lote_fch = self.obj("txt_01"), self.obj("txt_02")

        self.config_grilla_lotes()
        arch.connect_signals(self)

        self.obj("btn_item").set_visible(False)  # NO puede cambiar de ítem
        self.obj("txt_00").set_text(self.idItem)
        self.focus_out_event(self.obj("txt_00"), 0)  # Carga datos y grilla

        self.estadoedicion(False)
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_cancelar_clicked(self, objeto):
        cursor = self.conexion.cursor()
        cursor.execute("ROLLBACK TO SAVEPOINT lotes")
        cursor.close()

        self.obj("ventana").destroy()

    def on_btn_item_clicked(self, objeto):
        from clases.llamadas import items
        items(self.datos_conexion, self)

    def on_item_changed(self, objeto):
        if self.obj("btn_item").get_visible():
            if len(self.obj("txt_00").get_text()) == 0:
                estado = False
            else:
                if Op.comprobar_numero(int, objeto, "Cód. de Ítem", self.obj("barraestado")):
                    estado = True
                    self.cargar_grilla_lotes()
                else:
                    estado = False
            self.estadoguardar(estado)

    def key_press_event(self, objeto, evento):
        if self.obj("btn_item").get_visible():
            if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
                if evento.keyval == 65293:  # Presionando Enter
                    self.on_btn_item_clicked(0)
            elif evento.keyval == 65293:
                self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if self.obj("btn_item").get_visible():
            self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un Ítem.")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_00"):  # Código del Ítem
                self.obj("txt_00_1").set_text("")
                self.limpiar_items()
            elif objeto == self.obj("txt_00_1") and len(self.obj("txt_00").get_text()) == 0:
                self.obj("txt_00").set_text("")
                self.limpiar_items()
        else:
            if objeto == self.obj("txt_00"):
                if Op.comprobar_numero(int, objeto, "Cód. de Ítem", self.obj("barraestado")):
                    self.cargar_items(objeto, "idItem", valor, "Cód. de Ítem")

            elif objeto == self.obj("txt_00_1"):
                self.cargar_items(objeto, "CodigoBarras", "'" + valor + "'", "Código de Barras")

    def cargar_items(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "idItem, CodigoBarras, Nombre, " +
            "idPresentacion, Presentacion, idCategoria, Categoria, Porcentaje",
            "items_s", " WHERE " + campo + " = " + valor)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            self.obj("txt_00").set_text(str(datos[0][0]))
            codbar = "" if datos[0][1] is None else datos[0][1]

            self.obj("txt_00_1").set_text(codbar)
            self.obj("txt_00_2").set_text(datos[0][2])
            self.obj("txt_00_3").set_text(str(datos[0][3]))
            self.obj("txt_00_4").set_text(datos[0][4])
            self.obj("txt_00_5").set_text(str(datos[0][5]))
            self.obj("txt_00_6").set_text(datos[0][6])
            self.obj("txt_00_7").set_text(str(datos[0][7]))

            self.cargar_grilla_lotes()
            self.estadoguardar(True)
        else:
            objeto.grab_focus()
            self.estadoguardar(False)
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_00_1") if objeto == self.obj("txt_00") else self.obj("txt_00")
            self.limpiar_items()
            otro.set_text("")

    def limpiar_items(self):
        self.obj("txt_00_2").set_text("")
        self.obj("txt_00_3").set_text("")
        self.obj("txt_00_4").set_text("")
        self.obj("txt_00_5").set_text("")
        self.obj("txt_00_6").set_text("")
        self.obj("txt_00_7").set_text("")

    def estadoguardar(self, estado):
        self.obj("hbuttonbox1").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)
        self.obj("btn_guardar").set_sensitive(estado)

    def estadoedicion(self, estado):
        self.estadoguardar(not estado)
        self.obj("btn_cancelar").set_sensitive(not estado)

        self.obj("vbox3").set_visible(estado)
        self.obj("hbuttonbox2").set_visible(estado)

##### Lotes ############################################################

    def config_grilla_lotes(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Nro. de Lote", celda0, 0, True, 100, 100)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Fecha de Vencimiento", celda1, 1, True, 450)
        col1.set_sort_column_id(3)  # Para ordenarse usa la fila 3
        col2 = Op.columnas("Cantidad", celda2, 2, True, 100, 125)
        col2.set_sort_column_id(2)

        self.obj("grilla").append_column(col0)
        self.obj("grilla").append_column(col1)
        self.obj("grilla").append_column(col2)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(0)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(str, str, float, str, int)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_lotes(self):
        self.disponible = self.maximo

        cursor = Op.consultar(self.conexion, "NroLote, FechaVencimiento, " +
            "CantidadInv, idMovimiento, idDeposito, Observaciones",
            self.tabla + "_inventario_s", " WHERE " + self.cond_buscar +
            " AND idItem = " + self.idItem + " ORDER BY FechaVencimiento DESC")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            if datos[i][0] is None:
                fecha = ""  # Si Lote es NULL, la cantidad está disponible
            else:
                fecha = Cal.mysql_fecha(datos[i][1])
                self.disponible -= datos[i][2]  # Resta Cantidad a Máximo

            lista.append([datos[i][0], fecha, datos[i][2],
                str(datos[i][1]), datos[i][3]])

        self.dep = "NULL" if datos[0][4] is None else str(datos[0][4])
        self.obs = "NULL" if datos[0][5] is None else "'" + datos[0][5] + "'"

        self.obj("txt_total").set_text(str(self.maximo))
        self.obj("txt_disponible").set_text(str(self.disponible))

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_lote_clicked(self, objeto):
        if self.disponible > 0 or self.tabla == "lotes":
            self.editando = False
            self.funcion_lotes()
        else:
            self.obj("barraestado").push(0, "No quedan Ítems para " +
            "asignar a otro Lote (" + str(self.disponible) + ").")

    def on_btn_modificar_lote_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            lote = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Modificar.")
        else:
            if lote is not None:
                self.editando = True
                self.funcion_lotes()

    def on_btn_eliminar_lote_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            lote = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Eliminar.")
        else:
            if lote is not None:
                fecha = seleccion.get_value(iterador, 1)
                cant = seleccion.get_value(iterador, 2)
                mov_del = str(seleccion.get_value(iterador, 4))

                eleccion = Mens.pregunta_borrar("Seleccionó:\n\nNro. de Lote: " + lote +
                    "\nFecha de Vencimiento: " + fecha + "\nCantidad: " + str(cant))

                self.obj("grilla").get_selection().unselect_all()
                self.obj("barraestado").push(0, "")

                if eleccion:
                    # Buscar en Inventario registro con NroLote = NULL (no el que se borra)
                    cursor = Op.consultar(self.conexion, "idMovimiento, CantidadInv",
                        self.tabla + "_inventario_s", " WHERE " + self.cond_buscar +
                        " AND idItem = " + self.idItem + " AND NroLote IS NULL")
                    datos = cursor.fetchall()
                    filas = cursor.rowcount

                    if filas > 0:
                        idmov = str(datos[0][0])
                        cant_lote = datos[0][1]

                        if self.tabla in ("facturacompras", "notadebitocompras", "notacreditoventas"):
                            cant_lote += cant  # Suma Cantidad
                        elif self.tabla in ("notacreditocompras", "facturaventas", "notadebitoventas"):
                            cant_lote -= cant  # Resta Cantidad

                        # Sumar o Restar en Inventario a registro con NroLote = NULL
                        Op.modificar(self.conexion, "inventario",
                            self.idItem + ", " + self.idItem + ", " + idmov +
                            ", " + self.dep + ", NULL, " + str(cant_lote) + ", " + self.obs)

                        Op.eliminar(self.conexion, self.tabla + "_inventario",
                            self.cond_guardar + ", " + self.idItem + ", " + mov_del)
                        Op.eliminar(self.conexion, "inventario", self.idItem + ", " + mov_del)

                    else:  # Si no hay, Modificar en Inventario el registro con NroLote = NULL
                        Op.modificar(self.conexion, "inventario",
                            self.idItem + ", " + self.idItem + ", " + mov_del +
                            ", " + self.dep + ", NULL, " + str(cant) + ", " + self.obs)

                    if self.tabla == "facturacompras":
                        # Si el Lote no está relacionado a ningún movimiento, Eliminar de lotes
                        cursor = Op.consultar(self.conexion, "NroLote",
                            self.tabla + "_inventario_s", " WHERE " +
                            "NroLote = '" + lote + "' AND idItem = " + self.idItem)
                        datos = cursor.fetchall()
                        filas = cursor.rowcount

                        if filas == 0:
                            Op.eliminar(self.conexion, "lotes", "'" + lote + "', " + self.idItem)

                    self.cargar_grilla_lotes()

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_lote_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_lote_clicked(0)

##### Agregar-Modificar Lotes ##########################################

    def funcion_lotes(self):
        estado = True if self.tabla == "facturacompras" else False
        self.estadofechas(estado)

        if self.editando:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.cond_lote = seleccion.get_value(iterador, 0)
            fecha = seleccion.get_value(iterador, 1)
            self.cant = seleccion.get_value(iterador, 2)

            self.fecha_venc = seleccion.get_value(iterador, 3)
            self.idmov = str(seleccion.get_value(iterador, 4))

            self.obj("txt_01").set_text(self.cond_lote)
            self.obj("txt_02").set_text(fecha)
            self.obj("txt_03").set_text(str(self.cant))

            # Maximo permitido más cantidad original
            self.disponible += self.cant
        else:
            self.obj("txt_01").set_text("")
            self.obj("txt_02").set_text("")
            self.obj("txt_03").set_text(str(self.disponible))

        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        self.obj("txt_01").grab_focus()
        self.obj("btn_guardar_lote").set_sensitive(False)
        self.estadoedicion(True)

    def on_btn_guardar_lote_clicked(self, objeto):
        lote = self.obj("txt_01").get_text()
        cant = self.obj("txt_03").get_text()

        if self.disponible >= float(cant):
            if self.tabla == "facturacompras":  # Registro de Lotes
                sql = "'" + lote + "', " + self.idItem + ", '" + self.fecha_venc + "'"

                if not self.editando_lote:
                    Op.insertar(self.conexion, "lotes", sql)
                else:
                    Op.modificar(self.conexion, "lotes", "'" + self.cond_lote + "', " + sql)

            # Buscar datos del registro con NroLote = NULL
            cursor = Op.consultar(self.conexion, "idMovimiento, CantidadInv",
                self.tabla + "_inventario_s", " WHERE " + self.cond_buscar +
                " AND idItem = " + self.idItem + " AND NroLote IS NULL")
            datos = cursor.fetchall()
            filas = cursor.rowcount

            if not self.editando:
                idmov = str(datos[0][0])
                cant_null = datos[0][1]

                # Sumar o Restar en Inventario a registro con NroLote = NULL
                if self.tabla in ("facturacompras", "notadebitocompras", "notacreditoventas"):
                    cant_null -= float(cant)  # Resta Cantidad
                elif self.tabla in ("notacreditocompras", "facturaventas", "notadebitoventas"):
                    cant_null += float(cant)  # Suma Cantidad

                if self.disponible == float(cant):
                    # Agrega lote al registro con NroLote = NULL
                    Op.modificar(self.conexion, "inventario",
                        self.idItem + ", " + self.idItem + ", " + idmov + ", " +
                        self.dep + ", " + lote + ", " + cant + ", " + self.obs)
                else:
                    # Restar o Sumar cantidad al registro con NroLote = NULL
                    Op.modificar(self.conexion, "inventario",
                        self.idItem + ", " + self.idItem + ", " + idmov + ", " +
                        self.dep + ", NULL, " + str(cant_null) + ", " + self.obs)

                    # Insertar registro con nueva cantidad
                    mov = Op.nuevoid(self.conexion, "inventario" +
                        " WHERE idItem = " + self.idItem, "idMovimiento")

                    Op.insertar(self.conexion, "inventario", self.idItem + ", " + mov + ", " +
                        self.dep + ", " + lote + ", " + cant + ", " + self.obs)
                    Op.insertar(self.conexion, self.tabla + "_inventario",
                        self.cond_guardar + ", " + self.idItem + ", " + mov)
            else:
                # Agrega la nueva cantidad al registro que está editando
                Op.modificar(self.conexion, "inventario", self.idItem + ", " +
                    self.idItem + ", " + self.idmov + ", " + self.dep + ", " +
                    lote + ", " + cant + ", " + self.obs)

                if self.disponible == float(cant):
                    if filas > 0:
                        # Ya no quedan disponibles, entonces borrar registro con NroLote = NULL
                        Op.eliminar(self.conexion, self.tabla + "_inventario",
                            self.cond_guardar + ", " + self.idItem + ", " + str(datos[0][0]))
                        Op.eliminar(self.conexion, "inventario", self.idItem + ", " +
                            str(datos[0][0]))
                    else:
                        pass  # No hay registro con NroLote = NULL
                else:
                    if filas > 0:  # Modificar registro con NroLote = NULL
                        idmov = str(datos[0][0])
                        cant_null = datos[0][1]
                        cant = self.disponible - cant_null - float(cant)

                        Op.modificar(self.conexion, "inventario", self.idItem + ", " +
                            self.idItem + ", " + idmov + ", " + self.dep + ", " +
                            lote + ", " + str(cant) + ", " + self.obs)

                    else:  # Insertar registro con NroLote = NULL
                        mov = Op.nuevoid(self.conexion, "inventario" +
                            " WHERE idItem = " + self.idItem, "idMovimiento")
                        cant = self.disponible - float(cant)

                        Op.insertar(self.conexion, "inventario", self.idItem + ", " + mov + ", " +
                            self.dep + ", NULL, " + str(cant) + ", " + self.obs)
                        Op.insertar(self.conexion, self.tabla + "_inventario",
                            self.cond_guardar + ", " + self.idItem + ", " + mov)

            self.cargar_grilla_lotes()
            self.estadoedicion(False)
        else:
            self.obj("barraestado").push(0, "La Cantidad de Ítems " +
            "NO puede ser superior a " + str(self.disponible) + ".")

    def on_btn_cancelar_lote_clicked(self, objeto):
        if self.editando:  # Maximo permitido menos cantidad original
            self.disponible -= self.cant  # No fue modificado el registro
        self.estadoedicion(False)

    def on_btn_lote_clicked(self, objeto):
        self.obj("txt_01").grab_focus()
        lotes_buscar(self)

    def on_btn_fecha_venc_clicked(self, objeto):
        self.obj("txt_02").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_02").set_text(lista[0])
            self.fecha_venc = lista[1]

    def on_btn_limpiar_fecha_venc_clicked(self, objeto):
        self.obj("txt_02").grab_focus()
        self.obj("txt_02").set_text("")

    def verificacion_lote(self, objeto):
        if len(self.obj("txt_01").get_text()) == 0 or len(self.obj("txt_02").get_text()) == 0 \
        or len(self.obj("txt_03").get_text()) == 0:
            estado = False
        else:
            estado = Op.comprobar_numero(float, self.obj("txt_03"),
                "Cantidad de Ítems", self.obj("barraestado"))
        self.obj("btn_guardar_lote").set_sensitive(estado)

    def on_lote_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_01") and self.obj("btn_lote").get_visible():
                    self.on_btn_lote_clicked(0)
                elif objeto == self.obj("txt_02") and self.obj("btn_fecha_venc").get_visible():
                    self.on_btn_fecha_venc_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.on_lote_focus_out_event(objeto, 0)

    def on_lote_focus_in_event(self, objeto, evento):
        mens = "Presione CTRL + Enter para Buscar un"
        if objeto == self.obj("txt_01") and self.obj("btn_lote").get_visible():
            mens += " Nro. de Lote para el presente Ítem."
        elif objeto == self.obj("txt_02") and self.obj("btn_fecha_venc").get_visible():
            mens += "a Fecha de Vencimiento para el Lote seleccionado."
        else:
            mens = ""
        self.obj("barraestado").push(0, mens)

    def on_lote_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
        else:
            if objeto == self.obj("txt_01"):
                cursor = Op.consultar(self.conexion, "FechaVencimiento", "lotes",
                    " WHERE idItem = " + self.idItem + " AND NroLote = '" + valor + "'")
                datos = cursor.fetchall()
                cant = cursor.rowcount

                if cant > 0:
                    if self.tabla == "facturacompras":
                        self.editando_lote = True
                        self.cond_lote = valor

                    self.fecha_venc = str(datos[0][0])
                    fecha = Cal.mysql_fecha(datos[0][0])
                    self.obj("txt_02").set_text(fecha)

                    busq = "" if not self.editando else " AND NroLote <> '" + self.cond_lote + "'"
                    # Comprueba si el Nro. de Lote introducido ya ha sido registado
                    Op.comprobar_unique(self.conexion, self.tabla + "_inventario_s",
                        "NroLote", "'" + valor + "' AND " + self.cond_buscar +
                        " AND idItem = " + self.idItem + busq, objeto,
                        self.obj("btn_guardar_lote"), self.obj("barraestado"),
                        "El Nro. de Lote introducido ya ha sido registado (VEA LA TABLA).")
                else:
                    if self.tabla == "facturacompras":
                        self.editando_lote = False if not self.editando else True
                    else:
                        self.obj("txt_01").grab_focus()
                        self.obj("barraestado").push(0, "El Nro. de Lote NO es válido.")
                        self.obj("btn_guardar_lote").set_sensitive(False)

            elif objeto == self.obj("txt_02"):
                self.obj("barraestado").push(0, "")

            elif objeto == self.obj("txt_03"):
                Op.comprobar_numero(float, objeto, "Cantidad de Ítems", self.obj("barraestado"))

    def estadofechas(self, estado):
        if estado:  # Puede buscar una fecha de Vencimiento
            self.obj("txt_02").set_tooltip_text(Mens.usar_boton("una Fecha de Vencimiento del Lote"))
        else:
            self.obj("txt_02").set_tooltip_text("Fecha de Vencimiento del Lote")

        self.obj("txt_02").set_property('can_focus', estado)
        self.obj("btn_fecha_venc").set_visible(estado)
        self.obj("btn_limpiar_fecha_venc").set_visible(estado)


class lotes_buscar:

    def __init__(self, v_or, item):
        self.origen = v_or
        self.idItem = item

        arch = Op.archivo("buscador")
        self.obj = arch.get_object

        self.obj("ventana").set_title("Seleccione un Lote")
        self.obj("ventana").set_default_size(510, 500)
        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        self.config_grilla_buscar()
        self.cargar_grilla_buscar()

        arch.connect_signals(self)
        self.obj("ventana").show()

    def on_btn_busq_seleccionar_clicked(self, objeto):
        seleccion, iterador = self.obj("grilla_buscar").get_selection().get_selected()
        lote = seleccion.get_value(iterador, 0)
        fecha = seleccion.get_value(iterador, 1)
        fecha_sql = seleccion.get_value(iterador, 3)

        self.origen.txt_lote_nro.set_text(lote)
        self.origen.txt_lote_fch.set_text(fecha)

        try:
            self.origen.fecha_venc = fecha_sql
        except:
            pass

        self.obj("ventana").destroy()

    def on_btn_busq_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_filtrar_clicked(self, objeto):
        self.cargar_grilla_buscar(self)

    def on_btn_buscar_clicked(self, objeto):
        if self.campo_buscar == "FechaVencimiento":
            lista = calendario()

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

        col0 = Op.columnas("Nro. de Lote", celda0, 0, True, 100, 100)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Fecha de Vencimiento", celda1, 1, True, 300, 400)
        col1.set_sort_column_id(3)  # Para ordenarse usa la fila 3
        col2 = Op.columnas("Cantidad", celda2, 2, True, 100, 125)
        col2.set_sort_column_id(2)

        lista = [col0, col1, col2]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla_buscar").append_column(columna)

        self.obj("grilla_buscar").set_rules_hint(True)
        self.obj("grilla_buscar").set_search_column(1)
        self.obj("grilla_buscar").set_property('enable-grid-lines', 3)

        self.obj("txt_buscar").set_editable(True)
        self.obj("hbox_fecha").set_visible(False)
        self.columna_buscar(0)

        lista = ListStore(str, str, float, str)
        self.obj("grilla_buscar").set_model(lista)
        self.obj("grilla_buscar").show()

    def cargar_grilla_buscar(self):
        buscar = self.obj("txt_buscar").get_text()

        if self.campo_buscar == "FechaVencimiento":
            opcion = "" if len(buscar) == 0 else \
            " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
        else:
            opcion = "" if len(buscar) == 0 else \
            " AND " + self.campo_buscar + " LIKE '%" + buscar + "%'"

        conexion = Op.conectar(self.origen.datos_conexion)
        cursor = Op.consultar(conexion, "NroLote, FechaVencimiento, " +
            "Cantidad", "lotes", " WHERE idItem = " + self.idItem +
            opcion + " ORDER BY FechaVencimiento DESC")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        lista = self.obj("grilla_buscar").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], Cal.mysql_fecha(datos[i][1]),
                datos[i][2], str(datos[i][1])])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def columna_buscar(self, idcolumna):
        if idcolumna == 0:
            col, self.campo_buscar = "Nro. de Lote", "NroLote"
        elif idcolumna == 3:
            col, self.campo_buscar = "Fecha de Vencimiento", "FechaVencimiento"
            self.obj("txt_buscar").set_editable(False)
            self.obj("hbox_fecha").set_visible(True)
        elif idcolumna == 2:
            col, self.campo_buscar = "Cantidad de Ítems", "Cantidad"

        self.obj("label_buscar").set_text("Filtrar por " + col + ":")
