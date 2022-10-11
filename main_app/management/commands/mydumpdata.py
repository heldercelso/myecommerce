from django.core.management.commands.dumpdata import Command as Dumpdata
from django.core.management import call_command


class Command(Dumpdata):
    def handle(self, *args, **kwargs):
        with open("data.json", "w", encoding="utf-8") as fp:
            call_command("dumpdata", format="json", indent=2, stdout=fp)