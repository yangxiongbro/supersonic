import warnings
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine

from pandasai.data_loader.semantic_layer_schema import SQLConnectionConfig


def load_from_mysql(
    connection_info: SQLConnectionConfig, query: str, params: Optional[list] = None
):
    import pymysql

    conn = pymysql.connect(
        host=connection_info.host,
        user=connection_info.user,
        password=connection_info.password,
        database=connection_info.database,
        port=connection_info.port,
    )
    # Suppress warnings of SqlAlchemy
    # TODO - Later can be removed when SqlAlchemy is to used
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        return pd.read_sql(query, conn, params=params)


def load_from_postgres(
    connection_info: SQLConnectionConfig, query: str, params: Optional[list] = None
):
    import psycopg2

    conn = psycopg2.connect(
        host=connection_info.host,
        user=connection_info.user,
        password=connection_info.password,
        dbname=connection_info.database,
        port=connection_info.port,
    )
    # Suppress warnings of SqlAlchemy
    # TODO - Later can be removed when SqlAlchemy is to used
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        return pd.read_sql(query, conn, params=params)


def load_from_cockroachdb(
    connection_info: SQLConnectionConfig, query: str, params: Optional[list] = None
):
    import psycopg2

    conn = psycopg2.connect(
        host=connection_info.host,
        user=connection_info.user,
        password=connection_info.password,
        dbname=connection_info.database,
        port=connection_info.port,
    )
    # Suppress warnings of SqlAlchemy
    # TODO - Later can be removed when SqlAlchemy is to used
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        return pd.read_sql(query, conn, params=params)
def load_from_trino(connection_info:SQLConnectionConfig, query:str, params: Optional[list] = None):
# 配置Trino连接字符串
    # 格式：trino://[username:password@]host:port/[catalog.schema]
    # 注意：如果使用用户名和密码，它们应该以用户名:密码的形式放在URL中。
    # 如果你使用的是Kerberos认证或其他认证方式，你可能需要配置额外的参数。    
    engine = create_engine(
    f"""trino://{connection_info.user}@{connection_info.host}:{connection_info.port}"""
    )
    return pd.read_sql(query, engine)



__all__ = [
    "load_from_mysql",
    "load_from_postgres",
    "load_from_cockroachdb",
    "load_from_trino"
]
