from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.campaign import Campaign
from app.schemas.offer import (
    OfferCreate,
    OfferSharesUpdate,
    CampaignOfferResponse,
)
from app.services.offer_service import OfferService


router = APIRouter(
    prefix="/api/campaigns/{campaign_id}/offers",
    tags=["Campaign Offers"],
)


def get_keitaro_campaign_id(
    campaign_id: int,
    db: Session,
) -> int:
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id
    ).first()

    if campaign is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    if campaign.keitaro_campaign_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Campaign is not connected to Keitaro",
        )

    return campaign.keitaro_campaign_id


@router.get("", response_model=list[CampaignOfferResponse])
async def get_offers(
    campaign_id: int,
    db: Session = Depends(get_db),
):
    keitaro_id = get_keitaro_campaign_id(campaign_id, db)

    return await OfferService.get_campaign_offers(keitaro_id)


@router.post("", response_model=list[CampaignOfferResponse])
async def add_offer(
    campaign_id: int,
    data: OfferCreate,
    db: Session = Depends(get_db),
):
    keitaro_id = get_keitaro_campaign_id(campaign_id, db)

    return await OfferService.add_offer(
        keitaro_id,
        data.offer_id,
    )


@router.put("", response_model=list[CampaignOfferResponse])
async def update_offer_shares(
    campaign_id: int,
    data: OfferSharesUpdate,
    db: Session = Depends(get_db),
):
    keitaro_id = get_keitaro_campaign_id(campaign_id, db)

    return await OfferService.update_shares(
        keitaro_id,
        data.offers,
    )


@router.delete(
    "/{offer_id}",
    response_model=list[CampaignOfferResponse],
)
async def delete_offer(
    campaign_id: int,
    offer_id: int,
    db: Session = Depends(get_db),
):
    keitaro_id = get_keitaro_campaign_id(campaign_id, db)

    return await OfferService.delete_offer(
        keitaro_id,
        offer_id,
    )
