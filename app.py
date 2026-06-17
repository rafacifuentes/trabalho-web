from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def conectar():
    return sqlite3.connect('loja.db')

conn = conectar()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    descricao TEXT,
    preco REAL,
    estoque INTEGER
)
""")

conn.commit()
conn.close()


@app.route('/')
def index():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produtos")

    produtos = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        produtos=produtos
    )


@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():

    if request.method == 'POST':

        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        estoque = request.form['estoque']

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO produtos
        (nome, descricao, preco, estoque)
        VALUES (?, ?, ?, ?)
        """,
        (nome, descricao, preco, estoque))

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('cadastrar.html')


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):

    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':

        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        estoque = request.form['estoque']

        cursor.execute("""
        UPDATE produtos
        SET nome=?,
            descricao=?,
            preco=?,
            estoque=?
        WHERE id=?
        """,
        (nome, descricao, preco, estoque, id))

        conn.commit()
        conn.close()

        return redirect('/')

    cursor.execute(
        "SELECT * FROM produtos WHERE id=?",
        (id,)
    )

    produto = cursor.fetchone()

    conn.close()

    return render_template(
        'editar.html',
        produto=produto
    )


@app.route('/excluir/<int:id>')
def excluir(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM produtos WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/dashboard')
def dashboard():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(preco * estoque) FROM produtos")
    valor_total = cursor.fetchone()[0]

    if valor_total is None:
        valor_total = 0

    cursor.execute("""
    SELECT nome
    FROM produtos
    ORDER BY preco DESC
    LIMIT 1
    """)

    produto_caro = cursor.fetchone()

    if produto_caro:
        produto_caro = produto_caro[0]
    else:
        produto_caro = "Nenhum"

    cursor.execute("""
    SELECT nome
    FROM produtos
    ORDER BY preco ASC
    LIMIT 1
    """)

    produto_barato = cursor.fetchone()

    if produto_barato:
        produto_barato = produto_barato[0]
    else:
        produto_barato = "Nenhum"

    conn.close()

    return render_template(
        'dashboard.html',
        total_produtos=total_produtos,
        valor_total=valor_total,
        produto_caro=produto_caro,
        produto_barato=produto_barato
    )


if __name__ == '__main__':
    app.run(debug=True)