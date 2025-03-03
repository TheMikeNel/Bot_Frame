class IDObject:
    def __init__(self, id: str, params: dict[str, str]):
        self.id = id
        self.params = params
    
    def __str__(self):
        result = f"\nID: {self.id}"
        for key, value in self.params.items():
            fkey = rename_param(key)
            result += f"\n{fkey}: {value}"
        return (result + "\n- - - - - - - - - - - - - - - - - - - - - - - -")
    
    def to_dict(self):
        dict = {"id": self.id}
        dict.update(self.params)
        print(f"Encoding: {dict}")
        return dict

class User(IDObject):
    def __dict__(self):
        return {'user_id': self.id} + self.params
    
    def __init__(self, id: str, params: dict[str, str]):
        super().__init__(id, params)
        self.name = 'None'
        self.role = 'worker'
        if 'user_name' in params:
            self.name = params['user_name']
        if 'user_role' in params:
            self.role = params['user_role']
    pass