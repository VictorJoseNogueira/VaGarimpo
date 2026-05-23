from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    ListField,
    StringField,
    URLField,
    DynamicEmbeddedDocument
)


class LlmResponse(EmbeddedDocument):
    status = StringField()
    match_percentage = FloatField()
    motivation = StringField()


# Modelos auxiliares para os objetos aninhados
class JobDetails(DynamicEmbeddedDocument):
    category = StringField()
    subcategory = StringField()
    budget = StringField()
    experience_level = StringField()
    visibility = StringField()
    proposals = StringField()
    interested = StringField()
    exclude_proposals = StringField()
    time_remaining = StringField()
    minimum_value = StringField()


# Documento principal do MongoEngine
class JobData(Document):
    title = StringField(required=True)
    link = URLField(required=True, unique=True)
    description = StringField()
    skills = ListField(StringField())
    details = EmbeddedDocumentField(JobDetails)
    llm_response = EmbeddedDocumentField(LlmResponse)
    userName = StringField()

    # Substitui a class Settings do Beanie pelo dicionário meta do MongoEngine
    meta = {"collection": "jobs_collection"}
