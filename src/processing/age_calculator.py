from traits.api import HasTraits, Float, Property, cached_property, List, Button, Str, File, Any
from traitsui.api import View, Item, ListEditor, InstanceEditor, Label, HGroup, Group, TabularEditor
from uncertainties import ufloat
import xlrd
from src.processing.argon_calculations import calculate_arar_age
from traitsui.tabular_adapter import TabularAdapter


class ExcelMixin(object):
    def _make_row(self, sheet, ri, cast=str):
        return [cast(sheet.cell(ri, ci).value) for ci in range(sheet.ncols)]

class Constants(ExcelMixin):
    age_units = 'Ma'
    def __init__(self, sheet):
        self.sheet=sheet
        #lambda_epsilon = ufloat((5.81e-11,
        #                                    0))
        #lambda_beta = ufloat((4.962e-10,
        #                                 0))

#        lambda_e = ufloat((5.755e-11,
#                                            1.6e-13))
#        lambda_b = ufloat((4.9737e-10,
#                                         9.3e-13))

        lambda_e = self._get_constant('lambda_e', 5.81e-11, 1.6e-13)
#        lambda_e = get_constant('lambda_e', 5.81e-11, 0)
        lambda_b = self._get_constant('lambda_b', 4.962e-10, 9.3e-13)
#        lambda_b = get_constant('lambda_b', 4.962e-10, 0)

        self.lambda_k = lambda_e + lambda_b
        #lambda_k = get_constant('lambda_K', 5.81e-11 + 4.962e-10, 0)

        self.lambda_Ar37 = self._get_constant('lambda_Ar37', 0.01975, 0) #per day
        #lambda_37 = ufloat((0.01975, 0)) #per day
        self.lambda_Ar39 = self._get_constant('lambda_Ar39', 7.068000e-6, 0)  #per day
        #lambda_39 = ufloat((7.068000e-6, 0))  #per day
        self.lambda_Cl36 = self._get_constant('lambda_Cl36', 6.308000e-9, 0)  #per day
        #lambda_cl36 = ufloat((6.308000e-9, 0))  #per day

        #atmospheric ratios
        self.atm4036 = self._get_constant('Ar40_Ar36_atm', 295.5, 0)
        self.atm4038 = self._get_constant('Ar40_Ar38_atm', 1575, 2)

        #atm4038 = ufloat((1575, 2))
        self.atm3638 = self.atm4038 / self.atm4036
        self.atm3836 = self.atm4036 / self.atm4038
        
    def _get_constant(self, name, value, error):
        sheet=self.sheet
        header=self._make_row(sheet, 0)
        idx=header.index(name)
        idx_err=header.index('{}_err'.format(name))
        try:
            value=sheet.cell(1,idx).value
        except Exception,e:
            print e

        try:
            error=sheet.cell(1,idx_err).value
        except Exception, e:
            print e
        
#        print type(value)
        return ufloat((value, error))
        
        
class Isotope(HasTraits):
    value=Float
    error=Float
    uvalue=Property
    name=Str
    @cached_property
    def _get_uvalue(self):
        return ufloat((self.value, self.error))
    
    def traits_view(self):
        v=View(HGroup(Label(self.name), Item('value'), Item('error')))
        return v
    
class Result(HasTraits):
    age=Any
    identifier=Str
    
class ResultAdapter(TabularAdapter):
    columns=[
             ('Identifier', 'identifier'),
             ('Age', 'age'),
             ('Error', 'age_error'),
             ]
    age_text=Property
    age_error_text=Property
    def _float_fmt(self,v, n):
        return '{{:0.{}f}}'.format(n).format(v)
    
    def _get_value(self, attr):
        v=getattr(self.item, attr)
        return self._float_fmt(v.nominal_value, 5)
    
    def _get_error(self, attr):
        v=getattr(self.item, attr)
        return self._float_fmt(v.std_dev(), 6)
    
    def _get_age_text(self):
        return self._get_value('age')
    
    def _get_age_error_text(self):
        return self._get_error('age')
    
class AgeCalculator(HasTraits, ExcelMixin):
#    isotopes=List
    calc_button=Button
    results=List
    path=File
    def _calc_from_file(self, path):
        self.results=[]
        
        workbook=xlrd.open_workbook(path)
        ir_s=workbook.sheet_by_name('irradiation')
        i_s=workbook.sheet_by_name('intensities')
        c_s=workbook.sheet_by_name('constants')
        bl_s=workbook.sheet_by_name('blanks')
#            irrad_info=k4039, k3839, k3739, ca3937, ca3837, ca3637, cl3638, chronology_segments , decay_time
        #irrad_info=(1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), [], 1
        
        header=self._make_row(ir_s, 0)

        idx_k4039=header.index('k4039')
        idx_k4039err=header.index('k4039_err')
        idx_k3839=header.index('k3839')
        idx_k3839err=header.index('k3839_err')
        idx_k3739=header.index('k3839')
        idx_k3739err=header.index('k3839_err')
        
        idx_ca3937=header.index('ca3937')
        idx_ca3937err=header.index('ca3937_err')
        idx_ca3837=header.index('ca3837')
        idx_ca3837err=header.index('ca3837_err')
        idx_ca3637=header.index('ca3637')
        idx_ca3637err=header.index('ca3637_err')
        
        idx_cl3638=header.index('cl3638')
        idx_cl3638err=header.index('cl3638_err')
        
        row=self._make_row(ir_s, 1, cast=float)
        irrad_info=[(row[idx_k4039], row[idx_k4039err]),
                               (row[idx_k3839], row[idx_k3839err]),
                               (row[idx_k3739], row[idx_k3739err]),
                               (row[idx_ca3937], row[idx_ca3937err]),
                               (row[idx_ca3837], row[idx_ca3837err]),
                               (row[idx_ca3637], row[idx_ca3637err]),
                               (row[idx_cl3638], row[idx_cl3638err])
                               ]
                       
        irrad_info=irrad_info+[[], 1]
        
        header=self._make_row(i_s, 0)
        blank_header=self._make_row(bl_s, 0)
        
        idx_j=header.index('j')
        idx_jerr=header.index('j_err')        
        idx_ic=header.index('ic')
        idx_ic_err=header.index('ic_err')
        
        for ri in range(1,i_s.nrows):
            row=self._make_row(i_s, ri)
            idn=row[0]
            row=[idn]+map(float, row[1:])

            blrow=self._make_row(bl_s, ri)
            idn=blrow[0]
            blrow=[idn]+map(float, blrow[1:])
            
            baselines=[(0,0),(0,0),(0,0),(0,0),(0,0)]
            backgrounds=[(0,0),(0,0),(0,0),(0,0),(0,0)]
            
            signals=self._load_signals(header, row)
            blanks=self._load_signals(blank_header, blrow)
            
            j=(row[idx_j],row[idx_jerr])
            ic=(row[idx_ic],row[idx_ic_err])
            constants_obj=Constants(c_s)
            arar_result=calculate_arar_age(signals, baselines, blanks, backgrounds, j, irrad_info, 
                                           a37decayfactor=1,a39decayfactor=1,
                                           ic=ic, 
                                           constants=constants_obj)
            
            self.results.append(Result(identifier=idn,
                                       age=arar_result['age']/1e6))
#            self.result+='{:<10s} {}\n'.format(idn, str(arar_result['age']/1e6))
            
#            for i in range(5):
#                obj=self.isotopes[i]
#                obj.value=signals[i][0]
#                obj.error=signals[i][1]
    def _load_signals(self, header, row):
        idx_40=header.index('Ar40')
        idx_40err=header.index('Ar40_err')
        idx_39=header.index('Ar39')
        idx_39err=header.index('Ar39_err')
        idx_38=header.index('Ar38')
        idx_38err=header.index('Ar38_err')
        idx_37=header.index('Ar37')
        idx_37err=header.index('Ar37_err')
        idx_36=header.index('Ar36')
        idx_36err=header.index('Ar36_err')
        signals=[
                     (row[idx_40],row[idx_40err]),
                     (row[idx_39],row[idx_39err]),
                     (row[idx_38],row[idx_38err]),
                     (row[idx_37],row[idx_37err]),
                     (row[idx_36],row[idx_36err]),
                     ]
        return signals
         
    def _calc_button_fired(self):
        path=self.path
        self._calc_from_file(path)
         
    def traits_view(self):
        isotope_grp=Item('isotopes', show_label=False,style='custom',editor=ListEditor(mutable=False,
                                                                      style='custom',
                                                       editor=InstanceEditor()))
        
        v=View(
               HGroup(Item('path',springy=True, show_label=False),
                      Item('calc_button', show_label=False)),
#               isotope_grp,
               Item('results', editor=TabularEditor(adapter=ResultAdapter(),
                                                    editable=False
                                                    ),
                    
                    show_label=False,style='custom'),
               title='Age Calculator',
               width=500,
               height=300,
               )
        return v
    
    def _isotopes_default(self):
        return [
                Isotope(name='Ar40'),
                Isotope(name='Ar39'),
                Isotope(name='Ar37'),
                Isotope(name='Ar37'),
                Isotope(name='Ar36'),
                
                ]
if __name__ == '__main__':
    ag=AgeCalculator()
    ag.path='/Users/argonlab2/Sandbox/age_calculator_template.xls'
    ag.configure_traits()