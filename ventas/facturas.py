#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from decimal import Decimal
from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class facturas:

    def __init__(self, datos, tab, est, cja, num):
        self.datos_conexion = datos
        self.tabla = tab
        self.estab = est
        self.caja = cja
        self.numero = num

        arch = Op.archivo("venta_facturas")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_title("Facturación por Ventas")
        self.obj("ventana").set_modal(True)

        self.obj("txt_02").set_max_length(10)
        self.obj("txt_03").set_max_length(10)
        self.obj("txt_04").set_max_length(10)
        self.obj("txt_04_1").set_max_length(12)

        self.obj("txt_it_00").set_max_length(10)
        self.obj("txt_it_00_1").set_max_length(10)
        self.obj("txt_it_01").set_max_length(20)
        self.obj("txt_it_02").set_max_length(10)
        self.obj("txt_it_03").set_max_length(12)
        self.obj("txt_it_04").set_max_length(12)
        self.obj("txt_it_06").set_max_length(5)
        self.obj("txt_it_07").set_max_length(12)

        self.obj("btn_nuevo").set_tooltip_text("Presione este botón para Crear una nueva Factura")
        self.obj("btn_anular").set_tooltip_text("Presione este botón para Anular una Factura")
        self.obj("btn_cuentas").set_tooltip_text("Presione este botón para Registrar las Cuotas por Facturación a Crédito")
        self.obj("btn_forma_cobro").set_tooltip_text("Presione este botón para Registrar los Cheques o Tarjetas" +
        "\nutilizados por el cliente para efectuar el pago por la Factura")
        self.obj("btn_confirmar").set_tooltip_text("Presione este botón para Guardar la Factura")
        self.obj("btn_cancelar").set_tooltip_text("Presione este botón para Cancelar la Factura sin guardar los datos")
        self.obj("btn_salir").set_tooltip_text("Presione este botón para Cerrar esta ventana")

        self.obj("cmb_tipo_fact").set_tooltip_text("Seleccione el tipo de Factura")
        self.obj("cmb_tipo_doc").set_tooltip_text("Seleccione el Tipo de Documento de Identidad del Cliente")

        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("un Pedido y cargar la Factura"))
        self.obj("txt_03").set_tooltip_text(Mens.usar_boton("al Vendedor que realizó la operación"))
        self.obj("txt_03_1").set_tooltip_text("Nombre y Apellido del Vendedor")

        self.obj("txt_04").set_tooltip_text(Mens.usar_boton("al Cliente que se expide la Factura"))
        self.obj("btn_cliente").set_tooltip_text("Presione este botón para buscar datos de un Cliente")
        self.obj("txt_04_1").set_tooltip_text("Ingrese el Número de Documento de Identidad del Cliente")
        self.obj("txt_04_2").set_tooltip_text("Nombre y Apellido o Razón Social del Cliente")
        self.obj("txt_04_3").set_tooltip_text("Dirección de la residencia del Cliente")

        self.obj("btn_nuevo_item").set_tooltip_text("Presione este botón para agregar un nuevo Item")
        self.obj("btn_modificar_item").set_tooltip_text("Presione este botón para modificar datos de un Item")
        self.obj("btn_eliminar_item").set_tooltip_text("Presione este botón para eliminar un Item")

        self.obj("txt_it_00").set_tooltip_text(Mens.usar_boton("el Ítem a facturar"))
        self.obj("txt_it_00_1").set_tooltip_text("Ingrese el Código de Barras de Ítem")
        self.obj("txt_it_00_2").set_tooltip_text("Nombre o Descripción del Ítem")
        self.obj("txt_it_00_3").set_tooltip_text("Presentación del Ítem seleccionado")
        self.obj("txt_it_00_4").set_tooltip_text("Categoría del Ítem seleccionado")
        self.obj("txt_it_00_5").set_tooltip_text("Porcentaje del IVA que grava al Ítem")
        self.obj("txt_it_01").set_tooltip_text(Mens.usar_boton("el Lote del Ítem a facturar"))
        self.obj("txt_it_01_1").set_tooltip_text("Fecha de Vencimiento del Lote seleccionado")
        self.obj("txt_it_02").set_tooltip_text(Mens.usar_boton("el Depósito del Ítem a facturar"))
        self.obj("txt_it_02_1").set_tooltip_text("Descripción del Depósito seleccionado")
        self.obj("txt_it_03").set_tooltip_text("Ingrese la Cantidad de Ítems vendidos")
        self.obj("txt_it_04").set_tooltip_text("Ingrese el Precio de Venta del Ítems seleccionado")
        self.obj("txt_it_05").set_tooltip_text("SubTotal sin Descuento")
        self.obj("txt_it_06").set_tooltip_text("Ingrese el Porcentaje de Descuento")
        self.obj("txt_it_07").set_tooltip_text("Ingrese el Monto de Descuento")
        self.obj("txt_it_08").set_tooltip_text("SubTotal con Descuento")

        self.txt_nro_ped, self.cond_pedido = self.obj("txt_02"), None
        self.txt_cod_vnd, self.txt_nom_vnd = self.obj("txt_03"), self.obj("txt_03_1")
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_04"), self.obj("txt_04_2")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_04_1"), self.obj("cmb_tipo_doc")
        self.txt_dir_per = self.obj("txt_04_3")

        self.idTipoCliente, self.PorcDescMaximo = "1", 0  # Normal
        self.idTipoDoc = self.idTipoFact = -1
        self.txt_cod_it, self.txt_bar_it = self.obj("txt_it_00"), self.obj("txt_it_00_1")
        self.txt_nom_it, self.txt_des_pres = self.obj("txt_it_00_2"), self.obj("txt_it_00_3")
        self.txt_des_cat, self.txt_por_imp = self.obj("txt_it_00_4"), self.obj("txt_it_00_5")
        self.txt_cost_it = self.obj("txt_costo")

        self.txt_lote_nro, self.txt_lote_fch = self.obj("txt_it_01"), self.obj("txt_it_01_1")
        self.txt_cod_dep, self.txt_des_dep = self.obj("txt_it_02"), self.obj("txt_it_02_1")

        Op.combos_config(self.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.datos_conexion, self.obj("cmb_tipo_fact"), "tipofacturas", "idTipoFactura")
        arch.connect_signals(self)

        self.encabezado_guardado = True
        self.permisos_user()
        self.estadoitems(False)
        self.estadoedicion(False)
        self.config_grilla_detalles()
        self.limpiarcampos()

        self.obj("ventana").show()
        self.buscar_nro_timbrado()

    def on_btn_nuevo_clicked(self, objeto):
        self.buscar_nro_factura()
        self.cond_pedido = None
        self.encabezado_guardado = False
        self.editando = False
        self.estadoedicion(True)

        self.conexion = Op.conectar(self.datos_conexion)
        self.obj("cmb_tipo_fact").set_active(0)
        self.obj("cmb_tipo_doc").set_active(0)
        self.obj("chk_efectivo").set_active(True)
        self.obj("txt_04").grab_focus()

    def on_btn_anular_clicked(self, objeto):
        self.funcion_anulacion()

    def on_btn_cuentas_clicked(self, objeto):
        from compras.cuotas import cuotas

        if self.obj("btn_salir").get_sensitive():
            cuotas(self.datos_conexion, "cuentascobrar")
        else:
            self.guardar_encabezado()

            if self.idTipoFact == 2:
                self.conexion.commit()
                self.obj("barraestado").push(0, "La Factura ha sido Guardada.")

                # Evita que la Factura pueda ser modificada
                self.estadoencabezado(False)
                self.obj("hbuttonbox1").set_sensitive(False)
                self.obj("grilla").set_sensitive(False)
                self.obj("btn_cancelar").set_sensitive(False)

                # Datos -> Nro. Factura, Nro. Timbrado y Total
                datos = [self.obj("txt_00_3").get_text(),
                    self.obj("txt_01_1").get_text(),
                    self.obj("txt_total").get_text()]

                cuotas(self.datos_conexion, "cuentascobrar", datos, self.conexion)
            else:
                self.obj("barraestado").push(0, "Solamente las Facturas a Crédito poseen Cuentas a Cobrar.")

    def on_btn_forma_cobro_clicked(self, objeto):
        self.guardar_encabezado()

        nro = self.obj("txt_00_3").get_text()
        timb = self.obj("txt_01_1").get_text()
        total = self.obj("txt_total").get_text()

        from ventas.cobros import cobros
        cobros(self.datos_conexion, self.conexion, self.tabla, total, nro, timb)

    def on_btn_confirmar_clicked(self, objeto):
        self.guardar_encabezado()
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        self.limpiarcampos()
        self.estadoedicion(False)

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión

        self.limpiarcampos()
        self.estadoedicion(False)

    def on_btn_salir_clicked(self, objeto):
        self.obj("ventana").destroy()

    def buscar_nro_timbrado(self):
        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "NroTimbrado, FechaVencimiento",
            "timbrados_s", " WHERE NroEstablecimiento = " + self.estab +
            " AND NroPuntoExpedicion = " + self.caja + " AND Fecha" +
            "Vencimiento > CURRENT_DATE() AND idTipoDocumentoComercial = 1 " +
            "AND Anulado <> 1 ORDER BY NroTimbrado")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            # Datos del Timbrado
            self.obj("txt_01_1").set_text(str(datos[0][0]))
            self.obj("txt_01_2").set_text(Cal.mysql_fecha(datos[0][1]))
            # Datos del Punto de Expedición
            self.obj("txt_00_1").set_text(Op.cadenanumeros(self.estab, 3))
            self.obj("txt_00_2").set_text(Op.cadenanumeros(self.caja, 3))
        else:
            Mens.error_generico("¡ERROR!", "No se ha encontrado un Timbrado\npara este Punto de Expedición." +
            "\nConsulte al Administrador del Sistema.\n\nLa ventana de Facturación se cerrará.")
            self.obj("ventana").destroy()

    def permisos_user(self):
        self.btn_nuevo = self.btn_anular = False

        conexion = Op.conectar(self.datos_conexion)
        cursor = conexion.cursor()
        cursor.execute("SELECT ROUTINE_NAME FROM procedimientos_s")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        for i in range(0, cant):
            procedimiento = datos[i][0]

            if procedimiento == self.tabla + "_i":
                self.btn_nuevo = True
            elif procedimiento == self.tabla + "_a":
                self.btn_anular = True

        self.obj("btn_nuevo").set_sensitive(self.btn_nuevo)
        self.obj("btn_anular").set_sensitive(self.btn_anular)

##### Encabezado #######################################################

    def on_btn_cliente_clicked(self, objeto):
        from clases.llamadas import personas
        personas(self.datos_conexion, self, "Cliente = 1")

    def on_btn_pedido_clicked(self, objeto):
        eleccion = True if len(self.obj("txt_02").get_text()) == 0 \
            else Mens.pregunta_generico("¿Está seguro?",
                "Elegir una NUEVA NOTA DE PEDIDO eliminará todos los registros actuales.")

        if eleccion:
            from ventas.pedidos import nota_pedido_buscar
            nota_pedido_buscar(self)

    def on_btn_vendedor_clicked(self, par):
        from clases.llamadas import vendedores
        vendedores(self.datos_conexion, self)

    def verificacion(self, objeto):
        if len(self.obj("txt_03").get_text()) == 0 or len(self.obj("txt_04").get_text()) == 0 \
        or self.idTipoFact == -1 or self.idTipoDoc == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_03"), "Cód. de Vendedor", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_04"), "Cód. de Cliente", self.obj("barraestado")):
                if len(self.obj("txt_02").get_text()) == 0:
                    estado = True
                else:
                    estado = Op.comprobar_numero(int, self.obj("txt_02"),
                        "Nro. de Pedido", self.obj("barraestado"))
            else:
                estado = False

        self.encabezado_guardado = False
        self.estadoguardar(estado)

    def on_cmb_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            if objeto == self.obj("cmb_tipo_doc"):
                self.idTipoDoc = model[active][0]
                self.focus_out_event(self.obj("txt_04_1"), 0)  #  Nro. Documento
            elif objeto == self.obj("cmb_tipo_fact"):
                self.idTipoFact = model[active][0]
        else:
            if objeto == self.obj("cmb_tipo_doc"):
                tipo = "Tipos de Documentos de Identidad"
            elif objeto == self.obj("cmb_tipo_fact"):
                tipo = "Tipos de Factura"
            self.obj("barraestado").push(0, "No existen registros de " + tipo + " en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_02"):
                    self.on_btn_pedido_clicked(0)
                elif objeto == self.obj("txt_03"):
                    self.on_btn_pedido_clicked(0)
                elif objeto in (self.obj("txt_04"), self.obj("txt_04_1")):
                    self.on_btn_cliente_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            if objeto == self.obj("txt_02"):
                self.on_pedido_focus_out_event(objeto, 0)
            else:
                self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_02"):
            tipo = "a Nota de Pedido"
        elif objeto == self.obj("txt_03"):
            tipo = " Vendedor"
        elif objeto in (self.obj("txt_04"), self.obj("txt_04_1")):
            tipo = " Cliente"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un" + tipo + ".")

    def on_pedido_focus_out_event(self, objeto, evento):
        valor = self.obj("txt_02").get_text()
        if len(valor) == 0:
            # Si ya se había seleccionado una Nota de Pedido
            if self.cond_pedido is not None:
                eleccion = Mens.pregunta_generico("¿Está seguro?",
                "Al ELIMINAR la NOTA DE PEDIDO se eliminarán todos los registros actuales.")

                if eleccion:  # Decide eliminar todos los Ítems
                    fact = self.obj("txt_00_3").get_text()
                    timb = self.obj("txt_01_1").get_text()
                    datos = self.obj("grilla").get_model()
                    cant = len(datos)

                    for i in range(0, cant):
                        Op.eliminar(self.conexion, self.tabla + "_detalles",
                            timb + ", " + fact + ", " + str(datos[i][0]))

                    self.cargar_grilla_detalles()
                    self.estadoguardar(False)

                    # Se elimina relación entre Factura y Nota de Pedido
                    Op.eliminar(self.conexion, self.tabla + "_pedidos", timb + ", " + fact)
                    self.cond_pedido = None
        else:
            self.cargar_item_nota_pedido()

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()

        if len(valor) == 0:
            self.obj("barraestado").push(0, "")

            if objeto == self.obj("txt_03"):  # Código de Vendedor
                self.obj("txt_03_1").set_text("")

            elif objeto == self.obj("txt_04"):  # Código de Cliente
                self.obj("txt_04_1").set_text("")
                self.obj("txt_04_2").set_text("")
                self.obj("txt_04_3").set_text("")

            elif objeto == self.obj("txt_04_1") \
            and len(self.obj("txt_04").get_text()) == 0:  # Nro. Documento de Cliente
                self.obj("txt_04_2").set_text("")
                self.obj("txt_04_3").set_text("")
        else:
            if objeto == self.obj("txt_03"):
                if Op.comprobar_numero(int, objeto, "Cód. de Vendedor", self.obj("barraestado")):
                    conexion = Op.conectar(self.datos_conexion)
                    cursor = Op.consultar(conexion, "NombreApellido",
                        "vendedores_s", " WHERE idVendedor = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("txt_03_1").set_text(datos[0][0])
                        self.obj("barraestado").push(0, "")
                        self.verificacion(0)
                    else:
                        self.estadoguardar(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "El Cód. de Vendedor no es válido.")
                        self.obj("txt_03_1").set_text("")

            elif objeto == self.obj("txt_04"):
                if Op.comprobar_numero(int, objeto, "Cód. de Cliente", self.obj("barraestado")):
                    self.buscar_clientes(objeto, "idPersona", valor, "Cód. de Cliente")

            elif objeto == self.obj("txt_04_1"):
                self.buscar_clientes(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDoc + "'", "Nro. de Documento")

    def buscar_clientes(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "idPersona, RazonSocial, " +
            "NroDocumento, idTipoDocumento, DireccionPrincipal", "personas_s",
            " WHERE " + campo + " = " + valor + " AND Cliente = 1")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            direc = "" if datos[0][4] is None else datos[0][4]

            self.obj("txt_04").set_text(str(datos[0][0]))
            self.obj("txt_04_1").set_text(datos[0][2])
            self.obj("txt_04_2").set_text(datos[0][1])
            self.obj("txt_04_3").set_text(direc)

            # Asignación de Tipo de Documento en Combo
            model, i = self.obj("cmb_tipo_doc").get_model(), 0
            while model[i][0] != datos[0][3]: i += 1
            self.obj("cmb_tipo_doc").set_active(i)

            # Buscar Tipo de Cliente y Vendedor
            conexion = Op.conectar(self.datos_conexion)
            cursor = Op.consultar(conexion, "idTipoCliente, idVendedor, " +
                "NombreApellido", "clientes_s", " WHERE idCliente = " + str(datos[0][0]))
            datos = cursor.fetchall()
            cant = cursor.rowcount
            conexion.close()  # Finaliza la conexión

            self.idTipoCliente = str(datos[0][0])
            self.obj("txt_03").set_text(str(datos[0][1]))
            self.obj("txt_03_1").set_text(datos[0][2])

            self.obj("barraestado").push(0, "")
            self.verificacion(0)

        else:
            self.estadoguardar(False)
            objeto.grab_focus()
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_04_1") if objeto == self.obj("txt_04") else self.obj("txt_04")
            otro.set_text("")

            self.obj("txt_04_2").set_text("")
            self.obj("txt_04_3").set_text("")

    def buscar_nro_factura(self):
        timb = self.obj("txt_01_1").get_text()

        conexion = Op.conectar(self.datos_conexion)
        # Buscar datos del Timbrado de la Factura
        cursor = Op.consultar(conexion, "NroInicio, NroFin",
            "timbrados_s", " WHERE NroTimbrado = " + timb + " AND " +
            "idTipoDocumentoComercial = 1 AND FechaVencimiento > " +
            "CURRENT_DATE() AND Anulado <> 1")
        datos = cursor.fetchall()

        # Buscar datos de la Apertura de Caja actual
        cursor = Op.consultar(conexion, "IFNULL(NroInicio, 0)", "cajaaperturas",
            " WHERE NroApertura = " + self.numero + " AND " +
            "NroEstablecimiento = " + self.estab + " AND " +
            "NroPuntoExpedicion = " + self.caja + " AND " +
            "idTipoDocComercial = 1")
        apertura = cursor.fetchall()[0][0]
        conexion.close()  # Finaliza la conexión

        ini, fin = datos[0][0], datos[0][1]
        num_fact = Op.nuevoid(self.datos_conexion, self.tabla + "_s" +
            " WHERE NroTimbrado = " + timb, "NroFactura")

        if int(num_fact) >= ini and int(num_fact) <= fin:
            if int(num_fact) >= apertura:
                self.obj("txt_00_3").set_text(Op.cadenanumeros(num_fact, 7))
            else:
                self.obj("txt_00_3").set_text(Op.cadenanumeros(apertura, 7))
        elif int(num_fact) < ini:
            self.obj("txt_00_3").set_text(Op.cadenanumeros(str(ini), 7))
        elif int(num_fact) > fin:
            Mens.error_generico("¡ERROR!", "El nuevo Número de Factura es mayor " +
            "al último número\npara el Timbrado asignado a este Punto de Expedición." +
            "\n\nHable con el Administrador par resolver el problema.")
            self.estadoedicion(False)
            self.limpiarcampos()

    def guardar_encabezado(self):
        # Si el encabezado no ha sido registrado
        if not self.encabezado_guardado:
            fact = self.obj("txt_00_3").get_text()
            timb = self.obj("txt_01_1").get_text()
            vend = self.obj("txt_03").get_text()
            cli = self.obj("txt_04").get_text()

            sql = timb + ", " + fact + ", " + cli + ", " + str(self.idTipoFact) + ", " + \
                vend + ", " + self.estab + ", " + self.caja + ", " + self.numero

            if not self.editando:
                Op.insertar(self.conexion, self.tabla, sql)
            else:
                Op.modificar(self.conexion, self.tabla,
                    self.cond_timb + ", " + self.cond_fact + ", " + sql)

            self.cond_timb = timb  # Nuevo NroTimbrado original
            self.cond_fact = fact  # Nuevo NroFactura original
            self.encabezado_guardado = self.editando = True

    def cargar_item_nota_pedido(self):
        fact = self.obj("txt_00_3").get_text()
        timb = self.obj("txt_01_1").get_text()
        pedido = self.obj("txt_02").get_text()

        # Solo cargará los datos si la Nota de Pedido anterior es diferente a la nueva
        if self.cond_pedido != pedido:
            conexion = Op.conectar(self.datos_conexion)
            cursor = Op.consultar(conexion, "idCliente", "pedidoventas_s",
                " WHERE NroPedidoVenta = " + pedido)
            datos = cursor.fetchall()
            cant = cursor.rowcount
            conexion.close()  # Finaliza la conexión

            # Si existe la Nota de Pedido seleccionada cargará los nuevos datos
            if cant > 0:
                self.obj("txt_04").set_text(str(datos[0][0]))
                self.focus_out_event(self.obj("txt_04"), 0)
                self.guardar_encabezado()

                # Relaciona la Factura con la Nota de Pedido
                if self.cond_pedido is None:
                    Op.insertar(self.conexion, self.tabla + "_pedidos",
                        timb + ", " + fact + ", " + pedido)
                else:
                    Op.modificar(self.conexion, self.tabla + "_pedidos",
                        self.cond_pedido + ", " + timb + ", " + fact + ", " + pedido)
                self.cond_pedido = pedido

                # Eliminando Items de la Nota de Pedido anterior
                datos = self.obj("grilla").get_model()
                cant = len(datos)
                if cant > 0:  # Si existen ítems registrados en la Factura, los elimina
                    for i in range(0, cant):
                        Op.eliminar(self.conexion, self.tabla + "_detalles",
                            timb + ", " + fact + ", " + str(datos[i][0]))

                # Obteniendo Items desde Nota de Pedido seleccionada
                conexion = Op.conectar(self.datos_conexion)
                cursor = Op.consultar(conexion, "idItem, Cantidad, Precio",
                    "pedidoventas_detalles_s", " WHERE NroPedidoVenta = " + pedido)
                datos = cursor.fetchall()
                cant = cursor.rowcount
                conexion.close()  # Finaliza la conexión

                # Cargando Items desde Nota de Pedido seleccionada
                for i in range(0, cant):
                    # Buscar Precio de Costo / IVA del Item
                    conexion = Op.conectar(self.datos_conexion)
                    cursor = Op.consultar(conexion, "PrecioCosto, Porcentaje",
                        "items_s", " WHERE idItem = " + str(datos[i][0]))
                    datos_item = cursor.fetchall()
                    conexion.close()  # Finaliza la conexión

                    det = Op.nuevoid(self.conexion, self.tabla + "_detalles_s" +
                        " WHERE NroTimbrado = " + timb + " AND NroFactura = " + fact,
                        "idDetalle")

                    Op.insertar(self.conexion, self.tabla + "_detalles",
                        timb + ", " + fact + ", " + det + ", " +
                        str(datos[i][0]) + ", " + str(datos[i][1]) + ", " +
                        str(datos_item[0][0]) + ", " + str(datos[i][2]) +
                        ", 0, " + str(datos_item[0][1]))

                self.cargar_grilla_detalles()
                self.estadoguardar(True)
            else:
                Mens.error_generico("Nota de Pedido desconocida",
                "NO existe la Nota de Pedido Nº " + pedido + ".\n" +
                "Verifique que los datos introducidos estén correctos.")
                self.obj("txt_02").grab_focus()

    def limpiarcampos(self):
        self.obj("grilla").get_model().clear()
        self.obj("txt_00_4").set_text(Cal.fecha_hoy())

        self.obj("chk_efectivo").set_active(False)
        self.obj("chk_cheque").set_active(False)
        self.obj("chk_tarjeta").set_active(False)

        self.obj("txt_00_3").set_text("")
        self.obj("txt_02").set_text("")
        self.obj("txt_03").set_text("")
        self.obj("txt_03_1").set_text("")
        self.obj("txt_04").set_text("")
        self.obj("txt_04_1").set_text("")
        self.obj("txt_04_2").set_text("")
        self.obj("txt_04_3").set_text("")

        self.obj("txt_descuento").set_text("")
        self.obj("txt_exenta").set_text("")
        self.obj("txt_iva5").set_text("")
        self.obj("txt_iva10").set_text("")
        self.obj("txt_letras").set_text("")
        self.obj("txt_total").set_text("")
        self.obj("txt_liq_iva5").set_text("")
        self.obj("txt_liq_iva10").set_text("")
        self.obj("txt_total_liq_iva").set_text("")

        self.obj("cmb_tipo_fact").set_active(-1)
        self.obj("cmb_tipo_doc").set_active(-1)
        self.obj("barraestado").push(0, "")

    def estadoedicion(self, estado):
        if self.btn_nuevo:
            self.obj("btn_nuevo").set_sensitive(not estado)
        if self.btn_anular:
            self.obj("btn_anular").set_sensitive(not estado)

        self.obj("btn_cancelar").set_sensitive(estado)
        self.obj("btn_salir").set_sensitive(not estado)

        self.estadoencabezado(estado)
        self.estadoguardar(False)

        if self.obj("btn_salir").get_sensitive():
            self.obj("btn_cuentas").set_sensitive(True)

    def estadoencabezado(self, estado):
        self.obj("txt_00_1").set_sensitive(estado)
        self.obj("txt_00_2").set_sensitive(estado)
        self.obj("txt_00_3").set_sensitive(estado)

        self.obj("cmb_tipo_fact").set_sensitive(estado)
        self.obj("chk_efectivo").set_sensitive(estado)
        self.obj("chk_cheque").set_sensitive(estado)
        self.obj("chk_tarjeta").set_sensitive(estado)
        self.obj("txt_02").set_sensitive(estado)
        self.obj("btn_pedido").set_sensitive(estado)

        self.obj("txt_03").set_sensitive(estado)
        self.obj("txt_03_1").set_sensitive(estado)
        self.obj("btn_vendedor").set_sensitive(estado)

        self.obj("txt_04").set_sensitive(estado)
        self.obj("btn_cliente").set_sensitive(estado)
        self.obj("cmb_tipo_doc").set_sensitive(estado)
        self.obj("txt_04_1").set_sensitive(estado)
        self.obj("txt_04_2").set_sensitive(estado)
        self.obj("txt_04_3").set_sensitive(estado)

    def estadoguardar(self, estado):
        self.obj("hbuttonbox1").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)

        # Obligatoriamente debe poseer un detalle para poder Guardar
        guardar = True if estado and len(self.obj("grilla").get_model()) > 0 else False

        self.obj("btn_cuentas").set_sensitive(guardar)
        self.obj("btn_forma_cobro").set_sensitive(guardar)
        self.obj("btn_confirmar").set_sensitive(guardar)

    def estadoitems(self, estado):
        self.obj("vbox1").set_visible(not estado)
        self.obj("btn_cancelar").set_sensitive(not estado)

        self.obj("vbox2").set_visible(estado)
        self.obj("hbuttonbox2").set_visible(estado)

##### Ítems ############################################################

    def config_grilla_detalles(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Cód.", celda0, 0, True, 50, 100)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Nombre", celda1, 1, True, 200, 400)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Cantidad", celda2, 2, True, 100, 150)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Precio Unitario", celda2, 3, True, 100, 150)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Porc. Desc.", celda2, 4, True, 100, 150)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Monto Desc.", celda2, 5, True, 100, 150)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Exentas", celda2, 6, True, 100, 150)
        col6.set_sort_column_id(6)
        col7 = Op.columnas("Gravadas 5%", celda2, 7, True, 100, 150)
        col7.set_sort_column_id(7)
        col8 = Op.columnas("Gravadas 10%", celda2, 8, True, 100, 150)
        col8.set_sort_column_id(8)

        lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(1)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, float, float, float, float,
            float, float, float, int, float)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_detalles(self):
        timb = self.obj("txt_01_1").get_text()
        fact = self.obj("txt_00_3").get_text()

        # Cargar campos de Totales y Liquidación del IVA
        cursor = Op.consultar(self.conexion, "TotalDescuento, SubTotalExenta, " +
            "SubTotalGravada5, SubTotalGravada10, Total, TotalLiquidacionIVA5, " +
            "TotalLiquidacionIVA10, TotalLiquidacionIVA", self.tabla + "_s",
            " WHERE NroTimbrado = " + timb + " AND NroFactura = " + fact)
        datos = cursor.fetchall()

        self.obj("txt_descuento").set_text(str(datos[0][0]))
        self.obj("txt_exenta").set_text(str(datos[0][1]))
        self.obj("txt_iva5").set_text(str(datos[0][2]))
        self.obj("txt_iva10").set_text(str(datos[0][3]))
        self.obj("txt_total").set_text(str(datos[0][4]))
        self.obj("txt_liq_iva5").set_text(str(datos[0][5]))
        self.obj("txt_liq_iva10").set_text(str(datos[0][6]))
        self.obj("txt_total_liq_iva").set_text(str(datos[0][7]))

        # Cargar los Detalles de la Factura
        cursor = Op.consultar(self.conexion, "idDetalle, Nombre, Cantidad, " +
            "PrecioVenta, PorcDescuento, MontoDescuento, Exenta, Gravada5, " +
            "Gravada10, idItem, PrecioCosto", self.tabla + "_detalles_s",
            " WHERE NroTimbrado = " + timb + " AND NroFactura = " + fact +
            " ORDER BY idDetalle")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2],
                datos[i][3], datos[i][4], datos[i][5], datos[i][6],
                datos[i][7], datos[i][8], datos[i][9], datos[i][10]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_item_clicked(self, objeto):
        self.editando_item = False
        self.funcion_items()

    def on_btn_modificar_item_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.cond_det = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Modificar.")
        else:
            self.editando_item = True
            self.funcion_items()

    def on_btn_eliminar_item_clicked(self, objeto):
        self.guardar_encabezado()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            detalle = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Eliminar.")
        else:
            fact = self.obj("txt_00_3").get_text()
            timb = self.obj("txt_01_1").get_text()

            item = str(seleccion.get_value(iterador, 9))
            nomb = seleccion.get_value(iterador, 1)
            cant = str(seleccion.get_value(iterador, 2))
            precio = str(seleccion.get_value(iterador, 3))

            eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
                "\nCód. Ítem: " + item + "\nNombre: " + nomb +
                "\nCantidad: " + cant + "\nPrecio Unitario: " + precio)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                # Buscar datos del movimiento en tabla Inventario
                cursor = Op.consultar(self.conexion, "idMovimiento", self.tabla + "_inventario_s",
                    " WHERE NroTimbrado = " + timb + " AND NroFactura = '" + fact + "'" +
                    " AND idDetalle = " + detalle + " AND idItem = " + item)
                mov = str(cursor.fetchall()[0][0])

                # Eliminar datos en tabla que relaciona el movimiento con tabla Inventario
                Op.eliminar(self.conexion, self.tabla + "_inventario",
                    timb + ", '" + fact + "', " + detalle + ", " + item + ", " + mov)

                # Eliminar datos del movimiento en tabla Inventario
                Op.eliminar(self.conexion, "inventario", item + ", " + mov)

                # Eliminar datos del movimiento en tabla Detalles
                Op.eliminar(self.conexion, self.tabla + "_detalles",
                    timb + ", " + fact + ", " + item)

                self.cargar_grilla_detalles()
                self.estadoguardar(True)

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_item_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_item_clicked(0)

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla").set_search_column(i)

##### Agregar-Modificar Ítems ##########################################

    def funcion_items(self):
        self.guardar_encabezado()

        if self.editando_item:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.cond_det = str(seleccion.get_value(iterador, 0))
            cant = str(seleccion.get_value(iterador, 2))
            venta = str(seleccion.get_value(iterador, 3))
            porc = str(seleccion.get_value(iterador, 4))
            desc = str(seleccion.get_value(iterador, 5))
            self.cond_item = str(seleccion.get_value(iterador, 9))
            compra = str(seleccion.get_value(iterador, 10))

            self.obj("txt_it_00").set_text(self.cond_item)
            self.obj("txt_it_03").set_text(cant)
            self.obj("txt_it_04").set_text(venta)
            self.obj("txt_it_06").set_text(porc)
            self.obj("txt_it_07").set_text(desc)

            self.on_item_focus_out_event(self.obj("txt_it_00"), 0)
            self.on_item_focus_out_event(self.obj("txt_it_03"), 0)
            self.on_item_focus_out_event(self.obj("txt_it_07"), 0)

            # Buscar Depósito y Lotes
            fact = self.obj("txt_00_3").get_text()
            timb = self.obj("txt_01_1").get_text()

            conexion = Op.conectar(self.datos_conexion)
            cursor = Op.consultar(conexion, "idDeposito, Deposito, " +
                "NroLote, FechaVencimiento", self.tabla + "_inventario_s",
                " WHERE NroTimbrado = " + timb + " AND NroFactura = " + fact +
                " AND idDetalle = " + self.cond_det)
            datos = cursor.fetchall()
            cant = cursor.rowcount
            conexion.close()  # Finaliza la conexión

            if cant > 0:
                iddep = "" if datos[0][0] is None else str(datos[0][0])
                dep = "" if datos[0][1] is None else datos[0][1]
                lote = "" if datos[0][2] is None else datos[0][2]
                ven = "" if datos[0][3] is None else Cal.mysql_fecha(datos[0][3])

                self.obj("txt_it_02").set_text(lote)
                self.obj("txt_it_02_1").set_text(ven)
                self.obj("txt_it_03").set_text(iddep)
                self.obj("txt_it_03_1").set_text(dep)
        else:
            self.limpiar_campos()
            self.obj("txt_it_00").grab_focus()

        self.obj("btn_guardar_item").set_sensitive(False)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        self.estadoguardar(False)
        self.estadoitems(True)

    def on_btn_guardar_item_clicked(self, objeto):
        self.guardar_encabezado()

        fact = self.obj("txt_00_3").get_text()
        timb = self.obj("txt_01_1").get_text()

        if not self.editando_item:
            det = Op.nuevoid(self.conexion, self.tabla + "_detalles_s" +
                " WHERE NroTimbrado = " + timb + " AND NroFactura = " + fact,
                "idDetalle")
        else:
            det = self.cond_det

        item = self.obj("txt_it_00").get_text()
        lote = self.obj("txt_it_01").get_text()
        dep = self.obj("txt_it_02").get_text()
        cant = self.obj("txt_it_03").get_text()
        costo = self.obj("txt_costo").get_text()
        venta = self.obj("txt_it_04").get_text()
        desc = self.obj("txt_it_06").get_text()
        iva = self.obj("txt_it_00_5").get_text()

        lote = "NULL" if len(lote) == 0 else "'" + lote + "'"
        dep = "NULL" if len(dep) == 0 else dep

        sql = timb + ", " + fact + ", " + det + ", " + item + ", " + \
            cant + ", " + costo + ", " + venta + ", " + desc + ", " + iva

        if not self.editando_item:
            Op.insertar(self.conexion, self.tabla + "_detalles", sql)

            # Datos de la Tabla Inventario
            mov = Op.nuevoid(self.conexion, "inventario" +
                " WHERE idItem = " + item, "idMovimiento")

            Op.insertar(self.conexion, "inventario", item + ", " + mov + ", " +
                 dep + ", " + lote + ", -" + cant + ", NULL")
            Op.insertar(self.conexion, self.tabla + "_inventario",
                timb + ", " + fact + ", " + det + ", " + item + ", " + mov)
        else:
            # Buscar datos del movimiento en tabla Inventario
            cursor = Op.consultar(self.conexion, "idMovimiento",
                self.tabla + "_inventario_s", " WHERE NroTimbrado = " + timb +
                " AND NroFactura = " + fact + " AND idDetalle = " + det +
                " AND idItem = " + item)
            mov = str(cursor.fetchall()[0][0])

            Op.modificar(self.conexion, "inventario", self.cond_item + ", " +
                item + ", " + mov + ", " + dep + ", " + lote + ", -" + cant + ", NULL")
            Op.modificar(self.conexion, self.tabla + "_detalles", self.cond_det + ", " + sql)

        self.cargar_grilla_detalles()
        self.limpiar_campos()
        self.obj("txt_it_00").grab_focus()

    def on_btn_cancelar_item_clicked(self, objeto):
        self.limpiar_campos()

        self.estadoitems(False)
        self.estadoguardar(True)

    def on_btn_item_clicked(self, objeto):
        from clases.llamadas import items
        items(self.datos_conexion, self)

    def on_btn_lote_clicked(self, objeto):
        item = self.obj("txt_it_00").get_text()

        if len(item) == 0:
            self.obj("barraestado").push(0, "Para buscar un Lote primero debe elegir un Ítem")
        else:
            from compras.lotes import lotes_buscar
            lotes_buscar(self, item)

    def on_btn_deposito_clicked(self, objeto):
        from clases.llamadas import depositos
        depositos(self.datos_conexion, self)

    def verificacion_item(self, objeto):
        if len(self.obj("txt_it_00").get_text()) == 0 or len(self.obj("txt_it_03").get_text()) == 0 \
        or len(self.obj("txt_it_04").get_text()) == 0 or len(self.obj("txt_it_06").get_text()) == 0 \
        or len(self.obj("txt_it_07").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_it_00"), "Cód. de Ítem", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_it_03"), "Cantidad de Ítems", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_it_04"), "Precio Unitario", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_it_06"), "Porcentaje de Descuento", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_it_07"), "Monto de Descuento", self.obj("barraestado")):
                if len(self.obj("txt_it_00").get_text()) == 0:
                    estado = True
                else:
                    estado = Op.comprobar_numero(int, objeto, "Cód. de Depósito", self.obj("barraestado"))
            else:
                estado = False
        self.obj("btn_guardar_item").set_sensitive(estado)

    def on_item_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto in (self.obj("txt_it_00"), self.obj("txt_it_00_1")):
                    self.on_btn_item_clicked(0)
                elif objeto == self.obj("txt_it_01"):
                    self.on_btn_lote_clicked(0)
                elif objeto == self.obj("txt_it_02"):
                    self.on_btn_deposito_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.on_item_focus_out_event(objeto, 0)

    def on_item_focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_it_00"), self.obj("txt_it_00_1")):
            tipo = "Ítem"
        elif objeto == self.obj("txt_it_01"):
            tipo = "Lote"
        elif objeto == self.obj("txt_it_02"):
            tipo = "Depósito"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un " + tipo + ".")

    def on_item_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_it_00"):  # Código del Ítem
                self.obj("txt_it_00_1").set_text("")
                self.limpiar_items()
            elif objeto == self.obj("txt_it_00_1") and len(self.obj("txt_it_00").get_text()) == 0:
                self.obj("txt_it_00").set_text("")
                self.limpiar_items()
            elif objeto == self.obj("txt_it_01"):  # Código del Lote
                self.obj("txt_it_01_1").set_text("")
            elif objeto == self.obj("txt_it_02"):  # Código del Depósito
                self.obj("txt_it_02_1").set_text("")
        else:
            if objeto == self.obj("txt_it_00"):
                if Op.comprobar_numero(int, objeto, "Cód. de Ítem", self.obj("barraestado")):
                    self.buscar_items(objeto, "idItem", valor, "Cód. de Ítem")

            elif objeto == self.obj("txt_it_00_1"):
                self.buscar_items(objeto, "CodigoBarras", "'" + valor + "'", "Código de Barras")

            elif objeto == self.obj("txt_it_01"):
                item = self.obj("txt_it_00").get_text()
                if len(item) > 0:
                    conexion = Op.conectar(self.datos_conexion)
                    cursor = Op.consultar(conexion, "FechaVencimiento",
                        "lotes", " WHERE NroLote = '" + valor + "' AND " +
                        "idItem = " + item)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("txt_it_01_1").set_text(Cal.mysql_fecha(datos[0][0]))
                        self.obj("barraestado").push(0, "")
                        self.verificacion_item(0)
                    else:
                        self.obj("btn_guardar_item").set_sensitive(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "El Nro. de Lote no es válido.")
                        self.obj("txt_it_01_1").set_text("")

            elif objeto == self.obj("txt_it_02"):
                if Op.comprobar_numero(int, objeto, "Cód. de Depósito", self.obj("barraestado")):
                    conexion = Op.conectar(self.datos_conexion)
                    cursor = Op.consultar(conexion, "Descripcion",
                        "depositos_s", " WHERE idDeposito = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("txt_it_02_1").set_text(datos[0][0])
                        self.obj("barraestado").push(0, "")
                        self.verificacion_item(0)
                    else:
                        self.obj("btn_guardar_item").set_sensitive(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "El Cód. de Depósito no es válido.")
                        self.obj("txt_it_02_1").set_text("")

            elif objeto == self.obj("txt_it_03"):
                if Op.comprobar_numero(float, objeto, "Cantidad de Ítems", self.obj("barraestado")):
                    precio = self.obj("txt_it_04").get_text()
                    if len(precio) > 0:
                        monto = round(Decimal(valor) * Decimal(precio), 2)
                        self.obj("txt_it_05").set_text(str(monto))

            elif objeto == self.obj("txt_it_04"):
                if Op.comprobar_numero(float, objeto, "Precio Unitario", self.obj("barraestado")):
                    cant = self.obj("txt_it_03").get_text()
                    if len(cant) > 0:
                        monto = round(Decimal(valor) * Decimal(cant), 2)
                        self.obj("txt_it_05").set_text(str(monto))

            elif objeto == self.obj("txt_it_06"):
                if Op.comprobar_numero(float, objeto, "Porcentaje de Descuento", self.obj("barraestado")):
                    if Decimal(valor) > Decimal(self.PorcDescMaximo):
                        self.obj("btn_guardar_item").set_sensitive(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "El Porcentaje de Descuento " +
                            "no puede ser mayor a " + str(self.PorcDescMaximo) + ".")
                    else:
                        subtotal = self.obj("txt_it_05").get_text()
                        if len(subtotal) > 0:
                            descuento = round((Decimal(subtotal) * Decimal(valor)) / 100, 2)
                            monto = round(Decimal(subtotal) - descuento, 2)

                            self.obj("txt_it_07").set_text(str(descuento))
                            self.obj("txt_it_08").set_text(str(monto))

            elif objeto == self.obj("txt_it_07"):
                if Op.comprobar_numero(float, objeto, "Monto de Descuento", self.obj("barraestado")):
                    subtotal = self.obj("txt_it_05").get_text()
                    if len(subtotal) > 0:
                        porcentaje = round((Decimal(valor) * 100) / Decimal(subtotal), 2)
                        monto = round(Decimal(subtotal) - Decimal(valor), 2)

                        self.obj("txt_it_06").set_text(str(porcentaje))
                        self.obj("txt_it_08").set_text(str(monto))

    def buscar_items(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "idItem, CodigoBarras, " +
            "Nombre, Presentacion, Categoria, Porcentaje, PrecioCosto",
            "items_s", " WHERE " + campo + " = " + valor)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            codbar = "" if datos[0][1] is None else datos[0][1]

            self.obj("txt_it_00").set_text(str(datos[0][0]))
            self.obj("txt_it_00_1").set_text(codbar)
            self.obj("txt_it_00_2").set_text(datos[0][2])
            self.obj("txt_it_00_3").set_text(datos[0][3])
            self.obj("txt_it_00_4").set_text(datos[0][4])
            self.obj("txt_it_00_5").set_text(str(datos[0][5]))
            self.obj("txt_costo").set_text(str(datos[0][6]))

            # Buscar Precio de Venta
            conexion = Op.conectar(self.datos_conexion)
            cursor = Op.consultar(conexion, "IFNULL(PrecioVenta, 0), " +
                "IFNULL(PorcDescMaximo, 0)", "precios_s",
                " WHERE idItem = " + str(datos[0][0]) +
                " AND idTipoCliente = " + self.idTipoCliente)
            datos = cursor.fetchall()
            conexion.close()  # Finaliza la conexión

            self.obj("txt_it_04").set_text(str(datos[0][0]))
            self.PorcDescMaximo = datos[0][1]
        else:
            objeto.grab_focus()
            self.obj("btn_guardar_item").set_sensitive(False)
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_it_00_1") if objeto == self.obj("txt_it_00") else self.obj("txt_it_00")
            self.limpiar_items()
            otro.set_text("")

    def limpiar_campos(self):
        self.obj("txt_it_00").set_text("")
        self.obj("txt_it_00_1").set_text("")
        self.limpiar_items()

        self.obj("txt_it_01").set_text("")
        self.obj("txt_it_01_1").set_text("")
        self.obj("txt_it_02").set_text("")
        self.obj("txt_it_02_1").set_text("")
        self.obj("txt_it_03").set_text("")
        self.obj("txt_it_04").set_text("")
        self.obj("txt_it_05").set_text("")
        self.obj("txt_it_06").set_text("0.0")
        self.obj("txt_it_07").set_text("0.0")
        self.obj("txt_it_08").set_text("")

    def limpiar_items(self):
        self.obj("txt_it_00_2").set_text("")
        self.obj("txt_it_00_3").set_text("")
        self.obj("txt_it_00_4").set_text("")
        self.obj("txt_it_00_5").set_text("")

##### Ventana de Anulación de Facturas de Venta ########################

    def funcion_anulacion(self):
        factura_buscar(self.datos_conexion)


class factura_buscar:

    def __init__(self, conex, v_or=None, cond=""):
        self.datos_conexion = conex
        self.origen = v_or
        self.condicion = cond

        arch = Op.archivo("buscador")
        self.obj = arch.get_object

        self.obj("ventana").set_title("Seleccione una Factura")
        self.obj("ventana").set_default_size(950, 500)
        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        # Transforma boton Seleccionar en boton Anular
        if self.origen is None:
            self.obj("img_busq_seleccionar").set_property('stock', 'gtk-find-and-replace')
            self.obj("label_busq_seleccionar").set_text("Anular")
            self.obj("label_busq_cancelar").set_text("Salir")

        self.config_grilla_buscar()
        self.cargar_grilla_buscar()

        arch.connect_signals(self)
        self.obj("ventana").show()

    def on_btn_busq_seleccionar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla_buscar").get_selection().get_selected()
            timb = str(seleccion.get_value(iterador, 0))
            fact = str(seleccion.get_value(iterador, 1))
            fecha = seleccion.get_value(iterador, 2)
        except:
            tipo = "Anular" if self.origen is None else "Seleccionar"
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione " + tipo + ".")
        else:
            cod_per = seleccion.get_value(iterador, 16)
            tip_doc = seleccion.get_value(iterador, 3)
            nro_doc = seleccion.get_value(iterador, 4)
            rzn_scl = seleccion.get_value(iterador, 5)
            dir_per = seleccion.get_value(iterador, 6)

            if self.origen is None:
                # Anular Factura de Venta seleccionada
                eleccion = Mens.pregunta_anular("Seleccionó:\n\n" +
                    "Nro. Timbrado: " + timb + "\nNro. Factura: " + fact +
                    "\nCliente: " + rzn_scl + "\nFecha de Expedición: " + fecha)

                self.obj("grilla_buscar").get_selection().unselect_all()
                self.obj("barraestado").push(0, "")

                if eleccion:
                    conexion = Op.conectar(self.datos_conexion)
                    Op.anular(conexion, "facturaventas", timb + ", " + fact)
                    conexion.commit()
                    conexion.close()  # Finaliza la conexión
                    self.cargar_grilla_buscar()
            else:
                # Entrega de Datos de la Factura
                self.origen.fact_nro.set_text(fact)
                self.origen.fact_timb.set_text(timb)

                try:
                    self.origen.fact_fecha.set_text(fecha)
                except:
                    pass

                try:
                    self.origen.cod_per = cod_per
                    self.origen.nro_doc.set_text(nro_doc)
                    self.origen.rzn_scl.set_text(rzn_scl)
                    self.origen.dir_per.set_text(dir_per)
                except:
                    pass

                try:  # Asignación de Tipo de Documento en Combo
                    model, i = self.origen.tip_doc.get_model(), 0
                    while model[i][0] != tip_doc: i += 1
                    self.origen.tip_doc.set_active(i)
                except:
                    pass

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
            self.on_btn_filtrar_clicked(0)

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
        col2 = Op.columnas("Fecha de Expedición", celda0, 2, True, 225, 250)
        col2.set_sort_column_id(15)  # Para ordenarse usa la fila 15
        col3 = Op.columnas("Tipo Doc. Cliente", celda0, 3, True, 100, 200)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Nro. Doc. Cliente", celda0, 4, True, 100, 200)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Razón Social", celda1, 5, True, 200, 300)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Dirección Principal", celda1, 6, True, 200, 500)
        col6.set_sort_column_id(6)
        col7 = Op.columnas("Cód. Tipo Fact.", celda0, 7, True, 75, 150)
        col7.set_sort_column_id(7)
        col8 = Op.columnas("Tipo de Factura", celda1, 8, True, 125)
        col8.set_sort_column_id(8)
        col9 = Op.columnas("Total", celda2, 9, True, 150, 250)
        col9.set_sort_column_id(9)
        col10 = Op.columnas("Total Liq. IVA", celda2, 10, True, 150, 250)
        col10.set_sort_column_id(10)
        col11 = Op.columnas("Alias de Usuario", celda1, 11, True, 100, 200)
        col11.set_sort_column_id(11)
        col12 = Op.columnas("Nro. Documento", celda0, 12, True, 100, 200)
        col12.set_sort_column_id(12)
        col13 = Op.columnas("Nombre de Usuario", celda1, 13, True, 200, 300)
        col13.set_sort_column_id(13)
        col14 = Op.columna_active("Anulado", 14)
        col14.set_sort_column_id(14)

        lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8,
            col9, col10, col11, col12, col13]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla_buscar").append_column(columna)
        self.obj("grilla_buscar").append_column(col14)

        self.obj("grilla_buscar").set_rules_hint(True)
        self.obj("grilla_buscar").set_search_column(1)
        self.obj("grilla_buscar").set_property('enable-grid-lines', 3)

        self.obj("txt_buscar").set_editable(True)
        self.obj("hbox_fecha").set_visible(False)
        self.columna_buscar(1)

        lista = ListStore(int, int, str, str, str, str, str, int, str,
            float, float, str, str, str, bool, str, int)
        self.obj("grilla_buscar").set_model(lista)
        self.obj("grilla_buscar").show()

    def cargar_grilla_buscar(self):
        if self.campo_buscar == "FechaHora":
            opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
            " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
        else:
            opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
            " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

        if self.origen is None:  # Anulando Factura de Venta
            opcion += " WHERE " if len(opcion) == 0 else " AND "
            opcion += "Anulado <> 1"

        if len(self.condicion) > 0:
            self.condicion = " WHERE " + self.condicion if len(opcion) == 0 \
            else " AND " + self.condicion

        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "NroTimbrado, NroFactura, FechaHora, " +
            "idTipoDocCliente, NroDocCliente, RazonSocial, DireccionPrincipal, " +
            "idTipoFactura, TipoFactura, Total, TotalLiquidacionIVA, " +
            "Alias, NroDocUsuario, NombreApellido, Anulado, idCliente",
            "facturaventas_s", opcion + self.condicion + " ORDER BY FechaHora DESC")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        lista = self.obj("grilla_buscar").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], Cal.mysql_fecha_hora(datos[i][2]),
                datos[i][3], datos[i][4], datos[i][5], datos[i][6], datos[i][7], datos[i][8],
                datos[i][9], datos[i][10], datos[i][11], datos[i][12], datos[i][13],
                datos[i][14], str(datos[i][2]), datos[i][15]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def columna_buscar(self, idcolumna):
        if idcolumna == 0:
            col, self.campo_buscar = "Nro. Timbrado", "NroTimbrado"
        elif idcolumna == 1:
            col, self.campo_buscar = "Nro. Factura", "NroFactura"
        elif idcolumna == 15:
            col, self.campo_buscar = "Fecha de Expedición", "FechaHora"
            self.obj("txt_buscar").set_editable(False)
            self.obj("hbox_fecha").set_visible(True)
        elif idcolumna == 3:
            col, self.campo_buscar = "Tipo Doc. Cliente", "idTipoDocCliente"
        elif idcolumna == 4:
            col, self.campo_buscar = "Nro. Documento (Cliente)", "NroDocCliente"
        elif idcolumna == 5:
            col, self.campo_buscar = "Razón Social", "RazonSocial"
        elif idcolumna == 6:
            col, self.campo_buscar = "Dirección Principal", "DireccionPrincipal"
        elif idcolumna == 7:
            col, self.campo_buscar = "Cód. Tipo Factura", "idTipoFactura"
        elif idcolumna == 8:
            col, self.campo_buscar = "Tipo de Factura", "TipoFactura"
        elif idcolumna == 9:
            col, self.campo_buscar = "Total", "Total"
        elif idcolumna == 10:
            col, self.campo_buscar = "Total Liq. IVA", "TotalLiquidacionIVA"
        elif idcolumna == 11:
            col, self.campo_buscar = "Alias de Usuario", "Alias"
        elif idcolumna == 12:
            col, self.campo_buscar = "Nro. Documento (Usuario)", "NroDocUsuario"
        elif idcolumna == 13:
            col, self.campo_buscar = "Nombre de Usuario", "NombreApellido"

        self.obj("label_buscar").set_text("Filtrar por " + col + ":")
