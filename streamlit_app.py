from ModCompraControlador import ModCompraControlador
#borrar
import streamlit as st
import pandas as pd
from ModCompraModelo import ModCompraModelo
def main():
    controlador=ModCompraControlador()
    controlador.main()

if __name__ == '__main__':
    main()

