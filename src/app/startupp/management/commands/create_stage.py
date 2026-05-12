from app.startupp.models import StartupStage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a startup stage"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="Name of the stage")

    def handle(self, *args, **options):
        stage_name = options["name"]
        stage = StartupStage.objects.create(name=stage_name)
        self.stdout.write(f"Stage {stage_name} created successfully.")
