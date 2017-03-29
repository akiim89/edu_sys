# -*- coding: utf-8 -*-

import logging
import re

from rest_framework.exceptions import APIException
from rest_framework.filters import BaseFilterBackend

logger = logging.getLogger(__name__)

# Mapping of Parse's filter options to Django's
FILTER_OPS = {
    '$lt':'lt',
    '$lte':'lte',
    '$gt':'gt',
    # $ne special case
    '$in':'in',
    # $nin special case
    # $exists special case
    # $select not supported
    # $dontSelct not supported
    # $all not supported
    # $regex not supported
}

def _camel_to_snake(name):
    if name == 'objectId':
        return 'id'
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class ParselikeFilterBackend(BaseFilterBackend):
    '''
    Based on http://parseplatform.github.io/docs/rest/guide/#queries
    '''

    def filter_one(self, queryset, field, value):
        if type(value) is dict:
            if value.get('__type') == 'Pointer':
                # It's a foreign key.
                try:
                    objectId = value['objectId']
                except KeyError:
                    raise APIException('Pointer missing objectId')
                return queryset.filter(**{'%s_id' % field:objectId})

            return self.filter_one_with_operations(queryset, field, value)
        else:
            return queryset.filter(**{field:value})

    def filter_one_with_operations(self, queryset, field, ops):
        for (op, v) in ops.items():
            if op == '$nin':
                queryset = queryset.exclude(**{'%s__in' % field:v})
            elif op == '$exists':
                queryset = queryset.exclude(**{'%s__isnull' % field:False})
            else:
                try:
                    django_op = FILTER_OPS[op]
                    queryset = queryset.filter(**{'%s__%s' % (field, django_op):v})
                except KeyError:
                    raise APIException('Filter operation %s not supported' % op)
        return queryset

    def filter_queryset(self, request, queryset, view):
        import json
        where = request.query_params.get('where', '{}')
        if where:
            try:
                where = json.loads(where)
            except ValueError:
                raise APIException('Invalid where clause')

            if type(where) is not dict:
                raise APIException('Invalid where clause')

            logger.info('ParselikeFilterBackend: where=%r', where)
            for (k,v) in where.items():
                queryset = self.filter_one(queryset, _camel_to_snake(k), v)
 
        try:
            limit = request.query_params['limit']
        except KeyError:
            pass
        else:
            try:
                limit = int(limit)
            except ValueError:
                raise APIException('Invalid limit clause')
            queryset = queryset[:limit]
                

        return queryset
