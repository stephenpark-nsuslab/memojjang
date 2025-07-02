"""
Django management command to check production readiness
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
import os
import sys


class Command(BaseCommand):
    help = 'Check if the application is ready for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-permissions',
            action='store_true',
            help='Fix file permissions for production',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Checking production readiness...\n')
        )

        errors = []
        warnings = []

        # Check DEBUG setting
        if settings.DEBUG:
            errors.append('DEBUG is enabled. Set DEBUG=False in production.')
        else:
            self.stdout.write(self.style.SUCCESS('✅ DEBUG is disabled'))

        # Check SECRET_KEY
        if hasattr(settings, 'SECRET_KEY'):
            if settings.SECRET_KEY in ['your-default-secret-key', 'your-super-secret-key-here']:
                errors.append('SECRET_KEY is using default value. Generate a secure key!')
            elif len(settings.SECRET_KEY) < 50:
                warnings.append('SECRET_KEY is quite short. Consider using a longer key.')
            else:
                self.stdout.write(self.style.SUCCESS('✅ SECRET_KEY appears secure'))
        else:
            errors.append('SECRET_KEY is not set')

        # Check ALLOWED_HOSTS
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['']:
            errors.append('ALLOWED_HOSTS is empty. Add your domain(s).')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
            )

        # Check STATIC_ROOT
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            self.stdout.write(self.style.SUCCESS('✅ STATIC_ROOT is configured'))
        else:
            warnings.append('STATIC_ROOT is not configured')

        # Security checks
        if hasattr(settings, 'SECURE_SSL_REDIRECT') and settings.SECURE_SSL_REDIRECT:
            self.stdout.write(self.style.SUCCESS('✅ SSL redirect enabled'))
        else:
            warnings.append('SSL redirect not enabled (SECURE_SSL_REDIRECT)')

        # Run Django's built-in deployment check
        self.stdout.write(self.style.WARNING('\n🔍 Running Django deployment check...'))
        try:
            call_command('check', '--deploy', '--fail-level=ERROR')
            self.stdout.write(self.style.SUCCESS('✅ Django deployment check passed'))
        except Exception as e:
            errors.append(f'Django deployment check failed: {e}')

        # Display results
        self.stdout.write('\n' + '='*50)
        
        if errors:
            self.stdout.write(self.style.ERROR('\n❌ ERRORS (must fix):'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  • {error}'))

        if warnings:
            self.stdout.write(self.style.WARNING('\n⚠️  WARNINGS (recommended to fix):'))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f'  • {warning}'))

        if not errors and not warnings:
            self.stdout.write(
                self.style.SUCCESS('\n🎉 All checks passed! Ready for production.')
            )
        elif not errors:
            self.stdout.write(
                self.style.WARNING('\n⚠️  Ready for production with warnings above.')
            )
        else:
            self.stdout.write(
                self.style.ERROR('\n❌ Not ready for production. Fix errors above.')
            )
            
        self.stdout.write('\n📚 See DEPLOYMENT.md for detailed deployment instructions.')
        
        # Exit with error code if there are errors
        if errors:
            sys.exit(1)