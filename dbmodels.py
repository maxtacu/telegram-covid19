from peewee import *
import config
import datetime

db = SqliteDatabase(config.DATABASE["filename"])

class BaseModel(Model):
    class Meta:
        database = db
        legacy_table_names=False

class User(BaseModel):
   class Meta:
      table_name = 'users'

   id = IntegerField(primary_key=True)
   username = TextField(default='noname')
   started_date = DateField()
   last_check = DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
   language = CharField(max_length=10, default='eng')


class GlobalStats(BaseModel):
   class Meta:
      table_name = 'global_stats'
   
   cases = IntegerField()
   todayCases = IntegerField()
   deaths = IntegerField()
   todayDeaths = IntegerField()
   recovered = IntegerField()
   todayRecovered = IntegerField()
   active = IntegerField()
   updated = DateTimeField()


class CountryStats(BaseModel):
   class Meta:
      table_name = 'countries_stats'
   
   country = CharField(max_length=25)
   cases = IntegerField()
   todayCases = IntegerField() 
   deaths = IntegerField()
   todayDeaths = IntegerField()
   recovered = IntegerField()
   todayRecovered = IntegerField() 
   critical = IntegerField()
   active = IntegerField()
   casesPerOneMillion = IntegerField() 
   deathsPerOneMillion = IntegerField() 
   tests = IntegerField()
   updated = DateTimeField()


class Notification(BaseModel):
   class Meta:
      table_name = 'notifications'

   user_id = ForeignKeyField(User, backref='notifs')
   username = TextField(default='noname')
   country = CharField(max_length=25)
   last_check = DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
   added = DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

db.connect()
db.create_tables([User, GlobalStats, CountryStats, Notification])