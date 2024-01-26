import typing
import config
import operator
from datetime import datetime
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_utils import database_exists, create_database

DATABASE_CONNECTION_URL = config.DATABASE_CONNECTION_URL

if not database_exists(DATABASE_CONNECTION_URL):
    create_database(DATABASE_CONNECTION_URL)

engine = sqlalchemy.create_engine(config.DATABASE_CONNECTION_URL)
session = sqlalchemy.orm.Session(bind=engine)

FILTER_QUERIES = {
    'in': operator.contains,
    'contains': operator.contains,
    'eq': operator.eq,
    'gt': operator.gt,
    'gte': operator.ge,
    'lte': operator.le,
    'lt': operator.lt,
    'is_not': operator.is_not,
    'and': operator.and_,
    'or': operator.or_,
    'index': operator.indexOf,
}


def get_current_time():
    return datetime.now()


class SqlAlchemyModel(DeclarativeBase):
    """
    Базовая модель СУБД проекта
    """

    id = sqlalchemy.Column(
        sqlalchemy.Integer(),
        primary_key=True,
        autoincrement=True
    )

    def __str__(self):
        instance_dict = self.__dict__.copy()
        instance_dict.pop('_sa_instance_state')

        return f'<{self.__class__.__name__}: {instance_dict}>'

    def __repr__(self):
        return self.__str__()

    @classmethod
    def filter_field(cls, key, value):
        default_filter_name = 'eq'

        if key.count('__') > 1:
            raise RuntimeError(
                'Указано больше параметров, чем нужно'
            )

        if '__' not in key:
            filter_name = default_filter_name
        else:
            filter_input = key.split('__')
            filter_name = filter_input[-1]
            key = filter_input[0]

        if filter_name not in FILTER_QUERIES:
            raise RuntimeError(
                f'Фильтра "__{filter_name}" не существует.'
            )

        filter_func = FILTER_QUERIES[filter_name]
        return filter_func(getattr(cls, key), value)

    @classmethod
    def convert_kwargs(cls, **kwargs):
        new_filters = []

        for key, value in kwargs.items():
            new_filters.append(
                cls.filter_field(key, value)
            )

        return new_filters

    @classmethod
    def fetch_one(cls, *filters: typing.Callable, **kwargs: [str, typing.Any]):
        kwargs_filters = cls.convert_kwargs(**kwargs)

        query = session.execute(
            sqlalchemy.select(cls).where(*filters, *kwargs_filters).limit(1)
        )

        response = query.first()
        if not response:
            return None

        return response[0]

    @classmethod
    def fetch_all(cls, *filters: typing.Callable, **kwargs: [str, typing.Any]):
        kwargs_filters = cls.convert_kwargs(**kwargs)

        query = session.execute(
            sqlalchemy.select(cls).where(*filters, *kwargs_filters)
        )

        result = query.fetchall()
        return [row[0] for row in result]

    @classmethod
    def create(cls, **kwargs):
        query = session.execute(
            sqlalchemy.insert(cls).values(**kwargs)
        )

        session.commit()
        return cls.fetch_one(id=query.lastrowid)

    @classmethod
    def delete(cls,  *filters: typing.Callable, **kwargs: [str, typing.Any]):
        kwargs_filters = cls.convert_kwargs(**kwargs)

        session.execute(
            sqlalchemy.delete(cls).where(*filters, *kwargs_filters)
        )

        return session.commit()

    @classmethod
    def update(cls, row_id: int, **kwargs):
        filter_query = cls.convert_kwargs(id=row_id)

        query = session.execute(
            sqlalchemy.update(cls).where(*filter_query).values(**kwargs)
        )

        session.commit()
        return cls.fetch_one(id=query.lastrowid)


class Note(SqlAlchemyModel):
    __tablename__ = 'notes'

    title = sqlalchemy.Column(
        sqlalchemy.VARCHAR(length=50),
        nullable=False
    )

    text = sqlalchemy.Column(
        sqlalchemy.TEXT(),
        nullable=False,
        default=18
    )

    created_at = sqlalchemy.Column(
        sqlalchemy.TIMESTAMP(),
        nullable=False,
        default=get_current_time
    )


SqlAlchemyModel.metadata.create_all(bind=engine)
