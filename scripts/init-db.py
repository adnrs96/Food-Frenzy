#!/usr/bin/python3
import os
import sys
import logging

APP_FRENZY_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(APP_FRENZY_PATH)

from app_frenzy.db import engine
from app_frenzy.models import AppFrenzyBase


logging.info("Creating Database Tables.")
AppFrenzyBase.metadata.create_all(bind=engine)
logging.info("Creating Database Complete.")
