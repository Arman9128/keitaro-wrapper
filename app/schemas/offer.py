from pydantic import BaseModel, Field, ConfigDict, model_validator


class OfferCreate(BaseModel):
    offer_id: int = Field(gt=0)


class OfferUpdate(BaseModel):
    share: int = Field(ge=1, le=100)


class CampaignOfferResponse(BaseModel):
    id: int
    offer_id: int
    name: str
    share: int
    state: str


class OfferShareItem(BaseModel):
    offer_id: int = Field(gt=0)
    share: int = Field(ge=1, le=100)


class OfferSharesUpdate(BaseModel):
    offers: list[OfferShareItem] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_total_share(self):
        total = sum(offer.share for offer in self.offers)

        if total != 100:
            raise ValueError("Total offer share must equal 100")

        offer_ids = [offer.offer_id for offer in self.offers]

        if len(offer_ids) != len(set(offer_ids)):
            raise ValueError("Duplicate offer IDs are not allowed")

        return self
