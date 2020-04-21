from . import *


class Study(Base):
    """
    class for study
    research or case for units and labs
    """

    __tablename__ = 'studies'

    id = Column(types.Integer, Sequence('study_seq_id', optional=True), primary_key=True)
    uuid = Column(types.String, nullable=False)

    group_id = Column(types.Integer, ForeignKey('groups.id'), nullable=False)
    group = relationship(Group, backref=backref('studies'))

    study_name = Column(types.String(32), nullable=False)
    study_number = Column(types.String(4), nullable=False, unique=True)

    creator_id = Column(types.Integer, ForeignKey('users.id'), nullable=False)
    creator = relationship(User, backref=backref('studies'))

    @staticmethod
    def add(dbsession, group, name, num, creator=None):
        """add new study"""

        dbh = get_dbhandler()

        if creator is None:
            tCrt = get_userid()
        else:
            tCrt = dbh.get_user(user=creator)
        tUuid = UUID.new()
        tGroup = dbh.get_group(group=group)
        study = Study(uuid=tUuid, group_id=tGroup, study_name=name, study_number=num.upper(),
                      creator_id=tCrt)
        dbsession.add(study)

    @staticmethod
    def bulk_insert(itemlist, dbsession):
        """
        bulk insert study
        itemlist = [ (group_id, study_name, study_number, creator_id) ]
        """

        for item in itemlist:
            group_id, study_name, study_number, creator_id = item[0], item[1], item[2], item[3]
            Study.add(dbsession, group_id, study_name, study_number, creator_id)

    def as_dict(self):
        """return as python dictionary"""

        return dict(group_id=self.group_id, study_name=self.study_name,
                    study_number=self.study_number, creator_id=self.creator_id)

    @staticmethod
    def dump(out, query=None):
        """dump to yaml"""

        if query is None:
            query = Study.query()
        yaml.safe_dump((x.as_dict() for x in query), out, default_flow_style=False)

    def update(self, obj):
        """update from dictionary"""

        if isinstance(obj, dict):
            if 'group_id' in obj:
                self.group_id = obj['group_id']
            if 'study_name' in obj:
                self.study_name = obj['study_name']
            if 'study_number' in obj:
                self.study_number = obj['study_number']
            if 'creator_id' in obj:
                self.creator_id = obj['creator_id']

            return self

        raise NotImplementedError('ERR: updating object uses dictionary object')

    @staticmethod
    def search(stdname, dbsession):
        """search study by name"""

        qResult = Study.query(dbsession).filter(Study.study_name == stdname).first()
        if qResult: return qResult
        return None


class Location(Base):
    """
    study location
    every study could happen in different locations
    """

    __tablename__ = 'locations'

    id = Column(types.Integer, Sequence('location_seq_id', optional=True), primary_key=True)
    name = Column(types.String(32), nullable=False)

    @staticmethod
    def add(dbsession, name):
        """add a location"""

        loc = Location(name=name)
        dbsession.add(loc)

    @staticmethod
    def bulk_insert(itemlist, dbsession):
        """
        bulk insert locations
        itemlist = [ (name) ]
        """

        for item in itemlist:
            name = item
            Location.add(dbsession, name)

    def as_dict(self):
        """return as python dictionary"""

        return dict(name=self.name)

    @staticmethod
    def dump(out, query=None):
        """dump to yaml"""

        if query is None:
            query = Location.query()
        yaml.safe_dump((x.as_dict() for x in query), out, default_flow_style=False)

    @staticmethod
    def search(locnm, dbsession):
        """search location by name"""

        qResult = Location.query(dbsession).filter(Location.name == locnm).first()
        if qResult: return qResult
        return None


class Subject(Base):
    """
    class for study's subjects
    people with samples to take
    """

    __tablename__ = 'subjects'

    id = Column(types.Integer, Sequence('subject_seq_id', optional=True), primary_key=True)
    uuid = Column(types.String, nullable=False)

    study_id = Column(types.Integer, ForeignKey('studies.id'), nullable=False)
    study = relationship(Study, backref=backref('subjects'))

    subject_number = Column(types.SmallInteger, nullable=False, unique=True)

    location_id = Column(types.Integer, ForeignKey('locations.id'), nullable=False)
    location = relationship(Location, backref=backref('subjects'))

    year = Column(types.SmallInteger, nullable=False)

    creator_id = Column(types.Integer, ForeignKey('users.id'), nullable=False)
    creator = relationship(User, backref=backref('subjects'))

    @staticmethod
    def getSub(dbsession, study, loc, year, last=False):
        """get the last subject or every subject from the study with the location and year variable"""

        if checkYear(year) is False:
            RuntimeError('FATAL ERR: year not valid! 1899 < year < 2999, 4 digits format!')

        dbh = get_dbhandler()

        tStu = dbh.get_study(stud=study)
        tLoc = dbh.get_location(loc=loc)

        if last:
            qResult = Subject.query(dbsession). \
                filter(Subject.study_id == tStu).filter(Subject.location_id == tLoc). \
                filter(Subject.year == year).order_by(Subject.id.desc()).first()
        else:
            qResult = Subject.query(dbsession). \
                filter(Subject.study_id == tStu).filter(Subject.location_id == tLoc). \
                filter(Subject.year == year).all()

        if qResult: return qResult
        return None

    @staticmethod
    def add(dbsession, num, study, loc, year, creator=None):
        """add a subject"""

        dbh = get_dbhandler()

        if creator is None:
            tCrt = get_userid()
        else:
            tCrt = dbh.get_user(user=creator)

        tUuid = UUID.name()
        tStu = dbh.get_study(stud=study)
        tLoc = dbh.get_location(loc=loc)
        sub = Subject(uuid=tUuid, study_id=tStu, subject_number=num, location_id=tLoc, year=year,
                      creator_id=tCrt)
        dbsession.add(sub)

    @staticmethod
    def addBatch(dbsession, count, study, loc, year, creator):
        """add batch subjects"""

        sub = Subject.getSub(dbsession, study, loc, year)
        if sub is None:
            maxNum = 0
        else:
            maxNum = sub.subject_number

        for inc in range(count):
            tNum = maxNum + inc + 1
            Subject.add(dbsession, tNum, study, loc, year, creator)

    @staticmethod
    def bulk_insert(itemlist, dbsession):
        """
        bulk insert subject
        itemlist = [ (number, study, location, year, creator) ]
        """

        for item in itemlist:
            number, study, location, year, creator = item[0], item[1], item[2], item[3], item[4]
            Subject.add(dbsession, number, study, location, year, creator)

    def as_dict(self):
        """return as python dictionary"""

        return dict(number=self.subject_number, study=self.study_id, location=self.location_id,
                    year=self.year, creator=self.creator_id)

    @staticmethod
    def dump(out, query=None):
        """dump to yaml"""

        if query is None:
            query = Subject.query()
        yaml.safe_dump((x.as_dict() for x in query), out, default_flow_style=False)

    def update(self, obj):
        """update from dictionary"""

        if isinstance(obj, dict):
            if 'study_id' in obj:
                self.study_id = obj['study_id']
            if 'subject_number' in obj:
                self.subject_number = obj['subject_number']
            if 'location_id' in obj:
                self.location_id = obj['location_id']
            if 'year' in obj:
                self.year = obj['year']
            if 'creator_id' in obj:
                self.creator_id = obj['creator_id']

            return self

        raise NotImplementedError('ERR: updating object uses dictionary object')


def checkYear(year):
    """year check sanity"""

    if 1899 < year < 2999:
        digits = int(math.log10(year)) + 1
        return digits == 4
    else:
        return False
