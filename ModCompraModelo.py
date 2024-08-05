import pandas as pd
import numpy as np
import pyomo.environ as pyo
import os
import requests
import streamlit as st
class ModCompraModelo:
    
    def __init__(self):
        pass

    def optimizar(self, pN, pInv_min, pInv_max, pPrecio_nal, pPrecio_imp, pInv_ini, pCosto_uni_inv_ini, pConsumo_pn, p_Cap_compra_nal, p_Cap_compra_imp,p_costo_alm,P_costo_trans,p_porcentaje_merma):
        try:

            ipopt_path = os.getenv("IPOPT_PATH") 
            exe_local_path = "ipopt.exe"
            # Descargar el archivo ipopt.exe desde GitHub
            @st.cache_data
            def download_exe(url, save_path):
                response = requests.get(url)
                with open(save_path, 'wb') as f:
                    f.write(response.content)
            if not os.path.exists(exe_local_path):
                st.write("Descargando solver IPOPT...")
                download_exe(ipopt_path, exe_local_path)
                st.write("Descarga completada.")   
            if os.name != 'nt':  # No es necesario en Windows
                st.write("Estableciendo permisos de ejecución...")
                os.chmod(ipopt_path, 0o755)
                st.write("Permisos establecidos.")       
            #ipopt_path =r"C:\daacosta\Python\ipopt\Ipopt-3.14.16\bin\ipopt.exe"
            #ipopt_path ="https://github.com/Acdaacosta/ModCompraOportunidad/blob/main/ipopt.exe"
            # Parámetros
            n = pN + 1  # hay 1 registro de más, el registro cero
            precio_nal = pPrecio_nal
            precio_imp = pPrecio_imp
            inv_ini = pInv_ini
            costo_uni_inv_ini = pCosto_uni_inv_ini

            # Valores permitidos
            valores_permitidos = [0,25000,40000]

            pConsumo_pn_Adicional = pd.DataFrame({'Periodo -1': [0]})
            pConsumo_pn = pd.concat([pConsumo_pn_Adicional, pConsumo_pn], axis=1)
            consumo_pn = pConsumo_pn.values.flatten().tolist()
            #print(consumo_pn)
            #agregar la merma
            consumo_pn = [np.round(valor * (1+(p_porcentaje_merma/100))) for valor in consumo_pn]
           # print(consumo_pn)

            # Crear el modelo
            model = pyo.ConcreteModel()
            model.valores_permitidos = pyo.Set(initialize=valores_permitidos)

            # Definir variables de decisión
            model.comp_nal_pn = pyo.Var(range(n), within=pyo.NonNegativeIntegers, bounds=(0, p_Cap_compra_nal), initialize=0)
            model.comp_imp_pn = pyo.Var(range(n), within=pyo.NonNegativeIntegers, bounds=(0, p_Cap_compra_imp), initialize=0)
            model.inv_pn = pyo.Var(range(n), within=pyo.NonNegativeReals, bounds=(pInv_min, pInv_max), initialize=pInv_ini)
            
            #model.bin_vars_imp = pyo.Var(range(n), model.valores_permitidos, within=pyo.Binary)
            #def unica_seleccion_imp(model, i):
            #    return sum(model.bin_vars_imp[i, v] for v in model.valores_permitidos) == 1
            #model.unica_seleccion_imp = pyo.Constraint(range(n), rule=unica_seleccion_imp)

            #def comp_imp_valores_discretos(model, i):
            #    return model.comp_imp_pn[i] == sum(v * model.bin_vars_imp[i, v] for v in model.valores_permitidos)
            #model.comp_imp_valores_discretos = pyo.Constraint(range(n), rule=comp_imp_valores_discretos)

            # Definir restricciones de inventario
            def inventario_constraint(model, i):
                if i == 0:
                    return model.inv_pn[i] == inv_ini
                else:
                    return model.inv_pn[i] == model.inv_pn[i - 1] + model.comp_nal_pn[i] + model.comp_imp_pn[i] - consumo_pn[i]
            model.inventario_constraint = pyo.Constraint(range(n), rule=inventario_constraint)

            
            # Definir función objetivo
            def objetivo(model):
                costo_total = 0
                costo_uni_inv_pn_ant = costo_uni_inv_ini

                for i in range(1, n):
                    comp_nal_val = model.comp_nal_pn[i]
                    comp_imp_val = model.comp_imp_pn[i]
                    inv_pn_val_ant = model.inv_pn[i-1]
                    consumo_pn_val = consumo_pn[i]

                    costo_com_pn = (comp_nal_val * precio_nal) + (comp_imp_val * precio_imp)
                    inv_pn_val_current = model.inv_pn[i]

                    #if inv_pn_val_current == 0:
                    #    continue

                    costo_uni_inv_pn = ((inv_pn_val_ant * costo_uni_inv_pn_ant) + costo_com_pn - (consumo_pn_val * costo_uni_inv_pn_ant)) / inv_pn_val_current
                    costo_inv_pn = inv_pn_val_current * costo_uni_inv_pn
                    costo_alm_pn = inv_pn_val_current *  p_costo_alm
                    costo_trans_pn = comp_imp_val *  P_costo_trans 
                    costo_cap_pn = costo_inv_pn * ((1 + 0.12) ** (1 / 52) - 1)

                    costo_total += costo_com_pn + costo_cap_pn + costo_alm_pn + costo_trans_pn
                    costo_uni_inv_pn_ant = costo_uni_inv_pn

                return costo_total

            model.objetivo = pyo.Objective(rule=objetivo, sense=pyo.minimize)  # Cambia a minimize

            # Resolver el modelo usando un solver NLP 
            solver = pyo.SolverFactory('ipopt', executable=exe_local_path)  # Cambia el solver a ipopt

            result = solver.solve(model, tee=False)  # tee=True para ver el output del solver
            #print()
            if result.solver.status != pyo.SolverStatus.ok:
                raise ValueError("Optimización no exitosa")

            # Asegurarse de que todas las variables tienen valores después de la optimización
            comp_nal_real_values = [pyo.value(model.comp_nal_pn[i]) for i in range(n)]
            comp_imp_real_values = [pyo.value(model.comp_imp_pn[i]) for i in range(n)]
            inv_pn_values = [pyo.value(model.inv_pn[i]) for i in range(n)]

            ListCostoCompra = []
            ListCostoCapital = []
            ListCostoUnitario = []
            ListCostoInventario = []
            ListCostoAlmacenamiento = []
            ListCostoTransporte= []
            ListCostoTotal= []
            ListCostoCompra.append(0)
            ListCostoCapital.append(0)
            ListCostoUnitario.append(0)
            ListCostoInventario.append(0)
            ListCostoAlmacenamiento.append(0)
            ListCostoTransporte.append(0)
            ListCostoTotal.append(0)
            costo_uni_inv_pn_ant = costo_uni_inv_ini

            for i in range(1, n):
                comp_nal_val = comp_nal_real_values[i]
                comp_imp_val = comp_imp_real_values[i]
                inv_pn_value_ant = inv_pn_values[i - 1]
                inv_pn_value = inv_pn_values[i]
                consumo_pn_val = consumo_pn[i]
                costo_com_pn = comp_nal_val * precio_nal + comp_imp_val * precio_imp
                costo_uni_inv_pn = ((inv_pn_value_ant * costo_uni_inv_pn_ant) + costo_com_pn - (consumo_pn[i] * costo_uni_inv_pn_ant)) / inv_pn_value
                costo_alm_pn = inv_pn_value * p_costo_alm
                
                costo_trans_pn = comp_imp_val * P_costo_trans
                costo_inv_pn = inv_pn_value * costo_uni_inv_pn
                costo_cap_pn = costo_inv_pn * ((1 + 0.12) ** (1 / 52) - 1)
                costo_uni_inv_pn_ant = costo_uni_inv_pn
                costo_total_pn = costo_com_pn + costo_cap_pn + costo_alm_pn + costo_trans_pn

                ListCostoCompra.append(costo_com_pn / 1000)
                ListCostoCapital.append(costo_cap_pn)
                ListCostoUnitario.append(costo_uni_inv_pn)
                ListCostoInventario.append(costo_inv_pn / 1000)
                ListCostoAlmacenamiento.append(costo_alm_pn)
                ListCostoTransporte.append(costo_trans_pn)
                ListCostoTotal.append(costo_total_pn)

            df_results = pd.DataFrame({
                "Compra Nacional": comp_nal_real_values,
                "Compra Importada": comp_imp_real_values,
                "Inventario": inv_pn_values,
                "CostoCompra": ListCostoCompra,
                "CostoUnitario": ListCostoUnitario,
                "CostoInv": ListCostoInventario,
                "CostoCapital": ListCostoCapital,
                "CostoAlm": ListCostoAlmacenamiento,
                "costoTrans": ListCostoTransporte,
                "Costo Total": ListCostoTotal
            })

            total_cost = sum(ListCostoTotal)
            g_mensaje = "Se optimizó correctamente"
            return df_results, total_cost, 1, g_mensaje

        except Exception as e:
            e_mensaje = "Hubo un error al optimizar el modelo. " + str(e)
            return None, None, -1, e_mensaje

    def Baseline(self, pN,  pPrecio_nal, pPrecio_imp, pInv_ini, pCosto_uni_inv_ini, pConsumo_pn, p_costo_alm,P_costo_trans,p_comp_nal,pcompraImp):
        try:
            #print("yyyy")
            # Parámetros
            n = pN   # hay 1 registro de más, el registro cero
            #print("1")
            consumo_pn = pConsumo_pn.values.flatten().tolist()
            l_comp_nal=p_comp_nal.values.flatten().tolist()
            l_compraImp=pcompraImp.values.flatten().tolist()
            #print("2",consumo_pn)
            #Consumo_pn = [np.round(valor * (1+(p_porcentaje_merma/100))) for valor in pConsumo_pn]
            #print("3")

            ListCostoCompra = []
            ListCostoCapital = []
            ListCostoUnitario = []
            ListCostoInventario = []
            ListCostoAlmacenamiento = []
            ListCostoTransporte= []
            ListCostoTotal= []
            inv_pn_values= []
            #ListCostoCompra.append(0)
            #ListCostoCapital.append(0)
            #ListCostoUnitario.append(0)
            #ListCostoInventario.append(0)
            #ListCostoAlmacenamiento.append(0)
            #ListCostoTransporte.append(0)
            #ListCostoTotal.append(0)
            costo_uni_inv_pn_ant = pCosto_uni_inv_ini
            
            #inv_pn_values.append(pInv_ini)
            #print("yyyy222",n)
            #print("entro")
            for i in range(0, n):
                #print("oe",i)
                comp_nal_val = l_comp_nal[i]
                #print("oe2",i)
                comp_imp_val = l_compraImp[i]
                #print("oe3",i)
                if i==0 :
                    inv_pn_value_ant=pInv_ini
                else:    
                    inv_pn_value_ant = inv_pn_values[i - 1]
                #print("oe4",i)
                #print("i:",i," inv_pn_value_ant:",inv_pn_value_ant," comp_nal_val:",comp_nal_val," comp_imp_val:",comp_imp_val," consumo_pn[i] ",consumo_pn[i])
                inv_pn_value = inv_pn_value_ant + comp_nal_val + comp_imp_val - consumo_pn[i]
                #print("oe5",i)
                #inv_pn_value = inv_pn_values[i]
                #consumo_pn_val = consumo_pn[i]
                costo_com_pn = comp_nal_val * pPrecio_nal + comp_imp_val * pPrecio_imp
                costo_uni_inv_pn = ((inv_pn_value_ant * costo_uni_inv_pn_ant) + costo_com_pn - (consumo_pn[i] * costo_uni_inv_pn_ant)) / inv_pn_value
                costo_alm_pn = inv_pn_value * p_costo_alm
                
                costo_trans_pn = comp_imp_val * P_costo_trans
                costo_inv_pn = inv_pn_value * costo_uni_inv_pn
                costo_cap_pn = costo_inv_pn * ((1 + 0.12) ** (1 / 52) - 1)
                costo_uni_inv_pn_ant = costo_uni_inv_pn
                costo_total_pn = costo_com_pn + costo_cap_pn + costo_alm_pn + costo_trans_pn

                inv_pn_values.append(inv_pn_value)
                ListCostoCompra.append(costo_com_pn / 1000)
                ListCostoCapital.append(costo_cap_pn)
                ListCostoUnitario.append(costo_uni_inv_pn)
                ListCostoInventario.append(costo_inv_pn / 1000)
                ListCostoAlmacenamiento.append(costo_alm_pn)
                ListCostoTransporte.append(costo_trans_pn)
                ListCostoTotal.append(costo_total_pn)

            df_results = pd.DataFrame({
                "Compra Nacional": l_comp_nal,
                "Compra Importada": l_compraImp,
                "Inventario": inv_pn_values,
                "CostoCompra": ListCostoCompra,
                "CostoUnitario": ListCostoUnitario,
                "CostoInv": ListCostoInventario,
                "CostoCapital": ListCostoCapital,
                "CostoAlm": ListCostoAlmacenamiento,
                "costoTrans": ListCostoTransporte,
                "Costo Total": ListCostoTotal
            })
           # print("sisas XXX")
           # print(df_results)
           # print("sisas ZZZZZ")
            total_cost = sum(ListCostoTotal)
            g_mensaje = "Se optimizó correctamente"
            return df_results, total_cost, 1, g_mensaje

        except Exception as e:
            e_mensaje = "Hubo un error al optimizar el modelo. " + str(e)
            print(e_mensaje)
            return None, None, -1, e_mensaje  

    def optimizarSemilla(self, pN, pInv_min, pInv_max, pPrecio_nal, pPrecio_imp, pInv_ini, pCosto_uni_inv_ini, pConsumo_pn, p_Cap_compra_nal, p_Cap_compra_imp,p_costo_alm,P_costo_trans,p_porcentaje_merma,p_comp_nal,pcompraImp):
        try:
            # Parámetros
            n = pN + 1  # hay 1 registro de más, el registro cero
            precio_nal = pPrecio_nal
            precio_imp = pPrecio_imp
            inv_ini = pInv_ini
            costo_uni_inv_ini = pCosto_uni_inv_ini

            # Valores permitidos
            valores_permitidos = [0,25000,40000]

            pConsumo_pn_Adicional = pd.DataFrame({'Periodo -1': [0]})
            pConsumo_pn = pd.concat([pConsumo_pn_Adicional, pConsumo_pn], axis=1)

            p_comp_nal=pd.concat([p_comp_nal, pConsumo_pn], axis=1)
            pcompraImp=pd.concat([pcompraImp, pConsumo_pn], axis=1)
        
            consumo_pn = pConsumo_pn.values.flatten().tolist()
            comp_nal_ini=p_comp_nal.values.flatten().tolist()
            comp_imp_ini=pcompraImp.values.flatten().tolist()
            #print(consumo_pn)
            #agregar la merma
            consumo_pn = [np.round(valor * (1+(p_porcentaje_merma/100))) for valor in consumo_pn]
           # print(consumo_pn)


            total_comp_nal=sum(comp_nal_ini)
            total_comp_omp=sum(comp_imp_ini)
            print(total_comp_nal)

            

            # Crear el modelo
            model = pyo.ConcreteModel()
            model.valores_permitidos = pyo.Set(initialize=valores_permitidos)

            # Definir variables de decisión
            model.comp_nal_pn = pyo.Var(range(n), within=pyo.NonNegativeIntegers, bounds=(0, p_Cap_compra_nal), initialize=0)
            model.comp_imp_pn = pyo.Var(range(n), within=pyo.NonNegativeIntegers, bounds=(0, p_Cap_compra_imp), initialize=0)
            model.inv_pn = pyo.Var(range(n), within=pyo.NonNegativeReals, bounds=(pInv_min, pInv_max), initialize=pInv_ini)
            #print("semilla1")
            
            # Inicializar variables con valores proporcionados, si existen
            if comp_nal_ini is not None:
                #print("semilla1.1")
                #print(comp_nal_ini)
                for i in range(n):
                    #print("semilla1.1:",i)
                    model.comp_nal_pn[i].value = comp_nal_ini[i]
            if comp_imp_ini is not None:
                #print("semilla1.2")
                for i in range(n):
                    model.comp_imp_pn[i].value = comp_imp_ini[i]
            #print("semilla10")
            #model.bin_vars_imp = pyo.Var(range(n), model.valores_permitidos, within=pyo.Binary)
            #def unica_seleccion_imp(model, i):
            #    return sum(model.bin_vars_imp[i, v] for v in model.valores_permitidos) == 1
            #model.unica_seleccion_imp = pyo.Constraint(range(n), rule=unica_seleccion_imp)

            #def comp_imp_valores_discretos(model, i):
            #    return model.comp_imp_pn[i] == sum(v * model.bin_vars_imp[i, v] for v in model.valores_permitidos)
            #model.comp_imp_valores_discretos = pyo.Constraint(range(n), rule=comp_imp_valores_discretos)

            # Definir restricciones de inventario
            def inventario_constraint(model, i):
                if i == 0:
                    return model.inv_pn[i] == inv_ini
                else:
                    return model.inv_pn[i] == model.inv_pn[i - 1] + model.comp_nal_pn[i] + model.comp_imp_pn[i] - consumo_pn[i]
            model.inventario_constraint = pyo.Constraint(range(n), rule=inventario_constraint)
              # Nueva restricción: la suma de comp_nal_pn debe ser igual a 99999
            #def suma_comp_nal_constraint(model):
            #     return sum(model.comp_nal_pn[i] for i in range(n)) <= total_comp_nal
            #model.suma_comp_nal_constraint = pyo.Constraint(rule=suma_comp_nal_constraint)

           # def resta_comp_nal_constraint(model):
           #      return sum(model.comp_nal_pn[i] for i in range(n)) >= total_comp_nal-900000
           # model.resta_comp_nal_constraint = pyo.Constraint(rule=resta_comp_nal_constraint)
            # Definir función objetivo
            def objetivo(model):
                costo_total = 0
                costo_uni_inv_pn_ant = costo_uni_inv_ini

                for i in range(1, n):
                    comp_nal_val = model.comp_nal_pn[i]
                    comp_imp_val = model.comp_imp_pn[i]
                    inv_pn_val_ant = model.inv_pn[i-1]
                    consumo_pn_val = consumo_pn[i]

                    costo_com_pn = (comp_nal_val * precio_nal) + (comp_imp_val * precio_imp)
                    inv_pn_val_current = model.inv_pn[i]

                    #if inv_pn_val_current == 0:
                    #    continue

                    costo_uni_inv_pn = ((inv_pn_val_ant * costo_uni_inv_pn_ant) + costo_com_pn - (consumo_pn_val * costo_uni_inv_pn_ant)) / inv_pn_val_current
                    costo_inv_pn = inv_pn_val_current * costo_uni_inv_pn
                    costo_alm_pn = inv_pn_val_current *  p_costo_alm
                    costo_trans_pn = comp_imp_val *  P_costo_trans 
                    costo_cap_pn = costo_inv_pn * ((1 + 0.12) ** (1 / 52) - 1)

                    costo_total += costo_com_pn + costo_cap_pn + costo_alm_pn + costo_trans_pn
                    costo_uni_inv_pn_ant = costo_uni_inv_pn

                return costo_total

            model.objetivo = pyo.Objective(rule=objetivo, sense=pyo.minimize)  # Cambia a minimize

            # Resolver el modelo usando un solver NLP 
            solver = pyo.SolverFactory('ipopt')  # Cambia el solver a ipopt
            solver.options['warm_start_init_point'] = 'yes'
            solver.options['warm_start_same_structure'] = 'no'
            #solver.options['bound_push'] =1000
            solver.options['warm_start_bound_frac'] = 0.05
            #solver.options['max_iter'] = 10000
            

            result = solver.solve(model, tee=False)  # tee=True para ver el output del solver
            #print()
            if result.solver.status != pyo.SolverStatus.ok:
                raise ValueError("Optimización no exitosa")

            # Asegurarse de que todas las variables tienen valores después de la optimización
            comp_nal_real_values = [pyo.value(model.comp_nal_pn[i]) for i in range(n)]
            comp_imp_real_values = [pyo.value(model.comp_imp_pn[i]) for i in range(n)]
            inv_pn_values = [pyo.value(model.inv_pn[i]) for i in range(n)]

            ListCostoCompra = []
            ListCostoCapital = []
            ListCostoUnitario = []
            ListCostoInventario = []
            ListCostoAlmacenamiento = []
            ListCostoTransporte= []
            ListCostoTotal= []
            ListCostoCompra.append(0)
            ListCostoCapital.append(0)
            ListCostoUnitario.append(0)
            ListCostoInventario.append(0)
            ListCostoAlmacenamiento.append(0)
            ListCostoTransporte.append(0)
            ListCostoTotal.append(0)
            costo_uni_inv_pn_ant = costo_uni_inv_ini

            for i in range(1, n):
                comp_nal_val = comp_nal_real_values[i]
                comp_imp_val = comp_imp_real_values[i]
                inv_pn_value_ant = inv_pn_values[i - 1]
                inv_pn_value = inv_pn_values[i]
                consumo_pn_val = consumo_pn[i]
                costo_com_pn = comp_nal_val * precio_nal + comp_imp_val * precio_imp
                costo_uni_inv_pn = ((inv_pn_value_ant * costo_uni_inv_pn_ant) + costo_com_pn - (consumo_pn[i] * costo_uni_inv_pn_ant)) / inv_pn_value
                costo_alm_pn = inv_pn_value * p_costo_alm
                
                costo_trans_pn = comp_imp_val * P_costo_trans
                costo_inv_pn = inv_pn_value * costo_uni_inv_pn
                costo_cap_pn = costo_inv_pn * ((1 + 0.12) ** (1 / 52) - 1)
                costo_uni_inv_pn_ant = costo_uni_inv_pn
                costo_total_pn = costo_com_pn + costo_cap_pn + costo_alm_pn + costo_trans_pn

                ListCostoCompra.append(costo_com_pn / 1000)
                ListCostoCapital.append(costo_cap_pn)
                ListCostoUnitario.append(costo_uni_inv_pn)
                ListCostoInventario.append(costo_inv_pn / 1000)
                ListCostoAlmacenamiento.append(costo_alm_pn)
                ListCostoTransporte.append(costo_trans_pn)
                ListCostoTotal.append(costo_total_pn)

            df_results = pd.DataFrame({
                "Compra Nacional": comp_nal_real_values,
                "Compra Importada": comp_imp_real_values,
                "Inventario": inv_pn_values,
                "CostoCompra": ListCostoCompra,
                "CostoUnitario": ListCostoUnitario,
                "CostoInv": ListCostoInventario,
                "CostoCapital": ListCostoCapital,
                "CostoAlm": ListCostoAlmacenamiento,
                "costoTrans": ListCostoTransporte,
                "Costo Total": ListCostoTotal
            })

            total_cost = sum(ListCostoTotal)
            g_mensaje = "Se optimizó correctamente"
            return df_results, total_cost, 1, g_mensaje

        except Exception as e:
            e_mensaje = "Hubo un error al optimizar el modelo. " + str(e)
            return None, None, -1, e_mensaje      
