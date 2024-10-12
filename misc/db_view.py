import streamlit as st
import sqlite3
import pandas as pd


conn = sqlite3.connect(str(r".\misc\DB_Projeto01.db"))
cursor = conn.cursor()

cursor.execute("SELECT * FROM RegistrosEstufa")
data = cursor.fetchall()

df = pd.DataFrame(data, columns=['id', 'horadata', 'umidade', 'luminosidade'])

# Renomear as colunas se necessário
df.columns = ['ID', 'Data e Hora', 'Umidade (%)', 'Luminosidade (lx)']

st.title('Registros Terrario#01')
st.table(df)

conn.close()