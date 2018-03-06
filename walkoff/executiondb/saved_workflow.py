import logging

from sqlalchemy import Column, PickleType
from sqlalchemy_utils import UUIDType

from walkoff.executiondb import Device_Base

logger = logging.getLogger(__name__)


class SavedWorkflow(Device_Base):
    __tablename__ = 'saved_workflow'
    workflow_execution_id = Column(UUIDType(binary=False), primary_key=True)
    workflow_id = Column(UUIDType(binary=False), nullable=False)
    action_id = Column(UUIDType(binary=False), nullable=False)
    accumulator = Column(PickleType(), nullable=False)
    app_instances = Column(PickleType(), nullable=False)

    def __init__(self, workflow_execution_id, workflow_id, action_id, accumulator, app_instances):
        """Initializes a SavedWorkflow object. This is used when a workflow pauses execution, and must be reloaded
            at a later point.

        Args:
            workflow_execution_id (str): The workflow execution UID that this saved state refers to.
            workflow_id (str): The ID of the workflow that this saved state refers to.
            action_id (str): The currently executing action ID.
            accumulator (dict): The accumulator up to this point in the workflow.
            app_instances (str): The pickled app instances for the saved workflow
        """
        self.workflow_execution_id = workflow_execution_id
        self.workflow_id = workflow_id
        self.action_id = action_id
        self.accumulator = accumulator
        self.app_instances = app_instances
