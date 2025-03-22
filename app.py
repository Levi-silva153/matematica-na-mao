from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
import os
from werkzeug.utils import secure_filename
from users import check_login

app = Flask(__name__)
app.secret_key = 'chave-super-secreta'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CATEGORIAS = {
    "Ensino Fundamental": ["1º Ano", "2º Ano", "3º Ano", "4º Ano", "5º Ano", "6º Ano", "7º Ano", "8º Ano", "9º Ano"],
    "Ensino Médio": ["1ª Série", "2ª Série", "3ª Série"],
    "Universitário": ["Cálculo", "Álgebra Linear", "Estatística", "Geometria Analítica"]
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    arquivos = {}
    for cat in CATEGORIAS:
        arquivos[cat] = {}
        for sub in CATEGORIAS[cat]:
            path = os.path.join(app.config['UPLOAD_FOLDER'], cat, sub)
            arquivos[cat][sub] = os.listdir(path) if os.path.exists(path) else []
    return render_template('index.html', categorias=CATEGORIAS, arquivos=arquivos)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        categoria = request.form['categoria']
        subcategoria = request.form['subcategoria']
        file = request.files['arquivo']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], categoria, subcategoria)
            os.makedirs(save_path, exist_ok=True)
            file.save(os.path.join(save_path, filename))
            flash('PDF enviado com sucesso!')
        return redirect(url_for('admin'))
    return render_template('admin.html', categorias=CATEGORIAS)

@app.route('/uploads/<categoria>/<subcategoria>/<nome>')
def baixar_pdf(categoria, subcategoria, nome):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], categoria, subcategoria), nome)

@app.route('/delete/<categoria>/<subcategoria>/<nome>')
def delete_pdf(categoria, subcategoria, nome):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    caminho = os.path.join(app.config['UPLOAD_FOLDER'], categoria, subcategoria, nome)
    if os.path.exists(caminho):
        os.remove(caminho)
        flash(f'{nome} removido.')
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if check_login(request.form['usuario'], request.form['senha']):
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Login inválido.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
