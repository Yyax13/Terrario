import os
import subprocess

def pip(package): #Essa def eu peguei de um projeto antigo meu (https://github.com/Yyax13/ypg/blob/main/misc/update.py) e serve para pré-instalar os requerimentos
    try:
        subprocess.check_output(["pip", "show", package])
        print(f'O pacote {package} já está instalado.')
    except subprocess.CalledProcessError:
        os.system(f'pip install {package}')
        print(f'O pacote {package} foi instalado.')