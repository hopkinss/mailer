import os

from peewee import Model, CharField, IntegerField, ForeignKeyField,fn
from playhouse.db_url import connect

db = connect(os.environ.get('DATABASE_URL', 'sqlite:///my_database.db'))

class Donor(Model):
    name = CharField(max_length=255, unique=True)

    class Meta:
        database = db

class Donation(Model):
    value = IntegerField()
    donor = ForeignKeyField(Donor, backref='donations')

    class Meta:
        database = db

def get_total():
    qry=(Donor.select(Donor.name ,fn.SUM(Donation.value).alias("total") )
          .join(Donation)
          .group_by(Donor.name))
    return qry

