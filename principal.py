#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import main_quit
from clases.operaciones import archivo
from clases.operaciones import conectar
from acceso import acceso


class principal:

    def __init__(self):
        self.principal = archivo("principal")
        vent_principal = self.principal.get_object("ventana")
        vent_principal.set_default_size(950, 600)
        vent_principal.set_position(1)
        vent_principal.set_title("Sistema de Gestión de Recursos Humanos, Compras y Ventas")
        vent_principal.set_sensitive(False)
        vent_principal.show()

        self.principal.connect_signals({
            'on_sist_usuarios_activate': self.on_sist_usuarios_activate,
            'on_sist_cambiar_activate': self.on_sist_cambiar_activate,
            'on_sist_salir_activate': self.on_sist_salir_activate,

            'on_rrhh_empresas_activate': self.on_rrhh_empresas_activate,
            'on_rrhh_empleados_activate': self.on_rrhh_empleados_activate,
            'on_rrhh_beneficiarios_activate': self.on_rrhh_beneficiarios_activate,
            'on_rrhh_contratos_activate': self.on_rrhh_contratos_activate,
            'on_rrhh_vendedores_activate': self.on_rrhh_vendedores_activate,

            'on_rrhh_entradas_activate': self.on_rrhh_entradas_activate,
            'on_rrhh_asistencias_activate': self.on_rrhh_asistencias_activate,
            'on_rrhh_permisos_activate': self.on_rrhh_permisos_activate,
            'on_rrhh_sanciones_activate': self.on_rrhh_sanciones_activate,
            'on_rrhh_judiciales_activate': self.on_rrhh_judiciales_activate,
            'on_rrhh_reposos_activate': self.on_rrhh_reposos_activate,
            'on_rrhh_vacaciones_activate': self.on_rrhh_vacaciones_activate,
            'on_rrhh_preavisos_activate': self.on_rrhh_preavisos_activate,
            'on_rrhh_salidas_activate': self.on_rrhh_salidas_activate,

            'on_rrhh_aguinaldos_activate': self.on_rrhh_aguinaldos_activate,
            'on_rrhh_anticipos_activate': self.on_rrhh_anticipos_activate,
            'on_rrhh_descuentos_activate': self.on_rrhh_descuentos_activate,
            'on_rrhh_gratificaciones_activate': self.on_rrhh_gratificaciones_activate,
            'on_rrhh_horas_extras_activate': self.on_rrhh_horas_extras_activate,
            'on_rrhh_pagos_activate': self.on_rrhh_pagos_activate,

            'on_comp_ajustes_activate': self.on_comp_ajustes_activate,
            'on_comp_pedidos_activate': self.on_comp_pedidos_activate,
            'on_comp_ordenes_activate': self.on_comp_ordenes_activate,
            'on_comp_facturas_activate': self.on_comp_facturas_activate,
            'on_comp_creditos_activate': self.on_comp_creditos_activate,
            'on_comp_debitos_activate': self.on_comp_debitos_activate,

            'on_vent_aperturas_activate': self.on_vent_aperturas_activate,
            'on_vent_pedidos_activate': self.on_vent_pedidos_activate,
            'on_vent_facturas_activate': self.on_vent_facturas_activate,
            'on_vent_remisiones_activate': self.on_vent_remisiones_activate,
            'on_vent_creditos_activate': self.on_vent_creditos_activate,
            'on_vent_debitos_activate': self.on_vent_debitos_activate,
            'on_vent_recibos_activate': self.on_vent_recibos_activate,
            'on_vent_cheques_activate': self.on_vent_cheques_activate,
            'on_vent_tarjetas_activate': self.on_vent_tarjetas_activate,
            'on_vent_arqueos_activate': self.on_vent_arqueos_activate,
            'on_vent_cierres_activate': self.on_vent_cierres_activate,

            'on_reg_categorias_activate': self.on_reg_categorias_activate,
            'on_reg_depositos_activate': self.on_reg_depositos_activate,
            'on_reg_impuestos_activate': self.on_reg_impuestos_activate,
            'on_reg_marca_items_activate': self.on_reg_marca_items_activate,
            'on_reg_motivo_ajustes_activate': self.on_reg_motivo_ajustes_activate,
            'on_reg_presentaciones_activate': self.on_reg_presentaciones_activate,
            'on_reg_unidad_medidas_activate': self.on_reg_unidad_medidas_activate,
            'on_reg_items_activate': self.on_reg_items_activate,

            'on_reg_estados_civiles_activate': self.on_reg_estados_civiles_activate,
            'on_reg_generos_activate': self.on_reg_generos_activate,
            'on_reg_ocupaciones_activate': self.on_reg_ocupaciones_activate,
            'on_reg_rol_personas_activate': self.on_reg_rol_personas_activate,
            'on_reg_tipo_clientes_activate': self.on_reg_tipo_clientes_activate,
            'on_reg_tipo_documentos_activate': self.on_reg_tipo_documentos_activate,
            'on_reg_tipo_empresas_activate': self.on_reg_tipo_empresas_activate,
            'on_reg_zona_ventas_activate': self.on_reg_zona_ventas_activate,

            'on_reg_barrios_activate': self.on_reg_barrios_activate,
            'on_reg_calles_activate': self.on_reg_calles_activate,
            'on_reg_ciudades_activate': self.on_reg_ciudades_activate,
            'on_reg_departamentos_activate': self.on_reg_departamentos_activate,
            'on_reg_paises_activate': self.on_reg_paises_activate,
            'on_reg_tipo_calles_activate': self.on_reg_tipo_calles_activate,
            'on_reg_tipo_medios_activate': self.on_reg_tipo_medios_activate,

            'on_reg_personas_activate': self.on_reg_personas_activate,

            'on_reg_salarios_minimos_activate': self.on_reg_salarios_minimos_activate,
            'on_reg_actividades_activate': self.on_reg_actividades_activate,
            'on_reg_cargos_activate': self.on_reg_cargos_activate,
            'on_reg_formas_pago_activate': self.on_reg_formas_pago_activate,
            'on_reg_periodos_pago_activate': self.on_reg_periodos_pago_activate,
            'on_reg_tipo_contratos_activate': self.on_reg_tipo_contratos_activate,
            'on_reg_tipo_parentescos_activate': self.on_reg_tipo_parentescos_activate,
            'on_reg_tipo_salarios_activate': self.on_reg_tipo_salarios_activate,
            'on_reg_tipo_seguros_activate': self.on_reg_tipo_seguros_activate,
            'on_reg_turnos_trabajo_activate': self.on_reg_turnos_trabajo_activate,

            'on_reg_dias_no_habiles_activate': self.on_reg_dias_no_habiles_activate,
            'on_reg_concepto_salarios_activate': self.on_reg_concepto_salarios_activate,
            'on_reg_motivo_descuentos_activate': self.on_reg_motivo_descuentos_activate,
            'on_reg_motivo_gratificaciones_activate': self.on_reg_motivo_gratificaciones_activate,
            'on_reg_motivo_permisos_activate': self.on_reg_motivo_permisos_activate,
            'on_reg_motivo_salidas_activate': self.on_reg_motivo_salidas_activate,
            'on_reg_motivo_sanciones_activate': self.on_reg_motivo_sanciones_activate,
            'on_reg_tipo_juzgados_activate': self.on_reg_tipo_juzgados_activate,
            'on_reg_turnos_juzgado_activate': self.on_reg_turnos_juzgado_activate,

            'on_reg_establecimientos_activate': self.on_reg_establecimientos_activate,
            'on_reg_cajas_activate': self.on_reg_cajas_activate,
            'on_reg_timbrados_activate': self.on_reg_timbrados_activate,
            'on_reg_denominaciones_activate': self.on_reg_denominaciones_activate,
            'on_reg_tipo_denominaciones_activate': self.on_reg_tipo_denominaciones_activate,
            'on_reg_tipo_comerciales_activate': self.on_reg_tipo_comerciales_activate,
            'on_reg_tipo_valores_activate': self.on_reg_tipo_valores_activate,

            'on_reg_monedas_activate': self.on_reg_monedas_activate,
            'on_reg_cotizaciones_activate': self.on_reg_cotizaciones_activate,
            'on_reg_concepto_recibos_activate': self.on_reg_concepto_recibos_activate,
            'on_reg_marca_tarjetas_activate': self.on_reg_marca_tarjetas_activate,
            'on_reg_tipo_cheques_activate': self.on_reg_tipo_cheques_activate,
            'on_reg_tipo_facturas_activate': self.on_reg_tipo_facturas_activate,
            'on_reg_tipo_tarjetas_activate': self.on_reg_tipo_tarjetas_activate,

            'on_reg_marca_vehiculos_activate': self.on_reg_marca_vehiculos_activate,
            'on_reg_motivo_traslados_activate': self.on_reg_motivo_traslados_activate,
            'on_reg_vehiculos_activate': self.on_reg_vehiculos_activate,

            'on_info_rrhh_asistencias_activate': self.on_info_rrhh_asistencias_activate,

            'on_info_comp_facturas_activate': self.on_info_comp_facturas_activate,
            'on_info_comp_creditos_activate': self.on_info_comp_creditos_activate,
            'on_info_comp_debitos_activate': self.on_info_comp_debitos_activate,

            'on_info_vent_facturas_activate': self.on_info_vent_facturas_activate,
            'on_info_vent_creditos_activate': self.on_info_vent_creditos_activate,
            'on_info_vent_debitos_activate': self.on_info_vent_debitos_activate,

            'on_help_manual_activate': self.on_help_manual_activate,
            'on_help_acerca_activate': self.on_help_acerca_activate
        })

        self.estab = self.caja = self.numero = None
        # Ventana de acceso de Usuarios
        acceso(self.verificar_permisos)

########################################################################

    def on_sist_usuarios_activate(self, objeto):
        from usuarios import usuarios
        usuarios(self.datos_conexion)

    def on_sist_cambiar_activate(self, objeto):
        self.principal.get_object("ventana").set_sensitive(False)
        # Ventana de acceso de Usuarios
        acceso(self.verificar_permisos)

    def on_sist_salir_activate(self, objeto):
        main_quit()

########################################################################

    def on_rrhh_empresas_activate(self, objeto):
        from clases.llamadas import empresas
        empresas(self.datos_conexion)

    def on_rrhh_empleados_activate(self, objeto):
        from clases.llamadas import empleados
        empleados(self.datos_conexion)

    def on_rrhh_beneficiarios_activate(self, objeto):
        from clases.llamadas import beneficiarios
        beneficiarios(self.datos_conexion)

    def on_rrhh_contratos_activate(self, objeto):
        from clases.llamadas import contratos
        contratos(self.datos_conexion)

    def on_rrhh_vendedores_activate(self, objeto):
        from clases.llamadas import vendedores
        vendedores(self.datos_conexion)

########################################################################

    def on_rrhh_entradas_activate(self, objeto):
        from clases.llamadas import entradas
        entradas(self.datos_conexion)

    def on_rrhh_asistencias_activate(self, objeto):
        from humanos.asistencias import asistencias
        asistencias(self.datos_conexion)

    def on_rrhh_permisos_activate(self, objeto):
        from clases.llamadas import permisos
        permisos(self.datos_conexion)

    def on_rrhh_sanciones_activate(self, objeto):
        from clases.llamadas import sanciones
        sanciones(self.datos_conexion)

    def on_rrhh_judiciales_activate(self, objeto):
        from clases.llamadas import judiciales
        judiciales(self.datos_conexion)

    def on_rrhh_reposos_activate(self, objeto):
        from clases.llamadas import reposos
        reposos(self.datos_conexion)

    def on_rrhh_vacaciones_activate(self, objeto):
        from clases.llamadas import vacaciones
        vacaciones(self.datos_conexion)

    def on_rrhh_preavisos_activate(self, objeto):
        from clases.llamadas import preavisos
        preavisos(self.datos_conexion)

    def on_rrhh_salidas_activate(self, objeto):
        from clases.llamadas import salidas
        salidas(self.datos_conexion)

########################################################################

    def on_rrhh_aguinaldos_activate(self, objeto):
        from clases.llamadas import aguinaldos
        aguinaldos(self.datos_conexion)

    def on_rrhh_anticipos_activate(self, objeto):
        from clases.llamadas import anticipos
        anticipos(self.datos_conexion)

    def on_rrhh_descuentos_activate(self, objeto):
        from clases.llamadas import descuentos
        descuentos(self.datos_conexion)

    def on_rrhh_gratificaciones_activate(self, objeto):
        from clases.llamadas import gratificaciones
        gratificaciones(self.datos_conexion)

    def on_rrhh_horas_extras_activate(self, objeto):
        from clases.llamadas import horaextraordinarias
        horaextraordinarias(self.datos_conexion)

    def on_rrhh_pagos_activate(self, objeto):
        from clases.llamadas import comprobantepagos
        comprobantepagos(self.datos_conexion)

########################################################################

    def on_comp_ajustes_activate(self, objeto):
        print("Ajustes de Inventario")

    def on_comp_pedidos_activate(self, objeto):
        from clases.llamadas import pedidocompras
        pedidocompras(self.datos_conexion)

    def on_comp_ordenes_activate(self, objeto):
        from clases.llamadas import ordencompras
        ordencompras(self.datos_conexion)

    def on_comp_facturas_activate(self, objeto):
        from clases.llamadas import facturacompras
        facturacompras(self.datos_conexion)

    def on_comp_creditos_activate(self, objeto):
        from clases.llamadas import notacreditocompras
        notacreditocompras(self.datos_conexion)

    def on_comp_debitos_activate(self, objeto):
        from clases.llamadas import notadebitocompras
        notadebitocompras(self.datos_conexion)

########################################################################

    def on_vent_aperturas_activate(self, objeto):
        from ventas.caja_movimientos import cajaaperturas
        cajaaperturas(self.datos_conexion, self)

    def on_vent_pedidos_activate(self, objeto):
        from ventas.pedidos import pedidos
        pedidos(self.datos_conexion, "pedidoventas")

    def on_vent_facturas_activate(self, objeto):
        from ventas.facturas import facturas
        facturas(self.datos_conexion, "facturaventas", self.estab, self.caja, self.numero)

    def on_vent_remisiones_activate(self, objeto):
        print("Notas de Remision")

    def on_vent_creditos_activate(self, objeto):
        from ventas.notas_credito_debito import notas_credito_debito
        notas_credito_debito(self.datos_conexion, "Crédito", "notacreditoventas", self.estab, self.caja, self.numero)

    def on_vent_debitos_activate(self, objeto):
        from ventas.notas_credito_debito import notas_credito_debito
        notas_credito_debito(self.datos_conexion, "Débito", "notadebitoventas", self.estab, self.caja, self.numero)

    def on_vent_recibos_activate(self, objeto):
        print("Recibos de Dinero")

    def on_vent_cheques_activate(self, objeto):
        from clases.llamadas import chequeterceros
        chequeterceros(self.datos_conexion)

    def on_vent_tarjetas_activate(self, objeto):
        from clases.llamadas import tarjetas
        tarjetas(self.datos_conexion)

    def on_vent_arqueos_activate(self, objeto):
        print("Arqueos de Caja")

    def on_vent_cierres_activate(self, objeto):
        from ventas.caja_movimientos import cajacierres
        cajacierres(self.datos_conexion, self)

########################################################################

    def on_reg_categorias_activate(self, objeto):
        from clases.llamadas import categorias
        categorias(self.datos_conexion)

    def on_reg_depositos_activate(self, objeto):
        from clases.llamadas import depositos
        depositos(self.datos_conexion)

    def on_reg_impuestos_activate(self, objeto):
        from clases.llamadas import impuestos
        impuestos(self.datos_conexion)

    def on_reg_marca_items_activate(self, objeto):
        from clases.llamadas import marcaitems
        marcaitems(self.datos_conexion)

    def on_reg_motivo_ajustes_activate(self, objeto):
        from clases.llamadas import motivoajustes
        motivoajustes(self.datos_conexion)

    def on_reg_presentaciones_activate(self, objeto):
        from clases.llamadas import presentaciones
        presentaciones(self.datos_conexion)

    def on_reg_unidad_medidas_activate(self, objeto):
        from clases.llamadas import unidadmedidas
        unidadmedidas(self.datos_conexion)

    def on_reg_items_activate(self, objeto):
        from clases.llamadas import items
        items(self.datos_conexion)

########################################################################

    def on_reg_estados_civiles_activate(self, objeto):
        from clases.llamadas import estadosciviles
        estadosciviles(self.datos_conexion)

    def on_reg_generos_activate(self, objeto):
        from clases.llamadas import generos
        generos(self.datos_conexion)

    def on_reg_ocupaciones_activate(self, objeto):
        from clases.llamadas import ocupaciones
        ocupaciones(self.datos_conexion)

    def on_reg_rol_personas_activate(self, objeto):
        from clases.llamadas import rolpersonas
        rolpersonas(self.datos_conexion)

    def on_reg_tipo_clientes_activate(self, objeto):
        from clases.llamadas import tipoclientes
        tipoclientes(self.datos_conexion)

    def on_reg_tipo_documentos_activate(self, objeto):
        from clases.llamadas import tipodocumentos
        tipodocumentos(self.datos_conexion)

    def on_reg_tipo_empresas_activate(self, objeto):
        from clases.llamadas import tipoempresas
        tipoempresas(self.datos_conexion)

    def on_reg_zona_ventas_activate(self, objeto):
        from clases.llamadas import zonaventas
        zonaventas(self.datos_conexion)

########################################################################

    def on_reg_barrios_activate(self, objeto):
        from clases.llamadas import barrios
        barrios(self.datos_conexion)

    def on_reg_calles_activate(self, objeto):
        from clases.llamadas import calles
        calles(self.datos_conexion)

    def on_reg_ciudades_activate(self, objeto):
        from clases.llamadas import ciudades
        ciudades(self.datos_conexion)

    def on_reg_departamentos_activate(self, objeto):
        from clases.llamadas import departamentos
        departamentos(self.datos_conexion)

    def on_reg_paises_activate(self, objeto):
        from clases.llamadas import paises
        paises(self.datos_conexion)

    def on_reg_tipo_calles_activate(self, objeto):
        from clases.llamadas import tipocalles
        tipocalles(self.datos_conexion)

    def on_reg_tipo_medios_activate(self, objeto):
        from clases.llamadas import tipomediocontactos
        tipomediocontactos(self.datos_conexion)

########################################################################

    def on_reg_personas_activate(self, objeto):
        from clases.llamadas import personas
        personas(self.datos_conexion)

########################################################################

    def on_reg_salarios_minimos_activate(self, objeto):
        print("Salarios Minimos")

    def on_reg_actividades_activate(self, objeto):
        from clases.llamadas import actividadeseconomicas
        actividadeseconomicas(self.datos_conexion)

    def on_reg_cargos_activate(self, objeto):
        from clases.llamadas import cargos
        cargos(self.datos_conexion)

    def on_reg_formas_pago_activate(self, objeto):
        from clases.llamadas import formapagos
        formapagos(self.datos_conexion)

    def on_reg_periodos_pago_activate(self, objeto):
        from clases.llamadas import periodopagos
        periodopagos(self.datos_conexion)

    def on_reg_tipo_contratos_activate(self, objeto):
        from clases.llamadas import tipocontratos
        tipocontratos(self.datos_conexion)

    def on_reg_tipo_parentescos_activate(self, objeto):
        from clases.llamadas import tipoparentescos
        tipoparentescos(self.datos_conexion)

    def on_reg_tipo_salarios_activate(self, objeto):
        from clases.llamadas import tiposalarios
        tiposalarios(self.datos_conexion)

    def on_reg_tipo_seguros_activate(self, objeto):
        from clases.llamadas import tiposeguros
        tiposeguros(self.datos_conexion)

    def on_reg_turnos_trabajo_activate(self, objeto):
        print("Turnos de Trabajo")

########################################################################

    def on_reg_dias_no_habiles_activate(self, objeto):
        print("Dias No Habiles")

    def on_reg_concepto_salarios_activate(self, objeto):
        from clases.llamadas import conceptopagos
        conceptopagos(self.datos_conexion)

    def on_reg_motivo_descuentos_activate(self, objeto):
        from clases.llamadas import motivodescuentos
        motivodescuentos(self.datos_conexion)

    def on_reg_motivo_gratificaciones_activate(self, objeto):
        from clases.llamadas import motivogratificaciones
        motivogratificaciones(self.datos_conexion)

    def on_reg_motivo_permisos_activate(self, objeto):
        from clases.llamadas import motivopermisos
        motivopermisos(self.datos_conexion)

    def on_reg_motivo_salidas_activate(self, objeto):
        from clases.llamadas import motivosalidas
        motivosalidas(self.datos_conexion)

    def on_reg_motivo_sanciones_activate(self, objeto):
        from clases.llamadas import motivosanciones
        motivosanciones(self.datos_conexion)

    def on_reg_tipo_juzgados_activate(self, objeto):
        from clases.llamadas import tipojuzgados
        tipojuzgados(self.datos_conexion)

    def on_reg_turnos_juzgado_activate(self, objeto):
        from clases.llamadas import turnojuzgados
        turnojuzgados(self.datos_conexion)

########################################################################

    def on_reg_establecimientos_activate(self, objeto):
        from clases.llamadas import establecimientos
        establecimientos(self.datos_conexion)

    def on_reg_cajas_activate(self, objeto):
        from clases.llamadas import puntoexpediciones
        puntoexpediciones(self.datos_conexion)

    def on_reg_timbrados_activate(self, objeto):
        from clases.llamadas import timbrados
        timbrados(self.datos_conexion)

    def on_reg_denominaciones_activate(self, objeto):
        from clases.llamadas import denominaciones
        denominaciones(self.datos_conexion)

    def on_reg_tipo_denominaciones_activate(self, objeto):
        from clases.llamadas import tipodenominaciones
        tipodenominaciones(self.datos_conexion)

    def on_reg_tipo_comerciales_activate(self, objeto):
        from clases.llamadas import tipodocumentocomerciales
        tipodocumentocomerciales(self.datos_conexion)

    def on_reg_tipo_valores_activate(self, objeto):
        from clases.llamadas import tipovalores
        tipovalores(self.datos_conexion)

########################################################################

    def on_reg_monedas_activate(self, objeto):
        from clases.llamadas import monedas
        monedas(self.datos_conexion)

    def on_reg_cotizaciones_activate(self, objeto):
        from clases.llamadas import cotizaciones
        cotizaciones(self.datos_conexion)

    def on_reg_concepto_recibos_activate(self, objeto):
        from clases.llamadas import conceptorecibos
        conceptorecibos(self.datos_conexion)

    def on_reg_marca_tarjetas_activate(self, objeto):
        from clases.llamadas import marcatarjetas
        marcatarjetas(self.datos_conexion)

    def on_reg_tipo_cheques_activate(self, objeto):
        from clases.llamadas import tipocheques
        tipocheques(self.datos_conexion)

    def on_reg_tipo_facturas_activate(self, objeto):
        from clases.llamadas import tipofacturas
        tipofacturas(self.datos_conexion)

    def on_reg_tipo_tarjetas_activate(self, objeto):
        from clases.llamadas import tipotarjetas
        tipotarjetas(self.datos_conexion)

########################################################################

    def on_reg_marca_vehiculos_activate(self, objeto):
        from clases.llamadas import marcavehiculos
        marcavehiculos(self.datos_conexion)

    def on_reg_motivo_traslados_activate(self, objeto):
        from clases.llamadas import motivotraslados
        motivotraslados(self.datos_conexion)

    def on_reg_vehiculos_activate(self, objeto):
        from clases.llamadas import vehiculos
        vehiculos(self.datos_conexion)

########################################################################

    def on_info_rrhh_asistencias_activate(self, objeto):
        from informes.rrhh_asistencias import informe_asistencias
        informe_asistencias(self.datos_conexion)

########################################################################

    def on_info_comp_facturas_activate(self, objeto):
        from informes.compra_facturas import informe_compra_facturas
        informe_compra_facturas(self.datos_conexion)

    def on_info_comp_creditos_activate(self, objeto):
        from informes.compra_nota_creditos import informe_compra_nota_creditos
        informe_compra_nota_creditos(self.datos_conexion)

    def on_info_comp_debitos_activate(self, objeto):
        from informes.compra_nota_debitos import informe_compra_nota_debitos
        informe_compra_nota_debitos(self.datos_conexion)

########################################################################

    def on_info_vent_facturas_activate(self, objeto):
        from informes.venta_facturas import informe_venta_facturas
        informe_venta_facturas(self.datos_conexion)

    def on_info_vent_creditos_activate(self, objeto):
        from informes.venta_nota_creditos import informe_venta_nota_creditos
        informe_venta_nota_creditos(self.datos_conexion)

    def on_info_vent_debitos_activate(self, objeto):
        from informes.venta_nota_debitos import informe_venta_nota_debitos
        informe_venta_nota_debitos(self.datos_conexion)

########################################################################

    def on_help_manual_activate(self, objeto):
        from os import popen
        popen('"ayudas\\ayuda.pdf"')

    def on_help_acerca_activate(self, objeto):
        arch = archivo("acerca")
        vent = arch.get_object("aboutdialog")
        vent.set_position(1)
        vent.set_title("Acerca de ...")
        vent.set_modal(True)
        vent.run()

########################################################################

    def verificar_permisos(self, ventana_acceso, datos):
        self.datos_conexion = datos
        conexion = conectar(self.datos_conexion)
        cursor = conexion.cursor()
        self.desactiva()

        # Aqui se verifican los permisos sobre referenciales fuertes
        cursor.execute("SELECT TABLE_NAME FROM tablas_s")
        dato_tabla = cursor.fetchall()
        cant_tabla = cursor.rowcount

        for i in range(0, cant_tabla):
            tabla = dato_tabla[i][0]

            if tabla == "impuestos":
                self.principal.get_object("reg_impuestos").set_sensitive(True)
            elif tabla == "marcaitems":
                self.principal.get_object("reg_marca_items").set_sensitive(True)
            elif tabla == "motivoajustes":
                self.principal.get_object("reg_motivo_ajustes").set_sensitive(True)
            elif tabla == "presentaciones":
                self.principal.get_object("reg_presentaciones").set_sensitive(True)
            elif tabla == "unidadmedidas":
                self.principal.get_object("reg_unidad_medidas").set_sensitive(True)

            elif tabla == "estadosciviles":
                self.principal.get_object("reg_estados_civiles").set_sensitive(True)
            elif tabla == "generos":
                self.principal.get_object("reg_generos").set_sensitive(True)
            elif tabla == "ocupaciones":
                self.principal.get_object("reg_ocupaciones").set_sensitive(True)
            elif tabla == "rolpersonas":
                self.principal.get_object("reg_rol_personas").set_sensitive(True)
            elif tabla == "tipoclientes":
                self.principal.get_object("reg_tipo_clientes").set_sensitive(True)
            elif tabla == "tipodocumentos":
                self.principal.get_object("reg_tipo_documentos").set_sensitive(True)
            elif tabla == "tipoempresas":
                self.principal.get_object("reg_tipo_empresas").set_sensitive(True)
            elif tabla == "zonaventas":
                self.principal.get_object("reg_zona_ventas").set_sensitive(True)

            elif tabla == "barrios":
                self.principal.get_object("reg_barrios").set_sensitive(True)
            elif tabla == "calles":
                self.principal.get_object("reg_calles").set_sensitive(True)
            elif tabla == "paises":
                self.principal.get_object("reg_paises").set_sensitive(True)
            elif tabla == "tipocalles":
                self.principal.get_object("reg_tipo_calles").set_sensitive(True)
            elif tabla == "tipomediocontactos":
                self.principal.get_object("reg_tipo_medios").set_sensitive(True)

            elif tabla == "actividadeseconomicas":
                self.principal.get_object("reg_actividades").set_sensitive(True)
            elif tabla == "cargos":
                self.principal.get_object("reg_cargos").set_sensitive(True)
            elif tabla == "formapagos":
                self.principal.get_object("reg_formas_pago").set_sensitive(True)
            elif tabla == "periodopagos":
                self.principal.get_object("reg_periodos_pago").set_sensitive(True)
            elif tabla == "tipocontratos":
                self.principal.get_object("reg_tipo_contratos").set_sensitive(True)
            elif tabla == "tipoparentescos":
                self.principal.get_object("reg_tipo_parentescos").set_sensitive(True)
            elif tabla == "tiposalarios":
                self.principal.get_object("reg_tipo_salarios").set_sensitive(True)
            elif tabla == "tiposeguros":
                self.principal.get_object("reg_tipo_seguros").set_sensitive(True)

            elif tabla == "conceptopagos":
                self.principal.get_object("reg_concepto_salarios").set_sensitive(True)
            elif tabla == "motivodescuentos":
                self.principal.get_object("reg_motivo_descuentos").set_sensitive(True)
            elif tabla == "motivogratificaciones":
                self.principal.get_object("reg_motivo_gratificaciones").set_sensitive(True)
            elif tabla == "motivopermisos":
                self.principal.get_object("reg_motivo_permisos").set_sensitive(True)
            elif tabla == "motivosalidas":
                self.principal.get_object("reg_motivo_salidas").set_sensitive(True)
            elif tabla == "motivosanciones":
                self.principal.get_object("reg_motivo_sanciones").set_sensitive(True)
            elif tabla == "tipojuzgados":
                self.principal.get_object("reg_tipo_juzgados").set_sensitive(True)
            elif tabla == "turnojuzgados":
                self.principal.get_object("reg_turnos_juzgado").set_sensitive(True)

            elif tabla == "tipodenominaciones":
                self.principal.get_object("reg_tipo_denominaciones").set_sensitive(True)
            elif tabla == "tipodocumentocomerciales":
                self.principal.get_object("reg_tipo_comerciales").set_sensitive(True)
            elif tabla == "tipovalores":
                self.principal.get_object("reg_tipo_valores").set_sensitive(True)

            elif tabla == "conceptorecibos":
                self.principal.get_object("reg_concepto_recibos").set_sensitive(True)
            elif tabla == "marcatarjetas":
                self.principal.get_object("reg_marca_tarjetas").set_sensitive(True)
            elif tabla == "tipocheques":
                self.principal.get_object("reg_tipo_cheques").set_sensitive(True)
            elif tabla == "tipofacturas":
                self.principal.get_object("reg_tipo_facturas").set_sensitive(True)
            elif tabla == "tipotarjetas":
                self.principal.get_object("reg_tipo_tarjetas").set_sensitive(True)

            elif tabla == "marcavehiculos":
                self.principal.get_object("reg_marca_vehiculos").set_sensitive(True)
            elif tabla == "motivotraslados":
                self.principal.get_object("reg_motivo_traslados").set_sensitive(True)

        # Aqui se verifican los permisos en base a vistas
        cursor.execute("SELECT TABLE_NAME FROM vistas_s")
        dato_vista = cursor.fetchall()
        cant_vista = cursor.rowcount

        for i in range(0, cant_vista):
            vista = dato_vista[i][0]

            if vista == "usuarios_s":
                self.principal.get_object("sist_usuarios").set_sensitive(True)

            elif vista == "empresas_s":
                self.principal.get_object("rrhh_empresas").set_sensitive(True)
            elif vista == "beneficiarios_s":
                self.principal.get_object("rrhh_beneficiarios").set_sensitive(True)
            elif vista == "contratos_s":
                self.principal.get_object("rrhh_contratos").set_sensitive(True)
            elif vista == "vendedores_s":
                self.principal.get_object("rrhh_vendedores").set_sensitive(True)

            elif vista == "entradas_s":
                self.principal.get_object("rrhh_entradas").set_sensitive(True)
            elif vista == "permisos_s":
                self.principal.get_object("rrhh_permisos").set_sensitive(True)
            elif vista == "sanciones_s":
                self.principal.get_object("rrhh_sanciones").set_sensitive(True)
            elif vista == "judiciales_s":
                self.principal.get_object("rrhh_judiciales").set_sensitive(True)
            elif vista == "reposos_s":
                self.principal.get_object("rrhh_reposos").set_sensitive(True)
            elif vista == "vacaciones_s":
                self.principal.get_object("rrhh_vacaciones").set_sensitive(True)
            elif vista == "preavisos_s":
                self.principal.get_object("rrhh_preavisos").set_sensitive(True)
            elif vista == "salidas_s":
                self.principal.get_object("rrhh_salidas").set_sensitive(True)

            elif vista == "aguinaldos_s":
                self.principal.get_object("rrhh_aguinaldos").set_sensitive(True)
            elif vista == "anticipos_s":
                self.principal.get_object("rrhh_anticipos").set_sensitive(True)
            elif vista == "descuentos_s":
                self.principal.get_object("rrhh_descuentos").set_sensitive(True)
            elif vista == "gratificaciones_s":
                self.principal.get_object("rrhh_gratificaciones").set_sensitive(True)
            elif vista == "horaextraordinarias_s":
                self.principal.get_object("rrhh_horas_extras").set_sensitive(True)
            elif vista == "comprobantepagos_s":
                self.principal.get_object("rrhh_pagos").set_sensitive(True)

            elif vista == "pedidocompras_s":
                self.principal.get_object("comp_pedidos").set_sensitive(True)
            elif vista == "ordencompras_s":
                self.principal.get_object("comp_ordenes").set_sensitive(True)
            elif vista == "facturacompras_s":
                self.principal.get_object("comp_facturas").set_sensitive(True)
                self.principal.get_object("info_comp_facturas").set_sensitive(True)
            elif vista == "notacreditocompras_s":
                self.principal.get_object("comp_creditos").set_sensitive(True)
                self.principal.get_object("info_comp_creditos").set_sensitive(True)
            elif vista == "notadebitocompras_s":
                self.principal.get_object("comp_debitos").set_sensitive(True)
                self.principal.get_object("info_comp_debitos").set_sensitive(True)

            elif vista == "chequeterceros_s":
                self.principal.get_object("vent_cheques").set_sensitive(True)
            elif vista == "tarjetas_s":
                self.principal.get_object("vent_tarjetas").set_sensitive(True)

            elif vista == "categorias_s":
                self.principal.get_object("reg_categorias").set_sensitive(True)
            elif vista == "depositos_s":
                self.principal.get_object("reg_depositos").set_sensitive(True)
            elif vista == "items_s":
                self.principal.get_object("reg_items").set_sensitive(True)

            elif vista == "ciudades_s":
                self.principal.get_object("reg_ciudades").set_sensitive(True)
            elif vista == "departamentos_s":
                self.principal.get_object("reg_departamentos").set_sensitive(True)
            elif vista == "personas_s":
                self.principal.get_object("reg_personas").set_sensitive(True)
                self.principal.get_object("rrhh_empleados").set_sensitive(True)

            elif vista == "establecimientos_s":
                self.principal.get_object("reg_establecimientos").set_sensitive(True)
            elif vista == "puntoexpediciones_s":
                self.principal.get_object("reg_cajas").set_sensitive(True)
            elif vista == "denominaciones_s":
                self.principal.get_object("reg_denominaciones").set_sensitive(True)
            elif vista == "timbrados_s":
                self.principal.get_object("reg_timbrados").set_sensitive(True)

            elif vista == "monedas_s":
                self.principal.get_object("reg_monedas").set_sensitive(True)
            elif vista == "cotizaciones_s":
                self.principal.get_object("reg_cotizaciones").set_sensitive(True)
            elif vista == "vehiculos_s":
                self.principal.get_object("reg_vehiculos").set_sensitive(True)

            elif vista == "asistencias_s":
                self.principal.get_object("info_rrhh_asistencias").set_sensitive(True)

            elif vista == "facturaventas_s":
                self.principal.get_object("info_vent_facturas").set_sensitive(True)
            elif vista == "notacreditoventas_s":
                self.principal.get_object("info_vent_creditos").set_sensitive(True)
            elif vista == "notadebitoventas_s":
                self.principal.get_object("info_vent_debitos").set_sensitive(True)

        # Aqui se verifican los permisos en base a procedimientos
        cursor.execute("SELECT ROUTINE_NAME FROM procedimientos_s")
        dato_proce = cursor.fetchall()
        cant_proce = cursor.rowcount

        for i in range(0, cant_proce):
            procedimiento = dato_proce[i][0]

            if procedimiento == "ajusteinventarios_i":
                self.principal.get_object("comp_ajustes").set_sensitive(True)
            elif procedimiento == "asistencias_i":
                self.principal.get_object("rrhh_asistencias").set_sensitive(True)
            elif procedimiento == "cajaaperturas_i":
                self.principal.get_object("vent_aperturas").set_sensitive(True)
            elif procedimiento == "pedidoventas_i":
                self.principal.get_object("vent_pedidos").set_sensitive(True)

        conexion.close()  # Finaliza la conexión
        ventana_acceso.destroy()
        self.principal.get_object("ventana").set_sensitive(True)

    def verificar_permisos_caja(self, estado):
        conexion = conectar(self.datos_conexion)
        cursor = conexion.cursor()
        self.desactiva_permisos_caja()

        cursor.execute("SELECT ROUTINE_NAME FROM procedimientos_s")
        dato_proce = cursor.fetchall()
        cant_proce = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        for i in range(0, cant_proce):
            procedimiento = dato_proce[i][0]

            if procedimiento in ("facturaventas_a", "facturaventas_i"):
                self.principal.get_object("vent_facturas").set_sensitive(estado)

            elif procedimiento in ("notaremisiones_a", "notaremisiones_i"):
                self.principal.get_object("vent_remisiones").set_sensitive(estado)

            elif procedimiento in ("notacreditoventas_a", "notacreditoventas_i"):
                self.principal.get_object("vent_creditos").set_sensitive(estado)

            elif procedimiento in ("notadebitoventas_a", "notadebitoventas_i"):
                self.principal.get_object("vent_debitos").set_sensitive(estado)

            elif procedimiento in ("recibos_a", "recibos_i"):
                self.principal.get_object("vent_recibos").set_sensitive(estado)

            elif procedimiento == "arqueos_i":
                self.principal.get_object("vent_arqueos").set_sensitive(estado)

            elif procedimiento == "cajacierres_i":
                self.principal.get_object("vent_cierres").set_sensitive(estado)

        #self.principal.get_object("inf_resumen_movimiento").set_sensitive(estado)
        self.principal.get_object("vent_aperturas").set_sensitive(not estado)

    def desactiva_permisos_caja(self):
        self.principal.get_object("vent_facturas").set_sensitive(False)
        self.principal.get_object("vent_remisiones").set_sensitive(False)
        self.principal.get_object("vent_creditos").set_sensitive(False)
        self.principal.get_object("vent_debitos").set_sensitive(False)
        self.principal.get_object("vent_recibos").set_sensitive(False)

        self.principal.get_object("vent_arqueos").set_sensitive(False)
        self.principal.get_object("vent_cierres").set_sensitive(False)

    def desactiva(self):
        self.principal.get_object("sist_usuarios").set_sensitive(False)

        self.principal.get_object("rrhh_empresas").set_sensitive(False)
        self.principal.get_object("rrhh_empleados").set_sensitive(False)
        self.principal.get_object("rrhh_beneficiarios").set_sensitive(False)
        self.principal.get_object("rrhh_contratos").set_sensitive(False)
        self.principal.get_object("rrhh_vendedores").set_sensitive(False)

        self.principal.get_object("rrhh_entradas").set_sensitive(False)
        self.principal.get_object("rrhh_asistencias").set_sensitive(False)
        self.principal.get_object("rrhh_permisos").set_sensitive(False)
        self.principal.get_object("rrhh_sanciones").set_sensitive(False)
        self.principal.get_object("rrhh_judiciales").set_sensitive(False)
        self.principal.get_object("rrhh_reposos").set_sensitive(False)
        self.principal.get_object("rrhh_vacaciones").set_sensitive(False)
        self.principal.get_object("rrhh_preavisos").set_sensitive(False)
        self.principal.get_object("rrhh_salidas").set_sensitive(False)

        self.principal.get_object("rrhh_aguinaldos").set_sensitive(False)
        self.principal.get_object("rrhh_anticipos").set_sensitive(False)
        self.principal.get_object("rrhh_descuentos").set_sensitive(False)
        self.principal.get_object("rrhh_gratificaciones").set_sensitive(False)
        self.principal.get_object("rrhh_horas_extras").set_sensitive(False)
        self.principal.get_object("rrhh_pagos").set_sensitive(False)

        self.principal.get_object("comp_ajustes").set_sensitive(False)
        self.principal.get_object("comp_pedidos").set_sensitive(False)
        self.principal.get_object("comp_ordenes").set_sensitive(False)
        self.principal.get_object("comp_facturas").set_sensitive(False)
        self.principal.get_object("comp_creditos").set_sensitive(False)
        self.principal.get_object("comp_debitos").set_sensitive(False)

        self.principal.get_object("vent_aperturas").set_sensitive(False)
        self.principal.get_object("vent_pedidos").set_sensitive(False)
        self.principal.get_object("vent_cheques").set_sensitive(False)
        self.principal.get_object("vent_tarjetas").set_sensitive(False)
        self.desactiva_permisos_caja()

        self.principal.get_object("reg_categorias").set_sensitive(False)
        self.principal.get_object("reg_depositos").set_sensitive(False)
        self.principal.get_object("reg_impuestos").set_sensitive(False)
        self.principal.get_object("reg_marca_items").set_sensitive(False)
        self.principal.get_object("reg_motivo_ajustes").set_sensitive(False)
        self.principal.get_object("reg_presentaciones").set_sensitive(False)
        self.principal.get_object("reg_unidad_medidas").set_sensitive(False)
        self.principal.get_object("reg_items").set_sensitive(False)

        self.principal.get_object("reg_estados_civiles").set_sensitive(False)
        self.principal.get_object("reg_generos").set_sensitive(False)
        self.principal.get_object("reg_ocupaciones").set_sensitive(False)
        self.principal.get_object("reg_rol_personas").set_sensitive(False)
        self.principal.get_object("reg_tipo_clientes").set_sensitive(False)
        self.principal.get_object("reg_tipo_documentos").set_sensitive(False)
        self.principal.get_object("reg_tipo_empresas").set_sensitive(False)
        self.principal.get_object("reg_zona_ventas").set_sensitive(False)

        self.principal.get_object("reg_barrios").set_sensitive(False)
        self.principal.get_object("reg_calles").set_sensitive(False)
        self.principal.get_object("reg_ciudades").set_sensitive(False)
        self.principal.get_object("reg_departamentos").set_sensitive(False)
        self.principal.get_object("reg_paises").set_sensitive(False)
        self.principal.get_object("reg_tipo_calles").set_sensitive(False)
        self.principal.get_object("reg_tipo_medios").set_sensitive(False)

        self.principal.get_object("reg_personas").set_sensitive(False)

        self.principal.get_object("reg_salarios_minimos").set_sensitive(False)
        self.principal.get_object("reg_actividades").set_sensitive(False)
        self.principal.get_object("reg_cargos").set_sensitive(False)
        self.principal.get_object("reg_formas_pago").set_sensitive(False)
        self.principal.get_object("reg_periodos_pago").set_sensitive(False)
        self.principal.get_object("reg_tipo_contratos").set_sensitive(False)
        self.principal.get_object("reg_tipo_parentescos").set_sensitive(False)
        self.principal.get_object("reg_tipo_salarios").set_sensitive(False)
        self.principal.get_object("reg_tipo_seguros").set_sensitive(False)
        self.principal.get_object("reg_turnos_trabajo").set_sensitive(False)

        self.principal.get_object("reg_dias_no_habiles").set_sensitive(False)
        self.principal.get_object("reg_concepto_salarios").set_sensitive(False)
        self.principal.get_object("reg_motivo_descuentos").set_sensitive(False)
        self.principal.get_object("reg_motivo_gratificaciones").set_sensitive(False)
        self.principal.get_object("reg_motivo_permisos").set_sensitive(False)
        self.principal.get_object("reg_motivo_salidas").set_sensitive(False)
        self.principal.get_object("reg_motivo_sanciones").set_sensitive(False)
        self.principal.get_object("reg_tipo_juzgados").set_sensitive(False)
        self.principal.get_object("reg_turnos_juzgado").set_sensitive(False)

        self.principal.get_object("reg_establecimientos").set_sensitive(False)
        self.principal.get_object("reg_cajas").set_sensitive(False)
        self.principal.get_object("reg_timbrados").set_sensitive(False)
        self.principal.get_object("reg_denominaciones").set_sensitive(False)
        self.principal.get_object("reg_tipo_denominaciones").set_sensitive(False)
        self.principal.get_object("reg_tipo_comerciales").set_sensitive(False)
        self.principal.get_object("reg_tipo_valores").set_sensitive(False)

        self.principal.get_object("reg_monedas").set_sensitive(False)
        self.principal.get_object("reg_cotizaciones").set_sensitive(False)
        self.principal.get_object("reg_concepto_recibos").set_sensitive(False)
        self.principal.get_object("reg_marca_tarjetas").set_sensitive(False)
        self.principal.get_object("reg_tipo_cheques").set_sensitive(False)
        self.principal.get_object("reg_tipo_facturas").set_sensitive(False)
        self.principal.get_object("reg_tipo_tarjetas").set_sensitive(False)

        self.principal.get_object("reg_marca_vehiculos").set_sensitive(False)
        self.principal.get_object("reg_motivo_traslados").set_sensitive(False)
        self.principal.get_object("reg_vehiculos").set_sensitive(False)

        self.principal.get_object("info_rrhh_asistencias").set_sensitive(False)

        self.principal.get_object("info_comp_facturas").set_sensitive(False)
        self.principal.get_object("info_comp_creditos").set_sensitive(False)
        self.principal.get_object("info_comp_debitos").set_sensitive(False)

        self.principal.get_object("info_vent_facturas").set_sensitive(False)
        self.principal.get_object("info_vent_creditos").set_sensitive(False)
        self.principal.get_object("info_vent_debitos").set_sensitive(False)
