from ModCompraControlador import ModCompraControlador
#borrar
import streamlit as st
import pandas as pd
from ModCompraModelo import ModCompraModelo
def main():
    controlador=ModCompraControlador()
    controlador.main()
def test():
    print("inicio")
    pConsumo_pn = pd.read_csv(r'C:\Users\ACdaacosta\Downloads\DatosPrueba.csv',delimiter=';')

    print("longitud "+str(pConsumo_pn.shape[1]))
    edited_df = st.data_editor(pConsumo_pn)
    print("longitud2 "+str(len(edited_df)))
    clase=ModCompraModelo()

    clase.optimizar(17,120000,1200000,10000,15000,120000,10707,edited_df,40000,40000)
    
    print("termino")
if __name__ == '__main__':
    main()

