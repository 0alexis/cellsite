from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import os
import threading
import time
import shutil
import webbrowser
import base64

# Ruta base absoluta del proyecto (evita problemas con cwd relativo)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'app.db')
UPLOADS_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['UPLOAD_FOLDER'] = UPLOADS_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-please-change')

# Inicializar la extensión sin forzar conexión hasta que el app context exista
db = SQLAlchemy(app)


def parse_currency(value):
    if value is None:
        return 0.0
    digits = ''.join(ch for ch in str(value) if ch.isdigit())
    return float(digits) if digits else 0.0


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(200))
    address = db.Column(db.String(300))
    notes = db.Column(db.Text)
    sales = db.relationship('Sale', backref='client', cascade='all, delete-orphan', order_by='Sale.date')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    imei = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(50))
    invoice_number = db.Column(db.String(100))
    model = db.Column(db.String(200))
    price = db.Column(db.Numeric(10,2))
    paid = db.Column(db.Boolean, default=False)  # Marca si el producto está completamente pagado


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    sale_price = db.Column(db.Numeric(10,2), nullable=False)
    date = db.Column(db.DateTime, server_default=db.func.now())
    initial_amount = db.Column(db.Numeric(10,2), nullable=False)
    balance = db.Column(db.Numeric(10,2), nullable=False)
    status = db.Column(db.String(30), default='activo')
    products = db.relationship('Product', backref='sale', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='sale', cascade='all, delete-orphan')


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    date = db.Column(db.DateTime, server_default=db.func.now())
    amount = db.Column(db.Numeric(10,2), nullable=False)
    method = db.Column(db.String(100))
    note = db.Column(db.String(300))


class Return(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    date = db.Column(db.DateTime, server_default=db.func.now())
    reason = db.Column(db.String(300))
    refund_amount = db.Column(db.Numeric(10,2), default=0)

# añadir relación desde Sale a Return
Sale.returns = db.relationship('Return', backref='sale', cascade='all, delete-orphan')


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200))
    company_phone = db.Column(db.String(50))
    company_email = db.Column(db.String(200))
    company_address = db.Column(db.String(300))
    logo_path = db.Column(db.String(300))  # ruta relativa a la imagen del logo


def init_db():
    os.makedirs('data', exist_ok=True)
    # Usar el contexto de la aplicación para operaciones de base de datos
    with app.app_context():
        db.create_all()
        if not Item.query.first():
            db.session.add(Item(name='Elemento de ejemplo'))
        # crear usuario por defecto si no existe
        if not User.query.first():
            admin = User(username='admin', password_hash=generate_password_hash('admin'))
            db.session.add(admin)
        # crear configuración por defecto si no existe
        if not Config.query.first():
            cfg = Config(company_name='Mi Empresa', company_phone='', company_email='', company_address='')
            db.session.add(cfg)
        db.session.commit()


@app.route('/')
def index():
    # Requiere login
    if not session.get('user'):
        return redirect(url_for('login'))
    # dashboard links
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user'] = user.username
            flash('Login exitoso.', 'success')
            return redirect(url_for('index'))
        flash('Usuario o contraseña incorrectos.', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# Clientes
@app.route('/clients')
def clients():
    if not session.get('user'):
        return redirect(url_for('login'))
    clients = Client.query.order_by(Client.name).all()
    clients_data = []
    for client in clients:
        sales = [s for s in client.sales if s.status != 'devuelto']
        net_balance = sum([float(s.balance) for s in sales]) if sales else 0.0
        if net_balance > 0:
            status = 'debe'
        elif net_balance < 0:
            status = 'saldo a favor'
        else:
            status = 'al dia'
        clients_data.append({
            'client': client,
            'status': status,
            'net_balance': net_balance
        })
    return render_template('clients.html', clients=clients_data)


@app.route('/clients/new', methods=['GET', 'POST'])
def new_client():
    if not session.get('user'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        c = Client(
            name=request.form.get('name'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            notes=request.form.get('notes')
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('clients'))
    return render_template('client_form.html')


@app.route('/clients/<int:client_id>')
def view_client(client_id):
    if not session.get('user'):
        return redirect(url_for('login'))
    client = Client.query.get_or_404(client_id)
    return render_template('client_view.html', client=client)


# Ventas
@app.route('/sales/new', methods=['GET', 'POST'])
def new_sale():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    clients = Client.query.order_by(Client.name).all()
    
    client_id = request.args.get('client_id') or request.form.get('client_id')
    client = None
    if client_id:
        try:
            client = Client.query.get(int(client_id))
        except (ValueError, TypeError):
            client = None
    
    if request.method == 'POST':
        # ensure client_id is provided and valid
        try:
            cid = int(request.form.get('client_id'))
        except (TypeError, ValueError):
            flash('Debes seleccionar un cliente.', 'error')
            return render_template('sale_form.html', clients=clients, client=None)
        
        # Obtener arrays de datos de productos
        imeis = request.form.getlist('imei[]')
        models = request.form.getlist('model[]')
        colors = request.form.getlist('color[]')
        invoices = request.form.getlist('invoice[]')
        prices = request.form.getlist('price[]')
        
        if not imeis or not any(imeis):
            flash('Debes agregar al menos un dispositivo.', 'error')
            return render_template('sale_form.html', clients=clients, client=client)
        
        # Calcular precio total
        total_price = 0
        for price_str in prices:
            total_price += parse_currency(price_str)

        initial = parse_currency(request.form.get('initial'))
        
        # Aplicar saldo a favor del cliente a la nueva venta
        credit_sales = Sale.query.filter(
            Sale.client_id == cid,
            Sale.balance < 0,
            Sale.status != 'devuelto'
        ).order_by(Sale.date.asc()).all()

        available_credit = sum([-float(s.balance) for s in credit_sales])
        due_amount = total_price - initial
        credit_applied = 0
        credit_applied_details = []
        if due_amount > 0 and available_credit > 0:
            credit_applied = min(available_credit, due_amount)
            due_amount -= credit_applied

        # Crear la venta
        sale = Sale(
            client_id=cid,
            sale_price=total_price,
            initial_amount=initial,
            balance=due_amount
        )
        if sale.balance < 0:
            sale.status = 'saldo a favor'
        elif sale.balance == 0:
            sale.status = 'pagada'
        db.session.add(sale)
        db.session.flush()
        
        # Crear productos asociados a esta venta
        for i, imei in enumerate(imeis):
            if imei:  # Solo crear si hay IMEI
                price_value = parse_currency(prices[i]) if i < len(prices) else 0
                
                product = Product(
                    sale_id=sale.id,
                    imei=imei,
                    color=colors[i] if i < len(colors) else '',
                    invoice_number=invoices[i] if i < len(invoices) else '',
                    model=models[i] if i < len(models) else '',
                    price=price_value
                )
                db.session.add(product)
        
        # Registrar pago por saldo a favor aplicado
        if credit_applied > 0:
            # Consumir el saldo a favor de ventas anteriores
            remaining_credit = credit_applied
            for credit_sale in credit_sales:
                if remaining_credit <= 0:
                    break
                sale_credit = -float(credit_sale.balance)
                consume = min(sale_credit, remaining_credit)
                credit_sale.balance = float(credit_sale.balance) + consume
                if credit_sale.balance == 0:
                    credit_sale.status = 'pagada'
                else:
                    credit_sale.status = 'saldo a favor'
                credit_applied_details.append({
                    'id': credit_sale.id,
                    'amount': consume
                })
                remaining_credit -= consume

            details_text = ''
            if credit_applied_details:
                detail_parts = [
                    f"venta #{d['id']} COP {d['amount']:,.0f}" for d in credit_applied_details
                ]
                details_text = ' | Origen: ' + '; '.join(detail_parts)

            pay_credit = Payment(
                sale_id=sale.id,
                amount=credit_applied,
                method='saldo a favor',
                note=f"Cruce de saldo a favor COP {credit_applied:,.0f}{details_text}"
            )
            db.session.add(pay_credit)

        db.session.commit()
        
        # si hubo pago inicial, crear payment
        if initial > 0:
            pay = Payment(sale_id=sale.id, amount=initial, method='inicial', note='Pago inicial')
            db.session.add(pay)
            db.session.commit()

        update_paid_products(sale)
        
        flash(f'Venta registrada con {len([i for i in imeis if i])} dispositivo(s).', 'success')
        return redirect(url_for('view_client', client_id=sale.client_id))
    
    return render_template('sale_form.html', client=client, clients=clients)


@app.route('/sales/<int:sale_id>')
def view_sale(sale_id):
    if not session.get('user'):
        return redirect(url_for('login'))
    sale = Sale.query.get_or_404(sale_id)
    return render_template('sale_view.html', sale=sale)


# Función auxiliar para actualizar productos pagados
def update_paid_products(sale):
    """Actualiza el estado 'paid' de los productos según cuánto se ha pagado de la venta"""
    total_paid = float(sale.sale_price) - float(sale.balance)
    
    # Ordenar productos por id (orden de creación)
    products = sorted(sale.products, key=lambda p: p.id)
    
    accumulated = 0.0
    for product in products:
        product_price = float(product.price)
        # Si el total pagado cubre este producto completamente
        if accumulated + product_price <= total_paid:
            product.paid = True
            accumulated += product_price
        else:
            product.paid = False
    
    db.session.commit()


# Pagos
@app.route('/payments/new', methods=['POST'])
def new_payment():
    if not session.get('user'):
        return redirect(url_for('login'))
    sale_id = int(request.form.get('sale_id'))
    amount = parse_currency(request.form.get('amount'))
    method = request.form.get('method')
    note = request.form.get('note')
    sale = Sale.query.get_or_404(sale_id)
    pay = Payment(sale_id=sale_id, amount=amount, method=method, note=note)
    sale.balance = float(sale.balance) - amount
    # Actualizar status según el balance
    if sale.balance < 0:
        extra = -float(sale.balance)
        sale.balance = 0
        sale.status = 'pagada'

        applied_details = []

        # Aplicar excedente a otras ventas pendientes del cliente
        pending_sales = Sale.query.filter(
            Sale.client_id == sale.client_id,
            Sale.id != sale.id,
            Sale.balance > 0,
            Sale.status != 'devuelto'
        ).order_by(Sale.date.asc()).all()

        remaining = extra
        for pending in pending_sales:
            if remaining <= 0:
                break
            pending_balance = float(pending.balance)
            apply_amount = min(remaining, pending_balance)
            pending.balance = pending_balance - apply_amount
            if pending.balance == 0:
                pending.status = 'pagada'
            else:
                pending.status = 'activo'
            extra_pay = Payment(
                sale_id=pending.id,
                amount=apply_amount,
                method=method or 'abono excedente',
                note=f"Abono excedente de venta #{sale.id}"
            )
            db.session.add(extra_pay)
            update_paid_products(pending)
            remaining -= apply_amount
            applied_details.append({
                'id': pending.id,
                'amount': apply_amount
            })

        # Si queda excedente sin deudas pendientes, mantener saldo a favor
        if remaining > 0:
            sale.balance = -remaining
            sale.status = 'saldo a favor'

        if applied_details or remaining > 0:
            detail_parts = []
            if applied_details:
                detail_parts.append('Aplicado a ' + '; '.join(
                    [f"venta #{d['id']} COP {d['amount']:,.0f}" for d in applied_details]
                ))
            if remaining > 0:
                detail_parts.append(f"Saldo a favor generado COP {remaining:,.0f}")
            extra_note = ' | '.join(detail_parts)
            if pay.note:
                pay.note = f"{pay.note} | {extra_note}"
            else:
                pay.note = extra_note
    elif sale.balance == 0:
        sale.status = 'pagada'
    else:
        sale.status = 'activo'
    db.session.add(pay)
    db.session.commit()
    
    # Actualizar productos pagados
    update_paid_products(sale)
    
    return redirect(url_for('view_sale', sale_id=sale_id))


# Abono automático - distribuye a ventas más antiguas
@app.route('/payments/auto', methods=['POST'])
def auto_payment():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    client_id = int(request.form.get('client_id'))
    amount = parse_currency(request.form.get('amount'))
    method = request.form.get('method')
    note = request.form.get('note')
    
    client = Client.query.get_or_404(client_id)
    
    # Obtener ventas con saldo pendiente (balance > 0), ordenadas por fecha más antigua primero
    pending_sales = Sale.query.filter(
        Sale.client_id == client_id,
        Sale.balance > 0,
        Sale.status != 'devuelto'
    ).order_by(Sale.date.asc()).all()
    
    if not pending_sales:
        flash('Este cliente no tiene ventas con saldo pendiente.', 'warning')
        return redirect(url_for('view_client', client_id=client_id))
    
    remaining_amount = amount
    sales_paid = []
    
    # Distribuir el abono a las ventas más antiguas
    for sale in pending_sales:
        if remaining_amount <= 0:
            break
        
        balance = float(sale.balance)
        
        # Determinar cuánto abonar a esta venta
        payment_amount = min(remaining_amount, balance)
        
        # Crear el pago
        pay = Payment(
            sale_id=sale.id,
            amount=payment_amount,
            method=method or 'abono automático',
            note=f"{note or 'Abono automático'} (distribuido de COP {amount:,.0f})"
        )
        db.session.add(pay)
        
        # Actualizar balance
        sale.balance = balance - payment_amount
        
        # Actualizar status según el balance
        if sale.balance < 0:
            sale.status = 'saldo a favor'
        elif sale.balance == 0:
            sale.status = 'pagada'
        else:
            sale.status = 'activo'
        
        remaining_amount -= payment_amount
        sales_paid.append({
            'id': sale.id,
            'amount': payment_amount,
            'balance': sale.balance
        })
        
        # Actualizar productos pagados de esta venta
        update_paid_products(sale)
    
    # Si sobra dinero, aplicarlo como saldo a favor en la venta más reciente
    if remaining_amount > 0 and pending_sales:
        last_sale = pending_sales[-1]
        extra_pay = Payment(
            sale_id=last_sale.id,
            amount=remaining_amount,
            method=method or 'abono automático',
            note=f"{note or 'Abono automático - saldo a favor'} (sobrante de COP {amount:,.0f})"
        )
        db.session.add(extra_pay)
        last_sale.balance = float(last_sale.balance) - remaining_amount
        last_sale.status = 'saldo a favor'
        sales_paid.append({
            'id': last_sale.id,
            'amount': remaining_amount,
            'balance': last_sale.balance
        })
    
    db.session.commit()
    
    flash(f'Abono de COP {amount:,.0f} distribuido automáticamente a {len(sales_paid)} venta(s).', 'success')
    return redirect(url_for('view_client', client_id=client_id))


# Devoluciones / Returns
@app.route('/sales/<int:sale_id>/return', methods=['POST'])
def process_return(sale_id):
    if not session.get('user'):
        return redirect(url_for('login'))
    sale = Sale.query.get_or_404(sale_id)
    # calcular total pagado
    total_paid = sum([float(p.amount) for p in sale.payments]) if sale.payments else 0.0
    reason = request.form.get('reason')
    # crear registro de devolución
    ret = Return(sale_id=sale.id, reason=reason, refund_amount=total_paid)
    sale.status = 'devuelto'
    sale.balance = 0
    db.session.add(ret)
    db.session.commit()
    return redirect(url_for('view_sale', sale_id=sale_id))


# Dashboard de ventas y caja
@app.route('/sales')
def sales_dashboard():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    # Obtener fecha seleccionada o usar hoy
    selected_date_str = request.args.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.now().date()
    else:
        selected_date = datetime.now().date()
    
    # Filtros de búsqueda
    search_query = request.args.get('search', '').strip()
    
    today = datetime.now().date()
    selected_start = datetime.combine(selected_date, datetime.min.time())
    selected_end = datetime.combine(selected_date, datetime.max.time())
    
    # Ventas del día seleccionado
    sales_selected_query = Sale.query.filter(
        Sale.date >= selected_start,
        Sale.date <= selected_end,
        Sale.status != 'devuelto'
    )
    if search_query:
        sales_selected_query = sales_selected_query.join(Client).outerjoin(Product).filter(
            db.or_(
                Client.name.ilike(f'%{search_query}%'),
                Client.email.ilike(f'%{search_query}%'),
                Client.phone.ilike(f'%{search_query}%'),
                Product.model.ilike(f'%{search_query}%'),
                Product.invoice_number.ilike(f'%{search_query}%'),
                Product.imei.ilike(f'%{search_query}%')
            )
        ).distinct()
    sales_selected = sales_selected_query.all()
    
    # Totales
    total_sales_selected = sum([float(s.sale_price) for s in sales_selected]) if sales_selected else 0.0
    phones_sold_selected = len(sales_selected)
    
    def classify_method(method_value):
        text = (method_value or '').lower()
        if 'efectivo' in text:
            return 'cash'
        transfer_keywords = ['transfer', 'nequi', 'daviplata', 'bancolombia', 'datafono']
        if any(k in text for k in transfer_keywords):
            return 'transfer'
        credit_keywords = ['credito', 'addi', 'banco bogota', 'bogota']
        if any(k in text for k in credit_keywords):
            return 'credit'
        return 'credit'

    # Totales por método
    cash_total = 0.0
    transfer_total = 0.0
    credit_total = 0.0
    for sale in sales_selected:
        # Distribuir pagos por método
        for payment in sale.payments:
            if payment.date >= selected_start and payment.date <= selected_end:
                amt = float(payment.amount)
                bucket = classify_method(payment.method)
                if bucket == 'cash':
                    cash_total += amt
                elif bucket == 'transfer':
                    transfer_total += amt
                else:
                    credit_total += amt
        
        # Si hay saldo pendiente (se considera crédito)
        balance = float(sale.balance)
        if balance > 0:
            credit_total += balance
    
    # Pagos realizados en el día seleccionado (aunque la venta sea de otro día)
    all_payments_selected = Payment.query.filter(
        Payment.date >= selected_start,
        Payment.date <= selected_end
    ).join(Sale).filter(Sale.status != 'devuelto').all()
    
    # Agrupar pagos por método
    cash_payments = [p for p in all_payments_selected if classify_method(p.method) == 'cash']
    transfer_payments = [p for p in all_payments_selected if classify_method(p.method) == 'transfer']
    credit_payments = [p for p in all_payments_selected if classify_method(p.method) == 'credit']
    
    cash_income = sum([float(p.amount) for p in cash_payments])
    transfer_income = sum([float(p.amount) for p in transfer_payments])
    credit_income = sum([float(p.amount) for p in credit_payments])
    
    # Calcular ingresos reales del día
    actual_income = sum([float(p.amount) for p in all_payments_selected]) if all_payments_selected else 0.0
    
    # Deudores (balance > 0) - ordenados por fecha más antigua (más atrasados primero)
    debtors_query = Sale.query.filter(Sale.balance > 0, Sale.status != 'devuelto')
    
    # Aplicar filtro de búsqueda
    if search_query:
        debtors_query = debtors_query.join(Client).outerjoin(Product).filter(
            db.or_(
                Client.name.ilike(f'%{search_query}%'),
                Client.email.ilike(f'%{search_query}%'),
                Client.phone.ilike(f'%{search_query}%'),
                Product.model.ilike(f'%{search_query}%'),
                Product.invoice_number.ilike(f'%{search_query}%'),
                Product.imei.ilike(f'%{search_query}%')
            )
        ).distinct()
    
    debtors = debtors_query.order_by(Sale.date.asc()).all()
    
    # Total de deuda de todos los usuarios
    total_debt_all = sum([float(s.balance) for s in debtors]) if debtors else 0.0
    
    # Alertas: ventas con más de 3 días sin ser pagadas
    three_days_ago = datetime.now() - timedelta(days=3)
    overdue = [s for s in debtors if s.date and s.date < three_days_ago]
    
    # Calcular días navegación
    prev_day = selected_date - timedelta(days=1)
    next_day = selected_date + timedelta(days=1)
    
    return render_template('sales_dashboard.html',
                          today=today,
                          selected_date=selected_date,
                          is_today=(selected_date == today),
                          prev_day=prev_day,
                          next_day=next_day,
                          now=datetime.now(),
                          sales_selected=sales_selected,
                          total_sales_today=total_sales_selected,
                          phones_sold_today=phones_sold_selected,
                          actual_income=actual_income,
                          cash_total=cash_total,
                          transfer_total=transfer_total,
                          credit_total=credit_total,
                          cash_income=cash_income,
                          transfer_income=transfer_income,
                          credit_income=credit_income,
                          cash_payments=cash_payments,
                          transfer_payments=transfer_payments,
                          credit_payments=credit_payments,
                          total_debt_all=total_debt_all,
                          debtors=debtors,
                          overdue=overdue,
                          search_query=search_query)


# Crear usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or len(username) < 3:
            flash('El usuario debe tener al menos 3 caracteres.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe.', 'error')
            return render_template('register.html')
        
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Usuario creado. Puedes iniciar sesión ahora.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


# Configuración
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    cfg = Config.query.first() or Config()
    
    if request.method == 'POST':
        cfg.company_name = request.form.get('company_name') or cfg.company_name
        cfg.company_phone = request.form.get('company_phone')
        cfg.company_email = request.form.get('company_email')
        cfg.company_address = request.form.get('company_address')
        
        # Manejar carga de logo
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and '.' in file.filename:
                filename = secure_filename(file.filename)
                os.makedirs(UPLOADS_DIR, exist_ok=True)
                filepath = os.path.join(UPLOADS_DIR, filename)
                file.save(filepath)
                cfg.logo_path = f'uploads/{filename}'
        
        db.session.add(cfg)
        db.session.commit()
        flash('Configuración actualizada.', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', config=cfg)


# Exportar Excel
@app.route('/export-excel')
def export_excel():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'Clientes'
    
    # Encabezado
    header_fill = PatternFill(start_color='2563EB', end_color='2563EB', fill_type='solid')
    header_font = Font(color='FFFFFF', bold=True)
    
    headers = ['ID', 'Nombre', 'Teléfono', 'Email', 'Dirección']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
    
    # Datos de clientes
    clients = Client.query.all()
    for row, client in enumerate(clients, 2):
        ws.cell(row=row, column=1, value=client.id)
        ws.cell(row=row, column=2, value=client.name)
        ws.cell(row=row, column=3, value=client.phone)
        ws.cell(row=row, column=4, value=client.email)
        ws.cell(row=row, column=5, value=client.address)
    
    # Ajustar ancho de columnas
    for col in range(1, 6):
        ws.column_dimensions[chr(64 + col)].width = 20
    
    # Crear segunda hoja para ventas
    ws_sales = wb.create_sheet('Ventas')
    headers_sales = ['ID', 'Cliente', 'IMEI', 'Precio', 'Saldo', 'Estado', 'Fecha']
    for col, header in enumerate(headers_sales, 1):
        cell = ws_sales.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
    
    sales = Sale.query.all()
    for row, sale in enumerate(sales, 2):
        ws_sales.cell(row=row, column=1, value=sale.id)
        ws_sales.cell(row=row, column=2, value=sale.client.name)
        # Concatenar IMEIs con estado de pago
        if sale.products:
            imeis = ', '.join([f"{'✓' if p.paid else '○'} {p.imei}" for p in sale.products])
        else:
            imeis = ''
        ws_sales.cell(row=row, column=3, value=imeis)
        # Precio y saldo: formato de número con separadores de miles
        price_cell = ws_sales.cell(row=row, column=4, value=int(sale.sale_price))
        price_cell.number_format = '#,##0'
        balance_cell = ws_sales.cell(row=row, column=5, value=int(sale.balance))
        balance_cell.number_format = '#,##0'
        ws_sales.cell(row=row, column=6, value=sale.status)
        ws_sales.cell(row=row, column=7, value=sale.date.strftime('%d/%m/%Y') if sale.date else '')
    
    for col in range(1, 8):
        ws_sales.column_dimensions[chr(64 + col)].width = 18
    
    # Enviar archivo
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'ventas_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )


# PDF de factura
@app.route('/invoice-pdf/<int:sale_id>')
def invoice_pdf(sale_id):
    if not session.get('user'):
        return redirect(url_for('login'))
    
    sale = Sale.query.get_or_404(sale_id)
    cfg = Config.query.first()
    
    # Crear PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*cm, bottomMargin=0.5*cm)
    story = []
    styles = getSampleStyleSheet()
    
    # Título y datos empresa
    if cfg:
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('0f172a'), spaceAfter=4)
        story.append(Paragraph(f"<b>{cfg.company_name}</b>", title_style))
        info_text = f"{cfg.company_phone} • {cfg.company_email}<br/>{cfg.company_address}"
        story.append(Paragraph(info_text, styles['Normal']))
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("<b>FACTURA DE VENTA / RECIBO DE PAGO</b>", styles['Heading2']))
    story.append(Spacer(1, 0.3*cm))
    
    # Datos de factura
    invoice_data = [
        ['Venta #', str(sale.id), 'Fecha:', sale.date.strftime('%d/%m/%Y %H:%M') if sale.date else ''],
        ['Cliente:', sale.client.name, 'Tel:', sale.client.phone or '—'],
        ['', '', 'Email:', sale.client.email or '—'],
    ]
    invoice_table = Table(invoice_data, colWidths=[2*cm, 4*cm, 2*cm, 4*cm])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(invoice_table)
    story.append(Spacer(1, 0.3*cm))
    
    # Datos de los celulares
    story.append(Paragraph("<b>Dispositivos vendidos:</b>", styles['Heading3']))
    if sale.products:
        for idx, product in enumerate(sale.products, 1):
            paid_status = '✓ PAGADO' if product.paid else '○ PENDIENTE'
            product_data = [
                [f'Dispositivo #{idx}', '', paid_status, ''],
                ['IMEI:', product.imei, 'Modelo:', product.model or '—'],
                ['Color:', product.color or '—', 'Factura:', product.invoice_number or '—'],
                ['Precio:', f"COP {float(product.price):,.0f}", '', ''],
            ]
            product_table = Table(product_data, colWidths=[2*cm, 4*cm, 2*cm, 4*cm])
            bg_color = colors.HexColor('e8f5e9') if product.paid else colors.HexColor('f0f0f0')
            product_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('BACKGROUND', (0, 0), (3, 0), bg_color),
                ('SPAN', (0, 0), (1, 0)),
                ('TEXTCOLOR', (2, 0), (2, 0), colors.HexColor('16a34a') if product.paid else colors.HexColor('757575')),
            ]))
            story.append(product_table)
            story.append(Spacer(1, 0.2*cm))
    story.append(Spacer(1, 0.1*cm))
    
    # Resumen financiero
    summary_data = [
        ['Concepto', 'Monto'],
        ['Precio de venta', f"COP {float(sale.sale_price):,.0f}"],
        ['Total pagado', f"COP {float(sale.sale_price) - float(sale.balance):,.0f}"],
        ['Saldo pendiente', f"COP {float(sale.balance):,.0f}"],
    ]
    summary_table = Table(summary_data, colWidths=[6*cm, 3*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('2563EB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Abonos
    story.append(Paragraph("<b>Abonos registrados:</b>", styles['Heading3']))
    if sale.payments:
        payments_data = [['Fecha', 'Monto', 'Método', 'Nota']]
        for p in sale.payments:
            payments_data.append([
                p.date.strftime('%d/%m/%Y') if p.date else '—',
                f"COP {float(p.amount):,.0f}",
                p.method or '—',
                p.note or '—'
            ])
        payments_table = Table(payments_data, colWidths=[2*cm, 2*cm, 2*cm, 4*cm])
        payments_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('e6edf3')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(payments_table)
    else:
        story.append(Paragraph("Sin abonos registrados.", styles['Normal']))
    
    # Compilar PDF
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'venta_{sale.id}.pdf'
    )


def open_browser():
    webbrowser.open('http://127.0.0.1:5000')


def start_backup_thread(interval_seconds=1800):
    def backup_loop():
        backup_path = os.path.join(DATA_DIR, 'app.db.backup')
        temp_path = backup_path + '.tmp'
        while True:
            try:
                os.makedirs(DATA_DIR, exist_ok=True)
                if os.path.exists(DB_PATH):
                    shutil.copy2(DB_PATH, temp_path)
                    os.replace(temp_path, backup_path)
            except Exception:
                pass
            time.sleep(interval_seconds)

    thread = threading.Thread(target=backup_loop, daemon=True)
    thread.start()


if __name__ == '__main__':
    init_db()
    # abrir navegador tras 1s para que el servidor arranque
    threading.Timer(1.0, open_browser).start()
    start_backup_thread(1800)
    app.run(host='127.0.0.1', port=5000)
