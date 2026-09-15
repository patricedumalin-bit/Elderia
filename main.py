import flet as ft
from elderia.ui.android_ui import ElderiaAndroidApp

if __name__ == "__main__":
    app = ElderiaAndroidApp()
    ft.app(target=app.main, assets_dir="assets")
