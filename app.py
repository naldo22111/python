from flask import Flask, render_template, request, session, redirect, url_for
import json
import os
import random
import sys
from datetime import datetime

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

def get_question_by_id(questions, question_id):
    return next((q for q in questions if q['id'] == question_id), None)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Não executando com o servidor Werkzeug')
    func()

@app.route('/')
def index():
    session.clear()
    try:
        question_ids, all_questions = load_questions()
        if not question_ids:
            return "Erro ao carregar questões. Verifique o arquivo questions.json", 500
        
        # Armazenar apenas IDs e informações essenciais na sessão
        session['question_ids'] = question_ids
        session['current_index'] = 0
        session['score'] = 0
        session['total_questions'] = len(question_ids)
        
        return render_template('index.html', year=datetime.now().year)
    except Exception as e:
        print(f"Erro ao inicializar o exame: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Erro ao inicializar o exame", 500

@app.route('/quiz')
def quiz():
    if 'question_ids' not in session:
        return redirect(url_for('index'))
    
    current_index = session.get('current_index', 0)
    question_ids = session.get('question_ids', [])
    
    if current_index >= len(question_ids):
        return redirect(url_for('result'))
    
    # Carregar a questão atual do arquivo
    with open(os.path.join(os.path.dirname(__file__), 'questions.json'), 'r', encoding='utf-8') as file:
        all_questions = json.load(file)['questions']
        current_question = get_question_by_id(all_questions, question_ids[current_index][0])
    
    return render_template('quiz.html',
                         question=current_question,
                         question_number=current_index + 1,
                         total_questions=len(question_ids),
                         year=datetime.now().year)

@app.route('/submit', methods=['POST'])
def submit():
    if 'question_ids' not in session:
        return redirect(url_for('index'))
    
    current_index = session.get('current_index', 0)
    
    # Carregar a questão atual do arquivo
    with open(os.path.join(os.path.dirname(__file__), 'questions.json'), 'r', encoding='utf-8') as file:
        all_questions = json.load(file)['questions']
        current_question = get_question_by_id(all_questions, session['question_ids'][current_index][0])
    
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
    
    has_next = current_index + 1 < len(session['question_ids'])
    return render_template('feedback.html',
                         question=current_question,
                         is_correct=is_correct,
                         has_next=has_next,
                         year=datetime.now().year)

@app.route('/next', methods=['POST'])
def next_question():
    if 'question_ids' not in session:
        return redirect(url_for('index'))
    
    current = session.get('current_index', 0)
    session['current_index'] = current + 1
    
    if current + 1 >= len(session['question_ids']):
        return redirect(url_for('result'))
    
    return redirect(url_for('quiz'))

@app.route('/result')
def result():
    if 'question_ids' not in session:
        return redirect(url_for('index'))
    
    score = session.get('score', 0)
    total = len(session['question_ids'])
    return render_template('result.html', score=score, total=total, year=datetime.now().year)

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

if __name__ == '__main__':
    print("Iniciando o servidor Flask...")
    print(f"Diretório atual: {os.getcwd()}")
    # Aumentar o limite de tempo de resposta
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
