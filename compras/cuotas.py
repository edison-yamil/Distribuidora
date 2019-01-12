#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date
from gi.repository.Gtk import CellRendererText
from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class cuotas:

    def __init__(self, datos_conexion, tabla, datos=None, con=None):
        self.datos_conexion = datos_conexion
        self.tabla = tabla

        arch = Op.archivo("cuotas")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(700, 600)
        self.obj("ventana").set_modal(True)

        self.obj("ventana").set_title("Cuentas por Facturas a Crédito")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_i_00").set_tooltip_text("Ingrese la Cantidad de Cuotas que desea generar\n" +
            "Presione Enter para actualizar el Monto de cada Cuota")
        self.obj("cmb_pago").set_tooltip_text("Seleccione el Periodo de Pago de la Cuota")
        self.obj("txt_i_02").set_tooltip_text("Ingrese el Monto de cada Cuota\n" +
            "Presione Enter para actualizar la Cantidad de Cuotas a generar")

        self.obj("txt_d_00").set_tooltip_text("Ingrese el Número Identificador de la Cuota")
        self.obj("txt_d_01").set_tooltip_text(Mens.usar_boton("una Fecha de Vencimiento de la Cuota"))
        self.obj("txt_d_02").set_tooltip_text("Ingrese el Monto de la Cuota")

        self.obj("btn_factura").set_tooltip_text("Presione este botón para buscar la Factura para la que crearán las Cuotas")
        self.obj("btn_nueva_cuota").set_tooltip_text("Presione este botón para agregar una nueva Cuota")
        self.obj("btn_modificar_cuota").set_tooltip_text("Presione este botón para modificar datos de una Cuota")
        self.obj("btn_eliminar_cuota").set_tooltip_text("Presione este botón para eliminar una Cuota")

        if con is not None:
            self.conexion = con
            cursor = self.conexion.cursor()
            cursor.execute("SAVEPOINT cuotas")
            cursor.close()
        else:
            # Establece la conexión con la Base de Datos
            self.conexion = Op.conectar(self.datos_conexion)

        self.config_grilla_cuotas()
        self.configurar_combo_pagos()

        arch.connect_signals(self)

        self.estadocuotas(False)
        self.estadoguardar(False)

        if datos is not None:
            # Cuando se esta trabajando sobre una Factura
            self.obj("txt_fact").set_text(datos[0])
            self.obj("txt_timb").set_text(datos[1])
            self.obj("txt_total_fact").set_text(datos[2])
            # NO se puede elegir otra Factura
            self.obj("txt_fact").set_editable(False)
            self.obj("txt_timb").set_editable(False)
            self.obj("btn_factura").set_visible(False)

        self.focus_out_event(self.obj("txt_fact"), 0)
        self.fact_nro, self.fact_timb = self.obj("txt_fact"), self.obj("txt_timb")
        self.obj("txt_fact").grab_focus()

        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        if self.obj("btn_factura").get_visible():
            self.conexion.commit()
            self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()

    def on_btn_cancelar_clicked(self, objeto):
        if self.obj("btn_factura").get_visible():
            self.conexion.rollback()
            self.conexion.close()  # Finaliza la conexión
        else:
            cursor = self.conexion.cursor()
            cursor.execute("ROLLBACK TO SAVEPOINT cuotas")
            cursor.close()

        self.obj("ventana").destroy()

    def on_btn_factura_clicked(self, objeto):
        tabla = self.obj("grilla").get_model()

        if len(tabla) > 0:
            eleccion = Mens.pregunta_generico("Guardar Cambios",
            "¿Desea guardar los cambios que haya realizado en las Cuotas?")

            if eleccion:
                self.conexion.commit()
            else:
                self.conexion.rollback()

        if self.tabla == "cuentascobrar":
            from ventas.facturas import factura_buscar
            factura_buscar(self.datos_conexion, self, "idTipoFactura = 2")
        else:
            pass

    def verificacion(self, objeto):
        if len(self.obj("txt_fact").get_text()) == 0 or len(self.obj("txt_timb").get_text()) == 0:
            estado = False
        else:
            estado = True
        self.estadoguardar(estado)

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if self.obj("btn_factura").get_visible():
                    self.on_btn_factura_clicked(0)
        elif evento.keyval == 65293:
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if self.obj("btn_factura").get_visible():
            self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar la Factura.")

    def focus_out_event(self, objeto, evento):
        if len(self.obj("txt_fact").get_text()) == 0 or len(self.obj("txt_timb").get_text()) == 0:
            self.obj("barraestado").push(0, "")
        else:
            fact = self.obj("txt_fact").get_text()
            timb = self.obj("txt_timb").get_text()

            if self.tabla == "cuentaspagar":
                fact = "'" + fact + "'"
                tabla = "facturacompras_s"
            else:
                tabla = "facturaventas_s"

            conexion = Op.conectar(self.datos_conexion)
            cursor = Op.consultar(conexion, "Total", tabla, " WHERE " +
                "NroTimbrado = " + timb + " AND NroFactura = " + fact)
            datos = cursor.fetchall()
            cant = cursor.rowcount
            conexion.close()  # Finaliza la conexión

            if cant > 0:
                self.obj("txt_total_fact").set_text(str(datos[0][0]))
                self.obj("barraestado").push(0, "")
                self.cargar_grilla_cuotas()
            else:
                self.estadoguardar(False)
                self.obj("txt_fact").grab_focus()
                self.obj("barraestado").push(0, "El Nro. Factura introducido no es válido (NO EXISTE).")
                self.obj("txt_total_fact").set_text("")
                self.obj("txt_no_asignado").set_text("")

    def configurar_combo_pagos(self):
        lista = ListStore(str)
        self.obj("cmb_pago").set_model(lista)

        cell = CellRendererText()
        self.obj("cmb_pago").pack_start(cell, True)
        self.obj("cmb_pago").add_attribute(cell, 'text', 0)

        lista.clear()
        lista.append(["Mensual"])
        lista.append(["Quincenal"])
        lista.append(["Semanal"])

    def estadoguardar(self, estado):
        self.obj("hbuttonbox1").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)
        self.obj("btn_guardar").set_sensitive(estado)

    def estadocuotas(self, estado):
        self.obj("vbox1").set_visible(estado)
        self.obj("hbuttonbox2").set_visible(estado)

        self.obj("btn_factura").set_sensitive(not estado)
        self.obj("txt_fact").set_sensitive(not estado)
        self.obj("txt_timb").set_sensitive(not estado)
        self.obj("txt_total_fact").set_sensitive(not estado)
        self.obj("txt_no_asignado").set_sensitive(not estado)
        self.obj("btn_cancelar").set_sensitive(not estado)

##### Cuotas ###########################################################

    def config_grilla_cuotas(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Nro. Cuota", celda0, 0, True, 100, 100)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Fecha de Vencimiento", celda1, 1, True, 300, 400)
        col1.set_sort_column_id(3)  # Para ordenarse usa la fila 3
        col2 = Op.columnas("Monto", celda2, 2, True, 150, 200)
        col2.set_sort_column_id(2)

        self.obj("grilla").append_column(col0)
        self.obj("grilla").append_column(col1)
        self.obj("grilla").append_column(col2)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(1)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, float, str)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_cuotas(self):
        fact = self.obj("txt_fact").get_text()
        fact = "'" + fact + "'" if self.tabla == "cuentaspagar" else fact
        timb = self.obj("txt_timb").get_text()

        cursor = Op.consultar(self.conexion, "NroCuota, FechaVencimiento, " +
            "Monto", self.tabla, " WHERE NroTimbrado = " + timb +
            " AND NroFactura = " + fact + " ORDER BY NroCuota")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        monto = 0.0
        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], Cal.mysql_fecha(datos[i][1]),
                datos[i][2], str(datos[i][1])])
            monto += datos[i][2]

        fact = float(self.obj("txt_total_fact").get_text())
        self.obj("txt_total").set_text(str(monto))
        self.obj("txt_no_asignado").set_text(str(fact - monto))

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nueva_cuota_clicked(self, objeto):
        if float(self.obj("txt_no_asignado").get_text()) == 0:
            self.obj("barraestado").push(0, "No hay Monto disponible para asignar a una Nueva Cuota.")
        else:
            self.editando_cuota = False
            self.funcion_cuotas()

    def on_btn_modificar_cuota_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Modificar.")
        else:
            self.editando_cuota = True
            self.funcion_cuotas()

    def on_btn_eliminar_cuota_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            cuota = str(seleccion.get_value(iterador, 0))
            fecha = seleccion.get_value(iterador, 1)
            monto = str(seleccion.get_value(iterador, 2))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Eliminar.")
        else:
            fact = self.obj("txt_fact").get_text()
            fact = "'" + fact + "'" if self.tabla == "cuentaspagar" else fact
            timb = self.obj("txt_timb").get_text()

            eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
                "\nNro. Cuota: " + cuota + "\nFecha de Vencimiento: " + fecha +
                "\nMonto: " + monto)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, self.tabla, timb + ", " + fact + ", " + cuota)
                self.cargar_grilla_cuotas()
                self.estadoguardar(True)

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_cuota_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_cuota_clicked(0)

##### Agregar-Modificar Cuotas #########################################

    def funcion_cuotas(self):
        edit = "Agregar" if not self.editando_cuota else "Editar"
        self.obj("ventana").set_title(edit + " Cuota para Factura a Crédito")

        if self.editando_cuota:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.cond_cuota = str(seleccion.get_value(iterador, 0))
            fecha = seleccion.get_value(iterador, 1)
            self.monto = seleccion.get_value(iterador, 2)
            self.fecha_venc = seleccion.get_value(iterador, 3)

            self.obj("txt_d_00").set_text(self.cond_cuota)
            self.obj("txt_d_01").set_text(fecha)
            self.obj("txt_d_02").set_text(str(self.monto))

            self.obj("notebook").set_current_page(1)
            self.obj("notebook").set_show_tabs(False)
        else:
            self.obj("notebook").set_current_page(0)
            self.obj("notebook").set_show_tabs(True)
            self.obj("cmb_pago").set_active(0)

        self.obj("btn_guardar_cuota").set_sensitive(False)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        self.estadoguardar(False)
        self.estadocuotas(True)

    def on_btn_guardar_cuota_clicked(self, objeto):
        fact = self.obj("txt_fact").get_text()
        fact = "'" + fact + "'" if self.tabla == "cuentaspagar" else fact
        timb = self.obj("txt_timb").get_text()

        if self.obj("notebook").get_current_page() == 0:
            ini = int(Op.nuevoid(self.datos_conexion, self.tabla +
                " WHERE NroTimbrado = " + timb + " AND NroFactura = " + fact,
                "NroCuota"))

            resto = float(self.obj("txt_no_asignado").get_text())
            cant = float(self.obj("txt_i_00").get_text())
            monto = self.obj("txt_i_02").get_text()

            # Si cantidad es decimal, suma uno a la cantidad de cuotas
            if cant > int(cant):
                cant = int(cant) + ini + 1
            else:
                cant = int(cant) + ini

            # Valores Iniciales
            if self.pago == "Mensual":
                dia_venc = self.obj("txt_i_01_1").get_value_as_int()
                longitud_grilla = len(self.obj("grilla").get_model())

                if longitud_grilla == 0:  # Vacía
                    fecha = date.today()
                else:
                    conexion = Op.conectar(self.datos_conexion)
                    cursor = Op.consultar(conexion, "FechaVencimiento", self.tabla,
                        " WHERE NroTimbrado = " + timb + " AND NroFactura = " + fact +
                        " ORDER BY NroCuota DESC")
                    fecha = cursor.fetchall()[0][0]
                    conexion.close()  # Finaliza la conexión

                anho = fecha.strftime("%Y")
                mes = fecha.strftime("%m")
                dia = fecha.strftime("%d")

                if longitud_grilla == 0:  # Vacía
                    if dia_venc < int(dia):
                        mes, anho = Cal.mes_mas_uno(mes, anho)
                else:
                    if dia_venc <= int(dia):
                        mes, anho = Cal.mes_mas_uno(mes, anho)

                dia = Op.cadenanumeros(dia_venc, 2)
            else:
                periodo = 7 if self.pago == "Semanal" else 14

                anho = self.fecha_inic[0:4]
                mes = self.fecha_inic[5:7]
                dia = self.fecha_inic[8:10]

            # Carga de Datos
            for nro in range(ini, cant):
                if int(mes) == 2:
                    # Años bisiestos: 1900, (2000), 2100, 2200, 2300, (2400), 2500
                    if int(anho) % 4 == 0:  # Es Múltiplo de 4
                        dia_max = 29
                        if int(anho) % 100 == 0:  # Pero NO es múltiplo de 100
                            if int(anho) % 400 != 0:  # Excepto si es múltiplo de 400
                                dia_max = 28
                    else:
                        dia_max = 28
                elif int(mes) in (4, 6, 9, 11):
                    dia_max = 30
                else:
                    dia_max = 31

                if self.pago == "Mensual":
                    if int(dia) > dia_max:
                        dia = str(dia_max)

                fecha = "'" + anho + "-" + mes + "-" + dia + "'"
                monto = str(resto) if float(monto) > resto else monto
                resto -= float(monto)

                sql = timb + ", " + fact + ", " + str(nro) + ", " + fecha + ", " + monto
                Op.insertar(self.conexion, self.tabla, sql)

                if resto > 0:
                    # Modifica valores para proxima cuota
                    if self.pago == "Mensual":
                        dia = Op.cadenanumeros(int(dia_venc), 2)
                        mes, anho = Cal.mes_mas_uno(mes, anho)
                    else:
                        dia = str(int(dia) + periodo)
                        if int(dia) > dia_max:
                            dia = str(int(dia) - dia_max)
                            mes, anho = Cal.mes_mas_uno(mes, anho)
        else:
            nro = self.obj("txt_d_00").get_text()
            monto = self.obj("txt_d_02").get_text()

            sql = timb + ", " + fact + ", " + nro + ", '" + self.fecha_venc + "', " + monto

            if not self.editando_cuota:
                Op.insertar(self.conexion, self.tabla, sql)
            else:
                Op.modificar(self.conexion, self.tabla, self.cond_cuota + ", " + sql)

        self.cargar_grilla_cuotas()
        self.on_btn_cancelar_cuota_clicked(0)

    def on_btn_cancelar_cuota_clicked(self, objeto):
        self.limpiar_cuotas()

        self.obj("ventana").set_title("Cuentas por Facturas a Crédito")
        self.estadoguardar(True)
        self.estadocuotas(False)

    def on_btn_fecha_inicio_clicked(self, objeto):
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_i_01_2").set_text(lista[0])
            self.fecha_inic = lista[1]

    def on_btn_limpiar_fecha_inicio_clicked(self, objeto):
        self.obj("txt_i_01_2").set_text("")

    def on_btn_fecha_vencimiento_clicked(self, objeto):
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_d_01").set_text(lista[0])
            self.fecha_venc = lista[1]

    def on_btn_limpiar_fecha_vencimiento_clicked(self, objeto):
        self.obj("txt_d_01").set_text("")

    def on_notebook_change_current_page(self, objeto):
        self.verificacion_cuota(0)
        print("Cambiando NoteBook")

    def verificacion_cuota(self, objeto):
        if self.obj("notebook").get_current_page() == 0:  # Cuotas Iguales
            if len(self.obj("txt_i_00").get_text()) == 0 or len(self.obj("txt_i_02").get_text()) == 0:
                estado = False
            else:
                if Op.comprobar_numero(float, self.obj("txt_i_00"), "Cantidad de Cuotas", self.obj("barraestado")) \
                and Op.comprobar_numero(float, self.obj("txt_i_02"), "Monto de Cuota", self.obj("barraestado")):
                    estado = True
                else:
                    estado = False

        else:  # Cuotas Personalizadas
            if len(self.obj("txt_d_00").get_text()) == 0 or len(self.obj("txt_d_01").get_text()) == 0 \
            or len(self.obj("txt_d_02").get_text()) == 0:
                estado = False
            else:
                if Op.comprobar_numero(int, self.obj("txt_d_00"), "Nro. de Cuota", self.obj("barraestado")) \
                and Op.comprobar_numero(float, self.obj("txt_d_02"), "Monto de Cuota", self.obj("barraestado")):
                    estado = True
                else:
                    estado = False

        self.obj("btn_guardar_cuota").set_sensitive(estado)

    def on_cmb_pago_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()
        self.pago = model[active][0]

        self.obj("hbox61").set_visible(False)
        self.obj("hbox62").set_visible(False)

        if self.pago == "Mensual":
            self.obj("hbox61").set_visible(True)
        else:
            self.obj("hbox62").set_visible(True)

    def on_cuota_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_i_01_2"):
                    self.on_btn_fecha_inicio_clicked(0)
                elif objeto == self.obj("txt_d_01"):
                    self.on_btn_fecha_vencimiento_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.on_cuota_focus_out_event(objeto, 0)

    def on_cuota_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar una Fecha de Vencimiento.")

    def on_cuota_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
        else:
            if objeto == self.obj("txt_i_00"):
                if Op.comprobar_numero(float, objeto, "Cantidad de Cuotas", self.obj("barraestado")):
                    resto = float(self.obj("txt_no_asignado").get_text())
                    monto = str(round(resto / float(valor), 2))
                    self.obj("txt_i_02").set_text(monto)

            elif objeto == self.obj("txt_i_01_2"):
                self.obj("barraestado").push(0, "")

            elif objeto == self.obj("txt_i_02"):
                if Op.comprobar_numero(float, objeto, "Monto de Cuota", self.obj("barraestado")):
                    resto = float(self.obj("txt_no_asignado").get_text())
                    cantidad = str(round(resto / float(valor), 2))
                    self.obj("txt_i_00").set_text(cantidad)

            elif objeto == self.obj("txt_d_00"):
                Op.comprobar_numero(int, objeto, "Nro. de Cuota", self.obj("barraestado"))

            elif objeto == self.obj("txt_d_01"):
                self.obj("barraestado").push(0, "")

            elif objeto == self.obj("txt_d_02"):
                print("Comprueba")
                if Op.comprobar_numero(float, objeto, "Monto de Cuota", self.obj("barraestado")):
                    no_as = float(self.obj("txt_no_asignado").get_text())
                    total = float(self.obj("txt_total").get_text())

                    if self.editando_cuota:
                        disponible = no_as + self.monto
                    else:
                        disponible = no_as

                    if float(valor) > disponible:
                        self.obj("btn_guardar_cuota").set_sensitive(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "Monto de Cuota " +
                        "NO puede ser mayor a " + str(disponible) + ".")
                    else:
                        self.obj("barraestado").push(0, "")

    def limpiar_cuotas(self):
        self.obj("txt_i_00").set_text("")
        self.obj("cmb_pago").set_active(-1)
        self.obj("txt_i_01_1").set_value(1)
        self.obj("txt_i_01_2").set_text("")
        self.obj("txt_i_02").set_text("")

        self.obj("txt_d_00").set_text("")
        self.obj("txt_d_01").set_text("")
        self.obj("txt_d_02").set_text("")


class cuota_buscar:

    def __init__(self, v_or):
        self.origen = v_or

        arch = Op.archivo("buscador")
        self.obj = arch.get_object

        self.obj("ventana").set_title("Seleccione una Cuota a Cobrar")
        self.obj("ventana").set_default_size(950, 500)
        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        self.config_grilla_buscar()
        self.cargar_grilla_buscar()

        arch.connect_signals(self)
        self.obj("ventana").show()

    def on_btn_busq_seleccionar_clicked(self, objeto):
        seleccion, iterador = self.obj("grilla_buscar").get_selection().get_selected()
        cuota = str(seleccion.get_value(iterador, 2))
        monto = str(seleccion.get_value(iterador, 4))

        self.origen.cuota_nro.set_text(cuota)
        self.origen.cuota_monto.set_text(monto)

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
            self.on_btn_busq_seleccionar_clicked(0)

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

        col0 = Op.columnas("Nro. Timbrado", celda0, 0, True, 100, 150)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Nro. Factura", celda0, 1, True, 100, 150)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Nro. Cuota", celda0, 2, True, 100, 100)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Fecha de Vencimiento", celda1, 3, True, 300, 400)
        col3.set_sort_column_id(5)  # Para ordenarse usa la fila 5
        col4 = Op.columnas("Monto", celda2, 4, True, 150, 200)
        col4.set_sort_column_id(4)

        lista = [col0, col1, col2, col3, col4]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla_buscar").append_column(columna)

        self.obj("grilla_buscar").set_rules_hint(True)
        self.obj("grilla_buscar").set_search_column(1)
        self.obj("grilla_buscar").set_property('enable-grid-lines', 3)
        self.columna_buscar(1)

        lista = ListStore(int, int, int, str, float, str)
        self.obj("grilla_buscar").set_model(lista)
        self.obj("grilla_buscar").show()

    def cargar_grilla_buscar(self):
        if self.campo_buscar == "FechaVencimiento":
            opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
            " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
        else:
            opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
            " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

        conexion = Op.conectar(self.origen.datos_conexion)
        cursor = Op.consultar(conexion, "NroTimbrado, NroFactura, " +
            "NroCuota, FechaVencimiento, Monto", "cuentascobrar",
            opcion + " ORDER BY FechaVencimiento")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        lista = self.obj("grilla_buscar").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2],
                Cal.mysql_fecha(datos[i][3]), datos[i][4], str(datos[i][3])])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def columna_buscar(self, idcolumna):
        if idcolumna == 0:
            col, self.campo_buscar = "Nro. Timbrado", "NroTimbrado"
        elif idcolumna == 1:
            col, self.campo_buscar = "Nro. Factura", "NroFactura"
        elif idcolumna == 2:
            col, self.campo_buscar = "Nro. Cuota", "NroCuota"
        elif idcolumna == 5:
            col, self.campo_buscar = "Fecha de Vencimiento", "FechaVencimiento"
            self.obj("txt_buscar").set_editable(False)
            self.obj("hbox_fecha").set_visible(True)
        elif idcolumna == 4:
            col, self.campo_buscar = "Monto", "Monto"

        self.obj("label_buscar").set_text("Filtrar por " + col + ":")
