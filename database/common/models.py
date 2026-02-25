import datetime
import peewee as pw


db = pw.SqliteDatabase('history.db')


class ModelBase(pw.Model):
    """
    Базовый класс модели базы данных
    """
    created_at = pw.DateField(default=datetime.datetime.now)

    class Meta:
        """
        Класс модели будет использовать базу данных 'history.db'
        """
        database = db


class User(ModelBase):
    """
    Класс базы данных хранит информацию о пользователях

    : param user_id: int
        ID пользователя
    : param user_full_name: str
        имя пользователя
    : param user_date_time: str
        время и дата
    """
    user_id = pw.IntegerField(primary_key=True)
    user_full_name = pw.CharField(unique=True)
    user_date_time = pw.DateTimeField(default=datetime.datetime.now)


class Cities(ModelBase):
    """
    Класс базы данных собирает историю поиска городов

    : param user: str
        пользователь
    : param city_name: str
        название города
    : param city_id: int
        ID города
    """
    user = pw.ForeignKeyField(User, backref='cities')
    city_name = pw.TextField()
    city_id = pw.IntegerField()


class Hotels(ModelBase):
    """
    Класс базы данных собирает историю поиска отелей

    : param city_id: int
        ID города
    : param hotel_name: str
        название отеля
    : param distance_from_destination: int
        удаленность от центра города
    : param hotel_price: int
        стоимость отеля
    : param hotel_address_line: str
        адрес отеля
    : param hotel_images: list(url)
        фото отеля
    """
    city_id = pw.ForeignKeyField(Cities, backref='hotels')
    hotel_name = pw.TextField()
    distance_from_destination = pw.IntegerField()
    hotel_price = pw.IntegerField()
    hotel_address_line = pw.TextField()
    hotel_images = pw.CharField()


def create_tables():
    with db:
        db.create_tables([User, Cities, Hotels])
