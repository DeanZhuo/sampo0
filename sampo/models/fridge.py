from .sample import *


# TODO: bulk add, check move destination
# TODO: shelf = level, add isFull to rack database


class Fridge(Base):
    """
    class for fridge object
    storage for specimen and extraction
    """

    __tablename__ = 'fridges'

    id = Column(types.Integer, Sequence('fridge_sec_id', optional=True), primary_key=True)
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
    # TODO: check status at starting and after moving

    shelf = Column(types.SmallInteger, nullable=False)
    rack = Column(types.SmallInteger, nullable=False)
    depth_row = Column(types.SmallInteger, nullable=False)
    depth_column = Column(types.SmallInteger, nullable=False)

    creator_id = Column(types.Integer, ForeignKey('users.id'), nullable=False)
    creator = relationship(User, backref=backref('fridges'))

    last_user_id = Column(types.Integer, ForeignKey('users.id'), nullable=False)
    last_user = relationship(User, backref=backref('fridges'))

    @staticmethod
    def add(group, name, type, model, temp, loc, desc, full, shelf, rack, row, column,
            creator=None, last_user=None):
        """add a fridge"""

        dbh = get_dbhandler()

        if creator is None:
            tCrt = get_userid()
        else:
            tCrt = dbh.get_user(user=creator)

        if last_user is None:
            tLUsr = get_userid()
        else:
            tLUsr = dbh.get_user(user=last_user)

        tUuid = UUID.new()
        tGroup = dbh.get_group(group=group)
        tGName = tGroup.name
        tType = EK.getid(type, dbsession, grp='@FRIDGETYPE')
        tLoc = EK.getid(loc, dbsession, grp='@FRIDGELOC')
        fridge = Fridge(uuid=tUuid, group_name=tGName, fridge_name=name, fridge_type_id=tType,
                        fridge_model=model, temperature=temp, fridge_location_id=tLoc, fridge_desc=desc,
                        fridge_isFull=full, shelf=shelf, rack=rack, depth_row=row, depth_column=column,
                        creator_id=tCrt, last_user_id=tLUsr)
        dbsession.add(fridge)

    def update(self, obj):
        """update from dictionary"""

        if isinstance(obj, dict):
            if 'group_name' in obj:
                self.group_name = obj['group_name']
            if 'fridge_name' in obj:
                self.fridge_name = obj['fridge_name']
            if 'fridge_type_id' in obj:
                self.fridge_type_id = obj['fridge_type_id']
            if 'fridge_model' in obj:
                self.fridge_model = obj['fridge_model']
            if 'temperature' in obj:
                self.temperature = obj['temperature']
            if 'fridge_location_id' in obj:
                self.fridge_location_id = obj['fridge_location_id']
            if 'fridge_desc' in obj:
                self.fridge_desc = obj['fridge_desc']
            if 'fridge_isFull' in obj:
                self.fridge_isFull = obj['fridge_isFull']
            if 'shelf' in obj:
                self.shelf = obj['shelf']
            if 'rack' in obj:
                self.rack = obj['rack']
            if 'depth_row' in obj:
                self.depth_row = obj['depth_row']
            if 'depth_column' in obj:
                self.depth_column = obj['depth_column']
            if 'creator_id' in obj:
                self.creator_id = obj['creator_id']
            if 'last_user_id' in obj:
                self.last_user_id = obj['last_user_id']

            return self

        raise NotImplementedError('ERR: updating object uses dictionary object')

    @staticmethod
    def search(dbsession, fridge):
        """search by name"""

        q = Fridge.query(dbsession).filter(Fridge.fridge_name == fridge).first()
        if q: return q
        return None

    def edit(self, dbsession, temp, loc, desc):
        """edit fidge"""

        self.temperature = temp
        tLoc = EK.getid(loc, dbsession, grp='@FRIDGELOC')
        self.fridge_location_id = tLoc
        self.fridge_desc = desc

        pass
        # TODO: update to database

    @staticmethod
    def checkFull(fridge):
        """check fridge status"""

        dbh = get_dbhandler()
        tFridge = dbh.get_fridge(frid=fridge)
        lRacks = list()
        # TODO: get list of racks by fridge id

        for rack in lRacks:
            if rack.rack_isFull is False:
                return False
        return True


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
    rack_isFull = Column(types.Boolean, nullable=False, server_default=False)
    # TODO: check status at starting and after moving

    @staticmethod
    def add(dbsession, fridge, shelf, pos, row, col, full):
        """add a rack"""

        dbh = get_dbhandler()
        tUuid = UUID.new()
        tFridge = dbh.get_fridge(frid=fridge)
        rack = Rack(uuid=tUuid, fridge_id=tFridge, shelf_num=shelf, rack_post=pos,
                    num_row=row, num_column=col, rack_isFull=full)
        dbsession.add(rack)

    def update(self, obj):
        """update from dictionary"""

        if isinstance(obj, dict):
            if 'fridge_id' in obj:
                self.fridge_id = obj['fridge_id']
            if 'shelf_num' in obj:
                self.shelf_num = obj['shelf_num']
            if 'rack_post' in obj:
                self.rack_post = obj['rack_post']
            if 'num_row' in obj:
                self.num_row = obj['num_row']
            if 'num_column' in obj:
                self.num_column = obj['num_column']
            if 'rack_isFull' in obj:
                self.rack_isFull = obj['rack_isFull']

            return self

        raise NotImplementedError('ERR: updating object uses dictionary object')

    def move(self, rack):
        """swap with an empty rack"""

        dbh = get_dbhandler()
        tRack = dbh.get_rack(rck=rack)
        if self.checkStatus(tRack) is not 'empty':
            return ''

        if self.num_row == tRack.shelf_num and self.num_column == tRack.num_column:
            self.fridge_id, tRack.fridge_id = tRack.fridge_id, self.fridge_id
            self.shelf_num, tRack.shelf_num = tRack.shelf_num, self.shelf_num
            self.rack_post, tRack.rack_post = tRack.rack_post, self.rack_post

            # TODO: update database

    @staticmethod
    def checkStatus(rack):
        """check rack status"""

        dbh = get_dbhandler()
        tRack = dbh.get_rack(rck=rack)
        lBox = list()
        # TODO: get list of box by rack id

        if lBox:
            for box in lBox:
                if box.box_isFull:
                    return 'full'
            return 'available'
        return 'empty'


class Box(Base):
    """
    class for box object
    the one to put specimen and extraction before putting it inside the fridge
    """

    __tablename__ = 'boxes'

    id = Column(types.Integer, Sequence('box_seq_id', optional=True), primary_key=True)
    uuid = Column(types.String, nullable=False)
    box_name = Column(types.String(32), nullable=False)
    box_type = Column(types.SmallInteger, nullable=False)  # 0 = normal box, 1 = grid box

    rack_id = Column(types.Integer, ForeignKey('racks.id'), nullable=False)
    rack = relationship(Rack, backref=backref('boxes'))

    row = Column(types.SmallInteger, nullable=False)
    column = Column(types.SmallInteger, nullable=False)
    box_isFull = Column(types.Boolean, nullable=False, server_default=False)  # normal always False
    # TODO: check status at starting and after moving

    @staticmethod
    def add(dbsession, name, type, rack, row, col, full):
        """add a box"""

        dbh = get_dbhandler()
        tUuid = UUID.new()
        if type.lower() == 'grid' or type == 1:
            tType = 1
        else:
            tType = 0
        tRack = dbh.get_rack(rck=rack)
        box = Box(uuid=tUuid, box_name=name, box_type=tType, rack_id=tRack, row=row, column=col,
                  box_isFull=full)
        dbsession.add(box)

    def update(self, obj):
        """update from dictionary"""

        if isinstance(obj, dict):
            if 'box_name' in obj:
                self.box_name = obj['box_name']
            if 'box_type' in obj:
                self.box_type = obj['box_type']
            if 'rack_id' in obj:
                self.rack_id = obj['rack_id']
            if 'row' in obj:
                self.row = obj['row']
            if 'column' in obj:
                self.column = obj['column']
            if 'box_isFull' in obj:
                self.box_isFull = obj['box_isFull']

            return self

        raise NotImplementedError('ERR: updating object uses dictionary object')

    @staticmethod
    def search(dbsession, boxname):
        """search by name"""

        q = Box.query(dbsession).filter(Box.box_name == boxname).first()
        if q: return q
        return None

    def move(self, rack, row, col):
        """move box"""

        dbh = get_dbhandler()
        tRack = dbh.get_rack(rck=rack)
        self.rack_id = tRack
        self.row = row
        self.column = col
        # TODO: update database

    @staticmethod
    def checkFull(box):
        """check box status"""

        dbh = get_dbhandler()
        tBox = dbh.get_box(bx=box)
        lCells = list()
        # TODO: get list of cells by box id

        for cell in lCells:
            if cell.cell_status == 'E':
                return False
        return True


class BoxCell(Base):
    """
    class for cell object
    imagine a spreadsheet is inside a grid type box
    """

    __tablename__ = 'box_cells'

    id = Column(types.Integer, Sequence('boxcell_seq_id', optional=True), primary_key=True)
    column = Column(types.SmallInteger, nullable=False)
    row = Column(types.String(1), nullable=False)

    sample_id = Column(types.Integer, ForeignKey('samples.id'))
    sample = relationship(Sample, backref=backref('boxcells'))

    box_id = Column(types.Integer, ForeignKey('boxes.id'), nullable=False)
    box = relationship(Rack, backref=backref('boxcells'))

    cell_status = Column(types.String, nullable=False, server_default='E')
    # 'E'mpty, 'A'vailable, 'N'ot available

    @staticmethod
    def add(dbsession, col, row, sample, box, stat):
        """add a cell"""

        dbh = get_dbhandler()
        tSam = dbh.get_sample(sam=sample)
        tBox = dbh.get_box(bx=box)
        cell = BoxCell(column=col, row=row, sample_id=tSam, box_id=tBox, cell_status=stat)
        dbsession.add(cell)

    def addBatch(self, dbsession, box):
        """add cell for box"""

        for col in range(1, 9):
            for row in range(1, 9):
                self.add(dbsession, col, row, None, box, False)

    def update(self, obj):
        """update from dictionary"""

        if isinstance(obj, dict):
            if 'column' in obj:
                self.column = obj['column']
            if 'row' in obj:
                self.row = obj['row']
            if 'sample_id' in obj:
                self.sample_id = obj['sample_id']
            if 'box_id' in obj:
                self.box_id = obj['box_id']
            if 'cell_status' in obj:
                self.cell_status = obj['cell_status']

            return self

        raise NotImplementedError('ERR: updating object uses dictionary object')
