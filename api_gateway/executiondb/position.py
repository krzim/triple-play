import logging
from uuid import uuid4

from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy_utils import UUIDType
from marshmallow import fields, EXCLUDE
from marshmallow_sqlalchemy import field_for

from api_gateway.helpers import validate_uuid4
from api_gateway.executiondb.schemas import ExecutionBaseSchema
from api_gateway.executiondb import Execution_Base

logger = logging.getLogger(__name__)


class Position(Execution_Base):
    __tablename__ = 'position'
    id_ = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    action_id = Column(UUIDType(binary=False), ForeignKey('action.id_', ondelete='CASCADE'))
    condition_id = Column(UUIDType(binary=False), ForeignKey('condition.id_', ondelete='CASCADE'))
    transform_id = Column(UUIDType(binary=False), ForeignKey('transform.id_', ondelete='CASCADE'))
    trigger_id = Column(UUIDType(binary=False), ForeignKey('trigger.id_', ondelete='CASCADE'))

    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)

    def __init__(self, x, y, id_=None):
        """Initializes a new Position object. An Action has a Position object.

        Args:
            x (float): The X coordinate of the Action.
            y (float): The Y coordinate of the Action.
        """
        self.id_ = validate_uuid4(id_)
        self.x = x
        self.y = y


class PositionSchema(ExecutionBaseSchema):
    """Schema for positions
    """
    x = field_for(Position, 'x', required=True)
    y = field_for(Position, 'y', required=True)

    class Meta:
        model = Position
        unknown = EXCLUDE
        # exclude = ('id_',)
