#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen):
        self.editando = edit
        self.nav = origen

        arch = Op.archivo("abm_personas")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de " + self.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)   # Código
        self.obj("txt_01").set_max_length(12)   # Nro. Doc. (Persona)
        self.obj("txt_02").set_max_length(10)   # Nacionalidad
        self.obj("txt_03").set_max_length(10)   # Rol
        self.obj("txt_04").set_max_length(250)  # Observaciones

        self.obj("txt_05").set_max_length(50)   # Nombres
        self.obj("txt_06").set_max_length(50)
        self.obj("txt_07").set_max_length(50)   # Apellidos
        self.obj("txt_08").set_max_length(50)
        self.obj("txt_12").set_max_length(10)   # Ocupación

        self.obj("txt_13").set_max_length(50)   # Razón Social
        self.obj("txt_14").set_max_length(20)   # Contacto
        self.obj("txt_16").set_max_length(75)   # Página Web

        self.obj("txt_17").set_max_length(100)  # Medio Contacto
        self.obj("txt_18").set_max_length(100)  # Observaciones

        self.obj("txt_19").set_max_length(20)   # Zona de Ventas
        self.obj("txt_20").set_max_length(20)   # Vendedor
        self.obj("txt_22").set_max_length(50)   # Máximo Crédito

        self.obj("txt_23").set_max_length(10)   # Pais Nac.
        self.obj("txt_24").set_max_length(10)   # Dept. Nac.
        self.obj("txt_25").set_max_length(10)   # Ciudad Nac.
        self.obj("txt_26").set_max_length(10)   # Nro. Seguro
        self.obj("txt_27").set_max_length(7)    # ID Asegurado

        self.obj("txt_29").set_max_length(20)   # Banco
        self.obj("txt_30").set_max_length(20)   # Nro. Cuenta

        self.obj("txt_00").set_tooltip_text("Ingrese el Código de " + self.nav.titulo)
        self.obj("txt_01").set_tooltip_text("Ingrese el Nro. de Documento de " + self.nav.titulo)
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("la Nacionalidad de " + self.nav.titulo))
        self.obj("txt_02_1").set_tooltip_text("Descripción de la Nacionalidad")
        self.obj("txt_03").set_tooltip_text(Mens.usar_boton("el Rol de " + self.nav.titulo))
        self.obj("txt_03_1").set_tooltip_text("Descripción del Rol que tiene en la empresa")
        self.obj("txt_04").set_tooltip_text("Ingrese algunas Observaciones acerca de " + self.nav.titulo)
        self.obj("txt_01").grab_focus()

        self.obj("txt_05").set_tooltip_text("Ingrese el Primer Nombre de " + self.nav.titulo)
        self.obj("txt_06").set_tooltip_text("Ingrese el Primer Nombre de " + self.nav.titulo)
        self.obj("txt_07").set_tooltip_text("Ingrese el Primer Nombre de " + self.nav.titulo)
        self.obj("txt_08").set_tooltip_text("Ingrese el Primer Nombre de " + self.nav.titulo)
        self.obj("txt_09").set_tooltip_text(Mens.usar_boton("la Fecha de Nacimiento de " + self.nav.titulo))
        self.obj("txt_12").set_tooltip_text(Mens.usar_boton("la Ocupación de " + self.nav.titulo))
        self.obj("txt_12_1").set_tooltip_text("Descripción de la Ocupación")

        self.obj("txt_13").set_tooltip_text("Ingrese la Razón Social de la Empresa")
        self.obj("txt_14").set_tooltip_text(Mens.usar_boton("el Contacto en la Empresa"))
        self.obj("txt_14_1").set_tooltip_text("Nombre y Apellido del Contacto en la Empresa")
        self.obj("txt_14_2").set_tooltip_text("Dirección del Contacto en la Empresa")
        self.obj("txt_14_3").set_tooltip_text("Teléfono del Contacto en la Empresa")
        self.obj("txt_16").set_tooltip_text("Ingrese la Página Web de la Empresa")

        self.obj("txt_17").set_tooltip_text("Ingrese el Medio de Contacto (teléfono, e-mail...)")
        self.obj("txt_18").set_tooltip_text("Ingrese una Observación sobre el Medio de Contacto")

        self.obj("txt_19").set_tooltip_text(Mens.usar_boton("la Zona de Ventas en la que se ubica el Cliente"))
        self.obj("txt_19_1").set_tooltip_text("Descripción de la Zona de Ventas")
        self.obj("txt_20").set_tooltip_text(Mens.usar_boton("el Vendedor asignado al Cliente"))
        self.obj("txt_20_1").set_tooltip_text("Nombre y Apellido del Vendedor asignado")
        self.obj("txt_20_2").set_tooltip_text("Dirección del Vendedor asignado")
        self.obj("txt_20_3").set_tooltip_text("Teléfono del Vendedor asignado")
        self.obj("txt_22").set_tooltip_text("Ingrese el Monto máximo de Crédito que se podrá conceder al Cliente")

        self.obj("txt_23").set_tooltip_text(Mens.usar_boton("el Pais de Nacimiento del Empleado"))
        self.obj("txt_23_1").set_tooltip_text("Nombre del Pais de Nacimiento")
        self.obj("txt_24").set_tooltip_text(Mens.usar_boton("el Departamento de Nacimiento del Empleado"))
        self.obj("txt_24_1").set_tooltip_text("Nombre del Departamento de Nacimiento")
        self.obj("txt_25").set_tooltip_text(Mens.usar_boton("la Ciudad de Nacimiento del Empleado"))
        self.obj("txt_25_1").set_tooltip_text("Nombre de la Ciudad de Nacimiento")
        self.obj("txt_26").set_tooltip_text("Ingrese Número de Seguro en IPS")
        self.obj("txt_27").set_tooltip_text("Ingrese ID de Asegurado en IPS")

        self.obj("txt_29").set_tooltip_text(Mens.usar_boton("la Entidad Financiera con que trabaja la Persona"))
        self.obj("txt_29_1").set_tooltip_text("Razón Social de la Entidad Financiera")
        self.obj("txt_29_2").set_tooltip_text("RUC de la Entidad Financiera")
        self.obj("txt_29_3").set_tooltip_text("Dirección de la Entidad Financiera")
        self.obj("txt_29_4").set_tooltip_text("Teléfono de la Entidad Financiera")
        self.obj("txt_30").set_tooltip_text("Ingrese el Número de Cuenta Bancaria")

        arch.connect_signals(self)

        self.txt_cod_rol, self.txt_des_rol = self.obj("txt_03"), self.obj("txt_03_1")
        self.txt_cod_ocu, self.txt_des_ocu = self.obj("txt_12"), self.obj("txt_12_1")

        self.txt_cod_zona, self.txt_des_zona = self.obj("txt_19"), self.obj("txt_19_1")
        self.txt_cod_vnd, self.txt_nom_vnd = self.obj("txt_20"), self.obj("txt_20_1")
        self.txt_dir_vnd, self.txt_tel_vnd = self.obj("txt_20_2"), self.obj("txt_20_3")

        self.txt_cod_dep, self.txt_des_dep = self.obj("txt_24"), self.obj("txt_24_1")
        self.txt_cod_ciu, self.txt_des_ciu = self.obj("txt_25"), self.obj("txt_25_1")

        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_01"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_10"), "estadosciviles", "idEstadoCivil")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_11"), "generos", "idGenero")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_15"), "tipoempresas", "idTipoEmpresa")

        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_17"), "tipomediocontactos", "idTipoMedioContacto")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_21"), "tipoclientes", "idTipoCliente")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_28"), "tiposeguros", "idTipoSeguro")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_29"), "tipodocumentos", "idTipoDocumento")

        self.obj("cmb_10").set_active(0)
        self.obj("cmb_11").set_active(0)
        self.obj("cmb_15").set_active(0)
        self.obj("cmb_21").set_active(0)
        self.obj("cmb_28").set_active(0)
        self.obj("cmb_29").set_active(0)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond_id = str(seleccion.get_value(iterador, 0))
            tipodoc = seleccion.get_value(iterador, 1)
            nrodoc = seleccion.get_value(iterador, 3)
            nac = str(seleccion.get_value(iterador, 10))
            desnac = seleccion.get_value(iterador, 11)
            rol = str(seleccion.get_value(iterador, 21))
            desrol = seleccion.get_value(iterador, 22)
            obs = seleccion.get_value(iterador, 23)
            act = True if seleccion.get_value(iterador, 24) == 1 else False

            obs = "" if obs is None else obs

            self.obj("txt_00").set_text(self.cond_id)
            self.obj("txt_01").set_text(nrodoc)

            # Asignación de Tipo de Documento en Combo
            model, i = self.obj("cmb_01").get_model(), 0
            while model[i][0] != tipodoc: i += 1
            self.obj("cmb_01").set_active(i)

            self.obj("txt_02").set_text(nac)
            self.obj("txt_02_1").set_text(desnac)
            self.obj("txt_03").set_text(rol)
            self.obj("txt_03_1").set_text(desrol)
            self.obj("txt_04").set_text(obs)

            # Datos de Persona Física o Jurídica
            conexion = Op.conectar(self.nav.datos_conexion)
            cursor = Op.consultar(conexion,
                "PrimerNombre, OtroNombre, PrimerApellido, OtroApellido, FechaNacimiento",
                "personafisicas_s", " WHERE " + self.nav.campoid + " = " + self.cond_id)
            datos = cursor.fetchall()

            if cursor.rowcount == 1:
                self.obj("notebook1").set_current_page(0)
                self.editando_fisicas = True
                self.editando_juridicas = False

                fecha = seleccion.get_value(iterador, 5)
                estcivil = int(seleccion.get_value(iterador, 12))
                genero = seleccion.get_value(iterador, 14)
                codocup = seleccion.get_value(iterador, 16)
                desocup = seleccion.get_value(iterador, 17)

                otro_nombre = "" if datos[0][1] is None else datos[0][1]
                otro_apellido = "" if datos[0][3] is None else datos[0][3]
                self.fechanac = str(datos[0][4])
                print(self.fechanac)

                self.obj("txt_05").set_text(datos[0][0])
                self.obj("txt_06").set_text(otro_nombre)
                self.obj("txt_07").set_text(datos[0][2])
                self.obj("txt_08").set_text(otro_apellido)
                self.obj("txt_09").set_text(fecha)

                # Asignación de Estado Civil en Combo
                model, i = self.obj("cmb_10").get_model(), 0
                while model[i][0] != estcivil: i += 1
                self.obj("cmb_10").set_active(i)

                # Asignación de Género en Combo
                model, i = self.obj("cmb_11").get_model(), 0
                while model[i][0] != genero: i += 1
                self.obj("cmb_11").set_active(i)

                self.obj("txt_12").set_text(codocup)
                self.obj("txt_12_1").set_text(desocup)
            else:
                self.obj("notebook1").set_current_page(1)
                self.editando_fisicas = False
                self.editando_juridicas = True

                razon = seleccion.get_value(iterador, 4)
                tipoemp = int(seleccion.get_value(iterador, 18))

                web = seleccion.get_value(iterador, 20)
                web = "" if web is None else web

                self.obj("txt_13").set_text(razon)
                self.obj("txt_16").set_text(web)

                # Asignación de Tipo de Empresa en Combo
                model, i = self.obj("cmb_15").get_model(), 0
                while model[i][0] != tipoemp: i += 1
                self.obj("cmb_15").set_active(i)

                # Datos de la Persona de Contacto
                cursor = Op.consultar(conexion,
                    "idContacto, NombreApellido, DireccionPrincipal, TelefonoPrincipal",
                    "personajuridicas_s", " WHERE " + self.nav.campoid + " = " + self.cond_id)
                datos = cursor.fetchall()

                codigo = "" if datos[0][0] is None else str(datos[0][0])
                razon = "" if datos[0][1] is None else datos[0][1]
                direccion = "" if datos[0][2] is None else datos[0][2]
                telefono = "" if datos[0][3] is None else datos[0][3]

                self.obj("txt_14").set_text(codigo)
                self.obj("txt_14_1").set_text(razon)
                self.obj("txt_14_2").set_text(direccion)
                self.obj("txt_14_3").set_text(telefono)

            # Datos de Clientes
            cursor = Op.consultar(conexion,
                "idTipoCliente, idZonaVenta, ZonaVenta, MaximoCredito, " +
                "idVendedor, NombreApellido, DireccionPrincipal, TelefonoPrincipal",
                "clientes_s", " WHERE idCliente = " + self.cond_id)
            datos = cursor.fetchall()

            if cursor.rowcount == 1:
                self.obj("txt_19").set_text(str(datos[0][1]))
                self.obj("txt_19_1").set_text(datos[0][2])
                self.obj("txt_20").set_text(str(datos[0][4]))
                self.obj("txt_20_1").set_text(datos[0][5])
                self.obj("txt_20_2").set_text(datos[0][6])
                self.obj("txt_20_3").set_text(datos[0][7])
                self.obj("txt_22").set_text(str(datos[0][3]))

                # Asignación de Tipo de Cliente en Combo
                model, i = self.obj("cmb_21").get_model(), 0
                while model[i][0] != datos[0][0]: i += 1
                self.obj("cmb_21").set_active(i)

                self.editando_cliente = True
            else:
                self.editando_cliente = False

            # Datos de Empleados
            cursor = Op.consultar(conexion,
                "idPaisNac, Pais, idDepartamentoNac, Departamento, " +
                "idCiudadNac, Ciudad, idTipoSeguro, NroSeguroIPS, idAsegurado",
                "empleados_s", " WHERE idEmpleado = " + self.cond_id)
            datos = cursor.fetchall()

            if cursor.rowcount == 1:
                nro_seg = "" if datos[0][7] is None else datos[0][7]
                id_aseg = "" if datos[0][8] is None else datos[0][8]

                self.obj("txt_23").set_text(str(datos[0][0]))
                self.obj("txt_23_1").set_text(datos[0][1])
                self.obj("txt_24").set_text(str(datos[0][2]))
                self.obj("txt_24_1").set_text(datos[0][3])
                self.obj("txt_25").set_text(str(datos[0][4]))
                self.obj("txt_25_1").set_text(datos[0][5])
                self.obj("txt_26").set_text(nro_seg)
                self.obj("txt_27").set_text(id_aseg)

                # Asignación de Tipo de Seguro en Combo
                model, i = self.obj("cmb_28").get_model(), 0
                while model[i][0] != datos[0][6]: i += 1
                self.obj("cmb_28").set_active(i)

                self.editando_empleado = True
            else:
                self.editando_empleado = False

            # Datos de Bancos
            cursor = Op.consultar(conexion,
                "idBanco, idTipoDocumento, NroDocumento, RazonSocial, " +
                "DireccionPrincipal, TelefonoPrincipal, NroCuenta",
                "personas_bancos_s", " WHERE " + self.nav.campoid + " = " + self.cond_id)
            datos = cursor.fetchall()

            if cursor.rowcount == 1:
                self.obj("txt_29").set_text(str(datos[0][0]))
                self.obj("txt_29_1").set_text(datos[0][3])

                # Asignación de Tipo de Documento en Combo
                model, i = self.obj("cmb_29").get_model(), 0
                while model[i][0] != datos[0][1]: i += 1
                self.obj("cmb_29").set_active(i)

                self.obj("txt_29_2").set_text(datos[0][2])
                self.obj("txt_29_3").set_text(datos[0][4])
                self.obj("txt_29_4").set_text(datos[0][5])
                self.obj("txt_30").set_text(datos[0][6])

                self.editando_banco = True
            else:
                self.editando_banco = False

            conexion.close()  # Finaliza la conexión

            self.obj("rad_act").set_active(act)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(
                self.nav.datos_conexion, self.nav.tabla + "_s", self.nav.campoid))

            self.obj("cmb_01").set_active(0)
            self.obj("rad_act").set_active(True)

            self.editando_fisicas = self.editando_juridicas \
            = self.editando_cliente = self.editando_empleado = self.editando_banco = False

        self.conexion = Op.conectar(self.nav.datos_conexion)
        self.principal_guardado = self.contacto_guardado = self.cliente_guardado \
        = self.empleado_guardado = self.banco_guardado = True

        self.fisica_juridica_visible(True)
        self.config_grilla_medio()
        self.cargar_grilla_medio()
        self.config_grilla_dir()
        self.cargar_grilla_dir()

        if "Empleado = 1" in self.nav.condicion:
            self.obj("notebook1").remove_page(1)  # Persona Jurídica
            self.obj("notebook2").remove_page(2)  # Cliente

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_principal_personas()
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def on_btn_nacionalidad_clicked(self, objeto):
        self.txt_cod_pais, self.txt_nac_pais = self.obj("txt_02"), self.obj("txt_02_1")

        from clases.llamadas import paises
        paises(self.nav.datos_conexion, self)

    def on_btn_rol_clicked(self, objeto):
        from clases.llamadas import rolpersonas
        rolpersonas(self.nav.datos_conexion, self)

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0 or len(self.obj("txt_03").get_text()) == 0 \
        or self.idTipoDoc == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Cód. de Nacionalidad", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_03"), "Cód. de Rol de Persona", self.obj("barraestado")):
                page = self.obj("notebook1").get_current_page()
                if page == 0:  # Personas Físicas
                    estado = self.verificacion_fisicas()
                else:  # Personas Jurídicas
                    estado = self.verificacion_juridicas()
            else:
                estado = False
        self.principal_guardado = False
        self.estadoedicion(estado)

    def on_cmb_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            if objeto == self.obj("cmb_01"):
                self.idTipoDoc = model[active][0]
                self.focus_out_event(self.obj("txt_01"), 0)  # Nro. Documento

            elif objeto == self.obj("cmb_10"):
                self.idEstadoCivil = model[active][0]
            elif objeto == self.obj("cmb_11"):
                self.idGenero = model[active][0]
            elif objeto == self.obj("cmb_15"):
                self.idTipoEmpresa = model[active][0]

            elif objeto == self.obj("cmb_21"):
                self.idTipoCliente = model[active][0]
                self.verificacion_cliente(0)

            elif objeto == self.obj("cmb_28"):
                self.idTipoSeguro = model[active][0]
                self.verificacion_empleado(0)

            elif objeto == self.obj("cmb_29"):
                self.idTipoDocBanco = model[active][0]
                self.focus_out_event(self.obj("txt_29_2"), 0)

            if objeto in (self.obj("cmb_01"), self.obj("cmb_10"),
            self.obj("cmb_11"), self.obj("cmb_15")):
                self.verificacion(0)
        else:
            if objeto in (self.obj("cmb_01"), self.obj("cmb_29")):
                tipo = "Tipos de Documentos de Identidad"
            elif objeto == self.obj("cmb_10"):
                tipo = "Estados Civiles"
            elif objeto == self.obj("cmb_11"):
                tipo = "Géneros"
            elif objeto == self.obj("cmb_15"):
                tipo = "Tipos de Empresas"
            elif objeto == self.obj("cmb_21"):
                tipo = "Tipos de Clientes"
            elif objeto == self.obj("cmb_28"):
                tipo = "Tipos de Seguros (IPS)"
            self.obj("barraestado").push(0, "No existen registros de " + tipo + " en el Sistema.")

    def on_notebook_focus_in_event(self, objeto, evento):
        if self.obj("hbox1").get_sensitive():  # Solo si no se edita en las pestañas
            if objeto == self.obj("notebook1"):
                self.fisica_juridica_visible(True)
            elif objeto == self.obj("notebook2"):
                self.fisica_juridica_visible(False)
            self.verificacion(0)

    def on_notebook_change_current_page(self, objeto):
        self.verificacion(0)
        print("Cambiando Tipo de Persona")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_02"):
                    self.on_btn_nacionalidad_clicked(0)
                elif objeto == self.obj("txt_03"):
                    self.on_btn_rol_clicked(0)
                elif objeto == self.obj("txt_09"):
                    self.on_btn_fechanac_clicked(0)
                elif objeto == self.obj("txt_12"):
                    self.on_btn_ocupacion_clicked(0)
                elif objeto == self.obj("txt_14"):
                    self.on_btn_contacto_clicked(0)
                elif objeto == self.obj("txt_19"):
                    self.on_btn_zona_clicked(0)
                elif objeto == self.obj("txt_20"):
                    self.on_btn_vendedor_clicked(0)
                elif objeto == self.obj("txt_23"):
                    self.on_btn_pais_clicked(0)
                elif objeto == self.obj("txt_24"):
                    self.on_btn_departamento_clicked(0)
                elif objeto == self.obj("txt_25"):
                    self.on_btn_ciudad_clicked(0)
                elif objeto in (self.obj("txt_29"), self.obj("txt_29_2")):
                    self.on_btn_banco_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_02"):
            tipo = "a Nacionalidad"
        elif objeto == self.obj("txt_03"):
            tipo = " Rol de Personas"
        elif objeto == self.obj("txt_09"):
            tipo = "a Fecha de Nacimiento"
        elif objeto == self.obj("txt_12"):
            tipo = "a Ocupación"
        elif objeto == self.obj("txt_14"):
            tipo = "a Persona de Contacto"
        elif objeto == self.obj("txt_19"):
            tipo = "a Zona de Ventas"
        elif objeto == self.obj("txt_20"):
            tipo = " Vendedor"
        elif objeto == self.obj("txt_23"):
            tipo = " País"
        elif objeto == self.obj("txt_24"):
            tipo = " Departamento"
        elif objeto == self.obj("txt_25"):
            tipo = "a Ciudad"
        elif objeto in (self.obj("txt_29"), self.obj("txt_29_2")):
            tipo = " Banco o Entidad Financiera"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un" + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_02"):
                self.obj("txt_02_1").set_text("")
            elif objeto == self.obj("txt_03"):
                self.obj("txt_03_1").set_text("")
            elif objeto == self.obj("txt_12"):
                self.obj("txt_12_1").set_text("")
            elif objeto == self.obj("txt_14"):  # Contacto
                self.obj("txt_14_1").set_text("")
                self.obj("txt_14_2").set_text("")
                self.obj("txt_14_3").set_text("")
            elif objeto == self.obj("txt_19"):
                self.obj("txt_19_1").set_text("")
            elif objeto == self.obj("txt_20"):  # Vendedor
                self.obj("txt_20_1").set_text("")
                self.obj("txt_20_2").set_text("")
                self.obj("txt_20_3").set_text("")
            elif objeto == self.obj("txt_23"):
                self.obj("txt_23_1").set_text("")
            elif objeto == self.obj("txt_24"):
                self.obj("txt_24_1").set_text("")
            elif objeto == self.obj("txt_25"):
                self.obj("txt_25_1").set_text("")
            elif objeto == self.obj("txt_29"):  # Banco
                self.obj("txt_29_1").set_text("")
                self.obj("txt_29_2").set_text("")
                self.obj("txt_29_3").set_text("")
                self.obj("txt_29_4").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond_id) and \
                Op.comprobar_numero(int, objeto, "Código", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion, "personas_s",
                        self.nav.campoid, valor, self.obj("txt_00"),
                        self.estadoedicion, self.obj("barraestado"),
                        "El Código introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                busq = "" if not self.editando else " AND " + self.nav.campoid + " <> " + self.cond_id
                Op.comprobar_unique(self.nav.datos_conexion, "personas_s", "NroDocumento",
                    "'" + valor + "' AND idTipoDocumento = '" + self.idTipoDoc + "'" + busq,
                    self.obj("txt_01"), self.estadoedicion, self.obj("barraestado"),
                    "El Nro. de Documento introducido ya ha sido registado.")

            elif objeto == self.obj("txt_02"):
                self.buscar_foraneos(objeto, self.obj("txt_02_1"),
                    "Nacionalidad", "paises", "Nacionalidad", "idPais", valor)

            elif objeto == self.obj("txt_03"):
                self.buscar_foraneos(objeto, self.obj("txt_03_1"),
                    "Rol de Persona", "rolpersonas", "Descripcion", "idRolPersona", valor)

            elif objeto == self.obj("txt_09"):
                if Op.compara_fechas(self.nav.datos_conexion, "'" + self.fechanac + "'", ">=", "NOW()"):
                    self.estadoedicion(False)
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "La Fecha de Nacimiento NO puede estar en el Futuro.")
                else:
                    self.obj("barraestado").push(0, "")

            elif objeto == self.obj("txt_12"):
                self.buscar_foraneos(objeto, self.obj("txt_12_1"),
                    "Ocupación", "ocupaciones", "Descripcion", "idOcupacion", valor)

            elif objeto == self.obj("txt_14"):
                if Op.comprobar_numero(int, objeto, "Cód. de Persona de Contacto", self.obj("barraestado")):
                    self.buscar_personas("idPersona, NombreApellido, DireccionPrincipal, " +
                        "TelefonoPrincipal", "personafisicas_s", "idPersona",
                        valor, "Cód. de Persona de Contacto", self.obj("txt_14"),
                        self.obj("txt_14_1"), self.obj("txt_14_2"), self.obj("txt_14_3"))

            elif objeto == self.obj("txt_19"):
                self.buscar_foraneos(objeto, self.obj("txt_19_1"),
                    "Zona de Venta", "zonaventas", "Descripcion", "idZonaVenta", valor)

            elif objeto == self.obj("txt_20"):
                if Op.comprobar_numero(int, objeto, "Cód. de Vendedor", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "NombreApellido, " +
                        "DireccionPrincipal, TelefonoPrincipal",
                        "vendedores_s", " WHERE idVendedor = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        direccion = "" if datos[0][1] is None else datos[0][1]
                        telefono = "" if datos[0][2] is None else datos[0][2]

                        self.obj("txt_20_1").set_text(datos[0][0])
                        self.obj("txt_20_2").set_text(direccion)
                        self.obj("txt_20_3").set_text(telefono)

                        self.obj("barraestado").push(0, "")
                        self.verificacion_cliente(0)
                    else:
                        self.obj("btn_guardar").set_sensitive(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "El Cód. de Vendedor no es válido.")
                        self.obj("txt_20_1").set_text("")
                        self.obj("txt_20_2").set_text("")
                        self.obj("txt_20_3").set_text("")

            elif objeto == self.obj("txt_23"):
                self.buscar_foraneos(objeto, self.obj("txt_23_1"),
                    "País", "paises", "Nombre", "idPais", valor)

            elif objeto == self.obj("txt_24") and len(self.obj("txt_23").get_text()) > 0:
                self.buscar_foraneos(objeto, self.obj("txt_24_1"),
                    "Departamento", "departamentos_s", "Nombre", "idDepartamento", valor,
                    " AND idPais = " + self.obj("txt_23").get_text())

            elif objeto == self.obj("txt_25") and len(self.obj("txt_24").get_text()) > 0 \
            and len(self.obj("txt_23").get_text()) > 0:
                self.buscar_foraneos(objeto, self.obj("txt_25_1"),
                    "Ciudad", "ciudades_s", "Nombre", "idCiudad", valor,
                    " AND idDepartamento = " + self.obj("txt_24").get_text() +
                    " AND idPais = " + self.obj("txt_23").get_text())

            elif objeto == self.obj("txt_29"):
                if Op.comprobar_numero(int, objeto, "Cód. de Banco", self.obj("barraestado")):
                    self.buscar_personas("idPersona, RazonSocial, DireccionPrincipal, " +
                        "TelefonoPrincipal, NroDocumento, idTipoDocumento",
                        "personajuridicas_s", "idPersona", valor, "Cód. de Banco",
                        self.obj("txt_29"), self.obj("txt_29_1"),
                        self.obj("txt_29_3"), self.obj("txt_29_4"),
                        self.obj("txt_29_2"), self.obj("cmb_29"))

            elif objeto == self.obj("txt_29_2"):
                self.buscar_personas("idPersona, RazonSocial, DireccionPrincipal, " +
                    "TelefonoPrincipal, NroDocumento, idTipoDocumento",
                    "personajuridicas_s", "NroDocumento", "'" + valor + "'" + \
                    " AND idTipoDocumento = '" + str(self.idTipoDocBanco) + "'",
                    "Nro. de Documento del Banco", self.obj("txt_29"), self.obj("txt_29_1"),
                    self.obj("txt_29_3"), self.obj("txt_29_4"),
                    self.obj("txt_29_2"), self.obj("cmb_29"))

    def buscar_foraneos(self, objeto, companero, nombre, tabla, campo_busq, campo_id, valor, condicion=""):
        if Op.comprobar_numero(int, objeto, "Cód. de " + nombre, self.obj("barraestado")):
            conexion = Op.conectar(self.nav.datos_conexion)
            cursor = Op.consultar(conexion, campo_busq, tabla,
                " WHERE " + campo_id + " = " + valor + condicion)
            datos = cursor.fetchall()
            cant = cursor.rowcount
            conexion.close()  # Finaliza la conexión

            if cant > 0:
                companero.set_text(datos[0][0])
                self.obj("barraestado").push(0, "")

                if objeto == self.obj("txt_19"):
                    self.verificacion_cliente(0)

                elif objeto in (self.obj("txt_23"), self.obj("txt_24"), self.obj("txt_25")):
                    if objeto == self.obj("txt_23"):  # País
                        self.focus_out_event(self.obj("txt_24"), 0)

                    elif objeto == self.obj("txt_24"):  # Departamento
                        self.focus_out_event(self.obj("txt_25"), 0)

                    self.verificacion_empleado(0)

                else:  # Principales
                    self.verificacion(0)

            else:
                if objeto in (self.obj("txt_19"), self.obj("txt_23"), self.obj("txt_24"),
                self.obj("txt_25"), self.obj("txt_29"), self.obj("txt_29_2")):
                    self.obj("btn_guardar").set_sensitive(False)
                else:
                    self.estadoedicion(False)

                objeto.grab_focus()
                self.obj("barraestado").push(0, "El Cód. de " + nombre + " no es válido.")
                companero.set_text("")

    def buscar_personas(self, campos, tabla, campo_busq, valor, titulo, codigo, razon, direc, telef, nrodoc=None, tipodoc=None):
        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, campos, tabla,
            " WHERE " + campo_busq + " = " + valor)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            direccion = "" if datos[0][2] is None else datos[0][2]
            telefono = "" if datos[0][3] is not None else datos[0][3]

            codigo.set_text(str(datos[0][0]))
            razon.set_text(datos[0][1])
            direc.set_text(direccion)
            telef.set_text(telefono)

            if nrodoc is not None:
                nrodoc.set_text(datos[0][4])

            if tipodoc is not None:
                # Asignación de Tipo de Documento en Combo
                model, i = tipodoc.get_model(), 0
                while model[i][0] != datos[0][5]: i += 1
                tipodoc.set_active(i)

            self.obj("barraestado").push(0, "")

            if codigo == self.obj("txt_14"):  # Contacto
                self.verificacion(0)
            elif codigo == self.obj("txt_20"):
                self.verificacion_cliente(0)
            else:
                self.verificacion_banco(0)

        else:
            if codigo == self.obj("txt_14"):  # Contacto
                self.estadoedicion(False)
            else:
                self.obj("btn_guardar").set_sensitive(False)

            self.obj("barraestado").push(0, "El " + titulo + " no es válido.")
            razon.set_text("")
            direc.set_text("")
            telef.set_text("")

            if nrodoc is not None:  # Bancos
                if campo_busq == "NroDocumento":
                    nrodoc.grab_focus()
                    codigo.set_text("")
                else:
                    codigo.grab_focus()
                    nrodoc.set_text("")
            else:
                codigo.grab_focus()

    def guardar_principal_personas(self):
        v0 = self.obj("txt_00").get_text()  # idPersona

        # Guardar Encabezado y datos de Persona Fñisicas y Jurídicas
        if not self.principal_guardado:
            v1 = self.obj("txt_01").get_text()
            v2 = self.obj("txt_02").get_text()  # Nacionalidad
            v3 = self.obj("txt_03").get_text()  # Rol
            v4 = self.obj("txt_04").get_text()  # Observaciones

            v3 = "NULL" if len(v3) == 0 else "'" + v3 + "'"
            v4 = "NULL" if len(v4) == 0 else "'" + v4 + "'"
            v5 = "1" if self.obj("rad_act").get_active() else "0"

            sql = v0 + ", " + v2 + ", " + v3 + ", '" + self.idTipoDoc + "', '" + v1 + "', " + v4 + ", " + v5
            if not self.editando:
                Op.insertar(self.conexion, self.nav.tabla, sql)
            else:
                Op.modificar(self.conexion, self.nav.tabla, self.cond_id + ", " + sql)

            # Guardar Datos de Personas Físicas o Jurídicas
            page = self.obj("notebook1").get_current_page()
            if page == 0:
                # Guardar Personas Físicas
                v1 = self.obj("txt_05").get_text()  # Nombre
                v2 = self.obj("txt_06").get_text()
                v3 = self.obj("txt_07").get_text()  # Apellidos
                v4 = self.obj("txt_08").get_text()
                v5 = self.obj("txt_12").get_text()  # Ocupación

                v2 = "NULL" if len(v2) == 0 else "'" + v2 + "'"
                v4 = "NULL" if len(v4) == 0 else "'" + v4 + "'"

                sql = v0 + ", " + str(self.idEstadoCivil) + ", '" + self.idGenero + "', " + v5 + ", " + \
                    "'" + v1 + "', " + v2 + ", '" + v3 + "', " + v4 + ", '" + self.fechanac + "'"

                if not self.editando_fisicas:
                    Op.insertar(self.conexion, "personafisicas", sql)
                    self.editando_fisicas = True
                else:
                    Op.modificar(self.conexion, "personafisicas", sql)

                # Eliminar Datos de Persona Jurídica
                cursor = Op.consultar(self.conexion, self.nav.campoid,
                "personajuridicas_s", " WHERE " + self.nav.campoid + " = " + v0)
                datos = cursor.fetchall()

                if cursor.rowcount > 0:
                    Op.eliminar(self.conexion, "personajuridicas", v0)

            else:
                # Guardar Personas Jurídicas
                v1 = self.obj("txt_13").get_text()  # Razón Social
                v2 = self.obj("txt_16").get_text()
                v2 = "NULL" if len(v2) == 0 else "'" + v2 + "'"

                sql = v0 + ", " + str(self.idTipoEmpresa) + ", '" + v1 + "', " + v2

                if not self.editando_juridicas:
                    Op.insertar(self.conexion, "personajuridicas", sql)
                    self.editando_juridicas = True
                else:
                    Op.modificar(self.conexion, "personajuridicas", sql)

                # Guardar Persona de Contacto
                if not self.contacto_guardado:
                    v3 = self.obj("txt_14").get_text()

                    if len(v3) == 0:
                        if self.editando_contactos:  # Si está vacío y existía
                            Op.eliminar(self.conexion, "personajuridicas_contactos", v0)
                    else:
                        sql = v0 + ", " + v3

                        if not self.editando_contactos:
                            Op.insertar(self.conexion, "personajuridicas_contactos", sql)
                            self.editando_contactos = True
                        else:
                            Op.modificar(self.conexion, "personajuridicas_contactos", sql)

                    self.contacto_guardado = True

                # Eliminar Datos de Persona Física
                cursor = Op.consultar(self.conexion, self.nav.campoid,
                "personafisicas_s", " WHERE " + self.nav.campoid + " = " + v0)
                datos = cursor.fetchall()

                if cursor.rowcount > 0:
                    Op.eliminar(self.conexion, "personafisicas", v0)

            self.cond_id = v0  # Nuevo idPersona original
            self.principal_guardado = self.editando = True

        # Guardar Datos de Clientes
        if not self.cliente_guardado:
            v1 = self.obj("txt_19").get_text()
            v2 = self.obj("txt_20").get_text()  # Vendedor
            v3 = self.obj("txt_22").get_text()

            if len(v1) == 0 or len(v2) == 0 or len(v3) == 0 or self.idTipoCliente == -1:
                if self.editando_cliente:  # Si está vacío y existía
                    Op.eliminar(self.conexion, "clientes", v0)
                    self.editando_cliente = False
            else:
                sql = v0 + ", " + str(self.idTipoCliente) + ", " + \
                    v1 + ", " + v2 + ", " + v3

                if not self.editando_cliente:
                    Op.insertar(self.conexion, "clientes", sql)
                    self.editando_cliente = True
                else:
                    Op.modificar(self.conexion, "clientes", sql)

            self.cliente_guardado = True

        # Guardar Datos de Empleados
        if not self.empleado_guardado:
            v1 = self.obj("txt_23").get_text()
            v2 = self.obj("txt_24").get_text()
            v3 = self.obj("txt_25").get_text()  # Ciudad
            v4 = self.obj("txt_26").get_text()
            v5 = self.obj("txt_27").get_text()

            if len(v1) == 0 or len(v2) == 0 or len(v3) == 0 or self.idTipoSeguro == -1:
                if self.editando_empleado:  # Si está vacío y existía
                    Op.eliminar(self.conexion, "empleados", v0)
                    self.editando_empleado = False
            else:
                v4 = "NULL" if len(v4) == 0 else "'" + v4 + "'"
                v5 = "NULL" if len(v5) == 0 else "'" + v5 + "'"

                sql = v0 + ", " + v1 + ", " + v2 + ", " + v3 + ", " + \
                    str(self.idTipoSeguro) + ", " + v4 + ", " + v5

                if not self.editando_empleado:
                    Op.insertar(self.conexion, "empleados", sql)
                    self.editando_empleado = True
                else:
                    Op.modificar(self.conexion, "empleados", sql)

            self.empleado_guardado = True

        # Guardar Datos de Clientes
        if not self.cliente_guardado:
            v1 = self.obj("txt_29").get_text()
            v2 = self.obj("txt_30").get_text()

            if len(v1) == 0 or len(v2) == 0:
                if self.editando_banco:  # Si está vacío y existía
                    Op.eliminar(self.conexion, "personas_bancos", v0)
                    self.editando_banco = False
            else:
                sql = v0 + ", " + v1 + ", '" + v2 + "'"

                if not self.editando_banco:
                    Op.insertar(self.conexion, "personas_bancos", sql)
                    self.editando_banco = True
                else:
                    Op.modificar(self.conexion, "personas_bancos", sql)

            self.banco_guardado = True

    def fisica_juridica_visible(self, estado):
        self.obj("vbox11").set_visible(estado)
        self.obj("vbox21").set_visible(estado)
        self.obj("vbox31").set_visible(not estado)
        self.obj("vbox41").set_visible(not estado)
        self.obj("vbox51").set_visible(not estado)
        self.obj("vbox61").set_visible(not estado)
        self.obj("vbox71").set_visible(not estado)

        # Para evitar que se haga visible junto con el padre
        self.estadoedicion_medio_contacto(False)

    def estadoedicion(self, estado):
        self.obj("vbox31").set_sensitive(estado)
        self.obj("vbox41").set_sensitive(estado)
        self.obj("vbox51").set_sensitive(estado)
        self.obj("vbox71").set_sensitive(estado)

        if self.obj("notebook1").get_current_page() == 1:
            self.obj("vbox61").set_sensitive(False)
        else:
            self.obj("vbox61").set_sensitive(estado)

        self.obj("btn_guardar").set_sensitive(estado)

    def estadoedicion_pestanas(self, estado, origen):
        self.obj("hbox1").set_sensitive(estado)
        self.obj("hbox2").set_sensitive(estado)
        self.obj("notebook1").set_sensitive(estado)
        self.obj("hbox5").set_sensitive(estado)
        self.obj("hbox6").set_sensitive(estado)
        self.obj("hbox7").set_sensitive(estado)
        self.obj("hbox8").set_sensitive(estado)

        self.obj("vbox31").set_sensitive(estado)

        if origen != 0:
            self.obj("vbox41").set_sensitive(estado)
        if origen != 1:
            self.obj("vbox51").set_sensitive(estado)
        if origen != 2 and self.obj("notebook1").get_current_page() == 0:
            self.obj("vbox61").set_sensitive(estado)
        if origen != 3:
            self.obj("vbox71").set_sensitive(estado)

        self.obj("btn_guardar").set_sensitive(estado)

##### Personas Físicas #################################################

    def on_btn_fechanac_clicked(self, objeto):
        self.obj("txt_09").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_09").set_text(lista[0])
            self.fechanac = lista[1]

    def on_btn_limpiar_fechanac_clicked(self, objeto):
        self.obj("txt_09").set_text("")
        self.obj("txt_09").grab_focus()

    def on_btn_ocupacion_clicked(self, objeto):
        from clases.llamadas import ocupaciones
        ocupaciones(self.nav.datos_conexion, self)

    def verificacion_fisicas(self):
        if len(self.obj("txt_05").get_text()) == 0 or len(self.obj("txt_07").get_text()) == 0 \
        or len(self.obj("txt_09").get_text()) == 0 or len(self.obj("txt_12").get_text()) == 0 \
        or self.idEstadoCivil == -1 or self.idGenero == -1:
            estado = False
        else:
            estado = True if Op.comprobar_numero(int, self.obj("txt_12"),
                "Cód. de Ocupación", self.obj("barraestado")) else False
        return estado

##### Personas Jurídicas ###############################################

    def on_btn_contacto_clicked(self, objeto):
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_14"), self.obj("txt_14_1")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_14_2"), self.obj("txt_14_3")

        from clases.llamadas import personas
        personas(self.nav.datos_conexion, self, "Empresa = 0")

    def verificacion_contacto(self, objeto):
        if len(self.obj("txt_13").get_text()) == 0:
            estado = True
        else:
            estado = False

            if Op.comprobar_numero(int, self.obj("txt_14"),
            "Cód. de Persona de Contacto", self.obj("barraestado")):
                self.verificacion(0)
            else:
                self.estadoedicion(False)

        self.contacto_guardado = estado

    def verificacion_juridicas(self):
        if len(self.obj("txt_13").get_text()) == 0 or self.idTipoEmpresa == -1:
            estado = False
        else:
            estado = True
        return estado

##### Direcciones ######################################################

    def on_btn_nuevo_dir_clicked(self, objeto):
        self.guardar_principal_personas()

        from registros.direcciones import direcciones
        direcciones(False, False, self)  # Editando (False), Establecimiento (False)

    def on_btn_modificar_dir_clicked(self, objeto):
        self.guardar_principal_personas()

        try:
            seleccion, iterador = self.obj("grilla_dir").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Direcciones. Luego presione Modificar Dirección.")
        else:
            from registros.direcciones import direcciones
            direcciones(True, False, self)  # Editando (True), Establecimiento (False)

    def on_btn_eliminar_dir_clicked(self, objeto):
        self.guardar_principal_personas()

        try:
            seleccion, iterador = self.obj("grilla_dir").get_selection().get_selected()
            iddir = str(seleccion.get_value(iterador, 13))
            idper = self.obj("txt_00").get_text()
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Direcciones. Luego presione Eliminar Dirección.")
        else:
            valor0 = str(seleccion.get_value(iterador, 0))
            valor1 = seleccion.get_value(iterador, 6)
            valor2 = seleccion.get_value(iterador, 8)
            valor3 = seleccion.get_value(iterador, 9)
            valor4 = seleccion.get_value(iterador, 10)

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Código: " + valor0 + "Ciudad: " + valor1 + "\nBarrio: " + valor2 +
                "\nDirección: " + valor3 + "\nNro. Casa: " + valor4)

            self.obj("grilla_dir").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "personas_direcciones", idper + ", " + valor0)
                Op.eliminar(self.conexion, "direcciones", iddir)
                self.cargar_grilla_dir()

    def on_grilla_dir_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_dir_clicked(0)

    def on_grilla_dir_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_dir_clicked(0)

    def on_treeviewcolumn_dir_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla_dir").set_search_column(i)

    def config_grilla_dir(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)

        col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Cód. País", celda0, 1, True, 75, 150)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("País", celda1, 2, True, 150, 220)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Cód. Depart.", celda0, 3, True, 75, 150)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Departamento", celda1, 4, True, 150, 220)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Cód. Ciudad", celda0, 5, True, 75, 150)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Ciudad", celda1, 6, True, 150, 220)
        col6.set_sort_column_id(6)
        col7 = Op.columnas("Cód. Barrio", celda0, 7, True, 75, 150)
        col7.set_sort_column_id(7)
        col8 = Op.columnas("Barrio", celda1, 8, True, 150, 220)
        col8.set_sort_column_id(8)
        col9 = Op.columnas("Calles", celda1, 9, True, 300, 500)
        col9.set_sort_column_id(9)
        col10 = Op.columnas("Nro. Casa", celda0, 10, True, 100, 150)
        col10.set_sort_column_id(10)
        col11 = Op.columnas("Observaciones", celda0, 11, True, 100, 150)
        col11.set_sort_column_id(11)
        col12 = Op.columna_active("Principal", 12)
        col12.set_sort_column_id(12)

        lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_dir_clicked)
            self.obj("grilla_dir").append_column(columna)
        self.obj("grilla_dir").append_column(col12)

        self.obj("grilla_dir").set_rules_hint(True)
        self.obj("grilla_dir").set_search_column(1)
        self.obj("grilla_dir").set_property('enable-grid-lines', 3)

        lista = ListStore(int, int, str, int, str, int, str,
            int, str, str, str, str, int, int)
        self.obj("grilla_dir").set_model(lista)
        self.obj("grilla_dir").show()

    def cargar_grilla_dir(self):
        cursor = Op.consultar(self.conexion, "idDireccionPer, " +
            "idPais, Pais, idDepartamento, Departamento, idCiudad, Ciudad, " +
            "idBarrio, Barrio, Direccion, NroCasa, Observaciones, " +
            "Principal, idDireccion, idPersona", "personas_direcciones_s",
            " WHERE idPersona = " + self.obj("txt_00").get_text())
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla_dir").get_model()
        lista.clear()

        for i in range(0, cant):
            nrocasa = "" if datos[i][10] is None else str(datos[i][10])
            lista.append([datos[i][0], datos[i][1], datos[i][2],
                datos[i][3], datos[i][4], datos[i][5], datos[i][6],
                datos[i][7], datos[i][8], datos[i][9], nrocasa, datos[i][11],
                datos[i][12], datos[i][13]])

        cant = str(cant) + " dirección encontrada." if cant == 1 \
            else str(cant) + " direcciones encontradas."
        self.obj("barraestado").push(0, cant)

##### Medios de Contacto ###############################################

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
        self.guardar_principal_personas()

        try:
            seleccion, iterador = self.obj("grilla_medio").get_selection().get_selected()
            valor1 = str(seleccion.get_value(iterador, 1))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista de Medios de Contacto. Luego presione Eliminar.")
        else:
            valor2 = seleccion.get_value(iterador, 2)
            valor3 = seleccion.get_value(iterador, 3)
            idper = self.obj("txt_00").get_text()

            eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
                "Medio de Contacto: " + valor2 + "\nDescripción: " + valor3)

            self.obj("grilla_medio").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "personas_mediocontactos", idper + ", " + valor1)
                self.cargar_grilla_medio()

    def on_grilla_medio_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_medio_clicked(0)

    def on_grilla_medio_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_medio_clicked(0)

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
            "TipoMedioContacto, Descripcion, Observaciones", "personas_mediocontactos_s",
            " WHERE idPersona = " + self.obj("txt_00").get_text())
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla_medio").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([i + 1, datos[i][0], datos[i][1], datos[i][2], datos[i][3]])

        cant = str(cant) + " medio de contacto encontrado." if cant == 1 \
            else str(cant) + " medios de contactos encontrados."
        self.obj("barraestado").push(0, cant)

    def estadoedicion_medio_contacto(self, estado):
        self.obj("hbuttonbox2").set_sensitive(not estado)
        self.obj("grilla_medio").set_sensitive(not estado)

        self.obj("hbuttonbox3").set_visible(estado)  # Guardar-Cancelar
        self.obj("vbox411").set_visible(estado)

##### Agregar-Modificar Medios de Contacto #############################

    def funcion_medio_contacto(self):
        self.guardar_principal_personas()

        if self.editando_medio_contacto:
            seleccion, iterador = self.obj("grilla_medio").get_selection().get_selected()
            des = seleccion.get_value(iterador, 3)
            obs = seleccion.get_value(iterador, 4)
            obs = "" if obs is None else obs

            self.obj("txt_17").set_text(des)
            self.obj("txt_18").set_text(obs)

            # Asignación de Tipo de Medio de Contacto en Combo
            model, i = self.obj("cmb_17").get_model(), 0
            while model[i][0] != self.cond_medio_contacto: i += 1
            self.obj("cmb_17").set_active(i)
        else:
            self.obj("txt_17").set_text("")
            self.obj("cmb_17").set_active(0)
            self.obj("txt_18").set_text("")

        self.estadoedicion_medio_contacto(True)
        self.estadoedicion_pestanas(False, 0)

        self.obj("btn_guardar_medio").set_sensitive(False)
        self.obj("grilla_medio").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

    def on_btn_guardar_medio_clicked(self, objeto):
        self.guardar_principal_personas()

        v0 = self.obj("txt_00").get_text()  # idPersona
        v1 = self.obj("txt_17").get_text()

        v2 = self.obj("txt_18").get_text()
        v2 = "NULL" if len(v2) == 0 else "'" + v2 + "'"

        sql = v0 + ", " + str(self.idTipoMedioContacto) + ", '" + v1 + "', " + v2

        if not self.editando_medio_contacto:
            Op.insertar(self.conexion, "personas_mediocontactos", sql)
        else:
            Op.modificar(self.conexion, "personas_mediocontactos",
                str(self.cond_medio_contacto) + ", " + sql)

        self.on_btn_cancelar_medio_clicked(0)
        self.cargar_grilla_medio()

    def on_btn_cancelar_medio_clicked(self, objeto):
        self.estadoedicion_medio_contacto(False)
        self.estadoedicion_pestanas(True, 0)

        self.obj("txt_17").set_text("")
        self.obj("cmb_17").set_active(-1)
        self.obj("txt_18").set_text("")

    def verificacion_medio(self, objeto):
        estado = False if len(self.obj("txt_17").get_text()) == 0 else True
        self.obj("btn_guardar_medio").set_sensitive(estado)

    def medio_contacto_focus_out_event(self, objeto, evento):
        self.on_cmb_17_changed(self.obj("cmb_17"))

    def on_cmb_17_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            persona = self.obj("txt_00").get_text()
            condicion = "" if not self.editando_medio_contacto else \
            " AND idTipoMedioContacto <> " + str(self.cond_medio_contacto)

            cursor = Op.consultar(self.conexion, "Descripcion",
                "personas_mediocontactos_s", " WHERE idPersona = " + persona +
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

##### Clientes #########################################################

    def on_btn_zona_clicked(self, objeto):
        from clases.llamadas import zonaventas
        zonaventas(self.nav.datos_conexion, self)

    def on_btn_vendedor_clicked(self, objeto):
        from clases.llamadas import vendedores
        vendedores(self.datos_conexion, self)

    def verificacion_cliente(self, objeto):
        if len(self.obj("txt_19").get_text()) == 0 and len(self.obj("txt_20").get_text()) == 0 \
        and len(self.obj("txt_22").get_text()) == 0:
            estado = edicion = True  # Si todos están vacios
        else:
            estado = False

            if len(self.obj("txt_19").get_text()) == 0 or len(self.obj("txt_20").get_text()) == 0 \
            or len(self.obj("txt_22").get_text()) == 0 or self.idTipoCliente == -1:
                edicion = False
            else:
                if Op.comprobar_numero(int, self.obj("txt_19"), "Cód. de Zona de Ventas", self.obj("barraestado")) \
                and Op.comprobar_numero(int, self.obj("txt_20"), "Cód. de Vendedor", self.obj("barraestado")) \
                and Op.comprobar_numero(float, self.obj("txt_22"), "Monto Máximo de Crédito", self.obj("barraestado")):
                    edicion = True
                else:
                    edicion = False

        self.estadoedicion_pestanas(edicion, 1)
        self.cliente_guardado = estado

##### Empleados ########################################################

    def on_btn_ciudad_clicked(self, objeto):
        self.txt_cod_pais, self.txt_des_pais = self.obj("txt_23"), self.obj("txt_23_1")

        condicion = None if len(self.obj("txt_24_1").get_text()) == 0 \
            else [self.obj("txt_23").get_text(), self.obj("txt_24").get_text()]

        from clases.llamadas import ciudades
        ciudades(self.nav.datos_conexion, self, condicion)

    def on_btn_departamento_clicked(self, objeto):
        self.txt_cod_pais, self.txt_des_pais = self.obj("txt_23"), self.obj("txt_23_1")

        condicion = None if len(self.obj("txt_23_1").get_text()) == 0 \
            else self.obj("txt_23").get_text()

        from clases.llamadas import departamentos
        departamentos(self.nav.datos_conexion, self, condicion)

    def on_btn_pais_clicked(self, objeto):
        self.txt_cod_pais, self.txt_des_pais = self.obj("txt_23"), self.obj("txt_23_1")

        from clases.llamadas import paises
        paises(self.nav.datos_conexion, self)

    def verificacion_empleado(self, objeto):
        if len(self.obj("txt_23").get_text()) == 0 and len(self.obj("txt_24").get_text()) == 0 \
        and len(self.obj("txt_25").get_text()) == 0 and len(self.obj("txt_26").get_text()) == 0 \
        and len(self.obj("txt_27").get_text()) == 0:
            estado = edicion = True  # Si todos están vacios
        else:
            estado = False

            if len(self.obj("txt_23").get_text()) == 0 or len(self.obj("txt_24").get_text()) == 0 \
            or len(self.obj("txt_25").get_text()) == 0 or self.idTipoSeguro == -1:
                edicion = False
            else:
                if Op.comprobar_numero(int, self.obj("txt_23"), "Cód. de País", self.obj("barraestado")) \
                and Op.comprobar_numero(int, self.obj("txt_24"), "Cód. de Departamento", self.obj("barraestado")) \
                and Op.comprobar_numero(int, self.obj("txt_25"), "Cód. de Ciudad", self.obj("barraestado")):
                    edicion = True
                else:
                    edicion = False

        self.estadoedicion_pestanas(edicion, 2)
        self.empleado_guardado = estado

##### Bancos ###########################################################

    def on_btn_banco_clicked(self, objeto):
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_29"), self.obj("txt_29_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_29_2"), self.obj("cmb_29")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_29_3"), self.obj("txt_29_4")

        from clases.llamadas import personas
        personas(self.nav.datos_conexion, self, "Empresa = 1")

    def verificacion_banco(self, objeto):
        if len(self.obj("txt_29").get_text()) == 0 and len(self.obj("txt_29_2").get_text()) == 0 \
        and len(self.obj("txt_30").get_text()) == 0:
            estado = edicion = True  # Si todos están vacios
        else:
            estado = False

            if len(self.obj("txt_29").get_text()) == 0 or len(self.obj("txt_29_2").get_text()) == 0 \
            or len(self.obj("txt_30").get_text()) == 0 or self.idTipoDocBanco == -1:
                edicion = False
            else:
                edicion = Op.comprobar_numero(int, self.obj("txt_29"), "Cód. de Banco", self.obj("barraestado"))

        self.estadoedicion_pestanas(edicion, 3)
        self.banco_guardado = estado


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)

    col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Cód. Tipo Doc.", celda0, 1, True, 75, 150)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Tipo de Documento", celda1, 2, True, 150)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Nro. Documento", celda0, 3, True, 100, 150)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Razón Social", celda1, 4, True, 200)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Fecha de Nacimiento", celda1, 5, True, 100, 150)
    col5.set_sort_column_id(25)  # Para ordenarse usa la fila 25
    col6 = Op.columnas("Edad", celda0, 6, True, 50, 75)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Dirección", celda1, 7, True, 200)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Teléfono", celda0, 8, True, 125)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("E-mail", celda1, 9, True, 200)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Cód. Nacionalidad", celda0, 10, True, 75, 150)
    col10.set_sort_column_id(10)
    col11 = Op.columnas("Nacionalidad", celda1, 11, True, 125)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Cód. Est. Civil", celda0, 12, True, 75, 150)
    col12.set_sort_column_id(12)
    col13 = Op.columnas("Estado Civil", celda1, 13, True, 125)
    col13.set_sort_column_id(13)
    col14 = Op.columnas("Cód. Género", celda0, 14, True, 75, 150)
    col14.set_sort_column_id(14)
    col15 = Op.columnas("Género", celda1, 15, True, 125)
    col15.set_sort_column_id(15)
    col16 = Op.columnas("Cód. Ocu.", celda0, 16, True, 75, 150)
    col16.set_sort_column_id(16)
    col17 = Op.columnas("Ocupación", celda1, 17, True, 125)
    col17.set_sort_column_id(17)
    col18 = Op.columnas("Cód. Tipo Emp.", celda0, 18, True, 75, 150)
    col18.set_sort_column_id(18)
    col19 = Op.columnas("Tipo de Empresa", celda1, 19, True, 125)
    col19.set_sort_column_id(19)
    col20 = Op.columnas("Página Web", celda1, 20, True, 200)
    col20.set_sort_column_id(20)
    col21 = Op.columnas("Cód. Rol", celda0, 21, True, 75, 150)
    col21.set_sort_column_id(21)
    col22 = Op.columnas("Rol", celda1, 22, True, 125)
    col22.set_sort_column_id(22)
    col23 = Op.columnas("Observaciones", celda1, 23, True, 200)
    col23.set_sort_column_id(23)
    col24 = Op.columna_active("Activo", 24)
    col24.set_sort_column_id(24)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11,
    col12, col13, col14, col15, col16, col17, col18, col19, col20, col21, col22, col23]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col24)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(4)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 4)

    lista = ListStore(int, str, str, str, str, str, str, str, str, str, int, str,
    str, str, str, str, str, str, str, str, str, int, str, str, bool, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar == "FechaNacimiento":
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    if self.obj("rad_act").get_active() or self.obj("rad_ina").get_active():
        activo = "1" if self.obj("rad_act").get_active() else "0"
        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += "Activo = " + activo

    condicion = ""
    if len(self.condicion) > 0:
        condicion = " WHERE " + self.condicion if len(opcion) == 0 \
        else " AND " + self.condicion

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", idTipoDocumento, TipoDocumento, " +
        "NroDocumento, RazonSocial, FechaNacimiento, Edad, DireccionPrincipal, " +
        "TelefonoPrincipal, EmailPrincipal, idNacionalidad, Nacionalidad, " +
        "idEstadoCivil, EstadoCivil, idGenero, Genero, idOcupacion, Ocupacion, " +
        "idTipoEmpresa, TipoEmpresa, PaginaWeb, idRolPersona, RolPersona, " +
        "Observaciones, Activo, Empresa", self.tabla + "_s",
        opcion + condicion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        fecha = Cal.mysql_fecha(datos[i][5]) if datos[i][5] is not None else ""
        edad = str(datos[i][6]) if datos[i][6] is not None else ""
        codestado = str(datos[i][12]) if datos[i][12] is not None else ""
        codgenero = str(datos[i][14]) if datos[i][14] is not None else ""
        codocupa = str(datos[i][16]) if datos[i][16] is not None else ""
        codempresa = str(datos[i][18]) if datos[i][18] is not None else ""

        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], fecha, edad, datos[i][7], datos[i][8], datos[i][9],
            datos[i][10], datos[i][11], codestado, datos[i][13], codgenero, datos[i][15],
            codocupa, datos[i][17], codempresa, datos[i][19], datos[i][20],
            datos[i][21], datos[i][22], datos[i][23], datos[i][24], str(datos[i][5])])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Código", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "Cód. Tipo Documento", "idTipoDocumento"
    elif idcolumna == 2:
        col, self.campo_buscar = "Tipo de Documento", "TipoDocumento"
    elif idcolumna == 3:
        col, self.campo_buscar = "Nro. Documento", "NroDocumento"
    elif idcolumna == 4:
        col, self.campo_buscar = "Razón Social", "RazonSocial"
    elif idcolumna == 25:
        col, self.campo_buscar = "Fecha de Nacimiento, desde", "FechaNacimiento"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 6:
        col = self.campo_buscar = "Edad"
    elif idcolumna == 7:
        col, self.campo_buscar = "Dirección Principal", "DireccionPrincipal"
    elif idcolumna == 8:
        col, self.campo_buscar = "Teléfono Principal", "TelefonoPrincipal"
    elif idcolumna == 9:
        col, self.campo_buscar = "E-mail Principal", "EmailPrincipal"
    elif idcolumna == 10:
        col, self.campo_buscar = "Cód. Nacionalidad", "idNacionalidad"
    elif idcolumna == 11:
        col = self.campo_buscar = "Nacionalidad"
    elif idcolumna == 12:
        col, self.campo_buscar = "Cód. Estado Civil", "idEstadoCivil"
    elif idcolumna == 13:
        col, self.campo_buscar = "Estado Civil", "EstadoCivil"
    elif idcolumna == 14:
        col, self.campo_buscar = "Cód. Género", "idGenero"
    elif idcolumna == 15:
        col, self.campo_buscar = "Género", "Genero"
    elif idcolumna == 16:
        col, self.campo_buscar = "Cód. Ocupación", "idOcupacion"
    elif idcolumna == 17:
        col, self.campo_buscar = "Ocupación", "Ocupacion"
    elif idcolumna == 18:
        col, self.campo_buscar = "Cód. Tipo Empresa", "idTipoEmpresa"
    elif idcolumna == 19:
        col, self.campo_buscar = "Tipo de Empresa", "TipoEmpresa"
    elif idcolumna == 20:
        col, self.campo_buscar = "Página Web", "PaginaWeb"
    elif idcolumna == 21:
        col, self.campo_buscar = "Cód. Rol", "idRolPersona"
    elif idcolumna == 22:
        col, self.campo_buscar = "Rol", "RolPersona"
    elif idcolumna == 23:
        col = self.campo_buscar = "Observaciones"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 1)
    valor2 = seleccion.get_value(iterador, 3)

    valor3 = seleccion.get_value(iterador, 4)
    valor3 = "" if valor3 is None else valor3

    eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
        "Código: " + valor0 + "\nNro. " + valor1 + ": " + valor2 + "\nRazón Social: " + valor3)

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
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][3], body_ce), Par(datos[i][4], body_iz)])

    listado.listado(self.titulo, lista, [100, 100, 200], A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = seleccion.get_value(iterador, 1)
        valor2 = seleccion.get_value(iterador, 3)  # Nro. Documento
        valor3 = seleccion.get_value(iterador, 4)  # Razón Social
        valor4 = seleccion.get_value(iterador, 7)
        valor5 = seleccion.get_value(iterador, 8)

        valor4 = "" if valor4 is None else valor4
        valor5 = "" if valor5 is None else valor5

        self.origen.txt_cod_per.set_text(valor0)
        self.origen.txt_rzn_scl.set_text(valor3)

        try:  # Combo que indica el Tipo de Documento de Identidad
            model, i = self.origen.cmb_tip_doc.get_model(), 0
            while model[i][0] != valor1: i += 1
            self.origen.cmb_tip_doc.set_active(i)
        except:
            pass

        try:  # Número de Documento de Identidad
            self.origen.txt_nro_doc.set_text(valor2)
        except:
            pass

        try:  # Dirección Principal
            self.origen.txt_dir_per.set_text(valor4)
        except:
            pass

        try:  # Telefono Principal
            self.origen.txt_tel_per.set_text(valor5)
        except:
            pass

        try:  # Se usa en Movimientos de Empleados
            self.origen.idPersona = valor0
        except:
            pass

        self.on_btn_salir_clicked(0)
    except:
        pass
