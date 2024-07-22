import pandas as pd
import numpy as np
import pyomo.environ as pyo

class ModCompraModelo:
    def __init__(self):
        pass

    def optimizar(self, pN, pInv_min, pInv_max, pPrecio_nal, pPrecio_imp, pInv_ini, pCosto_uni_inv_ini, pConsumo_pn, p_Cap_compra_nal, p_Cap_compra_imp,p_costo_alm,P_costo_trans):
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
            consumo_pn = pConsumo_pn.values.flatten().tolist()

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
            solver = pyo.SolverFactory('ipopt')  # Cambia el solver a ipopt

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

# Ejemplo de uso
if __name__ == "__main__":
    # Definir parámetros de ejemplo
    pN = 17
    pInv_min = 120000
    pInv_max = 1200000
    pPrecio_nal = 13200
    pPrecio_imp = 19078
    pInv_ini = 120000
    pCosto_uni_inv_ini = 10707
    P_costo_trans=187
    p_costo_alm=315
    pConsumo_pn = pd.DataFrame({
        'Periodo 1': [0], 'Periodo 2': [0], 'Periodo 3': [0], 'Periodo 4': [0],
        'Periodo 5': [0], 'Periodo 6': [0], 'Periodo 7': [0], 'Periodo 8': [0],
        'Periodo 9': [0], 'Periodo 10': [0], 'Periodo 11': [100000], 'Periodo 12': [100000],
        'Periodo 13': [100000], 'Periodo 14': [100000], 'Periodo 15': [100000], 'Periodo 16': [100000],
        'Periodo 17': [100000]
    })
    p_Cap_compra_nal = 40000
    p_Cap_compra_imp = 40000

    # Crear instancia del modelo
    modelo = ModCompraModelo()

    # Optimizar
    df_results, total_cost, status, message = modelo.optimizar(pN, pInv_min, pInv_max, pPrecio_nal, pPrecio_imp, pInv_ini, pCosto_uni_inv_ini, pConsumo_pn, p_Cap_compra_nal, p_Cap_compra_imp,p_costo_alm,P_costo_trans)

    # Mostrar resultados
    if status != -1:
        print("Resultados:")
        print(df_results[1:].applymap(lambda x: '{:,.0f}'.format(x).replace(',', '.') if isinstance(x, (int, float)) else x))
        print("Costo Total:", total_cost)
    else:
        print("Error:", message)
