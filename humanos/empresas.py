#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import mensajes as Mens
from clases import operaciones as Op
from registros import establecimientos


class funcion_abm:

    def __init__(self, edit, origen):
        self.editando = edit
        self.nav = origen

        # Necesario para Establecimientos
        self.datos_conexion = self.nav.datos_conexion

        arch = Op.archivo("rrhh_empresas")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de " + self.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_02").set_max_length(10)
        self.obj("txt_03").set_max_length(12)
        self.obj("txt_04").set_max_length(10)
        self.obj("txt_05").set_max_length(50)
        self.obj("txt_06").set_max_length(50)

        self.obj("txt_m_01").set_max_length(100)
        self.obj("txt_m_02").set_max_length(100)
        self.obj("txt_a_00").set_max_length(10)
        self.obj("txt_a_01").set_max_length(100)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código de la Empresa")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("al Propietario de la Empresa"))
        self.obj("txt_01_1").set_tooltip_text("Nombre y Apellido del Propietario")
        self.obj("txt_01_2").set_tooltip_text("Dirección Principal del Propietario")
        self.obj("txt_01_3").set_tooltip_text("Teléfono Principal del Propietario")
        self.obj("txt_02").set_tooltip_text("Ingrese el R.U.C. de la Empresa")
        self.obj("txt_02_1").set_tooltip_text("Ingrese el Dígito Verificador")
        self.obj("txt_03").set_tooltip_text("Ingrese el Nro. Patronal del Instituto de Previsión Social (IPS)")
        self.obj("txt_04").set_tooltip_text("Ingrese el Nro. Patronal del Ministerio de Justicia y Trabajo (MJT)")
        self.obj("txt_05").set_tooltip_text("Ingrese la Razón Social de la Empresa")
        self.obj("txt_06").set_tooltip_text("Ingrese el Nombre de Fantasía de la Empresa")
        self.obj("txt_01").grab_focus()

        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_medio"),
            "tipomediocontactos", "idTipoMedioContacto")

        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_01_2"), self.obj("txt_01_3")
        self.txt_cod_act, self.txt_des_act = self.obj("txt_a_00"), self.obj("txt_a_00_1")

        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            codprop = str(seleccion.get_value(iterador, 4))
            prop = seleccion.get_value(iterador, 6)
            direccion = seleccion.get_value(iterador, 7)
            telefono = seleccion.get_value(iterador, 8)
            ruc = seleccion.get_value(iterador, 1)[:-2]  # Quita el dígito verificador
            verif = seleccion.get_value(iterador, 11)
            ips = seleccion.get_value(iterador, 9)
            mjt = str(seleccion.get_value(iterador, 10))
            social = seleccion.get_value(iterador, 2)
            fantasia = seleccion.get_value(iterador, 3)

            direccion = "" if direccion is None else direccion
            telefono = "" if telefono is None else telefono

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(codprop)
            self.obj("txt_01_1").set_text(prop)
            self.obj("txt_01_2").set_text(direccion)
            self.obj("txt_01_3").set_text(telefono)
            self.obj("txt_02").set_text(ruc)
            self.obj("txt_02_1").set_value(verif)
            self.obj("txt_03").set_text(ips)
            self.obj("txt_04").set_text(mjt)
            self.obj("txt_05").set_text(social)
            self.obj("txt_06").set_text(fantasia)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))

        self.conexion = Op.conectar(self.nav.datos_conexion)
        self.principal_guardado = True

        self.estadoedicion_medio_contacto(False)
        self.estadoedicion_actividad(False)

        self.config_grilla_establecimiento()
        self.cargar_grilla_establecimiento()
        self.config_grilla_medio()
        self.cargar_grilla_medio()
        self.config_grilla_actividad()
        self.cargar_grilla_actividad()

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_principal_empresas()
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def on_btn_propietario_clicked(self, objeto):
        from clases.llamadas import personas
        personas(self.nav.datos_conexion, self, "Empresa = 0")

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0 or len(self.obj("txt_03").get_text()) == 0 \
        or len(self.obj("txt_04").get_text()) == 0 or len(self.obj("txt_05").get_text()) == 0 \
        or len(self.obj("txt_06").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Cód. de Empresa", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Cód. de Propietario o Representante Legal", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Nro. de Documento de Identidad", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_04"), "Nro. Patronal del MJT", self.obj("barraestado")):
                estado = True
            else:
                estado = False

        self.principal_guardado = False
        self.estadoedicion(estado)

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_01"):
                    self.on_btn_propietario_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un Propietario o Representante Legal.")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_01"):
                self.obj("txt_01_1").set_text("")
                self.obj("txt_01_2").set_text("")
                self.obj("txt_01_3").set_text("")
            elif objeto == self.obj("txt_02"):
                self.obj("txt_02_1").set_value(0)
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) and \
                Op.comprobar_numero(int, objeto, "Código", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion, "empresas_s",
                        self.nav.campoid, valor, self.obj("txt_00"),
                        self.estadoedicion, self.obj("barraestado"),
                        "El Código introducido ya ha sido registado.")

            if objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Propietario o Representante Legal", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "idPersona, NombreApellido, " +
                        "DireccionPrincipal, TelefonoPrincipal", "personafisicas_s",
                        " WHERE idPersona = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        direccion = "" if datos[0][2] is None else datos[0][2]
                        telefono = "" if datos[0][3] is None else datos[0][3]

                        self.obj("txt_01_1").set_text(datos[0][1])
                        self.obj("txt_01_2").set_text(direccion)
                        self.obj("txt_01_3").set_text(telefono)

                        self.obj("barraestado").push(0, "")
                        self.verificacion(0)
                    else:
                        self.estadoedicion(False)
                        self.obj("barraestado").push(0, "El Cód. de Propietario o Representante Legal no es válido.")
                        self.obj("txt_01_1").set_text("")
                        self.obj("txt_01_2").set_text("")
                        self.obj("txt_01_3").set_text("")

            elif objeto == self.obj("txt_02"):
                pass

    def guardar_principal_empresas(self):
        # Guardar Encabezado
        if not self.principal_guardado:
            v0 = self.obj("txt_00").get_text()  # idEmpresa
            v1 = self.obj("txt_01").get_text()  # idPropietario
            v2 = self.obj("txt_02").get_text()
            v3 = str(self.obj("txt_02_1").get_value_as_int())
            v4 = self.obj("txt_03").get_text()  # IPS
            v5 = self.obj("txt_04").get_text()  # MJT
            v6 = self.obj("txt_05").get_text()
            v7 = self.obj("txt_06").get_text()

            sql = v0 + ", " + v1 + ", " + v2 + ", " + v3 + ", '" + v4 + "'," + \
                " " + v5 + ", '" + v6 + "', '" + v7 + "'"

            if not self.editando:
                Op.insertar(self.conexion, self.nav.tabla, sql)
            else:
                Op.modificar(self.conexion, self.nav.tabla, self.cond + ", " + sql)

            self.cond = v0  # Nuevo idEmpresa original
            self.principal_guardado = self.editando = True

    def estadoedicion(self, estado):
        self.obj("vbox4").set_sensitive(estado)
        self.obj("vbox5").set_sensitive(estado)
        self.obj("vbox6").set_sensitive(estado)
        self.obj("btn_guardar").set_sensitive(estado)

    def estadoedicion_pestanas(self, estado, origen):
        self.obj("box1").set_sensitive(estado)
        self.obj("box2").set_sensitive(estado)
        self.obj("box3").set_sensitive(estado)

        if origen != 0:
            self.obj("vbox5").set_sensitive(estado)
        elif origen != 1:
            self.obj("vbox6").set_sensitive(estado)

        self.obj("vbox4").set_sensitive(estado)
        self.obj("btn_guardar").set_sensitive(estado)

#### Establecimientos y Direcciones ####################################

    def config_grilla_establecimiento(self):
        establecimientos.config_grilla(self, True)

    def cargar_grilla_establecimiento(self):
        cursor = Op.consultar(self.conexion, "NroEstablecimiento, Nombre, " +
            "NroDocumento, RazonSocial, Ciudad, Barrio, Direccion, " +
            "NroTelefono, Activo, idEmpresa, idDireccion", "establecimientos_s",
            " WHERE idEmpresa = " + self.obj("txt_00").get_text() +
            " ORDER BY NroEstablecimiento")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
                datos[i][4], datos[i][5], datos[i][6], datos[i][7], datos[i][8],
                datos[i][9], datos[i][10]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_establecimiento_clicked(self, objeto):
        self.guardar_principal_empresas()
        establecimientos.funcion_abm(False, self, True)

    def on_btn_modificar_establecimiento_clicked(self, objeto):
        self.guardar_principal_empresas()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Establecimientos. Luego presione Modificar Dirección.")
        else:
            establecimientos.funcion_abm(True, self, True)

    def on_btn_eliminar_establecimiento_clicked(self, objeto):
        self.guardar_principal_empresas()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            valor0 = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Establecimientos. Luego presione Eliminar Dirección.")
        else:
            valor1 = seleccion.get_value(iterador, 1)
            valor2 = seleccion.get_value(iterador, 3)
            valor3 = seleccion.get_value(iterador, 6)

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Nro. de Establecimiento: " + valor0 + "\nNombre: " + valor1 +
                "\nDirección: " + valor3 + "\nEmpresa: " + valor2)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "establecimientos", valor0)
                self.cargar_grilla_establecimiento()

    def on_grilla_estab_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_establecimiento_clicked(0)

    def on_grilla_estab_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_establecimiento_clicked(0)

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla").set_search_column(i)

#### Medios de Contacto ################################################

    def config_grilla_medio(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)

        col0 = Op.columnas("Número", celda0, 0, True, 100, 150)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Cód. Tipo Medio", celda0, 1, True, 100, 150)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Tipo de Medio de Contacto", celda1, 2, True, 220, 300)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Descripción", celda1, 3, True, 200, 300)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Observaciones", celda1, 4, True, 200)
        col4.set_sort_column_id(4)

        lista = [col0, col1, col2, col3, col4]
        for columna in lista:
            self.obj("grilla_medio").append_column(columna)

        self.obj("grilla_medio").set_rules_hint(True)
        self.obj("grilla_medio").set_search_column(1)
        self.obj("grilla_medio").set_property('enable-grid-lines', 3)

        lista = ListStore(int, int, str, str, str)
        self.obj("grilla_medio").set_model(lista)
        self.obj("grilla_medio").show()

    def cargar_grilla_medio(self):
        cursor = Op.consultar(self.conexion, "idTipoMedioContacto, " +
            "TipoMedioContacto, Descripcion, Observaciones, idEmpresa",
            "empresas_mediocontactos_s",
            " WHERE idEmpresa = " + self.obj("txt_00").get_text())
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla_medio").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([i + 1, datos[i][0], datos[i][1], datos[i][2], datos[i][3]])

        cant = str(cant) + " medio de contacto encontrado." if cant == 1 \
            else str(cant) + " medios de contactos encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_medio_clicked(self, objeto):
        self.editando_medio_contacto = False
        self.funcion_medio_contacto()

    def on_btn_modificar_medio_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla_medio").get_selection().get_selected()
            self.cond_medio_contacto = seleccion.get_value(iterador, 1)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Medios de Contacto. Luego presione Modificar.")
        else:
            self.editando_medio_contacto = True
            self.funcion_medio_contacto()

    def on_btn_eliminar_medio_clicked(self, objeto):
        self.guardar_principal_empresas()

        try:
            seleccion, iterador = self.obj("grilla_medio").get_selection().get_selected()
            valor1 = str(seleccion.get_value(iterador, 1))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Medios de Contacto. Luego presione Eliminar.")
        else:
            valor2 = seleccion.get_value(iterador, 2)
            valor3 = seleccion.get_value(iterador, 3)
            idempr = self.obj("txt_00").get_text()

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Medio de Contacto: " + valor2 + "\nDescripción: " + valor3)

            self.obj("grilla_medio").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "empresas_mediocontactos", idempr + ", " + valor1)
                self.cargar_grilla_medio()

    def on_grilla_medio_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_medio_clicked(0)

    def on_grilla_medio_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_medio_clicked(0)

    def estadoedicion_medio_contacto(self, estado):
        self.obj("buttonbox_medio1").set_sensitive(not estado)
        self.obj("grilla_medio").set_sensitive(not estado)

        self.obj("box4").set_visible(estado)
        self.obj("buttonbox_medio2").set_visible(estado)

#### Agregar-Editar Medios de Contacto #################################

    def funcion_medio_contacto(self):
        self.guardar_principal_empresas()

        if self.editando_medio_contacto:
            seleccion, iterador = self.obj("grilla_medio").get_selection().get_selected()
            des = seleccion.get_value(iterador, 3)
            obs = seleccion.get_value(iterador, 4)
            obs = "" if obs is None else obs

            self.obj("txt_m_01").set_text(des)
            self.obj("txt_m_02").set_text(obs)

            # Asignación de Tipo de Medio de Contacto en Combo
            model, i = self.obj("cmb_medio").get_model(), 0
            while model[i][0] != self.cond_medio_contacto: i += 1
            self.obj("cmb_medio").set_active(i)
        else:
            self.obj("cmb_medio").set_active(0)
            self.on_cmb_medio_changed(self.obj("cmb_medio"))

        self.estadoedicion_medio_contacto(True)
        self.estadoedicion_pestanas(False, 0)

        self.obj("btn_guardar_medio").set_sensitive(False)
        self.obj("grilla_medio").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

    def on_btn_guardar_medio_clicked(self, objeto):
        self.guardar_principal_empresas()

        v0 = self.obj("txt_00").get_text()  # idEmpresa
        v1 = self.obj("txt_m_01").get_text()

        v2 = self.obj("txt_m_02").get_text()
        v2 = "NULL" if len(v2) == 0 else "'" + v2 + "'"

        sql = v0 + ", " + str(self.idTipoMedioContacto) + ", '" + v1 + "', " + v2

        if not self.editando_medio_contacto:
            Op.insertar(self.conexion, "empresas_mediocontactos", sql)
        else:
            Op.modificar(self.conexion, "empresas_mediocontactos",
                str(self.cond_medio_contacto) + ", " + sql)

        self.on_btn_cancelar_medio_clicked(0)
        self.cargar_grilla_medio()

    def on_btn_cancelar_medio_clicked(self, objeto):
        self.estadoedicion_medio_contacto(False)
        self.estadoedicion_pestanas(True, 0)

        self.obj("cmb_medio").set_active(-1)
        self.obj("txt_m_01").set_text("")
        self.obj("txt_m_02").set_text("")

    def on_cmb_medio_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            empresa = self.obj("txt_00").get_text()
            condicion = "" if not self.editando_medio_contacto else \
            " AND idTipoMedioContacto <> " + str(self.cond_medio_contacto)

            cursor = Op.consultar(self.conexion, "Descripcion",
                "empresas_mediocontactos_s", " WHERE idEmpresa = " + empresa +
                " AND idTipoMedioContacto = " + str(model[active][0]) + condicion)
            datos = cursor.fetchall()
            cant = cursor.rowcount

            if cant > 0:
                self.obj("barraestado").push(0, "Este Tipo de Medio de Contacto ya fue registrado.")
                self.obj("btn_guardar_medio").set_sensitive(False)
            else:
                self.idTipoMedioContacto = model[active][0]
                self.verificacion_medio(0)
        else:
            self.obj("barraestado").push(0, "No existen registros de Tipos de Medios de Contacto en el Sistema.")

    def verificacion_medio(self, objeto):
        estado = False if len(self.obj("txt_m_01").get_text()) == 0 else True
        self.obj("btn_guardar_medio").set_sensitive(estado)

#### Actividades Económicas ############################################

    def config_grilla_actividad(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)

        col0 = Op.columnas("Número", celda0, 0, True, 100, 150)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Cód. CIIU", celda0, 1, True, 100, 150)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Actividad Económica", celda1, 2, True, 220, 300)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Observaciones", celda1, 3, True, 200, -1)
        col3.set_sort_column_id(3)
        col4 = Op.columna_active("Principal", 4)
        col4.set_sort_column_id(4)

        lista = [col0, col1, col2, col3, col4]
        for columna in lista:
            self.obj("grilla_actividad").append_column(columna)

        self.obj("grilla_actividad").set_rules_hint(True)
        self.obj("grilla_actividad").set_search_column(1)
        self.obj("grilla_actividad").set_property('enable-grid-lines', 3)

        lista = ListStore(int, int, str, str, int)
        self.obj("grilla_actividad").set_model(lista)
        self.obj("grilla_actividad").show()

    def cargar_grilla_actividad(self):
        cursor = Op.consultar(self.conexion, "idActividadEconomica, " +
            "ActividadEconomica, Observaciones, Principal, idEmpresa",
            "empresas_actividadeseconomicas_s",
            " WHERE idEmpresa = " + self.obj("txt_00").get_text())
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla_actividad").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([i + 1, datos[i][0], datos[i][1], datos[i][2], datos[i][3]])

        cant = str(cant) + " actividad económica encontrada." if cant == 1 \
            else str(cant) + " actividades económicas encontradas."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_actividad_clicked(self, objeto):
        self.editando_actividad = False
        self.funcion_actividad()

    def on_btn_modificar_actividad_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla_actividad").get_selection().get_selected()
            self.cond_actividad = seleccion.get_value(iterador, 1)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Actividades Económicas. Luego presione Modificar.")
        else:
            self.editando_actividad = True
            self.funcion_actividad()

    def on_btn_eliminar_actividad_clicked(self, objeto):
        self.guardar_principal_empresas()

        try:
            seleccion, iterador = self.obj("grilla_actividad").get_selection().get_selected()
            valor1 = str(seleccion.get_value(iterador, 1))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Actividades Económicas. Luego presione Eliminar.")
        else:
            valor2 = seleccion.get_value(iterador, 2)
            idempr = self.obj("txt_00").get_text()

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Cód. CIIU: " + valor1 + "\nActividad Económica: " + valor2)

            self.obj("grilla_actividad").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "empresas_actividadeseconomicas", idempr + ", " + valor1)
                self.cargar_grilla_actividad()

    def on_grilla_actividad_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_actividad_clicked(0)

    def on_grilla_actividad_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_actividad_clicked(0)

    def estadoedicion_actividad(self, estado):
        self.obj("buttonbox_actividad1").set_sensitive(not estado)
        self.obj("grilla_actividad").set_sensitive(not estado)

        self.obj("box5").set_visible(estado)
        self.obj("buttonbox_actividad2").set_visible(estado)

#### Agregar-Editar Actividades Económicas #############################

    def funcion_actividad(self):
        self.guardar_principal_empresas()

        if self.editando_actividad:
            seleccion, iterador = self.obj("grilla_actividad").get_selection().get_selected()
            des = seleccion.get_value(iterador, 2)
            obs = seleccion.get_value(iterador, 3)
            pri = seleccion.get_value(iterador, 4)

            obs = "" if obs is None else obs
            pri = True if pri == 1 else False

            self.obj("txt_a_00").set_text(str(self.cond_actividad))
            self.obj("txt_a_00_1").set_text(des)
            self.obj("txt_a_01").set_text(obs)
            self.obj("chk_actividad").set_active(pri)

        self.estadoedicion_actividad(True)
        self.estadoedicion_pestanas(False, 1)

        self.obj("btn_guardar_actividad").set_sensitive(False)
        self.obj("grilla_actividad").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

    def on_btn_guardar_actividad_clicked(self, objeto):
        self.guardar_principal_empresas()

        v0 = self.obj("txt_00").get_text()  # idEmpresa
        v1 = self.obj("txt_a_00").get_text()
        v2 = self.obj("txt_a_01").get_text()

        v2 = "NULL" if len(v2) == 0 else "'" + v2 + "'"
        v3 = "1" if self.obj("chk_actividad").get_active() else "0"

        sql = v0 + ", " + v1 + ", " + v2 + ", " + v3

        if not self.editando_actividad:
            Op.insertar(self.conexion, "empresas_actividadeseconomicas", sql)
        else:
            Op.modificar(self.conexion, "empresas_actividadeseconomicas",
                str(self.cond_actividad) + ", " + sql)

        self.on_btn_cancelar_actividad_clicked(0)
        self.cargar_grilla_actividad()

    def on_btn_cancelar_actividad_clicked(self, objeto):
        self.estadoedicion_actividad(False)
        self.estadoedicion_pestanas(True, 1)

        self.obj("txt_a_00").set_text("")
        self.obj("txt_a_00_1").set_text("")
        self.obj("txt_a_01").set_text("")
        self.obj("chk_actividad").set_active(False)

    def on_btn_actividad_clicked(self, objeto):
        from clases.llamadas import actividadeseconomicas
        actividadeseconomicas(self.nav.datos_conexion, self)

    def verificacion_actividad(self, objeto):
        if len(self.obj("txt_a_00").get_text()) == 0:
            estado = False
        else:
            estado = Op.comprobar_numero(int, self.obj("txt_a_00"),
                "Cód. de Actividad Económica", self.obj("barraestado"))
        self.obj("btn_guardar_actividad").set_sensitive(estado)

    def on_actividad_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_actividad_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.on_actividad_focus_out_event(objeto, 0)

    def on_actividad_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar una Actividad Económica.")

    def on_actividad_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            self.obj("txt_a_00_1").set_text("")
        else:
            if Op.comprobar_numero(int, objeto, "Cód. de Actividad Económica", self.obj("barraestado")):
                conexion = Op.conectar(self.nav.datos_conexion)
                cursor = Op.consultar(conexion, "Descripcion",
                    "actividadeseconomicas", " WHERE idActividadEconomica = " + valor)
                datos = cursor.fetchall()
                cant = cursor.rowcount
                conexion.close()  # Finaliza la conexión

                if cant > 0:
                    self.obj("txt_a_00_1").set_text(datos[0][0])

                    empresa = self.obj("txt_00").get_text()
                    condicion = "" if not self.editando_actividad else \
                    " AND idActividadEconomica <> " + str(self.cond_actividad)

                    cursor = Op.consultar(self.conexion, "idActividadEconomica",
                        "empresas_actividadeseconomicas_s", " WHERE idEmpresa = " + empresa +
                        " AND idActividadEconomica = " + valor + condicion)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount

                    if cant > 0:
                        self.obj("barraestado").push(0, "Esta Actividad Económica ya fue registrada.")
                        self.obj("btn_guardar_actividad").set_sensitive(False)
                    else:
                        self.obj("barraestado").push(0, "")
                        self.verificacion_actividad(0)
                else:
                    self.obj("btn_guardar_actividad").set_sensitive(False)
                    self.obj("barraestado").push(0, "El Cód. de Actividad Económica no es válido.")
                    self.obj("txt_a_00_1").set_text("")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)

    col0 = Op.columnas("Código", celda0, 0, True, 75, 100)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("R.U.C", celda0, 1, True, 100, 150)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Razón Social", celda1, 2, True, 200)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Nombre de Fantasía", celda1, 3, True, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Cód. Prop.", celda0, 4, True, 150)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("C.I.", celda0, 5, True, 150)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Propietario", celda1, 6, True, 250)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Dirección", celda1, 7, True, 250)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Nro. Teléfono", celda1, 8, True, 150)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Nro. Patronal IPS", celda0, 9, True, 150, 200)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Nro. Patronal MJT", celda0, 10, True, 150, 200)
    col10.set_sort_column_id(10)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(2)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 2)

    lista = ListStore(int, str, str, str, int, str, str, str, str, str, int, int)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
    " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", NroDocumento, " +
        "DigitoVerificador, RazonSocial, NombreFantasia, idPropietario, " +
        "NroDocPropietario, NombreApellido, DireccionPrincipal, " +
        "TelefonoPrincipal, NroPatronalIPS, NroPatronalMJT", self.tabla + "_s",
        opcion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        documento = str(datos[i][1]) + "-" + str(datos[i][2])
        lista.append([datos[i][0], documento, datos[i][3], datos[i][4],
            datos[i][5], datos[i][6], datos[i][7], datos[i][8], datos[i][9],
            datos[i][10], datos[i][11], datos[i][2]])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Código", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "R.U.C", "NroDocumento"
    elif idcolumna == 2:
        col, self.campo_buscar = "Razón Social", "RazonSocial"
    elif idcolumna == 3:
        col, self.campo_buscar = "Nombre de Fantasía", "NombreFantasia"
    elif idcolumna == 4:
        col, self.campo_buscar = "Cód. Propietario", "idPropietario"
    elif idcolumna == 5:
        col, self.campo_buscar = "C.I.", "NroDocPropietario"
    elif idcolumna == 6:
        col, self.campo_buscar = "Propietario", "NombreApellido"
    elif idcolumna == 7:
        col, self.campo_buscar = "Dirección Principal", "DireccionPrincipal"
    elif idcolumna == 8:
        col, self.campo_buscar = "Teléfono Principal", "TelefonoPrincipal"
    elif idcolumna == 9:
        col, self.campo_buscar = "Nro. Patronal IPS", "NroPatronalIPS"
    elif idcolumna == 10:
        col, self.campo_buscar = "Nro. Patronal MJT", "NroPatronalMJT"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 1)
    valor2 = seleccion.get_value(iterador, 2)
    valor3 = seleccion.get_value(iterador, 6)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n\nCódigo: " + valor0 +
        "\nR.U.C.: " + valor1 + "\nRazón Social: " + valor2 + "\nPropietario: " + valor3)

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
    from reportlab.lib.pagesizes import A4

    datos = self.obj("grilla").get_model()
    cant = len(datos)

    head = listado.tabla_celda_titulo()
    body_ce = listado.tabla_celda_centrado()
    body_iz = listado.tabla_celda_just_izquierdo()

    lista = [[Par("Código", head), Par("Nro. Documento", head), Par("Razón Social", head)]]
    for i in range(0, cant):
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][1], body_ce), Par(datos[i][2], body_iz)])

    listado.listado(self.titulo, lista, [100, 100, 200], A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = seleccion.get_value(iterador, 2)

        self.origen.txt_cod_emp.set_text(valor0)
        self.origen.txt_rzn_scl.set_text(valor1)

        self.on_btn_salir_clicked(0)
    except:
        pass
