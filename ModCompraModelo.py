from gekko import GEKKO
import pandas as pd
import streamlit as st

class ModCompraModelo:
    def __init__(self):
        pass

    def optimizar(self, pN, pInv_min, pInv_max, pPrecio_nal, pPrecio_imp, pInv_ini, pCosto_uni_inv_ini, pConsumo_pn, p_Cap_compra_nal, p_Cap_compra_imp):
        try:
            m = GEKKO(remote=False)
            #m.options.SOLVER = 3  # 1 = APOPT, 2 = BPOPT, 3 = IPOPT
            m.options.IMODE = 3  # Modo de optimización de variables mixtas

            # Configurar la optimización global
           # m.options.MINLP_MAXIMUM_ITERATIONS = 100000  # Número máximo de iteraciones
           # m.options.MINLP_GAP_TOL = 1e-6  # Tolerancia de la brecha de óptimo global
           # m.options.MINLP_AS_NLP = 0  # Resolver como un problema no lineal mixto-integro (MINLP)
           # m.options.MINLP_BRANCH_METHOD = 1  # Método de ramificación

            # Parámetros
            n = pN
            inv_min = pInv_min
            inv_max = pInv_max
            precio_nal = pPrecio_nal
            precio_imp = pPrecio_imp
            inv_ini = pInv_ini
            costo_uni_inv_ini = pCosto_uni_inv_ini

            pConsumo_pn_Adicional = pd.DataFrame({'Periodo -1': [0]})
            pConsumo_pn=pd.concat([pConsumo_pn_Adicional, pConsumo_pn], axis=1)
            consumo_pn = pConsumo_pn.values.tolist()
            # Agregar un elemento al principio con valor 0
            #consumo_pn = [0] + consumo_pn[0]
            print(consumo_pn)
            
            # Variable auxiliar para asegurar múltiplos de 25000
           # mul_25000 = 25000  # Múltiplo deseado
            comp_nal_pn = m.Array(m.Var, n+1, lb=0, ub=p_Cap_compra_nal , integer =True)
            comp_imp_pn = m.Array(m.Var, n+1, lb=0, ub=p_Cap_compra_imp , integer =True)
            
            # Variables reales multiplicadas por el múltiplo
           # comp_nal_real = m.Array(m.Var, n)
            #comp_imp_real = m.Array(m.Var, n)

           # for i in range(n):
                # Relacionar las variables auxiliares con las reales
            #    m.Equation(comp_nal_real[i] == comp_nal_pn[i] * mul_25000)
             #   m.Equation(comp_imp_real[i] == comp_imp_pn[i] * mul_25000)

            #inv_pn = m.Array(m.Var, n + 1, lb=inv_min, ub=inv_max, integer=True)
            inv_pn = m.Array(m.Var, n + 1, lb=inv_min ,ub=inv_max,integer =True)

            costo_com_pn = m.Array(m.Var, n+1, lb=0,integer =True)
            costo_uni_inv_pn = m.Array(m.Var, n+1, lb=0,integer =True)
            costo_uni_inv_pn_ant = m.Array(m.Var, n+1, lb=0,integer =True, value=0)
            costo_inv_pn = m.Array(m.Var, n+1, lb=0,integer =True)
            costo_alm_pn = m.Array(m.Var, n+1, lb=0,integer =True)
            costo_trans_pn = m.Array(m.Var, n+1, lb=0,integer =True)
            costo_cap_pn = m.Array(m.Var, n+1, lb=0,integer =True)
            costo_total_pn = m.Array(m.Var, n+1, lb=0,integer =True)

            m.Equation(inv_pn[0] == inv_ini)
            m.Equation(costo_uni_inv_pn[0] == costo_uni_inv_ini)
            m.Equation(costo_inv_pn[0] == inv_ini*costo_uni_inv_ini)
            m.Equation(costo_uni_inv_pn_ant[0] == 0)
            m.Equation(costo_alm_pn[0] == 0)
            
            m.Equation(costo_cap_pn[0] == 0)
            m.Equation(comp_imp_pn[0] == 0)
            m.Equation(costo_trans_pn[0] == 0)
            for i in range(1, n ):
                m.Equation((costo_com_pn[i] == m.abs(comp_nal_pn[i] * precio_nal) + (comp_imp_pn[i] * precio_imp)))
                m.Equation(inv_pn[i] == inv_pn[i - 1] + comp_imp_pn[i] + comp_nal_pn[i] - consumo_pn[0][i])
                m.Equation(costo_uni_inv_pn_ant[i]==consumo_pn[0][i]*costo_uni_inv_pn[i-1])
                m.Equation(costo_uni_inv_pn[i] == (m.abs(costo_inv_pn[i-1])+m.abs(costo_com_pn[i])-costo_uni_inv_pn_ant[i])/ inv_pn[i])
                m.Equation(costo_inv_pn[i] == inv_pn[i]*costo_uni_inv_pn[i])
                m.Equation(costo_alm_pn[i] == inv_pn[i] * 315)
                #m.Equation(costo_trans_pn[i] == m.abs(comp_imp_pn[i]) * 187)
               # m.Equation(costo_trans_pn[i] == int(comp_imp_pn[i]))
                m.Equation(costo_cap_pn[i] == costo_inv_pn[i] * ((1 + 0.12) ** (1 / 52) - 1))
                #costo_com_pn[i] 
                #m.Equation(costo_total_pn[i] == costo_com_pn[i] +costo_cap_pn[i] + costo_alm_pn[i] + costo_trans_pn[i])

            m.Obj(sum(inv_pn))
            m.solve(disp=False)
            print("costo_trans_pn")
            print(costo_trans_pn)
            print("comp_imp_pn")
            print(comp_imp_pn )
            comp_nal_real_values = [round(value[0]) for value in comp_nal_pn]
            comp_imp_real_values = [round(value[0]) for value in comp_imp_pn]
            costo_total_pn_values = []
            inv_pn_values = []
            ListCompraNal = []
            ListCompraImp = []
            ListCostoCompra = []
            ListCostoCapital = []
            ListCostoAlmacenamiento = []
            ListCostoTransporte = []
            costo_uni_inv_pn_ant = costo_uni_inv_ini

            for i in range( n ):
                costo_com_pn = comp_nal_real_values[i] * precio_nal + comp_imp_real_values[i] * precio_imp
                if i == 0:
                    inv_pn_value_ant = inv_ini
                    inv_pn_value = inv_ini + comp_nal_real_values[i] + comp_imp_real_values[i] - consumo_pn[0][i]
                else:
                    inv_pn_value_ant = inv_pn_values[i - 1]
                    inv_pn_value = inv_pn_values[i - 1] + comp_nal_real_values[i] + comp_imp_real_values[i] - consumo_pn[0][i]

                costo_uni_inv_pn = ((inv_pn_value_ant * costo_uni_inv_pn_ant) + costo_com_pn - (consumo_pn[0][i] * costo_uni_inv_pn_ant)) / inv_pn_value
                costo_inv_pn = inv_pn_value * costo_uni_inv_pn
                costo_alm_pn = inv_pn_value * 315
                costo_trans_pn = comp_imp_real_values[i] * 187
                costo_cap_pn = costo_inv_pn * ((1 + 0.12) ** (1 / 52) - 1)
                costo_total_pn = costo_com_pn + costo_cap_pn + costo_alm_pn + costo_trans_pn

                ListCompraNal.append(comp_nal_real_values[i])
                ListCompraImp.append(comp_imp_real_values[i])
                ListCostoCompra.append(costo_com_pn)
                ListCostoCapital.append(costo_cap_pn)
                ListCostoAlmacenamiento.append(costo_alm_pn)
                ListCostoTransporte.append(costo_trans_pn)
                costo_total_pn_values.append(costo_total_pn)
                inv_pn_values.append(inv_pn_value)
                costo_uni_inv_pn_ant = costo_uni_inv_pn

            df_results = pd.DataFrame({
                "Compra Nacional": ListCompraNal,
                "Compra Importada": ListCompraImp,
                "Inventario": inv_pn_values,
                "Costo Compra": ListCostoCompra,
                "Costo Capital": ListCostoCapital,
                "Costo Almacenamiento": ListCostoAlmacenamiento,
                "Costo Transporte": ListCostoTransporte,
                "Costo Total": costo_total_pn_values
            })
            #df_results.to_excel(r"C:\Users\ACdaacosta\Downloads\resultadoOptimizacion.xlsx", index=False)
            total_cost = sum(costo_total_pn_values)
            g_mensaje="se optimizo Correctamente"
            return df_results, total_cost, m.options.APPSTATUS,g_mensaje
        except Exception as e:
            e_mensaje="Hubo un error al optimizar el modelo. "+str(e)
            # Captura la excepción si no se encontró solución
                   # Muestra el mensaje de error específico
            return None, None, -1,e_mensaje  # Retorna valores nulos o vacíos según convenga


# Ejemplo de uso
if __name__ == "__main__":
    # Definir parámetros de ejemplo
    pN = 17
    pInv_min = 120000
    pInv_max = 1200000
    pPrecio_nal = 11000 #error 10700 
    pPrecio_imp = 15000
    pInv_ini = 120000
    pCosto_uni_inv_ini = 10708
    pConsumo_pn = pd.DataFrame({
        'Periodo 1': [0], 'Periodo 2': [0], 'Periodo 3': [0], 'Periodo 4': [0],
        'Periodo 5': [0], 'Periodo 6': [0], 'Periodo 7': [0], 'Periodo 8': [0],
        'Periodo 9': [0], 'Periodo 10': [0], 'Periodo 11': [10000], 'Periodo 12': [20000],
        'Periodo 13': [30000], 'Periodo 14': [40000], 'Periodo 15': [50000], 'Periodo 16': [60000],
        'Periodo 17': [70000]
    })
    p_Cap_compra_nal = 40000
    p_Cap_compra_imp = 40000

    # Crear instancia del modelo
    modelo = ModCompraModelo()

    # Optimizar
    df_results, total_cost, status, message = modelo.optimizar(pN, pInv_min, pInv_max, pPrecio_nal, pPrecio_imp, pInv_ini, pCosto_uni_inv_ini, pConsumo_pn, p_Cap_compra_nal, p_Cap_compra_imp)
    print("estatus")
    print(status)
    # Mostrar resultados
    if status!=-1:
        print("Resultados:")
        print(df_results)
        print("Costo Total:", total_cost)
    else:
        print("Error:", message)
