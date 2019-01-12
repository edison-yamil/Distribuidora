#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import ListStore
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen):
        self.editando = edit
        self.nav = origen

        arch = Op.archivo("abm_fuertes")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de " + self.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("label1").set_text("Código:")
        self.obj("label2").set_text(self.nav.titulodos + ":")

        # Definición de la Longitud máxima de Campos
        if self.nav.tabla == "generos":
            longitud_id = 1
        elif self.nav.tabla in ("tipodocumentos", "unidadmedidas"):
            longitud_id = 5
        else:
            longitud_id = 10

        if self.nav.tabla == "generos":
            longitud_dos = 10
        elif self.nav.tabla in ("estadosciviles", "formapagos", "tipocheques",
        "tipodenominaciones", "tipofacturas", "tipojuzgados", "tiposalarios",
        "tipotarjetas", "tipovalores", "turnojuzgados"):
            longitud_dos = 25
        elif self.nav.tabla in ("motivodescuentos", "motivogratificaciones",
        "motivopermisos", "motivosanciones"):
            longitud_dos = 100
        elif self.nav.tabla == "actividadeseconomicas":
            longitud_dos = 200
        else:
            longitud_dos = 50

        self.obj("txt_00").set_max_length(longitud_id)
        self.obj("txt_01").set_max_length(longitud_dos)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código de " + self.nav.titulo)
        self.obj("txt_01").set_tooltip_text("Ingrese el Nombre o la Descripción de " + self.nav.titulo)

        if self.nav.tabla in ("generos", "tipodocumentos", "unidadmedidas"):
            self.obj("txt_00").grab_focus()
        else:
            self.obj("txt_01").grab_focus()

        # Definición de la Visibilidad de Campos Opcionales
        if self.nav.tabla in ("impuestos", "monedas", "paises", "tipocalles", "zonaventas"):
            self.obj("label3").set_text(self.nav.titulotres + ":")

            # Tamaño de la tercera Casilla
            tam = 225 if self.nav.tabla in ("paises", "zonaventas") else 125
            self.obj("txt_02").set_property('width_request', tam)

            if self.nav.tabla in ("monedas", "tipocalles"):
                longitud_tres = 5
            elif self.nav.tabla == "impuestos":
                longitud_tres = 10
            elif self.nav.tabla == "zonaventas":
                longitud_tres = 100
            else:
                longitud_tres = 50

            if self.nav.tabla == "zonaventas":
                opcion = self.nav.titulotres
            elif self.nav.tabla in ("impuestos", "monedas"):
                opcion = "el " + self.nav.titulotres
            else:
                opcion = "la " + self.nav.titulotres

            self.obj("txt_02").set_max_length(longitud_tres)
            self.obj("txt_02").set_tooltip_text("Ingrese " + opcion + " de " + self.nav.titulo)
            self.obj("hbox3").set_visible(True)
        else:
            self.obj("hbox3").set_visible(False)

        # Definición de la Visibilidad de Campos Booleanos (Radio)
        ver = True if self.nav.tabla in ("conceptopagos", "motivoajustes", "presentaciones") else False

        if self.nav.tabla == "presentaciones":
            self.obj("label4").set_text("Presentación:")
            self.obj("radio1").set_label("Unidad")
            self.obj("radio2").set_label("Fraccionado")
        self.obj("hbox4").set_visible(ver)

        # Definición de la Visibilidad de Campos Booleanos (Check)
        ver = True if self.nav.tabla in ("motivosalidas", "motivosanciones") else False

        if self.nav.tabla == "motivosanciones":
            self.obj("check").set_label("Cobro")
            self.obj("check").set_tooltip_text(
            "La sanción implica la realización de un cobro\n" +
            "al empleado por el perjuicio provocado")
        else:
            self.obj("check").set_tooltip_text(
            "El motivo de salida es justificado, es decir, no implica\n" +
            "el pago/cobro de una indemnización por despido/renuncia")
        self.obj("hbox5").set_visible(ver)

        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            descrip = seleccion.get_value(iterador, 1)

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(descrip)

            if self.nav.tabla in ("generos", "tipodocumentos", "unidadmedidas"):
                self.cond = "'" + self.cond + "'"

            # Acciones con el Tercer Campo
            if self.nav.tabla == "impuestos":
                self.tres = str(seleccion.get_value(iterador, 2))
                self.obj("txt_02").set_text(self.tres)

            elif self.nav.tabla in ("monedas", "paises", "tipocalles", "zonaventas"):
                self.tres = seleccion.get_value(iterador, 2)
                self.tres = "" if self.tres is None else self.tres
                self.obj("txt_02").set_text(self.tres)

            elif self.nav.tabla in ("motivosalidas", "motivosanciones"):
                self.tres = seleccion.get_value(iterador, 2)
                estado = True if self.tres == 1 else False
                self.obj("check").set_active(estado)

            elif self.nav.tabla in ("conceptopagos", "motivoajustes", "presentaciones"):
                self.tres = seleccion.get_value(iterador, 3)
                estado = True if self.tres == 1 else False
                self.obj("radio1").set_active(estado)
        else:
            if self.nav.tabla not in ("generos", "tipodocumentos", "unidadmedidas"):
                self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion, self.nav.tabla, self.nav.campoid))
            if self.nav.tabla in ("conceptopagos", "motivoajustes", "presentaciones"):
                self.obj("radio1").set_active(True)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        v1 = self.obj("txt_00").get_text()
        v2 = self.obj("txt_01").get_text()

        if self.nav.tabla in ("monedas", "paises", "tipocalles", "zonaventas"):
            v3 = self.obj("txt_02").get_text()
            v3 = "NULL" if len(v3) == 0 else "'" + v3 + "'"
        elif self.nav.tabla == "impuestos":
            v3 = self.obj("txt_02").get_text()
        elif self.nav.tabla in ("motivosalidas", "motivosanciones"):
            v3 = "1" if self.obj("check").get_active() else "0"
        elif self.nav.tabla in ("conceptopagos", "motivoajustes", "presentaciones"):
            v3 = "1" if self.obj("radio1").get_active() else "0"

        if self.nav.tabla in ("generos", "tipodocumentos", "unidadmedidas"):
            sql = "'" + v1 + "', '" + v2 + "'"
        else:
            sql = v1 + ", '" + v2 + "'"

        if self.nav.tabla in ("conceptopagos", "impuestos", "monedas",
        "motivoajustes", "motivosalidas", "motivosanciones", "paises",
        "presentaciones", "tipocalles", "zonaventas"):
            sql += ", " + v3

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        if not self.editando:
            Op.insertar(conexion, self.nav.tabla, sql)
        else:
            Op.modificar(conexion, self.nav.tabla, self.cond + ", " + sql)

        conexion.commit()
        conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def verificacion(self, objeto):
        # Verifica Campos Vacios y Numéricos, habilita Botón Guardar
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0:
            estado = False
        else:
            if self.nav.tabla in ("generos", "tipodocumentos", "unidadmedidas"):
                estado = True
            else:
                if Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")):
                    if self.nav.tabla in ("impuestos", "monedas", "paises"):
                        if len(self.obj("txt_02").get_text()) == 0:
                            estado = False
                        else:
                            if self.nav.tabla == "impuestos":
                                estado = Op.comprobar_numero(float, self.obj("txt_02"),
                                "Porcentaje", self.obj("barraestado"), True)
                            else:
                                estado = True
                    else:
                        estado = True
                else:
                    estado = False
        self.obj("btn_guardar").set_sensitive(estado)

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if self.nav.tabla in ("generos", "tipodocumentos", "unidadmedidas"):
                    busq = "" if not self.editando else " AND " + self.nav.campoid + " <> " + self.cond
                    Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla,
                        self.nav.campoid, "'" + valor + "'" + busq, self.obj("txt_00"),
                        self.obj("btn_guardar"), self.obj("barraestado"),
                        "El Código introducido ya ha sido registado.")

                else:
                    if (not self.editando or valor != self.cond) and \
                    Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")):
                        Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla,
                            self.nav.campoid, valor, self.obj("txt_00"),
                            self.obj("btn_guardar"), self.obj("barraestado"),
                            "El Código introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                x = ["La ", "a"] if self.nav.campodos == "Descripcion" else ["El ", "o"]
                busq = "" if not self.editando else " AND " + self.nav.campoid + " <> " + self.cond
                # Comprueba si el nombre o la descripcion ya ha sido registado/a
                Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla,
                    self.nav.campodos, "'" + valor + "'" + busq, self.obj("txt_01"),
                    self.obj("btn_guardar"), self.obj("barraestado"),
                    x[0] + self.nav.titulodos + " introducid" + x[1] + " ya ha sido registad" + x[1] + ".")

            else:
                if self.nav.tabla in ("monedas", "paises"):
                    x = ["La ", "a"] if self.nav.tabla == "paises" else ["El ", "o"]
                    busq = "" if not self.editando else " AND " + self.nav.campoid + " <> " + self.cond
                    # Comprueba si el símbolo o la nacionalidad ya ha sido registado/a
                    Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla,
                        self.nav.campotres, "'" + valor + "'" + busq, self.obj("txt_02"),
                        self.obj("btn_guardar"), self.obj("barraestado"),
                        x[0] + self.nav.titulotres + " introducid" + x[1] + " ya ha sido registad" + x[1] + ".")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)
    celda2 = Op.celdas(1.0)

    col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
    col0.set_sort_column_id(0)

    if self.tabla == "zonaventas":
        ancho = 300
    elif self.tabla in ("motivosalidas", "motivosanciones"):
        ancho = 500
    else:
        ancho = 400

    col1 = Op.columnas(self.titulodos, celda1, 1, True, ancho)
    col1.set_sort_column_id(1)

    lista = [col0, col1]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    if self.tabla in ("conceptopagos", "impuestos", "monedas", "motivoajustes",
    "motivosalidas", "motivosanciones", "paises", "presentaciones",
    "sistematablas", "tipocalles", "zonaventas"):
        if self.tabla == "impuestos":
            col2 = Op.columnas(self.titulotres, celda2, 2, True, 100, 150)
            tipo = float
        elif self.tabla in ("motivosalidas", "motivosanciones"):
            col2 = Op.columna_active(self.titulotres, 2)
            tipo = int
        elif self.tabla == "zonaventas":
            col2 = Op.columnas(self.titulotres, celda1, 2, True, 300)
            tipo = str
        else:
            col2 = Op.columnas(self.titulotres, celda1, 2, True, 100, 150)
            tipo = str

        col2.set_sort_column_id(2)
        col2.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(col2)

        if self.tabla in ("conceptopagos", "motivoajustes", "presentaciones"):
            lista = ListStore(int, str, tipo, int)
        else:
            lista = ListStore(int, str, tipo)
    else:
        tipo = str if self.tabla in ("generos", "tipodocumentos", "unidadmedidas") else int
        lista = ListStore(tipo, str)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 1)

    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
    " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    if self.obj("rad_act").get_active() or self.obj("rad_ina").get_active():
        estado = "1" if self.obj("rad_act").get_active() else "0"
        # Si está buscando inicia las condiciones, sino agrega
        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += self.campotres + " = " + estado

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, "*", self.tabla, opcion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        if self.tabla in ("conceptopagos", "impuestos", "monedas", "motivoajustes",
        "motivosalidas", "motivosanciones", "paises", "presentaciones",
        "sistematablas", "tipocalles", "zonaventas"):
            if self.tabla in ("conceptopagos", "motivoajustes", "presentaciones"):
                if self.tabla == "presentaciones":
                    tercero = "Unidad" if datos[i][2] == 1 else "Fraccionado"
                else: # Ajustes y Conceptos
                    tercero = "Suma" if datos[i][2] == 1 else "Resta"
                lista.append([datos[i][0], datos[i][1], tercero, datos[i][2]])
            else:
                lista.append([datos[i][0], datos[i][1], datos[i][2]])
        else:
            lista.append([datos[i][0], datos[i][1]])

    cant = str(cant) + " registro encontrado." if cant == 1 \
    else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Código", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = self.titulodos, self.campodos
    elif idcolumna == 2:
        col, self.campo_buscar = self.titulotres, self.campotres

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 1)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
        "Cód.: " + valor0 + "\n" + self.titulodos + ": " + valor1)

    self.obj("grilla").get_selection().unselect_all()
    self.obj("barraestado").push(0, "")

    if self.tabla in ("generos", "tipodocumentos", "unidadmedidas"):
        valor0 = "'" + valor0 + "'"

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
    body_de = listado.tabla_celda_just_derecho()
    body_iz = listado.tabla_celda_just_izquierdo()

    listafila = [Par("Código", head), Par(self.titulodos, head)]
    if self.tabla in ("conceptopagos", "impuestos", "monedas", "motivoajustes",
    "motivosalidas", "motivosanciones", "paises", "presentaciones",
    "sistematablas", "tipocalles"):
        listafila.append(Par(self.titulotres, head))
        tamanos = [100, 200, 100]
    else:
        tamanos = [100, 300]

    lista = [listafila]
    for i in range(0, cant):
        listafila = [Par(str(datos[i][0]), body_ce), Par(datos[i][1], body_iz)]

        if self.tabla in ("conceptopagos", "impuestos", "monedas", "motivoajustes",
        "motivosalidas", "motivosanciones", "paises", "presentaciones",
        "sistematablas", "tipocalles", "zonaventas"):
            if self.tabla == "impuestos": estilo = body_de
            elif self.tabla == "paises": estilo = body_iz
            else: estilo = body_ce
            listafila.append(Par(str(datos[i][2]), estilo))

        lista.append(listafila)

    listado.listado(self.titulo, lista, tamanos, A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = seleccion.get_value(iterador, 1)

        if self.tabla in ("impuestos", "paises"):
            valor2 = str(seleccion.get_value(iterador, 2))

        if self.tabla == "actividadeseconomicas":
            self.origen.txt_cod_act.set_text(valor0)
            self.origen.txt_des_act.set_text(valor1)

        elif self.tabla == "barrios":
            self.origen.txt_cod_bar.set_text(valor0)
            self.origen.txt_des_bar.set_text(valor1)

        elif self.tabla == "calles":
            self.origen.txt_cod_cal.set_text(valor0)
            self.origen.txt_des_cal.set_text(valor1)

        elif self.tabla == "conceptopagos":
            self.origen.txt_cod_con.set_text(valor0)
            self.origen.txt_des_con.set_text(valor1)

        elif self.tabla == "impuestos":
            self.origen.txt_cod_imp.set_text(valor0)
            self.origen.txt_des_imp.set_text(valor1)
            self.origen.txt_por_imp.set_text(valor2)

        elif self.tabla == "marcaitems":
            self.origen.txt_cod_mar_it.set_text(valor0)
            self.origen.txt_des_mar_it.set_text(valor1)

        elif self.tabla == "ocupaciones":
            self.origen.txt_cod_ocu.set_text(valor0)
            self.origen.txt_des_ocu.set_text(valor1)

        elif self.tabla == "paises":
            self.origen.txt_cod_pais.set_text(valor0)
            try: self.origen.txt_des_pais.set_text(valor1)
            except: pass
            try: self.origen.txt_nac_pais.set_text(valor2)
            except: pass

        elif self.tabla == "presentaciones":
            self.origen.txt_cod_pres.set_text(valor0)
            self.origen.txt_des_pres.set_text(valor1)

        elif self.tabla == "rolpersonas":
            self.origen.txt_cod_rol.set_text(valor0)
            self.origen.txt_des_rol.set_text(valor1)

        elif self.tabla == "sistematablas":
            self.origen.idTabla = int(valor0)
            self.origen.txt_cod_tabla.set_text(valor0)
            self.origen.txt_des_tabla.set_text(valor1)

        elif self.tabla == "zonaventas":
            self.origen.txt_cod_zona.set_text(valor0)
            self.origen.txt_des_zona.set_text(valor1)

        self.on_btn_salir_clicked(0)
    except:
        pass
