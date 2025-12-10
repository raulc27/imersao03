# Bibliotecas ----
from shiny import Inputs, Outputs, Session, render, reactive
from shinywidgets import render_widget
from globals import df_ipca
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# Back end ----
def server(input: Inputs, output: Outputs, session: Session):

    @reactive.calc
    def obter_dados_fanchart():
        modelo_selecionado = input.modelos()
        dados = (
            df_ipca
            .query("tipo in [@modelo_selecionado, 'Observado']")
            .assign(
                tipo = lambda x: x["tipo"].replace({"Observado": "IPCA"}),
                data_referencia = lambda x: x["data_referencia"].dt.strftime("%Y-%m-%d")
                )
            .tail(12*15)
        )
        return dados
    
    @reactive.calc
    def preparar_dados_fantable():
        modelo_selecionado = input.modelos()
        df_fantable = (
            obter_dados_fanchart()
            .query("tipo == @modelo_selecionado")
            .filter(["data_referencia", "ic_inferior", "valor", "ic_superior"])
            .assign(data_referencia = lambda x: pd.to_datetime(x.data_referencia).dt.strftime("%m/%Y"))
            .rename(
                columns = {
                    "data_referencia": "Período",
                    "ic_inferior": "I.C. Inferior",
                    "valor": "Previsão",
                    "ic_superior": "I.C. Superior"
                }
            )
            .round(2)
        )
        return df_fantable

    @render_widget
    def fanchart():
        df_fanchart = obter_dados_fanchart()
        fig = px.line(
            data_frame = df_fanchart,
            x = "data_referencia",
            y = "valor",
            color = "tipo",
            title = "Previsão do IPCA",
            labels = {"data_referencia": "Data", "valor": "Valor", "tipo": "Série"},
            hover_data = {"data_referencia": True, "valor": ':.2f', "tipo": True}
        )


        df_ic = df_fanchart.query("tipo != 'Observado'").sort_values("data_referencia")
        fig.add_trace(
            go.Scatter(
                x = df_ic["data_referencia"],
                y = df_ic["ic_superior"],
                mode = 'lines',
                line = dict(width=0),
                showlegend = False,
                hoverinfo = 'skip'
            )
        )
        fig.add_trace(
            go.Scatter(
                x = df_ic["data_referencia"],
                y = df_ic["ic_inferior"],
                mode = 'lines',
                line = dict(width=0),
                fill = 'tonexty',
                fillcolor = 'rgba(30,144,255,0.18)',
                showlegend = False,
                hoverinfo = 'skip'
            )
        )

        return fig

    @render.data_frame
    def fantable():
        return preparar_dados_fantable()