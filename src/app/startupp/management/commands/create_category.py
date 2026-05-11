from app.startupp.models import StartupCategory
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a startup category"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="Name of the category")

    def handle(self, *args, **options):
        category_name = options["name"]
        category = StartupCategory.objects.create(name=category_name)
        self.stdout.write(f"Category {category_name} created successfully.")
