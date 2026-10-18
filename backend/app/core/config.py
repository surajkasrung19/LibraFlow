from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LIBRAFLOW_",
        extra="ignore",
    )
    max_active_loans: int = Field(default=3, ge=1, le=20)
    loan_period_days: int = Field(default=14, ge=1, le=90)
    max_loan_renewals: int = Field(default=1,ge=0,le=5)

settings = Settings()