import re
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.keitaro import KeitaroClient
from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate


class CampaignService:

    @staticmethod
    async def create(
        db: Session,
        data: CampaignCreate,
    ) -> Campaign:
        country_code = data.country_code.upper()

        campaign = Campaign(
            name=data.name,
            country_code=country_code,
            offer_id=data.offer_id,
            status="pending",
        )

        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        client = KeitaroClient()

        try:
            # Check that the selected offer exists and is active.
            offer = await client.get(f"offers/{data.offer_id}")

            if offer.get("state") != "active":
                raise ValueError(
                    f"Offer {data.offer_id} is not active"
                )

            # Generate a unique campaign alias.
            alias = re.sub(
                r"[^a-z0-9-]+",
                "-",
                data.name.lower(),
            ).strip("-")

            alias = f"{alias[:80]}-{uuid.uuid4().hex[:8]}"

            # Create campaign in Keitaro.
            keitaro_campaign = await client.post(
                "campaigns",
                {
                    "alias": alias,
                    "name": data.name,
                    "type": "position",
                    "state": "active",
                    "group_id": str(settings.keitaro_group_id),
                    "traffic_source_id": settings.keitaro_traffic_source_id,
                },
            )

            keitaro_campaign_id = keitaro_campaign.get("id")

            if not keitaro_campaign_id:
                raise ValueError(
                    "Keitaro did not return campaign ID"
                )

            campaign.keitaro_campaign_id = keitaro_campaign_id
            db.commit()
            db.refresh(campaign)

            # Assign domain to the campaign.
            await client.put(
                f"campaigns/{keitaro_campaign_id}",
                {
                    "domain_id": settings.keitaro_domain_id,
                },
            )

            # Create Google redirect stream.
            google_stream = await client.post(
                "streams",
                {
                    "campaign_id": keitaro_campaign_id,
                    "schema": "redirect",
                    "type": "regular",
                    "name": "Google",
                    "action_type": "http",
                    "position": 1,
                    "state": "active",
                    "action_options": {
                        "url": "https://google.com",
                    },
                },
            )

            google_stream_id = google_stream.get("id")

            if not google_stream_id:
                raise ValueError(
                    "Keitaro did not return Google stream ID"
                )

            # Add country filter to Google stream.
            await client.put(
                f"streams/{google_stream_id}",
                {
                    "filters": [
                        {
                            "name": "country",
                            "mode": "accept",
                            "payload": [country_code],
                        }
                    ],
                },
            )

            # Create Offers stream.
            offers_stream = await client.post(
                "streams",
                {
                    "campaign_id": keitaro_campaign_id,
                    "schema": "landings",
                    "type": "regular",
                    "name": "Offers",
                    "action_type": "http",
                    "position": 2,
                    "state": "active",
                    "offers": [
                        {
                            "offer_id": data.offer_id,
                            "share": 100,
                            "state": "active",
                        }
                    ],
                },
            )

            if not offers_stream.get("id"):
                raise ValueError(
                    "Keitaro did not return Offers stream ID"
                )

            campaign.status = "active"
            campaign.error_message = None

            db.commit()
            db.refresh(campaign)

            return campaign

        except Exception as error:
            db.rollback()

            campaign = db.query(Campaign).filter(
                Campaign.id == campaign.id
            ).first()

            if campaign:
                campaign.status = "failed"
                campaign.error_message = str(error)[:4000]

                db.commit()
                db.refresh(campaign)

            raise

    @staticmethod
    def get_all(db: Session) -> list[Campaign]:
        return db.query(Campaign).order_by(
            Campaign.id.desc()
        ).all()

    @staticmethod
    def get_by_id(
        db: Session,
        campaign_id: int,
    ) -> Campaign | None:
        return db.query(Campaign).filter(
            Campaign.id == campaign_id
        ).first()
