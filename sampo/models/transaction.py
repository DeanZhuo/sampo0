from .sample import *

# TODO: getter setter handler, update, search bulk add, batch add, add, make reports, transactions

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
    