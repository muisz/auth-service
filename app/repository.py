from typing import Union

from app.models import Auth

class AuthRepository:
    def create(self, auth: Auth) -> Auth:
        raise NotImplementedError()
    
    def get_by_email(self, email: str) -> Union[Auth, None]:
        raise NotImplementedError()


class DbAuthRepository(AuthRepository):
    def __init__(self, db):
        self.db = db
    
    def create(self, auth: Auth) -> Auth:
        with self.db.cursor() as cursor:
            cursor.execute("insert into auths (name, email, password, is_active) values (%s, %s, %s, %s);", [auth.name, auth.email, auth.password, auth.is_active])
            self.db.commit()

            cursor.execute("select id, name, email, password, is_active, created_at, updated_at from auths where email = %s;", [auth.email])
            result = cursor.fetchone()
            return Auth(
                id=result[0],
                name=result[1],
                email=result[2],
                password=result[3],
                is_active=result[4],
                created_at=result[5],
                updated_at=result[6],
            )
    
    def get_by_email(self, email: str) -> Union[Auth, None]:
        with self.db.cursor() as cursor:
            cursor.execute("select id, name, email, password, is_active, created_at, updated_at from auths where email = %s;", [email])
            result = cursor.fetchone()
            if result is not None:
                return Auth(
                    id=result[0],
                    name=result[1],
                    email=result[2],
                    password=result[3],
                    is_active=result[4],
                    created_at=result[5],
                    updated_at=result[6],
                )
        return None
