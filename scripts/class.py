from typing import Union


class User:
    uuids = []

    def __init__(self, uuid: Union[int, str], username: str = None, password_hash: str = None, password: str = None):
        if uuid in User.uuids:
            raise Exception(f"User with this uuid already exists: {uuid}!")

        User.uuids.append(uuid)
        self.uuid: Union[int, str] = uuid
        self.username: str = username
        self.password_hash: str = password_hash
        self.password: str = password

    @classmethod
    def build(cls, builder: Union[dict, "User"] = None):
        if isinstance(builder, User):
            return cls(**User.__dict__)
        return cls(**builder)

    def to_dict(self):
        return self.__dict__
