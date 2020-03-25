from rhombus.models.core import get_userid
from sampo.views import *

# TODO add route, revise take/return mock up


class SampleViewer(object):
    """viewer class for sample"""

    def __init__(self, request):
        self.request = request
        self.dbh = get_dbhandler()

    @staticmethod
    def parse_new_sample(forml):
        """get data from new sample"""

        # if return as list
        retlist = list()
        retdict = dict()
        for formd in forml:
            retdict['subject'] = int(formd['subject'])
            retdict['type'] = int(formd['type'])
            retdict['date'] = formd['date']
            retdict['aliquot'] = int(formd['aliquot'])
            retdict['source'] = int(formd['source'])
            retdict['storage'] = int(formd['storage'])
            retdict['desc'] = formd['desc']
            retlist.append(retdict)
        return retlist

    @staticmethod
    def parse_search(formd):
        """get data from search"""

        retdict = dict()
        retdict['code'] = formd['code_number']
        retdict['spext'] = formd['spext']
        retdict['study'] = int(formd['study'])
        retdict['type'] = int(formd['type'])
        retdict['startD'] = formd['startD']
        retdict['endD'] = formd['endD']
        return retdict

    @staticmethod
    def parse_extract(forml):       # TODO: not sure
        """get list of extraction from new extraction page"""

        retlist = list()
        retdict = dict()
        for formd in forml:
            retdict['id'] = int(formd['id'])
            retdict['type'] = formd['type']
            retdict['date'] = formd['date']
            retdict['method'] = formd['method']
            retdict['storage'] = formd['storage']
            retdict['desc'] = formd['desc']
            retlist.append(retdict)
        return retlist

    @staticmethod
    def parse_move(forml):  # TODO: not sure
        """get list of sample from move sample page"""

        retlist = list()
        retdict = dict()
        for formd in forml:
            retdict['id'] = int(formd['id'])
            retdict['fridge'] = formd['fridge']
            retdict['shelf'] = formd['shelf']
            retdict['rack'] = formd['rack']
            retdict['box'] = formd['box']
            retdict['col'] = formd['col']
            retdict['row'] = formd['row']
            retlist.append(retdict)
        return retlist

    def new_sample_form(self, sublist):
        """HTML add sample form for one type of a subject"""

        dbh = self.dbh
        req = self.request

        eform = form(name='new_study', method=POST)
        for subd in sublist:
            sub = dbh.get_subject(sub=subd['subject'])
            for i in range(subd['amount']):
                eform.add(
                    fieldset(
                        p()['Subject ' + "{0:0=4d}".format(sub.subject_number)],
                        p()['Study ' + dbh.get_study(stud=req.study).study_name + req.year],
                        input_hidden(name='subject', value=sub.id),
                        input_select_ek(name='type', label='Sample Type', value='',
                                        parent_ek=dbh.list_ekeys(group='@SAMTYPE')),
                        literal(
                            '<div class ="form-inline row">'
                                '<label class ="align-self-start pt-2" for ="date">Date Created</label>'
                                '<div><input type="date" id="date" name="date" style="width:100%"/></div>'                
                            '</div>'
                            '<div class ="form-inline row">'
                                '<label class ="align-self-start pt-2" for ="aliquot">Number of Aliquot</label>'
                                '<div><input type="number" id="aliquot" name="aliquot" style="width:100%"/></div>'
                            '</div>'
                        ),
                        input_select_ek(name='source', label='Sample Source', value='',
                                        parent_ek=dbh.list_ekeys(group='@SPECSOURCE')),
                        input_select_ek(name='storage', label='Storage', value='',
                                        parent_ek=dbh.list_ekeys(group='@SAMSTORAGE')),
                        input_textarea(name='desc', label='Desc (op)')
                    )
                )
        eform.add(custom_submit_bar(('Add Samples', 'save')).set_hide(False).set_offset(2))
        return eform

    def search_form(self):
        """HTML search form"""

        dbh = self.dbh

        eform = form(name='search', method=POST)
        eform.add(
            fieldset(
                input_text(name='code_number', label='', placeholder='Code Number'),
                input_select(name='spext', label='', placeholder='Spec or Ext',
                             options=[('both', 'Both'), ('specimen', 'Specimen'), ('extraction', 'Extraction')]),
                input_select(name='study', label='', placeholder='Study',
                             options=[(s.id, s.study_name) for s in dbh.get_study()]),
                input_select_ek(name='type', label='', value='',
                                parent_ek=dbh.list_ekeys(group='@SAMTYPE')),
                literal(
                    '<div class ="form-inline row">'
                        '<label class ="align-self-start pt-2" for ="startD">From:</label>'
                        '<div><input type="date" id="startD" name="startD"/></div>'
                    '</div>'
                    '<div class ="form-inline row">'
                        '<label class ="align-self-start pt-2" for ="endD">Until:</label>'
                        '<div><input type="date" id="endD" name="endD"/></div>'
                    '</div>'
                ),
            ),
            fieldset(custom_submit_bar(('Search', 'search')).set_hide(False).set_offset(2))
        )
        return eform

    @staticmethod
    def take_return_table(showList, name):
        """HTML table (only) for taken or returned samples, including failed transaction"""

        samp_table = div()
        samp_table.add(
            fieldset(
                h2()[name],
                table()[
                    thead()[
                        th('Code Number'), th('Study'), th('Type'), th('Date Created'), th('Position')
                    ],
                    tbody()[
                        tuple([
                            tr()[
                                td('%s' % samp['label']),
                                td('%s' % samp['study']),
                                td('%s' % samp['type']),
                                td('%s' % samp['date']),
                                td('%s' % samp['position']),
                            ] for samp in showList
                        ])
                    ]
                ]
            )
        )
        return samp_table

    def extract_table(self, extracList):
        """HTML table form to input extraction data"""

        dbh = self.dbh
        samp_table = div()
        samp_table.add(
            fieldset(
                table()[
                    thead()[
                        th('', style="width: 2em;"),
                        th('Code Number'), th('Extraction'), th('Date'), th('Method'), th('Storage'),
                        th('Desc')
                    ],
                    tbody()[
                        tuple([
                            tr()[
                                td(input_hidden(name='id', value=samp.id)),
                                td('%s' % samp.label),
                                td(input_select_ek(name='type', label='', value='',
                                                   parent_ek=dbh.list_ekeys(group='@SAMTYPE'))),
                                td(literal(
                                           '<div class ="form-inline row">'
                                               '<div><input type="date" id="date" name="date"/></div>'
                                           '</div>'
                                           )),
                                td(input_select_ek(name='method', label='', value='',
                                                   parent_ek=dbh.list_ekeys(group='@EXTMETHOD'))),
                                td(input_select_ek(name='storage', label='', value='',
                                                   parent_ek=dbh.list_ekeys(group='@SAMSTORAGE'))),
                                td(input_text(name='desc', label='')),
                            ] for samp in extracList
                        ])
                    ]
                ],
                custom_submit_bar(('Add Extraction', 'save')).set_hide(False).set_offset(2),
            )
        )
        return samp_table

    def move_table(self, moveList):
        """HTML table form to input extraction data"""

        dbh = self.dbh
        samp_table = div()
        samp_table.add(
            fieldset(
                a(href='/')[button(label='Cancel')],     # TODO: go bach to search page (with var)
                custom_submit_bar('Move', 'save').set_hide(False).set_offset(2)
            ),
            fieldset(
                table()[
                    thead()[
                        th('', style="width: 2em;"),
                        th('Code Number'), th('Type'), th('Position'),
                        th('Fridge'), th('Shelf'),th('Rack'),th('Box'),
                        th('Column'),th('Row')
                    ],
                    tbody()[
                        tuple([
                            tr()[
                                td(input_hidden(name='id', value=samp.id)),
                                td('%s' % samp.label),
                                td(dbh.EK.getkey(samp.type_id, dbh.session())),
                                td(samp.getPosition()),
                                td(input_select(name='fridge', label='', options=[(f.id, f.fridge_name)
                                                         for f in dbh.get_fridge()])),
                                td(input_text(name='shelf', label='')),
                                td(input_text(name='rack', label='')),
                                td(input_text(name='box', label='')),
                                td(input_text(name='col', label='')),
                                td(input_text(name='row', label='')),
                            ] for samp in moveList
                        ])
                    ]
                ],
            )
        )
        return samp_table

    @m_roles(PUBLIC)  # TODO: state role
    def new_sample(self):
        """show new sample page if GET and process at POST"""

        req = self.request
        dbh = self.dbh
        content = div()
        subject_list = req.subjects

        if req.method == 'GET':
            content.add(h2()['New Sample'])
            content.add(self.new_sample_form(subject_list))

            return render_to_response("sampo:templates/generics_page.mako",  # TODO: simple template
                                      {'html': content,
                                       }, request=req
                                      )

        elif req.POST:
            # if return as list
            subjectDict = dict()
            sampleDict = dict()
            sam_list = self.parse_new_sample(req.POST)
            for sam_dict in sam_list:
                sampleDict['type'] = sam_dict['type']
                sampleDict['date'] = sam_dict['date']
                sampleDict['aliquot'] = sam_dict['aliquot']
                sampleDict['source'] = sam_dict['source']
                sampleDict['storage'] = sam_dict['storage']
                sampleDict['desc'] = sam_dict['desc']
                subjectDict[sam_dict['subject']] = sampleDict

            dbh.Specimen.addBatchSubject(dbsession=dbh.session(), study=req.study,
                                         subjectDict=subjectDict, creator=get_userid())
            dbh.session().flush()
            return HTTPFound(location='/')  # TODO: select box page

    @m_roles(PUBLIC)  # TODO: state role
    def search(self):
        """show search add page if GET and process at POST"""

        req = self.request
        dbh = self.dbh
        content = div()
        content.add(self.search_form())

        if req.POST:
            search_d = self.parse_search(req.POST)
            search_l = dbh.Sample.searchPage(dbsession=dbh.session(), label=search_d['code'],
                                             study=search_d['study'], spext=search_d['spext'],
                                             type=search_d['type'],
                                             dStart=search_d['startD'], dEnd=search_d['endD'])
            req.search_list = search_l

        return render_to_response("sampo:templates/generics_page.mako",  # TODO: search template
                                  {'html': content,
                                   }, request=req
                                  )

    @staticmethod
    def make_show_list(dbh, sampleList):
        """make a new list to show on the take return table"""

        show_list = list()
        show_dict = dict()
        for samp in sampleList:
            show_dict['label'] = samp.label
            show_dict['study'] = dbh.get_study(stud=dbh.get_subject(sub=samp.subject_id).
                                               study_id).study_name
            show_dict['type'] = dbh.EK.getkey(samp.type_id, dbh.session())
            show_dict['date'] = samp.date
            tBox = dbh.get_box(bx=samp.box_id)
            tRack = dbh.get_rack(rck=tBox.rack_id)
            tFrd = dbh.get_fridge(frid=tRack.fridge_id)
            show_dict['position'] = tFrd.fridge_name + ' Shelf ' + tRack.shelf_num + \
                                    ' Rack ' + tRack.rack_post + ', ' + tBox.box_name
            show_list.append(show_dict)
        return show_list

    @m_roles(PUBLIC)  # TODO: state role
    def take_or_ret(self):
        """process TAKE or RETURN transaction"""

        req = self.request
        dbh = self.dbh
        op = req.op  # should be 'take' or 'return'
        content = div()
        sampleList = list()
        # TODO: get sample to list from search page selection

        if not sampleList:
            content.add(
                h2(['Nothing to' + op + ', Please select Specimen or Extraction']),
                a(href='/')[button(label='Back')]  # TODO: go bach to search page (with var)
            )

        status = 'A' if op == 'take' else 'N'
        message = 'Taken Samples' if op == 'take' else 'Returned Samples'
        headers = 'Not Available' if op == 'take' else 'Not Returned'
        checklist = dbh.Sample.checkStatus(sampleList, status)
        show_check = list()
        if checklist:
            sampleList = [samp for samp in sampleList if samp not in checklist]
            show_check = self.make_show_list(dbh, checklist)

        dbh.TakeReturn.transaction(dbh.session(), sampleList, get_userid(), date.today())
        show_sample = self.make_show_list(dbh, sampleList)

        content.add(
            self.take_return_table(show_sample, message),
            self.take_return_table(show_check, headers) if show_check else '',
            a(href='/')[button(label='Done')]  # TODO: go to search page (without var)
        )

        return render_to_response("sampo:templates/generics_page.mako",  # TODO: search template
                                  {'html': content,
                                   }, request=req
                                  )

    @m_roles(PUBLIC)    # TODO: state role
    def extract(self):
        """show extraction table form if GET and process add extraction if POST"""

        req = self.request
        dbh = self.dbh
        content = div()
        content.add(self.extract_table(req.extractList))

        if req.POST:
            extract_list = self.parse_extract(req.POST)
            extDict = dict()
            extSpec = dict()

            for spec in extract_list:
                extSpec['type'] = spec['type']
                extSpec['date'] = spec['date']
                extSpec['method'] = spec['method']
                extSpec['storage'] = spec['storage']
                extSpec['desc'] = spec['desc']
                extDict[spec['id']] = extSpec

            dbh.Extraction.addBatchType(dbh.session(), extDict)
            dbh.session().flush()
            return HTTPFound(location='/')  # TODO: select box page

        return render_to_response("sampo:templates/generics_page.mako",  # TODO: simple template
                                  {'html': content,
                                   }, request=req
                                  )

    @m_roles(PUBLIC)        # TODO: state role
    def move_sample(self):
        """show move sample table form if GET and process if POST"""

        req = self.request
        dbh = self.dbh
        content = div()
        content.add(self.move_table(req.moveList))

        if req.POST:
            move_list = self.parse_move(req.POST)
            moveDict = dict()
            destDict = dict()

            for dest in move_list:
                destDict['fridge'] = dest['fridge']
                destDict['shelf'] = dest['shelf']
                destDict['rackpost'] = dest['rack']
                destDict['box'] = dest['box']
                destDict['column'] = dest['col']
                destDict['row'] = dest['row']
                moveDict[dest['id']] = destDict

            dbh.Sample.assignBox(moveDict)
            dbh.session().flush()
            return HTTPFound(location='/')  # TODO: search page (without var)

        return render_to_response("sampo:templates/generics_page.mako",  # TODO: simple template
                                  {'html': content,
                                   }, request=req
                                  )(req.POST)
