#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from navegador import navegador


#### Usuarios ##########################################################

class grupousuarios:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "grupousuarios", "idGrupoUsuario", 1,
            "Grupos de Usuarios" + ampliacion, origen, otros)


class sistematablas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "sistematablas", "idTabla", 3,
            "Tablas del Sistema" + ampliacion, origen, otros)


#### Recursos Humanos - Empleados ######################################

class empresas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "empresas", "idEmpresa", 2,
            "Empresas" + ampliacion, origen, otros)


class empleados:

    def __init__(self, datos_conexion, origen=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "personas", "idPersona", 4,
            "Empleados" + ampliacion, origen, "Empleado = 1")


class beneficiarios:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "beneficiarios", "idEmpleado", 3,
            "Beneficiarios" + ampliacion, origen, otros)


class contratos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        if origen is None:
            ampliacion = ""
        else:
            ampliacion = " (Buscar)"
            otros = "" if otros is None else otros + " AND "
            otros += "Vigente = 1"  # Solo contratos vigentes

        navegador(datos_conexion, "contratos", "NroContrato", 3,
            "Contratos" + ampliacion, origen, otros)


class vendedores:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "vendedores", "idVendedor", 3,
            "Vendedores" + ampliacion, origen, otros)


#### Recursos Humanos - Movimientos ####################################

class entradas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "entradas", "idEntrada", 3,
            "Entradas" + ampliacion, origen, otros)


class permisos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "permisos", "idPermiso", 3,
            "Permisos" + ampliacion, origen, otros)


class sanciones:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "sanciones", "idSancion", 3,
            "Sanciones" + ampliacion, origen, otros)


class judiciales:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "judiciales", "idJustificativo", 3,
            "Justificativos Judiciales" + ampliacion, origen, otros)


class reposos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "reposos", "idReposo", 3,
            "Reposos" + ampliacion, origen, otros)


class vacaciones:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "vacaciones", "idVacacion", 3,
            "Vacaciones" + ampliacion, origen, otros)


class preavisos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "preavisos", "idPreaviso", 3,
            "Preavisos" + ampliacion, origen, otros)


class salidas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "salidas", "idSalida", 3,
            "Salidas" + ampliacion, origen, otros)


#### Recursos Humanos - Remuneraciones #################################

class aguinaldos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "aguinaldos", "idAguinaldo", 3,
            "Aguinaldos" + ampliacion, origen, otros)


class anticipos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "anticipos", "idAnticipo", 3,
            "Anticipos" + ampliacion, origen, otros)


class descuentos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "descuentos", "idDescuento", 3,
            "Descuentos" + ampliacion, origen, otros)


class gratificaciones:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "gratificaciones", "idGratificacion", 3,
            "Gratificaciones" + ampliacion, origen, otros)


class horaextraordinarias:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "horaextraordinarias", "idHoraExtraordinaria", 3,
            "Hora Extraordinarias" + ampliacion, origen, otros)


class comprobantepagos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "comprobantepagos", "NroComprobante", 3,
            "Comprobantes de Pago" + ampliacion, origen, otros)


#### Compras ###########################################################

class pedidocompras:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "pedidocompras", "NroPedidoCompra", 3,
            "Pedidos de Compra" + ampliacion, origen, otros)


class ordencompras:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "ordencompras", "NroOrdenCompra", 3,
            "Órdenes de Compra" + ampliacion, origen, otros)


class facturacompras:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "facturacompras", "NroFactura", 3,
            "Facturas de Compra" + ampliacion, origen, otros)


class notacreditocompras:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "notacreditocompras", "NroNotaCredito", 3,
            "Notas de Crédito por Compras" + ampliacion, origen, otros)


class notadebitocompras:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "notadebitocompras", "NroNotaDebito", 3,
            "Notas de Débito por Compras" + ampliacion, origen, otros)


#### Ventas ############################################################

class chequeterceros:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "chequeterceros", "idChequeTercero", 3,
            "Cheques de Terceros" + ampliacion, origen, otros)


class tarjetas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tarjetas", "NroTarjeta", 3,
            "Tarjetas" + ampliacion, origen, otros)


#### Referenciales de Items ############################################

class categorias:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "categorias", "idCategoria", 1,
            "Categorías" + ampliacion, origen, otros)


class depositos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "depositos", "idDeposito", 1,
            "Depósitos" + ampliacion, origen, otros)


class impuestos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "impuestos", "idImpuesto", 1,
            "Impuestos" + ampliacion, origen, otros)


class marcaitems:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "marcaitems", "idMarca", 1,
            "Marcas de Items" + ampliacion, origen, otros)


class motivoajustes:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "motivoajustes", "idMotivoAjuste", 1,
            "Motivos de Ajuste" + ampliacion, origen, otros)


class presentaciones:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "presentaciones", "idPresentacion", 1,
            "Presentaciones" + ampliacion, origen, otros)


class unidadmedidas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "unidadmedidas", "idUnidadMedida", 1,
            "Unidades de Medida" + ampliacion, origen, otros)


class items:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "items", "idItem", 4,
            "Items" + ampliacion, origen, otros)


#### Referenciales de Datos Personales #################################

class estadosciviles:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "estadosciviles", "idEstadoCivil", 1,
            "Estados Civiles" + ampliacion, origen, otros)


class generos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "generos", "idGenero", 1,
            "Géneros" + ampliacion, origen, otros)


class ocupaciones:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "ocupaciones", "idOcupacion", 1,
            "Ocupaciones" + ampliacion, origen, otros)


class rolpersonas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "rolpersonas", "idRolPersona", 1,
            "Roles de Personas" + ampliacion, origen, otros)


class tipoclientes:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipoclientes", "idTipoCliente", 1,
            "Tipos de Clientes" + ampliacion, origen, otros)


class tipodocumentos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipodocumentos", "idTipoDocumento", 1,
            "Tipos de Documentos de Identidad" + ampliacion, origen, otros)


class tipoempresas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipoempresas", "idTipoEmpresa", 1,
            "Tipos de Empresas" + ampliacion, origen, otros)


class zonaventas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "zonaventas", "idZonaVenta", 1,
            "Zonas de Ventas" + ampliacion, origen, otros)


#### Referenciales de Datos de Localización ############################

class barrios:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "barrios", "idBarrio", 1,
            "Barrios" + ampliacion, origen, otros)


class calles:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "calles", "idCalle", 1,
            "Calles" + ampliacion, origen, otros)


class ciudades:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "ciudades", "idCiudad", 3,
            "Ciudades" + ampliacion, origen, otros)


class departamentos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "departamentos", "idDepartamento", 2,
            "Departamentos, Provincias, Estados" + ampliacion, origen, otros)


class paises:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "paises", "idPais", 1,
            "Países" + ampliacion, origen, otros)


class tipocalles:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipocalles", "idTipoCalle", 1,
            "Tipos de Calles" + ampliacion, origen, otros)


class tipomediocontactos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipomediocontactos", "idTipoMedioContacto", 1,
            "Tipos de Medios de Contacto" + ampliacion, origen, otros)

########################################################################

class personas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "personas", "idPersona", 4,
            "Personas" + ampliacion, origen, otros)


########################################################################

class actividadeseconomicas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "actividadeseconomicas", "idActividadEconomica", 1,
            "Actividades Económicas" + ampliacion, origen, otros)


class cargos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "cargos", "idCargo", 1,
            "Cargos" + ampliacion, origen, otros)


class formapagos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "formapagos", "idFormaPago", 1,
            "Formas de Pago" + ampliacion, origen, otros)


class periodopagos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "periodopagos", "idPeriodoPago", 1,
            "Periodos de Pago" + ampliacion, origen, otros)


class tipocontratos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipocontratos", "idTipoContrato", 1,
            "Tipos de Contratos" + ampliacion, origen, otros)


class tipoparentescos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipoparentescos", "idTipoParentesco", 1,
            "Tipos de Parentescos" + ampliacion, origen, otros)


class tiposalarios:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tiposalarios", "idTipoSalario", 1,
            "Tipos de Salarios" + ampliacion, origen, otros)


class tiposeguros:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tiposeguros", "idTipoSeguro", 1,
            "Tipos de Seguros" + ampliacion, origen, otros)


########################################################################

class conceptopagos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "conceptopagos", "idConcepto", 1,
            "Conceptos de Pago de Salarios" + ampliacion, origen, otros)


class motivodescuentos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "motivodescuentos", "idMotivoDescuento", 1,
            "Motivos de Descuentos" + ampliacion, origen, otros)


class motivogratificaciones:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "motivogratificaciones", "idMotivoGratificacion", 1,
            "Motivos de Gratificaciones" + ampliacion, origen, otros)


class motivopermisos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "motivopermisos", "idMotivoPermiso", 1,
            "Motivos de Permisos" + ampliacion, origen, otros)


class motivosalidas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "motivosalidas", "idMotivoSalida", 2,
            "Motivos de Salidas" + ampliacion, origen, otros)


class motivosanciones:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "motivosanciones", "idMotivoSancion", 2,
            "Motivos de Sanciones" + ampliacion, origen, otros)


class tipojuzgados:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipojuzgados", "idTipoJuzgado", 1,
            "Tipos de Juzgados" + ampliacion, origen, otros)


class turnojuzgados:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "turnojuzgados", "idTurnoJuzgado", 1,
            "Turnos de Juzgados" + ampliacion, origen, otros)


########################################################################

class establecimientos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "establecimientos", "NroEstablecimiento", 2,
            "Establecimientos" + ampliacion, origen, otros)


class puntoexpediciones:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "puntoexpediciones", "NroPuntoExpedicion", 2,
            "Puntos de Expedición o Cajas" + ampliacion, origen, otros)


class denominaciones:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "denominaciones", "idDenominacion", 2,
            "Denominaciones" + ampliacion, origen, otros)


class timbrados:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "timbrados", "NroTimbrado", 3,
            "Timbrado de Documentos" + ampliacion, origen, otros)


class tipodenominaciones:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipodenominaciones", "idTipoDenominacion", 1,
            "Tipos de Denominaciones" + ampliacion, origen, otros)


class tipodocumentocomerciales:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipodocumentocomerciales", "idTipoDocumentoComercial", 1,
            "Tipos de Documentos Comerciales" + ampliacion, origen, otros)


class tipovalores:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipovalores", "idTipoValor", 1,
            "Tipos de Valores" + ampliacion, origen, otros)


########################################################################

class monedas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "monedas", "idMoneda", 2,
            "Monedas" + ampliacion, origen, otros)


class cotizaciones:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "cotizaciones", "idCotizacion", 2,
            "Cotizaciones de Monedas" + ampliacion, origen, otros)


class conceptorecibos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "conceptorecibos", "idConcepto", 1,
            "Conceptos de Cobros por Recibos" + ampliacion, origen, otros)


class marcatarjetas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "marcatarjetas", "idMarcaTarjeta", 1,
            "Marcas de Tarjetas" + ampliacion, origen, otros)


class tipocheques:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipocheques", "idTipoCheque", 1,
            "Tipos de Cheques" + ampliacion, origen, otros)


class tipofacturas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipofacturas", "idTipoFactura", 1,
            "Tipos de Facturas" + ampliacion, origen, otros)


class tipotarjetas:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "tipotarjetas", "idTipoTarjeta", 1,
            "Tipos de Tarjetas" + ampliacion, origen, otros)


########################################################################

class marcavehiculos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "marcavehiculos", "idMarcaVehiculo", 1,
            "Marcas de Vehiculos" + ampliacion, origen, otros)


class motivotraslados:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "motivotraslados", "idMotivoTraslado", 1,
            "Motivos de Traslados" + ampliacion, origen, otros)


class vehiculos:

    def __init__(self, datos_conexion, origen=None, otros=None):
        ampliacion = "" if origen is None else " (Buscar)"
        navegador(datos_conexion, "vehiculos", "idVehiculo", 1,
            "Vehículos" + ampliacion, origen, otros)
