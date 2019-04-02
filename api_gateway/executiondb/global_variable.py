import logging
from uuid import uuid4, UUID

from sqlalchemy import Column, String
from sqlalchemy_utils import UUIDType, JSONType
from marshmallow import fields, EXCLUDE
from marshmallow_sqlalchemy import field_for

from api_gateway.executiondb.schemas import ExecutionBaseSchema
from api_gateway.executiondb import Execution_Base

logger = logging.getLogger(__name__)


# TODO: add in an is_encrypted bool for globals
class GlobalVariable(Execution_Base):
    """SQLAlchemy ORM class for Global, which are variables that can be dynamically loaded into workflow
       execution

    Attributes:
        id_ (UUID): The ID of the object
        name (str): The name of the environment variable
        value (any): The value of the object
        description (str): A description of the object

    """
    __tablename__ = 'global_variable'
    id_ = Column(UUIDType(binary=False), primary_key=True, nullable=False, default=uuid4)
    name = Column(String(80))
    value = Column(JSONType, nullable=False)
    description = Column(String(255))

    def __init__(self, name, value, id_=None, description=None):
        if id_:
            if not isinstance(id_, UUID):
                self.id_ = UUID(id_)
            else:
                self.id_ = id_
        self.name = name
        self.value = value
        self.description = description if description else ""


class GlobalVariableSchema(ExecutionBaseSchema):
    """Schema for global variables
    """
    name = field_for(GlobalVariable, 'name', required=True)
    value = fields.Raw()
    description = field_for(GlobalVariable, 'description')

    class Meta:
        model = GlobalVariable
        unknown = EXCLUDE

