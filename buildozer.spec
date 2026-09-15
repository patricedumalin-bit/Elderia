[app]

# Application title
title = Les Chroniques d'Elderia

# Package name
package.name = elderia
package.domain = org.elderia

# Source code directory (relative to the root directory)
source.dir = .

# Application versioning
version = 1.0.0
num_version = 1

# Orientation (landscape, portrait, sensorLandscape, sensorPortrait)
orientation = portrait

# Android API version
android.api = 33
android.minapi = 21
android.sdk = 34
android.ndk = 25b

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,flet==0.27.2,pygame,pillow

# Permissions
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# Applications entry point
entrypoint.module = main

# Include directories
source.include_exts = py,png,jpg,kv,atlas,json,ogg,mp3,txt,md

# (list) List of services to enable
services_enabled =

# (bool) Support Android TV ?
android.allow_backup = True

# (int) Target Android API, in comment if not specified
p4a.bootstrap = sdl2

# (str) android.logcat_args = <list>
android.logcat_args =

[buildozer]

# (str) Python version to use
buildozer.log_level = 2

# (str) Application version
buildozer.version = 1.0.0