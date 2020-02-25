from .study import *
from rhombus.models.ek import *


class Sample(Base):
    """
    base/parent class for spec and ext
    the one stored inside boxes and fridges
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

    # TODO: bulk insert from dict, assign box


    def update(self, obj):
        """update from dictionary"""

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
    def searchPage(dbsession, label, study, spext, type, dStart, dEnd):
        """function for search page"""

        # TODO: snap new search page

        qResult = Sample.query(dbsession).filter(and_(Sample.date >= dStart, Sample.date <= dEnd)).all()

        if label:
            qResult.query(dbsession).filter(Sample.label == label).all()
        if study:
            tStudy = Study.search(study, dbsession)
            qResult.query(dbsession).filter(Sample.study_id == tStudy).all()
        if spext:
            qResult.query(dbsession).filter(Sample.spext == spext).all()
        if type:
            if type(type) is not int:
                tType = EK.getid(type, dbsession, grp='@SAMTYPE')
            else:
                tType = type
            qResult.query(dbsession).filter(Sample.type_id == tType).all()

        if qResult: return qResult
        return None


def getSpecLabel(dbsession, study, subject, type, aliquot):
    """make label for specimen"""

    tStu = Study.search(study, dbsession)
    cStu = tStu.study_number.upper()

    tSub = Subject.get(subject)
    year = tSub.year
    if checkYear(year) is False:
        RuntimeError('FATAL ERR: year not valid! 1899 < year < 2999, 4 digits format!')

    tYr = year % 100
    cYr = str(tYr)

    num = tSub.subject_number
    cSub = "{0:0=4d}".format(num)

    tType = EK.getid(type, dbsession, grp='@SAMTYPE')
    cType = EK.getkey(tType, dbsession)

    cAl = str(aliquot)

    return cStu + '.' + cYr + '.' + cSub + '.' + cType + '.' + cAl


def getExtLabel(dbsession, spec, type):
    """make label for extraction"""

    tSpec = Specimen.search(dbsession, spec)
    cLabel = tSpec.label

    tType = EK.getid(type, dbsession, grp='@SAMTYPE')
    cType = EK.getkey(tType, dbsession)

    return cLabel + '.' + cType


class Specimen(Sample):
    """
    class for specimen
    the one taken from subjects
    """

    aliquot = Column(types.SmallInteger, nullable=False, server_default=1)
    aliquot_total = Column(types.SmallInteger, nullable=False, server_default=1)

    spec_source_id = Column(types.Integer, ForeignKey('eks.id'), nullable=False)
    spec_source = EK.proxy('spec_source_id', '@SPECSOURCE')

    __mapper_args__ = {
        'polymorphic_identity': 'specimen'
    }


    def add(self, dbsession, study, subject, type, date, storage, creator, ali, cAli,
            source, desc=None, box=None, status='A'):
        """add a specimen, with or without box id"""

        tUuid = UUID.new()
        tLabel = getSpecLabel(dbsession, study, subject, type, ali)
        spec = Specimen(uuid=tUuid, box_id=box, spext="SPECIMEN", study_id=study,
                            subject_id=subject, type_id=type, label=tLabel, date=date,
                            storage_id=storage, creator_id=creator, desc=desc, status=status,
                            aliquot=ali, aliquot_total=cAli, spec_source_id=source)

        dbsession.add(spec)


    def addBatchSubject(self, dbsession, study, subjectDict, creator):
        """
            add batch specimen by subject dictionary
            subjectDict = {
                            "Subject.id" : {
                                                "type" : EK.key
                                                "date" : Date # TODO: stamp date for form
                                                "aliquot" : int
                                                "source" : EK.key
                                                "storage" : EK.key
                                                "desc" : string # optional arg
                                            }
                            }
        """

        for subject, subSpec in subjectDict:
            tStu = Study.search(study, dbsession)
            tSub = Subject.get(subject, dbsession)
            tStor = EK.getid(subSpec["storage"], dbsession, grp='@SAMSTORAGE')
            tCrt = search_user(dbsession, creator)
            tSource = EK.getid(subSpec["source"], dbsession, grp='@SPECSOURCE')

            tType = EK.getid(subSpec["type"], dbsession, grp='@SAMTYPE')
            for n in range(subSpec["aliquot"]):
                tAli = n + 1

                if "desc" in subSpec:
                    self.add(dbsession, tStu, tSub, tType, subSpec["date"], tStor, tCrt,
                             tAli, subSpec["aliquot"], tSource, subSpec["desc"])
                else:
                    self.add(dbsession, tStu, tSub, tType, subSpec["date"], tStor, tCrt,
                             tAli, subSpec["aliquot"], tSource,)


class Extraction(Sample):   # TODO: question: does extraction has aliquot?
    """
    class for specimen's extractions
    extract parts of the specimen
    """

    spec_id = Column(types.Integer, ForeignKey('sample.id'), nullable=False)
    spec = relationship(Specimen, backref=backref('extraction'))

    ext_method_id = Column(types.Integer, ForeignKey('eks.id'), nullable=False)
    ext_method = EK.proxy('ext_method_id', '@EXTMETHOD')

    __mapper_args__ = {
        'polymorphic_identity': 'extraction'
    }


    def add(self, dbsession, study, subject, type, date, storage, creator, spec, method,
            desc=None, box=None, status='A'):
        """add a extraction, with or without box id"""

        tUuid = UUID.new()
        tLabel = getExtLabel(dbsession, spec, type)
        ext = Extraction(uuid=tUuid, box_id=box, spext="EXTRACTION", study_id=study,
                             subject_id=subject, type_id=type, label=tLabel, date=date,
                             storage_id=storage, creator_id=creator, desc=desc, status=status,
                             spec_id=spec, ext_method_id=method)

        dbsession.add(ext)


    def addBatchType(self, dbsession, extDict, creator):
        """
            add batch extraction by extraction list
            extDict = {
                         "Specimen.id" : {
                                            "type" : EK.key
                                            "date" : Date # TODO: stamp date for form
                                            "method" : EK.key
                                            "storage" : EK.key
                                            "desc" : string # optional arg
                                        }
                        }
        """

        for spec, extSpec in extDict:
            tSpec = Specimen.search(dbsession, spec)
            subject = tSpec.subject_id
            tSub = Subject.get(subject, dbsession)
            study = tSpec.study_id
            tStu = Study.search(study, dbsession)
            tType = EK.getid(extSpec["type"], dbsession, grp='@SAMTYPE')
            tStor = EK.getid(extSpec["storage"], dbsession, grp='@SAMSTORAGE')
            tMed = EK.getid(extSpec["method"], dbsession, grp='@EXTMETHOD')
            tCrt = search_user(dbsession, creator)

            if "desc" in extSpec:
                self.add(dbsession, tStu, tSub, tType, extSpec["date"], tStor, tCrt, tSpec, tMed,
                         extSpec["desc"])
            else:
                self.add(dbsession, tStu, tSub, tType, extSpec["date"], tStor, tCrt, tSpec, tMed)
