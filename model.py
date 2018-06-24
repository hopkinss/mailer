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

class DonorView():
    def __init__(self,name):
        self.name=name
        self.donations=[]

    def append_donation(self,donations):
        self.donations="<br />".join(donations)


def get_donors():
    dlist=[]
    donors=Donor.select()

    for d in donors:
        donor=DonorView(d.name)
        vals=[]
        for v in d.donations:
            vals.append("$"+ str(v.value))

        donor.append_donation(vals)
        dlist.append(donor)
    return dlist

def get_donor_list():
    dlist=[]
    for v in Donor.select():
        dlist.append(v.name)

    return dlist

def get_donations_list(name):
    dlist = []
    donors = Donor.select()

    for d in donors.where(Donor.name==name):
        dlist.append(name)
        vals = []
        for v in d.donations:
            vals.append("$" + str(v.value))


        dlist.append(vals)
    return dlist
