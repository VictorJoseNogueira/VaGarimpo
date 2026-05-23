from mongoengine import (
    Document,
    DynamicEmbeddedDocument,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    ListField,
    StringField,
    URLField,
)


from mongoengine import DynamicEmbeddedDocument, StringField, FloatField, ListField

class LlmResponse(DynamicEmbeddedDocument):
    first_match=StringField()
    status = StringField()
    match_percentage = FloatField()
    strengths = ListField(StringField())
    weaknesses = ListField(StringField())
    payments = StringField()
    proposta = StringField()
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
