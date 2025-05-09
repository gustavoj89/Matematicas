import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns


# Crear  tabla de amortizacion
TablaAmortizacion = {
    "Fecha de pago": [],
    "NumeroCuotas": [],
    "SaldoInicial": [],
    "CuotaFija": [],
    "Interes": [],
    "CuotaFinal": [],
}
# Crear tabla de Plazo del credito
PlazoCredito = {
    "Años": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
}

pd1 = pd.read_excel("Datos.xlsx", sheet_name="Tipo de vivienda")
pd2 = pd.read_excel("Datos.xlsx", sheet_name="Subsidios")
pd3 = pd.read_excel("Datos.xlsx", sheet_name="Periodos")
pd4 = pd.read_excel("Datos.xlsx", sheet_name="Puntaje sisben")
bancos_df = pd.read_excel("Datos.xlsx", sheet_name="Bancos")
chart_data = bancos_df[["Bancos", "Tasa Min", "Tasa Max", "Tipo vivienda"]]
st.header("Simulador de crédito hipotecario")


def main():

    # Definir fecha de pago del prestamo
    FechaPago = st.date_input(
        "Digite fecha para hacer los pagos", value=dt.date.today()
    )
    st.write("Fecha seleccionada:", FechaPago)
    # Definir monto del prestamo
    Monto = st.number_input(
        "Digite el monto solicitado",
        min_value=1000000,
        max_value=1000000000,
        value=1000000,
    )
    MontoInicial = (
        Monto  # Guardar el monto inicial para usarlo en la tabla de amortización
    )
    st.write("Monto seleccionado:", Monto)
    # Definir Banco sacando los datos de la grafica Tipo de vivienda
    Banco = st.selectbox("Seleccione el banco", options=chart_data["Bancos"].unique())
    # Filtrar datos del banco seleccionado
    Bancodata = chart_data[chart_data["Bancos"] == Banco]
    tasa_min = Bancodata["Tasa Min"].values[0]
    tasa_max = Bancodata["Tasa Max"].values[0]
    # Selectbox para el periodo de pago
    Periodo = st.selectbox(
        "Seleccione el Periodo de pago", options=pd3["Periodo"].unique()
    )
    # Filtrar datos del periodo seleccionado
    PeriodoData = pd3[pd3["Periodo"] == Periodo]
    Cuotas = PeriodoData["Numeros"].values[0]  # Extraer la cantidad de cuotas

    st.write("Cantidad de cuotas ajustada:", Cuotas)

    Plazo = st.selectbox(
        "Seleccione el Plazo del crédito (en años)", options=PlazoCredito["Años"]
    )
    st.write("Plazo seleccionado:", Plazo, "años")

    # Slice para tasa de interes
    InteresSel = st.slider(
        "Seleccione los intereses del prestamo", tasa_min, tasa_max, step=0.01
    )
    InteresSel1 = InteresSel / 100
    # Ajustar el interés según el periodo del crédito
    Interes = (1 + InteresSel1) ** (1 / Cuotas) - 1
    st.write("Interés ajustado:", f"{Interes:.5f}%")

    # Calcular la cantidad de cuotas según el período y el plazo
    Cuotas1 = Plazo * Cuotas
    st.write("Cantidad de cuotas ajustada:", Cuotas)

    # Crear filas para la tabla de amortizacion
    global dfa
    TablaAmortizacion.clear()  # Reset the table before populating
    for i in range(Cuotas1):
        # Calcular la fecha de pago
        if "Fecha de pago" not in TablaAmortizacion:
            TablaAmortizacion["Fecha de pago"] = []
        FechaPago = FechaPago + dt.timedelta(days=30)
        TablaAmortizacion["Fecha de pago"].append(FechaPago)

        if "NumeroCuotas" not in TablaAmortizacion:
            TablaAmortizacion["NumeroCuotas"] = []
        TablaAmortizacion["NumeroCuotas"].append(i + 1)

        if "SaldoInicial" not in TablaAmortizacion:
            TablaAmortizacion["SaldoInicial"] = []
        TablaAmortizacion["SaldoInicial"].append(f"${Monto:,.0f}")

        if "CuotaFija" not in TablaAmortizacion:
            TablaAmortizacion["CuotaFija"] = []
        # Calcular la cuota fija
        CuotaFija = (
            MontoInicial
            * (Interes * (1 + Interes) ** Cuotas1)
            / ((1 + Interes) ** Cuotas1 - 1)
        )
        TablaAmortizacion["CuotaFija"].append(f"${CuotaFija:,.0f}")

        if "Interes" not in TablaAmortizacion:
            TablaAmortizacion["Interes"] = []
        # Calcular el interés como porcentaje
        InteresPorcentaje = Interes * 100
        TablaAmortizacion["Interes"].append(f"{InteresPorcentaje:.2f}%")

        if "CuotaFinal" not in TablaAmortizacion:
            TablaAmortizacion["CuotaFinal"] = []
        # La cuota final es igual a la cuota fija
        CuotaFinal = CuotaFija
        TablaAmortizacion["CuotaFinal"].append(f"${CuotaFinal:,.0f}")

        # Reducir el saldo inicial
        Monto = Monto - (CuotaFija - (Monto * Interes))

    # Ensure all lists in TablaAmortizacion have the same length
    max_length = max(len(v) for v in TablaAmortizacion.values())
    for key in TablaAmortizacion:
        while len(TablaAmortizacion[key]) < max_length:
            TablaAmortizacion[key].append(None)

    dfa = pd.DataFrame(TablaAmortizacion)  # Create DataFrame after the loop

    st.dataframe(bancos_df, use_container_width=True)
    # Cargar datos desde el archivo Excel

    # Configurar el tema de Seaborn
    sns.set_theme(style="darkgrid")

    # Crear la gráfica con Seaborn
    plt.figure(figsize=(30, 10))  # Ajustar el tamaño de la figura
    sns.barplot(
        data=bancos_df, x="Bancos", y="Tasa Min", color="blue", label="Tasa Min"
    )
    sns.barplot(data=bancos_df, x="Bancos", y="Tasa Max", color="red", label="Tasa Max")
    plt.legend(title="Tasas")
    plt.title("Tasas de Interés por Banco")
    plt.xlabel("Bancos")
    plt.ylabel("Tasa (%)")

    # Mostrar la gráfica en Streamlit
    st.pyplot(plt.gcf())

    st.dataframe(pd1)
    # Grafica 2
    sns.set_theme(style="darkgrid")
    plt.figure(figsize=(30, 10))  # Ajustar el tamaño de la figura
    sns.displot(
        data=bancos_df,
        x="Tasa Min",
        hue="Tipo vivienda",
        kind="kde",
        fill=True,
        height=5,
        aspect=2,
    )
    plt.title("Distribución de Tasas de Interés por Tipo de Vivienda")
    plt.xlabel("Tasa (%)")
    plt.ylabel("Densidad")
    plt.legend(title="Tipo de Vivienda")
    # Mostrar la gráfica en Streamlit
    st.pyplot(plt.gcf())
    # Mostrar la gráfica en Streamlit

    st.dataframe(pd3)
    st.dataframe(dfa, use_container_width=True)


x = st.selectbox(
    "Selecciona el tipo de vivienda",
    options=chart_data["Tipo vivienda"].unique(),
    index=0,
)
match x:
    case "VIP":
        chart_data = chart_data[chart_data["Tipo vivienda"] == "VIP"]
    case "VIS":
        chart_data = chart_data[chart_data["Tipo vivienda"] == "VIS"]
    case "No VIS":
        chart_data = chart_data[chart_data["Tipo vivienda"] == "No VIS"]
    case _:
        st.write("No hay datos para el tipo de vivienda seleccionado")


if x == "No Vis":
    st.line_chart(
        chart_data,
        x="Bancos",
        y=["Tasa Min", "Tasa Max"],
        width=300,
        height=500,
        use_container_width=True,
    )
elif x == "Vis":
    st.line_chart(
        chart_data,
        x="Bancos",
        y=["Tasa Min", "Tasa Max"],
        width=300,
        height=500,
        use_container_width=True,
    )
else:
    st.line_chart(
        chart_data,
        x="Bancos",
        y=["Tasa Min", "Tasa Max"],
        width=300,
        height=500,
        use_container_width=True,
    )
    # Crear la gráfica de Small Multiple Time Series


# Llamar a la función en el flujo principal
if __name__ == "__main__":
    main()
