#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models import db, User, Role

def simple_clear():
    """Простая очистка - удаляем всех пользователей кроме директора"""
    app = create_app()
    
    with app.app_context():
        print("Простая очистка базы данных...")
        
        try:
            # Получаем всех пользователей кроме директора
            users_to_delete = User.query.filter(User.username != 'director').all()
            
            for user in users_to_delete:
                print(f"Удаление пользователя: {user.username}")
                # Удаляем связи с ролями
                user.roles = []
                db.session.delete(user)
            
            db.session.commit()
            print("Очистка завершена!")
            print("Оставлен только директор: director / director123")
            
            # Проверяем результат
            remaining_users = User.query.all()
            print(f"Осталось пользователей: {len(remaining_users)}")
            for user in remaining_users:
                print(f"- {user.username} ({user.first_name} {user.last_name})")
                
        except Exception as e:
            print(f"Ошибка: {e}")
            db.session.rollback()

if __name__ == '__main__':
    simple_clear()



