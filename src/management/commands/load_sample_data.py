import hashlib
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from src.models import Credential, Note

class Command(BaseCommand):

    def handle(self, *args, **options):
        Note.objects.update_or_create(
            owner="Topias",
            title="Topias's private note",
            defaults={
                "body": "Topias is testmaxxxing",
                "is_private": True,
            },
        )
        Note.objects.update_or_create(
            owner="Tiia",
            title="Tiia's private note",
            defaults={
                "body": "Remember to make tee for Topias",
                "is_private": True,
            },
        )
        

        # A02 vulnerable baseline: MD5 is fast and unsuitable for passwords.
        # different inputs can produce the same hash (collision) and brute force attacks are feasible.

        Credential.objects.update_or_create(
            username="Tiia",
            defaults={"password": hashlib.md5(b"Tiia-password").hexdigest()},
        )
        Credential.objects.update_or_create(
            username="Topias",
            defaults={"password": hashlib.md5(b"Topias-password").hexdigest()},
        )

        # Fixed version: use Django's adaptive password hashing instead.
        """ Credential.objects.update_or_create(
            username="Topias",
            defaults={"password": make_password("topias-password")},
        )
        Credential.objects.update_or_create(
            username="Tiia",
            defaults={"password": make_password("tiia-password")},
        ) """
        

        self.stdout.write(self.style.SUCCESS("Test notes and credentials created."))
