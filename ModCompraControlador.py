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
        inv_min, inv_max, precio_nal, precio_imp, inv_ini, costo_uni_inv_ini, archivo_csv,Cap_compra_nal,Cap_compra_imp,costo_alm,Cap_trans,precio_imp_merma = vista.mostrar_formulario()

        if archivo_csv is not None:
            df_archivo = pd.read_csv(archivo_csv, delimiter=';')
            lN = df_archivo.shape[1]
            
            edited_df = st.data_editor(df_archivo)
            if st.button('Optimizar'):
                Modelo=ModCompraModelo()
                resultados, total_cost, status,l_mensaje = Modelo.optimizar(lN, inv_min, inv_max, precio_nal, precio_imp, inv_ini, costo_uni_inv_ini, edited_df,Cap_compra_nal,Cap_compra_imp ,costo_alm,Cap_trans,precio_imp_merma)
                
                vista.mostrar_resultados(resultados, total_cost, status,l_mensaje)
                if status==1 :                    
                    vista.plotly_multi_bar_line_chart(edited_df.columns, resultados["Inventario"], edited_df.values.tolist()[0], resultados["Compra Nacional"] + resultados["Compra Importada"],status)

    #if __name__ == '__main__':
     #   main()
