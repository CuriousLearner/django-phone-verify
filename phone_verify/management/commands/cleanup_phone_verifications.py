# -*- coding: utf-8 -*-
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from phone_verify.constants import DEFAULT_RECORD_RETENTION_DAYS
from phone_verify.models import SMSVerification

# Number of records to preview in dry-run mode
DRY_RUN_PREVIEW_LIMIT = 10


class Command(BaseCommand):
    help = "Delete old SMS verification records based on RECORD_RETENTION_DAYS setting"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            help="Number of days to retain records (overrides RECORD_RETENTION_DAYS setting)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        days = options.get("days")
        dry_run = options.get("dry_run", False)

        if days is None:
            days = settings.PHONE_VERIFICATION.get(
                "RECORD_RETENTION_DAYS", DEFAULT_RECORD_RETENTION_DAYS
            )

        cutoff_date = timezone.now() - timedelta(days=days)

        old_verifications = SMSVerification.objects.filter(created_at__lt=cutoff_date)
        count = old_verifications.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f"No verification records older than {days} days found.")
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN: Would delete {count} verification record(s) older than {days} days"
                )
            )
            self.stdout.write("Records that would be deleted:")
            for record in old_verifications[:DRY_RUN_PREVIEW_LIMIT]:
                self.stdout.write(
                    f"  - {record.phone_number} (created: {record.created_at})"
                )
            if count > DRY_RUN_PREVIEW_LIMIT:
                self.stdout.write(f"  ... and {count - DRY_RUN_PREVIEW_LIMIT} more")
        else:
            deleted_count, _ = old_verifications.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted {deleted_count} verification record(s) older than {days} days"
                )
            )
