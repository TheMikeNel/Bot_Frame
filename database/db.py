from . import db_types

user_operator = db_types.UserOperator(
    table='users', 
    in_columns=('user_id', 'user_name', 'user_role'), 
    out_columns=['user_id', 'user_name', 'user_role'], 
    id_name='user_id')