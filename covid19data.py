from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Date, DateTime, VARCHAR

engine = create_engine('sqlite:///covid19new.db', echo = True)

meta = MetaData()

Users = Table(
   'users', meta, 
   Column('user_id', Integer, primary_key = True), 
   Column('username', String), 
   Column('started_date', Date), 
   Column('last_check', Date), 
   Column('language', VARCHAR(3)), 
)

Stats = Table(
   'stats', meta, 
   Column('cases', Integer), 
   Column('todayCases', Integer), 
   Column('deaths', Integer), 
   Column('todayDeaths', Integer), 
   Column('recovered', Integer), 
   Column('todayRecovered', Integer), 
   Column('active', Integer), 
   Column('updated', DateTime), 
)

Countries = Table(
   'countries', meta, 
   Column('country', VARCHAR(20)), 
   Column('cases', Integer), 
   Column('todayCases', Integer), 
   Column('deaths', Integer), 
   Column('todayDeaths', Integer), 
   Column('recovered', Integer), 
   Column('todayRecovered', Integer), 
   Column('critical', Integer), 
   Column('active', Integer), 
   Column('casesPerOneMillion', Integer), 
   Column('tests', Integer), 
   Column('updated', DateTime), 
)

Users = Table(
   'notifications', meta, 
   Column('user_id', Integer), 
   Column('username', String), 
   Column('country', VARCHAR(20)), 
   Column('last_check', Date), 
   Column('added', DateTime),
)

meta.create_all(engine)