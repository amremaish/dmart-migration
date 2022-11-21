from enums import JoinType
from utils.db import db_manager
from utils.docorators import process_mapper


@process_mapper(mapper="users")
def load(*args, **kwargs):
    # comes from process_mapper decorator
    mapper_data: dict = kwargs['mapper_data']

    db_result = db_manager.select_query(
        table_name=mapper_data.get('source').get('table'),
        columns=mapper_data.get('source').get('columns'),
        join_tables=mapper_data.get('source').get('join'))

    print(mapper_data)
