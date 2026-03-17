import grpc
from app.generated import startup_pb2, startup_pb2_grpc
from app.startupp.models import (
    BankInfo,
    Campaign,
    CompaignUpdate,
    Startup,
    StartupCategory,
    StartupStage,
)
from django.db import transaction
from google.protobuf.timestamp_pb2 import Timestamp


class StartupService(startup_pb2_grpc.StartupServiceServicer):
    def CreateStartup(self, request, context):
        try:
            with transaction.atomic():
                category = StartupCategory.objects.get(id=request.category_id)
                stage = StartupStage.objects.get(id=request.stage_id)

                startup = Startup.objects.create(
                    user_id=str(request.user_id),
                    name=request.name,
                    location=request.location,
                    description=request.description
                    if request.HasField("description")
                    else "",
                    website_url=request.website_url
                    if request.HasField("website_url")
                    else "",
                    founded_at=request.founded_at.ToDatetime().date(),
                )
                startup.categories.add(category)
                startup.stages.add(stage)

                return startup_pb2.CreateStartupResponse(
                    success=True,
                    message="Startup created successfully",
                    data={
                        "startup_id": str(startup.id),
                        "name": startup.name,
                        "user_id": startup.user_id,
                    },
                )
        except StartupCategory.DoesNotExist:
            return startup_pb2.CreateStartupResponse(
                success=False,
                message="Category not found",
            )
        except StartupStage.DoesNotExist:
            return startup_pb2.CreateStartupResponse(
                success=False,
                message="Stage not found",
            )
        except Exception as e:
            return startup_pb2.CreateStartupResponse(
                success=False,
                message=str(e),
            )

    def CreateCompaigns(self, request, context):
        try:
            with transaction.atomic():
                startup = Startup.objects.get(id=request.startup_id)

                campaign = Campaign.objects.create(
                    startup=startup,
                    target_amount=request.target_amount,
                    min_investment=request.min_investment,
                    revenue=request.revenue,
                    burn_rate=request.burn_rate,
                    runway=request.runway,
                    active_customers=int(request.active_customers)
                    if request.HasField("active_customers")
                    else 0,
                    valuation=request.valuation,
                    gross_margin=request.gross_margin,
                    status=request.status,
                    deadline=request.deadline.ToDatetime().date(),
                    percentage=request.revenue_share,
                    raised_amount=0,
                )

                return startup_pb2.CreateCompaignsResponse(
                    success=True,
                    message="Campaign created successfully",
                    data={
                        "campaign_id": str(campaign.id),
                        "startup_id": str(startup.id),
                        "status": campaign.status,
                    },
                )
        except Startup.DoesNotExist:
            return startup_pb2.CreateCompaignsResponse(
                success=False,
                message="Startup not found",
            )
        except Exception as e:
            return startup_pb2.CreateCompaignsResponse(
                success=False,
                message=str(e),
            )

    def CreateBankInfo(self, request, context):
        try:
            startup = Startup.objects.get(id=request.startup_id)

            bank_info = BankInfo.objects.create(
                startup=startup,
                account_number=request.account_number,
                mfo=request.mfo,
                receipient_name=request.receipant_name,
                bank_name="",
            )

            return startup_pb2.CreateBankInfoResponse(
                success=True,
                message="Bank info created successfully",
                data={
                    "bank_info_id": str(bank_info.id),
                    "startup_id": str(startup.id),
                    "account_number": bank_info.account_number,
                },
            )
        except Startup.DoesNotExist:
            return startup_pb2.CreateBankInfoResponse(
                success=False,
                message="Startup not found",
            )
        except Exception as e:
            return startup_pb2.CreateBankInfoResponse(
                success=False,
                message=str(e),
            )

    def CreateCompaignUpdate(self, request, context):
        try:
            campaign = Campaign.objects.get(id=request.compaign_id)

            update = CompaignUpdate.objects.create(
                campaign=campaign,
                title=request.title,
                body=request.body,
            )

            return startup_pb2.CreateCompaignUpdateResponse(
                success=True,
                message="Campaign update created successfully",
                data={
                    "update_id": str(update.id),
                    "campaign_id": str(campaign.id),
                    "title": update.title,
                },
            )
        except Campaign.DoesNotExist:
            return startup_pb2.CreateCompaignUpdateResponse(
                success=False,
                message="Campaign not found",
            )
        except Exception as e:
            return startup_pb2.CreateCompaignUpdateResponse(
                success=False,
                message=str(e),
            )
