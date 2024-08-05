from ModCompraControlador import ModCompraControlador
import os
import platform
#borrar
import streamlit as st
import pandas as pd
from ModCompraModelo import ModCompraModelo
def main():
    #controlador=ModCompraControlador()
    #controlador.main()
    os_name = os.name  # 'posix' para sistemas Unix (Linux, macOS) y 'nt' para Windows
    platform_name = platform.system()  # 'Linux', 'Windows', 'Darwin' (macOS
    st.write(f"Nombre del sistema operativo (os.name): {os_name}")
    st.write(f"Nombre del sistema operativo (platform.system()): {platform_name}")
def test():
    #print("inicio")
    pConsumo_pn = pd.read_csv(r'C:\Users\ACdaacosta\Downloads\DatosPrueba.csv',delimiter=';')

    #print("longitud "+str(pConsumo_pn.shape[1]))
    edited_df = st.data_editor(pConsumo_pn)
    #print("longitud2 "+str(len(edited_df)))
    clase=ModCompraModelo()
    pcompraNal = pd.DataFrame({
        'Periodo 1': [0], 'Periodo 2': [0], 'Periodo 3': [0], 'Periodo 4': [0],
        'Periodo 5': [20000], 'Periodo 6': [0], 'Periodo 7': [20000], 'Periodo 8': [20000],
        'Periodo 9': [0], 'Periodo 10': [40000], 'Periodo 11': [0], 'Periodo 12': [40000],
        'Periodo 13': [0], 'Periodo 14': [40000], 'Periodo 15': [40000], 'Periodo 16': [10000],
        'Periodo 17': [40000]
    })
    pcompraImp = pd.DataFrame({
        'Periodo 1': [40000], 'Periodo 2': [0], 'Periodo 3': [0], 'Periodo 4': [0],
        'Periodo 5': [0], 'Periodo 6': [40000], 'Periodo 7': [40000], 'Periodo 8': [0],
        'Periodo 9': [0], 'Periodo 10': [0], 'Periodo 11': [0], 'Periodo 12': [20000],
        'Periodo 13': [0], 'Periodo 14': [40000], 'Periodo 15': [0], 'Periodo 16': [15000],
        'Periodo 17': [40000]
    })
    print("inicio optimizar")
    resultados, total_cost, status ,lmensaje=clase.optimizar(17,120000,1200000,11000,15000,120000,10707,edited_df,40000,40000,315,187,1.5)
    
    #print("termino test")
    #print(resultados[1:].applymap(lambda x: '{:,.0f}'.format(x).replace(',', '.') if isinstance(x, (int, float)) else x))
    #print("Costo Total:", total_cost) 
    #print(lmensaje)
    #resultados[1:].to_excel(r'C:\Users\ACdaacosta\Downloads\SalidaCompraOportunidad.xlsx')
    if status != -1:
        print("Resultados:")
        #print(resultados[1:].applymap(lambda x: '{:,.0f}'.format(x).replace(',', '.') if isinstance(x, (int, float)) else x))
        print("Costo Total:", total_cost)
        resultados[1:].to_excel(r'C:\Users\ACdaacosta\Downloads\SalidaCompraOportunidad.xlsx')
    else:
        print("Error:", lmensaje)
    print("termino optimizar")

    print("inicia baseline")
    df_resultados_Base, total_cost, status ,lmensaje=clase.Baseline(17,11000,15000,120000,10707,edited_df,315,187,pcompraNal,pcompraImp)
    #print("termino baseline")
    #print(df_resultados_Base)
    #df_resultados_Base.to_excel(r'C:\Users\ACdaacosta\Downloads\SalidaCompraOportunidadBase.xlsx')
    #df_concatenado = pd.concat([df_optimizado, df_resultados_Base], axis=1)
    #df_concatenado.to_excel(r'C:\Users\ACdaacosta\Downloads\SalidaCompraOportunidadUnido.xlsx')
    if status != -1:
        print("Resultados:")
        #print(df_resultados_Base.applymap(lambda x: '{:,.0f}'.format(x).replace(',', '.') if isinstance(x, (int, float)) else x))
        print("Costo Total:", total_cost)
        df_resultados_Base.to_excel(r'C:\Users\ACdaacosta\Downloads\SalidaCompraOportunidadBase.xlsx')
    else:
        print("Error:", lmensaje)
    print("termino baseline")


    print("inicia optimizarSemilla")
    #resultados, total_cost, status ,lmensaje=clase.optimizarSemilla(17,120000,1200000,13500,15000,120000,10707,edited_df,40000,40000,315,187,1.5,pcompraNal,pcompraImp)
    
    #if status != -1:
        #print("Resultados:")
        #print(resultados[1:].applymap(lambda x: '{:,.0f}'.format(x).replace(',', '.') if isinstance(x, (int, float)) else x))
        #print("Costo Total:", total_cost)
        #resultados[1:].to_excel(r'C:\Users\ACdaacosta\Downloads\SalidaCompraOportunidadSemilla.xlsx')
    #else:
     #   print("Error:", lmensaje)
    #print("termino optimizarSemilla")
    
    
    

if __name__ == '__main__':
    main()
    

