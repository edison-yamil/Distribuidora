#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
from os import popen

from clases.dialogos import dialogo_guardar
from clases.fechas import fecha_hoy
from clases.fechas import mysql_fecha
from clases.mensajes import error_permiso_archivo
from clases.operaciones import cadenanumeros
from clases.operaciones import conectar
from clases.operaciones import consultar

from clases.listado import cabecera_style
from clases.listado import tabla_celda_centrado
from clases.listado import tabla_celda_just_izquierdo
from clases.listado import tabla_celda_just_derecho
from clases.listado import tabla_celda_titulo
from clases.listado import tabla_style

from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Table

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm


def genera_comprobante_pago(datos_conexion, nro_comp):
    ubicacion_archivo = dialogo_guardar("Comprobante de Pago")

    if ubicacion_archivo is not None:
        # Si no tiene la terminación .pdf se le agrega
        if ubicacion_archivo[-4:].lower() != ".pdf":
            ubicacion_archivo += ".pdf"

        story = []
        titulo = tabla_celda_titulo()
        texto = tabla_celda_just_izquierdo()
        numero = tabla_celda_just_derecho()
        centro = tabla_celda_centrado()

        tabla = Table([[
            Paragraph("<b><font size=15>Distribuidora María Auxiliadora</font></b><br/><br/>" +
                "<i><font size=12>Productos y Servicios S.A.</font></i><br/><br/><br/>" +
                "<font size=8>Caaguazú - Paraguay</font>", centro),
            Paragraph("RUC:<br/><br/>" +
                "<b><font size=15>RECIBO DE PAGO</font></b><br/><br/>" +
                "<i><font size=7>Liquidación de Sueldo y Otras Remuneraciones<br/>" +
                "(Conforme al Art. 235 del Código Laboral)</font></i><br/><br/>" +
                "<b><font size=15>" + cadenanumeros(nro_comp, 7) + "</font></b>", centro),
        ]], [350, 150])
        tabla.setStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación Vertical de la Tabla
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Borde Exterior de la Tabla
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Grilla Interior de la Tabla
        ])
        story.append(tabla)
        story.append(Spacer(0, 20))

        # Establece la conexión con la Base de Datos
        conexion = conectar(datos_conexion)
        cursor = consultar(conexion, "idEmpleado, NroDocumento, " +
            "NombreApellido, FechaInicio, FechaFin, TotalPagar",
            "comprobantepagos_s", " WHERE NroComprobante = " + nro_comp)
        datos_comp = cursor.fetchall()

        # Buscar otros datos del Empleado
        cursor = consultar(conexion, "DireccionPrincipal",
            "personas_s", " WHERE idPersona = " + str(datos_comp[0][0]))
        datos_empl = cursor.fetchall()
        if cursor.rowcount > 0:
            direccion = "" if datos_empl[0][0] is None else datos_empl[0][0]
        else:
            direccion = ""

        # Buscar datos de la Empresa
        cursor = consultar(conexion, "NroPatronalIPS, NroPatronalMJT",
            "empresas_s", " ORDER BY idEmpresa")
        datos_empr = cursor.fetchall()
        if cursor.rowcount > 0:
            ips = "" if datos_empr[0][0] is None else datos_empr[0][0]
            mjt = "" if datos_empr[0][1] is None else datos_empr[0][1]
        else:
            ips = mjt = ""

        tabla = Table([
            [Paragraph("<b>Lugar y Fecha:</b>",texto), Paragraph("Caaguazú, " + fecha_hoy(), texto), '', ''],
            [Paragraph("<b>Trabajador:</b>", texto), Paragraph(datos_comp[0][2], texto),
                Paragraph("<b>C.I. Nro.:</b>", texto), Paragraph(datos_comp[0][1], texto)],
            [Paragraph("<b>Dirección:</b>", texto), Paragraph(direccion, texto), '', ''],
            [Paragraph("<b>Sucursal:</b>", texto), Paragraph("Caaguazú", texto), '', ''],
            [Paragraph("<b>Periodo de Pago:</b>", texto), Paragraph("Desde " +
                mysql_fecha(datos_comp[0][3]) + " hasta " + mysql_fecha(datos_comp[0][4]), texto), '', ''],
            [Paragraph("<b>Nro. Patronal:</b>", texto), Paragraph(ips + " / " + str(mjt), texto), '', '']
        ], [100, 275, 50, 75])
        tabla.setStyle([
            ('SPAN', (1, 0), (-1, 0)),  # Combina columnas, primera fila
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Alineación de la Primera Columna
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),  # Alineación de Otras Columnas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación Vertical de la Tabla
            ('TOPPADDING', (0, 0), (-1, -1), 1),  # Espacio Arriba
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Espacio Abajo
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Izquierda
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Derecha
            ('SPAN', (1, 2), (-1, 2)),  # Combina columnas, segunda fila
            ('SPAN', (1, 3), (-1, 3)),  # Combina columnas, tercera fila
            ('SPAN', (1, 4), (-1, 4)),  # Combina columnas, cuarta fila
            ('SPAN', (1, 5), (-1, 5)),  # Combina columnas, quinta fila
        ])
        story.append(tabla)
        story.append(Spacer(0, 20))

        cursor = consultar(conexion, "Cantidad, Concepto, Monto",
            "comprobantepagos_detalles_s", " WHERE NroComprobante = " + nro_comp)
        datos_det = cursor.fetchall()
        cant = cursor.rowcount
        lista = [[Paragraph("Cantidad", titulo), Paragraph("Descripción", titulo), Paragraph("Importe", titulo)]]

        for i in range(0, cant):
            cantidad = "" if datos_det[i][0] is None else str(datos_det[i][0])
            lista.append([Paragraph(cantidad, centro), Paragraph(datos_det[i][1], texto),
                Paragraph(str(datos_det[i][2]), numero)])

        if cant < 16:  # Completar hasta 16 casillas
            for i in range(cant, 16):
                lista.append(["", "", ""])

        # Total a Pagar
        lista.append([Paragraph("Total a Pagar:", numero), '', Paragraph(str(datos_comp[0][5]), numero)])

        tabla = Table(lista, [100, 300, 100])
        tabla = tabla_style(tabla)
        tabla.setStyle([
            ('SPAN', (0, -1), (-2, -1)),  # Combina columnas, última fila
        ])
        story.append(tabla)

        #ubicacion_archivo = path.join(path.expanduser("~"), "Desktop", "listado.pdf")
        doc = SimpleDocTemplate(
            ubicacion_archivo,
            pagesize=A4,  # Tamaño de Página (landscape(A4) hoja horizontal)
            leftMargin=3 * cm,  # Margen Izquierdo
            rightMargin=3 * cm,  # Margen Derecho
            topMargin=2.5 * cm,  # Margen Superior
            bottomMargin=2.5 * cm,  # Margen Inferior
            allowSplitting=1,
            title="Comprobante de Pago Nro. " + cadenanumeros(nro_comp, 7),
            author="Sistema Distribuidora"
        )

        try:  # Generar Archivo
            doc.build(story)
            popen(ubicacion_archivo)
        except PermissionError as e:
            error_permiso_archivo(str(e))
