import uuid

from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseUUidModel(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BasePublicUUidModel(BaseModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseOwnerModel(BaseModel):
    owner = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name="%(class)s_owner")

    class Meta:
        abstract = True
