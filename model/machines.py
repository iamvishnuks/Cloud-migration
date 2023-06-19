from utils.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String


class VirtualMachine(Base):
    
    __tablename__ = 'vm'

    id = Column(String(40), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_locked = Column(Boolean, nullable=False, default=False)
    is_enabled = Column(Boolean, nullable=False, default=True)
    blueprint = Column(String(40), ForeignKey("blueprint.id"), nullable=False)
    hostname = Column(String(256))
    ip = Column(String(256))
    ip_created = Column(Boolean, nullable=False, default=False)
    network = Column(String(256))
    ports = Column(String(256))
    cpu_core = Column(String(256))
    cpu_model = Column(String(256))
    ram = Column(String(256))
    machine_type = Column(String(256))
    public_route = Column(Boolean, nullable=False, default=True)
    status = Column(Integer())
    image_id = Column(String(256))
    vm_id = Column(String(256))
    disk_clone = Column(String(256))
    nic_id = Column(String(256))
    artifact_location = Column(String(256))