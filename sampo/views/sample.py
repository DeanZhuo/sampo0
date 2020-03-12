from rhombus.models.core import get_userid
from sampo.views import *
from rhombus.lib.utils import get_dbhandler

# TODO add route, revise take/return mock up


class SampleViewer(object):
    """viewer class for sample"""

    def __init__(self, request):
        self.request = request
        self.dbh = get_dbhandler()


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

    def search_form(self):
        """HTML search form"""

        dbh = self.dbh

        eform = form(name='search', method=POST)
        eform.add(
            fieldset(
                input_text(name='code_number', label='', placeholder='Code Number'),
                literal(
                    '<select name=spext>'
                    '   <option value="both">Both'
                    '   <option value="specimen">Specimen'
                    '   <option value="extraction">Extraction'
                ),
                input_select(name='study', label='', placeholder='Study',
                             options=[(s.id, s.study_name) for s in dbh.get_study()]),
                input_select_ek(name='type', label='', value='',
                                parent_ek=dbh.list_ekeys(group='@SAMTYPE')),
                literal(
                    '<label for="startD">From:</label> <input type="date" name="startD">'
                    '<label for="endD">Until:</label> <input type="date" name="endD">'
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

    @m_roles(PUBLIC)            # TODO: state role
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

        return render_to_response("sampo:templates/generics_page.mako",     # TODO: search template
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


    @m_roles(PUBLIC)    # TODO: state role
    def take_or_ret(self):     # TODO: not yet
        """process TAKE or RETURN transaction"""

        req = self.request
        dbh = self.dbh
        op = req.op     # should be 'take' or 'return'
        content = div()
        sampleList = list()
        # TODO: get sample to list from search page

        if not sampleList:
            content.add(
                h2(['Nothing to' + op + ', Please select Specimen or Extraction']),
                a(href='/')[button(label='Back')]   # TODO: go bach to search page (with var)
            )

        status = 'A' if op == 'take' else 'N'
        message = 'Taken Samples' if op == 'take' else 'Returned Samples'
        headers = 'Not Available' if op == 'take' else 'Not Returned'
        checklist = dbh.Sample.checkStatus(sampleList, status)
        show_check = list()
        if checklist:
            sampleList = [samp for samp in sampleList if samp not in checklist]
            show_check = self.make_show_list(dbh, checklist)

        dbh.TakeReturn.transaction(dbh.session(), sampleList, get_userid(), time.now())     # TODO: date format
        show_sample = self.make_show_list(dbh, sampleList)

        content.add(
            self.take_return_table(show_sample, message),
            self.take_return_table(show_check, headers) if show_check else '',
            a(href='/')[button(label='Done')]   # TODO: go to search page (without var)
        )

        return render_to_response("sampo:templates/generics_page.mako",  # TODO: search template
                                  {'html': content,
                                   }, request=req
                                  )

# TODO: extract, move, clear for search menu
# TODO: continuation from study

