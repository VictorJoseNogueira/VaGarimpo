from mongoengine import (
    Document,
    EmailField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    ListField,
    StringField,
)


class PersonalData(EmbeddedDocument):
    name = StringField(required=True, max_length=100)
    email = EmailField()
    location = StringField(required=True, max_length=100)


class ProfessionalExperience(EmbeddedDocument):
    company = StringField(required=True, max_length=100)
    role = StringField(required=True, max_length=100)
    period = StringField(required=True, max_length=100)
    activities = ListField(StringField())


class Education(EmbeddedDocument):
    institution = StringField(required=True, max_length=100)
    course = StringField(required=True, max_length=100)
    completion = StringField(required=True, max_length=100)
    type = StringField(required=True, max_length=100)


class Language(EmbeddedDocument):
    language = StringField(required=True, max_length=100)
    level = StringField(required=True, max_length=100)


# Documento principal
class ResumeData(Document):
    personal_data = EmbeddedDocumentField(PersonalData, required=True)
    professional_summary = StringField(required=True, max_length=500)
    professional_experience = ListField(
        EmbeddedDocumentField(ProfessionalExperience)
    )
    education = ListField(EmbeddedDocumentField(Education))
    technical_skills = ListField(StringField())
    languages = ListField(EmbeddedDocumentField(Language))
    certifications = ListField(StringField())

    meta = {"collection": "resume_collection"}
