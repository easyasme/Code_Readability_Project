import logging

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.gis.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .mixins import TimestampedModelMixin

logger = logging.getLogger("db")


class ParkingZoneManager(models.Manager):
    def get_for_location(self, location):
        return self.get(location__intersects=location)


class ParkingZone(TimestampedModelMixin):
    name = models.CharField(_("Name"), max_length=128, unique=True)
    description = models.TextField(_("Description"), blank=True)
    description_sv = models.TextField(_("Description sv"), blank=True)
    location = models.MultiPolygonField(_("Area (2D)"), srid=settings.SRID)

    objects = ParkingZoneManager()

    class Meta:
        verbose_name = _("Parking zone")
        verbose_name_plural = _("Parking zones")

    def __str__(self):
        return self.name

    @property
    def label(self):
        return f"{self.name} - {self.description}"

    @property
    def label_sv(self):
        return f"{self.name} - {self.description_sv}"

    @property
    def resident_products(self):
        """Resident products that cover the following 12 months"""
        start_date = timezone.localdate(timezone.now())
        end_date = start_date + relativedelta(months=12, days=-1)
        return self.products.for_resident().for_date_range(start_date, end_date)

    @property
    def company_products(self):
        """Company products that cover the following 12 months"""
        start_date = timezone.localdate(timezone.now())
        end_date = start_date + relativedelta(months=12, days=-1)
        return self.products.for_company().for_date_range(start_date, end_date)
