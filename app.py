from flask import Flask, request, session, redirect, url_for
import os

# Use a stable secret key from environment in production
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-for-local")
app = Flask(__name__)
app.secret_key = SECRET_KEY

# ====== DATA STORAGE ======
questions = [
    "What is a programming language?",
    "Which of the following is a programming language?",
    "What is the main purpose of writing a program?",
    "In programming, what is a variable?",
    "What does 'print' do in most programming languages?"
]

options = [
    ["A. A type of computer hardware", "B. A way to communicate with a computer using code", "C. A social media app", "D. A computer virus"],
    ["A. HTML", "B. Python", "C. Google", "D. Excel"],
    ["A. To decorate a website", "B. To make the computer perform tasks", "C. To play music", "D. To design posters"],
    ["A. A type of food", "B. A storage location for data", "C. A computer virus", "D. A network device"],
    ["A. Sends data to a printer", "B. Displays output on the screen", "C. Shuts down the computer", "D. Deletes data"]
]

answers = ["B", "B", "B", "B", "B"]

# Student score records (temporary in memory)
student_scores = []

# Admin credentials (use env var in production)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secure123")

# ====== HTML UI STYLES ======
CSS = """
<style>
body {
  font-family: 'Poppins', sans-serif;
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  text-align: center;
  color: #222;
  margin: 0; padding: 0;
}
.container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  padding: 30px;
  width: 80%;
  max-width: 600px;
  margin: 50px auto;
}
button {
  background-color: #4CAF50;
  border: none;
  color: white;
  padding: 10px 20px;
  text-align: center;
  border-radius: 10px;
  font-size: 16px;
  cursor: pointer;
}
button:hover { background-color: #45a049; }
input[type=text], input[type=password] {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
  width: 80%;
}
a { color: #4CAF50; text-decoration: none; }
a:hover { text-decoration: underline; }
table { margin: 0 auto; }
</style>
"""

# ====== HELPER HTML ======
def layout(title, body):
    return f"<html><head><title>{title}</title>{CSS}</head><body><div class='container'>{body}</div></body></html>"

# ====== ROUTES ======
@app.route('/')
def home():
    session.clear()
    qcount = len(questions)
    html = f"""
    <h2>Welcome to the Programming Quiz</h2>
    <p>There are <b>{qcount}</b> questions in this quiz.</p>
    <form action="/start" method="POST">
      <input type="text" name="student_name" placeholder="Enter your name" required><br><br>
      <button type="submit">Start Quiz</button>
    </form>
    <br><a href="/admin">Admin Login</a>
    """
    return layout("Quiz Home", html)

@app.route('/start', methods=['POST'])
def start_quiz():
    name = request.form.get('student_name', '').strip()
    if not name:
        return layout("Error", "<p>Please enter your name.</p><a href='/'>Back</a>")
    session['student_name'] = name
    session['current_question'] = 0
    session['score'] = 0
    return redirect(url_for('quiz'))

@app.route('/quiz')
def quiz():
    current_q = session.get('current_question', 0)
    if current_q >= len(questions):
        return redirect(url_for('results'))

    question = questions[current_q]
    opts = options[current_q]
    html = f"""
    <h3>Question {current_q + 1} of {len(questions)}</h3>
    <p><b>{question}</b></p>
    <form method="POST" action="/submit">
    {"".join([f"<label><input type='radio' name='answer' value='{chr(65+i)}'> {opt}</label><br>" for i,opt in enumerate(opts)])}
    <br><button type="submit">Submit Answer</button>
    </form>
    """
    return layout(f"Question {current_q + 1}", html)

@app.route('/submit', methods=['POST'])
def submit_answer():
    answer = request.form.get('answer', '').upper()
    current_q = session.get('current_question', 0)

    if answer and current_q < len(questions):
        if answer == answers[current_q]:
            session['score'] = session.get('score', 0) + 1
        session['current_question'] = current_q + 1

    return redirect(url_for('quiz'))

@app.route('/results')
def results():
    name = session.get('student_name', 'Unknown')
    score = session.get('score', 0)
    percent = int(score / len(questions) * 100)
    # save record
    student_scores.append({'name': name, 'score': percent})
    html = f"""
    <h2>Quiz Completed!</h2>
    <p><b>{name}</b>, your score is <b>{percent}%</b> ({score}/{len(questions)} correct)</p>
    <a href="/">Back to Home</a>
    """
    return layout("Results", html)

# ====== ADMIN SECTION ======
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        return layout("Admin Login", "<p>Invalid credentials.</p><a href='/admin'>Try again</a>")
    html = """
    <h2>Admin Login</h2>
    <form method="POST">
      <input type="text" name="username" placeholder="Username" required><br><br>
      <input type="password" name="password" placeholder="Password" required><br><br>
      <button type="submit">Login</button>
    </form>
    """
    return layout("Admin Login", html)

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    # Student records table
    students_html = ""
    if student_scores:
        students_html = "<table border='1' cellpadding='6' style='margin:auto;'><tr><th>Student Name</th><th>Score (%)</th></tr>"
        for s in student_scores:
            students_html += f"<tr><td>{s['name']}</td><td>{s['score']}</td></tr>"
        students_html += "</table>"
    else:
        students_html = "<p>No quiz attempts yet.</p>"
    
    html = f"""
    <h2>Admin Panel</h2>
    <p>Welcome, {ADMIN_USERNAME}</p>
    <h3>Quiz Questions ({len(questions)} total)</h3>
    <ul>
    {''.join([f"<li><b>{i+1}.</b> {q} <br><i>Answer: {answers[i]}</i></li>" for i,q in enumerate(questions)])}
    </ul>
    <a href="/admin/add">Add Question</a><br><br>
    <h3>Student Scores</h3>
    {students_html}
    <br><a href="/admin/logout">Logout</a>
    """
    return layout("Admin Panel", html)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_question():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        q = request.form.get('question', '').strip()
        opts = [request.form.get(f'option{i}', '').strip() for i in range(4)]
        ans = request.form.get('answer', '').strip().upper()
        if not q or any(not o for o in opts) or ans not in ['A','B','C','D']:
            return layout("Error", "<p>All fields are required and answer must be A-D.</p><a href='/admin/add'>Back</a>")
        questions.append(q)
        options.append(opts)
        answers.append(ans)
        return redirect(url_for('admin_panel'))
    html = """
    <h2>Add New Question</h2>
    <form method="POST">
      <input type="text" name="question" placeholder="Question text" required><br><br>
      <input type="text" name="option0" placeholder="Option A" required><br>
      <input type="text" name="option1" placeholder="Option B" required><br>
      <input type="text" name="option2" placeholder="Option C" required><br>
      <input type="text" name="option3" placeholder="Option D" required><br><br>
      <input type="text" name="answer" placeholder="Correct Answer (A/B/C/D)" required><br><br>
      <button type="submit">Add Question</button>
    </form>
    <br><a href="/admin/panel">Back</a>
    """
    return layout("Add Question", html)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

# ====== RUN for local testing ======
if __name__ == '__main__':
    # local-only server settings for development
    port = int(os.environ.get('PORT', 5000))
    # bind to 127.0.0.1 for local dev; hosted platforms will run via gunicorn
    app.run(host='127.0.0.1', port=port, debug=False)
