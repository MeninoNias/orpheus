from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db.models import (BooleanField, CharField, DateTimeField,
                            EmailField, IntegerField)
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Manager personalizado para o modelo User usando email como identificador único
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('O campo Email é obrigatório'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('name', 'Admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superusuário precisa ter is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superusuário precisa ter is_superuser=True'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    username = None  # type: ignore[assignment]

    # Informações básicas
    name = CharField(_("Name"), max_length=255)
    email = EmailField(_("Email Address"), unique=True)

    # Configurações do usuário
    first_access = BooleanField(default=False)
    is_active = BooleanField(_("Active"), default=True)
    is_verified = BooleanField(_("Verified"), default=False)

    # Campos de auditoria
    last_login_ip = CharField(
        _("Last Login IP"), max_length=45, blank=True, null=True)
    failed_login_attempts = IntegerField(_("Failed Login Attempts"), default=0)
    password_changed_at = DateTimeField(
        _("Password Changed At"), null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]
