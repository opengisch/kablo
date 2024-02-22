from django.db.models import Aggregate


class MergeLines(Aggregate):
    name = "joined_geometries"
    template = "ST_SetSRID(ST_Expand(ST_Extent(%(expressions)s), 1), 2056)"
    allow_distinct = False
