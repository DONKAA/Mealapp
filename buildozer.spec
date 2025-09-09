[app]
title = Meal App
package.name = mealapp
package.domain = Mealapp
source.dir = .
source.include_exts = py,kv,txt,db,ttf
version = 0.1.0
requirements = python3,kivy,kivymd,sqlite3,reportlab,setuptools,cython
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.logcat_filters = *:S python:D
android.enable_androidx = 1
# Permessi (per compatibilità; su Android 10+ i file vanno nella sandbox)
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
