#pip install requests
import requests
import json

dados = requests.get('http://127.0.0.1:5000/listarpessoas/externoSemlogin')

print(dados.text)