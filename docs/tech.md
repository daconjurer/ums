# The tech

The project uses:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic v2](https://docs.pydantic.dev/latest/) for the schema validation
- [SQLModel](https://sqlmodel.tiangolo.com/) ([SQLAlchemy v2](https://www.sqlalchemy.org/)) for the ORM
- [PostgreSQL](https://www.postgresql.org/) (a [Docker](https://www.docker.com/) container)

Also, the dev scripts can be run with [Make](https://www.gnu.org/software/make/manual/make.html),
and use [ruff](https://github.com/astral-sh/ruff) and [Pyright](https://github.com/microsoft/pyright)
for formatting/linting and type checking.
