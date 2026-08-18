from fastapi import FastAPI
from .database.core import engine, Base
from .entities.todo import Todo
from fastapp.src.entities.user import User
from fastapp.src.api import register_routes
from .logging import configure_logging, LogLevels
configure_logging(LogLevels.info)
app=FastAPI()
register_routes(app)