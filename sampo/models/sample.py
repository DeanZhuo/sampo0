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

    # TODO: bulk insert from dict, assign box, check status


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

            return self

        raise NotImplementedError('ERR: updating object uses dictionary object')


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


    @staticmethod
    def checkStatus(dbsession, sampleList, status):
        """check all sample availability from list, return a list"""

        retList = list()
        for sample in sampleList:
            tSam = Sample.search(dbsession, sample)
            if tSam.status is not status:
                retList.append(tSam)

        return retList


    @staticmethod
    def changeStatus(dbsession, sampleList, status):
        """check all sample availability from list, return a list"""

        retList = list()
        for sample in sampleList:
            tSam = Sample.search(dbsession, sample)
            tSam.status = status
            # TODO: update database


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
        tStu = Study.search(study, dbsession)
        tSub = Subject.get(subject, dbsession)
        tStor = EK.getid(storage, dbsession, grp='@SAMSTORAGE')
        tCrt = search_user(dbsession, creator)
        tSource = EK.getid(source, dbsession, grp='@SPECSOURCE')
        tType = EK.getid(type, dbsession, grp='@SAMTYPE')

        spec = Specimen(uuid=tUuid, box_id=box, spext='SPECIMEN', study_id=tStu,
                            subject_id=tSub, type_id=tType, label=tLabel, date=date,
                            storage_id=tStor, creator_id=tCrt, desc=desc, status=status,
                            aliquot=ali, aliquot_total=cAli, spec_source_id=tSource)

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
            for n in range(subSpec["aliquot"]):
                tAli = n + 1

                if "desc" in subSpec:
                    self.add(dbsession, study, subject, subSpec["type"], subSpec["date"],
                             subSpec["storage"], creator, tAli, subSpec["aliquot"], subSpec["source"],
                             subSpec["desc"])
                else:
                    self.add(dbsession, study, subject, subSpec["type"], subSpec["date"],
                             subSpec["storage"], creator, tAli, subSpec["aliquot"], subSpec["source"])


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
        tSpec = Specimen.search(dbsession, spec)
        tSub = Subject.get(subject, dbsession)
        tStu = Study.search(study, dbsession)
        tType = EK.getid(type, dbsession, grp='@SAMTYPE')
        tStor = EK.getid(storage, dbsession, grp='@SAMSTORAGE')
        tMed = EK.getid(method, dbsession, grp='@EXTMETHOD')
        tCrt = search_user(dbsession, creator)
        ext = Extraction(uuid=tUuid, box_id=box, spext='EXTRACTION', study_id=tStu,
                             subject_id=tSub, type_id=tType, label=tLabel, date=date,
                             storage_id=tStor, creator_id=tCrt, desc=desc, status=status,
                             spec_id=tSpec, ext_method_id=tMed)

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
            study = tSpec.study_id

            if "desc" in extSpec:
                self.add(dbsession, study, subject, extSpec["type"], extSpec["date"],
                         extSpec["storage"], creator, tSpec, extSpec["method"],
                         extSpec["desc"])
            else:
                self.add(dbsession, study, subject, extSpec["type"], extSpec["date"],
                         extSpec["storage"], creator, tSpec, extSpec["method"])
