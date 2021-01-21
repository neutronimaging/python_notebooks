class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def marker_location(self, image_resolution='high_res', target_index='1'):

        roi_id = self.parent.markers[image_resolution][target_index]['ui']
        live_image = self.parent.current_live_image[image_resolution]
        image_view_item = self.parent.image_view[image_resolution].imageItem

        region = roi_id.getArraySlice(live_image,
                                      image_view_item)

        x0 = region[0][0].start
        y0 = region[0][1].start

        return {'x': x0, 'y': y0}
