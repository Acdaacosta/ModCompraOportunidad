# controller.py
import pandas as pd
from ModCompraModelo import ModCompraModelo
from ModCompraVista import ModCompraVista 
import streamlit as st

class ModCompraControlador:

    def __init__(self):
        
        pass

    def main(self):
        vista=ModCompraVista()
        vista.mostrar_banner()
        inv_min, inv_max, precio_nal, precio_imp, inv_ini, costo_uni_inv_ini, archivo_csv = vista.mostrar_formulario()

        if archivo_csv is not None:
            df_archivo = pd.read_csv(archivo_csv, delimiter=';')
            lN = len(df_archivo)
            edited_df = st.data_editor(df_archivo)
            if st.button('Optimizar'):
                Modelo=ModCompraModelo()
                resultados, total_cost, status = Modelo.optimizar(lN, inv_min, inv_max, precio_nal, precio_imp, inv_ini, costo_uni_inv_ini, edited_df)
                vista.mostrar_resultados(resultados, total_cost, status)
                vista.plotly_multi_bar_line_chart(edited_df.columns, resultados["Inventario"], edited_df.values.tolist()[0], resultados["Compra Nacional"] + resultados["Compra Importada"])

    #if __name__ == '__main__':
     #   main()
