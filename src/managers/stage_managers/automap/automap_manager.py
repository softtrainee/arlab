#=============enthought library imports=======================
from traits.api import  Instance, Range
from traitsui.api import View, Item
from src.managers.manager import Manager
#from src.managers.laser_managers.laser_manager import LaserManager
#from src.image.image_helper import crop, load_image, get_polygons, contour, \
#    grayspace, centroid
import os
import time
from src.image.image import Image
from src.image.image_editor import ImageEditor

#============= standard library imports ========================
#============= local library imports  ==========================


class AutomapManager(Manager):
    pxpermm = 64
    cropwidth = 2
    cropheight = 2
        
#    laser_manager = Instance(LaserManager)
    image = Instance(Image)
    threshold = Range(0, 255, 90)

    
#    def do_mapping(self):
#        lm = self.laser_manager
#        sm = lm.stage_manager
#        smap = sm._stage_map
#        
#        m, b = sm.camera_xcoefficients
#        zoom = 0
#        pxpermm = float(m) * zoom + float(b)
#        results = []
#        for hole in smap.sample_holes:
#            print hole
#            
#            sm.move_to_hole(hole.id, block=True)
#            
#            time.sleep(2)
#            
#            img, p = sm.video.snapshpt()
#            
#            cropwidth = 2
#            cropheight = 2
#            
#            #crop the image
##            cw_px = cropwidth * pxpermm
##            ch_px = cropheight * pxpermm
##            ox = 0.5 * (img.width - cw_px)
##            oy = 0.5 * (img.height - cw_px)
##            img = crop(img, ox, oy, cw_px, ch_px)
#            
#            cx, cy = self._get_corrected_xy(img, hole)
#            
#            cropx = hole.x - 0.5 * cropwidth
#            cropy = hole.y - 0.5 * cropheight
#            
#            cx = cx / pxpermm + cropx
#            cy = cy / pxpermm + cropy
#            
#            results.append('{},{},{},{},{},{}'.format(hole.x, hole.y,
#                                                cx, cy,
#                                                hole.x - cx,
#                                                hole.y - cy
#                                                ))
#        
#        corrected_tray_path = os.path.join(os.path.dirname(smap.file_path),
#                                           'corrected_{}.txt'.format(smap.name)
#                                           )
#        
#        #save results to file
#        with open(corrected_tray_path, 'w') as f:
#            for result in results:
#                f.writeline(result)
            
            
#    def _get_corrected_xy(self, img, hole):
#        correct_x = 0
#        correct_y = 0
#        return correct_x, correct_y
    
    
    def process_image(self, hx, hy):
        img = self.image
        
        
        #crop the image
        cw_px = self.cropwidth * self.pxpermm
        ch_px = self.cropheight * self.pxpermm
        #ox = 0.5 * (img.width - cw_px)
        #oy = 0.5 * (img.height - cw_px)
        img.center_crop(cw_px, ch_px)
        
        radius = 1
        for pi in img.polygonate(self.threshold, min_area=1000, max_area=4000, convextest=0):
            #exclude the border rect
            if len(pi) > 4:
                cx, cy = img.centroid(pi, frame_id=1)
                cropx = hx - 0.5 * self.cropwidth
                cropy = hy - 0.5 * self.cropheight
            
                cx = cx / float(self.pxpermm) + cropx
                cy = cy / float(self.pxpermm) + cropy
                
                #check to see if new center within one radius of old center
                dist = ((cx - hx) ** 2 + (cy - hy) ** 2) ** 0.5
                if dist < radius:
                    #this is a good new center point
                    pass
                
                
                
    def load_image(self, img):
        self.image = Image()
        if isinstance(img, str):
            self.image.load(img)
            
          
    def _threshold_changed(self):
        img = '/Users/Ross/Desktop/testtray.tiff'
        self.load_image(img)
        self.process_image(5, 5)
        
    def traits_view(self):
        v = View(Item('threshold', show_label=False),
                 Item('image', show_label=False, editor=ImageEditor()))
        return v
if __name__ == '__main__':
    am = AutomapManager()
    img = '/Users/Ross/Desktop/testtray.tiff'
    am.load_image(img)
    am.process_image(5, 5)
    
    am.configure_traits()
    
#============= EOF =====================================
