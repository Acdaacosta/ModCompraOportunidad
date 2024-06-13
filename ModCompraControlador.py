# controller.py
import pandas as pd
from ModCompraModelo import ModCompraModelo
from ModCompraVista import mostrar_banner, mostrar_formulario, mostrar_resultados, plotly_multi_bar_line_chart
import streamlit as st
def main():
    mostrar_banner()
    inv_min, inv_max, precio_nal, precio_imp, inv_ini, costo_uni_inv_ini, archivo_csv = mostrar_formulario()

    if archivo_csv is not None:
        df_archivo = pd.read_csv(archivo_csv, delimiter=';')
        lN = len(df_archivo)
        edited_df = st.data_editor(df_archivo)
        if st.button('Optimizar'):
            Modelo=ModCompraModelo()
            resultados, total_cost, status = Modelo.optimizar(lN, inv_min, inv_max, precio_nal, precio_imp, inv_ini, costo_uni_inv_ini, edited_df)
            mostrar_resultados(resultados, total_cost, status)
            plotly_multi_bar_line_chart(edited_df.columns, resultados["Inventario"], edited_df.values.tolist()[0], resultados["Compra Nacional"] + resultados["Compra Importada"])

if __name__ == '__main__':
    main()
