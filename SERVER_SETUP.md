# 🚀 НАСТРОЙКА НА СЕРВЕРЕ

## 📋 ПОСЛЕ ЗАГРУЗКИ ФАЙЛОВ:

### 1. ЗАМЕНИТЕ config.py
**На сервере замените содержимое `config.py` на содержимое `config_server.py`**

**Или вручную измените в config.py:**
```python
# Замените эту строку:
SQLALCHEMY_DATABASE_URI = 'sqlite:///crm.db'

# На эту:
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://teplores_teploresurscrm_user:KYm-yTb-mcn-eSH@localhost/teplores_teploresurscrm_db'
```

### 2. УСТАНОВИТЕ ЗАВИСИМОСТИ
```bash
pip install -r requirements.txt
```

### 3. ИНИЦИАЛИЗИРУЙТЕ БАЗУ ДАННЫХ
```bash
python init_db.py
python create_admin.py
```

### 4. ГОТОВО!
- **Логин:** director
- **Пароль:** director123

## 🎯 ЛОКАЛЬНОЕ ТЕСТИРОВАНИЕ:
**Сервер запущен на:** `http://localhost:5000`
**Логин:** director
**Пароль:** director123



