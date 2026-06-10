import os
import sqlalchemy
from pymysql.constants import CLIENT

db_user = os.environ.get("DB_USER", "root")
db_pass = os.environ.get("DB_PASS", "")
db_name = os.environ.get("DB_NAME", "Data")
db_host = os.environ.get("DB_HOST", "localhost") 

db_config = {
    "pool_size": 20,
    "pool_pre_ping": True,
    "max_overflow": -1,
    "pool_timeout": 30,  # 30 seconds
    "pool_recycle": 1800,  # 30 minutes
}

pool = sqlalchemy.create_engine(
    "mysql+pymysql://"+db_user+":"+db_pass+"@"+db_host+"/"+db_name,
    **db_config
)