from fastapi import HTTPException, status

from app.integrations.keitaro import KeitaroClient
from app.schemas.offer import CampaignOfferResponse


class OfferService:

    @staticmethod
    async def get_campaign_stream(client, campaign_id: int):
        streams = await client.get(
            f"campaigns/{campaign_id}/streams"
        )

        stream = next(
            (
                item
                for item in streams
                if item.get("name") == "Offers"
            ),
            None,
        )

        if not stream:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offers stream not found",
            )

        return stream

    @staticmethod
    async def get_campaign_offers(
        campaign_id: int,
    ) -> list[CampaignOfferResponse]:
        client = KeitaroClient()

        stream = await OfferService.get_campaign_stream(
            client,
            campaign_id,
        )

        available_offers = await client.get("offers")

        offers_by_id = {
            offer["id"]: offer
            for offer in available_offers
        }

        result = []

        for item in stream.get("offers", []):
            offer_id = item["offer_id"]
            offer = offers_by_id.get(offer_id, {})

            result.append(
                CampaignOfferResponse(
                    id=item["id"],
                    offer_id=offer_id,
                    name=offer.get("name", f"Offer {offer_id}"),
                    share=item["share"],
                    state=item["state"],
                )
            )

        return result

    @staticmethod
    async def add_offer(
        campaign_id: int,
        offer_id: int,
    ):
        client = KeitaroClient()

        stream = await OfferService.get_campaign_stream(
            client,
            campaign_id,
        )

        available_offer = await client.get(
            f"offers/{offer_id}"
        )

        if available_offer.get("state") != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offer is not active",
            )

        current_offers = stream.get("offers", [])

        if any(
            item["offer_id"] == offer_id
            for item in current_offers
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Offer already exists in campaign",
            )

        offer_ids = [
            item["offer_id"]
            for item in current_offers
        ]

        offer_ids.append(offer_id)

        shares = OfferService.distribute_shares(
            len(offer_ids)
        )

        updated_offers = [
            {
                "offer_id": current_id,
                "share": share,
                "state": "active",
            }
            for current_id, share in zip(offer_ids, shares)
        ]

        await client.put(
            f"streams/{stream['id']}",
            {
                "offers": updated_offers,
            },
        )

        return await OfferService.get_campaign_offers(
            campaign_id
        )

    @staticmethod
    async def delete_offer(
        campaign_id: int,
        offer_id: int,
    ):
        client = KeitaroClient()

        stream = await OfferService.get_campaign_stream(
            client,
            campaign_id,
        )

        current_offers = stream.get("offers", [])

        updated_ids = [
            item["offer_id"]
            for item in current_offers
            if item["offer_id"] != offer_id
        ]

        if len(updated_ids) == len(current_offers):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found in campaign",
            )

        if not updated_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign must have at least one offer",
            )

        shares = OfferService.distribute_shares(
            len(updated_ids)
        )

        updated_offers = [
            {
                "offer_id": current_id,
                "share": share,
                "state": "active",
            }
            for current_id, share in zip(updated_ids, shares)
        ]

        await client.put(
            f"streams/{stream['id']}",
            {
                "offers": updated_offers,
            },
        )

        return await OfferService.get_campaign_offers(
            campaign_id
        )

    @staticmethod
    async def update_shares(
        campaign_id: int,
        offers: list,
    ):
        client = KeitaroClient()

        stream = await OfferService.get_campaign_stream(
            client,
            campaign_id,
        )

        current_ids = {
            item["offer_id"]
            for item in stream.get("offers", [])
        }

        requested_ids = {
            item.offer_id
            for item in offers
        }

        if current_ids != requested_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submitted offers must match current campaign offers",
            )

        updated_offers = [
            {
                "offer_id": item.offer_id,
                "share": item.share,
                "state": "active",
            }
            for item in offers
        ]

        await client.put(
            f"streams/{stream['id']}",
            {
                "offers": updated_offers,
            },
        )

        return await OfferService.get_campaign_offers(
            campaign_id
        )

    @staticmethod
    def distribute_shares(count: int) -> list[int]:
        base = 100 // count
        remainder = 100 % count

        return [
            base + (1 if index < remainder else 0)
            for index in range(count)
        ]
