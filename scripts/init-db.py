#!/usr/bin/python3
import os
import sys

APP_FRENZY_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(APP_FRENZY_PATH)

from app_frenzy.db import engine
from app_frenzy.models import AppFrenzyBase


AppFrenzyBase.metadata.create_all(bind=engine)
