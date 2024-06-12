# view.py
import streamlit as st
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def mostrar_banner():
    st.set_page_config(page_title="Optimización de Inventarios", page_icon=":bar_chart:", layout="wide")
    st.title(':bar_chart: Modelo Compra Oportunidad')

def mostrar_formulario():
    col1, col2, col3 = st.columns(3)
    with col1:
        inv_min = st.number_input("Inventario Minimo", value=120000)
        inv_max = st.number_input("Inventario Maximo", value=1200000)
    with col2:
        precio_nal = st.number_input("Precio Nacional", value=10000)
        precio_imp = st.number_input("Precio Importado", value=15000)
    with col3:
        inv_ini = st.number_input("Inventario Inicial", value=120000)
        costo_uni_inv_ini = st.number_input("Costo Unitario Inv Ini", value=10707)
    archivo_csv = st.file_uploader(":open_file_folder: Cargar archivo CSV", type=["csv"])
    return inv_min, inv_max, precio_nal, precio_imp, inv_ini, costo_uni_inv_ini, archivo_csv

def mostrar_resultados(df_resultados, total_cost, status):
    st.subheader("Resultados:")
    st.write(df_resultados)
    st.write("Valor óptimo de TotalCosto :")
    total_cost_Formato=round(total_cost)
    total_cost_Formato_con_miles = "{:,.0f}".format(total_cost_Formato).replace(",", ".")                               
    st.subheader(total_cost_Formato_con_miles )
    
    st.write("Estado de la optimización:", status)

def plotly_multi_bar_line_chart(categorias, datos_barras_1, datos_barras_2, datos_lineas):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=categorias, y=datos_barras_1, name='Inventario', marker=dict(color='#87CEEB')), secondary_y=False)
    fig.add_trace(go.Scatter(x=categorias, y=datos_barras_2, mode='lines', name='Consumo', marker=dict(color='blue')), secondary_y=False)
    fig.add_trace(go.Scatter(x=categorias, y=datos_lineas, mode='lines', name='Compras'), secondary_y=False)
    fig.update_layout(title_text='Gráfico de Inventarios, Consumos y Compras', xaxis_title='Periodos', yaxis_title='Inventarios', yaxis2_title='Compras y Consumos')
    st.plotly_chart(fig)