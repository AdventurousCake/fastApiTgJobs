from fastapi import Query


def limit_offset(limit: int = Query(10, ge=0), offset: int = Query(None, ge=0)) -> dict:
    return {"limit": limit, "offset": offset}


def filter_params(filter_by: str = Query(None), filter_value: int = Query(None)) -> dict:
    if filter_by:
        return {filter_by: bool(filter_value)}
    else:
        return {}
