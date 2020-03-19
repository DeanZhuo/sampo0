from sqlalchemy import func

from .sample import *
from datetime import date


class TakeReturn(Base):
    """
    class for take and return transaction
    use to track specimen and extraction not yet returned
    """

    __tablename__ = 'take_return'

    id = Column(types.Integer, Sequence('takereturn_sec_id', optional=True), primary_key=True)
    uuid = Column(types.String, nullable=False)

    sample_id = Column(types.Integer, ForeignKey('samples.id'), nullable=False)
    sample = relationship(Sample, backref=backref('takereturn'))

    user_id = Column(types.Integer, ForeignKey('users.id'), nullable=False)
    user = relationship(User, backref=backref('takereturn'))

    take_date = Column(types.Date, nullable=False)  # TODO: add stamp
    returned = Column(types.Boolean, nullable=False, server_default=False)

    @staticmethod
    def add(dbsession, sample, user, date, ret):
        """add a transaction"""

        dbh = get_dbhandler()

        if user is None:
            tUsr = get_userid()
        else:
            tUsr = dbh.get_user(user=user)
        tUuid = UUID.new()
        tSam = dbh.get_sample(sam=sample)
        trans = TakeReturn(uuid=tUuid, sample_id=tSam, user_id=tUsr, take_date=date, returned=ret)
        dbsession.add(trans)

    @staticmethod
    def addBatch(dbsession, sampleList, user, date):
        """add transaction by list"""

        dbh = get_dbhandler()

        if user is None:
            tUsr = get_userid()
        else:
            tUsr = dbh.get_user(user=user)

        for sample in sampleList:
            tSam = dbh.get_sample(sam=sample)
            tSam.status = 'N'
            TakeReturn.add(dbsession, tSam, tUsr, date, None)

    @staticmethod
    def bulk_insert(itemlist, dbsession):
        """
        bulk insert box
        itemlist = [ (sample, user, take, ret) ]
        """

        for item in itemlist:
            sample, user, take, ret = item[0], item[1], item[2], item[3]
            TakeReturn.add(dbsession, sample, user, take, ret)

    def as_dict(self):
        """return as python dictionary"""

        return dict(sample=self.sample_id, user=self.user_id, take=self.take_date, ret=self.returned)

    @staticmethod
    def dump(out, query=None):
        """dump to yaml"""
        if query is None:
            query = TakeReturn.query()
        yaml.safe_dump((x.as_dict() for x in query), out, default_flow_style=False)

    def update(self, obj):
        """update from dictionary"""

        if isinstance(obj, dict):
            if 'sample_id' in obj:
                self.sample_id = obj['sample_id']
            if 'user_id' in obj:
                self.user_id = obj['user_id']
            if 'take_date' in obj:
                self.take_date = obj['take_date']
            if 'returned' in obj:
                self.returned = obj['returned']

            return self

        raise NotImplementedError('ERR: updating object uses dictionary object')

    @staticmethod
    def search(sample):
        """search by sample"""

        if isinstance(sample, int) is not True:
            dbh = get_dbhandler()
            tSam = dbh.get_sample(sam=sample)
        else:
            tSam = sample

        q = TakeReturn.query(dbsession).filter(TakeReturn.sample_id == tSam,
                                               TakeReturn.returned == False).first()
        if q: return q
        return None

    @staticmethod
    def transaction(dbsession, sampleList, user, date, type):
        """take and return transaction"""

        if type == 'take':
            status = 'N'
            TakeReturn.addBatch(dbsession, sampleList, user, date)
        else:
            status = 'A'
            for sample in sampleList:
                tTrans = TakeReturn.search(sample)
                tTrans.returned = True

        Sample.changeStatus(sampleList, status)

    @staticmethod
    def sampleReport():
        """return list of not returned sample"""

        dbh = get_dbhandler()
        return dbh.get_takereturn(take=True)

    @staticmethod
    def annualReport(dbsession, year):
        """return annual report by year"""

        checkYear(year)
        start = date(year-1, 12, 31)
        end = date(year+1, 1, 1)
        qResult = dbsession.query(Group.name, Study.study_name, Location.name,
                                  func.count(Subject), func.count(Sample))\
            .outerjoin(Study, Group.id == Study.group_id)\
            .outerjoin(Subject, Study.id == Subject.study_id)\
            .outerjoin(Location, Location.id == Subject.location_id)\
            .outerjoin(Sample, Subject.id == Sample.subject_id)\
            .filter(Sample.date.between(start, end))\
            .order_by(Group.name)\
            .order_by(Study.study_name).all()

        """
            select groups.name, studies.study_name, location.name, count(subject), count(sample)
            from groups 
            join studies on groups.id = studies.group_id
            join subjects on studies.id = subjects.study_id
            join locations on subjects.location_id = locations.id
            join samples on subjects.id = samples.subject_id
            where subjects.date between(start, end)
            sort by groups.name
        """

        return qResult

