from creator import creator
from dmart.helper import governorates_mapper
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer


@process_mapper(
    mapper="orders",
    remove_null_field=True,
    appended_list=['body.order_composition']
)
def load(*args, **kwargs):
    default_loader(args, kwargs, apply_modifier)
    print("Successfully done.")


def apply_modifier(
        space_name: str,
        subpath: str,
        resource_type: str,
        schema_shortname: str,
        meta: dict,
        body: dict,
        db_row: dict,
        lookup: dict
):
    meta = meta_fixer(meta)
    # mapped from SIMRegistrationServiceLayer/src/main/java/com/telephoenic/sr/gs/dao/imp/OrderHistoryDAOImp.java
    if meta.get('state'):
        state = str(meta.get('state'))
        if state == '1':  # APPROVED
            meta['state'] = 'assigned'
        elif state == '2':  # REJECTED
            meta['state'] = 'rejected'
            reason = db_row.get(db_manager.create_alias('ORDER_HISTORY.REJECTREASON'))
            meta['resolution_reason'] = reason if reason else ''
        elif state == '12':  # NOT DELIVERED
            meta['state'] = 'failed'
        elif state == '102':  # PENDING
            meta['state'] = 'pending'
        elif state == '11':  # DELIVERED
            meta['state'] = 'delivered'
        else:
            meta['state'] = ''

    if body.get('distributor_name'):
        body['distributor_name'] = creator.shortname_fixer(body.get('distributor_name'))

    # resolution_reason fixer
    if meta.get('resolution_reason'):
        meta['resolution_reason'] = creator.reason_fixer(meta['resolution_reason'])

    # fix governorate
    if body.get('delivery_details', {}).get('governorate'):
        governorate = body.get('delivery_details', {}).get('governorate')
        if governorate:
            governorate = governorates_mapper.get(creator.shortname_fixer(governorate))
            if governorate:
                if governorate == 'baghdad':
                    governorate = 'baghdad_karkh'
                body['delivery_details']['governorate'] = governorate
            else:
                body['delivery_details']['governorate'] = None

    # fix shortnames
    if body.get('order_composition') and len(body.get('order_composition')) > 0:
        order: dict = body.get('order_composition')[0]
        body['order_composition'][0]['parent_category'] = creator.shortname_fixer(order.get('parent_category'))
        body['order_composition'][0]['category'] = creator.shortname_fixer(order.get('category'))
        body['order_composition'][0]['shortname'] = creator.shortname_fixer(order.get('shortname'))

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body
    }
