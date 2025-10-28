#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models import db, User

def fix_all_passwords():
    """Исправление паролей для всех пользователей"""
    app = create_app()
    
    with app.app_context():
        print("Исправление паролей...")
        
        # Словарь пользователей и их паролей
        users_passwords = {
            'director': '1234',
            'a1': '123',
            'a2': '123', 
            'a3': '123',
            'a4': '123',
            'a5': '123'
        }
        
        for username, password in users_passwords.items():
            user = User.query.filter_by(username=username).first()
            if user:
                user.set_password(password)
                print(f"+ Пароль для {username} установлен")
            else:
                print(f"- Пользователь {username} не найден")
        
        db.session.commit()
        print("Все пароли исправлены!")

if __name__ == '__main__':
    fix_all_passwords()