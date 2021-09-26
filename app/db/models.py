from db.mongo_serializers import MongoModel, ObjectID
from pydantic import Field


class Tweet(MongoModel):
    id: ObjectID = Field()
    text: str = Field()
    created_at: str = Field()
    author_id: str = Field()
