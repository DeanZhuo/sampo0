from rhombus.models.ek import *
from rhombus.models.core import *
from rhombus.models.user import User, Group

from sqlalchemy.orm import backref
from sqlalchemy.sql.expression import func
import math


# TODO: bulk insert


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
    user = relationship(User, backref=backref('studies'))

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
    def getLastSub(study, loc, year):
        """get the last number from a study"""

        if checkYear(year) is False:
            RuntimeError('FATAL ERR: year not valid! 1899 < year < 2999, 4 digits format!')

        dbh = get_dbhandler()

        tStu = dbh.get_study(stud=study)
        tLoc = dbh.get_location(loc=loc)

        qResult = Subject.query(func.max(Subject.subject_number)). \
            filter(Subject.study_id == tStu).filter(Subject.location_id == tLoc). \
            filter(Subject.year == year).first()

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

    def addBatch(self, dbsession, count, study, loc, year, creator):
        """add batch subjects"""

        sub = self.getLastSub(study, loc, year)
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
