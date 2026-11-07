from typing import Any

from blueprint import BaseModel, BlueprintDagArgs, Field


class ProjectDagArgsConfig(BaseModel):
    schedule: str | None = None
    description: str | None = None
    start_date: str | None = None
    catchup: bool = False
    tags: list[str] = Field(default_factory=list)
    default_args: dict[str, str] = Field(default_factory=dict)


class ProjectDagArgs(BlueprintDagArgs[ProjectDagArgsConfig]):
    """DAG args template that passes through all standard Airflow DAG fields."""

    def render(self, config: ProjectDagArgsConfig) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"catchup": config.catchup}

        if config.schedule is not None:
            kwargs["schedule"] = config.schedule
        if config.description is not None:
            kwargs["description"] = config.description
        if config.start_date is not None:
            kwargs["start_date"] = config.start_date
        if config.tags:
            kwargs["tags"] = config.tags
        if config.default_args:
            kwargs["default_args"] = config.default_args

        return kwargs
