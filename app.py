import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import sqlite3
import bcrypt
import qrcode
from datetime import datetime
from database import init_db, get_db

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}


# Função para verificar extensões de arquivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Inicializar banco de dados
init_db()


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Usuário ou senha inválidos!')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('login'))


# Rotas do Administrador
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    db = get_db()
    stats = {
        'total_students': db.execute('SELECT COUNT(*) FROM users WHERE role = "student"').fetchone()[0],
        'pending_payments': db.execute('SELECT COUNT(*) FROM payments WHERE receipt IS NULL').fetchone()[0],
        'messages': db.execute('SELECT COUNT(*) FROM messages WHERE receiver_id = ?', (session['user_id'],)).fetchone()[
            0]
    }
    return render_template('admin/dashboard.html', stats=stats)


@app.route('/admin/students', methods=['GET', 'POST'])
def manage_students():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        if 'add' in request.form:
            username = request.form['username']
            password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            address = request.form['address']
            city = request.form['city']
            try:
                weight = float(request.form['weight'])
                height = float(request.form['height'])
                if weight <= 0 or height <= 0:
                    raise ValueError("Peso e altura devem ser positivos.")
                imc = round(weight / (height * height), 2)
            except (ValueError, KeyError):
                flash('Peso e altura devem ser números válidos e positivos!')
                return redirect(url_for('manage_students'))
            db.execute(
                'INSERT INTO users (username, password, role, name, email, phone, address, city) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (username, password, 'student', name, email, phone, address, city))
            db.commit()
            student_id = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()['id']
            db.execute('INSERT INTO body_measurements (student_id, weight, height, imc) VALUES (?, ?, ?, ?)',
                       (student_id, weight, height, imc))
            db.commit()
            flash('Aluno cadastrado com sucesso!')
        elif 'edit' in request.form:
            user_id = request.form['user_id']
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            address = request.form['address']
            city = request.form['city']
            try:
                weight = float(request.form['weight'])
                height = float(request.form['height'])
                if weight <= 0 or height <= 0:
                    raise ValueError("Peso e altura devem ser positivos.")
                imc = round(weight / (height * height), 2)
            except (ValueError, KeyError):
                flash('Peso e altura devem ser números válidos e positivos!')
                return redirect(url_for('manage_students'))
            db.execute('UPDATE users SET name = ?, email = ?, phone = ?, address = ?, city = ? WHERE id = ?',
                       (name, email, phone, address, city, user_id))
            db.execute('INSERT INTO body_measurements (student_id, weight, height, imc) VALUES (?, ?, ?, ?)',
                       (user_id, weight, height, imc))
            db.commit()
            flash('Aluno atualizado com sucesso!')
        elif 'delete' in request.form:
            user_id = request.form['user_id']
            db.execute('DELETE FROM users WHERE id = ?', (user_id,))
            db.execute('DELETE FROM body_measurements WHERE student_id = ?', (user_id,))
            db.commit()
            flash('Aluno excluído com sucesso!')
    students = db.execute('''
        SELECT u.*, b.weight, b.height, b.imc
        FROM users u
        LEFT JOIN body_measurements b ON u.id = b.student_id
        WHERE u.role = "student"
        ORDER BY b.measured_at DESC LIMIT 1
    ''').fetchall()
    return render_template('admin/manage_students.html', students=students)


@app.route('/admin/workouts', methods=['GET', 'POST'])
def manage_workouts():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        if 'add' in request.form:
            student_id = request.form['student_id']
            description = request.form['description']
            days_of_week = ','.join(request.form.getlist('days_of_week'))
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.execute('INSERT INTO workouts (student_id, description, photo, days_of_week) VALUES (?, ?, ?, ?)',
                           (student_id, description, filename, days_of_week))
                db.commit()
                flash('Plano de treino cadastrado com sucesso!')
        elif 'edit_id' in request.form:
            workout_id = request.form['edit_id']
            description = request.form['description']
            days_of_week = ','.join(request.form.getlist('days_of_week'))
            file = request.files.get('photo')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.execute('UPDATE workouts SET description = ?, photo = ?, days_of_week = ? WHERE id = ?',
                           (description, filename, days_of_week, workout_id))
            else:
                db.execute('UPDATE workouts SET description = ?, days_of_week = ? WHERE id = ?',
                           (description, days_of_week, workout_id))
            db.commit()
            flash('Plano de treino atualizado com sucesso!')
        elif 'delete' in request.form:
            workout_id = request.form['delete']
            db.execute('DELETE FROM workouts WHERE id = ?', (workout_id,))
            db.commit()
            flash('Plano de treino excluído com sucesso!')
    students = db.execute('SELECT id, name FROM users WHERE role = "student"').fetchall()
    workouts = db.execute('SELECT w.*, u.name FROM workouts w JOIN users u ON w.student_id = u.id').fetchall()
    return render_template('admin/manage_workouts.html', workouts=workouts, students=students)


@app.route('/admin/payments', methods=['GET', 'POST'])
def manage_payments():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        if 'add' in request.form:
            student_id = request.form['student_id']
            amount = request.form['amount']
            due_date = request.form['due_date']
            pix_key = request.form['pix_key']
            qr = qrcode.QRCode()
            qr.add_data(pix_key)
            qr.make(fit=True)
            qr_filename = f"pix_{student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            qr.make_image(fill_color="black", back_color="white").save(
                os.path.join(app.config['UPLOAD_FOLDER'], qr_filename))
            db.execute('INSERT INTO payments (student_id, amount, due_date, pix_key, qr_code) VALUES (?, ?, ?, ?, ?)',
                       (student_id, amount, due_date, pix_key, qr_filename))
            db.commit()
            flash('Mensalidade cadastrada com sucesso!')
        elif 'edit_id' in request.form:
            payment_id = request.form['edit_id']
            amount = request.form['amount']
            due_date = request.form['due_date']
            pix_key = request.form['pix_key']
            qr = qrcode.QRCode()
            qr.add_data(pix_key)
            qr.make(fit=True)
            qr_filename = f"pix_{payment_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            qr.make_image(fill_color="black", back_color="white").save(
                os.path.join(app.config['UPLOAD_FOLDER'], qr_filename))
            db.execute('UPDATE payments SET amount = ?, due_date = ?, pix_key = ?, qr_code = ? WHERE id = ?',
                       (amount, due_date, pix_key, qr_filename, payment_id))
            db.commit()
            flash('Mensalidade atualizada com sucesso!')
        elif 'delete' in request.form:
            payment_id = request.form['delete']
            db.execute('DELETE FROM payments WHERE id = ?', (payment_id,))
            db.commit()
            flash('Mensalidade excluída com sucesso!')
    students = db.execute('SELECT id, name FROM users WHERE role = "student"').fetchall()
    payments = db.execute('SELECT p.*, u.name FROM payments p JOIN users u ON p.student_id = u.id').fetchall()
    return render_template('admin/manage_payments.html', payments=payments, students=students)


@app.route('/admin/messages', methods=['GET', 'POST'])
def admin_messages():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        student_id = request.form['student_id']
        content = request.form['content']
        db.execute('INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)',
                   (session['user_id'], student_id, content))
        db.commit()
        flash('Mensagem enviada com sucesso!')
    students = db.execute('SELECT id, name FROM users WHERE role = "student"').fetchall()
    messages = db.execute('''
        SELECT m.*, u.name AS sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.receiver_id = ? OR m.sender_id = ?
        ORDER BY m.timestamp DESC
    ''', (session['user_id'], session['user_id'])).fetchall()
    receipts = db.execute('''
        SELECT p.*, u.name AS student_name
        FROM payments p
        JOIN users u ON p.student_id = u.id
        WHERE p.receipt IS NOT NULL
        ORDER BY p.due_date DESC
    ''').fetchall()
    return render_template('admin/messages.html', messages=messages, students=students, receipts=receipts)


# Rotas do Aluno
@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    measurements = db.execute('SELECT * FROM body_measurements WHERE student_id = ? ORDER BY measured_at DESC LIMIT 1',
                              (session['user_id'],)).fetchone()
    return render_template('student/dashboard.html', user=user, measurements=measurements)


@app.route('/student/profile')
def student_profile():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template('student/profile.html', user=user)


@app.route('/student/workouts', methods=['GET', 'POST'])
def student_workouts():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    db = get_db()
    workouts = db.execute('SELECT * FROM workouts WHERE student_id = ?', (session['user_id'],)).fetchall()
    days_order = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    selected_day = request.form.get('selected_day') if request.method == 'POST' else request.args.get('selected_day')

    if selected_day and selected_day not in days_order and selected_day != 'Todos':
        selected_day = 'Todos'

    if selected_day and selected_day != 'Todos':
        filtered_workouts = [workout for workout in workouts if
                             workout['days_of_week'] and selected_day in workout['days_of_week'].split(',')]
        return render_template('student/workouts.html', workouts=filtered_workouts, days_order=days_order,
                               selected_day=selected_day)
    else:
        workouts_by_day = {day: [] for day in days_order}
        for workout in workouts:
            if workout['days_of_week']:
                days = workout['days_of_week'].split(',')
                for day in days:
                    if day in days_order:
                        workouts_by_day[day].append(workout)
        return render_template('student/workouts.html', workouts_by_day=workouts_by_day, days_order=days_order,
                               selected_day=selected_day or 'Todos')


@app.route('/student/payments', methods=['GET', 'POST'])
def student_payments():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        payment_id = request.form['payment_id']
        file = request.files.get('receipt')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.execute('UPDATE payments SET receipt = ? WHERE id = ? AND student_id = ?',
                       (filename, payment_id, session['user_id']))
            db.commit()
            flash('Comprovante enviado com sucesso!')
        else:
            flash('Arquivo inválido! Use PNG, JPG, JPEG ou PDF.')
    payments = db.execute('SELECT * FROM payments WHERE student_id = ?', (session['user_id'],)).fetchall()
    return render_template('student/payments.html', payments=payments)


@app.route('/student/messages', methods=['GET', 'POST'])
def student_messages():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        content = request.form['content']
        admin = db.execute('SELECT id FROM users WHERE role = "admin"').fetchone()
        db.execute('INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)',
                   (session['user_id'], admin['id'], content))
        db.commit()
        flash('Mensagem enviada com sucesso!')
    messages = db.execute(
        'SELECT m.*, u.name FROM messages m JOIN users u ON m.sender_id = u.id WHERE m.receiver_id = ? OR m.sender_id = ?',
        (session['user_id'], session['user_id'])).fetchall()
    return render_template('student/messages.html', messages=messages)


if __name__ == '__main__':
    app.run(debug=True)