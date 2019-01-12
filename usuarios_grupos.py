#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen):
        self.editando = edit
        self.nav = origen

        arch = Op.archivo("usuarios_grupos")
        self.obj = arch.get_object

        self.obj("ventana").set_default_size(700, 500)
        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro del Grupo de Usuarios")

        self.obj("btn_guardar").set_tooltip_text("Presione este botón para guardar el registro del Grupo de Usuarios")
        self.obj("btn_cancelar").set_tooltip_text("Presione este botón para cerrar esta ventana sin guardar cambios")

        self.estadoedicion(True)
        self.estadoguardar(False)
        self.estadopermiso(False)

        self.txt_cod_tabla = self.obj("txt_cod_tabla")
        self.txt_des_tabla = self.obj("txt_des_tabla")

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(50)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código del Grupo de Usuarios")
        self.obj("txt_01").set_tooltip_text("Ingrese la Descripción del Grupo de Usuarios")
        self.obj("txt_01").grab_focus()

        self.obj("btn_nuevo").set_tooltip_text("Presione este botón para Agregar\nun permiso sobre una Tabla")
        self.obj("btn_modificar").set_tooltip_text("Presione este botón para Modificar\nel permiso sobre una Tabla")
        self.obj("btn_eliminar").set_tooltip_text("Presione este botón para Eliminar\nel permiso sobre una Tabla")

        self.obj("btn_guardar_tab").set_tooltip_text("Presione este botón para Guardar el registro")
        self.obj("btn_cancelar_tab").set_tooltip_text("Presione este botón para Cancelar esta operación")

        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            self.desc = seleccion.get_value(iterador, 1)

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(self.desc)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                "grupousuarios_s", self.nav.campoid))
            self.obj("txt_01").set_text("")

        self.conexion = Op.conectar(self.nav.datos_conexion)
        self.config_grilla_tablas()
        self.cargar_grilla_tablas()

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_encabezado()
        self.conexion.commit()
        self.conexion.close()  # Finaliza la Conexión
        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la Conexión
        self.obj("ventana").destroy()

    def on_btn_nuevo_clicked(self, objeto):
        self.editando_tabla = False
        self.funcion_permisos()

    def on_btn_modificar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un Permiso de la lista. Luego presione Modificar.")
        else:
            self.editando_tabla = True
            self.funcion_permisos()

    def on_btn_eliminar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            tabla = str(seleccion.get_value(iterador, 0))
            descr = str(seleccion.get_value(iterador, 1))
        except:
            self.obj("barraestado").push(0, "Seleccione un Permiso de la lista. Luego presione Eliminar.")
        else:
            grupo = self.obj("txt_00").get_text()

            eleccion = Mens.pregunta_borrar(
                "Seleccionó los Permisos de la Tabla:\n\n" + descr)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "grupousuarios_permisos", grupo + ", " + tabla)
                self.cargar_grilla_tablas()

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0:
            self.estadoguardar(False)
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Cód. de Grupo", self.obj("barraestado")):
                self.encabezado_guardado = False
                self.estadoguardar(True)
                self.obj("barraestado").push(0, "")
            else:
                self.estadoguardar(False)

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_clicked(0)

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) and \
                Op.comprobar_numero(int, self.obj("txt_00"), "Cód. de Grupo", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion, "grupousuarios_s",
                        "idGrupoUsuario", valor, self.obj("txt_00"),
                        self.obj("btn_guardar"), self.obj("barraestado"),
                        "El Código introducido ya ha sido registado.")
            else:
                busc = "" if not self.editando else " AND idGrupoUsuario <> " + self.cond
                # Comprueba si la descripcion ya ha sido registada
                Op.comprobar_unique(self.nav.datos_conexion, "grupousuarios_s",
                    "Descripcion", "'" + valor + "'" + busc, self.obj("txt_01"),
                    self.obj("btn_guardar"), self.obj("barraestado"),
                    "La Descripción introducida ya ha sido registada.")

    def config_grilla_tablas(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)

        col0 = Op.columnas("Código", celda0, 0, False)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Tabla", celda1, 1, True, 170)
        col1.set_sort_column_id(1)
        col2 = Op.columna_active("Consulta", 2)
        col2.set_sort_column_id(2)
        col3 = Op.columna_active("Inserción", 3)
        col3.set_sort_column_id(3)
        col4 = Op.columna_active("Modificación", 4)
        col4.set_sort_column_id(4)
        col5 = Op.columna_active("Eliminación", 5)
        col5.set_sort_column_id(5)
        col6 = Op.columna_active("Anulación", 6)
        col6.set_sort_column_id(6)

        lista = [col0, col1, col2, col3, col4, col5, col6]
        for columna in lista:
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(1)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, int, int, int, int, int)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_tablas(self):
        cursor = Op.consultar(self.conexion, "*", "grupousuarios_permisos_s",
            " WHERE idGrupoUsuario = " + self.obj("txt_00").get_text() +
            " ORDER BY idTabla")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][2], datos[i][3], datos[i][4],
            datos[i][5], datos[i][6], datos[i][7], datos[i][8]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def guardar_encabezado(self):
        # Si el encabezado no ha sido registrado
        if not self.encabezado_guardado:
            cod = self.obj("txt_00").get_text()
            des = self.obj("txt_01").get_text()

            sql = cod + ", '" + des + "'"
            if not self.editando:
                Op.insertar(self.conexion, "grupousuarios", sql)
            else:
                Op.modificar(self.conexion, "grupousuarios", self.cond + ", " + sql)

            self.encabezado_guardado = True
            self.editando = True
            self.cond = cod

    def estadoedicion(self, estado):
        self.obj("txt_00").set_sensitive(estado)
        self.obj("txt_01").set_sensitive(estado)
        self.obj("btn_cancelar").set_sensitive(estado)

    def estadoguardar(self, estado):
        self.obj("btn_nuevo").set_sensitive(estado)
        self.obj("btn_modificar").set_sensitive(estado)
        self.obj("btn_eliminar").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)
        self.obj("btn_guardar").set_sensitive(estado)

##### Ventana de Inserción y Actualización de Entidades ################

    def estadopermiso(self, estado):
        self.obj("separador1").set_visible(estado)
        self.obj("hbox3").set_visible(estado)
        self.obj("tabla").set_visible(estado)
        self.obj("btn_guardar_tab").set_visible(estado)
        self.obj("btn_cancelar_tab").set_visible(estado)

    def funcion_permisos(self):
        edit = "Agregar" if not self.editando_tabla else "Modificar"
        self.obj("ventana").set_title(edit + " Registro de Permisos de Grupo")

        if self.editando_tabla:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.idTabla = seleccion.get_value(iterador, 0)
            tab = seleccion.get_value(iterador, 1)

            self.obj("txt_cod_tabla").set_text(str(self.idTabla))
            self.obj("txt_des_tabla").set_text(tab)

            self.obj("txt_cod_tabla").set_editable(False)
            self.obj("txt_cod_tabla").set_property('can_focus', False)

            self.obj("btn_tablas").set_sensitive(False)
            visibilidad_permisos(self)
        else:
            self.obj("txt_cod_tabla").set_text("")
            self.obj("txt_des_tabla").set_text("")

            self.obj("txt_cod_tabla").set_editable(True)
            self.obj("txt_cod_tabla").set_property('can_focus', True)
            self.obj("btn_tablas").set_sensitive(True)

        self.obj("btn_guardar_tab").set_sensitive(False)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        self.estadoedicion(False)
        self.estadoguardar(False)
        self.estadopermiso(True)

    def on_btn_guardar_tab_clicked(self, objeto):
        self.guardar_encabezado()

        gru = self.obj("txt_00").get_text()
        con = "1" if self.obj("chk_consulta").get_active() else "0"
        ins = "1" if self.obj("chk_inserta").get_active() else "0"
        act = "1" if self.obj("chk_modifica").get_active() else "0"
        eli = "1" if self.obj("chk_elimina").get_active() else "0"
        anu = "1" if self.obj("chk_anula").get_active() else "0"

        sql = gru + ", " + str(self.idTabla) + ", " + \
            con + ", " + ins + ", " + act + ", " + eli + ", " + anu

        if not self.editando_tabla:
            Op.insertar(self.conexion, "grupousuarios_permisos", sql)
        else:
            Op.modificar(self.conexion, "grupousuarios_permisos", sql)

        self.cargar_grilla_tablas()
        self.on_btn_cancelar_tab_clicked(0)

    def on_btn_cancelar_tab_clicked(self, objeto):
        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro del Grupo de Usuarios")

        self.estadoedicion(True)
        self.estadoguardar(True)
        self.estadopermiso(False)

    def on_btn_tablas_clicked(self, objeto):
        from clases.llamadas import sistematablas
        sistematablas(self.nav.datos_conexion, self)

    def on_txt_cod_tabla_changed(self, objeto):
        if len(self.obj("txt_cod_tabla").get_text()) == 0:
            self.obj("btn_guardar_tab").set_sensitive(False)
        else:
            if Op.comprobar_numero(int, objeto, "Código", self.obj("barraestado")) \
            and len(self.obj("txt_des_tabla").get_text()) > 0:
                self.editando_tabla = cambiar_tabla_seleccionada(self)
                self.on_chk_toggled(0)
            else:
                self.obj("btn_guardar_tab").set_sensitive(False)

    def on_txt_cod_tabla_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_tablas_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.on_txt_cod_tabla_focus_out_event(objeto, 0)

    def on_txt_cod_tabla_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar una Tabla.")

    def on_txt_cod_tabla_focus_out_event(self, objeto, evento):
        txt_tabla_focus_out(self, objeto, self.nav.datos_conexion, self.obj("btn_guardar_tab"))

    def on_chk_toggled(self, objeto):
        verificacion_permisos(self, self.obj("btn_guardar_tab"))

    def on_chk_todo_toggled(self, objeto):
        check_button_todo_toggled(self)


def txt_tabla_focus_out(self, objeto, datos_conexion, boton_guardar):
    codigo = objeto.get_text()

    if len(codigo) > 0 and Op.comprobar_numero(int, objeto, "Código", self.obj("barraestado")):
        conexion = Op.conectar(datos_conexion)
        cursor = Op.consultar(conexion, "Nombre, Tabla",
            "sistematablas", " WHERE idTabla = " + codigo)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            self.idTabla = int(codigo)
            self.obj("txt_des_tabla").set_text(datos[0][0])

            self.editando_tabla = cambiar_tabla_seleccionada(self)
        else:
            objeto.grab_focus()
            self.obj("txt_des_tabla").set_text("")
            boton_guardar.set_sensitive(False)
            self.obj("barraestado").push(0, "El Código de Tabla no es válido.")
    else:
        self.obj("txt_des_tabla").set_text("")
        boton_guardar.set_sensitive(False)

        self.idTabla = -1
        visibilidad_permisos(self)


def cambiar_tabla_seleccionada(self, opcion=False):
    # Configuración de Checks para la tabla seleccionada
    check_button_active(self, False, False, False, False, False)
    visibilidad_permisos(self)

    lista = self.obj("grilla").get_model()
    cant = len(lista)

    editando = False
    if opcion:  # Opcion indica que viene de UsuariosPermisos
        self.con, self.ins, self.act, self.eli, self.anu = False, False, False, False, False

    # Verifica si se están editando los permisos de la Tabla
    for i in range(0, cant):
        if lista[i][0] == self.idTabla:
            con = True if lista[i][2] == 1 else False
            ins = True if lista[i][3] == 1 else False
            act = True if lista[i][4] == 1 else False
            eli = True if lista[i][5] == 1 else False
            anu = True if lista[i][6] == 1 else False
            check_button_active(self, con, ins, act, eli, anu)

            if opcion:  # Opcion indica que viene de UsuariosPermisos
                self.con, self.ins, self.act, self.eli, self.anu = con, ins, act, eli, anu

            editando = True
            break

    return editando


def verificacion_permisos(self, boton_guardar):
    anu = True if not self.obj("chk_anula").get_visible() \
    else self.obj("chk_anula").get_active()

    ins = True if not self.obj("chk_inserta").get_visible() \
    else self.obj("chk_inserta").get_active()

    act = True if not self.obj("chk_modifica").get_visible() \
    else self.obj("chk_modifica").get_active()

    eli = True if not self.obj("chk_elimina").get_visible() \
    else self.obj("chk_elimina").get_active()

    # Para realizar estas acciones necesita consultar
    if self.obj("chk_inserta").get_active() or self.obj("chk_modifica").get_active() \
    or self.obj("chk_elimina").get_active() or self.obj("chk_anula").get_active():
        self.obj("chk_consulta").set_active(True)

    if self.obj("chk_consulta").get_active() and anu and ins and act and eli:
        self.obj("chk_todo").set_active(True)
    else:
        self.condicion = False  # Para no deseleccionar todo
        self.obj("chk_todo").set_active(False)

    # Habilitar en botón Guardar
    if len(self.obj("txt_cod_tabla").get_text()) > 0 \
    and len(self.obj("txt_des_tabla").get_text()) > 0 \
    and (self.obj("chk_consulta").get_active() \
    or self.obj("chk_inserta").get_active() or self.obj("chk_modifica").get_active() \
    or self.obj("chk_elimina").get_active() or self.obj("chk_anula").get_active()):
        boton_guardar.set_sensitive(True)
    else:
        boton_guardar.set_sensitive(False)


def check_button_todo_toggled(self):
    if self.obj("chk_todo").get_active():
        self.condicion = True  # Para poder seleccionar todo
        check_button_evaluacion(self, True)  # Seleccionar Todo
    else:
        check_button_evaluacion(self, False)  # Deseleccionar Todo


def check_button_evaluacion(self, estado):
    if self.condicion:
        check_button_active(self, estado, estado, estado, estado, estado)


def check_button_active(self, con, ins, act, eli, anu):
    # Para que los no visibles no se activen al seleccionar todo
    if not self.obj("chk_anula").get_visible(): anu = False
    if not self.obj("chk_inserta").get_visible(): ins = False
    if not self.obj("chk_modifica").get_visible(): act = False
    if not self.obj("chk_elimina").get_visible(): eli = False

    self.obj("chk_anula").set_active(anu)
    self.obj("chk_inserta").set_active(ins)
    self.obj("chk_modifica").set_active(act)
    self.obj("chk_elimina").set_active(eli)
    self.obj("chk_consulta").set_active(con)


def check_button_visible(self, ins, act, eli, anu):
    self.obj("chk_anula").set_visible(anu)
    self.obj("chk_inserta").set_visible(ins)
    self.obj("chk_modifica").set_visible(act)
    self.obj("chk_elimina").set_visible(eli)


def visibilidad_permisos(self):
    if self.idTabla == 1:     # Actividades Económicas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 2:   # Aguinaldos
        check_button_visible(self, True, False, True, False)
    elif self.idTabla == 3:   # Ajustes de Inventario
        check_button_visible(self, True, False, False, False)
    elif self.idTabla == 4:   # Anticipos
        check_button_visible(self, True, False, True, False)
    elif self.idTabla == 5:   # Aperturas y Cierres de Caja
        check_button_visible(self, True, False, False, False)
    elif self.idTabla == 6:   # Arqueos de Caja
        check_button_visible(self, True, False, False, False)
    elif self.idTabla == 7:   # Asistencias
        check_button_visible(self, True, False, False, False)
    elif self.idTabla == 8:   # Barrios
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 9:   # Beneficiarios
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 10:  # Calles
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 11:  # Cargos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 12:  # Categorías
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 13:  # Cheques de Terceros
        check_button_visible(self, True, True, False, True)
    elif self.idTabla == 14:  # Ciudades
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 15:  # Comprobantes de Pago
        check_button_visible(self, True, True, True, True)
    elif self.idTabla == 16:  # Conceptos de Cobro por Recibos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 17:  # Conceptos de Pago de Salarios
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 18:  # Contratos
        check_button_visible(self, True, True, False, True)
    elif self.idTabla == 19:  # Cotizaciones de Monedas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 20:  # Denominaciones
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 21:  # Departamentos, Provincias, Estados
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 22:  # Depósitos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 23:  # Descuentos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 24:  # Días No Hábiles
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 25:  # Empresas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 26:  # Entradas de Empleados
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 27:  # Establecimientos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 28:  # Estados Civiles
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 29:  # Facturas de Compra
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 30:  # Facturas de Venta
        check_button_visible(self, True, False, False, True)
    elif self.idTabla == 31:  # Formas de Pago
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 32:  # Géneros
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 33:  # Gratificaciones
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 34:  # Horas Extraordinarias
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 35:  # Impuestos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 36:  # Ítems
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 37:  # Justificativos Judiciales
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 38:  # Justificativos por Permisos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 39:  # Justificativos por Sanciones
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 40:  # Marcas de Ítems
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 41:  # Marcas de Tarjetas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 42:  # Marcas de Vehículos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 43:  # Monedas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 44:  # Motivos de Ajuste
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 45:  # Motivos de Descuentos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 46:  # Motivos de Gratificaciones
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 47:  # Motivos de Permisos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 48:  # Motivos de Salidas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 49:  # Motivos de Sanciones
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 50:  # Motivos de Traslados
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 51:  # Notas de Crédito por Compras
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 52:  # Notas de Crédito por Ventas
        check_button_visible(self, True, False, False, True)
    elif self.idTabla == 53:  # Notas de Débito por Compras
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 54:  # Notas de Débito por Ventas
        check_button_visible(self, True, False, False, True)
    elif self.idTabla == 55:  # Notas de Remisión
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 56:  # Ocupaciones
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 57:  # Órdenes de Compra
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 58:  # Países
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 59:  # Pedidos de Compra
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 60:  # Pedidos de Venta
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 61:  # Periodos de Pago
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 62:  # Personas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 63:  # Preavisos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 64:  # Presentaciones
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 65:  # Puntos de Expedición o Cajas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 66:  # Recibos de Dinero
        check_button_visible(self, True, False, False, True)
    elif self.idTabla == 67:  # Reposos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 68:  # Roles de Personas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 69:  # Salarios Mínimos
        check_button_visible(self, True, False, False, True)
    elif self.idTabla == 70:  # Salidas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 71:  # Tarjetas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 72:  # Timbrados
        check_button_visible(self, True, True, False, True)
    elif self.idTabla == 73:  # Tipos de Calles
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 74:  # Tipos de Cheques
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 75:  # Tipos de Clientes
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 76:  # Tipos de Contratos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 77:  # Tipos de Denominaciones
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 78:  # Tipos de Documentos Comerciales
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 79:  # Tipos de Documentos de Identidad
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 80:  # Tipos de Empresas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 81:  # Tipos de Facturas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 82:  # Tipos de Juzgados
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 83:  # Tipos de Medios de Contacto
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 84:  # Tipos de Parentescos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 85:  # Tipos de Salarios
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 86:  # Tipos de Seguros
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 87:  # Tipos de Tarjetas
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 88:  # Tipos de Valores
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 89:  # Turnos de Juzgados
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 90:  # Turnos de Trabajo
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 91:  # Unidades de Medida
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 92:  # Usuarios del Sistema
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 93:  # Vacaciones
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 94:  # Vehículos
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 95:  # Vendedores
        check_button_visible(self, True, True, True, False)
    elif self.idTabla == 96:  # Zonas de Venta
        check_button_visible(self, True, True, True, False)
    else:  # Tabla NO especificada aún
        check_button_visible(self, True, True, True, True)


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)

    col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Descripción", celda1, 1, True, 345)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Cantidad de Permisos", celda0, 2, True, 150)
    col2.set_sort_column_id(2)

    lista = [col0, col1, col2]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 1)

    lista = ListStore(int, str, int)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
    " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, "*", "grupousuarios_s",
        opcion + " ORDER BY idGrupoUsuario")
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], datos[i][1], datos[i][2]])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Código", "idGrupoUsuario"
    elif idcolumna == 1:
        col, self.campo_buscar = "Descripción", "Descripcion"
    elif idcolumna == 2:
        col, self.campo_buscar = "Cantidad de Permisos", "CantPermisos"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 1)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
        "Cód.: " + valor0 + "\nDescripción: " + valor1)

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

    lista = [[Par("Código", head), Par("Descripción", head), Par("Cantidad de Permisos", head)]]

    for i in range(0, cant):
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][1], body_iz),
        Par(str(datos[i][2]), body_ce)])

    listado.listado(self.titulo, lista, [100, 250, 100], A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        self.origen.concesion_de_permisos_grupos(valor0)
        self.on_btn_salir_clicked(0)
    except:
        pass
