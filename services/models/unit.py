from django.contrib.gis.db import models
from django.contrib.postgres.fields import HStoreField
from django.contrib.postgres.fields import JSONField

from munigeo.models import AdministrativeDivision, Municipality
from munigeo.utils import get_default_srid

from services.utils import get_translated
from .department import Department
from .organization import Organization
from .service import Service
from .service_tree_node import ServiceTreeNode
from .keyword import Keyword


PROJECTION_SRID = get_default_srid()
PROVIDER_TYPES = (
    (1, 'SELF_PRODUCED'),
    (2, 'MUNICIPALITY'),
    (3, 'ASSOCIATION'),
    (4, 'PRIVATE_COMPANY'),
    (5, 'OTHER_PRODUCTION_METHOD'),
    (6, 'PURCHASED_SERVICE'),
    (7, 'UNKNOWN_PRODUCTION_METHOD'),
    (8, 'CONTRACT_SCHOOL'),
    (9, 'SUPPORTED_OPERATIONS'),
    (10, 'PAYMENT_COMMITMENT'),
)


class UnitSearchManager(models.GeoManager):
    def get_queryset(self):
        qs = super(UnitSearchManager, self).get_queryset()
        if self.only_fields:
            qs = qs.only(*self.only_fields)
        if self.include_fields:
            for f in self.include_fields:
                qs = qs.prefetch_related(f)
        return qs


class Unit(models.Model):
    id = models.IntegerField(primary_key=True)

    data_source_url = models.URLField(null=True)
    description = models.TextField(null=True)

    location = models.PointField(null=True, srid=PROJECTION_SRID)  # lat, lng?
    geometry = models.GeometryField(srid=PROJECTION_SRID, null=True)
    department = models.ForeignKey(Department, null=True)
    organization = models.ForeignKey(Organization)

    organizer_type = models.CharField(max_length=50, null=True)
    organizer_name = models.CharField(max_length=100, null=True)
    organizer_business_id = models.CharField(max_length=10, null=True)

    provider_type = models.PositiveSmallIntegerField(choices=PROVIDER_TYPES, null=True)
    picture_url = models.URLField(max_length=250, null=True)
    picture_entrance_url = models.URLField(max_length=500, null=True)
    streetview_entrance_url = models.URLField(max_length=500, null=True)

    desc = models.TextField(null=True)
    short_desc = models.TextField(null=True)
    name = models.CharField(max_length=200, db_index=True)
    street_address = models.CharField(max_length=100, null=True)
    address_city = models.CharField(max_length=100, null=True)
    www = models.URLField(max_length=400, null=True)
    address_postal_full = models.CharField(max_length=100, null=True)
    call_charge_info = models.CharField(max_length=100, null=True)

    picture_caption = models.TextField(null=True)
    extra_searchwords = models.TextField(null=True)

    phone = models.CharField(max_length=50, null=True)
    fax = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=100, null=True)
    accessibility_phone = models.CharField(max_length=50, null=True)
    accessibility_email = models.EmailField(max_length=100, null=True)
    accessibility_www = models.URLField(max_length=400, null=True)

    # accessibility_viewpoints = models.ManyToManyField(AccessibilityViewpoint)

    created_time = models.DateTimeField(null=True)  # ASK API: are these UTC? no Z in output
    modified_time = models.DateTimeField(null=True)  # ASK API: are these UTC? no Z in output

    municipality = models.ForeignKey(Municipality, null=True, db_index=True)
    address_zip = models.CharField(max_length=10, null=True)

    data_source = models.CharField(max_length=20, null=True)
    # extensions = HStoreField(null=True)

    # origin_last_modified_time = models.DateTimeField(db_index=True, help_text='Time of last modification')

    service_tree_nodes = models.ManyToManyField("ServiceTreeNode", related_name='units')
    services = models.ManyToManyField("Service", related_name='units')
    divisions = models.ManyToManyField(AdministrativeDivision)
    keywords = models.ManyToManyField(Keyword)

    connection_hash = models.CharField(max_length=40, null=True,
                                       help_text='Automatically generated hash of connection info')
    accessibility_property_hash = models.CharField(max_length=40, null=True,
                                                   help_text='Automatically generated hash of accessibility property info')
    accessibility_sentence_hash = models.CharField(max_length=40, null=True)
    identifier_hash = models.CharField(max_length=40, null=True,
                                       help_text='Automatically generated hash of other identifiers')

    accessibility_viewpoints = JSONField(default="{}")

    # Cached fields for better performance
    root_services = models.CommaSeparatedIntegerField(max_length=50, null=True)
    root_servicenodes = models.CommaSeparatedIntegerField(max_length=50, null=True)

    objects = models.GeoManager()
    search_objects = UnitSearchManager()

    def __str__(self):
        return "%s (%s)" % (get_translated(self, 'name'), self.id)

    def get_root_servicenodes(self):
        # FIXME: fix once services are up and running..
        return []
        tree_ids = self.services.all().values_list('tree_id', flat=True).distinct()
        qs = Service.objects.filter(level=0).filter(tree_id__in=list(tree_ids))
        srv_list = qs.values_list('id', flat=True).distinct()
        return sorted(srv_list)

    def get_root_servitreenodes(self):
        tree_ids = self.service_tree_nodes.all().values_list('tree_id', flat=True).distinct()
        qs = ServiceTreeNode.objects.filter(level=0).filter(tree_id__in=list(tree_ids))
        srv_list = qs.values_list('id', flat=True).distinct()
        return sorted(srv_list)