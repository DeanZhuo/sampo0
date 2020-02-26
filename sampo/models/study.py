from rhombus.models.core import *
from rhombus.models.user import User, Group
from sampo.models import search_user
from sqlalchemy.sql.expression import func
import math

# TODO: setter getter handler, bulk insert


class Study(Base):
    """
    class for study
    research or case for units and labs
    """

    __tablename__ = 'studies'

    id = Column(types.Integer, Sequence('study_seq_id', optional=True), primary_key=True)
    uuid = Column(types.String, nullable=False)
    group_id = Column(types.Integer, ForeignKey('groups.id'), nullable=False)
    study_name = Column(types.String(32), nullable=False)
    study_number = Column(types.String(4), nullable=False, unique=True)
    creator_id = Column(types.Integer, ForeignKey('users.id'), nullable=False)

    user = relationship(User, backref=backref('studies'))


    def add(self, dbsession, group, name, num, creator):
        """add new study"""

        tUuid = UUID.new()
        tGroup = Group.search(group, dbsession)
        tCreator = search_user(dbsession, creator)
        study = Study(uuid=tUuid, group_id=tGroup, study_name=name, study_number=num.upper(), creator_id=tCreator)
        dbsession.add(study)


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
        """search study, id or name"""

        if type(stdname) == int:
            pass
            # TODO: setter getter
        qResult = Study.query(dbsession).filter(Study.study_name == stdname).first()
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
    subject_number = Column(types.SmallInteger, nullable=False, unique=True)
    location_id = Column(types.Integer, ForeignKey('locations.id'), nullable=False)
    year = Column(types.SmallInteger, nullable=False)
    creator_id = Column(types.Integer, ForeignKey('users.id'), nullable=False)

    study = relationship(Study, backref=backref('subjects'))


    @staticmethod
    def getLastSub(dbsession, study, loc, year):
        """get the last number from a study"""

        if checkYear(year) is False:
            RuntimeError('FATAL ERR: year not valid! 1899 < year < 2999, 4 digits format!')

        tStu = Study.search(study, dbsession)
        tLoc = Location.search(loc, dbsession)

        qResult = Subject.query(func.max(Subject.subject_number)).\
            filter(Subject.study_id == tStu).filter(Subject.location_id == tLoc).\
            filter(Subject.year == year).first()

        if qResult: return qResult
        return None


    def add(self, dbsession, num, study, loc, year, creator):
        """add a subject"""

        tUuid = UUID.name()
        tStu = Study.search(study, dbsession)
        tLoc = Location.search(loc, dbsession)
        tCrt = search_user(dbsession, creator)
        sub = Subject(uuid=tUuid, study_id=tStu, subject_number=num, location_id=tLoc, year=year,
                      creator_id=tCrt)
        dbsession.add(sub)


    def addBatch(self, dbsession, count, study, loc, year, creator):
        """add batch subjects"""

        sub = self.getLastSub(dbsession, study, loc, year)
        if sub is None:
            maxNum = 0
        else:
            maxNum = sub.subject_number

        for inc in range(count):
            tNum = maxNum + count + 1
            self.add(dbsession, tNum, study, loc, year, creator)


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


class Location(Base):
    """
    study location
    every study could happen in different locations
    """

    __tablename__ = 'locations'

    id = Column(types.Integer, Sequence('location_seq_id', optional=True), primary_key=True)
    name = Column(types.String(32), nullable=False)


    def add(self, dbsession, name):
        """add a location"""

        loc = Location(name=name)
        dbsession.add(loc)


    @staticmethod
    def search(locnm, dbsession):
        """search location by id or name"""

        if type(locnm) == int:
            pass
            # TODO: setter getter
        qResult = Location.query(dbsession).filter(Location.name == locnm).first()
        if qResult: return qResult
        return None
