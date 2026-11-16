from pydantic import BaseModel, Field, ConfigDict, field_validator


class CampaignCreate(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=255,
        description="Campaign name",
        examples=["Adrobot Integration Test"],
    )

    country_code: str = Field(
        min_length=2,
        max_length=2,
        pattern=r"^[A-Za-z]{2}$",
        description="Two-letter ISO country code, for example DE",
        examples=["DE"],
    )

    offer_id: int = Field(
        gt=0,
        description="Existing active Keitaro offer ID",
        examples=[4440],
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if value.lower() == "string":
            raise ValueError("Please enter a real campaign name")

        if not value:
            raise ValueError("Campaign name cannot be empty")

        return value

    @field_validator("country_code")
    @classmethod
    def normalize_country_code(cls, value: str) -> str:
        return value.upper()


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    keitaro_campaign_id: int | None
    name: str
    country_code: str
    offer_id: int
    status: str
    error_message: str | None
