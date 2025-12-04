# Bibliotecas ----
from shiny import App
from server import server
from ui import app_ui

# Shiny app ----
app = App(app_ui, server)
