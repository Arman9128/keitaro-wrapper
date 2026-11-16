from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.campaign import CampaignCreate, CampaignResponse
from app.services.campaign_service import CampaignService


router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])


@router.post(
    "",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_campaign(
    data: CampaignCreate,
    db: Session = Depends(get_db),
):
    try:
        return await CampaignService.create(db, data)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create campaign in Keitaro: {str(error)}",
        ) from error


@router.get("", response_model=list[CampaignResponse])
def get_campaigns(db: Session = Depends(get_db)):
    return CampaignService.get_all(db)


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
):
    campaign = CampaignService.get_by_id(db, campaign_id)

    if campaign is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    return campaign
