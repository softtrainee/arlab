'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#'''
#@author: Jake Ross
#@copyright: 2009
#@license: Educational Community License 1.0
#'''
#import os
#
#def load_proxy_tree(src, dst):
#    '''
#        @type dst: C{str}
#        @param dst:
#    '''
#
#    import shutil
#
#    if os.path.exists(dst):
#        logger.info('removing %s' % dst)
#        shutil.rmtree(dst)
#
#    logger.info('copying source tree %s' % src)
#    shutil.copytree(src, dst)
#
#    logger.info('changing to dst directory')
#    os.chdir(dst)
#
#def profile_code():
#    '''
#    '''
#
#    import cProfile
#    app_path = '/Users/Ross/Programming/pychron_beta/application_launch.py'
#    l = open(app_path, 'r')
#    logger.info('Profiling code')
#    cProfile.run(l, 'profile.out')
#
#def build_documentation(src, dst):
#    '''
#        @type dst: C{str}
#        @param dst:
#    '''
#
#    logger.info('Generating Documentation')
#    print dst, os.path.join(dst, 'epyconf.cfg')
#    print os.path.isfile(os.path.join(dst, 'epyconf.cfg'))
#    import subprocess
#    subprocess.call(['epydoc', '-v',
#     '--config', os.path.join(dst, 'epyconf.cfg')])
#
#def process_source_code(dst):
#    '''
#        walk the proxy source tree and process the python source files
#
#        1. add boiler plate docstrings to the init.py files
#        2. add boiler plate docstrings to the source files
#        3. add boiler plate docstrings to the classes
#        4. add boiler plate docstrings to the methods of each class
#        
#        what should be done for files with doc strings already?
#        going to ignore unit if it has a doc string
#        
#        in the future we can grab the doc string (__doc__) 
#            and append it with new info
#        
#    
#    '''
#    packages = []
#    files = []
#    lines = 0
#    for root, dirs, _files in os.walk(dst):
#
#        for f in _files:
#            #print f
#            if f[0] != '.':
#
#                if f[-2:] == 'py':
#                    files.append(f)
#                    p = os.path.join(root, f)
#                    os.rename(p, p + '~')
#                    dest = open(p, 'w')
#                    source = open(p + '~', 'r')
#
#                    if f == '__init__.py':
#                        #print f,root
#                        h, t = os.path.split(root)
#                        packages.append(t)
#
#                        for line in source:
#                            lines += 1
#                            if line.startswith("'''"):
#                                pass
#                            else:
#                                add_init_bp(dest, t)
#                                break
#
#                    else:
#                        check_doc = False
#                        in_doc = False
#                        _class_method = False
#                        _class_po = False
#                        _def_po = False
#
#                        for i, oline in enumerate(source):
#                            lines += 1
#                            if i == 0 and not oline.startswith("'''"):
#                                #add_source_bp(dest)
#                                pass
#
#                            #get number of tabs at beginnnig
#                            space_cnt = 0
#                            for c in oline:
#                                print ord(c), c == chr(32)
#                                if c == chr(32):
#                                    space_cnt += 1
#                                else:
#                                    break
#                            print space_cnt
#                            line = oline.strip()
#                            if line.startswith('def') and not line.startswith('defined_when'):
#                                in_doc = False
#                                check_doc = True
#                                _def_po = True
#                                args = line.split(',')
#                                _class_method = False
#                                if 'self' in args[0]:
#                                    _class_method = True
#
#                                if len(args) > 1:
#                                    args = args[1:]
#                                    args[-1] = args[-1][:-2]
#                                    args = [a.strip() for a in args]
#                                else:
#                                    args = []
#                            elif line.startswith('class'):
#                                in_doc = False
#                                check_doc = True
#                                _class_po = True
#                            elif check_doc:
#                                if line.startswith("'''") and len(line) < 7:
#                                    in_doc = True
#
#                                elif _def_po and not in_doc:
#                                    add_method_bp(dest, args, _class_method, space_cnt)
#                                    _def_po = False
#                                    check_doc = False
#
#                                elif _class_po and not in_doc:
#                                    add_class_bp(dest)
#                                    _class_po = False
#                                    check_doc = False
#                            dest.write(oline)
#
#                    os.remove(os.path.join(root, f + '~'))
#    return packages, files, lines
#def add_source_bp(dest):
#    '''
#    '''
#    source_file_bp = '''\'\'\'
#@author: Jake Ross
#@copyright: 2009
#@license: Educational Community License 1.0
#\'\'\'\n'''
#    dest.write(source_file_bp)
#
#def add_init_bp(dest, name):
#    '''
#        @type name: C{str}
#        @param name:
#    '''
#    init_bp = '''\'\'\'
#%s Package contains
#
#G{packagetree }
#
#\'\'\'''' % name.capitalize()
#    dest.write(init_bp)
#
#def add_class_bp(dest):
#    '''
#    '''
#    dest.write('''    \'\'\'
#        G{classtree}
#    \'\'\'\n''')
#
#def add_method_bp(dest, args, class_method, space_cnt):
#    '''
#        @type args: C{str}
#        @param args:
#
#        @type class_method: C{str}
#        @param class_method:
#    '''
#    print space_cnt, 'asdf'
#    tab_cnt = space_cnt / 4
#    print tab_cnt, 'fads'
#    tabs = chr(9) * (tab_cnt + 1)
#    bracket = '%s\'\'\'' % tabs
#    #tabs = '    '
##    if class_method:
##        bracket = '%s\'\'\''
##        
#    tabs = chr(9) * (tab_cnt + 2)
#
#    dest.write(bracket)
#
#    if args:
#        for a in args:
#            if '=' in a:
#                a = a.split('=')[0].strip()
#
#            param_bp = '''
#    %s@type %s: C{str}
#    %s@param %s:
#''' % (tabs, a, tabs, a)
#            dest.write(param_bp)
#    else:
#        dest.write('\n')
#
#
#    dest.write(bracket + '\n')
#
#def stats(packages, files, nlines):
#    '''
#        @type files: C{str}
#        @param files:
#
#        @type nlines: C{str}
#        @param nlines:
#    '''
#    logger.info('====packages  %i=====' % len(packages))
#    logger.info('====files %i=====' % len(files))
#    logger.info('====lines  %i=====' % nlines)
#
#
#if __name__ == '__main__':
#    import logging
#    logger = logging.getLogger()
#    logger.addHandler(logging.StreamHandler())
#    logger.setLevel(logging.INFO)
#    src = os.getcwd()
##    dst = os.path.join(os.path.expanduser('~'), 'Programming', 'pychron_beta_doc')
#
##    load_proxy_tree(src, dst)
#    src = '/Users/Ross/Programming/Sandbox/build_doc_test'
#    p, f, l = process_source_code(src)
#    stats(p, f, l)
#
##    profile_code()
##
##    build_documentation(src, dst)
