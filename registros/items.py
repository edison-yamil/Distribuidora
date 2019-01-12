#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from decimal import Decimal
from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen):
        self.editando = edit
        self.nav = origen

        arch = Op.archivo("abm_items")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de " + self.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(40)
        self.obj("txt_02").set_max_length(20)
        self.obj("txt_03").set_max_length(100)
        self.obj("txt_04").set_max_length(100)
        self.obj("txt_05").set_max_length(10)
        self.obj("txt_06").set_max_length(10)
        self.obj("txt_07").set_max_length(10)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código del Ítem")
        self.obj("txt_01").set_tooltip_text("Ingrese el Código de Barras del Ítem")
        self.obj("txt_02").set_tooltip_text("Ingrese el Nombre del Ítem")
        self.obj("txt_03").set_tooltip_text("Ingrese una Descripción del Ítem")
        self.obj("txt_04").set_tooltip_text("Ingrese una Observación acerca del Ítem")
        self.obj("txt_02").grab_focus()

        self.obj("txt_05").set_tooltip_text(Mens.usar_boton("la Categoría a la que pertenece"))
        self.obj("txt_05_1").set_tooltip_text("Descripción de la Categoría")
        self.obj("txt_05_2").set_tooltip_text("Porcentaje grabado a la Categoría")
        self.obj("txt_06").set_tooltip_text(Mens.usar_boton("la Marca del Ítem"))
        self.obj("txt_06_1").set_tooltip_text("Descripción de la Marca")
        self.obj("txt_07").set_tooltip_text(Mens.usar_boton("la Presentación del Ítem"))
        self.obj("txt_07_1").set_tooltip_text("Descripción de la Presentación")
        self.obj("txt_08").set_tooltip_text("Ingrese el Contenido Neto")
        self.obj("txt_09").set_tooltip_text("Ingrese la cantidad mínima de unidades que debe haber en el Stock")
        self.obj("txt_10").set_tooltip_text("Ingrese el Porcentaje de Comisión aplicado sobre el precio de venta del Ítem")

        self.txt_cod_cat, self.txt_des_cat, self.txt_por_imp = self.obj("txt_05"), self.obj("txt_05_1"), self.obj("txt_05_2")
        self.txt_cod_mar_it, self.txt_des_mar_it = self.obj("txt_06"), self.obj("txt_06_1")
        self.txt_cod_pres, self.txt_des_pres = self.obj("txt_07"), self.obj("txt_07_1")

        self.idUnidadMedida = self.idTipoCliente = -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_unidad"), "unidadmedidas", "idUnidadMedida")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_cliente"), "tipoclientes", "idTipoCliente")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            codbar = seleccion.get_value(iterador, 1)
            nombre = seleccion.get_value(iterador, 2)
            descrip = seleccion.get_value(iterador, 3)
            obs = seleccion.get_value(iterador, 16)
            act = True if seleccion.get_value(iterador, 17) == 1 else False

            codcat = str(seleccion.get_value(iterador, 4))
            descat = seleccion.get_value(iterador, 5)
            porc = str(seleccion.get_value(iterador, 7))
            codmar = str(seleccion.get_value(iterador, 8))
            desmar = seleccion.get_value(iterador, 9)
            codpres = str(seleccion.get_value(iterador, 10))
            despres = seleccion.get_value(iterador, 11)
            cont = seleccion.get_value(iterador, 12)
            unmed = seleccion.get_value(iterador, 13)
            stock = seleccion.get_value(iterador, 15)

            codbar = "" if codbar is None else codbar
            descrip = "" if descrip is None else descrip
            obs = "" if obs is None else obs

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(codbar)
            self.obj("txt_02").set_text(nombre)
            self.obj("txt_03").set_text(descrip)
            self.obj("txt_04").set_text(obs)
            self.obj("rad_activo").set_active(act)

            self.obj("txt_05").set_text(codcat)
            self.obj("txt_05_1").set_text(descat)
            self.obj("txt_05_2").set_text(porc)
            self.obj("txt_06").set_text(codmar)
            self.obj("txt_06_1").set_text(desmar)
            self.obj("txt_07").set_text(codpres)
            self.obj("txt_07_1").set_text(despres)

            self.obj("txt_08").set_value(cont)
            self.obj("txt_09").set_value(stock)

            # Asignación de Unidad de Medida en Combo
            model, i = self.obj("cmb_unidad").get_model(), 0
            while model[i][0] != unmed: i += 1
            self.obj("cmb_unidad").set_active(i)

            # Búsqueda de Precio de Costo y Porc. de Comisión
            conexion = Op.conectar(self.nav.datos_conexion)
            cursor = Op.consultar(conexion, "PrecioCosto, PorcComision",
                "items_s", " WHERE " + self.nav.campoid + " = " + self.cond)
            datos = cursor.fetchall()

            self.PrecioCosto = datos[0][0]
            self.obj("txt_10").set_value(datos[0][1])
            self.obj("txt_p_00").set_text(str(self.PrecioCosto))
            self.buscar_precio_sin_iva(self.obj("txt_p_00"), self.obj("txt_p_01"))

        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))

            self.PrecioCosto = 0
            self.obj("txt_p_00").set_text("0.0")
            self.obj("txt_p_01").set_text("0.0")

            self.obj("cmb_unidad").set_active(0)
            self.obj("rad_activo").set_active(True)

        self.conexion = Op.conectar(self.nav.datos_conexion)
        self.principal_guardado = True

        self.config_grilla_precio()
        self.cargar_grilla_precio()

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_principal_items()
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def on_btn_categoria_clicked(self, objeto):
        from clases.llamadas import categorias
        categorias(self.nav.datos_conexion, self)
        self.obj("barraestado").push(0, "")

    def on_btn_marca_clicked(self, objeto):
        from clases.llamadas import marcaitems
        marcaitems(self.nav.datos_conexion, self)
        self.obj("barraestado").push(0, "")

    def on_btn_presentacion_clicked(self, objeto):
        from clases.llamadas import presentaciones
        presentaciones(self.nav.datos_conexion, self)
        self.obj("barraestado").push(0, "")

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_02").get_text()) == 0 \
        or len(self.obj("txt_05").get_text()) == 0 or len(self.obj("txt_06").get_text()) == 0 \
        or len(self.obj("txt_07").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Cód. de Ítem", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_05"), "Cód. de Categoría", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_06"), "Cód. de Marca", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_07"), "Cód. de Presentación", self.obj("barraestado")):
                estado = True
                self.obj("barraestado").push(0, "")
            else:
                estado = False

        self.principal_guardado = False
        self.estadoedicion(estado)

    def on_cmb_unidad_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            self.idUnidadMedida = model[active][0]
            self.verificacion(0)
        else:
            self.obj("barraestado").push(0, "No existen registros de Unidades de Medida en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_05"):
                    self.on_btn_categoria_clicked(0)
                elif objeto == self.obj("txt_06"):
                    self.on_btn_marca_clicked(0)
                elif objeto == self.obj("txt_07"):
                    self.on_btn_presentacion_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_05"):
            tipo = "a Categoría"
        elif objeto == self.obj("txt_06"):
            tipo = "a Marca de Ítem"
        elif objeto == self.obj("txt_07"):
            tipo = "a Presentación"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un" + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_05"):
                self.obj("txt_05_1").set_text("")
                self.obj("txt_05_2").set_text("")
            elif objeto == self.obj("txt_06"):
                self.obj("txt_06_1").set_text("")
            elif objeto == self.obj("txt_07"):
                self.obj("txt_07_1").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) and \
                Op.comprobar_numero(int, self.obj("txt_00"), "Cód. de Ítem", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                        self.nav.campoid, valor, objeto, self.estadoedicion, self.obj("barraestado"),
                        "El Código introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                if not len(self.obj("txt_00").get_text()) == 0:
                    # Al editar debe ser diferente al original
                    busc = "" if not self.editando else " AND idItem <> " + self.obj("txt_00").get_text()
                    # Comprueba si el codigo de barras ya ha sido registado
                    Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                        "CodigoBarras", "'" + valor + "'" + busc, objeto,
                        self.estadoedicion, self.obj("barraestado"),
                        "El Código de Barras introducido ya ha sido registado.")

            elif objeto == self.obj("txt_02"):
                # Al editar debe ser diferente al original
                busc = "" if not self.editando else " AND " + self.nav.campoid + " <> " + self.cond
                # Comprueba si el nombre ya ha sido registado
                Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                    "Nombre", "'" + valor + "'" + busc, objeto, self.estadoedicion,
                    self.obj("barraestado"), "El Nombre introducido ya ha sido registado.")

            elif objeto == self.obj("txt_05"):
                self.buscar_foraneos(objeto, self.obj("txt_05_1"),
                    " Categoría", "categorias_s", "Descripcion, Porcentaje", "idCategoria", valor)

            elif objeto == self.obj("txt_06"):
                self.buscar_foraneos(objeto, self.obj("txt_06_1"),
                    "Marca", "marcaitems", "Descripcion", "idMarca", valor)

            elif objeto == self.obj("txt_07"):
                self.buscar_foraneos(objeto, self.obj("txt_07_1"),
                    "Presentación", "presentaciones", "Descripcion", "idPresentacion", valor)

    def buscar_foraneos(self, objeto, companero, nombre, tabla, campo_busq, campo_id, valor, condicion=""):
        if Op.comprobar_numero(int, objeto, "Cód. de " + nombre, self.obj("barraestado")):
            conexion = Op.conectar(self.nav.datos_conexion)
            cursor = Op.consultar(conexion, campo_busq, tabla,
                " WHERE " + campo_id + " = " + valor + condicion)
            datos = cursor.fetchall()
            cant = cursor.rowcount
            conexion.close()  # Finaliza la conexión

            if cant > 0:
                companero.set_text(datos[0][0])
                if tabla == "categorias_s":
                    self.obj("txt_05_2").set_text(str(datos[0][1]))

                self.obj("barraestado").push(0, "")
                self.verificacion(0)

            else:
                self.estadoedicion(False)
                objeto.grab_focus()
                self.obj("barraestado").push(0, "El Cód. de " + nombre + " no es válido.")

                companero.set_text("")
                if tabla == "categorias_s":
                    self.obj("txt_05_2").set_text("")

    def guardar_principal_items(self):
        if not self.principal_guardado:
            v1 = self.obj("txt_00").get_text()
            v2 = self.obj("txt_01").get_text()  # Código de Barras
            v3 = self.obj("txt_02").get_text()
            v4 = self.obj("txt_03").get_text()  # Descripción
            v5 = self.obj("txt_04").get_text()  # Observación
            v6 = self.obj("txt_05").get_text()
            v7 = self.obj("txt_06").get_text()
            v8 = self.obj("txt_07").get_text()

            v9 = str(round(self.obj("txt_08").get_value(), 2))  # Contenido Neto
            v10 = str(round(self.obj("txt_09").get_value(), 2))
            v11 = str(round(self.obj("txt_10").get_value(), 2))
            v12 = "1" if self.obj("rad_activo").get_active() else "0"

            v2 = "NULL" if len(v2) == 0 else "'" + v2 + "'"
            v4 = "NULL" if len(v4) == 0 else "'" + v4 + "'"
            v5 = "NULL" if len(v5) == 0 else "'" + v5 + "'"

            sql = v1 + ", " + v6 + ", " + v7 + ", " + v8 + ", " + \
                "'" + self.idUnidadMedida + "', " + v2 + ", " + \
                "'" + v3 + "', " + v4 + ", " + v9 + ", " + \
                v10 + ", " + v11 + ", " + v5 + ", " + v12

            if not self.editando:
                Op.insertar(self.conexion, self.nav.tabla, sql)
            else:
                Op.modificar(self.conexion, self.nav.tabla, self.cond + ", " + sql)

    def estadoedicion(self, estado):
        self.obj("box3").set_sensitive(estado)
        self.obj("box4").set_sensitive(False)
        self.obj("box5").set_sensitive(estado)
        self.obj("btn_guardar").set_sensitive(estado)

#### Precios ###########################################################

    def config_grilla_precio(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)

        col0 = Op.columnas("Código", Op.celdas(0.5), 0, True, 100)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Tipo de Cliente", Op.celdas(0.0), 1, True, 175)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Precio", Op.celdas(1.0), 2, True, 100)
        col2.set_sort_column_id(2)

        self.obj("grilla_precio").append_column(col0)
        self.obj("grilla_precio").append_column(col1)
        self.obj("grilla_precio").append_column(col2)

        self.obj("grilla_precio").set_rules_hint(True)
        self.obj("grilla_precio").set_search_column(1)
        self.obj("grilla_precio").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, float, float)
        self.obj("grilla_precio").set_model(lista)
        self.obj("grilla_precio").show()

    def cargar_grilla_precio(self):
        cursor = Op.consultar(self.conexion,
            "idTipoCliente, TipoCliente, PrecioVenta, PorcDescMaximo",
            "precios_s", " WHERE idItem = " + self.obj("txt_00").get_text() +
            " ORDER BY idTipoCliente")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla_precio").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_precio_clicked(self, objeto):
        self.editando_precio = False
        self.funcion_precios()

    def on_btn_modificar_precio_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla_precio").get_selection().get_selected()
            self.cond_precio = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Modificar.")
        else:
            self.editando_precio = True
            self.funcion_precios()

    def on_btn_eliminar_precio_clicked(self, objeto):
        self.guardar_principal_items()

        try:
            seleccion, iterador = self.obj("grilla_precio").get_selection().get_selected()
            cod = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Eliminar.")
        else:
            tip = seleccion.get_value(iterador, 1)
            pre = str(seleccion.get_value(iterador, 2))

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Código: " + cod + "\nTipo: " + tip + "\nPrecio: " + pre)

            self.obj("grilla_precio").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "precios", item + ", " + cod)
                self.cargar_grilla_precio()

    def on_grilla_precio_cursor_changed(self, objeto):
        if len(self.obj("grilla_precio").get_model()) > 0:
            self.buscar_datos_precio()

    def on_grilla_precio_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_precio_clicked(0)

    def on_grilla_precio_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_precio_clicked(0)

    def buscar_datos_precio(self):
        seleccion, iterador = self.obj("grilla_precio").get_selection().get_selected()
        tipo = seleccion.get_value(iterador, 0)
        venta = seleccion.get_value(iterador, 2)
        porc = seleccion.get_value(iterador, 3)

        # Asignación de Tipo de Cliente en Combo
        model, i = self.obj("cmb_cliente").get_model(), 0
        while model[i][0] != tipo: i += 1
        self.obj("cmb_cliente").set_active(i)

        self.obj("txt_p_04").set_value(porc)
        self.obj("txt_p_06").set_text(str(venta))
        self.buscar_precio_sin_iva(self.obj("txt_p_06"), self.obj("txt_p_05"))

        self.obj("txt_p_02").set_value(0.0)
        self.obj("txt_p_03").set_text("")

    def buscar_precio_sin_iva(self, con_iva, sin_iva):
        valor = Decimal(con_iva.get_text())
        iva = self.obj("txt_05_2").get_text()

        if len(iva) > 0 and valor > 0:
            # Cálculo del divisor (100/10+1=11 y 100/5+1=21)
            divisor = (100 / Decimal(iva)) + 1

            monto = valor / divisor
            sin_iva.set_text(str(monto))
        else:
            sin_iva.set_text("0.0")

    def calculo_utilidad(self, objeto):
        costo_sin_iva = self.obj("txt_p_01").get_text()
        if not len(costo_sin_iva) == 0:
            if objeto == self.obj("txt_09_1"):
                porc = self.obj("txt_09_1").get_text()
                if not len(porc) == 0:
                    ganancia = Decimal(costo) * Decimal(porc) / 100
                    resultado = Decimal(costo) + ganancia
                    self.obj("txt_09").set_text(str(resultado))
            else:
                venta = self.obj("txt_09").get_text()
                if not len(venta) == 0:
                    diferencia = Decimal(venta) - Decimal(costo)
                    resultado = diferencia * 100 / Decimal(costo)
                    self.obj("txt_09_1").set_text(str(resultado))

    def estadoedicion_precio(self, estado):
        self.estadoedicion(not estado)
        self.obj("btn_cancelar").set_sensitive(not estado)
        self.obj("box4").set_sensitive(estado)

#### Agregar-Modificar Precios #########################################

    def funcion_precios(self):
        self.guardar_principal_items()

        if self.editando_precio:
            self.buscar_datos_precio()
        else:
            self.obj("cmb_cliente").set_active(0)
            self.obj("txt_p_02").set_value(0.0)
            self.obj("txt_p_03").set_text("")
            self.obj("txt_p_04").set_value(0.0)
            self.obj("txt_p_05").set_text("")
            self.obj("txt_p_06").set_text("")

        self.obj("grilla_precio").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        self.estadoedicion_precio(True)

    def on_btn_guardar_precio_clicked(self, objeto):
        self.guardar_principal_items()

        item = self.obj("txt_00").get_text()
        vent = self.obj("txt_p_06").get_text()
        desc = round(self.obj("txt_p_04").get_value(), 2)

        sql = item + ", " + str(self.idTipoCliente) + ", " + vent + ", " + str(desc)
        if not self.editando_precio:
            Op.insertar(self.conexion, "precios", sql)
        else:
            Op.modificar(self.conexion, "precios", self.cond_precio + ", " + sql)

        self.cargar_grilla_precio()
        self.on_btn_cancelar_precio_clicked(0)

    def on_btn_cancelar_precio_clicked(self, objeto):
        self.obj("cmb_cliente").set_active(-1)
        self.obj("barraestado").push(0, "")
        self.estadoedicion_precio(False)

    def verificacion_precio(self, objeto):
        if len(self.obj("txt_p_06").get_text()) == 0 or self.idTipoCliente == -1:
            estado = False
        else:
            if Op.comprobar_numero(float, self.obj("txt_p_06"), "Precio de Venta", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar_precio").set_sensitive(estado)

    def verificacion_utilidad(self, objeto):
        pass

    def on_cmb_cliente_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            self.idTipoCliente = model[active][0]
            self.verificacion_precio(0)
        else:
            self.obj("barraestado").push(0, "No existen registros de Tipos de Clientes en el Sistema.")

#### Depósitos #########################################################

    def funcion_depositos(self):
        pass

#### Lotes #############################################################

    def funcion_lotes(self):
        pass


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)
    celda2 = Op.celdas(1.0)

    col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Código de Barras", celda1, 1, True, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Nombre", celda1, 2, True, 200)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Descripción", celda1, 3, True, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Cód. Cat.", celda0, 4, True, 100, 150)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Categoría", celda1, 5, True, 150)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Impuesto", celda1, 6, True, 150)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Porcentaje", celda2, 7, True, 100, 150)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Cód. Marca", celda0, 8, True, 100, 150)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Marca", celda1, 9, True, 150)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Cód. Pres.", celda0, 10, True, 100, 150)
    col10.set_sort_column_id(10)
    col11 = Op.columnas("Presentación", celda1, 11, True, 150)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Contenido Neto", celda2, 12, True, 150)
    col12.set_sort_column_id(12)
    col13 = Op.columnas("Cód. Un. Med.", celda0, 13, True, 100, 150)
    col13.set_sort_column_id(13)
    col14 = Op.columnas("Unidad de Medida", celda1, 14, True, 150)
    col14.set_sort_column_id(14)
    col15 = Op.columnas("Stock Mínimo", celda2, 15, True, 150)
    col15.set_sort_column_id(15)
    col16 = Op.columnas("Observaciones", celda1, 16, True, 200)
    col16.set_sort_column_id(16)
    col17 = Op.columna_active("Activo", 17)
    col17.set_sort_column_id(17)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9,
        col10, col11, col12, col13, col14, col15, col16]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col17)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 1)

    if len(self.condicion) == 0:
        lista = ListStore(int, str, str, str, int, str, str, float, int, str,
            int, str, float, str, str, float, str, int, int)
    else:  # ListStore NO puede modificarse después de haber sido creado
        lista = ListStore(int, str, str, str, int, str, str, float, int, str,
            int, str, float, str, str, float, str, int, int, float, float, float, float)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
    " WHERE I." + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    if self.obj("rad_act").get_active() or self.obj("rad_ina").get_active():
        activo = "1" if self.obj("rad_act").get_active() else "0"
        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += "I.Activo = " + activo

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, "I." + self.campoid + ", " +
        "I.CodigoBarras, I.Nombre, I.Descripcion, I.idCategoria, I.Categoria, " +
        "I.Impuesto, I.Porcentaje, I.idMarca, I.Marca, I.idPresentacion, I.Presentacion, " +
        "I.ContenidoNeto, I.idUnidadMedCont, I.UnidadMedida, I.StockMinimo, " +
        "I.Observaciones, I.Activo, I.Unidad" + self.otroscampos,
        self.tabla + "_s I" + self.condicion, opcion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        listafila = [datos[i][0], datos[i][1], datos[i][2], datos[i][3],
        datos[i][4], datos[i][5], datos[i][6], datos[i][7], datos[i][8], datos[i][9],
        datos[i][10], datos[i][11], datos[i][12], datos[i][13], datos[i][14],
        datos[i][15], datos[i][16], datos[i][17], datos[i][18]]

        if len(self.condicion) > 0:
            # Cantidad, Precio o PrecioCosto, PrecioVenta, IVA
            listafila.extend([datos[i][19], datos[i][20], datos[i][21], datos[i][22]])

        lista.append(listafila)

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Código", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "Código de Barras", "CodigoBarras"
    elif idcolumna == 2:
        col, self.campo_buscar = "Nombre", "Nombre"
    elif idcolumna == 3:
        col, self.campo_buscar = "Descripción", "Descripcion"
    elif idcolumna == 4:
        col, self.campo_buscar = "Cód. Categoría", "idCategoria"
    elif idcolumna == 5:
        col, self.campo_buscar = "Categoría", "Categoria"
    elif idcolumna == 6:
        col, self.campo_buscar = "Impuesto", "Impuesto"
    elif idcolumna == 7:
        col, self.campo_buscar = "Porcentaje", "Porcentaje"
    elif idcolumna == 8:
        col, self.campo_buscar = "Cód. Marca", "idMarca"
    elif idcolumna == 9:
        col, self.campo_buscar = "Marca", "Marca"
    elif idcolumna == 10:
        col, self.campo_buscar = "Cód. Presentación", "idPresentacion"
    elif idcolumna == 11:
        col, self.campo_buscar = "Presentación", "Presentacion"
    elif idcolumna == 12:
        col, self.campo_buscar = "Contenido Neto", "ContenidoNeto"
    elif idcolumna == 13:
        col, self.campo_buscar = "Cód. Unidad de Medida", "idUnidadMedida"
    elif idcolumna == 14:
        col, self.campo_buscar = "Unidad de Medida", "UnidadMedida"
    elif idcolumna == 15:
        col, self.campo_buscar = "Stock Mínimo", "StockMinimo"
    elif idcolumna == 16:
        col, self.campo_buscar = "Observaciones", "Observaciones"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 2)
    valor2 = seleccion.get_value(iterador, 11)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
        "Código: " + valor0 + "\nNombre: " + valor1 + "\nPresentación: " + valor2)

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
    from reportlab.lib.pagesizes import A4, landscape

    datos = self.obj("grilla").get_model()
    cant = len(datos)

    head = listado.tabla_celda_titulo()
    body_ce = listado.tabla_celda_centrado()
    body_iz = listado.tabla_celda_just_izquierdo()
    body_de = listado.tabla_celda_just_derecho()

    lista = [[Par("Código", head), Par("Código de Barras", head), Par("Nombre", head),
    Par("Presentación", head), Par("Precio de Costo", head), Par("Precio de Venta", head), Par("Estado", head)]]

    for i in range(0, cant):
        codbar = "" if datos[i][1] is None else datos[i][1]
        estado = "Activo" if datos[i][21] == 1 else "Inactivo"

        lista.append([Par(str(datos[i][0]), body_ce), Par(codbar, body_iz),
        Par(datos[i][2], body_iz), Par(datos[i][13], body_iz),
        Par(str(datos[i][17]), body_de), Par(str(datos[i][18]), body_de), Par(estado, body_ce)])

    listado.listado(self.titulo, lista, [75, 100, 175, 100, 100, 100, 50], landscape(A4))


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = seleccion.get_value(iterador, 1)
        valor2 = seleccion.get_value(iterador, 2)
        valor3 = str(seleccion.get_value(iterador, 10))
        valor4 = seleccion.get_value(iterador, 11)
        valor5 = str(seleccion.get_value(iterador, 4))
        valor6 = seleccion.get_value(iterador, 5)
        valor7 = str(seleccion.get_value(iterador, 7))
        #valor8 = str(seleccion.get_value(iterador, 17))
        #valor9 = str(seleccion.get_value(iterador, 18))

        valor1 = "" if valor1 is None else valor1

        self.origen.txt_cod_it.set_text(valor0)
        self.origen.txt_bar_it.set_text(valor1)
        self.origen.txt_nom_it.set_text(valor2)

        try:  # Presentación
            self.origen.txt_des_pres.set_text(valor4)
            self.origen.txt_cod_pres.set_text(valor3)
        except:
            pass

        try:  # Categoría
            self.origen.txt_des_cat.set_text(valor6)
            self.origen.txt_cod_cat.set_text(valor5)
        except:
            pass

        try:  # Porcentaje de IVA
            self.origen.txt_por_imp.set_text(valor7)
        except:
            pass

        '''try:  # Precio de Costo
            self.origen.txt_cost_it.set_text(valor8)
        except:
            pass

        try:  # Precio o Precio de Costo (Nota de Crédito)
            valor10 = str(seleccion.get_value(iterador, 23))
            self.origen.txt_precio_costo_nota.set_text(valor10)
        except:
            pass

        try:  # Precio de Venta (Nota de Crédito)
            valor11 = str(seleccion.get_value(iterador, 24))
            self.origen.txt_precio_venta_nota.set_text(valor11)
        except:
            pass'''


        self.on_btn_salir_clicked(0)
    except:
        pass
