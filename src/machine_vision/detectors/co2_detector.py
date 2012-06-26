#===============================================================================
# Copyright 2011 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

#============= enthought library imports =======================
from traits.api import on_trait_change, Any
#============= standard library imports ========================
from numpy import percentile, histogram, argmax

#============= local library imports  ==========================
from src.image.cvwrapper import asMat, grayspace, colorspace, \
    dilate, sharpen
from src.image.cvwrapper import smooth as smooth_image
from src.image.image import StandAloneImage
from hole_detector import HoleDetector
from time import time
from timeit import Timer


class CO2HoleDetector(HoleDetector):

    target_image = Any(transient=True)
#    target_area = None

    @on_trait_change('target_image:ui')
    def _add_target_window(self, new):
        try:
            #added windows will be closed by the application on exit
            self.parent.add_window(new)
        except AttributeError:
            pass

    def close_images(self):
#        if self.brightness_image is not None:
#            self.brightness_image.close()

        if self.target_image is not None:
            self.target_image.close()

#    def _segmentation_style_changed(self):
#        self._segmentation_style_hook()

#    def _segmentation_style_hook(self):
#        self.locate_sample_well(0, 0)

    def sharpen(self, src, verbose=True):
        if verbose:
            self.info('sharpening image')
        src = sharpen(src)
        return src

    def smooth(self, src, verbose=True):
#        if self.use_smoothing:
        if verbose:
            self.info('smoothing image')
        src = smooth_image(src)
        return src

    def contrast_equalization(self, src, verbose=True):
#        if self.use_contrast_equalization:
        from skimage.exposure import rescale_intensity

        if verbose:
            self.info('maximizing image contrast')

        if hasattr(src, 'ndarray'):
            src = src.ndarray
        # Contrast stretching
        p2 = percentile(src, 2)
        p98 = percentile(src, 98)
        img_rescale = rescale_intensity(src, in_range=(p2, p98))

        src = asMat(img_rescale)
        return src

    def locate_sample_well(self, cx, cy, holenum, holedim, **kw):
        '''
            if do_all== true

        '''

        #convert hole dim to pxpermm
        holedim *= self.pxpermm

        if self.target_image is not None:
            self.target_image.close()

        im = StandAloneImage(title='Positioning Error',
                             view_identifier='pychron.fusions.co2.target')
        self.target_image = im

        #use a manager to open so will auto close on quit
        self.parent.open_view(im)

        self._nominal_position = (cx, cy)
        self.current_hole = holenum
        self.info('locating CO2 sample hole {}'.format(holenum if holenum else ''))

        im.load(self.parent.get_new_frame())

        src = grayspace(im.source_frame)
        im.set_frame(0, colorspace(src.clone()))

        cw = None
        ch = None
        if self.use_crop:
            ci = 0
            cw = (1 + ci * self.crop_expansion_scalar) * self.cropwidth
            ch = (1 + ci * self.crop_expansion_scalar) * self.cropheight

            self.info('cropping image to {}mm x {}mm'.format(cw, ch))
            src = self._crop_image(src, cw, ch, image=im)

        '''
            come up with way to generate tests 
            binary representation of 0 to 2**nfeatures
            
            000000
            000001
            000010
            000011
            ...
            
        '''

        '''
        
            remove do_all as a keyword.
            make it a attribute 
            its more for debugging anyways
        '''

        width = 4
        ba = lambda v: [bool((v >> i) & 1) for i in xrange(width - 1, -1, -1)]
        test = [ba(i) for i in range(2 ** 4)]

        pos_argss = []
        ntests = 1
        for convextest, sharpen, smooth, contrast in test:
            params = self._process_image(src, im, cx, cy, holenum, holedim,
                                 smooth=smooth,
                                 contrast=contrast,
                                 sharpen=sharpen,
                                 convextest=convextest
                                 )
            if self.use_all_permutations:
                pos_argss.append(((smooth, contrast, sharpen, convextest), params))
            else:
                if params is not None:
                    pos_argss.append(params)
                    if len(pos_argss) > ntests:
                        nxs, nys = zip(*pos_argss)
                        nx = sum(nxs) / len(nxs)
                        ny = sum(nys) / len(nys)
#                        print nxs
#                        print nys
#                        print nx
#                        print ny
#                        bx, vx = histogram(nx, 3)
#                        by, vy = histogram(ny, 3)
#
#
#                        avg = lambda v, b: (v[argmax(b)] + v[argmax(b) + 1]) / 2.
#                        cen = avg(vx, bx), avg(vy, by)
#                        print cen
                        src = self.target_image.get_frame(0)


                        cx, cy = self._get_true_xy(src)
                        nomx, nomy = self._nominal_position

                        dx = (nomx - nx) * self.pxpermm
                        dy = (nomy - ny) * self.pxpermm

                        self._draw_indicator(src, (cx - dx, cy + dy), shape='crosshairs',
                                             size=10)
                        return nx, ny

#                        return avg(vx, bx), avg(vy, by)

        return pos_argss

    def _process_image(self, src, im, cx, cy, holenum, holedim,
                       smooth=False, contrast=False, sharpen=False,
                       convextest=False,
                       *args):

#        print self.use_all_permutations
#        seg1 = self.segmentation_style
        seg1 = 'threshold'
        self.info('using {} segmentation smooth={} contrast={} sharpen={} \
convextest={}'.format(seg1, smooth, contrast, sharpen, convextest))

        if sharpen:
            src = self.sharpen(src)
        if contrast:
            src = self.contrast_equalization(src)
        if smooth:
            src = self.smooth(src)

        params = []
        if self.use_all_permutations:
#            osrc = src.clone()
            for seg in ['region', 'edge', 'threshold']:
                def add():
                    st = time()
                    npos, tlow, thigh = self._segment_source(src, seg,
                                                            cx, cy,
                                                            holenum, holedim,
                                                            convextest=convextest
                                                            )

                    params.append((npos, seg, tlow, thigh, time() - st))

                self.info('using {} segmentation smooth={} contrast={} sharpen={} \
convextest={}'.format(seg, smooth, contrast, sharpen, convextest))
                add()

        else:
#            im.set_frame(0, colorspace(src))
#            seg1 = self.segmentation_style
            params, _, _ = self._segment_source(src, seg1,
                                                cx, cy,
                                                holenum, holedim,
                                                convextest=convextest
                                                )
            if params is None:
                self.info('Failed segmentation={}. Trying alternates'.format(seg1))
                test_alternates = True
                if test_alternates:
                    for seg in ['region', 'edge', 'threshold']:
                        if seg == seg1:
                            continue
                        self.info('using {} segmentation smooth={} contrast={} sharpen={} \
convextest={}'.format(seg, smooth, contrast, sharpen, convextest))
                        params, _, _ = self._segment_source(src, seg,
                                                        cx, cy,
                                                        holenum, holedim,
                                                        convextest=False
                                                        )
                        if params is not None:
                            break
                        self.info('Failed segmentation={}'.format(seg))

        return params

    def _segment_source(self, src, style, cx, cy, holenum, holedim, **kw):
        def segment(si, **kwargs):
            targets = func(si, **kwargs)
            if targets:
                npos = self._get_corrected_position(targets, cx, cy, holenum, holedim)
                if npos:
                    return npos
        func = getattr(self, '_{}_segmentation'.format(style))

        if style == 'region':
            retries = 4
            s = 5
            for j in range(1, retries):
                tl = 125 - s * j
                th = 125 + s * j
                npos = segment(src, tlow=tl,
                               thigh=th,
                               **kw
                               )
                if npos:
                    break
            return npos, tl, th
        else:
            self._threshold_start = None
            self._threshold_end = None
            return segment(src, **kw), self._threshold_start, self._threshold_end
#        retries = 25
#        s = 2
#        for j in range(1, retries):
#            self.info('segmentation iteration{}'.format(j))
#            params = dict()
##            if self.use_dilation:
##                ndilation = 2
##                for i in range(ndilation):
##                    #self.info('target not found. increasing dilation')
##                    #self.info('dilating image (increase white areas). value={}'.format(i + 1))
##        #            src = dilate(src, self._dilation_value)
##                    osrc = dilate(src, i)
##                    self.target_image.set_frame(0, colorspace(osrc))
###                    self.image.frames[0] = colorspace(osrc)
###                    self.working_image.frames[0] = colorspace(osrc)
##            else:
##                osrc = src
#            osrc = src
#            if style == 'region':
#                params['tlow'] = 125 - s * j
#                params['thigh'] = 125 + s * j
#    #            import time
#    #            time.sleep(2)
#            npos = segment(osrc, **params)
#            if npos:
#                return npos

    def _get_corrected_position(self, args, cx, cy, holenum, holedim):
        mi = holedim ** 2 * 3.14 * 0.75
        if args is None:
            return

        targets = [t for t in args if t.area > mi]

        #use only targets that are close to cx,cy
        targets = [t for t in targets
                   if self._near_center(*t.centroid_value)]
        if targets:
            nx, ny = self._get_positioning_error(targets, cx, cy, holenum)
            #self.info('found a target at {},{}'.format(nx, ny))
            return nx, ny


                #do not dilation on the first try

#            if args is not None:
#                break

#        else:
#            self.warning('no target found during search. threshold {} - {}'.
#                         format(s, e))
#            self._draw_center_indicator(self.image.frames[0])
#            return


#============= EOF =====================================
