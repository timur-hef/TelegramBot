import logging
import sqlalchemy as sa

from auth import DATABASE
from sqlalchemy.orm import declarative_base, Session, sessionmaker

logger = logging.getLogger('utils')

Base = declarative_base()


def init_db():
    global engine, Session    
    
    engine = sa.create_engine(DATABASE)  # change to localhost
    Session = sessionmaker(engine)
    Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = 'user_info'

    id = sa.Column(sa.Integer, primary_key=True)
    location = sa.Column(sa.String(100))
    horo_sign = sa.Column(sa.String(20))

    def __repr__(self):
        return f"User(id={self.id}, location={self.location}, horo_sign={self.horo_sign})"


def add_user(user_id, location=None, horo=None):
    s = Session()

    user = s.query(User).filter(User.id == user_id).first()
    if user:
        return

    user = User(id=user_id, location=location, horo_sign=horo)

    s.add(user)
    s.commit()
    logger.info(f'Пользователь ({user_id}) успешно добавлен')
    return


def update_user(user_id, location=None, horo=None):
    s = Session()
    user = s.query(User).filter(User.id == user_id).first()

    if not user:
        logger.error(f'Пользователь ({user_id}) не найден. Добавляю в БД')
        add_user(user_id, location=location, horo_sign=horo)
    else:
        user.location = location if location else user.location
        user.horo_sign = horo if horo else user.horo_sign

        s.merge(user)
        s.commit()
        logger.info(f'Информация пользователя ({user_id}) успешно обновлена')

    s.close()
    return


def delete_user(user_id):
    s = Session()
    user = s.query(User).filter(User.id == user_id).first()

    if not user:
        logger.error(f'Не удалось найти юзера id = {user_id}')
    else:
        s.delete(user)
        logger.info(f'Информация пользователя {user_id} успешно удалена')

    s.commit()
    s.close()
    return


# init_db()
# delete_user_info(1)