#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date
from time import strftime
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class cajaaperturas:

    def __init__(self, datos, v_or):
        self.datos_conexion = datos
        self.origen = v_or

        arch = Op.archivo("caja_aperturas")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_title("Aperturas de Cajas")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_02").set_max_length(7)
        self.obj("txt_03").set_max_length(15)

        self.obj("txt_00").set_tooltip_text(Mens.usar_boton("el Establecimiento que afectará"))
        self.obj("txt_00_1").set_tooltip_text("Nombre del Establecimiento")
        self.obj("txt_00_2").set_tooltip_text("Dirección o Localización del Establecimiento")
        self.obj("txt_00_2").set_tooltip_text("Teléfono del Establecimiento")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Punto de Expedición que afectará"))
        self.obj("txt_01_1").set_tooltip_text("Nombre del Punto de Expedición")
        self.obj("txt_02").set_tooltip_text("Ingrese el Número Inicial del Documento a emitir")
        self.obj("txt_03").set_tooltip_text("Ingrese el Monto de Dinero disponible en Caja en este momento")

        self.txt_nro_est, self.txt_nom_est = self.obj("txt_00"), self.obj("txt_00_1")
        self.txt_dir_est, self.txt_tel_est = self.obj("txt_00_2"), self.obj("txt_00_3")
        self.txt_nro_cja, self.txt_nom_cja = self.obj("txt_01"), self.obj("txt_01_1")

        self.idTipoDoc = -1
        Op.combos_config(self.datos_conexion, self.obj("cmb_tipo_doc"),
            "tipodocumentocomerciales", "idTipoDocumentoComercial")
        arch.connect_signals(self)

        self.obj("txt_fecha").set_text(Cal.mysql_fecha(date.today()))
        self.obj("txt_hora").set_text(strftime('%H:%M:%S'))
        self.obj("ventana").show()

    #self.obj("txt_fecha").set_text(str(localtime()[2]) + "/" + str(localtime()[1]) + "/" + str(localtime()[0]))
    #self.obj("txt_hora").set_text(str(localtime()[3]) + ":" + str(localtime()[4]) + ":" + str(localtime()[5]))

    def on_btn_guardar_clicked(self, objeto):
        v0 = str(self.numero)
        v1 = self.obj("txt_00").get_text()
        v2 = self.obj("txt_01").get_text()
        v3 = self.obj("txt_02").get_text()  # NroInicio
        v4 = self.obj("txt_03").get_text()

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.datos_conexion)

        Op.insertar(conexion, "cajaaperturas", v1 + ", " + v2 + ", " +
            str(self.idTipoDoc) + ", " + v3 + ", " + v4)
        self.origen.estab, self.origen.caja, self.origen.numero = v1, v2, v0

        conexion.commit()
        conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        self.origen.verificar_permisos_caja(True)

    def on_btn_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_establecimiento_clicked(self, objeto):
        self.obj("txt_00").grab_focus()

        from clases.llamadas import establecimientos
        establecimientos(self.datos_conexion, self)

    def on_btn_caja_clicked(self, objeto):
        establecimiento = None if len(self.obj("txt_00_2").get_text()) == 0 else self.obj("txt_00").get_text()
        self.obj("txt_01").grab_focus()

        from clases.llamadas import puntoexpediciones
        puntoexpediciones(self.datos_conexion, self, establecimiento)

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0 or len(self.obj("txt_03").get_text()) == 0 \
        or self.idTipoDoc == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Nro. de Establecimiento", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Nro. de Punto de Expedición", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Número Inicial del Documento a emitir", self.obj("barraestado"), False) \
            and Op.comprobar_numero(float, self.obj("txt_03"), "Monto de Apertura", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar").set_sensitive(estado)

    def on_cmb_tipo_doc_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            self.idTipoDoc = model[active][0]
            self.verificacion(0)
        else:
            self.obj("barraestado").push(0, "No existen registros " +
            "de Tipo de Documentos Comerciales en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_00"):
                    self.on_btn_establecimiento_clicked(0)
                elif objeto == self.obj("txt_01"):
                    self.on_btn_caja_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_00"):
            tipo = "Establecimiento"
        elif objeto == self.obj("txt_01"):
            tipo = "Punto de Expedición o Caja"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un " + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            self.limpiar_campos(objeto)
        else:
            if objeto == self.obj("txt_00"):
                if Op.comprobar_numero(int, objeto, "Nro. de Establecimiento", self.obj("barraestado")):
                    conexion = Op.conectar(self.datos_conexion)
                    cursor = Op.consultar(conexion, "Nombre, Ciudad, Direccion, NroTelefono, Activo",
                        "establecimientos_s", " WHERE NroEstablecimiento = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        direccion = "" if datos[0][2] is None else ", " + datos[0][2]
                        telefono = "" if datos[0][3] is None else datos[0][3]

                        self.obj("txt_00_1").set_text(datos[0][0])
                        self.obj("txt_00_2").set_text(datos[0][1] + direccion)
                        self.obj("txt_00_3").set_text(telefono)

                        if datos[0][4] != 1:  # Si no está Activo
                            self.obj("btn_guardar").set_sensitive(False)
                            self.obj("txt_00").grab_focus()
                            self.obj("barraestado").push(0, "El Establecimiento seleccionado NO está Activo.")
                        else:
                            self.obj("barraestado").push(0, "")
                            self.focus_out_event(self.obj("txt_01"), 0)
                    else:
                        self.obj("btn_guardar").set_sensitive(False)
                        self.obj("txt_00").grab_focus()
                        self.obj("barraestado").push(0, "El Nro. de Establecimiento NO es válido.")
                        self.limpiar_campos(objeto)

            elif objeto == self.obj("txt_01") and not len(self.obj("txt_00").get_text()) == 0:
                if Op.comprobar_numero(int, objeto, "Nro. de Punto de Expedición", self.obj("barraestado")):
                    conexion = Op.conectar(self.datos_conexion)
                    cursor = Op.consultar(conexion, "Nombre, Activo",
                        "puntoexpediciones_s", " WHERE NroPuntoExpedicion = " + valor +
                        " AND NroEstablecimiento = " + self.obj("txt_00").get_text())
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("txt_01_1").set_text(datos[0][0])

                        if datos[0][1] != 1:  # Si no está Activo
                            self.obj("btn_guardar").set_sensitive(False)
                            self.obj("txt_01").grab_focus()
                            self.obj("barraestado").push(0, "El Punto de Expedición seleccionado NO está Activo.")
                        else:
                            self.obj("barraestado").push(0, "")
                            self.buscar_numero_movimiento()
                    else:
                        self.obj("btn_guardar").set_sensitive(False)
                        self.obj("txt_01").grab_focus()
                        self.obj("barraestado").push(0, "El Nro. de Punto de Expedición NO es válido.")
                        self.limpiar_campos(objeto)

            elif objeto == self.obj("txt_02"):
                Op.comprobar_numero(int, objeto, "Número Inicial del Documento a emitir", self.obj("barraestado"), False)

            elif objeto == self.obj("txt_03"):
                Op.comprobar_numero(float, objeto, "Monto de Apertura", self.obj("barraestado"))

    def limpiar_campos(self, objeto):
        if objeto == self.obj("txt_00"):
            self.obj("txt_00_1").set_text("")
            self.obj("txt_00_2").set_text("")
            self.obj("txt_00_3").set_text("")
        elif objeto == self.obj("txt_01"):
            self.obj("txt_01_1").set_text("")

    def buscar_numero_movimiento(self):
        conexion = Op.conectar(self.datos_conexion)
        cursor = Op.consultar(conexion, "IFNULL(MAX(NroApertura), 0)", "cajaaperturas"
            " WHERE NroPuntoExpedicion = " + self.obj("txt_01").get_text() +
            " AND NroEstablecimiento = " + self.obj("txt_00").get_text())
        self.numero = cursor.fetchall()[0][0]  # Apertura Anterior

        cursor = Op.consultar(conexion, "NroCierre", "cajacierres",
            " WHERE NroCierre = " + str(self.numero) +
            " AND NroPuntoExpedicion = " + self.obj("txt_01").get_text() +
            " AND NroEstablecimiento = " + self.obj("txt_00").get_text())
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant == 0 and self.numero != 0:
            # Todavía no se ha registrado el cierre de Caja
            self.obj("dialogo").set_position(1)
            self.obj("dialogo").set_modal(True)
            self.obj("dialogo").show()
        else:
            # Ya se registró el cierre de Caja, nuevo Número de Apertura
            self.numero += 1

#### Diálogo ###########################################################

    def on_btn_aceptar_clicked(self, objeto):
        self.obj("dialogo").hide()

    def on_dialogo_hide(self, objeto):
        if self.obj("radio1").get_active():
            # Cancelar Apertura y Cerrar ventana
            self.obj("ventana").destroy()

        elif self.obj("radio2").get_active():
            # Elegir otra Caja u otro Establecimiento
            self.obj("txt_01").grab_focus()
            self.obj("btn_guardar").set_sensitive(False)
            self.obj("barraestado").push(0, "Debe ELEGIR otra Caja para realizar su apertura o CANCELAR la operación.")

        elif self.obj("radio3").get_active():
            # Mantener Abierta la Caja selecionada
            self.origen.verificar_permisos_caja(True)
            self.origen.estab = self.obj("txt_00").get_text()
            self.origen.caja = self.obj("txt_01").get_text()
            self.origen.numero = str(self.numero)
            self.obj("ventana").destroy()

        elif self.obj("radio4").get_active():
            # Registrar Cierre de la Caja seleccionada
            self.origen.estab = self.obj("txt_00").get_text()
            self.origen.caja = self.obj("txt_01").get_text()
            self.origen.numero = str(self.numero)
            self.obj("ventana").destroy()
            cajacierres(self.datos_conexion, self.origen)


class cajacierres:

    def __init__(self, datos, v_or):
        self.datos_conexion = datos
        self.origen = v_or

        if self.origen.estab is not None:
            #cerrar = self.comprobar_cierre_arqueo()
            cerrar = True

            if not cerrar:
                eleccion = Mens.pregunta_generico(
                    "Aún no ha sido registrado el Arqueo de Caja",
                    "Se ha registrado movimiento desde el último Arqueo.\n" +
                    "¿Desea registra dicho Arqueo en este momento?")

                if eleccion:
                    from arqueos import arqueos
                    arqueos(self.datos_conexion, self.origen.estab,
                        self.origen.caja, self.origen.numero)
                else:
                    self.cerrar_caja()
            else:
                self.cerrar_caja()

    def cerrar_caja(self):
        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.datos_conexion)

        Op.insertar(conexion, "cajacierres", self.origen.estab + ", " + self.origen.caja)

        conexion.commit()
        conexion.close()  # Finaliza la conexión

        self.origen.estab = self.origen.caja = self.origen.numero = None
        self.origen.verificar_permisos_caja(False)

    def comprobar_cierre_arqueo(self):
        # Si fechahora de Arqueo es posterior a última factura registrada para esta Caja,
        # retorna 1 (Verdadero, puede cerrar caja), sino 0 (Falso, no puede cerrar caja)
        conexion = Op.conectar(self.datos_conexion)
        cursor = conexion.cursor()
        cursor.execute("SELECT IF(" +
            "((" +
                "SELECT IFNULL(" +
                    "(" +
                        "SELECT FechaHora FROM arqueos_s WHERE NroArqueo = (" +
                            "SELECT IFNULL(MAX(NroArqueo), 0) FROM arqueos WHERE NroPuntoExpedicion = 1 AND NroEstablecimiento = 1" +
                        ") AND NroPuntoExpedicion = 1 AND NroEstablecimiento = 1" +
                    "), NOW()" +
                ")" +
            ") > (" +
                "SELECT IFNULL(" +
                    "(" +  # Modificar para seleccionar el timbrado
                        "SELECT FechaHora FROM facturaventas_s WHERE NroFactura = (" +
                            "SELECT IFNULL(MAX(NroFactura), 0) FROM facturaventas_s WHERE NroPuntoExpedicion = 1 AND NroEstablecimiento = 1" +
                        ") AND NroPuntoExpedicion = 1 AND NroEstablecimiento = 1" +
                    "), NOW()" +
                ")" +
            ")), 1, 0" +
        ")")
        datos = cursor.fetchall()
        conexion.close()  # Finaliza la conexión

        cerrar = True if datos[0][0] == 1 else False
        return cerrar
