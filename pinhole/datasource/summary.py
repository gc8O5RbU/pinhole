from pinhole.datasource.utils import hexstr2str, str2hexstr
from pydantic.dataclasses import dataclass
from pydantic.root_model import RootModel


@dataclass(repr=False)
class Summary:
    # among the following two ids, only one should be present
    # while another should be empty
    document_id: int
    publication_id: int
    _model: str
    _content: str

    def __repr__(self) -> str:
        return f"<Summary of document {self.document_id} />"

    @property
    def model(self) -> str:
        return hexstr2str(self._model)

    @property
    def content(self) -> str:
        return hexstr2str(self._content)

    @classmethod
    def build(cls, document_id: int, publication_id: int, model: str, publisher: str) -> 'Summary':
        if document_id >= 0 and publication_id >= 0:
            raise ValueError(f"invalid summary, one of document id and publication id should be -1")

        _model = str2hexstr(model)
        _publisher = str2hexstr(publisher)
        return Summary(document_id, publication_id, _model, _publisher)

    @classmethod
    def from_json(cls, content: str) -> 'Summary':
        return RootModel[Summary].model_validate(content).root
