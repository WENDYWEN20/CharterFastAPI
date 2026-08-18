import pytest
import warnings
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.core import Base
from src.entities.user import User
from src.entities.todo import Todo
from src.auth.models import TokenData
from src.auth.service import get_password_hash
from src.rate_limiter import limiter

@pytest.fixture(scope='function')
def db_session():
    SQLALCHEMY_DATABASE_URL = 'sqlite:///.test.db'
    engine=create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
    TestingSessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db=TestingSessionLocal()
    try: 
        yield db
    finally: 
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope='function')
def test_user():
    password_hash=get_password_hash('password123')
    return User(id=uuid4(), email='test@example.com', first_name='Test', last_name='User', password_hash=password_hash)
    