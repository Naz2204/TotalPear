from reverse_semantic_consts import SEMANTIC_TYPE

class Syntax_var_table:
    def __init__(self):
        self.__declared_vars: dict[str, SEMANTIC_TYPE] = {}

    def add(self, name: str, var_type: SEMANTIC_TYPE) -> bool:
        '''
        :return: true - on success, false - if var already exists
        '''
        if name in self.__declared_vars: return False

        self.__declared_vars[name] = var_type
        return True

    def get(self, name: str) -> SEMANTIC_TYPE | None:
        try:
            return self.__declared_vars[name]
        except:
            return None

