#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import exc_info
from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from mysql.connector import errors as MySqlErr
from clases import mensajes as Mens
from clases import operaciones as Op
import usuarios_grupos as Ug


class permisos:

    def __init__(self, datos, usu):
        self.datos_conexion = datos
        self.usuario = usu

        arch = Op.archivo("usuarios_permisos")
        self.obj = arch.get_object

        self.obj("ventana").set_default_size(700, 500)
        self.obj("ventana").set_position(1)
        self.obj("ventana").set_title("Navegar - Permisos del Usuario")
        self.obj("label").set_text("Permisos de «" + self.usuario + "»")

        self.obj("btn_per_guardar").set_tooltip_text("Presione este botón para Guardar la operación")
        self.obj("btn_per_cancelar").set_tooltip_text("Presione este botón para Cancelar la operación")

        self.obj("btn_per_nuevo").set_tooltip_text("Presione este botón para Agregar\nun permiso sobre una Tabla")
        self.obj("btn_per_modificar").set_tooltip_text("Presione este botón para Modificar\nel permiso sobre una Tabla")
        self.obj("btn_per_eliminar").set_tooltip_text("Presione este botón para Eliminar\nel permiso sobre una Tabla")
        self.obj("btn_per_grupo").set_tooltip_text("Presione este botón para Seleccionar el Grupo\nal que pertenece el Usuario y obtener sus permisos")
        self.obj("btn_per_todos").set_tooltip_text("Presione este botón para Eliminar\ntodos los permisos del Usuario")
        self.obj("btn_per_salir").set_tooltip_text("Presione este botón para Cerrar esta ventana")

        arch.connect_signals(self)

        self.con, self.ins, self.act, self.eli, self.anu = False, False, False, False, False
        self.txt_cod_tabla = self.obj("txt_cod_tabla")
        self.txt_des_tabla = self.obj("txt_des_tabla")
        self.estadoedicion(False)

        self.config_grilla()
        self.cargar_grilla()
        self.obj("ventana").show()

    def on_btn_per_nuevo_clicked(self, objeto):
        self.editando_tabla = False
        self.funcion_permisos()

    def on_btn_per_modificar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un Permiso de la lista. Luego presione Modificar.")
        else:
            self.editando_tabla = True
            self.funcion_permisos()

    def on_btn_per_eliminar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.idTabla = seleccion.get_value(iterador, 0)
            tabla = seleccion.get_value(iterador, 1)
        except:
            self.obj("barraestado").push(0, "Seleccione un Permiso de la lista. Luego presione Revocar Permiso.")
        else:
            con = True if seleccion.get_value(iterador, 2) == 1 else False
            ins = True if seleccion.get_value(iterador, 3) == 1 else False
            act = True if seleccion.get_value(iterador, 4) == 1 else False
            eli = True if seleccion.get_value(iterador, 5) == 1 else False
            anu = True if seleccion.get_value(iterador, 6) == 1 else False

            eleccion = Mens.pregunta_borrar(
                "Seleccionó los Permisos de la Tabla:\n\n" + tabla + "")

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                try:
                    self.permisos_tablas(con, ins, act, eli, anu, False)

                    if self.idTabla == 48:  # Usuarios
                        self.borrar_permiso_administrativo()
                except MySqlErr.DatabaseError as e:
                    print(("Error de Base de Datos:\n" + str(e) + "\n"))
                    Mens.no_puede_borrar()
                except:
                    print("Error: ", exc_info()[0])
                    Mens.no_puede_borrar()
                else:
                    self.cargar_grilla()

    def on_btn_per_grupo_clicked(self, objeto):
        from clases.llamadas import grupousuarios
        grupousuarios(self.datos_conexion, self)

    def on_btn_per_todos_clicked(self, objeto):
        eleccion = Mens.pregunta_borrar("Seleccionó revocar todos los permisos del Usuario.")
        if eleccion:
            conexion = Op.conectar(self.datos_conexion)
            try:
                cursor = conexion.cursor()
                cursor.execute("REVOKE ALL PRIVILEGES, GRANT OPTION FROM '" + self.usuario + "'")
                Op.concede_select(cursor, "tablas_s", self.usuario)
                Op.concede_select(cursor, "vistas_s", self.usuario)
                Op.concede_select(cursor, "procedimientos_s", self.usuario)
                conexion.commit()
            except MySqlErr.DatabaseError as e:
                print(("Error de Base de Datos:\n" + str(e) + "\n"))
                self.obj("barraestado").push(0, "No ha sido posible revocar Todos los Permisos del Usuario.")
            except:
                print("Error: ", exc_info()[0])
                conexion.rollback()
                self.obj("barraestado").push(0, "No ha sido posible revocar Todos los Permisos del Usuario.")
            else:
                self.cargar_grilla()
            finally:
                conexion.close()  # Finaliza la conexión

    def on_btn_per_salir_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_grilla_per_row_activated(self, objeto, fila, col):
        self.on_btn_per_modificar_clicked(0)

    def on_grilla_per_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_per_eliminar_clicked(0)

    def config_grilla(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)

        col0 = Op.columnas("Cód.", celda0, 0, False)
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

        lista = ListStore(int, str, int, int, int, int, int, str)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla(self):
        conexion = Op.conectar(self.datos_conexion)
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM sistematablas")
        dato_tab = cursor.fetchall()
        cant_tab = cursor.rowcount

        cursor.execute("SELECT Routine_name FROM mysql.procs_priv" +
        " WHERE User = '" + self.usuario + "' AND Db = 'distribuidora'")
        dato_proce = cursor.fetchall()
        cant_proce = cursor.rowcount

        cursor.execute("SELECT Table_name FROM mysql.tables_priv" +
        " WHERE User = '" + self.usuario + "' AND Db = 'distribuidora'")
        dato_tabla = cursor.fetchall()
        cant_tabla = cursor.rowcount

        conexion.close()  # Finaliza la conexión
        cant = 0

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant_tab):  # Tablas del Sistema
            tabla = dato_tab[i][2]
            con, ins, act, eli, anu = 0, 0, 0, 0, 0

            for x in range(0, cant_tabla):  # Permisos
                if dato_tabla[x][0] == bytearray(tabla, 'utf-8') \
                or dato_tabla[x][0] == bytearray(tabla + "_s", 'utf-8'):
                    con = 1
            for x in range(0, cant_proce):
                if dato_proce[x][0] == tabla + "_i":
                    ins = 1
            for x in range(0, cant_proce):
                if dato_proce[x][0] == tabla + "_u":
                    act = 1
            for x in range(0, cant_proce):
                if dato_proce[x][0] == tabla + "_d":
                    eli = 1
            for x in range(0, cant_proce):
                if dato_proce[x][0] == tabla + "_a":
                    anu = 1

            if con != 0 or ins != 0 or act != 0 or eli != 0 or anu != 0:
                lista.append([dato_tab[i][0], dato_tab[i][1],
                    con, ins, act, eli, anu, dato_tab[i][2]])
                cant += 1

        cant = str(cant) + " permiso encontrado." if cant == 1 \
        else str(cant) + " permisos encontrados."
        self.obj("barraestado").push(0, cant)

    def borrar_permiso_administrativo(self):
        conexion = Op.conectar(self.datos_conexion)
        cursor = conexion.cursor()

        cursor.execute("REVOKE ALL PRIVILEGES, GRANT OPTION FROM '" + self.usuario + "'")
        Op.concede_select(cursor, "tablas_s", self.usuario)
        Op.concede_select(cursor, "vistas_s", self.usuario)
        Op.concede_select(cursor, "procedimientos_s", self.usuario)

        conexion.close()  # Finaliza la conexión
        lista = self.obj("grilla").get_model()
        cant = len(lista)

        for i in range(0, cant):
            self.idTabla = lista[i][0]

            if self.idTabla != 48:
                con = True if lista[i][2] == 1 else False
                ins = True if lista[i][3] == 1 else False
                act = True if lista[i][4] == 1 else False
                eli = True if lista[i][5] == 1 else False
                anu = True if lista[i][6] == 1 else False

                self.permisos_tablas(con, ins, act, eli, anu, True)

    def tabla_o_vista(self, cursor, tabla):
        cursor.execute("SHOW TABLES FROM distribuidora")
        datos = cursor.fetchall()

        vista = ""  # Identifica si se trata de una tabla o una vista
        for i in range(0, cursor.rowcount):
            if datos[i][0] == tabla + "_s":
                vista = "_s"

        return vista

    def estadoedicion(self, estado):
        self.obj("hbox1").set_visible(estado)
        self.obj("separador2").set_visible(estado)
        self.obj("btn_per_guardar").set_visible(estado)
        self.obj("btn_per_cancelar").set_visible(estado)

        self.obj("grilla").set_sensitive(not estado)
        self.obj("btn_per_nuevo").set_sensitive(not estado)
        self.obj("btn_per_modificar").set_sensitive(not estado)
        self.obj("btn_per_eliminar").set_sensitive(not estado)
        self.obj("btn_per_grupo").set_sensitive(not estado)
        self.obj("btn_per_todos").set_sensitive(not estado)
        self.obj("btn_per_salir").set_sensitive(not estado)

##### Ventana de Permisos ##############################################

    def funcion_permisos(self):
        tit = "Agregando" if not self.editando_tabla else "Actualizando"
        self.obj("ventana").set_title(tit + " Permisos")

        if self.editando_tabla:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.idTabla = seleccion.get_value(iterador, 0)
            tab = seleccion.get_value(iterador, 1)

            # Valores originales, para conceder o revocar permisos
            self.con = True if seleccion.get_value(iterador, 2) == 1 else False
            self.ins = True if seleccion.get_value(iterador, 3) == 1 else False
            self.act = True if seleccion.get_value(iterador, 4) == 1 else False
            self.eli = True if seleccion.get_value(iterador, 5) == 1 else False
            self.anu = True if seleccion.get_value(iterador, 6) == 1 else False

            self.obj("txt_cod_tabla").set_text(str(self.idTabla))
            self.obj("txt_des_tabla").set_text(tab)

            self.obj("txt_cod_tabla").set_editable(False)
            self.obj("txt_cod_tabla").set_property('can_focus', False)

            self.obj("btn_tablas").set_sensitive(False)
            Ug.visibilidad_permisos(self)
        else:
            # Valores iniciales, para poder conceder permisos
            self.idTabla = -1
            self.con = self.ins = self.act = self.eli = self.anu = False

            self.obj("txt_cod_tabla").set_text("")
            self.obj("txt_des_tabla").set_text("")

            self.obj("chk_anula").set_active(False)
            self.obj("chk_inserta").set_active(False)
            self.obj("chk_modifica").set_active(False)
            self.obj("chk_elimina").set_active(False)
            self.obj("chk_consulta").set_active(False)

            self.obj("txt_cod_tabla").set_editable(True)
            self.obj("txt_cod_tabla").set_property('can_focus', True)
            self.obj("btn_tablas").set_sensitive(True)
            Ug.visibilidad_permisos(self)

        self.obj("btn_per_guardar").set_sensitive(False)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")
        self.estadoedicion(True)

    def on_btn_per_guardar_clicked(self, objeto):
        con = True if self.obj("chk_consulta").get_active() else False
        ins = True if self.obj("chk_inserta").get_active() else False
        act = True if self.obj("chk_modifica").get_active() else False
        eli = True if self.obj("chk_elimina").get_active() else False
        anu = True if self.obj("chk_anula").get_active() else False
        self.permisos_tablas(con, ins, act, eli, anu, True)

        self.cargar_grilla()
        self.on_btn_per_cancelar_clicked(0)

    def on_btn_per_cancelar_clicked(self, objeto):
        self.estadoedicion(False)
        self.obj("ventana").set_title("Navegar - Permisos del Usuario")

    def on_btn_tablas_clicked(self, objeto):
        from clases.llamadas import sistematablas
        sistematablas(self.datos_conexion, self)

    def on_txt_cod_tabla_changed(self, objeto):
        if len(self.obj("txt_cod_tabla").get_text()) == 0:
            self.obj("btn_per_guardar").set_sensitive(False)
        else:
            if Op.comprobar_numero(int, objeto, "Código", self.obj("barraestado")):
                self.editando_tabla = Ug.cambiar_tabla_seleccionada(self, True)
                self.on_chk_toggled(0)
            else:
                self.obj("btn_per_guardar").set_sensitive(False)

    def on_txt_cod_tabla_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_tablas_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.on_txt_cod_tabla_focus_out_event(objeto, 0)

    def on_txt_cod_tabla_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar una Tabla.")

    def on_txt_cod_tabla_focus_out_event(self, objeto, evento):
        Ug.txt_tabla_focus_out(self, objeto, self.datos_conexion, self.obj("btn_per_guardar"))

    def on_chk_toggled(self, objeto):
        Ug.verificacion_permisos(self, self.obj("btn_per_guardar"))

    def on_chk_todo_toggled(self, objeto):
        Ug.check_button_todo_toggled(self)

    def concesion_de_permisos(self, tabla, con, ins, act, eli, anu, concede, referenciales=None, detalles=None):
        conexion = Op.conectar(self.datos_conexion)
        cursor = conexion.cursor()

        vista = self.tabla_o_vista(cursor, tabla)
        if concede:
            # Si Tenía y ahora no, REVOCA, sino, si Tiene ahora, CONCEDE
            if self.con and not con: Op.revoca_select(cursor, tabla + vista, self.usuario)
            elif con: Op.concede_select(cursor, tabla + vista, self.usuario)

            if self.ins and not ins: Op.revoca_rutina(cursor, tabla + "_i", self.usuario)
            elif ins: Op.concede_rutina(cursor, tabla + "_i", self.usuario)

            if self.act and not act: Op.revoca_rutina(cursor, tabla + "_u", self.usuario)
            elif act: Op.concede_rutina(cursor, tabla + "_u", self.usuario)

            if self.eli and not eli: Op.revoca_rutina(cursor, tabla + "_d", self.usuario)
            elif eli: Op.concede_rutina(cursor, tabla + "_d", self.usuario)

            if self.anu and not anu: Op.revoca_rutina(cursor, tabla + "_a", self.usuario)
            elif anu: Op.concede_rutina(cursor, tabla + "_a", self.usuario)
        else:
            if con: Op.revoca_select(cursor, tabla + vista, self.usuario)
            if ins: Op.revoca_rutina(cursor, tabla + "_i", self.usuario)
            if act: Op.revoca_rutina(cursor, tabla + "_u", self.usuario)
            if eli: Op.revoca_rutina(cursor, tabla + "_d", self.usuario)
            if anu: Op.revoca_rutina(cursor, tabla + "_a", self.usuario)

        if tabla in ("comprobantepagos", "descuentos", "empresas", "items", \
        "personas", "pedidocompras", "pedidoventas", "ordencompras", \
        "facturacompras", "facturaventas", "notacreditocompras", \
        "notacreditoventas", "notadebitocompras", "notadebitoventas", \
        "notaremisiones", "recibos", "vacaciones") \
        and ins and not act:
            # Si inserta, puede modificar (encabezado); pero no se concedió, entonces concede
            Op.concede_rutina(cursor, tabla + "_u", self.usuario)

        if tabla == "beneficiarios" and (ins or act):
            # Si inserta o modifica, necesita de los tres
            if not ins: Op.concede_rutina(cursor, tabla + "_i", self.usuario)
            if not act: Op.concede_rutina(cursor, tabla + "_u", self.usuario)
            if not eli: Op.concede_rutina(cursor, tabla + "_d", self.usuario)

        if tabla in ("comprobantepagos", "vacaciones"):
            if ins or act:
                if concede: # Si inserta o actualiza necesita saber la antigüedad del Empleado
                    Op.concede_rutina(cursor, "antiguedad_s", self.usuario)
                else:
                    Op.revoca_rutina(cursor, "antiguedad_s", self.usuario)
            else:  # No concede permisos de inserción y actualización
                # Si concede permisos, y tenía los de inserción o actualización
                if concede and (self.ins or self.act):
                    Op.revoca_rutina(cursor, "antiguedad_s", self.usuario)

        if tabla in ("facturacompras", "notacreditocompras", "notadebitocompras"):
            # La Compra de ítem modifica su precio de costo
            Op.concede_rutina(cursor, "items_costo_u", self.usuario)

        if tabla == "usuarios":
            cursor.execute("GRANT ALL PRIVILEGES ON *.* TO '" + self.usuario + "'")
            cursor.execute("GRANT GRANT OPTION ON *.* TO '" + self.usuario + "'")

        if referenciales is not None:  # Solo para realizar consultas
            if concede and (ins or act):  # Solo si concede la inserción o actualización
                longitud = len(referenciales)
                for i in range(0, longitud):
                    tabla = referenciales[i]
                    vista = self.tabla_o_vista(cursor, tabla)
                    Op.concede_select(cursor, tabla + vista, self.usuario)

        if detalles is not None:  # Puede consultar, insertar, modificar y eliminar
            longitud = len(detalles)
            for i in range(0, longitud):
                tabla = detalles[i]
                vista = self.tabla_o_vista(cursor, tabla)
                if ins or act:  # Solo si concede o revoca el permiso de inserción o actualización
                    if concede:
                        Op.concede_select(cursor, tabla + vista, self.usuario)
                        Op.concede_rutina(cursor, tabla + "_i", self.usuario)
                        Op.concede_rutina(cursor, tabla + "_u", self.usuario)
                        Op.concede_rutina(cursor, tabla + "_d", self.usuario)
                    else:
                        Op.revoca_select(cursor, tabla + vista, self.usuario)
                        Op.revoca_rutina(cursor, tabla + "_i", self.usuario)
                        Op.revoca_rutina(cursor, tabla + "_u", self.usuario)
                        Op.revoca_rutina(cursor, tabla + "_d", self.usuario)

                else:  # No concede permisos de inserción y actualización
                    # Si concede permisos, y tenía los de inserción o actualización
                    if concede and (self.ins or self.act):
                        Op.revoca_select(cursor, tabla + vista, self.usuario)
                        Op.revoca_rutina(cursor, tabla + "_i", self.usuario)
                        Op.revoca_rutina(cursor, tabla + "_u", self.usuario)
                        Op.revoca_rutina(cursor, tabla + "_d", self.usuario)

        conexion.commit()
        conexion.close()  # Finaliza la conexión

    def permisos_tablas(self, con, ins, act, eli, anu, concede):
        if self.idTabla == 1:     # Actividades Económicas
            self.concesion_de_permisos("actividadeseconomicas", con, ins, act, eli, anu, concede)

        elif self.idTabla == 2:   # Aguinaldos
            ref = ["contratos", "empresas", "personas", "tipodocumentos"]
            self.concesion_de_permisos("aguinaldos", con, ins, act, eli, anu, concede, ref)

            if concede:  # Tiene permiso para crear y anular Comprobantes
                self.idTabla = 15
                self.permisos_tablas(True, True, False, False, True, concede)

        elif self.idTabla == 3:   # Ajustes de Inventario
            pass

        elif self.idTabla == 4:   # Anticipos
            ref = ["contratos", "empresas", "personas", "tipodocumentos"]
            self.concesion_de_permisos("anticipos", con, ins, act, eli, anu, concede, ref)

            if concede:  # Tiene permiso para crear y anular Comprobantes
                self.idTabla = 15
                self.permisos_tablas(True, True, False, False, True, concede)

        elif self.idTabla == 5:   # Aperturas y Cierres de Caja
            ref = ["establecimientos", "puntoexpediciones", "tipodocumentocomerciales"]
            self.concesion_de_permisos("cajaaperturas", con, ins, act, eli, anu, concede, ref)

            ref = ["arqueos"]
            self.concesion_de_permisos("cajacierres", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 6:   # Arqueos de Caja
            pass

        elif self.idTabla == 7:   # Asistencias
            ref = ["contratos", "personas", "tipodocumentos"]
            self.concesion_de_permisos("asistencias", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 8:   # Barrios
            self.concesion_de_permisos("barrios", con, ins, act, eli, anu, concede)

        elif self.idTabla == 9:   # Beneficiarios
            ref = ["personas", "personas_direcciones", "personas_mediocontactos",
                "tipodocumentos", "tipoparentescos"]
            self.concesion_de_permisos("beneficiarios", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 10:  # Calles
            self.concesion_de_permisos("calles", con, ins, act, eli, anu, concede)

        elif self.idTabla == 11:  # Cargos
            self.concesion_de_permisos("cargos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 12:  # Categorías
            ref = ["impuestos"]
            self.concesion_de_permisos("categorias", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 13:  # Cheques de Terceros
            ref = ["personas", "tipocheques", "tipodocumentos"]
            self.concesion_de_permisos("chequeterceros", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 14:  # Ciudades
            ref = ["departamentos", "paises"]
            self.concesion_de_permisos("ciudades", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 15:  # Comprobantes de Pago
            ref = ["beneficiarios", "conceptopagos", "contratos", "descuentos",
                "descuentos_periodocobros", "empresas", "horaextraordinarias",
                "gratificaciones", "personas", "salariosminimos", "tipodocumentos"]
            det = ["comprobantepagos_detalles"]
            self.concesion_de_permisos("comprobantepagos", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 16:  # Conceptos de Cobro por Recibos
            self.concesion_de_permisos("conceptorecibos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 17:  # Conceptos de Pago de Salarios
            self.concesion_de_permisos("conceptopagos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 18:  # Contratos
            ref = ["cargos", "diassemana", "formapagos", "periodopagos",
                "personas", "salariosminimos", "tipocontratos",
                "tipodocumentos", "tiposalarios", "turnos"]
            det = ["horarios"]
            self.concesion_de_permisos("contratos", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 19:  # Cotizaciones de Monedas
            ref = ["monedas"]
            self.concesion_de_permisos("cotizaciones", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 20:  # Denominaciones
            ref = ["monedas", "tipodenominaciones"]
            self.concesion_de_permisos("denominaciones", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 21:  # Departamentos, Provincias, Estados
            ref = ["paises"]
            self.concesion_de_permisos("departamentos", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 22:  # Depósitos
            ref = ["establecimientos"]
            self.concesion_de_permisos("depositos", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 23:  # Descuentos
            ref = ["contratos", "motivodescuentos", "periodopagos",
                "personas", "sanciones", "tipodocumentos"]
            det = ["descuentos_periodocobros", "descuentos_sanciones"]
            self.concesion_de_permisos("descuentos", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 24:  # Días No Hábiles
            pass

        elif self.idTabla == 25:  # Empresas
            ref = ["actividadeseconomicas", "barrios", "calles", "ciudades",
                "departamentos", "paises", "personas", "personafisicas",
                "tipocalles", "tipomediocontactos"]
            det = ["empresas_actividadeseconomicas", "empresas_mediocontactos",
                "establecimientos", "direcciones", "direcciones_calles"]
            self.concesion_de_permisos("empresas", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 26:  # Entradas de Empleados
            ref = ["personas", "tipodocumentos"]
            self.concesion_de_permisos("entradas", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 27:  # Establecimientos
            ref = ["barrios", "calles", "ciudades", "departamentos",
                "empresas", "paises", "tipocalles"]
            det = ["direcciones", "direcciones_calles"]
            self.concesion_de_permisos("establecimientos", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 28:  # Estados Civiles
            self.concesion_de_permisos("estadosciviles", con, ins, act, eli, anu, concede)

        elif self.idTabla == 29:  # Facturas de Compra
            ref = ["items", "ordencompras", "ordencompras_detalles",
                "personas", "tipodocumentos", "tipofacturas"]
            det = ["facturacompras_detalles", "facturacompras_inventario",
                "facturacompras_ordenes", "cuentaspagar", "inventario", "lotes"]
            self.concesion_de_permisos("facturacompras", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 30:  # Facturas de Venta
            ref = ["clientes", "items", "lotes", "pedidoventas", "pedidoventas_detalles",
                "personas", "precios", "tipodocumentos", "tipofacturas", "vendedores"]
            det = ["facturaventas_chequeterceros", "facturaventas_detalles",
                "facturaventas_inventario", "facturaventas_monedas",
                "facturaventas_pedidos", "facturaventas_tarjetas",
                "cuentascobrar", "inventario"]
            self.concesion_de_permisos("facturaventas", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 31:  # Formas de Pago
            self.concesion_de_permisos("formapagos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 32:  # Géneros
            self.concesion_de_permisos("generos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 33:  # Gratificaciones
            ref = ["contratos", "motivogratificaciones", "personas", "tipodocumentos"]
            self.concesion_de_permisos("gratificaciones", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 34:  # Horas Extraordinarias
            ref = ["contratos", "personas", "tipodocumentos"]
            self.concesion_de_permisos("horaextraordinarias", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 35:  # Impuestos
            self.concesion_de_permisos("impuestos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 36:  # Ítems
            ref = ["categorias", "depositos", "inventario", "lotes", "marcaitems",
                "presentaciones", "tipoclientes", "unidadmedidas"]
            det = ["inventario", "precios"]
            self.concesion_de_permisos("items", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 37:  # Justificativos Judiciales
            ref = ["contratos", "personas", "tipodocumentos", "tipojuzgados", "turnojuzgados"]
            self.concesion_de_permisos("judiciales", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 38:  # Justificativos por Permisos
            ref = ["contratos", "motivopermisos", "personas", "tipodocumentos"]
            self.concesion_de_permisos("permisos", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 39:  # Justificativos por Sanciones
            ref = ["contratos", "motivosanciones", "personas", "tipodocumentos"]
            self.concesion_de_permisos("sanciones", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 40:  # Marcas de Ítems
            self.concesion_de_permisos("marcaitems", con, ins, act, eli, anu, concede)

        elif self.idTabla == 41:  # Marcas de Tarjetas
            self.concesion_de_permisos("marcatarjetas", con, ins, act, eli, anu, concede)

        elif self.idTabla == 42:  # Marcas de Vehículos
            self.concesion_de_permisos("marcavehiculos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 43:  # Monedas
            ref = ["paises"]
            self.concesion_de_permisos("monedas", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 44:  # Motivos de Ajuste
            self.concesion_de_permisos("motivoajustes", con, ins, act, eli, anu, concede)

        elif self.idTabla == 45:  # Motivos de Descuentos
            self.concesion_de_permisos("motivodescuentos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 46:  # Motivos de Gratificaciones
            self.concesion_de_permisos("motivogratificaciones", con, ins, act, eli, anu, concede)

        elif self.idTabla == 47:  # Motivos de Permisos
            self.concesion_de_permisos("motivopermisos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 48:  # Motivos de Salidas
            self.concesion_de_permisos("motivosalidas", con, ins, act, eli, anu, concede)

        elif self.idTabla == 49:  # Motivos de Sanciones
            self.concesion_de_permisos("motivosanciones", con, ins, act, eli, anu, concede)

        elif self.idTabla == 50:  # Motivos de Traslados
            self.concesion_de_permisos("motivotraslados", con, ins, act, eli, anu, concede)

        elif self.idTabla == 51:  # Notas de Crédito por Compras
            ref = ["facturacompras", "facturacompras_detalles", "items", "lotes", "personas"]
            det = ["notacreditocompras_detalles", "notacreditocompras_inventario", "inventario"]
            self.concesion_de_permisos("notacreditocompras", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 52:  # Notas de Crédito por Ventas
            pass

        elif self.idTabla == 53:  # Notas de Débito por Compras
            ref = ["facturacompras", "items", "lotes", "personas"]
            det = ["notadebitocompras_detalles", "notadebitocompras_inventario", "inventario"]
            self.concesion_de_permisos("notadebitocompras", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 54:  # Notas de Débito por Ventas
            pass

        elif self.idTabla == 55:  # Notas de Remisión
            pass

        elif self.idTabla == 56:  # Ocupaciones
            self.concesion_de_permisos("ocupaciones", con, ins, act, eli, anu, concede)

        elif self.idTabla == 57:  # Órdenes de Compra
            ref = ["formapagos", "inventario", "items", "pedidocompras", "personas", "tipodocumentos"]
            det = ["ordencompras_detalles", "ordencompras_pedidos"]
            self.concesion_de_permisos("ordencompras", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 58:  # Países
            self.concesion_de_permisos("paises", con, ins, act, eli, anu, concede)

        elif self.idTabla == 59:  # Pedidos de Compra
            ref = ["inventario", "items"]
            det = ["pedidocompras_detalles"]
            self.concesion_de_permisos("pedidocompras", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 60:  # Pedidos de Venta
            ref = ["clientes", "items", "personas", "precios", "tipodocumentos", "vendedores"]
            det = ["pedidoventas_detalles"]
            self.concesion_de_permisos("pedidoventas", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 61:  # Periodos de Pago
            self.concesion_de_permisos("periodopagos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 62:  # Personas
            ref = ["barrios", "calles", "ciudades", "departamentos", "estadosciviles",
                "generos", "ocupaciones", "paises", "rolpersonas", "tipocalles",
                "tipoclientes", "tipodocumentos", "tipoempresas", "tipomediocontactos",
                "tiposeguros", "vendedores", "zonaventas"]
            det = ["personafisicas", "personajuridicas", "personas_bancos",
                "personas_direcciones", "personas_mediocontactos", "clientes",
                "direcciones", "direcciones_calles", "empleados"]
            self.concesion_de_permisos("personas", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 63:  # Preavisos
            ref = ["contratos", "entradas", "personas", "tipodocumentos"]
            self.concesion_de_permisos("preavisos", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 64:  # Presentaciones
            self.concesion_de_permisos("presentaciones", con, ins, act, eli, anu, concede)

        elif self.idTabla == 65:  # Puntos de Expedición o Cajas
            ref = ["establecimientos"]
            self.concesion_de_permisos("puntoexpediciones", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 66:  # Recibos de Dinero
            pass

        elif self.idTabla == 67:  # Reposos
            ref = ["contratos", "personas", "tipodocumentos"]
            self.concesion_de_permisos("reposos", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 68:  # Roles de Personas
            self.concesion_de_permisos("rolpersonas", con, ins, act, eli, anu, concede)

        elif self.idTabla == 69:  # Salarios Mínimos
            pass

        elif self.idTabla == 70:  # Salidas
            ref = ["comprobantepagos", "motivosalidas", "personas", "tipodocumentos"]
            det = ["salidas_comprpagos"]
            self.concesion_de_permisos("salidas", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 71:  # Tarjetas
            ref = ["marcatarjetas", "personas", "tipodocumentos", "tipotarjetas"]
            self.concesion_de_permisos("tarjetas", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 72:  # Timbrados
            ref = ["establecimientos", "puntoexpediciones", "tipodocumentocomerciales"]
            self.concesion_de_permisos("timbrados", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 73:  # Tipos de Calles
            self.concesion_de_permisos("tipocalles", con, ins, act, eli, anu, concede)

        elif self.idTabla == 74:  # Tipos de Cheques
            self.concesion_de_permisos("tipocheques", con, ins, act, eli, anu, concede)

        elif self.idTabla == 75:  # Tipos de Clientes
            self.concesion_de_permisos("tipoclientes", con, ins, act, eli, anu, concede)

        elif self.idTabla == 76:  # Tipos de Contratos
            self.concesion_de_permisos("tipocontratos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 77:  # Tipos de Denominaciones
            self.concesion_de_permisos("tipodenominaciones", con, ins, act, eli, anu, concede)

        elif self.idTabla == 78:  # Tipos de Documentos Comerciales
            self.concesion_de_permisos("tipodocumentocomerciales", con, ins, act, eli, anu, concede)

        elif self.idTabla == 79:  # Tipos de Documentos de Identidad
            self.concesion_de_permisos("tipodocumentos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 80:  # Tipos de Empresas
            self.concesion_de_permisos("tipoempresas", con, ins, act, eli, anu, concede)

        elif self.idTabla == 81:  # Tipos de Facturas
            self.concesion_de_permisos("tipofacturas", con, ins, act, eli, anu, concede)

        elif self.idTabla == 82:  # Tipos de Juzgados
            self.concesion_de_permisos("tipojuzgados", con, ins, act, eli, anu, concede)

        elif self.idTabla == 83:  # Tipos de Medios de Contacto
            self.concesion_de_permisos("tipomediocontactos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 84:  # Tipos de Parentescos
            self.concesion_de_permisos("tipoparentescos", con, ins, act, eli, anu, concede)

        elif self.idTabla == 85:  # Tipos de Salarios
            self.concesion_de_permisos("tiposalarios", con, ins, act, eli, anu, concede)

        elif self.idTabla == 86:  # Tipos de Seguros
            self.concesion_de_permisos("tiposeguros", con, ins, act, eli, anu, concede)

        elif self.idTabla == 87:  # Tipos de Tarjetas
            self.concesion_de_permisos("tipotarjetas", con, ins, act, eli, anu, concede)

        elif self.idTabla == 88:  # Tipos de Valores
            self.concesion_de_permisos("tipovalores", con, ins, act, eli, anu, concede)

        elif self.idTabla == 89:  # Turnos de Juzgados
            self.concesion_de_permisos("turnojuzgados", con, ins, act, eli, anu, concede)

        elif self.idTabla == 90:  # Turnos de Trabajo
            pass

        elif self.idTabla == 91:  # Unidades de Medida
            self.concesion_de_permisos("unidadmedidas", con, ins, act, eli, anu, concede)

        elif self.idTabla == 92:  # Usuarios del Sistema
            self.concesion_de_permisos("usuarios", con, ins, act, eli, anu, concede)

        elif self.idTabla == 93:  # Vacaciones
            ref = ["comprobantepagos", "contratos", "entradas", "personas", "tipodocumentos"]
            det = ["vacacionestomadas", "vacaciones_comprpagos"]
            self.concesion_de_permisos("vacaciones", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 94:  # Vehículos
            ref = ["marcavehiculos"]
            self.concesion_de_permisos("vehiculos", con, ins, act, eli, anu, concede, ref)

        elif self.idTabla == 95:  # Vendedores
            ref = ["categorias", "contratos", "items", "personas", "tipodocumentos"]
            det = ["vendedorcomisioncategorias", "vendedorcomisionitems"]
            self.concesion_de_permisos("vendedores", con, ins, act, eli, anu, concede, ref, det)

        elif self.idTabla == 96:  # Zonas de Venta
            self.concesion_de_permisos("zonaventas", con, ins, act, eli, anu, concede)

    def concesion_de_permisos_grupos(self, codigo):
        cant = len(self.obj("grilla").get_model())
        if cant > 0:
            eleccion = Mens.pregunta_generico("¿Desea conservar los permisos?",
            "El usuario ya posee pemisos sobre unas " + str(cant) + " entidades.")

            if not eleccion:
                self.on_btn_per_todos_clicked(0)

        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "*", "grupousuarios_permisos_s",
        " WHERE idGrupoUsuario = " + codigo + " ORDER BY idTabla")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        for i in range(0, cant):
            self.idTabla = datos[i][2]
            con = True if datos[i][4] == 1 else False
            ins = True if datos[i][5] == 1 else False
            act = True if datos[i][6] == 1 else False
            eli = True if datos[i][7] == 1 else False
            anu = True if datos[i][8] == 1 else False
            self.permisos_tablas(con, ins, act, eli, anu, True)

        self.cargar_grilla()
