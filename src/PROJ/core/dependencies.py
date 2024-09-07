from fastapi import Query


def limit_offset2(limit: int = Query(10, ge=0), offset: int = Query(None, ge=0)) -> dict:
    return {"limit": limit, "offset": offset}


def filter_params0(filter_by: str = Query(None), filter_value: str = Query(None)) -> dict:
    return {filter_by: filter_value}


def filter_params(filter_by: str = Query(None), filter_value: int = Query(None)) -> dict:
    return {filter_by: bool(filter_value)}
