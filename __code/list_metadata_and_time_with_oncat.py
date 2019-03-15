from __code import oncat


class ListMetadata:

    def __init__(self, system=None):

        self.instrument = system.System.get_instrument_selected()
        self.facility = system.System.get_facility_selected()

        # self.session = oncat.Oncat()
        #self.session.authentication()

