from dmart import core


def convert_db_to_meta(row_data: dict, mapper: dict):
    meta = mapper.get('columns_mapper').get('meta')
    body = mapper.get('columns_mapper').get('body')
    schema_shortname = mapper.get('dest').get('schema_shortname')

    meta_data: dict = {}
    for meta_name in meta.keys():
        col_name = meta[meta_name]
        if col_name not in row_data:
            raise Exception(f'column {col_name} is not found in row: {row_data}')
        meta_data[meta_name] = row_data[col_name]

    body_data: dict = {}
    for body_name in body.keys():
        col_name = body[body_name]
        if col_name not in row_data:
            raise Exception(f'column {col_name} is not found in row: {row_data}')
        body_data[body_name] = row_data[col_name]

    meta_data['owner_shortname'] = 'dmart'
    meta_obj = core.Meta(**meta_data)
    payload = core.Payload(content_type='json', schema_shortname=schema_shortname, body=f'{meta_obj.shortname}.json')
    meta_obj.payload = payload
    return meta_obj, body_data
