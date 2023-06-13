from typing import Any, Dict, List, Optional
from datetime import datetime


from dataclasses import dataclass, field

from dbt.contracts.util import (
    AdditionalPropertiesMixin,
    ArtifactMixin,
    BaseArtifactMetadata,
    schema_version,
)
from dbt.contracts.graph.unparsed import NodeVersion
from dbt.contracts.graph.nodes import ManifestOrPublicNode
from dbt.dataclass_schema import dbtClassMixin, ExtensibleDbtClassMixin
from dbt.node_types import AccessType, NodeType


@dataclass
class ProjectDependency(AdditionalPropertiesMixin, ExtensibleDbtClassMixin):
    name: str
    _extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectDependencies(dbtClassMixin):
    projects: List[ProjectDependency] = field(default_factory=list)


@dataclass
class PublicationMetadata(BaseArtifactMetadata):
    dbt_schema_version: str = field(
        default_factory=lambda: str(PublicationArtifact.dbt_schema_version)
    )
    adapter_type: Optional[str] = None
    quoting: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PublicModel(dbtClassMixin, ManifestOrPublicNode):
    """Used to represent cross-project models"""

    name: str
    package_name: str
    unique_id: str
    relation_name: str
    database: Optional[str] = None
    schema: Optional[str] = None
    identifier: Optional[str] = None
    version: Optional[NodeVersion] = None
    latest_version: Optional[NodeVersion] = None
    # list of model unique_ids
    public_node_dependencies: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    deprecation_date: Optional[datetime] = None

    @property
    def is_latest_version(self) -> bool:
        return self.version is not None and self.version == self.latest_version

    # Needed for ref resolution code
    @property
    def resource_type(self):
        return NodeType.PublicModel

    # Needed for ref resolution code
    @property
    def access(self):
        return AccessType.Public

    @property
    def search_name(self):
        if self.version is None:
            return self.name
        else:
            return f"{self.name}.v{self.version}"

    @property
    def depends_on_nodes(self):
        return []

    @property
    def depends_on_public_nodes(self):
        return []

    @property
    def is_public_node(self):
        return True

    @property
    def is_versioned(self):
        return self.version is not None

    @property
    def alias(self):
        return self.identifier

    @property
    def fqn(self):
        return [self.package_name, self.name]

    def to_ls_dict(self, **kwargs):
        dct = self.to_dict(**kwargs)
        dct["resource_type"] = NodeType.PublicModel.value
        return dct


@dataclass
class PublicationMandatory:
    project_name: str


@dataclass
@schema_version("publication", 1)
class PublicationArtifact(ArtifactMixin, PublicationMandatory):
    public_models: Dict[str, PublicModel] = field(default_factory=dict)
    metadata: PublicationMetadata = field(default_factory=PublicationMetadata)
    # list of project name strings
    dependencies: List[str] = field(default_factory=list)


@dataclass
class PublicationConfig(ArtifactMixin, PublicationMandatory):
    """This is for the part of the publication artifact which is stored in
    the internal manifest. The public_nodes are stored separately in the manifest,
    and just the unique_ids of the public models are stored here."""

    metadata: PublicationMetadata = field(default_factory=PublicationMetadata)
    # list of project name strings
    dependencies: List[str] = field(default_factory=list)
    public_node_ids: List[str] = field(default_factory=list)

    @classmethod
    def from_publication(cls, publication: PublicationArtifact):
        return cls(
            project_name=publication.project_name,
            metadata=publication.metadata,
            dependencies=publication.dependencies,
            public_node_ids=list(publication.public_models.keys()),
        )
