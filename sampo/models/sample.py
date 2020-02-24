from .study import *


class Sample(Base):
    """
    base class for spec and ext
    """

    __tablename__ = 'samples'

    id = Column(types.Integer, Sequence('spec_seq_id', optional=True), primary_key=True)
    uuid = Column(types.String, nullable=False)
    box_id = Column(types.Integer, ForeignKey('boxes.id'), nullable=False, server_default=0)
    spext = Column(types.String(10))

    study_id = Column(types.Integer, ForeignKey('studies.id'), nullable=False)
    study = relationship(Study, backref=backref('samples'))

    subject_id = Column(types.Integer, ForeignKey('subjects.id'), nullable=False)
    subject = relationship(Subject, backref=backref('samples'))

    type_id = Column(types.Integer, ForeignKey('eks.id'), nullable=False)
    type = EK.proxy('sam_type_id', '@SAMTYPE')

    label = Column(types.String(32), nullable=False)
    date = Column(types.Date, nullable=False)  # TODO: add stamp

    storage_id = Column(types.Integer, ForeignKey('eks.id'), nullable=False)
    storage = EK.proxy('sam_storage_id', '@SAMSTORAGE')

    creator_id = Column(types.Integer, ForeignKey('users.id'), nullable=False)
    creator = relationship(User, backref=backref('samples'))

    desc = Column(types.String(128))
    status = Column(types.String(1), nullable=False, server_default='A')  # A:Available, N:Not available

    __mapper_args__ = {
        'polymorphic_identity': 'sample',
        'polymorphic_on': spext
    }

    # TODO: box getter


    def update(self, obj):
        if isinstance(obj, dict):
            if 'box_id' in obj:
                self.box_id = obj['box_id']
            if 'spext' in obj:
                self.spext = obj['spext']
            if 'study_id' in obj:
                self.study_id = obj['study_id']
            if 'subject_id' in obj:
                self.subject_id = obj['subject_id']
            if 'type_id' in obj:
                self.type_id = obj['type_id']
            if 'label' in obj:
                self.label = obj['label']
            if 'date' in obj:
                self.date = obj['date']
            if 'storage_id' in obj:
                self.storage_id = obj['storage_id']
            if 'creator_id' in obj:
                self.creator_id = obj['creator_id']
            if 'desc' in obj:
                self.desc = obj['desc']
            if 'status' in obj:
                self.status = obj['status']

            # specimen
            if 'aliquot' in obj:
                self.aliquot = obj['aliquot']
            if 'aliquot_total' in obj:
                self.aliquot_total = obj['aliquot_total']
            if 'spec_source_id' in obj:
                self.spec_source_id = obj['spec_source_id']

            # extraction
            if 'spec_id' in obj:
                self.spec_id = obj['spec_id']
            if 'ext_method_id' in obj:
                self.ext_method_id = obj['ext_method_id']


    @staticmethod
    def search(dbsession, samp):
        """search by name or label"""

        if type(samp) is int:
            pass
            # TODO: setter getter

        q = Sample.query(dbsession).filter(Sample.label == samp).first()
        if q: return q
        return q


    @staticmethod
    def searchPage(dbsession, label, study, spext, type, dstart, dend):
        """function for search page"""

        # TODO: snap new search page

        qresult = Sample.query(dbsession).filter(and_(Sample.date >= dstart, Sample.date <= dend)).all()

        if label:
            qresult.query(dbsession).filter(Sample.label == label).all()
        if study:
            tstudy = Study.search(study, dbsession)
            qresult.query(dbsession).filter(Sample.study_id == tstudy).all()
        if spext:
            qresult.query(dbsession).filter(Sample.spext == spext).all()
        if type:
            if type(type) is not int:
                type_id = EK._id(type)
            else:
                type_id = type
            qresult.query(dbsession).filter(Sample.type_id == type_id).all()

        if qresult: return qresult
        return None


class Specimen(Sample):
    """
    class for specimen
    """

    aliquot = Column(types.SmallInteger, nullable=False, server_default=1)
    aliquot_total = Column(types.SmallInteger, nullable=False, server_default=1)

    spec_source_id = Column(types.Integer, ForeignKey('eks.id'), nullable=False)
    spec_source = EK.proxy('spec_source_id', '@SPECSOURCE')

    __mapper_args__ = {
        'polymorphic_identity': 'specimen'
    }


    def add(self, dbsession, spext, study, subject, type, label, date, storage, creator, desc, box=None, status='A'):
        """add a specimen, with or without box id"""

        # TODO: not completed

        tUuid = UUID.new()
        if box:
            spec = Specimen(uuid=tUuid, box_id=box, spext=spext, study_id=study, subject_id=subject, type_id=type,
                            label=label, date=date, storage_id=storage, creator_id=creator, desc=desc, status=status)
        else:
            spec = Specimen(uuid=tUuid, spext=spext, study_id=study, subject_id=subject, type_id=type, label=label,
                            date=date, storage_id=storage, creator_id=creator, desc=desc)

        dbsession.add(spec)


class Extraction(Sample):
    """
    class for specimen's extractions
    """

    spec_id = Column(types.Integer, ForeignKey('sample.id'), nullable=False)
    spec = relationship(Specimen, backref=backref('extraction'))

    ext_method_id = Column(types.Integer, ForeignKey('eks.id'), nullable=False)
    ext_method = EK.proxy('ext_method_id', '@EXTSOURCE')

    __mapper_args__ = {
        'polymorphic_identity': 'extraction'
    }


    def add(self, dbsession, spext, study, subject, type, label, date, storage, creator, desc, box=None, status='A'):
        """add a extraction, with or without box id"""
        
        # TODO: not completed

        tUuid = UUID.new()
        if box:
            ext = Extraction(uuid=tUuid, box_id=box, spext=spext, study_id=study, subject_id=subject, type_id=type,
                            label=label, date=date, storage_id=storage, creator_id=creator, desc=desc, status=status)
        else:
            ext = Extraction(uuid=tUuid, spext=spext, study_id=study, subject_id=subject, type_id=type, label=label,
                            date=date, storage_id=storage, creator_id=creator, desc=desc)

        dbsession.add(ext)
