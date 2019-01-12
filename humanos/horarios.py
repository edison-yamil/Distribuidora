#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import ListStore
from clases import mensajes as Mens
from clases import operaciones as Op


class horarios:

    def __init__(self, origen):
        self.origen = origen

        cursor = self.origen.conexion.cursor()
        cursor.execute("SAVEPOINT horario")
        cursor.close()

        arch = Op.archivo("rrhh_horarios")
        self.obj = arch.get_object

        self.obj("ventana").set_default_size(800, 600)
        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        self.obj("ventana").set_title("Registro de Horarios")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_hora_1_ig").set_max_length(8)
        self.obj("txt_hora_2_ig").set_max_length(8)
        self.obj("txt_cod_dif").set_max_length(10)
        self.obj("txt_hora_2_dif").set_max_length(8)
        self.obj("txt_hora_2_dif").set_max_length(8)

        Op.combos_config(self.origen.nav.datos_conexion, self.obj("cmb_primer_dia"), "diassemana", "idDia")
        Op.combos_config(self.origen.nav.datos_conexion, self.obj("cmb_ultimo_dia"), "diassemana", "idDia")
        Op.combos_config(self.origen.nav.datos_conexion, self.obj("cmb_dia"), "diassemana", "idDia")
        Op.combos_config(self.origen.nav.datos_conexion, self.obj("cmb_turno_ig"), "turnos", "idTurno")
        Op.combos_config(self.origen.nav.datos_conexion, self.obj("cmb_turno_dif"), "turnos", "idTurno")

        arch.connect_signals(self)

        self.estadoedicion(False)
        self.config_grilla()
        self.cargar_grilla()

        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_cancelar_clicked(self, objeto):
        cursor = self.origen.conexion.cursor()
        cursor.execute("ROLLBACK TO SAVEPOINT horario")
        cursor.close()

        self.obj("ventana").destroy()

    def on_btn_nuevo_clicked(self, objeto):
        self.editando = False
        self.funcion_horario()

    def on_btn_modificar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Horarios. Luego presione Modificar Horario.")
        else:
            self.editando = True
            self.funcion_horario()

    def on_btn_eliminar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            codhora = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Horarios. Luego presione Eliminar Horario.")
        else:
            dia = seleccion.get_value(iterador, 4)
            entrada = seleccion.get_value(iterador, 5)
            salida = seleccion.get_value(iterador, 6)
            contrato = self.origen.obj("txt_00").get_text()

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Cód. Horario: " + codhora + "\nDía: " + dia + "\n"
                "Hora de Entrada: " + entrada + "\nHora de Salida: " + salida)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.origen.conexion, "horarios", contrato + ", " + codhora)
                self.cargar_grilla()

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

        col0 = Op.columnas("Código", celda0, 0, True, 75, 100)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Cód. Turno", celda0, 1, True, 100, 150)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Turno", celda1, 2, True, 150)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Cód. Día", celda0, 3, True, 100, 150)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Día", celda1, 4, True, 150)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Hora de Entrada", celda0, 5, True, 100, 150)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Hora de Salida", celda0, 6, True, 100, 150)
        col6.set_sort_column_id(6)

        lista = [col0, col1, col2, col3, col4, col5, col6]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(1)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, int, str, int, str, str, str)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla(self):
        cursor = Op.consultar(self.origen.conexion, "idHorario, " +
            "idTurno, Turno, idDia, Dia, HoraEntrada, HoraSalida",
            "horarios_s", " ORDER BY idHorario")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2],
                datos[i][3], datos[i][4], str(datos[i][5]), str(datos[i][6])])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def estadoedicion(self, estado):
        self.obj("hbuttonbox_abm").set_sensitive(not estado)
        self.obj("grilla").set_sensitive(not estado)
        self.obj("hbuttonbox").set_sensitive(not estado)

        self.obj("notebook").set_sensitive(estado)
        self.obj("hbuttonbox_hora").set_visible(estado)

##### Horarios #########################################################

    def funcion_horario(self):
        if self.editando:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.hora = str(seleccion.get_value(iterador, 0))
            idturno = seleccion.get_value(iterador, 1)
            iddia = seleccion.get_value(iterador, 3)
            entrada = seleccion.get_value(iterador, 5)
            salida = seleccion.get_value(iterador, 6)

            self.obj("txt_cod_dif").set_text(self.hora)
            self.obj("txt_hora_1_dif").set_text(entrada)
            self.obj("txt_hora_2_dif").set_text(salida)

            # Asignación de Día en Combo
            model, i = self.obj("cmb_dia").get_model(), 0
            while model[i][0] != iddia: i += 1
            self.obj("cmb_dia").set_active(i)

            # Asignación de Turno en Combo
            model, i = self.obj("cmb_turno_dif").get_model(), 0
            while model[i][0] != idturno: i += 1
            self.obj("cmb_turno_dif").set_active(i)

            self.obj("notebook").set_current_page(1)
            self.obj("notebook").set_show_tabs(False)
        else:
            self.obj("txt_cod_dif").set_text(Op.nuevoid(self.origen.conexion,
                "horarios_s WHERE NroContrato = " + self.origen.obj("txt_00").get_text(),
                "idHorario"))

            self.obj("cmb_primer_dia").set_active(0)
            self.obj("cmb_ultimo_dia").set_active(0)
            self.obj("cmb_turno_ig").set_active(0)
            self.obj("cmb_dia").set_active(0)
            self.obj("cmb_turno_dif").set_active(0)

        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        self.obj("btn_guardar_hora").set_sensitive(False)
        self.estadoedicion(True)

    def on_btn_guardar_hora_clicked(self, objeto):
        cont = self.origen.obj("txt_00").get_text()
        page = self.obj("notebook").get_current_page()

        if page == 0:  # Horas Iguales
            ent = self.obj("txt_hora_1_ig").get_text()
            sal = self.obj("txt_hora_2_ig").get_text()

            guardar, dia = True, self.idPrimerDia
            hora = int(Op.nuevoid(self.origen.conexion, "horarios_s "
                "WHERE NroContrato = " + self.origen.obj("txt_00").get_text(),
                "idHorario"))

            while guardar:
                Op.insertar(self.origen.conexion, "horarios", cont + ", " +
                    str(hora) + ", " + str(self.idTurno) + ", " +
                    str(dia) + ", '" + ent + "', '" + sal + "'")

                if dia == self.idUltimoDia:
                    guardar = False
                    break

                dia += 1
                if dia > 7:  # No puede ser mayor a 7
                    dia = 1
                hora += 1

        else:  # Horas Diferenciadas
            hor = self.obj("txt_cod_dif").get_text()
            ent = self.obj("txt_hora_1_dif").get_text()
            sal = self.obj("txt_hora_2_dif").get_text()

            sql = cont + ", " + hor + ", " + str(self.idTurno) + ", " + \
                str(self.idDia) + ", '" + ent + "', '" + sal + "'"

            if not self.editando:
                Op.insertar(self.origen.conexion, "horarios", sql)
            else:
                Op.modificar(self.origen.conexion, "horarios", self.hora + ", " + sql)

        self.cargar_grilla()
        self.on_btn_cancelar_hora_clicked(0)
        self.obj("btn_guardar").set_sensitive(True)

    def on_btn_cancelar_hora_clicked(self, objeto):
        self.obj("cmb_primer_dia").set_active(-1)
        self.obj("cmb_ultimo_dia").set_active(-1)
        self.obj("cmb_turno_ig").set_active(-1)
        self.obj("cmb_dia").set_active(-1)
        self.obj("cmb_turno_dif").set_active(-1)

        self.obj("txt_hora_1_ig").set_text("")
        self.obj("txt_hora_2_ig").set_text("")
        self.obj("txt_cod_dif").set_text("")
        self.obj("txt_hora_1_dif").set_text("")
        self.obj("txt_hora_2_dif").set_text("")

        self.estadoedicion(False)
        self.obj("notebook").set_current_page(0)
        self.obj("notebook").set_show_tabs(True)
        self.obj("barraestado").push(0, "")

    def verificacion(self, objeto):
        page = self.obj("notebook").get_current_page()
        if page == 0:  # Horas Iguales
            if len(self.obj("txt_hora_1_ig").get_text()) == 0 \
            or len(self.obj("txt_hora_2_ig").get_text()) == 0 \
            or self.idPrimerDia < 0 or self.idUltimoDia < 0 or self.idTurno < 0 :
                estado = False
            else:
                estado = True

        else:  # Horas Diferenciadas
            if len(self.obj("txt_cod_dif").get_text()) == 0 \
            or len(self.obj("txt_hora_1_dif").get_text()) == 0 \
            or len(self.obj("txt_hora_2_dif").get_text()) == 0 \
            or self.idDia < 0 or self.idTurno < 0 :
                estado = False
            else:
                estado = Op.comprobar_numero(int, self.obj("txt_cod_dif"),
                    "Cód. de Horario", self.obj("barraestado"))

        self.obj("btn_guardar_hora").set_sensitive(estado)

    def on_cmb_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            if objeto == self.obj("cmb_dia"):
                self.idDia = model[active][0]
            elif objeto == self.obj("cmb_turno_dif"):
                self.idTurno = model[active][0]
                self.obj("txt_hora_1_dif").set_text(model[active][2])
                self.obj("txt_hora_2_dif").set_text(model[active][3])

            elif objeto == self.obj("cmb_primer_dia"):
                self.idPrimerDia = model[active][0]
            elif objeto == self.obj("cmb_ultimo_dia"):
                self.idUltimoDia = model[active][0]
            elif objeto == self.obj("cmb_turno_ig"):
                self.idTurno = model[active][0]
                self.obj("txt_hora_1_ig").set_text(model[active][2])
                self.obj("txt_hora_2_ig").set_text(model[active][3])

            self.verificacion(0)
        else:
            if objeto in (self.obj("cmb_dia"), self.obj("cmb_primer_dia"),
            self.obj("cmb_ultimo_dia")):
                tipo = "Días"
            elif objeto in (self.obj("cmb_turno_dif"), self.obj("cmb_turno_ig")):
                tipo = "Turnos"
            self.obj("barraestado").push(0, "No existen registros de " + tipo + " en el Sistema.")

    def on_notebook_focus_in_event(self, objeto, evento):
        self.verificacion(0)

    def on_notebook_change_current_page(self, objeto):
        self.verificacion(0)
        print("Cambiando Horarios")

    def on_txt_cod_dif_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
        else:
            # Cuando crea nuevo registro o, al editar, valor es diferente del original,
            # y si es un numero entero, comprueba si ya ha sido registado
            if (not self.editando or valor != self.hora) and \
            Op.comprobar_numero(int, objeto, "Cód. de Horario", self.obj("barraestado")):
                Op.comprobar_unique(self.origen.conexion, "horarios_s", "idHorario",
                    valor + " AND NroContrato = " + self.origen.obj("txt_00").get_text(),
                    objeto, self.obj("btn_guardar_hora"), self.obj("barraestado"),
                    "El Cód. de Horario introducido ya ha sido registado.")
