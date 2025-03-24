#
# Este script é um servidor Flask que serve um exame de múltipla escolha.
# Ele carrega questões de um arquivo JSON e exibe uma questão por vez.
# O usuário pode responder a cada pergunta e ver o feedback imediatamente.
# No final, o usuário recebe uma pontuação e pode reiniciar o exame.
#
# Autor: Naldo Pinheiro
# Data: 2025-03-25
# Versão: 1.0
from flask import Flask, render_template, request, session, redirect, url_for
import json
import os
import random
import sys
from datetime import datetime
import tempfile
import pickle

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

def load_questions():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'questions.json')
        print(f"Tentando carregar arquivo: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as file:
            all_questions = json.load(file)['questions']
            print(f"Carregadas {len(all_questions)} questões com sucesso")
            
            # Embaralhar todas as questões
            random.shuffle(all_questions)
            
            # Armazenar apenas os IDs das questões na sessão
            return [(q['id'], q['exam_topic']) for q in all_questions], all_questions
    except Exception as e:
        print(f"Erro ao carregar questions.json: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def load_questions_from_file(file_content):
    try:
        data = json.loads(file_content)
        questions = data['questions']
        exam_description = data.get('exam_description', 'Exame de Múltipla Escolha')
        print(f"Carregadas {len(questions)} questões do arquivo enviado")
        return questions, exam_description
    except Exception as e:
        print(f"Erro ao carregar arquivo enviado: {str(e)}")
        return None, None

def get_question_by_id(questions, question_id):
    return next((q for q in questions if q['id'] == question_id), None)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Não executando com o servidor Werkzeug')
    func()

def save_questions_temp(questions):
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Criar arquivo temporário com ID único
    temp_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))
    temp_path = os.path.join(temp_dir, f'questions_{temp_id}.pkl')
    
    with open(temp_path, 'wb') as f:
        pickle.dump(questions, f)
    
    return temp_id

def load_questions_temp(temp_id):
    temp_path = os.path.join(os.path.dirname(__file__), 'temp', f'questions_{temp_id}.pkl')
    try:
        with open(temp_path, 'rb') as f:
            return pickle.load(f)
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    session.clear()
    if request.method == 'POST':
        if 'question_file' not in request.files:
            return "Nenhum arquivo selecionado", 400
        
        file = request.files['question_file']
        if file.filename == '':
            return "Nenhum arquivo selecionado", 400
        
        if not file.filename.endswith('.json'):
            return "Por favor, selecione um arquivo JSON", 400
        
        try:
            file_content = file.read().decode('utf-8')
            questions, exam_description = load_questions_from_file(file_content)
            
            if not questions:
                return "Erro ao processar arquivo. Verifique o formato.", 400
            
            # Salvar questões em arquivo temporário
            temp_id = save_questions_temp(questions)
            
            # Armazenar informações na sessão
            session['temp_id'] = temp_id
            session['current_index'] = 0
            session['score'] = 0
            session['total_questions'] = len(questions)
            session['exam_description'] = exam_description
            
            return redirect(url_for('quiz'))
        except Exception as e:
            print(f"Erro ao processar arquivo: {str(e)}")
            return "Erro ao processar arquivo", 500
    
    return render_template('index.html', year=datetime.now().year)

@app.route('/quiz')
def quiz():
    if 'temp_id' not in session:
        return redirect(url_for('index'))
    
    questions = load_questions_temp(session['temp_id'])
    if not questions:
        return redirect(url_for('index'))
    
    current_index = session.get('current_index', 0)
    
    if current_index >= len(questions):
        return redirect(url_for('result'))
    
    return render_template('quiz.html',
                         question=questions[current_index],
                         question_number=current_index + 1,
                         total_questions=len(questions),
                         exam_description=session.get('exam_description', 'Exame'),
                         year=datetime.now().year)

@app.route('/submit', methods=['POST'])
def submit():
    if 'temp_id' not in session:
        return redirect(url_for('index'))
    
    questions = load_questions_temp(session['temp_id'])
    if not questions:
        return redirect(url_for('index'))
    
    current_index = session.get('current_index', 0)
    current_question = questions[current_index]
    
    if current_question.get('multiple_answers', False):
        user_answers = request.form.getlist('answer')
        correct_answers = current_question['correct_answers']
        is_correct = set(user_answers) == set(correct_answers)
    else:
        user_answer = request.form.get('answer')
        correct_answer = current_question['correct_answer']
        is_correct = user_answer == correct_answer

    if is_correct:
        session['score'] = session.get('score', 0) + 1
    
    has_next = current_index + 1 < len(questions)
    return render_template('feedback.html',
                         question=current_question,
                         is_correct=is_correct,
                         has_next=has_next,
                         year=datetime.now().year)

@app.route('/next', methods=['POST'])
def next_question():
    if 'temp_id' not in session:  # Mudado de question_ids para temp_id
        return redirect(url_for('index'))
    
    questions = load_questions_temp(session['temp_id'])
    if not questions:
        return redirect(url_for('index'))
    
    current = session.get('current_index', 0)
    session['current_index'] = current + 1
    
    if current + 1 >= len(questions):  # Mudado de question_ids para questions
        return redirect(url_for('result'))
    
    return redirect(url_for('quiz'))

@app.route('/result')
def result():
    if 'temp_id' not in session:  # Mudado de question_ids para temp_id
        return redirect(url_for('index'))
    
    questions = load_questions_temp(session['temp_id'])
    if not questions:
        return redirect(url_for('index'))
    
    score = session.get('score', 0)
    total = len(questions)  # Usar questions diretamente
    return render_template('result.html', 
                         score=score, 
                         total=total, 
                         exam_description=session.get('exam_description', 'Exame'),
                         year=datetime.now().year)

@app.route('/finish')
def finish():
    session.clear()
    return render_template('confirm_exit.html', year=datetime.now().year)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    session.clear()
    try:
        response = render_template('goodbye.html', year=datetime.now().year)
        
        # Agendar o encerramento do servidor para depois da resposta
        def shutdown_after_request():
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                sys.exit(0)
            func()
            
        # Executar o shutdown em uma thread separada após 1 segundo
        import threading
        threading.Timer(1.0, shutdown_after_request).start()
        
        return response
    except Exception as e:
        print(f"Erro ao tentar encerrar: {str(e)}")
        return redirect(url_for('index'))

# Configurações adicionais do Flask
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Desabilitar cache

def cleanup_temp_files():
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    if os.path.exists(temp_dir):
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            # Remover arquivos mais antigos que 1 hora
            if os.path.getctime(file_path) < time.time() - 3600:
                os.remove(file_path)

if __name__ == '__main__':
    # Criar diretório temp se não existir
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    print("Iniciando o servidor Flask...")
    print(f"Diretório atual: {os.getcwd()}")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
