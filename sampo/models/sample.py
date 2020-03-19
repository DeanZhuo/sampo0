from sampo.models.fridge import Box
from sqlalchemy import and_

from .study import *


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

    @staticmethod
    def bulk_insert(itemlist, dbsession):
        """
        bulk insert study
        itemlist = [ (box, spext, study, subject, type, label, date, storage, creator, desc, status,
                        aliquot, aliquot_total, spec_source, spec_id, ext_method) ]
        """

        for item in itemlist:
            box, spext, study, subject, type, label, date, storage, creator, \
                desc, status, aliquot, aliquot_total, spec_source, spec_id, ext_method \
                = item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], \
                  item[9], item[10], item[11], item[12], item[13], item[14], item[15]
            if spext.upper() == 'SPECIMEN':
                Specimen.add(dbsession, study, subject, type, date, storage,
                             aliquot, aliquot_total, spec_source, creator, desc, box, status)
            else:
                Extraction.add(dbsession, study, subject, type, date, storage, spec_source,
                               ext_method, creator, desc, box, status)

    def as_dict(self):
        """return as python dictionary"""

        return dict(box=self.box_id, spext=self.spext, study=self.study_id, subject=self.study_id,
                    type=self.type_id, label=self.label, date=self.date, storage=self.storage_id,
                    creator=self.creattBoxor_id, desc=self.desc, status=self.status,
                    aliquot=self.aliquot, aliquot_total=self.aliquot_total, spec_source=self.spec_source_id,
                    spec_id=self.spec_id, ext_method=self.ext_method_id)

    @staticmethod
    def dump(out, query=None):
        """dump to yaml"""

        if query is None:
            query = Study.query()
        yaml.safe_dump((x.as_dict() for x in query), out, default_flow_style=False)

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
    def search(samp, dbsession):
        """search by label"""

        q = Sample.query(dbsession).filter(Sample.label == samp).first()
        if q: return q
        return q

    @staticmethod
    def searchPage(dbsession, label, study, spext, type, dStart, dEnd):
        """function for search page"""

        qResult = Sample.query(dbsession).filter(and_(Sample.date >= dStart, Sample.date <= dEnd)).all()

        if label:
            qResult.query(dbsession).filter(Sample.label == label).all()
        if study:
            tStudy = Study.search(study, dbsession)
            qResult.query(dbsession).filter(Sample.study_id == tStudy).all()
        if spext:
            qResult.query(dbsession).filter(Sample.spext == spext).all()
        if type:
            if not isinstance(type, int):
                tType = EK.getid(type, dbsession, grp='@SAMTYPE')
            else:
                tType = type
            qResult.query(dbsession).filter(Sample.type_id == tType).all()

        if qResult: return qResult
        return None

    @staticmethod
    def checkStatus(sampleList, status):
        """check all sample availability from list, return a list with different status"""

        dbh = get_dbhandler()
        retList = list()
        for sample in sampleList:
            tSam = dbh.get_sample(sam=sample)
            if tSam.status is not status:
                retList.append(tSam)

        return retList

    @staticmethod
    def changeStatus(sampleList, status):
        """change all sample availability from list"""

        dbh = get_dbhandler()
        for sample in sampleList:
            tSam = dbh.get_sample(sam=sample)
            tSam.status = status

    def getPostition(self):
        """get position (complete address) of a sample"""

        dbh = get_dbhandler()
        tBox = dbh.get_box(bx=self.box_id)
        tRck = dbh.get_rack(rck=tBox.rack_id)
        tFrd = dbh.get_fridge(frid=tRck.fridge_id)

        position = tFrd.fridge_name + ' Shelf ' + str(tRck.shelf_num) + ' Rack ' + str(tRck.rack_post) + ', ' \
                   + tBox.box_name

        if tBox.box_type == 1:
            tCel = dbh.get_boxcell(sample=self.id)
            position += '\n Column ' + tCel.column + ' Row ' + str(tCel.row)

        return position

    @staticmethod
    def assignBox(moveDict):
        """
            move specimen and extraction according to dictionary.
            can only be moved to similar box type.
            moveDict = {
                            "Sample.id" : {
                                            "fridge" : string
                                            "shelf" : int
                                            "rackpost" : int
                                            "box" : string
                                            "type" : 0 or 1
                                            "nRow" : int
                                            "nCol : int
                                            "column" : string
                                            "row" : int
                                            }
                        }
        """

        retList = list()
        dbh = get_dbhandler()

        for sample, dest in moveDict:
            tSam = dbh.get_sample(sam=sample)
            nBox = dbh.get_box(bx=dest['box'])

            if nBox is None:
                nFrd = dbh.get_fridge(frid=dest['fridge'])
                nRack = dbh.get_rack(frid=nFrd, shelf=dest['shelf'], rackpos=dest['rackpost'])
                Box.add(dbh.session(), dest['box'], dest['type'], nRack, dest['nRow'], dest['nCol'], False)
                nBox = dbh.get_box(bx=dest['box'])

            if tSam.box_id is not 0:
                oBox = dbh.get_box(bx=tSam.box_id)
                if oBox.box_type != nBox.box_type or oBox.box_isFull is True:
                    retList.append(tSam)
                    continue
                if oBox.box_type == 1:
                    oCell = dbh.get_boxcell(sample=tSam)
                    oCell.sample_id = None
                    oCell.status = 'E'

            if nBox.box_type == 1:
                nCell = dbh.get_boxcell(box=nBox, col=dest['column'], row=dest['row'])
                if nCell.status != 'E' or tSam.storage_id != 1:     # 1 is for cups which fit in the grid
                    retList.append(tSam)
                    continue
                nCell.sample_id = tSam
                nCell.status = tSam.status

            tSam.box_id = nBox

        return retList


def getSpecLabel(dbsession, study, subject, type, aliquot):
    """make label for specimen"""

    dbh = get_dbhandler()
    tStu = dbh.get_study(stud=study)
    cStu = tStu.study_number.upper()

    tSub = dbh.get_subject(sub=subject)
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

    dbh = get_dbhandler()
    tSpec = dbh.get_sample(sam=spec)
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

    @staticmethod
    def add(dbsession, study, subject, type, date, storage, ali, cAli, source,
            creator=None, desc=None, box=None, status='A'):
        """add a specimen, with or without box id"""

        dbh = get_dbhandler()

        if creator is None:
            tCrt = get_userid()
        else:
            tCrt = dbh.get_user(user=creator)

        tUuid = UUID.new()
        tLabel = getSpecLabel(dbsession, study, subject, type, ali)
        tStu = dbh.get_study(stud=study)
        tSub = dbh.get_subject(sub=subject)
        tStor = EK.getid(storage, dbsession, grp='@SAMSTORAGE')
        tSource = EK.getid(source, dbsession, grp='@SPECSOURCE')
        tType = EK.getid(type, dbsession, grp='@SAMTYPE')

        spec = Specimen(uuid=tUuid, box_id=box, spext='SPECIMEN', study_id=tStu,
                        subject_id=tSub, type_id=tType, label=tLabel, date=date,
                        storage_id=tStor, creator_id=tCrt, desc=desc, status=status,
                        aliquot=ali, aliquot_total=cAli, spec_source_id=tSource)

        dbsession.add(spec)

    @staticmethod
    def addBatchSubject(dbsession, study, subjectDict, creator):
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

                if 'desc' in subSpec:
                    Specimen.add(dbsession, study, subject, subSpec["type"], subSpec["date"],
                                 subSpec["storage"], tAli, subSpec["aliquot"], subSpec["source"], creator,
                                 subSpec["desc"])
                else:
                    Specimen.add(dbsession, study, subject, subSpec["type"], subSpec["date"],
                                 subSpec["storage"], tAli, subSpec["aliquot"], subSpec["source"], creator)


class Extraction(Sample):  # TODO: question: does extraction has aliquot?
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

    @staticmethod
    def add(dbsession, study, subject, type, date, storage, spec, method,
            creator=None, desc=None, box=None, status='A'):
        """add a extraction, with or without box id"""

        dbh = get_dbhandler()

        if creator is None:
            tCrt = get_userid()
        else:
            tCrt = dbh.get_user(user=creator)

        tUuid = UUID.new()
        tLabel = getExtLabel(dbsession, spec, type)
        tSpec = dbh.get_sample(sam=spec)
        tSub = dbh.get_subject(sub=subject)
        tStu = dbh.get_study(stud=study)
        tType = EK.getid(type, dbsession, grp='@SAMTYPE')
        tStor = EK.getid(storage, dbsession, grp='@SAMSTORAGE')
        tMed = EK.getid(method, dbsession, grp='@EXTMETHOD')
        ext = Extraction(uuid=tUuid, box_id=box, spext='EXTRACTION', study_id=tStu,
                         subject_id=tSub, type_id=tType, label=tLabel, date=date,
                         storage_id=tStor, creator_id=tCrt, desc=desc, status=status,
                         spec_id=tSpec, ext_method_id=tMed)

        dbsession.add(ext)

    @staticmethod
    def addBatchType(dbsession, extDict):
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

        dbh = get_dbhandler()

        for spec, extSpec in extDict:
            tSpec = dbh.get_sample(sam=spec)
            subject = tSpec.subject_id
            study = tSpec.study_id

            if 'desc' in extSpec:
                Extraction.add(dbsession, study, subject, extSpec["type"], extSpec["date"],
                               extSpec["storage"], tSpec, extSpec["method"],
                               extSpec["desc"])
            else:
                Extraction.add(dbsession, study, subject, extSpec["type"], extSpec["date"],
                               extSpec["storage"], tSpec, extSpec["method"])
