import streamlit as st
from gekko import GEKKO
import numpy as np
import pandas as pd
#import locale

import plotly.graph_objs as go
from plotly.subplots import make_subplots

#fom itertools import cycle

#para que la moneda salga con signo pesos
#locale.setlocale(locale.LC_MONETARY, "en_US.UTF-8" ) #en_US



def plotly_multi_bar_line_chart(categorias, datos_barras_1, datos_barras_2, datos_lineas):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Agregar las barras 1 en el primer eje y
    
    fig.add_trace(
        go.Bar(x=categorias, y=datos_barras_1, name='Inventario',marker=dict(color='#87CEEB')),
        secondary_y=False,
    )

    # Agregar las barras 2 en el primer eje y
    fig.add_trace(
        go.Scatter(x=categorias, y=datos_barras_2,mode='lines', name='Consumo',marker=dict(color='blue')),
        secondary_y=False,
    )

    # Agregar la línea en el segundo eje y
    fig.add_trace(
        go.Scatter(x=categorias, y=datos_lineas, mode='lines', name='Compras'),
        secondary_y=False,
    )

    # Configurar el diseño del gráfico
    fig.update_layout(
        title_text='Gráfico de Inventarios, Consumos y Compras',
        xaxis_title='Periodos',
        yaxis_title='Inventarios',
        yaxis2_title='Compras y Consumos',
    )

    return fig







# Código de optimización (puede ser en una función separada)
def optimizar(pN
             ,pInv_min
             ,pInv_max
             ,pPrecio_nal
             ,pPrecio_imp
             ,pInv_ini
             ,pCosto_uni_inv_ini
             ,pConsumo_pn
                               ):
    # Crear un modelo GEKKO
    m = GEKKO(remote=False)

    # Parámetros
    n = pN
    inv_min = pInv_min
    inv_max = pInv_max
    precio_nal = pPrecio_nal
    precio_imp = pPrecio_imp
    inv_ini = pInv_ini
    costo_uni_inv_ini = pCosto_uni_inv_ini
    
    consumo_pn=pConsumo_pn.values.tolist()
    # Variables de decisión
    comp_nal_pn = m.Array(m.Var, n, lb=0, ub=40000, integer=True)
    comp_imp_pn = m.Array(m.Var, n, lb=0, ub=40000, integer=True)
    inv_pn = m.Array(m.Var, n + 1, lb=inv_min, ub=inv_max, integer=True)

    costo_com_pn = m.Array(m.Var, n)
    costo_uni_inv_pn = m.Array(m.Var, n)
    costo_inv_pn = m.Array(m.Var, n)
    costo_alm_pn = m.Array(m.Var, n)
    costo_trans_pn = m.Array(m.Var, n)
    costo_cap_pn = m.Array(m.Var, n)
    costo_total_pn = m.Array(m.Var, n)

    # Ecuaciones de restricción
    m.Equation(inv_pn[-1] == inv_ini)
    m.Equation(costo_uni_inv_pn[-1] == costo_uni_inv_ini)
    
    for i in range(n):
        
        m.Equation((costo_com_pn[i] == comp_nal_pn[i] * precio_nal) + (comp_imp_pn[i] * precio_imp))
        
        m.Equation(inv_pn[i] == inv_pn[i - 1] + comp_imp_pn[i] + comp_nal_pn[i] - consumo_pn[0][i])
        
        m.Equation(costo_uni_inv_pn[i] == ((inv_pn[i - 1] * costo_uni_inv_pn[i - 1]) + costo_com_pn[i] - (consumo_pn[0][i] * costo_uni_inv_pn[i - 1])) / inv_pn[i])
        m.Equation(costo_inv_pn[i] == inv_pn[i] * costo_uni_inv_pn[i])
        m.Equation(costo_alm_pn[i] == inv_pn[i] * 315)
        m.Equation(costo_trans_pn[i] == comp_imp_pn[i] * 187)
        m.Equation(costo_cap_pn[i] == costo_inv_pn[i] * ((1 + 0.12) ** (1 / 52) - 1))
        m.Equation(costo_total_pn[i] == costo_com_pn[i] + costo_cap_pn[i] + costo_alm_pn[i] + costo_trans_pn[i])

    # Función objetivo
    m.Obj(sum(costo_total_pn))

    # Resolver el problema de optimización
    m.solve(disp=False)

    # Redondear los valores de las variables a enteros
    comp_nal_pn_values = [round(value[0]) for value in comp_nal_pn]
    comp_imp_pn_values = [round(value[0]) for value in comp_imp_pn]

    # Imprimir los resultados
    print("Valores óptimos de CompNalPn:", comp_nal_pn_values)
    print("Valores óptimos de CompImpPn:", comp_imp_pn_values)

    #Mostrar los resultados 
    costo_total_pn_values = []
    inv_pn_values = []         # Lista para almacenar los valores de inventario
    ListCompraNal=[]           # Lista para almacenar los valores de las compras nacionales
    ListCompraImp=[]           # Lista para almacenar los valores de las compras importadas
    ListCostoCompra=[]         # Lista para almacenar los valores totales de las compras
    ListCostoCapital=[]        # Lista para almacenar los valores de costo capital
    ListCostoAlmacenamiento=[] # Lista para almacenar los valores de costo de almacenamiento
    ListCostoTransporte=[]     # Lista para almacenar los valores de costo transporte
    costo_uni_inv_pn_ant=costo_uni_inv_ini
    for i in range(n):
        costo_com_pn = comp_nal_pn_values[i] * precio_nal + comp_imp_pn_values[i] * precio_imp
        if i == 0:
            inv_pn_value_ant=inv_ini
            inv_pn_value = inv_ini+comp_nal_pn_values[i]+comp_imp_pn_values[i]- consumo_pn[0][i]        
        else:
            inv_pn_value_ant=inv_pn_values[i - 1]
            inv_pn_value = inv_pn_values[i - 1]+comp_nal_pn_values[i]+comp_imp_pn_values[i]- consumo_pn[0][i] 

        costo_uni_inv_pn = ((inv_pn_value_ant * costo_uni_inv_pn_ant) + costo_com_pn -( consumo_pn[0][i] * costo_uni_inv_pn_ant)) / inv_pn_value        
          
        costo_inv_pn = inv_pn_value * costo_uni_inv_pn
        costo_alm_pn = inv_pn_value * 315
        costo_trans_pn = comp_imp_pn_values[i] * 187
        costo_cap_pn = costo_inv_pn * ((1 + 0.12) ** (1 / 52) - 1)
        costo_total_pn = costo_com_pn + costo_cap_pn + costo_alm_pn + costo_trans_pn

        ListCompraNal.append(comp_nal_pn_values[i])
        ListCompraImp.append(comp_imp_pn_values[i])
        ListCostoCompra.append(costo_com_pn)
        ListCostoCapital.append(costo_cap_pn)
        ListCostoAlmacenamiento.append(costo_alm_pn)
        ListCostoTransporte.append(costo_trans_pn)
        costo_total_pn_values.append(costo_total_pn)
        inv_pn_values.append(inv_pn_value)
        costo_uni_inv_pn_ant=costo_uni_inv_pn
        
    #st.write("Inventarios totales")  
    
    
    df_ListCompraNal=pd.DataFrame(ListCompraNal)
    df_ListCompraNal=df_ListCompraNal.T
    df_ListCompraNal.columns = pConsumo_pn.columns
    df_ListCompraImp=pd.DataFrame(ListCompraImp)
    df_ListCompraImp=df_ListCompraImp.T
    df_ListCompraImp.columns = pConsumo_pn.columns

    df_inv_pn_values=pd.DataFrame(inv_pn_values)
    df_inv_pn_values=df_inv_pn_values.T    
    df_inv_pn_values.columns = pConsumo_pn.columns

    df_ListCostoCompra=pd.DataFrame(ListCostoCompra)
    df_ListCostoCompra=df_ListCostoCompra.T    
    df_ListCostoCompra.columns = pConsumo_pn.columns  


    df_ListCostoCapital=pd.DataFrame(ListCostoCapital)
    df_ListCostoCapital=df_ListCostoCapital.T    
    df_ListCostoCapital.columns = pConsumo_pn.columns 

    df_ListCostoAlmacenamiento=pd.DataFrame(ListCostoAlmacenamiento)
    df_ListCostoAlmacenamiento=df_ListCostoAlmacenamiento.T    
    df_ListCostoAlmacenamiento.columns = pConsumo_pn.columns   
     
    df_ListCostoTransporte=pd.DataFrame(ListCostoTransporte)
    df_ListCostoTransporte=df_ListCostoTransporte.T    
    df_ListCostoTransporte.columns = pConsumo_pn.columns  

     
    df_costo_total_pn_values=pd.DataFrame(costo_total_pn_values)
    df_costo_total_pn_values=df_costo_total_pn_values.T
    df_costo_total_pn_values.columns = pConsumo_pn.columns
    
    # Suma de los costos totales
    total_cost = sum(costo_total_pn_values)
    df_final=pd.concat([df_ListCompraNal,df_ListCompraImp, df_inv_pn_values,df_ListCostoCompra,df_ListCostoCapital,df_ListCostoAlmacenamiento,df_ListCostoTransporte, df_costo_total_pn_values], axis=0)
    ColNombres=["Compra Nacional","Compra Importada","inventario","Costo Compra","Costo Capital","Costo Almacenamiento","Costo Transporte","costo total"]
    df_final.insert(loc=0,column="Descripcion",value=ColNombres)
    st.subheader("Resultados:")
    df_final=df_final.set_index('Descripcion')
    df_final=df_final.T #trasponer
    df_final=df_final.round(0)                               
    st.write(df_final)    
    st.write("Valor óptimo de TotalCosto :")
    #total_cost_Formato=locale.format_string("$%i",round(total_cost),grouping=True,monetary=True) 
    #total_cost_Formato=locale.currency(total_cost_Formato,grouping=True)
    total_cost_Formato=round(total_cost)
    st.subheader(total_cost_Formato )
    st.write("Estado de la optimización:", m.options.APPSTATUS)

    st.subheader("Gráfico de Barras y Líneas")
    st.plotly_chart(plotly_multi_bar_line_chart(pConsumo_pn.columns,inv_pn_values, consumo_pn[0], ListCompraNal+ListCompraImp))
    
    
    


  


    

# Página principal de la aplicación
def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Optimización de Inventarios",
        page_icon=":bar_chart:",
        layout="wide"
    )

    # Banner con imagen
    #image_url = "https://www.zenu.com.co/wp-content/uploads/2019/06/logo-ppal.jpg"  # Reemplaza esto con la URL de tu imagen
    #st.image(image_url, width=700) 

    st.title(':bar_chart: Modelo Compra Oportunidad')
    #para que lo coloque arriba y 2rem para que lo baje un poquito y no quede mocho
    
    col1, col2,col3 =st.columns((3))
    # Mostrar los datos en formato Excel (pandas DataFrame)
    with col1:
         lInv_min = st.number_input("Inventario Minimo", value=120000)
         lInv_max= st.number_input("Inventario Maximo", value=1200000)
         
    
    with col2:
         lPrecio_nal= st.number_input("Precio Nacional", value=10000)
         lPrecio_imp= st.number_input("Precio Importado", value=15000)
         
    with col3:     
         lInv_ini= st.number_input("Inventario Inicial", value=120000)
         lCosto_uni_inv_ini= st.number_input("Costo Unitario Inv Ini", value=10707)
    # Widget para ingresar inventario Monimo
    #lInv_min = st.sidebar.number_input("Inventario Minimo", value=120000)
    #lInv_max= st.sidebar.number_input("Inventario Maximo", value=1200000)
     # Widget para ingresar 
    
    #lPrecio_nal= st.sidebar.number_input("Precio Nacional", value=10000)
    #lPrecio_imp= st.sidebar.number_input("Preicio Importado", value=15000)
    #lInv_ini= st.sidebar.number_input("Inventario Inicial", value=120000)
    #lCosto_uni_inv_ini= st.sidebar.number_input("Costo Unitario Inv Ini", value=10707)
     
    
    # ... Agrega más controles según tus necesidades ...
    # Widget para cargar el archivo CSV
    archivo_csv = st.file_uploader(":open_file_folder: Cargar archivo CSV", type=["csv"])
    
    # Verificar si se ha cargado un archivo
    if archivo_csv is not None:
        # Leer el archivo CSV y convertirlo en un DataFrame
        df_archivo = pd.read_csv(archivo_csv,delimiter=';')
        lN = df_archivo.size
        # Generar el grid dinámico
        #data_ingresada = generar_grid_excel(lN)
        edited_df = st.data_editor(df_archivo)
        # Botón para ejecutar la optimización
        if st.button('Optimizar'):
            #st.write(edited_df)
            resultados = optimizar(lN
                                ,lInv_min
                                ,lInv_max
                                ,lPrecio_nal
                                ,lPrecio_imp
                                ,lInv_ini
                                ,lCosto_uni_inv_ini
                                ,edited_df
                                )

        

# Punto de entrada principal
if __name__ == '__main__':
    main()
