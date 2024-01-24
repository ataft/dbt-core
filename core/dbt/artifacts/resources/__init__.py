from dbt.artifacts.resources.base import BaseArtifactNode

# alias to latest resource definitions
from dbt.artifacts.resources.v1.documentation import Documentation
from dbt.artifacts.resources.v1.semantic_layer_components import (
    WhereFilter,
    WhereFilterIntersection,
)
