import logging

from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand
from munigeo.models import Address, AdministrativeDivision

from services.models import Service, ServiceNode, Unit

logger = logging.getLogger("search")


def get_search_column(model, lang):
    """
    Reads the columns, config languages and weights from the model
    to be indexed. Creates and returns a CombinedSearchVector, that
    can be stored into the search_column.
    """
    search_column = None
    columns = model.get_search_column_indexing(lang)
    for column in columns:
        if search_column:
            search_column += SearchVector(column[0], config=column[1], weight=column[2])
        else:
            search_column = SearchVector(column[0], config=column[1], weight=column[2])

    return search_column


def index_servicenodes(lang):
    """
    Index ServiceNodes which service_reference is null
    to avoid duplicates with Services in results
    """
    service_nodes_indexed = 0
    key = "search_column_%s" % lang
    columns = ServiceNode.get_search_column_indexing(lang)
    for service_node in ServiceNode.objects.all():
        search_column = None
        if service_node.service_reference is None:
            for column in columns:
                if search_column:
                    search_column += SearchVector(
                        column[0], config=column[1], weight=column[2]
                    )
                else:
                    search_column = SearchVector(
                        column[0], config=column[1], weight=column[2]
                    )
            setattr(service_node, key, search_column)
            service_node.save()
            service_nodes_indexed += 1
    return service_nodes_indexed


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        for lang in ["fi", "sv", "en"]:
            key = "search_column_%s" % lang
            logger.info(
                f"{lang} Units indexed: {Unit.objects.update(**{key: get_search_column(Unit, lang)})}"
            )
            logger.info(
                f"{lang} Services indexed: {Service.objects.update(**{key: get_search_column(Service, lang)})}"
            )
            logger.info(f"{lang} ServiceNodes indexed: {index_servicenodes(lang)}")

            logger.info(
                f"{lang} AdministrativeDivisions indexed: "
                f"{AdministrativeDivision.objects.update(**{key: get_search_column(AdministrativeDivision, lang)})}"
            )
            logger.info(
                f"{lang} Addresses indexed: {Address.objects.update(**{key: get_search_column(Address, lang)})}"
            )
