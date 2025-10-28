# 🔧 ИСПРАВЛЕНИЕ ОШИБОК НА СЕРВЕРЕ

## ❌ ПРОБЛЕМА: ValueError: unsupported hash type scrypt

### 🎯 РЕШЕНИЕ:

#### 1. УСТАНОВИТЕ ПРАВИЛЬНЫЕ ЗАВИСИМОСТИ
```bash
pip install Werkzeug==2.3.7
pip install -r requirements.txt
```

#### 2. ИСПРАВЬТЕ ХЕШИРОВАНИЕ ПАРОЛЕЙ
```bash
python fix_passwords.py
```

#### 3. ПЕРЕЗАПУСТИТЕ ПРИЛОЖЕНИЕ
После исправления перезапустите Python приложение в панели управления.

## 📋 ПОШАГОВО:

1. **Загрузите** `CRM_FINAL_FIXED.zip` на сервер
2. **Распакуйте** файлы
3. **Замените** `config.py` на `config_server.py`
4. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Инициализируйте базу данных:**
   ```bash
   python init_db.py
   python create_admin.py
   ```
6. **Исправьте пароли:**
   ```bash
   python fix_passwords.py
   ```
7. **Перезапустите** приложение

## ✅ РЕЗУЛЬТАТ:
- **Логин:** director
- **Пароль:** director123
- **Все роли работают** без ошибок

## 🎯 ГОТОВО К РАБОТЕ!



