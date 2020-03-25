from rhombus.models import handler as rhombus_handler
from rhombus.lib.utils import cerr, cout

from .setup import setup

from sampo.models import post, study, sample, fridge, transaction


class DBHandler(rhombus_handler.DBHandler):
    # add additional class references
    Post = post.Post
    Study = study.Study
    Location = study.Location
    Subject = study.Subject
    Sample = sample.Sample
    Specimen = sample.Specimen
    Extraction = sample.Extraction
    Fridge = fridge.Fridge
    Rack = fridge.Rack
    Box = fridge.Box
    BoxCell = fridge.BoxCell
    TakeReturn = transaction.TakeReturn

    def initdb(self, create_table=True, init_data=True, rootpasswd=None):
        """ initialize database """
        super().initdb(create_table, init_data, rootpasswd)
        if init_data:
            from .setup import setup
            setup(self)
            cerr('[sampo-rbmgr] Database has been initialized')

    # add additional methods here

    def get_post(self, q):
        """ get single, specific post """
        if type(q) == int:
            return self.Post.get(q, self.session())

    def get_posts(self, query=None):
        """ get multiple posts by query """
        q = self.Post.query(self.session())

        # do the necessary filtering here

        return q.all()

    def get_study(self, stud=None):
        """get study by name or all"""

        if stud is None:
            return self.Study.query(self.session()).all()
        if isinstance(stud, int):
            return self.Study.get(stud, self.session())
        if isinstance(stud, list):
            return [self.get_study(x) for x in stud]
        if isinstance(stud, str):
            return self.Study.search(stud, self.session())

        raise RuntimeError('ERR: unknown data type for getting Study')

    def get_location(self, loc=None):
        """get location by name or all"""

        if loc is None:
            return self.Location.query(self.session()).all()
        if isinstance(loc, int):
            return self.Location.get(loc, self.session())
        if isinstance(loc, list):
            return [self.get_location(x) for x in loc]
        if isinstance(loc, str):
            return self.Location.search(loc, self.session())

        raise RuntimeError('ERR: unknown data type for getting Location')

    def get_subject(self, sub=None):
        """get subject"""

        if sub is None:
            return self.Subject.query(self.session()).all()
        if isinstance(sub, int):
            return self.Subject.get(sub, self.session())
        if isinstance(sub, list):
            return [self.get_subject(x) for x in sub]

        raise RuntimeError('ERR: unknown data type for getting Subject')

    def get_sample(self, sam=None, box=None):
        """get sample by label or all"""

        if sam is None:
            return self.Sample.query(self.session()).all()
        if isinstance(sam, int):
            return self.Sample.get(sam, self.session())
        if isinstance(sam, list):
            return [self.get_sample(x) for x in sam]
        if isinstance(sam, str):
            return self.Sample.search(sam, self.session())
        if box:
            qResult = self.Sample.query(self.session()).filter(self.Sample.box_id == box).all()
            if qResult: return qResult
            return None

        raise RuntimeError('ERR: unknown data type for getting Sample')

    def get_fridge(self, frid=None):
        """get fridge by name or all"""

        if frid is None:
            return self.Fridge.query(self.session()).all()
        if isinstance(frid, int):
            return self.Fridge.get(frid, self.session())
        if isinstance(frid, list):
            return [self.get_fridge(x) for x in frid]
        if isinstance(frid, str):
            return self.Fridge.search(frid, self.session())

        raise RuntimeError('ERR: unknown data type for getting Fridge')

    def get_rack(self, rck=None, frid=None, shelf=None, rackpos=None):
        """get rack by fridge, shelf, or all"""

        if rck is None:
            return self.Rack.query(self.session()).all()
        if isinstance(rck, int):
            return self.Rack.get(rck, self.session())
        if isinstance(rck, list):
            return [self.get_rack(x) for x in rck]
        if frid:
            tFrd = self.get_fridge(frid=frid)
            if shelf and rackpos:
                qResult = self.Rack.query(self.session()).filter(self.Rack.fridge_id == tFrd)\
                    .filter(self.Rack.shelf_num == shelf, self.Rack.rack_post == rackpos).first()
            else:
                qResult = self.Rack.query(self.session()).filter(self.Rack.fridge_id == tFrd).all()
            if qResult: return qResult
            return None

        raise RuntimeError('ERR: unknown data type for getting Rack')

    def get_box(self, bx=None, rack=None):
        """get box by name, rack, or all"""

        if bx is None:
            return self.Box.query(self.session()).all()
        if isinstance(bx, int):
            return self.Box.get(bx, self.session())
        if isinstance(bx, list):
            return [self.get_box(x) for x in bx]
        if isinstance(bx, str):
            return self.Box.search(bx, self.session())
        if rack:
            qResult = self.Box.query(self.session()).filter(self.Box.rack_id == rack).all()
            if qResult: return qResult
            return None

        raise RuntimeError('ERR: unknown data type for getting Box')

    def get_boxcell(self, cell=None, sample=None, box=None, col=None, row=None):
        """get box cell by sample, box, position, or all"""

        if cell is None:
            return self.BoxCell.query(self.session()).all()
        if isinstance(cell, int):
            return self.BoxCell.get(cell, self.session())
        if isinstance(cell, list):
            return [self.get_boxcell(x) for x in cell]
        if sample:
            return self.BoxCell.search(sample, self.session())
        if box:
            tBox = self.get_box(bx=box)
            if col and row:
                qResult = self.BoxCell.query(self.session()).filter(self.BoxCell.box_id == tBox)\
                    .filter(self.BoxCell.column == col, self.BoxCell.row == row).first()
            else:
                qResult = self.BoxCell.query(self.session()).filter(self.BoxCell.box_id == tBox).all()
            if qResult: return qResult
            return None

        raise RuntimeError('ERR: unknown data type for getting BoxCell')

    def get_takereturn(self, tr=None, take=False):
        """get loc by name, not returned (yet), or all"""

        if tr is None:
            return self.TakeReturn.query(self.session()).all()
        if isinstance(tr, int):
            return self.TakeReturn.get(tr, self.session())
        if isinstance(tr, list):
            return [self.get_takereturn(x) for x in tr]
        if take:
            return self.TakeReturn.query(self.session()).filter(self.TakeReturn.returned == False).all()

        raise RuntimeError('ERR: unknown data type for getting TakeReturn')
