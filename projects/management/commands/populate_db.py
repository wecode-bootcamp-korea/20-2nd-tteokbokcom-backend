from django.core.management.base import BaseCommand, CommandError

from utils.populate_db import populate_db

class Command(BaseCommand):
    help = "Read Data from Mockup csv file and Populate DB"

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.NOTICE("Start Populating DB"))
            populate_db()
            self.stdout.write(self.style.SUCCESS("DB Population Finished."))
            
        except CommandError as e:
            print(e)
