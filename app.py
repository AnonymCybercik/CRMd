from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_file, make_response, session
import uuid
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import (db, User, Role, Product, Order, ProductionTask, FinancialTransaction, InventoryItem, 
                   SupplierOrder, Notification, Company, Resource, ResourceRequest, CustomOrder, OrderItem,
                   SalaryPayment, PaymentMethod, Client, Contract, ExpenseCategory, Budget, InventoryTransaction,
                   QualityControl, MaintenanceRecord, Report)
from functools import wraps
import os, io, csv, random, string
from datetime import datetime, timedelta
from openpyxl import Workbook
from flask_migrate import Migrate

def create_app(config_name=None):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    # Загружаем конфигурацию
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    try:
        from config import config
        app.config.from_object(config[config_name])
    except ImportError:
        # Fallback к старой конфигурации
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-change-this-secret'
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///crm.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    def role_required(roles):
        if isinstance(roles, str):
            roles = [roles]
        def decorator(f):
            @wraps(f)
            @login_required
            def decorated_function(*args, **kwargs):
                if not any(current_user.has_role(r) for r in roles):
                    flash('У вас нет доступа к этой странице', 'danger')
                    return redirect(url_for('login'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.has_role('director'):
                return redirect(url_for('director_dashboard'))
            elif current_user.has_role('manager'):
                return redirect(url_for('manager_dashboard'))
            elif current_user.has_role('supplier'):
                return redirect(url_for('supplier_dashboard'))
            elif current_user.has_role('warehouse'):
                return redirect(url_for('warehouse_dashboard'))
            elif current_user.has_role('production'):
                return redirect(url_for('production_dashboard'))
            elif current_user.has_role('accountant'):
                return redirect(url_for('accountant_dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            
            print(f"Попытка входа: {username}")
            print(f"Пользователь найден: {user is not None}")
            if user:
                print(f"Проверка пароля: {user.check_password(password)}")
            
            if user and user.check_password(password):
                login_user(user)
                flash('Успешный вход в систему!', 'success')
                print(f"Успешный вход для пользователя: {username}")
                return redirect(url_for('index'))
            else:
                flash('Неверное имя пользователя или пароль', 'danger')
                print(f"Ошибка входа для пользователя: {username}")
        
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Вы вышли из системы', 'info')
        return redirect(url_for('login'))

    # Директор
    @app.route('/director')
    @role_required('director')
    def director_dashboard():
        # Получаем данные для директора
        users = User.query.all()
        
        # Финансовые данные
        income = FinancialTransaction.query.filter_by(transaction_type='income').with_entities(db.func.sum(FinancialTransaction.amount)).scalar() or 0
        expense = FinancialTransaction.query.filter_by(transaction_type='expense').with_entities(db.func.sum(FinancialTransaction.amount)).scalar() or 0
        profit = income - expense
        # Статистика заказов
        orders_by_status = type('obj', (object,), {
            'new': Order.query.filter_by(status='new').count(),
            'in_production': Order.query.filter_by(status='in_production').count(),
            'completed': Order.query.filter_by(status='completed').count(),
            'cancelled': Order.query.filter_by(status='cancelled').count()
        })()
        
        # Статистика задач
        tasks_by_status = type('obj', (object,), {
            'waiting': ProductionTask.query.filter_by(status='waiting').count(),
            'in_progress': ProductionTask.query.filter_by(status='in_progress').count(),
            'completed': ProductionTask.query.filter_by(status='completed').count()
        })()
        
        # Статистика запросов
        requests_by_status = type('obj', (object,), {
            'pending': ResourceRequest.query.filter_by(status='pending').count(),
            'approved': ResourceRequest.query.filter_by(status='approved').count(),
            'purchased': ResourceRequest.query.filter_by(status='purchased').count(),
            'delivered': ResourceRequest.query.filter_by(status='delivered').count()
        })()
        
        # Последние транзакции
        txs = FinancialTransaction.query.order_by(FinancialTransaction.created_at.desc()).limit(10).all()
        
        return render_template('director.html', 
                             users=users, income=income, expense=expense, profit=profit,
                             orders_by_status=orders_by_status, tasks_by_status=tasks_by_status,
                             requests_by_status=requests_by_status, txs=txs)

    @app.route('/director/company-settings')
    @role_required('director')
    def director_company_settings():
        return render_template('director_company_settings.html')

    # Менеджер
    @app.route('/manager', methods=['GET','POST', 'DELETE'])
    @role_required('manager')
    def manager_dashboard():

        # Получаем данные для менеджера
        orders = Order.query.all()
        users = User.query.all()
        products = Product.query.all()

        if request.method == "DELETE":
            order = Order.query.get(request.get_json().get('order_id'))
            db.session.delete(order)
            db.session.commit()
            
        if request.method == "POST":
            order_data = request.get_json()
            try: 
                d_date = datetime.strptime(order_data.get('delivery_date'), "%m/%d/%Y")
            except:
                d_date = None
            order_create = Order(
                    customer_name = order_data.get('customer_name'),
                    customer_phone = order_data.get('customer_phone'),
                    customer_email = order_data.get('customer_email'),
                    total_amount = int(order_data.get('total_amount')),
                    delivery_date = d_date,
                    order_date = datetime.now(),
                    notes = order_data.get('notes'),
                    user_id = current_user.id
                )
            
            db.session.add(order_create)
            db.session.commit()

            try:
                total_price = (int(order_data.get('unit_price')) * int(order_data.get('total_amount')))
                product_id = int(order_data.get('product_id'))
            except:
                total_price = 0
                product_id = None
            
            order_item = OrderItem(
                order_id = order_create.id,
                product_id = product_id,
                quantity = int(order_data.get('total_amount')) or None,
                unit_price = order_data.get('unit_price') or None,
                total_price = total_price,
            )

            db.session.add(order_item)
            db.session.commit()
        
        # Статистика заказов
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        completed_orders = Order.query.filter_by(status='completed').count()
        
        return render_template('manager.html', 
                             orders=orders, users=users,
                             total_orders=total_orders, pending_orders=pending_orders, 
                             completed_orders=completed_orders, products=products)

    # Поставщик
    @app.route('/supplier')
    @role_required('supplier')
    def supplier_dashboard():
        # Получаем данные для поставщика
        resources = Resource.query.all()
        requests = ResourceRequest.query.all()
        
        # Статистика запросов
        total_requests = ResourceRequest.query.count()
        pending_requests = ResourceRequest.query.filter_by(status='pending').count()
        approved_requests = ResourceRequest.query.filter_by(status='approved').count()
        delivered_requests = ResourceRequest.query.filter_by(status='delivered').count()
        
        return render_template('supplier.html', 
                             resources=resources, requests=requests,
                             total_requests=total_requests, pending_requests=pending_requests,
                             approved_requests=approved_requests, delivered_requests=delivered_requests)

    @app.route('/supplier/contracts')
    @role_required('supplier')
    def supplier_contracts():
        return render_template('supplier_contracts.html')

    @app.route('/supplier/quality-control')
    @role_required('supplier')
    def supplier_quality_control():
        return render_template('supplier_quality_control.html')

    @app.route('/supplier/emergency-orders')
    @role_required('supplier')
    def supplier_emergency_orders():
        return render_template('supplier_emergency_orders.html')

    @app.route('/supplier/budget-management')
    @role_required('supplier')
    def supplier_budget_management():
        return render_template('supplier_budget_management.html')

    @app.route('/supplier/recommendations')
    @role_required('supplier')
    def supplier_recommendations():
        return render_template('supplier_recommendations.html')

    @app.route('/supplier/reports')
    @role_required('supplier')
    def supplier_reports():
        return render_template('supplier_reports.html')

    # Склад
    @app.route('/warehouse')
    @role_required('warehouse')
    def warehouse_dashboard():
        # Получаем данные для склада
        inventory_items = InventoryItem.query.all()
        resources = Resource.query.all()
        
        # Статистика склада
        total_items = InventoryItem.query.count()
        low_stock_items = InventoryItem.query.filter(InventoryItem.quantity < InventoryItem.min_stock).count()
        out_of_stock_items = InventoryItem.query.filter_by(quantity=0).count()
        total_value = db.session.query(db.func.sum(InventoryItem.quantity * InventoryItem.price_per_unit)).scalar() or 0
        
        return render_template('warehouse.html', 
                             inventory_items=inventory_items, resources=resources,
                             total_items=total_items, low_stock_items=low_stock_items,
                             out_of_stock_items=out_of_stock_items, total_value=total_value)

    @app.route('/warehouse/stock-alerts')
    @role_required('warehouse')
    def warehouse_stock_alerts():
        return render_template('warehouse.html')

    @app.route('/warehouse/analytics')
    @role_required('warehouse')
    def warehouse_analytics():
        return render_template('warehouse.html')

    @app.route('/warehouse/supplier-performance')
    @role_required('warehouse')
    def warehouse_supplier_performance():
        return render_template('warehouse.html')

    @app.route('/warehouse/automated-reordering')
    @role_required('warehouse')
    def warehouse_automated_reordering():
        return render_template('warehouse_automated_reordering.html')

    @app.route('/warehouse/barcode-scanner')
    @role_required('warehouse')
    def warehouse_barcode_scanner():
        return render_template('warehouse_barcode_scanner.html')

    @app.route('/warehouse/cycle-counting')
    @role_required('warehouse')
    def warehouse_cycle_counting():
        return render_template('warehouse_cycle_counting.html')

    @app.route('/warehouse/expected-deliveries')
    @role_required('warehouse')
    def warehouse_expected_deliveries():
        return render_template('warehouse_expected_deliveries.html')

    @app.route('/warehouse/quality-inspection')
    @role_required('warehouse')
    def warehouse_quality_inspection():
        return render_template('warehouse_quality_inspection.html')

    @app.route('/warehouse/reports')
    @role_required('warehouse')
    def warehouse_reports():
        return render_template('warehouse_reports.html')

    @app.route('/warehouse/zones')
    @role_required('warehouse')
    def warehouse_zones():
        return render_template('warehouse_zones.html')

    # Производство
    @app.route('/production')
    @role_required('production')
    def production_dashboard():
        # Получаем данные для производства
        production_tasks = ProductionTask.query.all()
        orders = Order.query.all()
        users = User.query.all()
        
        # Статистика производства
        total_tasks = ProductionTask.query.count()
        active_tasks = ProductionTask.query.filter_by(status='in_progress').count()
        completed_tasks = ProductionTask.query.filter_by(status='completed').count()
        efficiency = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return render_template('production.html', 
                             production_tasks=production_tasks, orders=orders, users=users,
                             total_tasks=total_tasks, active_tasks=active_tasks,
                             completed_tasks=completed_tasks, efficiency=efficiency)

    @app.route('/production/planning')
    @role_required('production')
    def production_planning():
        return render_template('production_planning.html')

    @app.route('/production/equipment-management')
    @role_required('production')
    def production_equipment_management():
        return render_template('production_equipment_management.html')

    @app.route('/production/material-requirements')
    @role_required('production')
    def production_material_requirements():
        return render_template('production_material_requirements.html')

    @app.route('/production/check-materials')
    @role_required('production')
    def production_check_materials():
        return render_template('production_check_materials.html')

    @app.route('/production/worker-productivity')
    @role_required('production')
    def production_worker_productivity():
        return render_template('production_worker_productivity.html')

    @app.route('/production/safety-compliance')
    @role_required('production')
    def production_safety_compliance():
        return render_template('production_safety_compliance.html')

    @app.route('/production/reports')
    @role_required('production')
    def production_reports():
        return render_template('production_reports.html')

    # Бухгалтер
    @app.route('/accountant')
    @role_required('accountant')
    def accountant_dashboard():
        # Получаем данные для бухгалтера
        recent_transactions = FinancialTransaction.query.order_by(FinancialTransaction.created_at.desc()).limit(10).all()
        salary_payments = SalaryPayment.query.all()
        
        # Финансовые данные
        total_income = FinancialTransaction.query.filter_by(transaction_type='income').with_entities(db.func.sum(FinancialTransaction.amount)).scalar() or 0
        total_expense = FinancialTransaction.query.filter_by(transaction_type='expense').with_entities(db.func.sum(FinancialTransaction.amount)).scalar() or 0
        current_balance = total_income - total_expense
        
        # Ежемесячные данные
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_income = FinancialTransaction.query.filter(
            db.extract('month', FinancialTransaction.created_at) == current_month,
            db.extract('year', FinancialTransaction.created_at) == current_year,
            FinancialTransaction.transaction_type == 'income'
        ).with_entities(db.func.sum(FinancialTransaction.amount)).scalar() or 0
        
        monthly_expense = FinancialTransaction.query.filter(
            db.extract('month', FinancialTransaction.created_at) == current_month,
            db.extract('year', FinancialTransaction.created_at) == current_year,
            FinancialTransaction.transaction_type == 'expense'
        ).with_entities(db.func.sum(FinancialTransaction.amount)).scalar() or 0
        
        return render_template('accountant.html', 
                             recent_transactions=recent_transactions, salary_payments=salary_payments,
                             total_income=total_income, total_expense=total_expense, current_balance=current_balance,
                             monthly_income=monthly_income, monthly_expense=monthly_expense)

    @app.route('/accountant/invoice-management')
    @role_required('accountant')
    def accountant_invoice_management():
        return render_template('accountant_invoice_management.html')

    @app.route('/accountant/payroll-management')
    @role_required('accountant')
    def accountant_payroll_management():
        return render_template('accountant_payroll_management.html')

    @app.route('/accountant/tax-management')
    @role_required('accountant')
    def accountant_tax_management():
        return render_template('accountant_tax_management.html')

    @app.route('/accountant/budget-planning')
    @role_required('accountant')
    def accountant_budget_planning():
        return render_template('accountant_budget_planning.html')

    @app.route('/accountant/cash-flow')
    @role_required('accountant')
    def accountant_cash_flow():
        return render_template('accountant_cash_flow.html')

    @app.route('/accountant/financial-analysis')
    @role_required('accountant')
    def accountant_financial_analysis():
        return render_template('accountant_financial_analysis.html')

    @app.route('/accountant/asset-management')
    @role_required('accountant')
    def accountant_asset_management():
        return render_template('accountant_asset_management.html')

    @app.route('/accountant/expense-approval')
    @role_required('accountant')
    def accountant_expense_approval():
        return render_template('accountant_expense_approval.html')

    @app.route('/accountant/audit-trail')
    @role_required('accountant')
    def accountant_audit_trail():
        return render_template('accountant_audit_trail.html')

    @app.route('/accountant/compliance')
    @role_required('accountant')
    def accountant_compliance():
        return render_template('accountant_compliance.html')

    # Калькуляторы
    @app.route('/itp-calculator')
    @login_required
    def itp_calculator():
        return render_template('itp_calculator.html')

    @app.route('/gvs-calculator')
    @login_required
    def gvs_calculator():
        return render_template('gvs_calculator.html')

    # Центр аккаунта
    @app.route('/account')
    @login_required
    def account_center():
        
        users = User.query.all()
        roles = Role.query.all()
        return render_template('account_center.html', users=users, roles=roles)
    
    @app.route('/create-user', methods=['POST'])
    @login_required
    def create_user():
        
        if not current_user.has_role('director'):
            flash('У вас нет прав для добавления пользователей', 'danger')
            return redirect(url_for('account_center'))
        
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        role_name = request.form.get('role')
        
        if not all([username, email, password, first_name, last_name, role_name]):
            flash('Все поля обязательны для заполнения', 'danger')
            return redirect(url_for('account_center'))
        
        # Проверяем, не существует ли уже пользователь
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует', 'danger')
            return redirect(url_for('account_center'))
        
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'danger')
            return redirect(url_for('account_center'))
        
        # Создаем пользователя
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        user.set_password(password)
        
        # Находим роль
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            flash('Роль не найдена', 'danger')
            return redirect(url_for('account_center'))
        
        user.roles.append(role)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Пользователь {username} успешно создан', 'success')
        return redirect(url_for('account_center'))
    
    @app.route('/account/delete-user/<int:user_id>', methods=['POST'])
    @login_required
    def delete_user(user_id):
        if not current_user.has_role('director'):
            flash('У вас нет прав для удаления пользователей', 'danger')
            return redirect(url_for('account_center'))
        
        user = User.query.get_or_404(user_id)
        if user.id == current_user.id:
            flash('Нельзя удалить самого себя', 'danger')
            return redirect(url_for('account_center'))
        
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Пользователь {user.username} удален', 'success')
        return redirect(url_for('account_center'))
    
    @app.route('/account/reset-password/<int:user_id>', methods=['POST'])
    @login_required
    def reset_user_password(user_id):
        if not current_user.has_role('director'):
            flash('У вас нет прав для сброса паролей', 'danger')
            return redirect(url_for('account_center'))
        
        user = User.query.get_or_404(user_id)
        user.set_password('123')  # Сброс на стандартный пароль
        db.session.commit()
        
        flash(f'Пароль пользователя {user.username} сброшен на "123"', 'success')
        return redirect(url_for('account_center'))

    # API для работы с ресурсами
    @app.route('/api/resources', methods=['GET'])
    @login_required
    def get_resources():
        """Получение списка ресурсов"""
        resources = Resource.query.all()
        return jsonify([{
            'id': r.id,
            'name': r.name,
            'resource_type': r.resource_type,
            'quantity': r.quantity,
            'unit': r.unit,
            'cost_per_unit': r.cost_per_unit,
            'company_name': r.company.name if r.company else 'N/A',
            'company_id': r.company_id
        } for r in resources])

    @app.route('/api/resources', methods=['POST'])
    @role_required(['supplier', 'director'])
    def create_resource():
        """Создание нового ресурса"""
        data = request.get_json()
        
        resource = Resource(
            name=data['name'],
            resource_type=data.get('resource_type', 'material'),
            quantity=data.get('quantity', 0),
            unit=data.get('unit', 'шт'),
            cost_per_unit=data.get('cost_per_unit', 0.0),
            company_id=data['company_id']
        )
        
        db.session.add(resource)
        db.session.commit()
        
        return jsonify({'message': 'Ресурс создан успешно', 'id': resource.id}), 201

    @app.route('/api/resources/<int:resource_id>', methods=['PUT'])
    @role_required(['supplier', 'director'])
    def update_resource(resource_id):
        """Обновление ресурса"""
        resource = Resource.query.get_or_404(resource_id)
        data = request.get_json()
        
        resource.name = data.get('name', resource.name)
        resource.resource_type = data.get('resource_type', resource.resource_type)
        resource.quantity = data.get('quantity', resource.quantity)
        resource.unit = data.get('unit', resource.unit)
        resource.cost_per_unit = data.get('cost_per_unit', resource.cost_per_unit)
        resource.company_id = data.get('company_id', resource.company_id)
        
        db.session.commit()
        
        return jsonify({'message': 'Ресурс обновлен успешно'})

    @app.route('/api/resources/<int:resource_id>', methods=['DELETE'])
    @role_required(['supplier', 'director'])
    def delete_resource(resource_id):
        """Удаление ресурса"""
        resource = Resource.query.get_or_404(resource_id)
        db.session.delete(resource)
        db.session.commit()
        
        return jsonify({'message': 'Ресурс удален успешно'})

    @app.route('/api/resource-requests', methods=['GET'])
    @login_required
    def get_resource_requests():
        """Получение списка запросов на ресурсы"""
        requests = ResourceRequest.query.all()
        return jsonify([{
            'id': r.id,
            'resource_name': r.resource_name,
            'quantity': r.quantity,
            'priority': r.priority,
            'status': r.status,
            'requested_by': r.requested_by,
            'created_at': r.created_at.isoformat()
        } for r in requests])

    @app.route('/api/resource-requests', methods=['POST'])
    @login_required
    def create_resource_request():
        """Создание запроса на ресурс"""
        data = request.get_json()
        
        request_obj = ResourceRequest(
            resource_name=data['resource_name'],
            quantity=data['quantity'],
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'pending'),
            requested_by=current_user.username
        )
        
        db.session.add(request_obj)
        db.session.commit()
        
        return jsonify({'message': 'Запрос создан успешно', 'id': request_obj.id}), 201

    @app.route('/api/resource-requests/<int:request_id>/approve', methods=['POST'])
    @role_required(['supplier', 'director'])
    def approve_resource_request(request_id):
        """Одобрение запроса на ресурс"""
        request_obj = ResourceRequest.query.get_or_404(request_id)
        request_obj.status = 'approved'
        db.session.commit()
        
        return jsonify({'message': 'Запрос одобрен'})

    @app.route('/api/resource-requests/<int:request_id>/reject', methods=['POST'])
    @role_required(['supplier', 'director'])
    def reject_resource_request(request_id):
        """Отклонение запроса на ресурс"""
        request_obj = ResourceRequest.query.get_or_404(request_id)
        request_obj.status = 'rejected'
        db.session.commit()
        
        return jsonify({'message': 'Запрос отклонен'})

    @app.route('/api/companies', methods=['GET'])
    @login_required
    def get_companies():
        """Получение списка компаний"""
        companies = Company.query.all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'address': c.address,
            'phone': c.phone,
            'email': c.email
        } for c in companies])

    @app.route('/api/companies', methods=['POST'])
    @role_required(['supplier', 'director'])
    def create_company():
        """Создание новой компании"""
        data = request.get_json()
        
        company = Company(
            name=data['name'],
            address=data.get('address', ''),
            phone=data.get('phone', ''),
            email=data.get('email', '')
        )
        
        db.session.add(company)
        db.session.commit()
        
        return jsonify({'message': 'Компания создана успешно', 'id': company.id}), 201

    # Загрузка Excel файлов
    @app.route('/upload-excel', methods=['POST'])
    @role_required(['supplier', 'director'])
    def upload_excel():
        """Загрузка Excel файла с данными"""
        if 'file' not in request.files:
            return jsonify({'error': 'Файл не выбран'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Файл не выбран'}), 400
        
        if file and file.filename.endswith(('.xlsx', '.xls')):
            try:
                # Сохраняем файл
                filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Загружаем данные в зависимости от типа файла
                file_type = request.form.get('file_type', 'resources')
                
                if file_type == 'companies':
                    from load_excel_data import load_companies_from_excel
                    load_companies_from_excel(filepath)
                elif file_type == 'resources':
                    from load_excel_data import load_resources_from_excel
                    load_resources_from_excel(filepath)
                elif file_type == 'products':
                    from load_excel_data import load_products_from_excel
                    load_products_from_excel(filepath)
                
                # Удаляем временный файл
                os.remove(filepath)
                
                return jsonify({'message': 'Данные успешно загружены'})
                
            except Exception as e:
                return jsonify({'error': f'Ошибка при загрузке файла: {str(e)}'}), 500
        
        return jsonify({'error': 'Неподдерживаемый формат файла'}), 400

    @app.route('/change-password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        if request.method == 'POST':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            
            if not current_user.check_password(current_password):
                flash('Текущий пароль неверен', 'danger')
                return render_template('change_password.html')
            
            if new_password != confirm_password:
                flash('Новые пароли не совпадают', 'danger')
                return render_template('change_password.html')
            
            current_user.set_password(new_password)
            db.session.commit()
            flash('Пароль успешно изменен', 'success')
            return redirect(url_for('account_center'))
        
        return render_template('change_password.html')

    # Обработчики ошибок
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
