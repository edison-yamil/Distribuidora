#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from decimal import Decimal
from gi.repository.Gdk import ModifierType
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_items:

    def __init__(self, edit, origen):
        self.editando = self.editando_inventario = edit
        self.origen = origen

        arch = Op.archivo("compra_items")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Ítems en la " + self.origen.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))
        self.obj("btn_lotes").set_tooltip_text(
        "Presione este botón para registrar los Lotes del Ítem seleccionado")

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_02").set_max_length(10)
        self.obj("txt_02_1").set_max_length(40)
        self.obj("txt_03").set_max_length(14)
        self.obj("txt_04").set_max_length(14)
        self.obj("txt_05_1").set_max_length(14)
        self.obj("txt_07").set_max_length(100)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código del Detalle")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Depósito en que es almacenado el ítem"))
        self.obj("txt_01_1").set_tooltip_text("Descripción del Depósito")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("Código de Ítem"))
        self.obj("txt_02_1").set_tooltip_text("Ingrese el Código de Barras del Ítem")
        self.obj("txt_02_2").set_tooltip_text("Descripción del Ítem")
        self.obj("txt_02_3").set_tooltip_text("Cód. de Presentación del Ítem")
        self.obj("txt_02_4").set_tooltip_text("Presentación del Ítem")
        self.obj("txt_02_5").set_tooltip_text("Cód. de Categoría del Ítem")
        self.obj("txt_02_6").set_tooltip_text("Categoría del Ítem")
        self.obj("txt_02_7").set_tooltip_text("Porcentaje de IVA gravado al Ítem")
        self.obj("txt_03").set_tooltip_text("Ingrese la Cantidad de Ítems adquiridos")
        self.obj("txt_04").set_tooltip_text("Ingrese el Precio Unitario del Ítem")
        self.obj("txt_05").set_tooltip_text("Ingrese el Porcentaje de Descuento")
        self.obj("txt_05_1").set_tooltip_text("Monto Total Descontado")
        self.obj("txt_06").set_tooltip_text("Monto Total con Descuento")
        self.obj("txt_07").set_tooltip_text("Ingrese una Observación sobre esta operación")
        self.obj("txt_02").grab_focus()

        self.txt_cod_dep, self.txt_des_dep = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_cod_it, self.txt_bar_it, self.txt_nom_it = self.obj("txt_02"), \
            self.obj("txt_02_1"), self.obj("txt_02_2")
        self.txt_cod_pres, self.txt_des_pres = self.obj("txt_02_3"), self.obj("txt_02_4")
        self.txt_cod_cat, self.txt_des_cat, self.txt_por_imp = self.obj("txt_02_5"), \
            self.obj("txt_02_6"), self.obj("txt_02_7")
        #self.cost_it, self.precio_costo_nota = self.obj("txt_02_8"), self.obj("txt_02_9")
        arch.connect_signals(self)

        self.avisado = False  # Se avisó que no ha sido posible guardar la modificación

        estado = False if self.origen.nav.tabla != "facturacompras" else True
        self.obj("txt_04").set_property('can_focus', estado)  # Precio Unitario
        self.obj("txt_04").set_property('editable', estado)

        # Códigos de Timbrado y Nro. de Documento
        nro = self.origen.obj("txt_00").get_text()
        timb = self.origen.obj("txt_01").get_text()

        if self.editando:
            seleccion, iterador = self.origen.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            self.cond_item = str(seleccion.get_value(iterador, 9))
            cant = str(seleccion.get_value(iterador, 2))
            precio = str(seleccion.get_value(iterador, 3))
            porc = seleccion.get_value(iterador, 4)

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_02").set_text(self.cond_item)
            self.obj("txt_03").set_text(cant)
            self.obj("txt_04").set_text(precio)
            self.obj("txt_05").set_value(porc)

            self.focus_out_event(self.obj("txt_02"), 0)
            self.calcular_montos()

            # Buscar Depósito y Observaciones
            conexion = Op.conectar(self.origen.nav.datos_conexion)
            cursor = Op.consultar(conexion, "idDeposito, Deposito, Observaciones",
                self.origen.nav.tabla + "_inventario_s", " WHERE NroTimbrado = " + timb +
                " AND " + self.origen.nav.campoid + " = '" + nro + "'" +
                " AND idDetalle = " + self.cond)
            datos = cursor.fetchall()
            cant = cursor.rowcount
            conexion.close()  # Finaliza la conexión

            if cant > 0:
                iddep = "" if datos[0][0] is None else str(datos[0][0])
                dep = "" if datos[0][1] is None else datos[0][1]
                obs = "" if datos[0][2] is None else datos[0][2]

                self.obj("txt_01").set_text(iddep)
                self.obj("txt_01_1").set_text(dep)
                self.obj("txt_07").set_text(obs)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.origen.conexion,
                self.origen.nav.tabla + "_detalles_s WHERE NroTimbrado = " + timb +
                " AND " + self.origen.nav.campoid + " = '" + nro + "'", "idDetalle"))
            self.estadoguardar(False)

        self.origen.obj("grilla").get_selection().unselect_all()
        self.origen.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.origen.guardar_encabezado()
        puede_cerrar = True

        nro = self.origen.obj("txt_00").get_text()
        timb = self.origen.obj("txt_01").get_text()

        det = self.obj("txt_00").get_text()
        item = self.obj("txt_02").get_text()
        imp = self.obj("txt_02_7").get_text()
        cant = self.obj("txt_03").get_text()
        precio = self.obj("txt_04").get_text()
        porc = str(round(self.obj("txt_05").get_value(), 2))

        dep = self.obj("txt_01").get_text()
        obs = self.obj("txt_07").get_text()

        dep = "NULL" if len(dep) == 0 else dep
        obs = "NULL" if len(obs) == 0 else "'" + obs + "'"

        sql = timb + ", '" + nro + "', " + det + ", " + item + ", " + \
            cant + ", " + precio + ", " + porc + ", " + imp
        inv = timb + ", '" + nro + "', " + det + ", " + item

        if not self.editando:
            Op.insertar(self.origen.conexion, self.origen.nav.tabla + "_detalles", sql)

            # Datos de la Tabla Inventario
            mov = Op.nuevoid(self.origen.conexion, "inventario" +
                " WHERE idItem = " + item, "idMovimiento")
            lote = "NULL"

            if self.origen.nav.tabla == "notacreditocompras":
                cant = "-" + cant  # Se retiran ítems

            Op.insertar(self.origen.conexion, "inventario", item + ", " + mov + ", " +
                dep + ", " + lote + ", " + cant + ", " + obs)
            Op.insertar(self.origen.conexion, self.origen.nav.tabla + "_inventario",
                inv + ", " + mov)
        else:
            # Buscar datos del movimiento en tabla Inventario
            cursor = Op.consultar(self.origen.conexion, "idMovimiento, NroLote, CantidadFact",
                self.origen.nav.tabla + "_inventario_s", " WHERE " +
                "NroTimbrado = " + timb + " AND " + self.origen.nav.campoid + " = '" + nro + "'" +
                " AND idDetalle = " + det + " AND idItem = " + item)
            datos = cursor.fetchall()
            filas = cursor.rowcount

            if filas == 1:  # Solo hay un movimiento del Inventario que modificar
                mov = str(datos[0][0])
                lote = "NULL" if datos[0][1] is None else "'" + datos[0][1] + "'"

                if self.origen.nav.tabla == "notacreditocompras":
                    cant = "-" + cant  # Se retiran ítems

                Op.modificar(self.origen.conexion, "inventario", self.cond_item + ", " +
                    item + ", " + mov + ", " + dep + ", " + lote + ", " + cant + ", " + obs)
                Op.modificar(self.origen.conexion, self.origen.nav.tabla + "_detalles",
                    self.cond + ", " + sql)

            else:  # Hay varios registros por este detalle
                cantidad_anterior = datos[0][2]

                # Buscar registro de movimiento con NroLote = NULL
                cursor = Op.consultar(self.origen.conexion, "idMovimiento, CantidadInv",
                    self.tabla + "_inventario_s", " WHERE " + self.cond_buscar +
                    " AND idItem = " + self.idItem + " AND NroLote IS NULL")
                datos_null = cursor.fetchall()
                filas_null = cursor.rowcount

                if float(cant) == cantidad_anterior:
                    print("La cantidad NO ha cambiado: (" + str(cantidad_anterior) + ")")

                elif float(cant) > cantidad_anterior:  # La cantidad actual es mayor a la original
                    if filas_null > 0:
                        # Cantidad Anterior - Nueva Cantidad + Cantidad del Movimiento ya registrado
                        cant_null = float(cant) - cantidad_anterior + datos_null[0][1]

                        Op.modificar(self.conexion, "inventario",
                            item + ", " + item + ", " + str(datos_null[0][0]) + ", " +
                            dep + ", NULL, " + str(cant_null) + ", " + obs)
                    else:
                        # Datos de la Tabla Inventario
                        mov = Op.nuevoid(self.origen.conexion, "inventario" +
                            " WHERE idItem = " + item, "idMovimiento")
                        lote = "NULL"  # Inserta registro sin lote
                        cant = float(cant) - cantidad_anterior

                        # Inserta nuevo registro de movimiento con NroLote = NULL
                        Op.insertar(self.origen.conexion, "inventario", item + ", " +
                            mov + ", " + dep + ", " + lote + ", " + str(cant) + ", " + obs)
                        Op.insertar(self.origen.conexion, self.origen.nav.tabla + "_inventario",
                            inv + ", " + mov)

                    # Modificar registro del Detalle
                    Op.modificar(self.origen.conexion, self.origen.nav.tabla + "_detalles",
                        self.cond + ", " + sql)

                else:  # La cantidad actual es menor a la original
                    espacio_suficiente = True

                    if filas_null > 0:
                        retira = cantidad_anterior - float(cant)

                        if datos_null[0][1] == retira:
                            # Elimina registro de movimiento con NroLote = NULL
                            Op.eliminar(self.conexion, self.tabla + "_inventario",
                                inv + ", " + str(datos_null[0][0]))
                            Op.eliminar(self.conexion, "inventario",
                                item + ", " + str(datos_null[0][0]))

                        elif datos_null[0][1] > retira:
                            cant_null = datos_null[0][1] - retira

                            # Modifica registro de movimiento con NroLote = NULL
                            Op.modificar(self.conexion, "inventario",
                                item + ", " + item + ", " + str(datos_null[0][0]) + ", " +
                                dep + ", NULL, " + str(cant_null) + ", " + obs)

                        else:
                            espacio_suficiente = puede_cerrar = False
                    else:
                        espacio_suficiente = puede_cerrar = False

                    if not espacio_suficiente:
                        Mens.atencion_generico("No ha sido posible Guardar el registro",
                            "Se ha disminuido la Cantidad de Ítems. Por favor, revise el registro de Lotes." +
                            "\nDebe dejar una cantidad de Ítem con el Lote sin asignar para la modificación.")
                        self.avisado = True

                    else:
                        # Modificar registro del Detalle
                        Op.modificar(self.origen.conexion, self.origen.nav.tabla + "_detalles",
                            self.cond + ", " + sql)

        if puede_cerrar:
            self.origen.cargar_grilla_detalles()
            self.origen.estadoguardar(True)
            self.obj("ventana").destroy()

    def on_btn_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_lotes_clicked(self, objeto):
        nro = self.origen.obj("txt_00").get_text()
        timb = self.origen.obj("txt_01").get_text()
        det = self.obj("txt_00").get_text()
        item = self.obj("txt_02").get_text()
        cant = float(self.obj("txt_03").get_text())

        buscar = "NroTimbrado = " + timb + " AND " + self.origen.nav.campoid + \
            " = '" + nro + "' AND idDetalle = " + det
        guardar = timb + ", '" + nro + "', " + det

        if not self.avisado:
            # Guarda el Ítem en el detalle y cierra la ventana Ins-Mod Ítems
            self.on_btn_guardar_clicked(0)

        from compras.lotes import lotes
        lotes(self.origen.conexion, self.origen.nav.datos_conexion,
            self.origen.nav.tabla, cant, item, buscar, guardar)

    def on_btn_item_clicked(self, objeto):
        if self.origen.nav.tabla == "notacreditocompras":
            fact = self.origen.nro_fact.get_text()
            timb = str(self.origen.nro_timb)
            self.obj("txt_00").grab_focus()

            opcion = [" INNER JOIN facturacompras_detalles_s F " +
            "ON ((F.NroTimbrado = " + timb + ") AND (F.NroFactura = '" + fact + "')" +
            " AND (I.idItem = F.idItem))", ", F.Cantidad, F.Precio, 0, F.IVA"]
        else:
            opcion = None

        from clases.llamadas import items
        items(self.origen.nav.datos_conexion, self, opcion)

    def on_btn_deposito_clicked(self, objeto):
        from clases.llamadas import depositos
        depositos(self.origen.nav.datos_conexion, self)

    def on_txt_05_value_changed(self, objeto):
        print(str(self.obj("txt_05").get_value()))
        self.calcular_montos()

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_02").get_text()) == 0 \
        or len(self.obj("txt_03").get_text()) == 0 or len(self.obj("txt_04").get_text()) == 0 \
        or len(self.obj("txt_05_1").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Cód. de Detalle", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Cód. de Ítem", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_03"), "Cantidad de Ítems", self.obj("barraestado"), False) \
            and Op.comprobar_numero(float, self.obj("txt_04"), "Precio Unitario", self.obj("barraestado"), False) \
            and Op.comprobar_numero(float, self.obj("txt_05_1"), "Monto de Descuento", self.obj("barraestado")):
                if len(self.obj("txt_01").get_text()) > 0:
                    estado = Op.comprobar_numero(int, self.obj("txt_01"),
                        "Cód. de Depósito", self.obj("barraestado"))
                else:
                    estado = True
            else:
                estado = False

        self.avisado = False
        self.estadoguardar(estado)

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_01"):
                    self.on_btn_deposito_clicked(0)
                elif objeto in (self.obj("txt_02"), self.obj("txt_02_1")):
                    self.on_btn_item_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_01"):
            tipo = "Depósito"
        elif objeto in (self.obj("txt_02"), self.obj("txt_02_1")):
            tipo = "Ítem"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un " + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_01"):  # Depósito
                self.obj("txt_01_1").set_text("")
            elif objeto == self.obj("txt_02"):  # Código del Ítem
                self.obj("txt_02_1").set_text("")
                self.limpiar_items()
            elif objeto == self.obj("txt_02_1") and len(self.obj("txt_02").get_text()) == 0:
                self.limpiar_items()
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) and \
                Op.comprobar_numero(int, objeto, "Cód. de Detalle", self.obj("barraestado")):
                    Op.comprobar_unique(self.origen.conexion, self.origen.nav.tabla + "_detalles_s",
                        "idDetalle", valor + " AND NroTimbrado = " + self.origen.obj("txt_01").get_text() +
                        " AND " + self.origen.nav.campoid + " = '" + self.origen.obj("txt_00").get_text() + "'",
                        self.obj("txt_00"), self.estadoguardar, self.obj("barraestado"),
                        "El Código introducido ya ha sido registado en esta " + self.origen.nav.titulo + ".")

            elif objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Depósito", self.obj("barraestado")):
                    conexion = Op.conectar(self.origen.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "Descripcion", "depositos_s",
                        " WHERE idDeposito = " + valor + " AND Activo = 1")
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("txt_01_1").set_text(datos[0][0])
                        self.obj("barraestado").push(0, "")
                        self.verificacion(0)
                    else:
                        objeto.grab_focus()
                        self.estadoguardar(False)
                        self.obj("barraestado").push(0, "El Cód. de Depósito no es válido.")
                        self.obj("txt_01_1").set_text("")

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Cód. de Ítem", self.obj("barraestado")):
                    self.buscar_item(objeto, "idItem", valor, "Ítem")

            elif objeto == self.obj("txt_02_1"):
                self.buscar_item(objeto, "CodigoBarras", "'" + valor + "'", "Barras")

            elif objeto == self.obj("txt_03"):
                if Op.comprobar_numero(float, objeto, "Cantidad de Ítems", self.obj("barraestado")):
                    if self.origen.nav.tabla == "notacreditocompras":
                        if float(valor) > self.item_cant_max:
                            self.obj("barraestado").push(0, "La Cantidad de Ítems " +
                            "NO puede ser Mayor a la de la Factura (" + str(self.item_cant_max) + ").")
                            self.obj("txt_02").grab_focus()
                            self.estadoguardar(False)
                        else:
                            self.calcular_montos()
                    else:
                        self.calcular_montos()

            elif objeto == self.obj("txt_04"):
                if Op.comprobar_numero(float, objeto, "Precio Unitario", self.obj("barraestado")):
                    self.calcular_montos()

            elif objeto == self.obj("txt_05_1"):
                if Op.comprobar_numero(float, objeto, "Monto de Descuento", self.obj("barraestado")):
                    self.calcular_montos(False)

    def buscar_item(self, objeto, campo, valor, nombre):
        if self.origen.nav.tabla == "notacreditocompras":
            fact = self.origen.nro_fact.get_text()
            timb = str(self.origen.nro_timb)

            opcion = " INNER JOIN facturacompras_detalles_s F ON ((F.NroTimbrado" + \
            " = " + timb + ") AND (F.NroFactura = '" + fact + "') AND (I.idItem = F.idItem))"
            otroscampos = "F.IVA, F.Cantidad, F.Precio"
        else:
            opcion, otroscampos = "", "I.Porcentaje"

        conexion = Op.conectar(self.origen.nav.datos_conexion)
        cursor = Op.consultar(conexion, "I.idItem, I.CodigoBarras, I.Nombre, " +
            "I.idPresentacion, I.Presentacion, I.idCategoria, I.Categoria, " +
            otroscampos, "items_s I" + opcion, " WHERE " + campo + " = " + valor)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            codbar = "" if datos[0][1] is None else datos[0][1]

            self.obj("txt_02").set_text(str(datos[0][0]))
            self.obj("txt_02_1").set_text(codbar)
            self.obj("txt_02_2").set_text(datos[0][2])
            self.obj("txt_02_3").set_text(str(datos[0][3]))
            self.obj("txt_02_4").set_text(datos[0][4])
            self.obj("txt_02_5").set_text(str(datos[0][5]))
            self.obj("txt_02_6").set_text(datos[0][6])
            self.obj("txt_02_7").set_text(str(datos[0][7]))

            if self.origen.nav.tabla == "notacreditocompras":
                self.item_cant_max = datos[0][8]
                self.obj("txt_04").set_text(str(datos[0][9]))

        else:
            objeto.grab_focus()
            self.estadoguardar(False)
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_02_1") if objeto == self.obj("txt_02") else self.obj("txt_02")
            self.limpiar_items()
            otro.set_text("")

    def limpiar_items(self):
        self.obj("txt_02_2").set_text("")
        self.obj("txt_02_3").set_text("")
        self.obj("txt_02_4").set_text("")
        self.obj("txt_02_5").set_text("")
        self.obj("txt_02_6").set_text("")
        self.obj("txt_02_7").set_text("")

    def calcular_montos(self, desde_porcentaje=True):
        cantidad = self.obj("txt_03").get_text()
        precio = self.obj("txt_04").get_text()

        if desde_porcentaje:
            porcentaje = round(Decimal(self.obj("txt_05").get_value()), 2)
        else:
            descuento = Decimal(self.obj("txt_05_1").get_text())

        if len(cantidad) > 0 and len(precio) > 0:
            monto = Decimal(precio) * Decimal(cantidad)

            if desde_porcentaje:
                descuento = monto * porcentaje / 100  # Monto de Descuento
                self.obj("txt_05_1").set_text(str(descuento))
            else:
                porcentaje = descuento * 100 / monto  # Porcentaje de Desc.
                self.obj("txt_05").set_value(round(porcentaje, 2))

            subtotal = monto - descuento
            self.obj("txt_06").set_text(str(subtotal))

    def estadoguardar(self, estado):
        self.obj("btn_guardar").set_sensitive(estado)
        self.obj("btn_lotes").set_sensitive(estado)
