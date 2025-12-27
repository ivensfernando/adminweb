from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from config.settings.base import API_KEYS_SECRET_KEY, API_KEYS_SECRET_HASHER


class Command(BaseCommand):
    help = 'Create a new API key'

    def add_arguments(self, parser):
        parser.add_argument(
            "-key",
            "--key",
            type=str,
            required=False,
            help="API key value to be persisted to tb",
        )

    def handle(self, *args, **options):
        key = options.get("key")

        key_hash = make_password(password=key, salt=API_KEYS_SECRET_KEY, hasher=API_KEYS_SECRET_HASHER)

        self.stdout.write(self.style.SUCCESS(f'API key hash created successfully. key_hash={key_hash}'))
