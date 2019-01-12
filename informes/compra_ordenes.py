#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import popen

from clases.dialogos import dialogo_guardar
from clases.mensajes import error_permiso_archivo

from clases.listado import cabecera_style
from clases.listado import tabla_celda_just_izquierdo
from clases.listado import tabla_celda_just_derecho
from clases.listado import tabla_style

from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Table

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm


def genera_orden_compra(datos):
    ubicacion_archivo = dialogo_guardar()

    if ubicacion_archivo is not None:
        # Si no tiene la terminación .pdf se le agrega
        if ubicacion_archivo[-4:].lower() != ".pdf":
            ubicacion_archivo += ".pdf"

        story = []
        cabecera = cabecera_style()
        texto = tabla_celda_just_izquierdo()
        titulo = tabla_celda_just_derecho()

        parrafo = Paragraph("Orden de Compra Nº " + datos[0], cabecera)
        story.append(parrafo)
        story.append(Spacer(0, 20))

        # Generar datos del encabezado
        tabla = Table([
            [Paragraph("<b>Proveedor:</b>", titulo), Paragraph(datos[1][0] + ", " + datos[1][1], texto)],
            [Paragraph("<b>Dirección:</b>", titulo), Paragraph(datos[1][2], texto)],
            [Paragraph("<b>Nro. Telefónico:</b>", titulo), Paragraph(datos[1][3], texto)],
            [Paragraph("<b>Forma de Pago:</b>", titulo), Paragraph(datos[2], texto)]
        ], [100, 300])
        tabla.setStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Alineación de la Primera Columna
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),  # Alineación de Otras Columnas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación Vertical de la Tabla
            ('TOPPADDING', (0, 0), (-1, -1), 1),  # Espacio Arriba
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Espacio Abajo
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Izquierda
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Derecha
        ])
        story.append(tabla)
        story.append(Spacer(0, 20))

        # Generar Tabla de Órdenes de Compra
        tabla = Table(datos[3], [70, 125, 150, 75])
        tabla = tabla_style(tabla)
        story.append(tabla)

        doc = SimpleDocTemplate(
            ubicacion_archivo,
            pagesize=A4,  # Tamaño de Página (landscape(A4) hoja horizontal)
            leftMargin=3 * cm,  # Margen Izquierdo
            rightMargin=3 * cm,  # Margen Derecho
            topMargin=2.5 * cm,  # Margen Superior
            bottomMargin=2.5 * cm,  # Margen Inferior
            allowSplitting=1,
            title="Orden de Compra Nro. " + datos[0],
            author="Sistema Distribuidora"
        )

        try:  # Generar Archivo
            doc.build(story)
            popen(ubicacion_archivo)
        except PermissionError as e:
            error_permiso_archivo(str(e))
