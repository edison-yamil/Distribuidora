#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import mensajes as Mens
from clases import operaciones as Op


class direcciones:

    def __init__(self, edit, estab, v_or):
        self.editando = self.editando_persona = edit
        self.establecimiento = estab
        self.origen = v_or

        cursor = self.origen.conexion.cursor()
        cursor.execute("SAVEPOINT direccion")
        cursor.close()

        arch = Op.archivo("abm_direcciones")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Direcciones")
        self.obj("btn_guardar").set_sensitive(False)

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_02").set_max_length(10)
        self.obj("txt_03").set_max_length(10)
        self.obj("txt_04").set_max_length(10)
        self.obj("txt_05").set_max_length(10)
        self.obj("txt_06").set_max_length(10)
        self.obj("txt_07").set_max_length(100)
        self.obj("txt_08").set_max_length(10)

        self.obj("txt_00").set_tooltip_text("Ingrese el Número de la Dirección de la Persona")
        self.obj("txt_01").set_tooltip_text("Ingrese el Código de la Dirección (general)")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el País donde se encuentra"))
        self.obj("txt_02_1").set_tooltip_text("Nombre del País")
        self.obj("txt_03").set_tooltip_text(Mens.usar_boton("la Ciudad donde se encuentra"))
        self.obj("txt_03_1").set_tooltip_text("Nombre del Departamento, Provincia, Estado")
        self.obj("txt_04").set_tooltip_text(Mens.usar_boton("la Ciudad donde se encuentra"))
        self.obj("txt_04_1").set_tooltip_text("Nombre de la Ciudad")
        self.obj("txt_05").set_tooltip_text(Mens.usar_boton("el Barrio donde se encuentra"))
        self.obj("txt_05_1").set_tooltip_text("Nombre del Barrio")
        self.obj("txt_06").set_tooltip_text("Ingrese el Nro. de Casa")
        self.obj("txt_07").set_tooltip_text("Ingrese algunas Observaciones acerca de la Dirección")
        self.obj("txt_08").set_tooltip_text(Mens.usar_boton("la Calle sobre la que se encuentra"))
        self.obj("txt_08_1").set_tooltip_text("Nombre de la Calle")
        self.obj("txt_02").grab_focus()

        self.txt_cod_pais, self.txt_des_pais = self.obj("txt_02"), self.obj("txt_02_1")
        self.txt_cod_dep, self.txt_des_dep = self.obj("txt_03"), self.obj("txt_03_1")
        self.txt_cod_ciu, self.txt_des_ciu = self.obj("txt_04"), self.obj("txt_04_1")
        self.txt_cod_bar, self.txt_des_bar = self.obj("txt_05"), self.obj("txt_05_1")
        self.txt_cod_cal, self.txt_des_cal = self.obj("txt_08"), self.obj("txt_08_1")

        Op.combos_config(self.origen.nav.datos_conexion,
            self.obj("cmb_tipo_calle"), "tipocalles", "idTipoCalle")
        arch.connect_signals(self)
        self.config_grilla_calle()

        if self.editando:
            if not self.establecimiento:
                seleccion, iterador = self.origen.obj("grilla_dir").get_selection().get_selected()
                self.idDirecPers = str(seleccion.get_value(iterador, 0))  # Nro. de Orden
                self.idDireccion = str(seleccion.get_value(iterador, 13))

                codpais = str(seleccion.get_value(iterador, 1))
                pais = seleccion.get_value(iterador, 2)
                coddepart = str(seleccion.get_value(iterador, 3))
                depart = seleccion.get_value(iterador, 4)
                codciudad = str(seleccion.get_value(iterador, 5))
                ciudad = seleccion.get_value(iterador, 6)
                codbarrio = str(seleccion.get_value(iterador, 7))
                barrio = seleccion.get_value(iterador, 8)

                nrocasa = seleccion.get_value(iterador, 10)
                obs = seleccion.get_value(iterador, 11)

                self.obj("txt_00").set_text(self.idDirecPers)
            else:
                self.idDireccion = str(self.origen.idDirec)

                cursor = Op.consultar(self.origen.conexion, "idPais, Pais, " +
                    "idDepartamento, Departamento, idCiudad, Ciudad, " +
                    "idBarrio, Barrio, NroCasa, Observaciones, idDireccion",
                    "direcciones_s", " WHERE idDireccion = " + self.idDireccion)
                datos = cursor.fetchall()
                print(datos)

                codpais, pais = str(datos[0][0]), datos[0][1]
                coddepart, depart = str(datos[0][2]), datos[0][3]
                codciudad, ciudad = str(datos[0][4]), datos[0][5]
                codbarrio, barrio = str(datos[0][6]), datos[0][7]
                nrocasa, obs = datos[0][8], datos[0][9]

            nrocasa = "" if nrocasa is None else str(nrocasa)
            obs = "" if obs is None else obs

            self.obj("txt_01").set_text(self.idDireccion)
            self.obj("txt_02").set_text(codpais)
            self.obj("txt_02_1").set_text(pais)
            self.obj("txt_03").set_text(coddepart)
            self.obj("txt_03_1").set_text(depart)
            self.obj("txt_04").set_text(codciudad)
            self.obj("txt_04_1").set_text(ciudad)
            self.obj("txt_05").set_text(codbarrio)
            self.obj("txt_05_1").set_text(barrio)

            self.obj("txt_06").set_text(nrocasa)
            self.obj("txt_07").set_text(obs)

            self.estadoedicion(True)
        else:
            if not self.establecimiento:
                self.obj("txt_00").set_text(Op.nuevoid(self.origen.nav.datos_conexion,
                    "personas_direcciones_s WHERE idPersona = " +
                    self.origen.obj("txt_00").get_text(), "idDireccionPer"))

            self.obj("txt_01").set_text(Op.nuevoid(self.origen.nav.datos_conexion,
                "direcciones_s", "idDireccion"))
            self.estadoedicion(False)

        if self.establecimiento:
            self.obj("hbox2").set_visible(False)
            self.obj("label2").set_property('width_request', 150)

        self.estadoedicion_calle(False)
        self.cargar_grilla_calle()

        if not self.establecimiento:
            self.origen.obj("grilla_dir").get_selection().unselect_all()
            self.origen.obj("barraestado").push(0, "")

        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_direccion()

        # Para Personas debe guardar en personas_direcciones y cargar una grilla
        if not self.establecimiento:
            self.origen.guardar_principal_personas()

            v0 = self.origen.obj("txt_00").get_text()
            v1 = self.obj("txt_00").get_text()
            v2 = self.obj("txt_01").get_text()
            v3 = "1" if self.obj("chk_principal").get_active() else "0"

            sql = v0 + ", " + v1 + ", " + v2 + ", " + v3

            if not self.editando_persona:
                Op.insertar(self.origen.conexion, "personas_direcciones", sql)
            else:
                Op.modificar(self.origen.conexion, "personas_direcciones",
                    self.idDirecPers + ", " + sql)

            self.origen.cargar_grilla_dir()

        else:  # Para Establecimientos debe cargar los campos de texto
            ciudad = self.obj("txt_04_1").get_text()
            nrocasa = self.obj("txt_06").get_text()
            nrocasa = "" if len(nrocasa) == 0 else ", Nº " + nrocasa

            direccion = self.obj("txt_09").get_text()
            direccion = ciudad if len(direccion) == 0 else ciudad + ", " + direccion + nrocasa

            self.origen.idDirec = int(self.obj("txt_01").get_text())
            self.origen.txt_des_dir.set_text(direccion)

        self.obj("ventana").destroy()

    def on_btn_cancelar_clicked(self, objeto):
        cursor = self.origen.conexion.cursor()
        cursor.execute("ROLLBACK TO SAVEPOINT direccion")
        cursor.close()

        self.obj("ventana").destroy()

    def on_btn_pais_clicked(self, objeto):
        from clases.llamadas import paises
        paises(self.origen.nav.datos_conexion, self)

    def on_btn_departamento_clicked(self, objeto):
        condicion = None if len(self.obj("txt_02_1").get_text()) == 0 \
        else self.obj("txt_02").get_text()

        from clases.llamadas import departamentos
        departamentos(self.origen.nav.datos_conexion, self, condicion)

    def on_btn_ciudad_clicked(self, objeto):
        condicion = None if len(self.obj("txt_03_1").get_text()) == 0 \
        else [self.obj("txt_02").get_text(), self.obj("txt_03").get_text()]

        from clases.llamadas import ciudades
        ciudades(self.origen.nav.datos_conexion, self, condicion)

    def on_btn_barrio_clicked(self, objeto):
        from clases.llamadas import barrios
        barrios(self.origen.nav.datos_conexion, self)

    def verificacion(self, objeto):
        if len(self.obj("txt_01").get_text()) == 0 or len(self.obj("txt_02").get_text()) == 0 \
        or len(self.obj("txt_03").get_text()) == 0 or len(self.obj("txt_04").get_text()) == 0 \
        or len(self.obj("txt_05").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_01"), "Cód. de Dirección", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Cód. de País", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_03"), "Cód. de Departamento", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_04"), "Cód. de Ciudad", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_05"), "Cód. de Barrio", self.obj("barraestado")):
                if len(self.obj("txt_06").get_text()) == 0:
                    if not self.establecimiento:  # Solo con personas
                        if len(self.obj("txt_00").get_text()) == 0:
                            estado = False
                        else:
                            estado = Op.comprobar_numero(int, self.obj("txt_00"),
                                "Cód. de Dirección", self.obj("barraestado"))
                    else:
                        estado = True
                else:
                    estado = Op.comprobar_numero(int, self.obj("txt_06"),
                        "Nro. de Casa", self.obj("barraestado"))
            else:
                estado = False
        self.direccion_guardada = False
        self.estadoedicion(estado)

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_02"):
                    self.on_btn_pais_clicked(0)
                elif objeto == self.obj("txt_03"):
                    self.on_btn_departamento_clicked(0)
                elif objeto == self.obj("txt_04"):
                    self.on_btn_ciudad_clicked(0)
                elif objeto == self.obj("txt_05"):
                    self.on_btn_barrio_clicked(0)
                elif objeto == self.obj("txt_08"):
                    self.on_btn_calle_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_02"):
            tipo = " País"
        elif objeto == self.obj("txt_03"):
            tipo = " Departamento"
        elif objeto == self.obj("txt_04"):
            tipo = "a Ciudad"
        elif objeto == self.obj("txt_05"):
            tipo = " Barrio"
        elif objeto == self.obj("txt_08"):
            tipo = "a Calle"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un" + tipo)

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_02"):
                self.obj("txt_02_1").set_text("")
            elif objeto == self.obj("txt_03"):
                self.obj("txt_03_1").set_text("")
            elif objeto == self.obj("txt_04"):
                self.obj("txt_04_1").set_text("")
            elif objeto == self.obj("txt_05"):
                self.obj("txt_05_1").set_text("")
            elif objeto == self.obj("txt_08"):
                self.obj("txt_08_1").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando_persona or valor != self.idDirecPers) and \
                Op.comprobar_numero(int, objeto, "Código", self.obj("barraestado")):
                    Op.comprobar_unique(self.origen.nav.datos_conexion,
                        "personas_direcciones_s", "idDireccionPer", valor +
                        " AND idPersona = " + self.origen.obj("txt_00").get_text(),
                        self.obj("txt_00"), self.estadoedicion, self.obj("barraestado"),
                        "El Número de Dirección introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                if (not self.editando or valor != self.idDireccion) and \
                Op.comprobar_numero(int, objeto, "Código", self.obj("barraestado")):
                    Op.comprobar_unique(self.origen.nav.datos_conexion,
                        "direcciones_s", "idDireccion", valor,
                        self.obj("txt_01"), self.estadoedicion, self.obj("barraestado"),
                        "El Código de Dirección introducido ya ha sido registado.")

            elif objeto == self.obj("txt_02"):
                self.buscar_foraneos(objeto, self.obj("txt_02_1"),
                    "País", "paises", "Nombre", "idPais", valor)

            elif objeto == self.obj("txt_03") and len(self.obj("txt_02").get_text()) > 0:
                self.buscar_foraneos(objeto, self.obj("txt_03_1"),
                    "Departamento", "departamentos_s", "Nombre", "idDepartamento", valor,
                    " AND idPais = " + self.obj("txt_02").get_text())

            elif objeto == self.obj("txt_04") and len(self.obj("txt_03").get_text()) > 0 \
            and len(self.obj("txt_02").get_text()) > 0:
                self.buscar_foraneos(objeto, self.obj("txt_04_1"),
                    "Ciudad", "ciudades_s", "Nombre", "idCiudad", valor,
                    " AND idDepartamento = " + self.obj("txt_03").get_text() +
                    " AND idPais = " + self.obj("txt_02").get_text())

            elif objeto == self.obj("txt_05"):
                self.buscar_foraneos(objeto, self.obj("txt_05_1"),
                    "Barrio", "barrios", "Nombre", "idBarrio", valor)

            elif objeto == self.obj("txt_08"):
                self.buscar_foraneos(objeto, self.obj("txt_08_1"),
                    "Calle", "calles", "Nombre", "idCalle", valor)

    def buscar_foraneos(self, objeto, companero, nombre, tabla, campo_busq, campo_id, valor, condicion=""):
        if Op.comprobar_numero(int, objeto, "Cód. de " + nombre, self.obj("barraestado")):
            conexion = Op.conectar(self.origen.nav.datos_conexion)
            cursor = Op.consultar(conexion, campo_busq, tabla,
                " WHERE " + campo_id + " = " + valor + condicion)
            datos = cursor.fetchall()
            cant = cursor.rowcount
            conexion.close()  # Finaliza la conexión

            if cant > 0:
                companero.set_text(datos[0][0])
                self.obj("barraestado").push(0, "")

                if objeto == self.obj("txt_02"):  # País
                    self.focus_out_event(self.obj("txt_03"), 0)

                elif objeto == self.obj("txt_03"):  # Departamento
                    self.focus_out_event(self.obj("txt_04"), 0)

                if objeto != self.obj("txt_08"):
                    self.verificacion(0)

            else:
                if objeto == self.obj("txt_08"):
                    self.obj("btn_guardar_calle").set_sensitive(False)
                else:
                    self.estadoedicion(False)

                objeto.grab_focus()
                self.obj("barraestado").push(0, "El Cód. de " + nombre + " no es válido.")
                companero.set_text("")

    def guardar_direccion(self):
        if not self.direccion_guardada:
            v1 = self.obj("txt_01").get_text()
            v2 = self.obj("txt_02").get_text()
            v3 = self.obj("txt_03").get_text()
            v4 = self.obj("txt_04").get_text()
            v5 = self.obj("txt_05").get_text()
            v6 = self.obj("txt_06").get_text()
            v7 = self.obj("txt_07").get_text()

            v6 = "NULL" if len(v6) == 0 else v6
            v7 = "NULL" if len(v7) == 0 else "'" + v7 + "'"

            # Guardar en Direcciones
            sql = v1 + ", " + v2 + ", " + v3 + ", " + v4 + ", " + v5 + ", "  + v6 + ", " + v7

            if not self.editando:
                Op.insertar(self.origen.conexion, "direcciones", sql)
            else:
                Op.modificar(self.origen.conexion, "direcciones", self.idDireccion + ", " + sql)

            self.idDireccion = v1  # Nuevo idDireccion original

            self.editando = True
            self.direccion_guardada = True

    def estadoedicion(self, estado):
        self.obj("hbuttonbox1").set_sensitive(estado)
        self.obj("grilla_calle").set_sensitive(estado)
        self.obj("btn_guardar").set_sensitive(estado)

##### Calles ###########################################################

    def config_grilla_calle(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)

        col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Nombre", celda1, 1, True, 200, 300)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Cód. Tipo Calle", celda1, 2, True, 100, 150)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Tipo de Calle", celda1, 3, True, 100, 150)
        col3.set_sort_column_id(3)

        lista = [col0, col1, col2, col3]
        for columna in lista:
            self.obj("grilla_calle").append_column(columna)

        self.obj("grilla_calle").set_rules_hint(True)
        self.obj("grilla_calle").set_search_column(1)
        self.obj("grilla_calle").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, int, str)
        self.obj("grilla_calle").set_model(lista)
        self.obj("grilla_calle").show()

    def cargar_grilla_calle(self):
        cursor = Op.consultar(self.origen.conexion, "idCalle, Calle, " +
            "idTipoCalle, TipoCalle, Abreviatura, DireccionCalle",
            "direcciones_calles_s", " WHERE idDireccion = " +
            self.obj("txt_01").get_text() + " ORDER BY idTipoCalle")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        vistaprevia = ""
        lista = self.obj("grilla_calle").get_model()
        lista.clear()

        for i in range(0, cant):
            abreviatura = "" if datos[i][4] is None else " (" + datos[i][4] + ")"
            lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3] + abreviatura])
            vistaprevia += " " + datos[i][5]
        self.obj("txt_09").set_text(vistaprevia)

        cant = str(cant) + " calle encontrada." if cant == 1 \
            else str(cant) + " calles encontradas."
        self.obj("barraestado").push(0, cant)

    def on_btn_nueva_calle_clicked(self, objeto):
        self.editando_calle = False
        self.funcion_calles()

    def on_btn_modificar_calle_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla_calle").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Calles. Luego presione Modificar Calle.")
        else:
            self.editando_calle = True
            self.funcion_calles()

    def on_btn_eliminar_calle_clicked(self, objeto):
        self.guardar_direccion()

        try:
            seleccion, iterador = self.obj("grilla_calle").get_selection().get_selected()
            codcalle = str(seleccion.get_value(iterador, 0))
            calle = seleccion.get_value(iterador, 1)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Calles. Luego presione Eliminar Calle.")
        else:
            iddir = self.obj("txt_01").get_text()

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Cód. Calle: " + codcalle + "\nCalle: " + calle)

            self.obj("grilla_calle").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.origen.conexion, "direcciones_calles", iddir + ", " + codcalle)
                self.cargar_grilla_calle()

    def on_grilla_calle_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_calle_clicked(0)

    def on_grilla_calle_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_calle_clicked(0)

##### Agregar-Modificar Calles #########################################

    def funcion_calles(self):
        self.guardar_direccion()

        if self.editando_calle:
            seleccion, iterador = self.obj("grilla_calle").get_selection().get_selected()
            self.calle = str(seleccion.get_value(iterador, 0))
            nombre = seleccion.get_value(iterador, 1)
            tipocalle = seleccion.get_value(iterador, 2)

            self.obj("txt_08").set_text(self.calle)
            self.obj("txt_08_1").set_text(nombre)

            # Asignación de Tipo de Calle en Combo
            model, i = self.obj("cmb_tipo_calle").get_model(), 0
            while model[i][0] != tipocalle: i += 1
            self.obj("cmb_tipo_calle").set_active(i)

        else:
            self.obj("txt_08").set_text("")
            self.obj("txt_08_1").set_text("")
            self.obj("cmb_tipo_calle").set_active(0)

        self.obj("grilla_calle").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        self.obj("btn_guardar_calle").set_sensitive(False)
        self.estadoedicion_calle(True)
        self.estadoedicion(False)

    def on_btn_guardar_calle_clicked(self, objeto):
        self.guardar_direccion()

        v1 = self.obj("txt_01").get_text()
        v2 = self.obj("txt_08").get_text()

        sql = v1 + ", " + v2 + ", " + str(self.idTipoCalle)

        if not self.editando_calle:
            Op.insertar(self.origen.conexion, "direcciones_calles", sql)
        else:
            Op.modificar(self.origen.conexion, "direcciones_calles", self.calle + ", " + sql)

        self.on_btn_cancelar_calle_clicked(0)
        self.cargar_grilla_calle()

    def on_btn_cancelar_calle_clicked(self, objeto):
        self.estadoedicion_calle(False)
        self.estadoedicion(True)

    def on_btn_calle_clicked(self, objeto):
        from clases.llamadas import calles
        calles(self.origen.nav.datos_conexion, self)

    def verificacion_calle(self, objeto):
        if len(self.obj("txt_08").get_text()) == 0:
            estado = False
        else:
            estado = Op.comprobar_numero(int, self.obj("txt_08"),
                "Cód. de Calle", self.obj("barraestado"))
        self.obj("btn_guardar_calle").set_sensitive(estado)

    def on_cmb_tipo_calle_changed(self, objeto):
        model = self.obj("cmb_tipo_calle").get_model()
        active = self.obj("cmb_tipo_calle").get_active()

        if active > -1:
            self.idTipoCalle = model[active][0]
            self.verificacion_calle(0)
        else:
            self.obj("barraestado").push(0, "No existen registros de Tipos de Calles en el Sistema.")

    def estadoedicion_calle(self, estado):
        self.obj("vbox1").set_visible(estado)
        self.obj("hbuttonbox2").set_visible(estado)

        self.obj("hbox1").set_sensitive(not estado)
        self.obj("hbox4").set_sensitive(not estado)
        self.obj("hbox5").set_sensitive(not estado)
        self.obj("hbox6").set_sensitive(not estado)
        self.obj("hbox7").set_sensitive(not estado)

        self.obj("hbox8").set_visible(not estado)
        self.obj("hbox9").set_visible(not estado)

        estab = not estado if not self.establecimiento else False
        self.obj("hbox10").set_visible(estab)

        self.obj("btn_cancelar").set_sensitive(not estado)
