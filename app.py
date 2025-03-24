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
        # Usar caminho absoluto para o arquivo JSON
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'questions.json')
        print(f"Tentando carregar arquivo: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)['questions']
    except Exception as e:
        print(f"Erro ao carregar questions.json: {str(e)}")
        return []

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Não executando com o servidor Werkzeug')
    func()

@app.route('/')
def index():
    session.clear()
    questions = load_questions()
    session['questions'] = questions
    session['current_question'] = 0
    session['score'] = 0
    return render_template('index.html', year=datetime.now().year)

@app.route('/quiz')
def quiz():
    if 'questions' not in session:
        return redirect(url_for('index'))
    
    questions = session['questions']
    current = session['current_question']
    
    if current >= len(questions):
        return redirect(url_for('result'))
    
    return render_template('quiz.html', 
                         question=questions[current],
                         question_number=current + 1,
                         total_questions=len(questions),
                         year=datetime.now().year)

@app.route('/submit', methods=['POST'])
def submit():
    if 'questions' not in session:
        return redirect(url_for('index'))
    
    questions = session['questions']
    current = session['current_question']
    
    # Armazenar a resposta do usuário e a correta para feedback
    if questions[current].get('multiple_answers', False):
        user_answers = request.form.getlist('answer')
        correct_answers = questions[current]['correct_answers']
        is_correct = set(user_answers) == set(correct_answers)
    else:
        user_answer = request.form.get('answer')
        correct_answer = questions[current]['correct_answer']
        is_correct = user_answer == correct_answer

    if is_correct:
        session['score'] = session.get('score', 0) + 1
    
    has_next = current + 1 < len(questions)
    return render_template('feedback.html', 
                         question=questions[current],
                         is_correct=is_correct,
                         has_next=has_next,
                         year=datetime.now().year)

@app.route('/next', methods=['POST'])
def next_question():
    if 'questions' not in session:
        return redirect(url_for('index'))
    
    current = session.get('current_question', 0)
    session['current_question'] = current + 1
    
    if current + 1 >= len(session['questions']):
        return redirect(url_for('result'))
    
    return redirect(url_for('quiz'))

@app.route('/result')
def result():
    if 'questions' not in session:
        return redirect(url_for('index'))
    
    score = session.get('score', 0)
    total = len(session['questions'])
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

if __name__ == '__main__':
    print("Iniciando o servidor Flask...")
    print(f"Diretório atual: {os.getcwd()}")
    app.run(debug=True, host='0.0.0.0', port=5000)
