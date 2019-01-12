#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from cx_Freeze import setup, Executable


base = None
if sys.platform == "win32":
    base = "Win32GUI"


#        "includes": [
#            "/*.glade",
#            "/*.pdf"
#        ],


options = {
    "build_exe": {
        "compressed": True,
        "path": sys.path + ["modules"]
    }
}


executables = [
    Executable("__init__.pyw")
]


setup(
    name = "Distribuidora",
    version = "1.0",
    description = "Sistema de Gestión de Recursos Humanos, Compras y Facturación",
    author = "Edison Yamil Yinde García",
    author_email = "edison_yamil@hotmail.com",
    executables = executables,
    packages=["ventanas", "ayudas"],
    options = options,
)
