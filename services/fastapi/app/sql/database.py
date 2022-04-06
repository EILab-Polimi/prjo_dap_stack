
from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker


# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
# First version of database
# SQLALCHEMY_DATABASE_URL = "postgresql://d8map:d8map@localhost/prjo_dap"
# Second version of database - 25-01-2022
SQLALCHEMY_DATABASE_URL = "postgresql://prjo:prjo@postgres/prjo_dap_v2"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
