[app]
# --- Info app ---
title = Meal App
package.name = mealapp
package.domain = org.donkaa
version = 0.1

# --- Sorgenti ---
source.dir = .
source.include_exts = py,kv,txt,db,ttf

# --- UI ---
orientation = portrait
fullscreen = 0

# --- Python on host/mac (ignorato su GH Actions, ok così) ---
osx.python_version = 3

# =================================================================
# ANDROID
# =================================================================
# Usa l’SDK installato dal workflow in /home/runner/android-sdk
android.sdk_path = /home/runner/android-sdk

# Target / min API
android.api = 33
android.minapi = 24

# Build-tools stabili (evita 36.x rc che non esistono)
android.build_tools = 33.0.2

# Architetture supportate
android.archs = arm64-v8a, armeabi-v7a

# Permessi (per salvare/leggere PDF nella sandbox, compat)
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# AndroidX abilitato
android.enable_androidx = True

# Log utili in debug
android.logcat_filters = *:S python:D

# =================================================================
# DIPENDENZE PYTHON
# =================================================================
# Kivy + KivyMD + SQLite + ReportLab (Pillow utile a ReportLab)
requirements = python3,kivy,kivymd,sqlite3,reportlab,pillow,setuptools,cython

# (Opzionale) se vuoi limitare i moduli di kivy per alleggerire:
# android.include_exts = py,kv,txt,db,ttf
# android.requirements = ...

# =================================================================
# FIRMA (lascia vuoto per debug)
# =================================================================
# android.keystore = %(source.dir)s/keystore.jks
# android.keyalias = mealapp
# android.keystore_password = 
# android.keyalias_password = 

# =================================================================
# VARI (lascia default se non sai cosa sono)
# =================================================================
# p4a.branch = master
# android.ndk = 25b
# android.accept_sdk_license = True
