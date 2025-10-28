#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models import db, User

def fix_director_password():
    """Исправление пароля директора"""
    app = create_app()
    
    with app.app_context():
        print("Исправление пароля директора...")
        
        director = User.query.filter_by(username='director').first()
        if director:
            director.set_password('1234')
            db.session.commit()
            print("Пароль директора изменен на '1234'")
            print("Проверка: ", director.check_password('1234'))
        else:
            print("Директор не найден!")

if __name__ == '__main__':
    fix_director_password()



