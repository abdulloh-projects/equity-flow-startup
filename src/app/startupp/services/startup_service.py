import datetime

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


def _date_to_timestamp(d):
    ts = Timestamp()
    ts.FromDatetime(datetime.datetime.combine(d, datetime.time.min))
    return ts


def _datetime_to_timestamp(dt):
    ts = Timestamp()
    ts.FromDatetime(dt.replace(tzinfo=None))
    return ts


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

    def GetStartup(self, request, context):
        try:
            startup = Startup.objects.get(id=request.startup_id)
            return startup_pb2.GetStartupResponse(
                success=True,
                message="Startup retrieved successfully",
                id=startup.id,
                user_id=startup.user_id,
                name=startup.name,
                location=startup.location,
                description=startup.description,
                website_url=startup.website_url,
                founded_at=_date_to_timestamp(startup.founded_at),
                created_at=_datetime_to_timestamp(startup.created_at),
                updated_at=_datetime_to_timestamp(startup.updated_at),
            )
        except Startup.DoesNotExist:
            return startup_pb2.GetStartupResponse(
                success=False,
                message="Startup not found",
            )
        except Exception as e:
            return startup_pb2.GetStartupResponse(
                success=False,
                message=str(e),
            )

    def UpdateStartup(self, request, context):
        try:
            with transaction.atomic():
                startup = Startup.objects.get(id=request.startup_id)

                if request.HasField("name"):
                    startup.name = request.name
                if request.HasField("location"):
                    startup.location = request.location
                if request.HasField("description"):
                    startup.description = request.description
                if request.HasField("website_url"):
                    startup.website_url = request.website_url
                if request.HasField("founded_at"):
                    startup.founded_at = request.founded_at.ToDatetime().date()
                startup.save()

                if request.HasField("category_id"):
                    category = StartupCategory.objects.get(id=request.category_id)
                    startup.categories.set([category])
                if request.HasField("stage_id"):
                    stage = StartupStage.objects.get(id=request.stage_id)
                    startup.stages.set([stage])

                return startup_pb2.UpdateStartupResponse(
                    success=True,
                    message="Startup updated successfully",
                    data={
                        "startup_id": str(startup.id),
                        "name": startup.name,
                    },
                )
        except Startup.DoesNotExist:
            return startup_pb2.UpdateStartupResponse(
                success=False,
                message="Startup not found",
            )
        except StartupCategory.DoesNotExist:
            return startup_pb2.UpdateStartupResponse(
                success=False,
                message="Category not found",
            )
        except StartupStage.DoesNotExist:
            return startup_pb2.UpdateStartupResponse(
                success=False,
                message="Stage not found",
            )
        except Exception as e:
            return startup_pb2.UpdateStartupResponse(
                success=False,
                message=str(e),
            )

    def DeleteStartup(self, request, context):
        try:
            startup = Startup.objects.get(id=request.startup_id)
            startup.delete()
            return startup_pb2.DeleteStartupResponse(
                success=True,
                message="Startup deleted successfully",
            )
        except Startup.DoesNotExist:
            return startup_pb2.DeleteStartupResponse(
                success=False,
                message="Startup not found",
            )
        except Exception as e:
            return startup_pb2.DeleteStartupResponse(
                success=False,
                message=str(e),
            )

    def GetCompaigns(self, request, context):
        try:
            campaign = Campaign.objects.get(id=request.campaign_id)
            return startup_pb2.GetCompaignsResponse(
                success=True,
                message="Campaign retrieved successfully",
                id=campaign.id,
                startup_id=campaign.startup_id,
                target_amount=float(campaign.target_amount),
                raised_amount=float(campaign.raised_amount),
                min_investment=float(campaign.min_investment),
                revenue=float(campaign.revenue),
                revenue_share=float(campaign.percentage),
                burn_rate=float(campaign.burn_rate),
                runway=float(campaign.runway),
                active_customers=float(campaign.active_customers),
                valuation=float(campaign.valuation),
                gross_margin=float(campaign.gross_margin),
                status=campaign.status,
                deadline=_date_to_timestamp(campaign.deadline),
                created_at=_datetime_to_timestamp(campaign.created_at),
                updated_at=_datetime_to_timestamp(campaign.updated_at),
            )
        except Campaign.DoesNotExist:
            return startup_pb2.GetCompaignsResponse(
                success=False,
                message="Campaign not found",
            )
        except Exception as e:
            return startup_pb2.GetCompaignsResponse(
                success=False,
                message=str(e),
            )

    def UpdateCompaigns(self, request, context):
        try:
            with transaction.atomic():
                campaign = Campaign.objects.get(id=request.campaign_id)

                if request.HasField("target_amount"):
                    campaign.target_amount = request.target_amount
                if request.HasField("min_investment"):
                    campaign.min_investment = request.min_investment
                if request.HasField("revenue"):
                    campaign.revenue = request.revenue
                if request.HasField("revenue_share"):
                    campaign.percentage = request.revenue_share
                if request.HasField("burn_rate"):
                    campaign.burn_rate = request.burn_rate
                if request.HasField("runway"):
                    campaign.runway = request.runway
                if request.HasField("active_customers"):
                    campaign.active_customers = int(request.active_customers)
                if request.HasField("valuation"):
                    campaign.valuation = request.valuation
                if request.HasField("gross_margin"):
                    campaign.gross_margin = request.gross_margin
                if request.HasField("status"):
                    campaign.status = request.status
                if request.HasField("deadline"):
                    campaign.deadline = request.deadline.ToDatetime().date()
                campaign.save()

                return startup_pb2.UpdateCompaignsResponse(
                    success=True,
                    message="Campaign updated successfully",
                    data={
                        "campaign_id": str(campaign.id),
                        "startup_id": str(campaign.startup_id),
                        "status": campaign.status,
                    },
                )
        except Campaign.DoesNotExist:
            return startup_pb2.UpdateCompaignsResponse(
                success=False,
                message="Campaign not found",
            )
        except Exception as e:
            return startup_pb2.UpdateCompaignsResponse(
                success=False,
                message=str(e),
            )

    def DeleteCompaigns(self, request, context):
        try:
            campaign = Campaign.objects.get(id=request.campaign_id)
            campaign.delete()
            return startup_pb2.DeleteCompaignsResponse(
                success=True,
                message="Campaign deleted successfully",
            )
        except Campaign.DoesNotExist:
            return startup_pb2.DeleteCompaignsResponse(
                success=False,
                message="Campaign not found",
            )
        except Exception as e:
            return startup_pb2.DeleteCompaignsResponse(
                success=False,
                message=str(e),
            )

    def GetBankInfo(self, request, context):
        try:
            bank_info = BankInfo.objects.get(id=request.bank_info_id)
            return startup_pb2.GetBankInfoResponse(
                success=True,
                message="Bank info retrieved successfully",
                id=bank_info.id,
                startup_id=bank_info.startup_id,
                account_number=bank_info.account_number,
                bank_name=bank_info.bank_name,
                receipient_name=bank_info.receipient_name,
                mfo=bank_info.mfo,
            )
        except BankInfo.DoesNotExist:
            return startup_pb2.GetBankInfoResponse(
                success=False,
                message="Bank info not found",
            )
        except Exception as e:
            return startup_pb2.GetBankInfoResponse(
                success=False,
                message=str(e),
            )

    def UpdateBankInfo(self, request, context):
        try:
            bank_info = BankInfo.objects.get(id=request.bank_info_id)

            if request.HasField("mfo"):
                bank_info.mfo = request.mfo
            if request.HasField("account_number"):
                bank_info.account_number = request.account_number
            if request.HasField("receipant_name"):
                bank_info.receipient_name = request.receipant_name
            bank_info.save()

            return startup_pb2.UpdateBankInfoResponse(
                success=True,
                message="Bank info updated successfully",
                data={
                    "bank_info_id": str(bank_info.id),
                    "startup_id": str(bank_info.startup_id),
                    "account_number": bank_info.account_number,
                },
            )
        except BankInfo.DoesNotExist:
            return startup_pb2.UpdateBankInfoResponse(
                success=False,
                message="Bank info not found",
            )
        except Exception as e:
            return startup_pb2.UpdateBankInfoResponse(
                success=False,
                message=str(e),
            )

    def DeleteBankInfo(self, request, context):
        try:
            bank_info = BankInfo.objects.get(id=request.bank_info_id)
            bank_info.delete()
            return startup_pb2.DeleteBankInfoResponse(
                success=True,
                message="Bank info deleted successfully",
            )
        except BankInfo.DoesNotExist:
            return startup_pb2.DeleteBankInfoResponse(
                success=False,
                message="Bank info not found",
            )
        except Exception as e:
            return startup_pb2.DeleteBankInfoResponse(
                success=False,
                message=str(e),
            )

    def GetCompaignUpdate(self, request, context):
        try:
            update = CompaignUpdate.objects.get(id=request.update_id)
            return startup_pb2.GetCompaignUpdateResponse(
                success=True,
                message="Campaign update retrieved successfully",
                id=update.id,
                campaign_id=update.campaign_id,
                title=update.title,
                body=update.body,
                posted_at=_datetime_to_timestamp(update.posted_at),
                updated_at=_datetime_to_timestamp(update.updated_at),
            )
        except CompaignUpdate.DoesNotExist:
            return startup_pb2.GetCompaignUpdateResponse(
                success=False,
                message="Campaign update not found",
            )
        except Exception as e:
            return startup_pb2.GetCompaignUpdateResponse(
                success=False,
                message=str(e),
            )

    def UpdateCompaignUpdate(self, request, context):
        try:
            update = CompaignUpdate.objects.get(id=request.update_id)

            if request.HasField("title"):
                update.title = request.title
            if request.HasField("body"):
                update.body = request.body
            update.save()

            return startup_pb2.UpdateCompaignUpdateResponse(
                success=True,
                message="Campaign update updated successfully",
                data={
                    "update_id": str(update.id),
                    "campaign_id": str(update.campaign_id),
                    "title": update.title,
                },
            )
        except CompaignUpdate.DoesNotExist:
            return startup_pb2.UpdateCompaignUpdateResponse(
                success=False,
                message="Campaign update not found",
            )
        except Exception as e:
            return startup_pb2.UpdateCompaignUpdateResponse(
                success=False,
                message=str(e),
            )

    def DeleteCompaignUpdate(self, request, context):
        try:
            update = CompaignUpdate.objects.get(id=request.update_id)
            update.delete()
            return startup_pb2.DeleteCompaignUpdateResponse(
                success=True,
                message="Campaign update deleted successfully",
            )
        except CompaignUpdate.DoesNotExist:
            return startup_pb2.DeleteCompaignUpdateResponse(
                success=False,
                message="Campaign update not found",
            )
        except Exception as e:
            return startup_pb2.DeleteCompaignUpdateResponse(
                success=False,
                message=str(e),
            )

    def ListStartups(self, request, context):
        try:
            page = max(1, request.page) if request.page else 1
            limit = min(50, max(1, request.limit)) if request.limit else 9
            offset = (page - 1) * limit
            qs = Startup.objects.all().order_by("-created_at")
            total = qs.count()
            startups = qs[offset : offset + limit]
            items = []
            for s in startups:
                items.append(
                    startup_pb2.StartupSummary(
                        id=s.id,
                        name=s.name,
                        location=s.location,
                        description=s.description or "",
                        website_url=s.website_url or "",
                        category_id=s.categories.first().id
                        if s.categories.exists()
                        else 0,
                        stage_id=s.stages.first().id if s.stages.exists() else 0,
                        founded_at=_date_to_timestamp(s.founded_at),
                        created_at=_datetime_to_timestamp(s.created_at),
                    )
                )
            return startup_pb2.ListStartupsResponse(
                success=True,
                message="OK",
                startups=items,
                total=total,
                page=page,
                limit=limit,
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return startup_pb2.ListStartupsResponse(success=False, message=str(e))

    def GetStartupsByUser(self, request, context):
        try:
            startups = Startup.objects.filter(user_id=str(request.user_id)).order_by(
                "-created_at"
            )
            items = []
            for s in startups:
                items.append(
                    startup_pb2.StartupSummary(
                        id=s.id,
                        name=s.name,
                        location=s.location,
                        description=s.description or "",
                        website_url=s.website_url or "",
                        category_id=s.categories.first().id
                        if s.categories.exists()
                        else 0,
                        stage_id=s.stages.first().id if s.stages.exists() else 0,
                        founded_at=_date_to_timestamp(s.founded_at),
                        created_at=_datetime_to_timestamp(s.created_at),
                    )
                )
            return startup_pb2.GetStartupsByUserResponse(
                success=True,
                message="OK",
                startups=items,
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return startup_pb2.GetStartupsByUserResponse(success=False, message=str(e))

    def ListCampaignsByStartup(self, request, context):
        try:
            campaigns = Campaign.objects.filter(startup_id=request.startup_id).order_by(
                "-created_at"
            )
            items = []
            for c in campaigns:
                items.append(
                    startup_pb2.CampaignSummary(
                        id=c.id,
                        startup_id=c.startup_id,
                        target_amount=float(c.target_amount),
                        raised_amount=float(c.raised_amount),
                        min_investment=float(c.min_investment),
                        revenue=float(c.revenue),
                        revenue_share=float(
                            getattr(c, "percentage", None)
                            or getattr(c, "revenue_share", 0)
                            or 0
                        ),
                        burn_rate=float(c.burn_rate),
                        runway=float(c.runway),
                        active_customers=float(c.active_customers or 0),
                        valuation=float(c.valuation),
                        gross_margin=float(c.gross_margin),
                        status=c.status,
                        deadline=_date_to_timestamp(c.deadline),
                        created_at=_datetime_to_timestamp(c.created_at),
                    )
                )
            return startup_pb2.ListCampaignsByStartupResponse(
                success=True,
                message="OK",
                campaigns=items,
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return startup_pb2.ListCampaignsByStartupResponse(
                success=False, message=str(e)
            )
