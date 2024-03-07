import os
from flask import Flask, render_template, request, redirect, url_for
from joblib import load
import pandas as pd
import mysql.connector
 
mydb = mysql.connector.connect(
    host="35.247.214.14",
    user="root",
    password="Ma@080908",
    database="portfolio"
)
mycursor = mydb.cursor()
 
app = Flask(__name__)
pipeline = load('C:\\Users\\mendes\\estudosPython\\DATASCIENCE\\aprovado.joblib')
 
@app.route('/')
def login():
    return render_template('login.html')
 
@app.route('/index', methods=['POST'])
def index():
    return redirect(url_for('dados'))
 
@app.route('/dados', methods=['GET', 'POST'])
def dados():
    if request.method == 'POST':
        return redirect(url_for('resultado'))
 
    return render_template('index.html')
 
@app.route('/resultado', methods=['POST'])
def resultado():
    nome = request.form.get('NOME')
    idade = request.form.get('IDADE')
    empregado_anos = request.form.get('EMPREGADO A QUANTOS ANOS')
    profissao = request.form.get('PROFISSÃO')
    salario = request.form.get('SALÁRIO')
    estado_civil = request.form.get('ESTADO CIVIL')
    tem_filhos = request.form.get('TEM FILHOS')
    patrimonio = request.form.get('PATRIMÔNIO')
    nome_limpo = request.form.get('NOME LIMPO')
    valor_emprestimo = request.form.get('VALOR EMPRÉSTIMO')
    parcelas = int(request.form.get('parcelas'))
 
    if '' in [nome, empregado_anos, profissao, salario, estado_civil, tem_filhos, patrimonio, nome_limpo, valor_emprestimo]:
        return render_template('index.html', error_message="Por favor, preencha todos os campos.")
 
    if idade and idade.strip():
        idade = int(idade)
    else:
        idade = None
 
    nova_pessoa = {
        'NOME': nome,
        'IDADE': idade,
        'EMPREGADO A QUANTOS ANOS': int(empregado_anos),
        'PROFISSÃO': profissao,
        'SALÁRIO': float(salario),
        'ESTADO CIVIL': estado_civil,
        'TEM FILHOS': tem_filhos,
        'PATRIMÔNIO': float(patrimonio),
        'NOME LIMPO': nome_limpo,
        'VALOR EMPRÉSTIMO': float(valor_emprestimo)
    }
 
    if nova_pessoa['VALOR EMPRÉSTIMO'] > 3 * nova_pessoa['SALÁRIO']:
        resultado_modelo = "Empréstimo NÃO APROVADO (Valor do empréstimo excede 3 vezes o salário)"
        sql = "INSERT INTO todas_verificacoes (NOME, IDADE, EMPREGADO_ANOS, PROFISSAO, SALARIO, ESTADO_CIVIL, TEM_FILHOS, PATRIMONIO, NOME_LIMPO, VALOR_EMPRESTIMO, APROVADO) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (nova_pessoa['NOME'], nova_pessoa['IDADE'], nova_pessoa['EMPREGADO A QUANTOS ANOS'], nova_pessoa['PROFISSÃO'], nova_pessoa['SALÁRIO'], nova_pessoa['ESTADO CIVIL'], nova_pessoa['TEM FILHOS'], nova_pessoa['PATRIMÔNIO'], nova_pessoa['NOME LIMPO'], nova_pessoa['VALOR EMPRÉSTIMO'], 'NÃO')
        mycursor.execute(sql, val)
        mydb.commit()
        valor_total = None
        valor_parcela = None
 
    elif nova_pessoa['VALOR EMPRÉSTIMO'] > 1500000:
        resultado_modelo = "Empréstimo NÃO APROVADO (Valor muito alto)"
        sql = "INSERT INTO todas_verificacoes (NOME, IDADE, EMPREGADO_ANOS, PROFISSAO, SALARIO, ESTADO_CIVIL, TEM_FILHOS, PATRIMONIO, NOME_LIMPO, VALOR_EMPRESTIMO, APROVADO) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (nova_pessoa['NOME'], nova_pessoa['IDADE'], nova_pessoa['EMPREGADO A QUANTOS ANOS'], nova_pessoa['PROFISSÃO'], nova_pessoa['SALÁRIO'], nova_pessoa['ESTADO CIVIL'], nova_pessoa['TEM FILHOS'], nova_pessoa['PATRIMÔNIO'], nova_pessoa['NOME LIMPO'], nova_pessoa['VALOR EMPRÉSTIMO'], 'NÃO')
        mycursor.execute(sql, val)
        mydb.commit()
        valor_total = None
        valor_parcela = None
    else:
        aprovado = pipeline.predict(pd.DataFrame([nova_pessoa]))[0]
        if aprovado == 'SIM':
            resultado_modelo = "Empréstimo APROVADO"
            valor_total = nova_pessoa['VALOR EMPRÉSTIMO'] * (1 + 0.05 * parcelas)
            valor_parcela = valor_total / parcelas
            sql = "INSERT INTO todas_verificacoes (NOME, IDADE, EMPREGADO_ANOS, PROFISSAO, SALARIO, ESTADO_CIVIL, TEM_FILHOS, PATRIMONIO, NOME_LIMPO, VALOR_EMPRESTIMO, APROVADO) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (nova_pessoa['NOME'], nova_pessoa['IDADE'], nova_pessoa['EMPREGADO A QUANTOS ANOS'], nova_pessoa['PROFISSÃO'], nova_pessoa['SALÁRIO'], nova_pessoa['ESTADO CIVIL'], nova_pessoa['TEM FILHOS'], nova_pessoa['PATRIMÔNIO'], nova_pessoa['NOME LIMPO'], nova_pessoa['VALOR EMPRÉSTIMO'], 'SIM')
            mycursor.execute(sql, val)
            mydb.commit()
        else:
            resultado_modelo = "Empréstimo NÃO APROVADO"
            sql = "INSERT INTO todas_verificacoes (NOME, IDADE, EMPREGADO_ANOS, PROFISSAO, SALARIO, ESTADO_CIVIL, TEM_FILHOS, PATRIMONIO, NOME_LIMPO, VALOR_EMPRESTIMO, APROVADO) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (nova_pessoa['NOME'], nova_pessoa['IDADE'], nova_pessoa['EMPREGADO A QUANTOS ANOS'], nova_pessoa['PROFISSÃO'], nova_pessoa['SALÁRIO'], nova_pessoa['ESTADO CIVIL'], nova_pessoa['TEM FILHOS'], nova_pessoa['PATRIMÔNIO'], nova_pessoa['NOME LIMPO'], nova_pessoa['VALOR EMPRÉSTIMO'], 'NÃO')
            mycursor.execute(sql, val)
            mydb.commit()
            valor_total = None
            valor_parcela = None
               
 
    return render_template('resultado.html', resultado=resultado_modelo, valor_total=valor_total, valor_parcela=valor_parcela)
 
 
if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')