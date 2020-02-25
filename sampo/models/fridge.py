from .sample import *

# TODO: change last_editor_id to lastuser_id from BaseMixIn
# TODO: setter getter handler, update, search, add, bulk add, batch add

class Fridge(Base, BaseMixIn):
    """
    class for fridge object
    storage for specimen and extraction
    """

    __tablename__ = 'fridges'

    uuid = Column(types.String, nullable=False)

    group_name = Column(types.String(32), ForeignKey('groups.name'), nullable=False)
    group = relationship(Group, backref=backref('fridges'))

    fridge_name = Column(types.String(32), nullable=False)

    fridge_type_id = Column(types.Integer, ForeignKey('eks.id'), nullable=False)
    fridge_type = EK.proxy('fridge_type_id', '@FRIDGETYPE')

    fridge_model = Column(types.String(32))
    temperature = Column(types.SmallInteger, nullable=False)

    fridge_location_id = Column(types.Integer, ForeignKey('eks.id'), nullable=False)
    fridge_location = EK.proxy('fridge_loc_id', '@FRIDGELOC')

    fridge_desc = Column(types.String(128))
    fridge_isFull = Column(types.Boolean, nullable=False, server_default=False)

    shelf = Column(types.SmallInteger, nullable=False)
    rack = Column(types.SmallInteger, nullable=False)
    depth_row = Column(types.SmallInteger, nullable=False)
    depth_column = Column(types.SmallInteger, nullable=False)

    creator_id = Column(types.Integer, ForeignKey('users.id'), nullable=False)
    creator = relationship(User, backref=backref('fridges'))


class Rack(Base):
    """
    class for rack object
    the part you can push on pull when ypu open up a fridge
    """

    __tablename__ = 'racks'

    id = Column(types.Integer, Sequence('rack_seq_id', optional=True), primary_key=True)
    uuid = Column(types.String, nullable=False)

    fridge_id = Column(types.Integer, ForeignKey('fridges.id'), nullable=False)
    fridge = relationship(Fridge, backref=backref('racks'))

    shelf_num = Column(types.SmallInteger, nullable=False)
    rack_post = Column(types.SmallInteger, nullable=False)
    num_row = Column(types.SmallInteger, nullable=False)
    num_column = Column(types.SmallInteger, nullable=False)


class Box(Base):
    """
    class for box object
    the one to put specimen and extraction before putting it inside the fridge
    """

    __tablename__ = 'boxes'

    id = Column(types.Integer, Sequence('box_seq_id', optional=True), primary_key=True)
    uuid = Column(types.String, nullable=False)
    box_name = Column(types.String(32), nullable=False)
    box_type = Column(types.SmallInteger, nullable=False)   # 0 = normal box, 1 = grid box

    rack_id = Column(types.Integer, ForeignKey('racks.id'), nullable=False)
    rack = relationship(Rack, backref=backref('boxes'))

    row = Column(types.SmallInteger, nullable=False)
    column = Column(types.SmallInteger, nullable=False)
    box_isFull = Column(types.Boolean, nullable=False, server_default=False)


class BoxCell(Base):
    """
    class for cell object
    imagine a spreadsheet is inside a grid type box
    """

    __tablename__ = 'box_cells'

    id = Column(types.Integer, Sequence('boxcell_seq_id', optional=True), primary_key=True)
    column = Column(types.SmallInteger, nullable=False)
    row = Column(types.SmallInteger, nullable=False)

    sample_id = Column(types.Integer, ForeignKey('samples.id'))
    sample = relationship(Sample, backref=backref('boxcells'))

    box_id = Column(types.Integer, ForeignKey('boxes.id'), nullable=False)
    box = relationship(Rack, backref=backref('boxcells'))

    cell_status = Column(types.String, nullable=False, server_default='E')
    # 'E'mpty, 'A'vailable, 'N'ot available
