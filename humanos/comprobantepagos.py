#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date
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

        arch = Op.archivo("rrhh_comprobantes")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(800, 600)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Comprobante de Pago")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_01_2").set_max_length(12)
        self.obj("txt_02").set_max_length(10)
        self.obj("txt_05").set_max_length(100)

        self.obj("txt_c_01").set_max_length(10)
        self.obj("txt_c_02").set_max_length(10)
        self.obj("txt_c_03").set_max_length(12)

        self.obj("txt_00").set_tooltip_text("Ingrese el Número de Comprobante de Pago")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Empleado cuyo Pago es registrado"))
        self.obj("txt_01_1").set_tooltip_text("Nombre y Apellido del Empleado")
        self.obj("txt_01_2").set_tooltip_text("Ingrese el Nro. de Documento del Empleado")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el Contrato del Empleado seleccionado"))
        self.obj("txt_02_1").set_tooltip_text("Cargo del Empleado dentro de la Empresa")
        self.obj("txt_03").set_tooltip_text(Mens.usar_boton("la Fecha de Inicio del Periodo de Pago"))
        self.obj("txt_04").set_tooltip_text(Mens.usar_boton("la Fecha de Finalización del Periodo de Pago"))
        self.obj("txt_05").set_tooltip_text("Ingrese cualquier información adicional con respecto al Pago")
        self.obj("txt_02").grab_focus()

        self.obj("txt_c_01").set_tooltip_text("Ingrese el Código del Detalle del Pago")
        self.obj("txt_c_02").set_tooltip_text(Mens.usar_boton("el Concepto de Pago"))
        self.obj("txt_c_03").set_tooltip_text("Ingrese la Cantidad que es Pagada\n(días trabajados, horas extraordinarias, cantidad de hijos...)")
        self.obj("txt_c_04").set_tooltip_text("Ingrese el Monto a Pagar")

        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_01_2"), self.obj("cmb_tipo_doc")
        self.txt_cod_cnt, self.txt_crg_cnt = self.obj("txt_02"), self.obj("txt_02_1")
        self.txt_cod_con, self.txt_des_con = self.obj("txt_c_02"), self.obj("txt_c_02_1")

        self.idPersona, self.borrar_contrato, self.idTipoDoc = None, not edit, -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc"), "tipodocumentos", "idTipoDocumento")

        self.salariominimo = Op.obtener_salario_minimo(self.nav.datos_conexion)
        arch.connect_signals(self)

        self.config_grilla_conceptos()
        self.conexion = Op.conectar(self.nav.datos_conexion)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            idcont = str(seleccion.get_value(iterador, 1))
            fini = seleccion.get_value(iterador, 9)
            ffin = seleccion.get_value(iterador, 10)
            fecha = seleccion.get_value(iterador, 13)[:-9]

            obs = seleccion.get_value(iterador, 14)
            obs = "" if obs is None else obs

            self.fechaini = seleccion.get_value(iterador, 21)
            self.fechafin = seleccion.get_value(iterador, 22)

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_02").set_text(idcont)
            self.obj("txt_03").set_text(fini)
            self.obj("txt_04").set_text(ffin)
            self.obj("txt_05").set_text(obs)

            self.focus_out_event(self.obj("txt_02"), 0)
            self.obj("lbl_fecha").set_text(fecha)

            self.cargar_grilla_conceptos()
            self.estadoguardar(True)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))
            self.obj("cmb_tipo_doc").set_active(0)

            self.obj("lbl_fecha").set_text(Cal.mysql_fecha(date.today()))
            self.cargar_grilla_conceptos()
            self.estadoguardar(False)

        self.principal_guardado = True
        self.estadoedicion(False)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_principal_comprobantes()
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def on_btn_confirmar_clicked(self, objeto):
        self.principal_guardado = False
        self.guardar_principal_comprobantes("1")
        comp = self.obj("txt_00").get_text()

        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        from informes.rrhh_comprobantes import genera_comprobante_pago
        genera_comprobante_pago(self.nav.datos_conexion, comp)

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_consultar_clicked(self, objeto):
        self.guardar_principal_comprobantes()

        comp = self.obj("txt_00").get_text()
        grilla = self.obj("grilla").get_model()

        eleccion = True if len(grilla) == 0 else \
            Mens.pregunta_borrar("Esta operación eliminará todos" +
            " los datos cargados en el Detalle del Comprobante de Pago")

        if eleccion:
            if not len(grilla) == 0:  # Borrar Datos Anteriores
                for i in range(0, len(grilla)):
                    Op.eliminar(self.conexion, "comprobantepagos_detalles",
                        comp + ", " + str(grilla[i][0]))

            # Valores Iniciales
            conexion = Op.conectar(self.nav.datos_conexion)
            empl = self.obj("txt_01").get_text()
            cont = self.obj("txt_02").get_text()
            sal = self.obj("txt_02_2").get_text()
            det, total = 1, 0

            if self.idPeriodoPago == 1:  # Mensual
                dias = 26
            elif self.idPeriodoPago == 2:  # Quincenal
                dias = 12
            elif self.idPeriodoPago == 3:  # Semanal
                dias = 6
            else:  # Diario
                dias = 1

            # Sueldo Básico (Cód. 0)
            sql = comp + ", " + str(det) + ", 0, " + sal + ", " + str(dias) + ", NULL"
            Op.insertar(self.conexion, "comprobantepagos_detalles", sql)
            total += Decimal(sal)
            det += 1

            # Bonificación Familiar (Cód. 4)
            maximo = round((self.salariominimo * 200 / 100), 2)  # 200% del salario mínimo (art. 263)

            if Decimal(sal) < maximo:
                cada_hijo = round((self.salariominimo * 5 / 100), 2)  # 5% del Salario Mínimo (art. 261)
                cant = 0

                # Buscar Hijos discapacitados
                cursor = Op.consultar(conexion, "idFamiliar", "beneficiarios_s",
                    " WHERE idEmpleado = " + empl + " AND idTipoParentesco = 5")
                datos = cursor.fetchall()
                cant += cursor.rowcount

                # Buscar Hijos menores
                cursor = Op.consultar(conexion, "idFamiliar", "beneficiarios_s",
                    " WHERE idEmpleado = " + empl + " AND idTipoParentesco = 4")
                datos = cursor.fetchall()
                cant += cursor.rowcount

                monto = cada_hijo * cant
                sql = comp + ", " + str(det) + ", 4, " + str(monto) + ", " + str(cant) + ", NULL"
                Op.insertar(self.conexion, "comprobantepagos_detalles", sql)
                det += 1

            # Horas Extraordinarias (Cód. 10)
            cursor = Op.consultar(conexion, "SEC_TO_TIME(SUM(TIME_TO_SEC(CantidadHoras))) AS TotalHoras",
                "horaextraordinarias_s", " WHERE NroContrato = " + cont + " AND " +
                "Fecha BETWEEN '" + self.fechaini + "' AND '" + self.fechafin + "'")
            datos = cursor.fetchall()
            cant = cursor.rowcount

            if datos[0][0] is not None:
                # Cantidad de Horas (HH:MM:SS)
                cadena = str(datos[0][0])
                hora = int(cadena[:cadena.find(":", 0, 3)])  # Busca hasta el tercer caracter
                minuto = int(cadena[cadena.find(":", 0, 3) + 1 :cadena.find(":", 3, 6)])

                if minuto >= 45:
                    valor = 0.75
                elif minuto >= 30:
                    valor = 0.5
                elif minuto >= 15:
                    valor = 0.25
                else:
                    valor = 0.0
                hora += Decimal(valor)

                # Monto a Pagar
                pago_dia = round((Decimal(sal) / dias), 2)
                pago_hora = round((pago_dia / 8), 2)
                monto = round((pago_hora * hora), 2)

                sql = comp + ", " + str(det) + ", 10, " + str(monto) + ", " + str(hora) + ", NULL"
                Op.insertar(self.conexion, "comprobantepagos_detalles", sql)
                total += monto
                det += 1

            # Gratificaciones (Cód. 11)
            cursor = Op.consultar(conexion, "Monto, MotivoGratificacion",
                "gratificaciones_s", " WHERE NroContrato = " + cont + " AND " +
                "FechaHora BETWEEN '" + self.fechaini + "' AND '" + self.fechafin + " 23:59:59'")
            datos = cursor.fetchall()
            cant = cursor.rowcount

            for i in range(0, cant):
                sql = comp + ", " + str(det) + ", 11, " + str(datos[i][0]) + ", NULL, '(" + datos[i][1] + ")'"
                Op.insertar(self.conexion, "comprobantepagos_detalles", sql)
                total += Decimal(datos[i][0])
                det += 1

            # Comisiones (Cód. 13)
            cursor = Op.consultar(conexion, "idVendedor",
                "vendedores_s", " WHERE NroContrato = " + cont)
            datos = cursor.fetchall()
            cant = cursor.rowcount

            if cant > 0:
                # Buscar Comisiones del vendedor durante el periodo de pago
                cursor = Op.consultar(conexion, "IFNULL(SUM(TotalComision), 0)",
                    "facturaventas_s", " WHERE idVendedor = " + str(datos[0][0]) +
                    " AND FechaHora BETWEEN '" + self.fechaini + "'" +
                    " AND '" + self.fechafin + " 23:59:59'")
                monto = cursor.fetchall()[0][0]

                sql = comp + ", " + str(det) + ", 13, " + str(monto) + ", NULL, NULL"
                Op.insertar(self.conexion, "comprobantepagos_detalles", sql)
                total += Decimal(monto)
                det += 1

            # Descuentos (Cód. 12)
            cursor = Op.consultar(conexion, "DP.Monto, D.MotivoDescuento",
                "descuentos_periodocobros DP INNER JOIN descuentos_s D " +
                "ON (DP.idDescuento = D.idDescuento)", " WHERE " +
                "D.NroContrato = " + cont + " AND DP.FechaCobro = CURRENT_DATE()")
            datos = cursor.fetchall()
            cant = cursor.rowcount

            for i in range(0, cant):
                sql = comp + ", " + str(det) + ", 12, " + str(datos[i][0] * -1) + ", NULL, '(" + datos[i][1] + ")'"
                Op.insertar(self.conexion, "comprobantepagos_detalles", sql)
                total -= Decimal(datos[i][0])
                det += 1

            # IPS Obrero (9%) (Cód. 5)
            monto = round((total * 9 / 100), 2)
            sql = comp + ", " + str(det) + ", 5, " + str(monto * -1) + ", NULL, NULL"
            Op.insertar(self.conexion, "comprobantepagos_detalles", sql)
            det += 1

            # Descuento de Anticipo (Cód. 2)
            cursor = Op.consultar(conexion, "D.Monto", "comprobantepagos_detalles_s D" +
                " INNER JOIN comprobantepagos_s C ON (D.NroComprobante = C.NroComprobante)",
                " WHERE C.NroContrato = " + cont + " AND C.FechaHoraExp BETWEEN " +
                "'" + self.fechaini + "' AND '" + self.fechafin + " 23:59:59'")

            for i in range(0, cant):
                sql = comp + ", " + str(det) + ", 2, " + str(datos[i][0] * -1) + ", NULL, NULL"
                Op.insertar(self.conexion, "comprobantepagos_detalles", sql)
                det += 1

            conexion.close()  # Finaliza la conexión
            self.cargar_grilla_conceptos()
            self.estadoguardar(True)

    def on_btn_empleado_clicked(self, objeto):
        from clases.llamadas import empleados
        empleados(self.nav.datos_conexion, self)

    def on_btn_contrato_clicked(self, objeto):
        condicion = None if len(self.obj("txt_01").get_text()) == 0 \
        else "idEmpleado = " + self.obj("txt_01").get_text()

        from clases.llamadas import contratos
        contratos(self.nav.datos_conexion, self, condicion)

    def on_btn_fecha_ini_clicked(self, objeto):
        self.obj("txt_03").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_03").set_text(lista[0])
            self.fechaini = lista[1]

    def on_btn_limpiar_fecha_ini_clicked(self, objeto):
        self.obj("txt_03").set_text("")
        self.obj("txt_03").grab_focus()

    def on_btn_fecha_fin_clicked(self, objeto):
        self.obj("txt_04").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_04").set_text(lista[0])
            self.fechafin = lista[1]

    def on_btn_limpiar_fecha_fin_clicked(self, objeto):
        self.obj("txt_04").set_text("")
        self.obj("txt_04").grab_focus()

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_01_2").get_text()) == 0 or len(self.obj("txt_02").get_text()) == 0 \
        or len(self.obj("txt_03").get_text()) == 0 or len(self.obj("txt_04").get_text()) == 0 \
        or self.idTipoDoc == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Nro. de Comprobante", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Cód. de Empleado", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Nro. de Contrato", self.obj("barraestado")):
                estado = True
            else:
                estado = False

        self.principal_guardado = False
        self.estadoguardar(estado)

    def on_cmb_tipo_doc_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            self.idTipoDoc = model[active][0]
            self.focus_out_event(self.obj("txt_01_2"), 0)  # Nro. Documento
        else:
            self.obj("barraestado").push(0, "No existen registros de Tipos de Documentos en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
                    self.on_btn_empleado_clicked(0)
                elif objeto == self.obj("txt_02"):
                    self.on_btn_contrato_clicked(0)
                elif objeto == self.obj("txt_03"):
                    self.on_btn_fecha_ini_clicked(0)
                elif objeto == self.obj("txt_04"):
                    self.on_btn_fecha_fin_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
            tipo = "un Empleado"
        elif objeto == self.obj("txt_02"):
            tipo = "un Contrato"
        elif objeto == self.obj("txt_03"):
            tipo = "la Fecha de Inicio del Periodo de Pago"
        elif objeto == self.obj("txt_04"):
            tipo = "la Fecha de Finalización del Periodo de Pago"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar " + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")

            if objeto == self.obj("txt_01"):  # Código de Empleado
                self.idPersona == None
                self.obj("txt_01_1").set_text("")
                self.obj("txt_01_2").set_text("")

            elif objeto == self.obj("txt_01_2") \
            and len(self.obj("txt_01").get_text()) == 0:  # Nro. Documento de Empleado
                self.obj("txt_01_1").set_text("")

            elif objeto == self.obj("txt_02"):  # Número de Contrato
                self.obj("txt_02_1").set_text("")
                self.obj("txt_02_2").set_text("")
                self.obj("txt_02_3").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) and \
                Op.comprobar_numero(int, objeto, "Nro. de Comprobante", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion,
                        self.nav.tabla + "_s", self.nav.campoid, valor,
                        objeto, self.estadoguardar, self.obj("barraestado"),
                        "El Nro. de Comprobante introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Empleado", self.obj("barraestado")):
                    self.buscar_empleados(objeto, "idPersona", valor, "Cód. de Empleado")

            elif objeto == self.obj("txt_01_2"):
                self.buscar_empleados(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + str(self.idTipoDoc) + "'", "Nro. de Documento")

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Nro. de Contrato", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "idEmpleado, Cargo, " +
                        "Salario, PeriodoPago, idPeriodoPago, Vigente",
                        "contratos_s", " WHERE NroContrato = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        if datos[0][5] == 1:
                            self.obj("txt_01").set_text(str(datos[0][0]))
                            self.obj("txt_02_1").set_text(datos[0][1])
                            self.obj("txt_02_2").set_text(str(datos[0][2]))
                            self.obj("txt_02_3").set_text(datos[0][3])

                            self.idPeriodoPago = datos[0][4]
                            self.obj("barraestado").push(0, "")

                            if len(self.obj("txt_03").get_text()) == 0:
                                # Buscar último pago y comparar fechas
                                conexion = Op.conectar(self.nav.datos_conexion)
                                cursor = Op.consultar(conexion,
                                    "MAX(FechaFin)", "comprobantepagos_s",
                                    " WHERE (NroContrato = " + valor + ")")
                                datos = cursor.fetchall()
                                cant = cursor.rowcount
                                conexion.close()  # Finaliza la conexión

                                if datos[0][0] is None:
                                    fecha = ""
                                else:
                                    fecha = Cal.mysql_fecha(datos[0][0])
                                    self.fechaini = str(datos[0][0])
                                self.obj("txt_03").set_text(fecha)

                            self.borrar_contrato = False
                            self.focus_out_event(self.obj("txt_01"), 0)
                        else:
                            objeto.grab_focus()
                            self.estadoguardar(False)
                            self.obj("barraestado").push(0, "El Contrato seleccionado ya no se encuentra vigente.")
                    else:
                        objeto.grab_focus()
                        self.estadoguardar(False)
                        self.obj("barraestado").push(0, "El Nro. de Contrato no es válido.")

            elif objeto == self.obj("txt_03"):
                if Op.compara_fechas(self.nav.datos_conexion, "'" + self.fechaini + "'", ">", "NOW()"):
                    self.estadoguardar(False)
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "La Fecha de Inicio del Periodo de Pago NO puede estar en el Futuro.")
                else:
                    self.comparar_fechas_periodo_pago()

            elif objeto == self.obj("txt_04"):
                if Op.compara_fechas(self.nav.datos_conexion, "'" + self.fechafin + "'", ">", "NOW()"):
                    self.estadoguardar(False)
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "La Fecha de Finalización del Periodo de Pago NO puede estar en el Futuro.")
                else:
                    self.comparar_fechas_periodo_pago()

    def buscar_empleados(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, "idPersona, RazonSocial, " +
            "NroDocumento, idTipoDocumento", "personas_s",
            " WHERE " + campo + " = " + valor + " AND Empleado = 1")
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            # Si aún no se ha seleccionado o es diferente del anterior
            if self.idPersona is None or self.idPersona != str(datos[0][0]):
                self.idPersona = str(datos[0][0])

                self.obj("txt_01").set_text(self.idPersona)
                self.obj("txt_01_1").set_text(datos[0][1])
                self.obj("txt_01_2").set_text(datos[0][2])

                # Asignación de Tipo de Documento en Combo
                model, i = self.obj("cmb_tipo_doc").get_model(), 0
                while model[i][0] != datos[0][3]: i += 1
                self.obj("cmb_tipo_doc").set_active(i)

                if self.borrar_contrato:  # Debe indicarse otro Contrato
                    self.obj("txt_02").set_text("")
                    self.obj("txt_02_1").set_text("")
                else:
                    self.borrar_contrato = True

                self.obj("barraestado").push(0, "")
                self.verificacion(0)

        else:
            self.idPersona = valor
            self.estadoguardar(False)
            objeto.grab_focus()
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = self.obj("txt_01_2") if objeto == self.obj("txt_01") else self.obj("txt_01")
            otro.set_text("")
            self.obj("txt_01_1").set_text("")

    def comparar_fechas_periodo_pago(self):
        if len(self.obj("txt_03").get_text()) > 0 and len(self.obj("txt_04").get_text()) > 0:
            if Op.compara_fechas(self.nav.datos_conexion,
            "'" + self.fechaini + "'", ">", "'" + self.fechafin + "'"):
                self.estadoguardar(False)
                objeto.grab_focus()
                self.obj("barraestado").push(0, "La Fecha de Inicio del Periodo de Pago NO puede ser posterior a la de Finalización.")
            else:
                self.obj("barraestado").push(0, "")

    def guardar_principal_comprobantes(self, confirmado="0"):
        if not self.principal_guardado:
            comp = self.obj("txt_00").get_text()
            cont = self.obj("txt_02").get_text()
            obs = self.obj("txt_05").get_text()
            obs = "NULL" if len(obs) == 0 else "'" + obs + "'"

            sql = comp + ", " + cont + ", '" + self.fechaini + "', " + \
                "'" + self.fechafin + "', " + obs + ", " + confirmado

            if not self.editando:
                Op.insertar(self.conexion, self.nav.tabla, sql)
            else:
                Op.modificar(self.conexion, self.nav.tabla, self.cond + ", " + sql)

            self.cond = comp  # Nuevo NroComprobante original
            self.principal_guardado = self.editando = True

    def estadoguardar(self, estado):
        self.obj("buttonbox_abm").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)
        self.obj("btn_consultar").set_sensitive(estado) # Borrar todo y consultar

        # Obligatoriamente debe poseer un Concepto seleccionado para poder Guardar
        estado = True if estado and len(self.obj("grilla").get_model()) > 0 else False
        self.obj("btn_confirmar").set_sensitive(estado)
        self.obj("btn_guardar").set_sensitive(estado)

    def estadoedicion(self, estado):
        self.obj("vbox1").set_sensitive(not estado)
        self.obj("btn_cancelar").set_sensitive(not estado)

        self.obj("vbox2").set_visible(estado)
        self.obj("buttonbox_concepto").set_visible(estado)

##### Conceptos de Pago ################################################

    def config_grilla_conceptos(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Código", celda0, 0, True, 100, 200)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Cód. Concepto", celda0, 1, True, 100, 200)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Concepto de Pago", celda1, 2, True, 200)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Cantidad", celda2, 3, True, 100, 200)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Monto", celda2, 4, True, 100, 200)
        col4.set_sort_column_id(4)

        lista = [col0, col1, col2, col3, col4]
        for columna in lista:
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(0)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, int, str, str, float, bool, str)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_conceptos(self):
        cursor = Op.consultar(self.conexion, "idDetalle, idConcepto, Concepto, " +
            "Cantidad, Monto, Suma, Observaciones", "comprobantepagos_detalles_s",
            " WHERE NroComprobante = " + self.obj("txt_00").get_text() +
            " ORDER BY idDetalle")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        total = 0  # Monto Total a Pagar

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            cantidad = "" if datos[i][3] is None else str(datos[i][3])
            obs = "" if datos[i][6] is None else " " + datos[i][6]
            total += datos[i][4]

            lista.append([datos[i][0], datos[i][1], datos[i][2] + obs,
                cantidad, datos[i][4], datos[i][5], obs])

        self.obj("txt_total").set_text(str(total))
        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_clicked(self, objeto):
        self.editando_concepto = False
        self.funcion_conceptos()

    def on_btn_modificar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.cond_concepto = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Conceptos de Pago. Luego presione Modificar.")
        else:
            self.editando_concepto = True
            self.funcion_conceptos()

    def on_btn_eliminar_clicked(self, objeto):
        self.guardar_principal_comprobantes()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            det = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Conceptos de Pago. Luego presione Eliminar.")
        else:
            comp = self.obj("txt_00").get_text()
            idcon = str(seleccion.get_value(iterador, 1))
            con = seleccion.get_value(iterador, 2)
            cant = seleccion.get_value(iterador, 3)
            mont = str(seleccion.get_value(iterador, 4))

            eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
                "\nCódigo: " + idcon + "\nConcepto: " + con +
                "\nCantidad: " + cant + "\nMonto: " + mont)

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "comprobantepagos_detalles", comp + ", " + det)
                self.cargar_grilla_conceptos()

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_clicked(0)

##### Agregar-Modificar Conceptos de Pago ##############################

    def funcion_conceptos(self):
        self.guardar_principal_comprobantes()

        if self.editando_concepto:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            idcon = str(seleccion.get_value(iterador, 1))
            con = seleccion.get_value(iterador, 2)
            cant = str(seleccion.get_value(iterador, 3))
            monto = str(seleccion.get_value(iterador, 4))
            obs = seleccion.get_value(iterador, 6)

            self.obj("txt_c_01").set_text(self.cond_concepto)
            self.obj("txt_c_02").set_text(idcon)
            self.obj("txt_c_02_1").set_text(con)
            self.obj("txt_c_03").set_text(cant)
            self.obj("txt_c_04").set_text(monto)
            self.obj("txt_c_05").set_text(obs)
        else:
            self.obj("txt_c_01").set_text(Op.nuevoid(self.conexion,
                "comprobantepagos_detalles_s WHERE NroComprobante = " +
                self.obj("txt_00").get_text(), "idDetalle"))

        self.estadoedicion(True)
        self.estadoguardar(False)

        self.obj("btn_guardar_concepto").set_sensitive(False)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

    def on_btn_guardar_concepto_clicked(self, objeto):
        self.guardar_principal_comprobantes()

        comp = self.obj("txt_00").get_text()
        det = self.obj("txt_c_01").get_text()
        con = self.obj("txt_c_02").get_text()
        cant = self.obj("txt_c_03").get_text()
        mont = self.obj("txt_c_04").get_text()
        obs = self.obj("txt_c_05").get_text()

        cant = "NULL" if len(cant) == 0 else cant
        obs = "NULL" if len(obs) == 0 else "'" + obs + "'"

        sql = comp + ", " + det + ", " + con + ", " + mont + ", " + cant + ", " + obs

        if not self.editando_concepto:
            Op.insertar(self.conexion, "comprobantepagos_detalles", sql)
        else:
            Op.modificar(self.conexion, "comprobantepagos_detalles",
                self.cond_concepto + ", " + sql)

        self.cargar_grilla_conceptos()
        self.on_btn_cancelar_concepto_clicked(0)

    def on_btn_cancelar_concepto_clicked(self, objeto):
        self.estadoedicion(False)
        self.estadoguardar(True)

        self.obj("txt_c_01").set_text("")
        self.obj("txt_c_02").set_text("")
        self.obj("txt_c_02_1").set_text("")
        self.obj("txt_c_03").set_text("")
        self.obj("txt_c_04").set_text("")
        self.obj("txt_c_05").set_text("")

    def on_btn_concepto_clicked(self, objeto):
        from clases.llamadas import conceptopagos
        conceptopagos(self.nav.datos_conexion, self)

    def verificacion_concepto(self, objeto):
        if len(self.obj("txt_c_01").get_text()) == 0 or len(self.obj("txt_c_02").get_text()) == 0 \
        or len(self.obj("txt_c_04").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_c_01"), "Cód. de Detalle", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_c_04"), "Monto a Pagar", self.obj("barraestado"), False):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar_concepto").set_sensitive(estado)

    def on_txt_c_02_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_concepto_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.on_concepto_focus_out_event(objeto, 0)

    def on_txt_c_02_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un Concepto de Pago.")

    def on_concepto_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_c_02"):
                self.obj("txt_c_02_1").set_text("")
        else:
            if objeto == self.obj("txt_c_01"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando_concepto or valor != self.cond_concepto) and \
                Op.comprobar_numero(int, objeto, "Cód. de Detalle", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion, "comprobantepagos_detalles_s",
                        "idDetalle", valor + " AND NroComprobante = " + self.obj("txt_00").get_text(),
                        objeto, self.obj("btn_guardar_concepto"), self.obj("barraestado"),
                        "El Cód. de Detalle introducido ya ha sido registado en este Comprobante.")

            elif objeto == self.obj("txt_c_02"):
                if Op.comprobar_numero(int, objeto, "Cód. de Concepto", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "Descripcion",
                        "conceptopagos", " WHERE idConcepto = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("txt_c_02_1").set_text(datos[0][0])
                        self.obj("barraestado").push(0, "")
                    else:
                        objeto.grab_focus()
                        self.obj("btn_guardar_concepto").set_sensitive(False)
                        self.obj("barraestado").push(0, "El Cód. de Concepto no es válido.")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)

    col0 = Op.columnas("Número", celda0, 0, True, 100, 200)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Nro. Contrato", celda0, 1, True, 100, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Cód. Empleado", celda0, 2, True, 100, 200)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Tipo Doc. Identidad", celda0, 3, True, 100, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Nro. Doc. Identidad", celda0, 4, True, 100, 200)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Nombre y Apellido", celda1, 5, True, 200)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Fecha de Nacimiento", celda0, 6, True, 200)
    col6.set_sort_column_id(20)  # Para ordenarse usa la fila 20
    col7 = Op.columnas("Edad", celda0, 7, True, 100, 200)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Cargo", celda1, 8, True, 150)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Inicio de Periodo de Pago", celda0, 9, True, 200)
    col9.set_sort_column_id(21)  # Para ordenarse usa la fila 21
    col10 = Op.columnas("Fin de Periodo de Pago", celda0, 10, True, 200)
    col10.set_sort_column_id(22)  # Para ordenarse usa la fila 22
    col11 = Op.columnas("Cantidad de Días", celda0, 11, True, 100, 200)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Total a Pagar", celda0, 12, True, 100, 200)
    col12.set_sort_column_id(12)
    col13 = Op.columnas("Fecha de Modificación", celda0, 13, True, 200)
    col13.set_sort_column_id(23)  # Para ordenarse usa la fila 23
    col14 = Op.columnas("Observaciones", celda1, 14, True, 200)
    col14.set_sort_column_id(14)
    col15 = Op.columnas("Alias de Usuario", celda1, 15, True, 100, 200)
    col15.set_sort_column_id(15)
    col16 = Op.columnas("Nro. Documento", celda0, 16, True, 100, 200)
    col16.set_sort_column_id(16)
    col17 = Op.columnas("Nombre de Usuario", celda1, 17, True, 200)
    col17.set_sort_column_id(17)
    col18 = Op.columna_active("Confirmado", 18)
    col18.set_sort_column_id(18)
    col19 = Op.columna_active("Anulado", 19)
    col19.set_sort_column_id(19)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8,
        col9, col10, col11, col12, col13, col14, col15, col16, col17]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col18)
    self.obj("grilla").append_column(col19)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(5)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 5)

    lista = ListStore(int, int, int, str, str, str, str, int, str,
        str, str, int, float, str, str, str, str, str, int, int,
        str, str, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar in ("FechaInicio", "FechaFin", "FechaHoraExp", "FechaNacimiento"):
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    if self.obj("rad_act").get_active() or self.obj("rad_ina").get_active():
        confirmado = "1" if self.obj("rad_act").get_active() else "0"
        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += "Confirmado = " + confirmado

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, "NroComprobante, NroContrato, idEmpleado, " +
        "idTipoDocumento, NroDocumento, NombreApellido, FechaNacimiento, " +
        "Edad, Cargo, FechaInicio, FechaFin, CantDias, TotalPagar, " +
        "FechaHoraExp, Observaciones, Alias, NroDocUsuario, NombreUsuario, " +
        "Confirmado, Anulado", self.tabla + "_s", opcion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        fechanac = "" if datos[i][6] is None else Cal.mysql_fecha(datos[i][6])
        fechaini = "" if datos[i][9] is None else Cal.mysql_fecha(datos[i][9])
        fechafin = "" if datos[i][10] is None else Cal.mysql_fecha(datos[i][10])
        fechaexp = "" if datos[i][13] is None else Cal.mysql_fecha_hora(datos[i][13])

        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], datos[i][5], fechanac, datos[i][7], datos[i][8],
            fechaini, fechafin, datos[i][11], datos[i][12], fechaexp,
            datos[i][14], datos[i][15], datos[i][16], datos[i][17],
            datos[i][18], datos[i][19], str(datos[i][6]), str(datos[i][9]),
            str(datos[i][10]), str(datos[i][13])])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Nro. de Comprobante", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "Nro. Contrato", "NroContrato"
    elif idcolumna == 2:
        col, self.campo_buscar = "Cód. Empleado", "idEmpleado"
    elif idcolumna == 3:
        col, self.campo_buscar = "Tipo Doc. Identidad", "idTipoDocumento"
    elif idcolumna == 4:
        col, self.campo_buscar = "Nro. Doc. Identidad", "NroDocumento"
    elif idcolumna == 5:
        col, self.campo_buscar = "Nombre y Apellido", "NombreApellido"
    elif idcolumna == 20:
        col, self.campo_buscar = "Fecha de Nacimiento, desde", "FechaNacimiento"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 7:
        col = self.campo_buscar = "Edad"
    elif idcolumna == 8:
        col = self.campo_buscar = "Cargo"
    elif idcolumna == 21:
        col, self.campo_buscar = "Inicio de Periodo de Pago, desde", "FechaInicio"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 22:
        col, self.campo_buscar = "Fin de Periodo de Pago, desde", "FechaFin"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 11:
        col, self.campo_buscar = "Cantidad de Días", "CantDias"
    elif idcolumna == 12:
        col, self.campo_buscar = "Total a Pagar", "TotalPagar"
    elif idcolumna == 23:
        col, self.campo_buscar = "Fecha de Modificación, desde", "FechaHoraExp"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 14:
        col = self.campo_buscar = "Observaciones"
    elif idcolumna == 15:
        col, self.campo_buscar = "Alias de Usuario", "Alias"
    elif idcolumna == 16:
        col, self.campo_buscar = "Nro. Documento", "NroDocUsuario"
    elif idcolumna == 17:
        col, self.campo_buscar = "Nombre de Usuario", "NombreUsuario"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 5)
    valor2 = seleccion.get_value(iterador, 9)
    valor3 = seleccion.get_value(iterador, 10)
    valor4 = seleccion.get_value(iterador, 15)

    mensaje = "Seleccionó:\n\nNúmero: " + valor0 + "\nNombre y Apellido: " + valor1 + \
        "\nInicio de Periodo: " + valor2 + "\nFin de Periodo: " + valor3 + \
        "\nUsuario Responsable: " + valor4

    if self.eli_anu == "Anular":
        eleccion = Mens.pregunta_anular(mensaje)
    else:
        eleccion = Mens.pregunta_borrar(mensaje)

    self.obj("grilla").get_selection().unselect_all()
    self.obj("barraestado").push(0, "")

    if eleccion:
        conexion = Op.conectar(self.datos_conexion)

        if self.eli_anu == "Anular":
            Op.anular(conexion, self.tabla, valor0)
        else:
            Op.eliminar(conexion, self.tabla, valor0)

        conexion.commit()
        conexion.close()  # Finaliza la conexión
        cargar_grilla(self)


def listar_grilla(self):
    pass


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        contrato = str(seleccion.get_value(iterador, 0))
        codempl = str(seleccion.get_value(iterador, 1))
        tipdoc = seleccion.get_value(iterador, 2)
        nrodoc = seleccion.get_value(iterador, 3)
        nombre = seleccion.get_value(iterador, 4)
        direc = seleccion.get_value(iterador, 6)
        telef = seleccion.get_value(iterador, 7)
        cargo = seleccion.get_value(iterador, 13)
        salario = seleccion.get_value(iterador, 24)

        direc = "" if direc is None else direc
        telef = "" if telef is None else telef

        self.origen.txt_cod_cnt.set_text(contrato)

        try:  # Cargo del Empleado
            self.origen.txt_crg_cnt.set_text(cargo)
        except:
            pass

        try:  # Salario del Empleado
            self.origen.txt_sal_cnt.set_text(salario)
        except:
            pass

        self.origen.txt_cod_per.set_text(codempl)
        self.origen.txt_rzn_scl.set_text(nombre)

        try:  # Combo que indica el Tipo de Documento de Identidad
            model, i = self.origen.cmb_tip_doc.get_model(), 0
            while model[i][0] != tipdoc: i += 1
            self.origen.cmb_tip_doc.set_active(i)
        except:
            pass

        try:  # Número de Documento de Identidad
            self.origen.txt_nro_doc.set_text(nrodoc)
        except:
            pass

        try:  # Dirección Principal
            self.origen.txt_dir_per.set_text(direc)
        except:
            pass

        try:  # Telefono Principal
            self.origen.txt_tel_per.set_text(telef)
        except:
            pass

        try:  # Se usa en Movimientos de Empleados
            self.origen.idPersona = valor0
        except:
            pass

        self.on_btn_salir_clicked(0)
    except:
        pass
