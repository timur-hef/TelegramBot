import logging
import sqlalchemy as sa

from functools import wraps

from auth import DATABASE
from sqlalchemy.orm import declarative_base, Session, sessionmaker

logger = logging.getLogger('utils')

Base = declarative_base()


def init_db():
    global engine, Session    
    
    engine = sa.create_engine(DATABASE)  # change to localhost
    Session = sessionmaker(engine)
    Base.metadata.create_all(engine)


def provide_session(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        s = Session()
        func(*args, **kwargs, session=s)
        s.commit()
        s.close()

    return wrapper


class User(Base):
    __tablename__ = 'user_info'

    id = sa.Column(sa.Integer, primary_key=True)
    location = sa.Column(sa.String(100))
    horo_sign = sa.Column(sa.String(20))

    def __repr__(self):
        return f"User(id={self.id}, location={self.location}, horo_sign={self.horo_sign})"


@provide_session
def update_user(user_id, session=None, location=None, horo=None):
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        user = User(id=user_id, location=location, horo_sign=horo)
        logger.info(f'Пользователь ({user_id}) успешно добавлен')
        return

    user.location = location if location else user.location
    user.horo_sign = horo if horo else user.horo_sign

    session.merge(user)
    logger.info(f'Информация пользователя ({user_id}) успешно обновлена')

    return


@provide_session
def delete_user(user_id, session=None):
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        logger.error(f'Не удалось найти юзера id = {user_id}')
    else:
        session.delete(user)
        logger.info(f'Информация пользователя {user_id} успешно удалена')

    return



# init_db()
# delete_user_info(1)