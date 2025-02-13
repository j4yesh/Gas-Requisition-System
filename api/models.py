from django.db import models
from .dbConnection import db
from cloudinary.models import CloudinaryField


UserCollection=db['User']
RequisitionCollection=db['Requisition']
