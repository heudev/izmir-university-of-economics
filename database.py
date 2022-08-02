from peewee import SqliteDatabase, Model, AutoField, CharField, TextField

db = SqliteDatabase("data.db")


class BaseModel(Model):
    class Meta:
        database = db


class Ieu_sfl(BaseModel):
    id = AutoField()
    title = TextField(null=True)
    url = TextField(null=True)
    date = CharField(null=True)


class Ieu_announcement(BaseModel):
    id = AutoField()
    title = TextField(null=True)
    url = TextField(null=True)
    date = CharField(null=True)


class Ieu_news(BaseModel):
    id = AutoField()
    title = TextField(null=True)
    news = TextField(null=True)
    url = TextField(null=True)


db.connect()
db.create_tables([Ieu_sfl, Ieu_announcement, Ieu_news], safe=True)
