from .sample import *

# TODO: getter setter handler, bulk add, make reports

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


    def add(self, dbsession, sample, user, date, ret):
        """add a transaction"""

        tUuid = UUID.new()
        tSam = Sample.search(dbsession, sample)
        tUsr = search_user(dbsession, user)
        trans = TakeReturn(uuid=tUuid, sample_id=tSam, user_id=tUsr, take_date=date, returned=ret)
        dbsession.add(trans)


    def addBatch(self, dbsession, sampleList, user, date):
        """add transaction by list"""

        tUsr = search_user(dbsession, user)

        for sample in sampleList:
            tSam = Sample.search(dbsession, sample)
            tSam.status = 'N'
            # TODO: update database
            self.add(dbsession, tSam, tUsr, date, None)


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


    def transaction(self, dbsession, sampleList, user, date, type):
        """take and return transaction"""

        if type is 'Take':
            status = 'N'
            self.addBatch(dbsession, sampleList, user, date)
        else:
            status = 'N'
            lTrans = list()
            # TODO: getter by sample list

            for trans in lTrans:
                trans.returned = True
                # TODO: update database

        Sample.changeStatus(dbsession, sampleList, status)
