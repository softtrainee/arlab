#=============enthought library imports=======================
from traits.api import  Instance
from traitsui.api import View, Item
from src.managers.manager import Manager
#from src.managers.laser_managers.laser_manager import LaserManager
from src.image.image_helper import crop, load_image, get_polygons, contour, \
    grayspace
import os
import time
from src.image.image import Image
from src.image.image_editor import ImageEditor

#============= standard library imports ========================
#============= local library imports  ==========================


class AutomapManager(Manager):

#    laser_manager = Instance(LaserManager)
    image = Instance(Image)

    
    def do_mapping(self):
        lm = self.laser_manager
        sm = lm.stage_manager
        smap = sm._stage_map
        
        m, b = sm.camera_xcoefficients
        zoom = 0
        pxpermm = float(m) * zoom + float(b)
        results = []
        for hole in smap.sample_holes:
            print hole
            
            sm.move_to_hole(hole.id, block=True)
            
            time.sleep(2)
            
            img, p = sm.video.snapshpt()
            
            cropwidth = 2
            cropheight = 2
            
            #crop the image
            cw_px = cropwidth * pxpermm
            ch_px = cropheight * pxpermm
            ox = 0.5 * (img.width - cw_px)
            oy = 0.5 * (img.height - cw_px)
            img = crop(img, ox, oy, cw_px, ch_px)
            
            cx, cy = self._get_corrected_xy(img, hole)
            
            cropx = hole.x - 0.5 * cropwidth
            cropy = hole.y - 0.5 * cropheight
            
            cx = cx / pxpermm + cropx
            cy = cy / pxpermm + cropy
            
            results.append('{},{},{},{},{},{}'.format(hole.x, hole.y,
                                                cx, cy,
                                                hole.x - cx,
                                                hole.y - cy
                                                ))
        
        corrected_tray_path = os.path.join(os.path.dirname(smap.file_path),
                                           'corrected_{}.txt'.format(smap.name)
                                           )
        
        #save results to file
        with open(corrected_tray_path, 'w') as f:
            for result in results:
                f.writeline(result)
            
            
    def _get_corrected_xy(self, img, hole):
        correct_x = 0
        correct_y = 0
        return correct_x, correct_y
    
    
    def process_image(self):
        img = self.image
        img.circleate()
        
        #print img.polygonate(200, min_area=20)
        
    def load_image(self, img):
        self.image = Image()
        if isinstance(img, str):
            self.image.load(img)
            
    def traits_view(self):
        v = View(Item('image', show_label=False, editor=ImageEditor()))
        return v
if __name__ == '__main__':
    am = AutomapManager()
    img = '/Users/Ross/Desktop/target_automapping.png'
    am.load_image(img)
    am.process_image()
    
    am.configure_traits()
    
#============= EOF =====================================
