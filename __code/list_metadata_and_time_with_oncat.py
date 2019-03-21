from __code import oncat


class ListMetadata:

    def __init__(self, system=None, file=''):

        self.instrument = system.System.get_instrument_selected()
        self.facility = system.System.get_facility_selected()
        self.file = file

        self.session = oncat.Oncat()
        self.session.authentication()

    def retrieve_list_metadata(self):

        o_data = oncat.GetEverything(instrument=self.instrument,
                                     facility=self.facility,
                                     runs=self.file,
                                     oncat=self.session)

        print(o_data.datafiles)

