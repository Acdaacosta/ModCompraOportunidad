# model.py
from gekko import GEKKO
import pandas as pd
import streamlit as st
class ModCompraModelo:
    def __init__(self):
        pass

    def optimizar(self,pN, pInv_min, pInv_max, pPrecio_nal, pPrecio_imp, pInv_ini, pCosto_uni_inv_ini, pConsumo_pn,p_Cap_compra_nal,p_Cap_compra_imp ):
        
     
        m = GEKKO(remote=False)

        # Parámetros
        n = pN
        inv_min = pInv_min
        inv_max = pInv_max
        precio_nal = pPrecio_nal
        precio_imp = pPrecio_imp
        inv_ini = pInv_ini
        costo_uni_inv_ini = pCosto_uni_inv_ini
        
        consumo_pn = pConsumo_pn.values.tolist()
        comp_nal_pn = m.Array(m.Var, n, lb=0, ub=p_Cap_compra_nal, integer=True)
        comp_imp_pn = m.Array(m.Var, n, lb=0, ub=p_Cap_compra_imp, integer=True)
        inv_pn = m.Array(m.Var, n + 1, lb=inv_min, ub=inv_max, integer=True)

        costo_com_pn = m.Array(m.Var, n)
        costo_uni_inv_pn = m.Array(m.Var, n)
        costo_inv_pn = m.Array(m.Var, n)
        costo_alm_pn = m.Array(m.Var, n)
        costo_trans_pn = m.Array(m.Var, n)
        costo_cap_pn = m.Array(m.Var, n)
        costo_total_pn = m.Array(m.Var, n)

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

        m.Obj(sum(costo_total_pn))
        m.solve(disp=False)

        comp_nal_pn_values = [round(value[0]) for value in comp_nal_pn]
        comp_imp_pn_values = [round(value[0]) for value in comp_imp_pn]
        costo_total_pn_values = []
        inv_pn_values = []  
        ListCompraNal = []  
        ListCompraImp = []  
        ListCostoCompra = []  
        ListCostoCapital = []  
        ListCostoAlmacenamiento = []  
        ListCostoTransporte = []  
        costo_uni_inv_pn_ant = costo_uni_inv_ini

        for i in range(n):
            costo_com_pn = comp_nal_pn_values[i] * precio_nal + comp_imp_pn_values[i] * precio_imp
            if i == 0:
                inv_pn_value_ant = inv_ini
                inv_pn_value = inv_ini + comp_nal_pn_values[i] + comp_imp_pn_values[i] - consumo_pn[0][i]        
            else:
                inv_pn_value_ant = inv_pn_values[i - 1]
                inv_pn_value = inv_pn_values[i - 1] + comp_nal_pn_values[i] + comp_imp_pn_values[i] - consumo_pn[0][i]

            costo_uni_inv_pn = ((inv_pn_value_ant * costo_uni_inv_pn_ant) + costo_com_pn - (consumo_pn[0][i] * costo_uni_inv_pn_ant)) / inv_pn_value        
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

        total_cost = sum(costo_total_pn_values)
        return df_results, total_cost, m.options.APPSTATUS
