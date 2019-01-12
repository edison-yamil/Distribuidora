#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gdk import ModifierType
from clases.fechas import calendario
from clases.operaciones import archivo
from clases.operaciones import conectar


class navegador:

    def __init__(self, datos, tab, v_id, tam, tit, v_or=None, otros=None):
        self.datos_conexion = datos
        self.campoid = v_id
        self.tabla = tab
        self.titulo = tit
        self.origen = v_or

        arch = archivo("navegador")
        self.obj = arch.get_object

        if tam == 1:  # ancho ,alto
            self.obj("ventana").set_default_size(600, 350)
        elif tam == 2:
            self.obj("ventana").set_default_size(700, 350)
        elif tam == 3:
            self.obj("ventana").set_default_size(850, 500)
        else:
            self.obj("ventana").set_default_size(950, 600)

        # Condicionamientos especiales enviados desde otras ventanas
        if self.tabla == "ciudades":
            self.condicion = "" if otros is None \
            else "idPais = " + otros[0] + " AND idDepartamento = " + otros[1]

        elif self.tabla == "departamentos":
            self.condicion = "" if otros is None \
            else "idPais = " + otros

        elif self.tabla == "personas":  # Para filtrar entre Humanos y Empresas
            if otros is not None:
                # Empresa: Empresa (1-True), Humano (0-False)
                # idRolPersona: Proveedor (3), Cliente (2), Empleado (1)
                self.condicion = otros
            else:
                self.condicion = ""

        elif self.tabla == "items":
            # Para mostrar solo los relacionados con la Factura de Compra o Venta para Notas de Crédito
            if otros is not None:
                self.condicion, self.otroscampos = otros[0], otros[1]
            else:
                self.condicion = self.otroscampos = ""

        elif self.tabla == "puntoexpediciones":
            # Para filtrar por el Establecimiento
            self.condicion = "" if otros is None else "NroEstablecimiento = " + otros

        elif self.tabla == "ordencompras":
            # Para mostrar solo los Aprobados y filtrar por el Proveedor
            self.condicion = "" if otros is None else "Aprobado = 1 AND " + otros

        elif self.tabla == "facturacompras":
            # Para mostrar solo los Confirmados y filtrar por el Proveedor
            self.condicion = "" if otros is None else "Confirmado = 1 AND " + otros

        elif self.tabla == "contratos":  # Para filtrar por el Empleado
            self.condicion = "" if otros is None else otros

        if self.tabla == "sistematablas":  # Solo permite búsquedas
            self.obj("hbuttonbox").set_visible(False)

        # Transforma boton Eliminar en boton Anular
        if self.tabla in ("chequeterceros", "comprobantepagos", "contratos", "timbrados"):
            self.obj("image_eliminar").set_property('stock', 'gtk-find-and-replace')
            self.obj("label_eliminar").set_text("Anular")
            self.eli_anu = "Anular"
        else:
            self.eli_anu = "Eliminar"

        # Permite filtrar entre registros activos e inactivos, o anulados o no
        if self.tabla in ("chequeterceros", "comprobantepagos", "conceptopagos",
        "contratos", "establecimientos", "facturacompras", "items",
        "motivoajustes", "motivosalidas", "motivosanciones", "notacreditocompras",
        "notadebitocompras", "ordencompras", "personas", "preavisos",
        "presentaciones", "puntoexpediciones", "timbrados"):
            # Referenciales Fuertes
            if self.tabla in ("conceptopagos", "motivoajustes"):
                self.obj("rad_act").set_label("Mostrar Solo los que Suman.")
                self.obj("rad_ina").set_label("Mostrar Solo los que Restan.")

            elif self.tabla == "motivosalidas":
                self.obj("rad_act").set_label("Mostrar Solo los Justificados.")
                self.obj("rad_ina").set_label("Mostrar Solo los Injustificados.")

            elif self.tabla == "motivosanciones":
                self.obj("rad_act").set_label("Mostrar Solo por los que se Cobran.")
                self.obj("rad_ina").set_label("Mostrar Solo por los que NO se Cobran.")

            elif self.tabla == "presentaciones":
                self.obj("rad_act").set_label("Mostrar Solo los Unitarios.")
                self.obj("rad_ina").set_label("Mostrar Solo los Fraccionados.")

            # Referenciales Débiles y Transacciones
            elif self.tabla in ("chequeterceros", "timbrados"):
                self.obj("rad_act").set_label("Mostrar Solo Anulados.")
                self.obj("rad_ina").set_label("Mostrar Solo NO Anulados.")

            elif self.tabla in ("comprobantepagos", "notacreditocompras",
            "notadebitocompras", "facturacompras"):
                self.obj("rad_act").set_label("Mostrar Solo Confirmados.")
                self.obj("rad_ina").set_label("Mostrar Solo NO Confirmados.")

                if self.tabla == "facturacompras":
                    estado = True if otros is None else False
                    self.obj("hbox_act").set_visible(estado)  # Muestra solo confirmados y no puede cambiar

            elif self.tabla == "contratos":
                self.obj("rad_act").set_label("Mostrar Solo Vigentes.")
                self.obj("rad_ina").set_label("Mostrar Solo NO Vigentes.")

                estado = True if otros is None else False  # Muestra solo vigentes y no puede cambiar
                self.obj("hbox_act").set_visible(estado)

            elif self.tabla == "ordencompras":
                self.obj("rad_act").set_label("Mostrar Solo Aprobados.")
                self.obj("rad_ina").set_label("Mostrar Solo NO Aprobados.")

                estado = True if otros is None else False  # Muestra solo aprobados y no puede cambiar
                self.obj("hbox_act").set_visible(estado)

            elif self.tabla == "preavisos":
                self.obj("rad_act").set_label("Mostrar Solo los del Trabajador.")
                self.obj("rad_ina").set_label("Mostrar Solo los del Empleador.")

            self.obj("rad_todos").set_active(True)
        else:
            self.obj("hbox_act").set_visible(False)

        self.obj("hbox_fecha").set_visible(False)
        self.obj("ventana").set_position(1)
        self.obj("ventana").set_title("Navegar - Registros de " + self.titulo)
        arch.connect_signals(self)

        self.ubica_archivo()
        self.permisos_user()
        self.archivo.config_grilla(self)
        self.archivo.cargar_grilla(self)

        if self.origen is not None:
            self.obj("ventana").set_modal(True)
        self.obj("ventana").show()

    def on_btn_nuevo_clicked(self, objeto):
        self.archivo.funcion_abm(False, self)

    def on_btn_modificar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Modificar.")
        else:
            self.archivo.funcion_abm(True, self)

    def on_btn_eliminar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione " + self.eli_anu + ".")
        else:
            self.archivo.eliminar(self)

    def on_btn_listar_clicked(self, objeto):
        self.archivo.listar_grilla(self)

    def on_btn_salir_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_filtrar_clicked(self, objeto):
        self.archivo.cargar_grilla(self)

    def on_btn_buscar_clicked(self, objeto):
        if self.campo_buscar in ("Fecha", "FechaCobro", "FechaEmision",
        "FechaEntrada", "FechaExpediente", "FechaFin", "FechaHora",
        "FechaHoraExp", "FechaInicio", "FechaNacFamiliar", "FechaNacimiento",
        "FechaPreaviso", "FechaSalida", "FechaVencimiento", "PruebaInicio",
        "PruebaFin"):
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

    def on_txt_buscar_key_press_event(self, objeto, evento):
        if evento.keyval == 65293:  # Presionando Enter
            self.on_btn_filtrar_clicked(0)

    def on_grilla_cursor_changed(self, objeto):
        lista = self.obj("grilla").get_model()

        if len(lista) > 0:  # Debe haber datos cargados
            if self.tabla == "comprobantepagos":
                seleccion, iterador = self.obj("grilla").get_selection().get_selected()
                confirmado = seleccion.get_value(iterador, 18)

                if confirmado == 1:  # Si está confirmado (ya fue expedido) solo puede anular
                    self.obj("btn_eliminar").set_sensitive(self.puede_anular)
                    self.obj("image_eliminar").set_property('stock', 'gtk-find-and-replace')
                    self.obj("label_eliminar").set_text("Anular")
                    self.eli_anu = "Anular"
                else:
                    self.obj("btn_eliminar").set_sensitive(self.puede_eliminar)
                    self.obj("image_eliminar").set_property('stock', 'gtk-delete')
                    self.obj("label_eliminar").set_text("Eliminar")
                    self.eli_anu = "Eliminar"

    def on_grilla_row_activated(self, objeto, fila, col):
        if self.origen is None:
            if self.obj("btn_modificar").get_sensitive():
                self.on_btn_modificar_clicked(0)
        else:
            self.archivo.seleccion(self)

    def on_grilla_key_press_event(self, objeto, evento):
        if self.obj("btn_eliminar").get_sensitive():
            if evento.keyval == 65535:  # Presionando Suprimir (Delete)
                self.on_btn_eliminar_clicked(0)

    def on_ventana_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 102:  # Presionando Tecla 'F'
                self.obj("txt_buscar").grab_focus()

    def on_rad_toggled(self, objeto):
        if objeto.get_active():
            self.archivo.cargar_grilla(self)

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()

        # En estas tablas no busca por el tercer campo
        if self.tabla not in ("conceptopagos", "motivoajustes",
        "motivosalidas", "motivosanciones", "presentaciones") or i != 2:
            self.obj("grilla").set_search_column(i)

            self.obj("txt_buscar").set_editable(True)
            self.obj("hbox_fecha").set_visible(False)
            self.archivo.columna_buscar(self, i)

    def ubica_archivo(self):
        if self.tabla in ("actividadeseconomicas", "barrios", "calles",
        "cargos", "conceptopagos", "conceptorecibos", "estadosciviles",
        "formapagos", "generos", "impuestos", "marcaitems", "marcatarjetas",
        "marcavehiculos", "motivoajustes", "motivodescuentos",
        "motivogratificaciones", "motivopermisos", "motivosalidas",
        "motivosanciones", "motivotraslados", "ocupaciones", "paises",
        "periodopagos", "presentaciones", "rolpersonas", "sistematablas",
        "tipocalles", "tipocheques", "tipoclientes", "tipocontratos",
        "tipodenominaciones", "tipodocumentos", "tipodocumentocomerciales",
        "tipoempresas", "tipofacturas", "tipojuzgados", "tipomediocontactos",
        "tipoparentescos", "tiposalarios", "tiposeguros", "tipotarjetas",
        "tipovalores", "turnojuzgados", "unidadmedidas", "zonaventas"):  # 45 tablas
            from registros import fuertes
            self.archivo = fuertes

            if self.tabla in ("barrios", "calles", "impuestos", "monedas", "paises",
            "sistematablas", "tipodocumentos", "tipodocumentocomerciales"):
                self.titulodos, self.campodos = "Nombre", "Nombre"
            else:
                self.titulodos, self.campodos = "Descripción", "Descripcion"

            if self.tabla in ("conceptopagos", "motivoajustes"):
                self.titulotres, self.campotres = "Efecto", "Suma"
            elif self.tabla == "impuestos":
                self.titulotres = self.campotres = "Porcentaje"
            elif self.tabla == "monedas":
                self.titulotres, self.campotres = "Símbolo", "Simbolo"
            elif self.tabla == "motivosalidas":
                self.titulotres = self.campotres = "Justificado"
            elif self.tabla == "motivosanciones":
                self.titulotres = self.campotres = "Cobro"
            elif self.tabla == "paises":
                self.titulotres, self.campotres = "Nacionalidad", "Nacionalidad"
            elif self.tabla == "presentaciones":
                self.titulotres, self.campotres = "Presentación", "Unidad"
            elif self.tabla == "sistematablas":
                self.titulotres = self.campotres = "Tabla"
            elif self.tabla == "tipocalles":
                self.titulotres = self.campotres = "Abreviatura"
            elif self.tabla == "zonaventas":
                self.titulotres = self.campotres = "Observaciones"

        elif self.tabla == "categorias":
            from registros import categorias
            self.archivo = categorias

        elif self.tabla in ("ciudades", "departamentos"):
            from registros import ciudad_depart
            self.archivo = ciudad_depart

        elif self.tabla == "depositos":
            from registros import depositos
            self.archivo = depositos

        elif self.tabla == "items":
            from registros import items
            self.archivo = items

        elif self.tabla == "grupousuarios":
            import usuarios_grupos
            self.archivo = usuarios_grupos

        elif self.tabla == "personas":
            from registros import personas
            self.archivo = personas

        # Registros de Puntos de Expedición

        elif self.tabla == "chequeterceros":
            from registros import cheques
            self.archivo = cheques

        elif self.tabla == "cotizaciones":
            from registros import cotizaciones
            self.archivo = cotizaciones

        elif self.tabla == "denominaciones":
            from registros import denominaciones
            self.archivo = denominaciones

        elif self.tabla == "establecimientos":
            from registros import establecimientos
            self.archivo = establecimientos

        elif self.tabla == "monedas":
            from registros import monedas
            self.archivo = monedas

        elif self.tabla == "puntoexpediciones":
            from registros import puntoexpediciones
            self.archivo = puntoexpediciones

        elif self.tabla == "tarjetas":
            from registros import tarjetas
            self.archivo = tarjetas

        elif self.tabla == "timbrados":
            from registros import timbrados
            self.archivo = timbrados

        elif self.tabla == "vehiculos":
            from registros import vehiculos
            self.archivo = vehiculos

        # Registros de Compras

        elif self.tabla == "facturacompras":
            from compras import facturas
            self.archivo = facturas

        elif self.tabla in ("notacreditocompras", "notadebitocompras"):
            from compras import notas_credito_debito
            self.archivo = notas_credito_debito

        elif self.tabla == "ordencompras":
            from compras import ordenes
            self.archivo = ordenes

        elif self.tabla == "pedidocompras":
            from compras import pedidos
            self.archivo = pedidos

        # Registros de Empleados

        elif self.tabla == "beneficiarios":
            from humanos import beneficiarios
            self.archivo = beneficiarios

        elif self.tabla == "contratos":
            from humanos import contratos
            self.archivo = contratos

        elif self.tabla == "empresas":
            from humanos import empresas
            self.archivo = empresas

        elif self.tabla == "vendedores":
            from humanos import vendedores
            self.archivo = vendedores

        # Registros de Movimientos

        elif self.tabla == "entradas":
            from humanos import entradas
            self.archivo = entradas

        elif self.tabla == "permisos":
            from humanos import permisos
            self.archivo = permisos

        elif self.tabla == "sanciones":
            from humanos import sanciones
            self.archivo = sanciones

        elif self.tabla == "judiciales":
            from humanos import judiciales
            self.archivo = judiciales

        elif self.tabla == "reposos":
            from humanos import reposos
            self.archivo = reposos

        elif self.tabla == "vacaciones":
            from humanos import vacaciones
            self.archivo = vacaciones

        elif self.tabla == "preavisos":
            from humanos import preavisos
            self.archivo = preavisos

        elif self.tabla == "salidas":
            from humanos import salidas
            self.archivo = salidas

        # Registros de Remuneraciones

        elif self.tabla == "aguinaldos":
            from humanos import aguinaldos
            self.archivo = aguinaldos

        elif self.tabla == "anticipos":
            from humanos import anticipos
            self.archivo = anticipos

        elif self.tabla == "descuentos":
            from humanos import descuentos
            self.archivo = descuentos

        elif self.tabla == "gratificaciones":
            from humanos import gratificaciones
            self.archivo = gratificaciones

        elif self.tabla == "horaextraordinarias":
            from humanos import horaextraordinarias
            self.archivo = horaextraordinarias

        elif self.tabla == "comprobantepagos":
            from humanos import comprobantepagos
            self.archivo = comprobantepagos

        else:
            print("Archivo no encontrado")

    def permisos_user(self):
        self.puede_eliminar = self.puede_anular = False

        self.obj("btn_nuevo").set_sensitive(False)
        self.obj("btn_modificar").set_sensitive(False)
        self.obj("btn_eliminar").set_sensitive(False)

        conexion = conectar(self.datos_conexion)
        cursor = conexion.cursor()
        cursor.execute("SELECT ROUTINE_NAME FROM procedimientos_s")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        for i in range(0, cant):
            procedimiento = datos[i][0]
            if procedimiento == self.tabla + "_i":
                self.obj("btn_nuevo").set_sensitive(True)
            elif procedimiento == self.tabla + "_u":
                self.obj("btn_modificar").set_sensitive(True)
            elif procedimiento == self.tabla + "_d":
                self.puede_eliminar = True
                self.obj("btn_eliminar").set_sensitive(True)
            elif procedimiento == self.tabla + "_a":
                self.puede_anular = True
                self.obj("btn_eliminar").set_sensitive(True)
