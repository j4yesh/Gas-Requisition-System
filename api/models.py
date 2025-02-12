from django.db import models
from .dbConnection import db

UserCollection=db['User']
RequisitionCollection=db['Requisition']