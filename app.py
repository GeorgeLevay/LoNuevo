from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import random
import json
from dotenv import load_dotenv
import hashlib
import pathlib
import requests

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///rifas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos de la base de datos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Raffle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_tickets = db.Column(db.Integer, nullable=False)
    available_tickets = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    raffle_id = db.Column(db.Integer, db.ForeignKey('raffle.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    payment_method = db.Column(db.String(50))
    
    # Datos del comprador
    buyer_name = db.Column(db.String(100), nullable=False)
    buyer_lastname = db.Column(db.String(100), nullable=False)
    buyer_cedula = db.Column(db.String(20), nullable=False)
    buyer_phone = db.Column(db.String(20), nullable=False)
    
    # Datos del pago
    bank_name = db.Column(db.String(100), nullable=False)
    reference_number = db.Column(db.String(50), nullable=False)
    
    # Números de boletos asignados
    assigned_tickets = db.Column(db.Text)  # JSON string con los números
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas principales
@app.route('/')
def index():
    active_raffles = Raffle.query.filter_by(is_active=True).all()
    return render_template('index.html', raffles=active_raffles)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

# Ruta de registro eliminada - solo administrador puede acceder

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))

@app.route('/raffle/<int:raffle_id>')
def raffle_detail(raffle_id):
    raffle = Raffle.query.get_or_404(raffle_id)
    return render_template('raffle_detail.html', raffle=raffle)

@app.route('/buy_tickets', methods=['POST'])
def buy_tickets():
    raffle_id = request.form.get('raffle_id')
    quantity = int(request.form.get('quantity'))
    
    raffle = Raffle.query.get_or_404(raffle_id)
    
    if quantity > raffle.available_tickets:
        flash('No hay suficientes boletos disponibles', 'error')
        return redirect(url_for('raffle_detail', raffle_id=raffle_id))
    
    total_amount = quantity * raffle.price
    
    # Obtener datos del formulario
    buyer_name = request.form.get('buyer_name')
    buyer_lastname = request.form.get('buyer_lastname')
    buyer_cedula = request.form.get('buyer_cedula')
    buyer_phone = request.form.get('buyer_phone')
    bank_name = request.form.get('bank_name')
    reference_number = request.form.get('reference_number')
    
    # Validar que todos los campos estén completos
    if not all([buyer_name, buyer_lastname, buyer_cedula, buyer_phone, bank_name, reference_number]):
        flash('Por favor complete todos los campos requeridos', 'error')
        return redirect(url_for('raffle_detail', raffle_id=raffle_id))
    
    purchase = Purchase(
        user_id=1,  # Usuario por defecto (admin)
        raffle_id=raffle_id,
        quantity=quantity,
        total_amount=total_amount,
        payment_method='transferencia',
        buyer_name=buyer_name,
        buyer_lastname=buyer_lastname,
        buyer_cedula=buyer_cedula,
        buyer_phone=buyer_phone,
        bank_name=bank_name,
        reference_number=reference_number
    )
    
    db.session.add(purchase)
    db.session.commit()
    
    flash('¡Solicitud de compra enviada exitosamente! El administrador revisará tu pago y te asignará los números de boletos.', 'success')
    return redirect(url_for('raffle_detail', raffle_id=raffle_id))

@app.route('/my_purchases')
@login_required
def my_purchases():
    # Solo administradores pueden ver compras
    if not current_user.is_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    purchases = Purchase.query.filter_by(user_id=current_user.id).order_by(Purchase.created_at.desc()).all()
    # Obtener información de rifas para cada compra
    for purchase in purchases:
        purchase.raffle = Raffle.query.get(purchase.raffle_id)
    return render_template('my_purchases.html', purchases=purchases)

# Rutas de administrador
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    total_raffles = Raffle.query.count()
    total_users = User.query.count()
    total_purchases = Purchase.query.count()
    pending_purchases = Purchase.query.filter_by(status='pending').count()
    
    recent_purchases = Purchase.query.order_by(Purchase.created_at.desc()).limit(10).all()
    # Obtener información de usuarios y rifas para cada compra
    for purchase in recent_purchases:
        purchase.user = User.query.get(purchase.user_id)
        purchase.raffle = Raffle.query.get(purchase.raffle_id)
    
    return render_template('admin/dashboard.html', 
                         total_raffles=total_raffles,
                         total_users=total_users,
                         total_purchases=total_purchases,
                         pending_purchases=pending_purchases,
                         recent_purchases=recent_purchases)

@app.route('/admin/purchases')
@login_required
def admin_purchases():
    if not current_user.is_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    # Listas separadas: pendientes y aprobadas (historial)
    pending_purchases = (
        Purchase.query.filter_by(status='pending')
        .order_by(Purchase.created_at.desc())
        .all()
    )
    approved_purchases = (
        Purchase.query.filter_by(status='approved')
        .order_by(Purchase.approved_at.desc())
        .all()
    )
    # Enriquecer con datos relacionados
    for purchase in pending_purchases + approved_purchases:
        purchase.user = User.query.get(purchase.user_id)
        purchase.raffle = Raffle.query.get(purchase.raffle_id)
    return render_template('admin/purchases.html', 
                           pending_purchases=pending_purchases,
                           approved_purchases=approved_purchases)

@app.route('/admin/approve_purchase/<int:purchase_id>')
@login_required
def approve_purchase(purchase_id):
    if not current_user.is_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    purchase = Purchase.query.get_or_404(purchase_id)
    raffle = Raffle.query.get(purchase.raffle_id)
    
    # Generar números aleatorios únicos para los boletos
    total_tickets = raffle.total_tickets
    sold_tickets = total_tickets - raffle.available_tickets
    
    # Obtener números ya asignados
    existing_tickets = []
    all_purchases = Purchase.query.filter_by(raffle_id=purchase.raffle_id, status='approved').all()
    for p in all_purchases:
        if p.assigned_tickets:
            existing_tickets.extend(json.loads(p.assigned_tickets))
    
    # Generar números únicos para esta compra
    available_numbers = [i for i in range(1, total_tickets + 1) if i not in existing_tickets]
    if len(available_numbers) < purchase.quantity:
        flash('No hay suficientes números disponibles', 'error')
        return redirect(url_for('admin_purchases'))
    
    assigned_numbers = random.sample(available_numbers, purchase.quantity)
    assigned_numbers.sort()  # Ordenar los números
    
    # Actualizar la compra
    purchase.status = 'approved'
    purchase.approved_at = datetime.utcnow()
    purchase.approved_by = current_user.id
    purchase.assigned_tickets = json.dumps(assigned_numbers)
    
    # Actualizar boletos disponibles
    raffle.available_tickets -= purchase.quantity
    
    db.session.commit()
    flash(f'Compra aprobada exitosamente. Números asignados: {", ".join(map(str, assigned_numbers))}', 'success')
    return redirect(url_for('admin_purchases'))

@app.route('/admin/reject_purchase/<int:purchase_id>')
@login_required
def reject_purchase(purchase_id):
    if not current_user.is_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    purchase = Purchase.query.get_or_404(purchase_id)
    purchase.status = 'rejected'
    purchase.approved_at = datetime.utcnow()
    purchase.approved_by = current_user.id
    
    db.session.commit()
    flash('Compra rechazada', 'info')
    return redirect(url_for('admin_purchases'))

@app.route('/admin/raffles')
@login_required
def admin_raffles():
    if not current_user.is_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    raffles = Raffle.query.order_by(Raffle.created_at.desc()).all()
    return render_template('admin/raffles.html', raffles=raffles)

@app.route('/admin/create_raffle', methods=['GET', 'POST'])
@login_required
def create_raffle():
    if not current_user.is_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        raffle = Raffle(
            title=request.form.get('title'),
            description=request.form.get('description'),
            price=float(request.form.get('price')),
            total_tickets=int(request.form.get('total_tickets')),
            available_tickets=int(request.form.get('total_tickets')),
            image_url=request.form.get('image_url', '').strip(),
            is_active=request.form.get('is_active') == 'on',
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        )
        db.session.add(raffle)
        db.session.commit()
        flash('Rifa creada exitosamente', 'success')
        return redirect(url_for('admin_raffles'))
    
    return render_template('admin/create_raffle.html')

@app.route('/admin/edit_raffle/<int:raffle_id>', methods=['GET', 'POST'])
@login_required
def edit_raffle(raffle_id):
    if not current_user.is_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    raffle = Raffle.query.get_or_404(raffle_id)
    
    if request.method == 'POST':
        raffle.title = request.form.get('title')
        raffle.description = request.form.get('description')
        raffle.price = float(request.form.get('price'))
        raffle.total_tickets = int(request.form.get('total_tickets'))
        raffle.image_url = request.form.get('image_url', '').strip()
        raffle.is_active = request.form.get('is_active') == 'on'
        raffle.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        
        db.session.commit()
        flash('Rifa actualizada exitosamente', 'success')
        return redirect(url_for('admin_raffles'))
    
    return render_template('admin/edit_raffle.html', raffle=raffle)

def ensure_database_initialized() -> None:
    """Create DB tables and ensure default admin exists.

    This runs at import time so it applies both in local (flask run/python)
    and in production under Gunicorn (Render/Docker).
    """
    with app.app_context():
        db.create_all()
        existing_admin = User.query.filter_by(username='Admin').first()
        if existing_admin is None:
            admin = User(
                username='Admin',
                email='admin@rifas.com',
                password_hash=generate_password_hash('11153920'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

# Ensure DB schema/admin are present when the app is imported by Gunicorn
ensure_database_initialized()

def _cache_dir() -> str:
    cache_dir = os.path.join(app.root_path, 'static', 'cache', 'raffles')
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

@app.route('/img/raffle/<int:raffle_id>')
def raffle_image(raffle_id: int):
    raffle = Raffle.query.get_or_404(raffle_id)
    if not raffle.image_url:
        # Fallback: servir un placeholder estático si existe
        placeholder = os.path.join(app.root_path, 'static', 'images', 'placeholder.png')
        if os.path.exists(placeholder):
            return send_file(placeholder)
        return ('', 404)

    # Generar nombre de archivo cacheado estable a partir de la URL
    url_bytes = raffle.image_url.encode('utf-8')
    file_hash = hashlib.sha256(url_bytes).hexdigest()[:24]
    suffix = pathlib.Path(raffle.image_url).suffix or '.img'
    cache_path = os.path.join(_cache_dir(), f'{raffle_id}-{file_hash}{suffix}')

    # Si ya está cacheado, servirlo
    if os.path.exists(cache_path):
        return send_file(cache_path)

    # Descargar con timeout corto y cabeceras simples
    try:
        resp = requests.get(raffle.image_url, timeout=6, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) RifaPy/1.0'
        })
        resp.raise_for_status()
        with open(cache_path, 'wb') as f:
            f.write(resp.content)
        return send_file(cache_path)
    except Exception:
        # Si falla, responder 404 para que el frontend muestre placeholder
        return ('', 404)

if __name__ == '__main__':
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()

        # Crear usuario administrador por defecto si no existe
        existing_admin = User.query.filter_by(username='Admin').first()
        if existing_admin is None:
            admin = User(
                username='Admin',
                email='admin@rifas.com',
                password_hash=generate_password_hash('11153920'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Administrador creado por defecto: Admin / 11153920")

    app.run(debug=True)