[app]

# Nome dell'app come appare sul telefono
title = Meal App
# Nome del pacchetto (identificativo univoco)
package.name = mealapp
package.domain = org.donkaa

# Versione
version = 0.1

# Sorgente (tutti i file .py, .kv, ecc. nella root del repo)
source.dir = .
source.include_exts = py,kv,txt,db,ttf

# Orientamento: portrait / landscape / all
orientation = portrait

# Modalità fullscreen (0 = no, 1 = sì)
fullscreen = 0

# Linguaggio
osx.python_version = 3

# -----------------------------------------------------
# ANDROID
# -----------------------------------------------------

# SDK path: puntiamo alla cartella che installiamo nel workflow GitHub
android.sdk_path = /home/runner/android-sdk

# Target API (Android 13)
android.api = 33
# Minima API supportata
android.minapi = 24

# Architetture supportate
android.archs = arm64-v8a, armeabi-v7a

# Build tools: mettiamo una versione stabile disponibile
android.build_tools = 33.0.2

# Permessi (esempio: per scrivere file PDF)
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# -----------------------------------------------------
# REQUISITI
# -----------------------------------------------------
# Librerie Python da includere
requirements = python3,kivy,kivymd,sqlite3,reportlab,setuptools,cython

# -----------------------------------------------------
# EXTRA
# -----------------------------------------------------
# Usa AndroidX (consigliato su Android moderni)
android.enable_androidx = True

# (opzionale) logcat filter per debug
android.logcat_filters = *:S python:D


