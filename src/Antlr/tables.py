from Antlr.consts import VALUE_TYPES

class Var_table:
    def __init__(self):
        self.__declared_vars: dict[str, VALUE_TYPES] = {}

    def add(self, var_type: VALUE_TYPES, name: str) -> bool:
        '''
        :return: true - on success, false - if var already exists
        '''
        if name in self.__declared_vars: return False

        self.__declared_vars[name] = var_type
        return True

    def get_type(self, name: str) -> VALUE_TYPES | None:
        try:
            return self.__declared_vars[name]
        except:
            return None

    def get_table(self) -> tuple[tuple[str, str]]:
        return tuple((i[0], i[1].value) for i in self.__declared_vars.items())

    def get_table_CIL(self, prefix: str) -> tuple[tuple[str, VALUE_TYPES]]:
        return tuple((prefix + i[0], i[1]) for i in self.__declared_vars.items())


class Label_generator:
    def __init__(self):
        self.__PREFIX = 'label'
        self.__label_id = -1

    def get_label(self) -> str:
        self.__label_id += 1
        return f'{self.__PREFIX}{self.__label_id}'
