from __code import oncat


class ListMetadata:

    def __init__(self, system=None, file=''):
        self.instrument = system.System.get_instrument_selected()
        self.facility = system.System.get_facility_selected()
        self.file = file

        _oncat = oncat.Oncat()
        self.oncat_session = _oncat.authentication()

    def retrieve_list_metadata(self):
        o_data = oncat.GetEverything(instrument=self.instrument,
                                     facility=self.facility,
                                     run=self.file,
                                     oncat=self.oncat_session)

        print(o_data.datafiles)

