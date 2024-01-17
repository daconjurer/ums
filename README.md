# A User management API with FastAPI

The project uses:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic v2](https://docs.pydantic.dev/latest/) for the schema validation
- [SQLModel](https://sqlmodel.tiangolo.com/) ([SQLAlchemy v2](https://www.sqlalchemy.org/)) for the ORM
- [PostgreSQL](https://www.postgresql.org/) (a [Docker](https://www.docker.com/) container)

## Data models
The database schemas are described in the `ums.models` module.

## Development start-up
The database can be started with:

```./scripts/test_db.sh up```

This will spin up a Postgres container with a `docker_test_ums_data` volume attached
to it for the DB data. It can then be initialised with:

```poetry run python3 db/init_db.py```

The app starts with:
    
```poetry run python3 main.py```
