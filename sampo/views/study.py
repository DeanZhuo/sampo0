from sampo.views import *

# TODO add route, revise add and select mock up


class StudyViewer(object):
    """viewer class for study models"""

    def __init__(self, request):
        self.request = request
        self.dbh = get_dbhandler()

    @staticmethod
    def parse_form_study(formd):
        """get data from study form"""

        retd = dict()
        retd['id'] = int(formd['study_id'])
        retd['group_id'] = int(formd['study_group_id'])
        retd['study_name'] = formd['study_name']
        retd['study_number'] = formd['study_number']
        retd['location'] = int(formd['location_id'])
        retd['year'] = int(formd['study_year'])
        retd['new_sub'] = int(formd['new_sub'])
        return retd

    @staticmethod
    def parse_form_subject(formd):   # TODO: Not sure
        """get data from subject form"""

        retlist = list()
        retdict = dict()
        # if formd is a list
        for d in formd:
            if d['amount'] != 0 or d['amount'] != '':
                retdict['subject'] = int(d['subject'])
                retdict['amount'] = int(d['amount'])
                retlist.append(retdict)
        return retlist

    def study_form(self, study, static=False):
        """HTML study input form"""

        dbh = self.dbh

        eform = form(name='study', method=POST)
        eform.add(
            fieldset(
                input_hidden(name='study_id', value=study.id or 0),
                input_select(name='study_group_id', label='Group', value=study.group_id,            # no
                             options=[(g.id, g.name) for g in dbh.get_group()]),
                input_text(name='study_name', label='Study Name', value=study.study_name),          # no
                input_text(name='study_number', label='Study Number', value=study.study_number,     # no(os)
                           static=static),
                input_select(name='location_id', label='Location',                                  # no
                             options=[(l.id, l.name) for l in dbh.get_location()]),
                literal(
                    '<div class ="form-inline row">'
                        '<label class ="align-self-start pt-2" for ="study_year">Year</label>'
                        '<div><input type="number" id="study_number" name="study_number" min="1899" max="2999" style="width:100%"/></div>'                
                    '</div>'
                ),                                                                                  # no
                input_text(name='new_sub', label='Subject (New)', value=0),                         # no
            ),
            fieldset(
                custom_submit_bar(('Subject', 'save')).set_hide(False).set_offset(2)
            ),
        )
        return eform

    @staticmethod
    def subject_form(subjectList):
        """HTML subject selection form"""

        eform = form(name='subject', method=POST)
        eform.add(
            fieldset(
                table()[
                    thead()[
                        th('', style="width: 2em;"), th('Subject'), th('Type(s) Amount')
                    ],
                    tbody()[
                        tuple([
                            tr()[
                                td(input_hidden(name='subject', value=subject.id)),
                                td('%s' % subject.subject_number,),
                                td(
                                   literal(
                                       '<div class ="form-inline row">'
                                       '<div><input type="number" id="amount" name="amount" style="width:100%"/></div>'
                                       '</div>'
                                   ),
                                   )
                            ] for subject in subjectList
                        ])
                    ]
                ]
            ),
            fieldset(
                custom_submit_bar(('Subject', 'save')).set_hide(False).set_offset(2)
            ),
        )
        return eform

    @m_roles(PUBLIC)            # TODO: state role
    def add_study(self):
        """show add study page if GET and process at POST"""
        req = self.request
        dbh = self.dbh
        study = dbh.Study()

        if req.method == 'GET':
            content = div()
            content.add(self.study_form(study))
            return render_to_response("sampo:templates/generics_page.mako",     # TODO: simple template
                                      {'html': content,
                                       }, request=req
                                      )
        elif req.POST:
            study_d = self.parse_form_study(req.POST)

            study = dbh.Study.add(dbsession=dbh.session(), group=study_d['group_id'],
                                name=study_d['study_name'], num=study_d['study_number'])

            dbh.Subject.addBatch(dbsession=dbh.session(), count=study_d['new_sub'], study=study,
                                 loc=study_d['location'], year=study_d['year'])
            dbh.session().flush()
            return HTTPFound(location='/',  # TODO: select subject route
                             study=study, loc=study_d['location'], year=study_d['year'])

    @m_roles(PUBLIC)  # TODO: state role
    def select_study(self):
        """show select study page if GET and process at POST"""
        req = self.request
        dbh = self.dbh
        study = dbh.Study()

        if req.method == 'GET':
            content = div()
            content.add(self.study_form(study))
            return render_to_response("sampo:templates/generics_page.mako",     # TODO: simple template
                                      {'html': content,
                                       }, request=req
                                      )
        elif req.POST:
            study_d = self.parse_form_study(req.POST)
            dbh.Subject.addBatch(dbsession=dbh.session(), count=study_d['new_sub'], study=study_d['id'],
                                 loc=study_d['location'], year=study_d['year'])
            dbh.session().flush()
            return HTTPFound(location='/',  # TODO: select subject page
                             study=study_d['id'], loc=study_d['location'], year=study_d['year'])

    @m_roles(PUBLIC)    # TODO: state role
    def select_subject(self):
        """show select subject page if GET and process at POST"""
        req = self.request
        dbh = self.dbh

        if req.method == 'GET':
            subjectList = dbh.Subject.getSub(dbh.session(), req.study, req.loc, req.year, last=True)
            content = div()
            content.add(self.subject_form(subjectList))
            return render_to_response("sampo:templates/generics_page.mako",     # TODO: simple template
                                      {'html': content,
                                       }, request=req
                                      )
        elif req.POST:
            subject_l = self.parse_form_subject(req.POST)
            return HTTPFound(location='/', subjects=subject_l, study=req.study, year=req.year)
            # TODO: select sample page
