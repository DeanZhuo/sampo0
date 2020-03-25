from sampo.views import *

# TODO: add route, add template


class FridgeViewer(object):
    """viewer class for fridge"""

    def __init__(self, request):
        self.request = request
        self.dbh = get_dbhandler()

    @staticmethod
    def parse_new_fridge(formd):
        """get new fridge data from new fridge form"""

        retdict = dict()
        retdict['group'] = int(formd['group'])
        retdict['name'] = formd['name']
        retdict['type'] = int(formd['type'])
        retdict['model'] = formd['model']
        retdict['temp'] = formd['temp']
        retdict['loc'] = int(formd['loc'])
        retdict['desc'] = formd['desc']
        retdict['shelf'] = int(formd['shelf'])
        return retdict

    @staticmethod
    def parse_racks(forml):
        """get new racks data from new fridge racks form"""

        retlist = list()
        retdict = dict()
        for formd in forml:
            retdict['shelf'] = formd['shelf']
            retdict['rack'] = formd['rack']
            retdict['row'] = formd['row']
            retdict['col'] = formd['col']
            retlist.append(retdict)
        return retlist

    def normal_view(self, samples):
        """HTML table for normal box view"""

        dbh = self.dbh

        content = div()
        content.add(
            fieldset(
                table()[
                    thead()[
                        th('Code Number'), th('Study'), th('Subject'), th('Type'), th('Date Created'),
                        th('Aliquot'), th('Status')
                    ],
                    tbody()[
                        tuple([
                            tr()[
                                td('%s' % sample.label),
                                td('%s' % dbh.get_study(stud=sample.study_id).study_name),
                                td('%0.4d' % dbh.get_subject(sub=sample.subject_id).subject_number),
                                td('%s' % dbh.EK.getkey(sample.type_id)),
                                td('%s' % sample.date),
                                td('%d of %d' % sample.aliquot, sample.aliquot_total),
                                td('%s' % 'Available' if sample.status == 'A' else 'Not available'),
                            ] for sample in samples
                        ])
                    ]
                ]
            )
        )
        return content

    def new_fridge_form(self):
        """HTML form for new fridge"""

        dbh = self.dbh
        content = div()
        content.add(
            fieldset(
                h2()['New Fridge']
            ),
            fieldset(
                input_select(name='group', label='Group',
                             options=[(g.id, g.name) for g in dbh.get_group()]),
                input_text(name='name', label='Name'),
                input_select_ek(name='type', label='Type', value='',
                           parent_ek=dbh.list_ekeys(group='@FRIDGETYPE')),
                input_text(name='model', label='Model (op)'),
                input_text(name='name', label='Name'),
                literal(
                    '<label for="temp">Temperature (C)</label>'
                    '<input type="number" name="temp">'
                ),
                input_select_ek(name='loc', label='Location', value='',
                            parent_ek=dbh.list_ekeys(group='@FRIDGELOC')),
                input_text(name='desc', label='Desc (op)'),
                literal(
                    '<label for="shelf">Number of Shelf</label>'
                    '<input type="number" name="shelf">'
                ),
            ),
            fieldset(
                custom_submit_bar(('Add Fridge', 'save'))
            )
        )
        return content

    def new_fridge_racks_form(self):
        """HTML form for new racks"""

        req = self.request
        content = div()
        content.add(
            fieldset(
                h2()['New Fridge Racks'],
            ),
            fieldset(
                tuple([
                    div()[
                        p()['%s' % shelf],
                        input_hidden(name='fridge', value=req.fridge),
                        literal(
                            '<label for="number">Number of Rack</label> '
                            '<input type="number" name="number"><br>'
                        ),
                    ]for shelf in req.shelf
                ])
            )
        )

    @m_roles(PUBLIC)
    def all_fridge(self):
        """show Fridge menu page"""

        req = self.request
        dbh = self.dbh

        loc_list = dbh.list_ekey(group='@FRIDGELOC')
        req.locations = loc_list

        fridge_list = dbh.get_fridge()
        fridges = list()
        tFrd = dict()
        for fridge in fridge_list:
            tFrd['id'] = fridge.id
            tFrd['name'] = fridge.group_name + ' ' + fridge.fridge_name
            tFrd['type'] = dbh.EK.getkey(fridge.fridge_type_id, dbh.session())
            tFrd['model'] = fridge.fridge_model
            tFrd['temp'] = fridge.temperature
            tFrd['location'] = dbh.EK.getkey(fridge.fridge_location_id, dbh.session())
            tFrd['desc'] = fridge.fridge_desc
            fridges.append(tFrd)
        req.fridges = fridges

        return render_to_response("sampo:templates/generics_page.mako",     # TODO: fridge menu template
                                  {}, request=req
                                  )

    @m_roles(PUBLIC)            # TODO: not yet, stuck at the structure
    def show_fridge(self):
        """show fridge view page"""

        req = self.request
        dbh = self.dbh

        tFrd = dbh.get_fridge(frid=req.fridge)
        tShf = list()
        racks = dbh.get_rack(frid=tFrd)


    @m_roles(PUBLIC)        # TODO: not yet, stuck at the view detail
    def grid_box(self):
        """show view box page, with grid box type"""

        req = self.request
        dbh = self.dbh

        tBox = dbh.get_box(bx=req.box)
        cells = dbh.get_boxcell(box=tBox)

    @m_roles(PUBLIC)
    def normal_box(self):
        """show view box page, with normal box type"""

        req = self.request
        dbh = self.dbh

        tBox = dbh.get_box(bx=req.box)
        samples = dbh.get_sample(box=tBox.id)
        content = self.normal_view(samples)

        return render_to_response("sampo:templates/generics_page.mako",  # TODO: box view template
                                  {
                                      'html': content,
                                  }, request=req
                                  )

    @m_roles(PUBLIC)    # TODO: state role
    def new_fridge(self):
        """show new fridge form if GET and process if POST"""

        dbh = self.dbh
        req = self.request
        content = self.new_fridge_form()

        if req.POST:
            fridge = self.parse_new_fridge(req.POST)
            tFrd = dbh.Fridge.add(dbsession=dbh.session(), group=fridge['group'], name=fridge['name'],
                           type=fridge['type'], model=fridge['model'], temp=fridge['temp'],
                           loc=fridge['loc'], desc=fridge['desc'], shelf=fridge['shelf'])
            dbh.session().flush()
            return HTTPFound(location='/',      # TODO: new fridge rack page
                             shelf=fridge['shelf'], fridge=tFrd.id)

        return render_to_response("sampo:templates/generics_page.mako",  # TODO: simple template
                                  {
                                      'html': content,
                                  }, request=req
                                  )
