# -- coding: utf-8 --
#!/usr/bin/env python
import os
import re
from collections import OrderedDict as dict

from damgteam.core import log
import options


regex = dict(
    style_name = re.compile(r"@STYLENAME\s?=\s?(?P<style>\w+)"),
    property = re.compile(r"\@(?P<attr>[\.\w\-]+)[\:|\s]?((?P<platform>[\.\w\-]+)?[\:|\s]?(?P<subclass>[\.\w\-]+)?)[^\=]+[\=][\s]?(?P<value>[\.\w\-\s\#\+]+)"),
    #value = re.compile(r"@(?P<value>[\.\w\-]+)"),
    value = re.compile(r"@(?P<value>[\.\w\-\:]+)"),
    numeric = re.compile(r"(?P<num>^\d+(\.\d{0,2})?)"),
    derived = re.compile(r"@(?P<value>[^\:]+\:[^\:]+)?\:"),
    )


class StylesheetManager(object):
    """
    The StylesheetManager reads and parses stylesheet data, plus does some basic sass 
    substitution via external config files.

    :param QtGui.QWidget parent: parent UI.
    :param str style: default style name.
    :param list paths: additional search paths.
    """
    def __init__(self, parent=None, style='default', paths=[]):
        from PySide.QtGui import QFontDatabase

        self._ui            = parent                    # parent UI
        self._style         = style                     # style to parse
        self._font_db       = QFontDatabase()           # font database
        self._fonts         = dict()                    # dictionary of valid font types (ui, mono)

        self._config_paths  = ()                        # paths for cfg mods
        self._config_files  = dict()                    # cfg files

        self._qss_paths     = ()                        # qss file paths
        self._qss_files     = dict()                    # qss files
        self._initialized   = False

        # debugging data
        self._data          = dict()

        if not self._initialized:
            self.run(paths=paths)

    def run(self, paths=[]):
        """
        Read all of the currently defined config files/stylesheets.

        :param str style: style name to parse.
        :param list paths: additional search paths.
        """
        self._fonts = self.initializeFontsList()

        self._config_paths = self._get_config_paths(paths=paths)
        self._config_files = self._get_config_files(self._config_paths)
        self._qss_paths = self._get_qss_paths(paths=paths)
        self._qss_files = self._get_qss_files(self._qss_paths)

        # set parent defaults if not already set
        defaults = self.font_defaults()
        for default in defaults.keys():
            if hasattr(self._ui, default):
                if getattr(self._ui, default) is None:
                    value = defaults.get(default)
                    #print '# DEBUG: setting UI default; "%s", "%s"' % (default, value)
                    setattr(self._ui, default, value)

        self._initialized = True

    @property
    def style(self):
        return self._style

    def style_data(self, **kwargs):
        """
        Return the stylesheet data.

        :returns: parsed stylesheet data.
        :rtype: str
        """
        stylesheet_name = kwargs.pop('stylesheet_name', 'default')
        palette_style = kwargs.pop('palette_style', 'default')
        font_style = kwargs.pop('font_style', 'default')
        
        self._data = dict()
        parser = StyleParser(self, style=stylesheet_name, palette_style=palette_style, font_style=font_style)
        parser.run(style=stylesheet_name, palette_style=palette_style, font_style=font_style)
        data = parser.data(**kwargs)

        # grab data here for debugging
        self._data = parser._data
        return data

    @property
    def config_names(self):
        """
        Returns a list of config file names.

        :returns: list of config names.
        :rtype: list
        """
        return self._config_files.keys()    

    def config_files(self, style='default'):
        """
        Returns a dictionary of config files for the given style.

        :param str style: style name to return.

        :returns: font/palette config files.
        :rtype: dict
        """
        return self._config_files.get(style, {})

    @property
    def qss_names(self):
        """
        Returns a list of stylesheet file names.

        :returns: list of stylesheet names.
        :rtype: list
        """
        return self._qss_files.keys()    

    @property
    def palette_styles(self):
        """
        Returns a list of palette style names.

        :returns: list of palette names.
        :rtype: list
        """
        styles = []
        for style_name, files in self._config_files.iteritems():
            if 'palette' in files:
                value = files.get('palette', None)
                if value is not None:
                    if os.path.exists(value):
                        styles.append(style_name)
        return styles

    @property
    def font_styles(self):
        """
        Returns a list of font style names.

        :returns: list of font style names.
        :rtype: list
        """
        styles = []
        for style_name, files in self._config_files.iteritems():
            if 'fonts' in files:
                value = files.get('fonts', None)
                if value is not None:
                    if os.path.exists(value):
                        styles.append(style_name)
        return styles

    @property
    def qss_files(self):
        return self._qss_files.values() 

    def _get_config_paths(self, paths=[]):
        """
        Read configs from config paths.

        :param list paths: list of paths to add to the scan.

        :returns: array of search paths.
        :rtype: tuple
        """
        if paths and type(paths) in [str, unicode]:
            paths = [paths,]

        cfg_paths = ()
        cfg_paths = cfg_paths + (options.SCENEGRAPH_CONFIG_PATH,)

        # read external paths
        if 'SCENEGRAPH_CONFIG_PATH' in os.environ:
            spaths = os.getenv('SCENEGRAPH_CONFIG_PATH').split(':')
            if paths:
                for p in paths:
                    if p not in spaths:
                        spaths.append(p)

            for path in spaths:
                if path not in cfg_paths:
                    if not os.path.exists(path):
                        log.warning('config path "%s" does not exist, skipping.' % path)
                        continue
                    log.debug('reading config external path: "%s".' % path)
                    cfg_paths = cfg_paths + (path,)

        return cfg_paths

    def _get_qss_paths(self, paths=[]):
        """
        Read stylesheets from config paths.

        :param list paths: list of paths to add to the scan.

        :returns: array of search paths.
        :rtype: tuple
        """
        if paths and type(paths) in [str, unicode]:
            paths = [paths,]

        qss_paths = ()
        qss_paths = qss_paths + (options.SCENEGRAPH_STYLESHEET_PATH,)

        # read external paths
        if 'SCENEGRAPH_STYLESHEET_PATH' in os.environ:
            qpaths = os.getenv('SCENEGRAPH_STYLESHEET_PATH').split(':')
            if paths:
                for p in paths:
                    if p not in qpaths:
                        qpaths.append(p)

            for path in qpaths:
                if path not in qss_paths:
                    if not os.path.exists(path):
                        log.warning('stylesheet path "%s" does not exist, skipping.' % path)
                        continue
                    log.debug('reading external stylesheet path: "%s".' % path)
                    qss_paths = qss_paths + (path,)

        return qss_paths

    def _get_config_files(self, paths=[]):
        """
        Get config files.

        :param list path: ist of paths to add to the scan.

        :returns: dictionary of config names/filenames.
        :rtype: dict
        """
        cfg_files = dict()
        if not paths:
            return []

        for path in paths:
            for fn in os.listdir(path):
                bn, fext = os.path.splitext(fn)
                if fext.lower() in ['.ini', '.cfg']:
                    cfg_file = os.path.join(path, fn)

                    names = bn.split('-')
                    if len(names) < 2:
                        log.warning('improperly named config file: "%s"' % cfg_file)
                        continue

                    style_name, cfg_type = names
                    if style_name not in cfg_files:
                        cfg_files[style_name] = dict(fonts=None, palette=None)

                    log.debug('adding %s config "%s" from "%s".' % (cfg_type, style_name, cfg_file))
                    cfg_files[style_name][cfg_type] = cfg_file
        return cfg_files

    def _get_qss_files(self, paths=[]):
        """
        Get qss files.

        :param list path: ist of paths to add to the scan.

        :returns: dictionary of stylesheet names/filenames.
        :rtype: dict
        """
        qss_files = dict()
        if not paths:
            return []

        for path in paths:
            for fn in os.listdir(path):
                bn, fext = os.path.splitext(fn)
                if fext.lower() in ['.qss', '.css']:
                    qss_file = os.path.join(path, fn)
                    if qss_file not in qss_files.values():
                        style_name = self._parse_stylesheet_name(qss_file)
                        if style_name is None:
                            log.warning('cannot parse style name from "%s".' % qss_file)
                            style_name = 'no-style'

                        log.debug('adding stylesheet "%s" from "%s".' % (style_name, qss_file))

                        if style_name not in qss_files:
                            qss_files[style_name] = qss_file
        return qss_files

    def _parse_stylesheet_name(self, filename):
        """
        Parse the stylesheet name from a file.

        :param str: filename to read.

        :returns: style name.
        :rtype: str
        """
        style_name = None
        if os.path.exists(filename):
            for line in open(filename,'r'):
                line = line.rstrip('\n')
                rline = line.lstrip(' ')
                rline = rline.rstrip()
                smatch = re.search(regex.get('style_name'), rline)
                if smatch:
                    style_name = smatch.group('style')
                    break
        return style_name

    def add_config(self, filename, name=None):
        """
        Add a config to the config files attribute.

        :param str filename: filename to read.
        :param str name: name of the config.
        """
        if filename in self._config_files.values():
            for cfg_name, cfg_file in self._config_files.iteritems():
                if cfg_file == filename:
                    if name != cfg_name:
                        self._config_files.pop(cfg_name)
        self._config_files[name] = filename

    #- Fonts -----
    def initializeFontsList(self, valid=[]):
        """
        Builds the manager fonts list.

        :param list valid: list of valid font names.

        :returns: dictionary of fonts.
        :rtype: dict
        """
        if not valid:
            valid = [x for fontlist in options.SCENEGRAPH_VALID_FONTS.values() for x in fontlist]

        result = dict(ui=[], mono=[])
        for font_name in self._font_db.families():
            if font_name in valid:
                if not self._font_db.isFixedPitch(font_name):                
                    result['ui'].append(font_name)
                else:
                    result['mono'].append(font_name)
        return result

    def buildUIFontList(self, valid=[]):
        """
        Returns a list of monospace fonts.
        """
        if not valid:
            valid = options.SCENEGRAPH_VALID_FONTS.get('ui')

        families = []
        for font_name in self._fonts.get('ui'):
            if font_name in valid:
                families.append(font_name)
        return families

    def buildMonospaceFontList(self, valid=[]):
        """
        Returns a list of monospace fonts.
        """
        if not valid:
            valid = options.SCENEGRAPH_VALID_FONTS.get('mono')

        families = []
        for font_name in self._fonts.get('mono'):
            if font_name in valid:
                families.append(font_name)
        return families

    def buildNodesFontList(self, valid=[]):
        """
        Returns a list of fonts for node display.
        """
        if not valid:
            valid = options.SCENEGRAPH_VALID_FONTS.get('nodes')

        families = []
        all_fonts = [x for fontlist in self._fonts.values() for x in fontlist]
        for font_name in all_fonts:
            if font_name in valid:
                families.append(font_name)
        return families

    def font_defaults(self, platform=None, style='default'):
        """
        Builds a dictionary of font & size defaults by platform.

        :param str platform: os type

        :returns: font and font size defaults dictionary.
        :rtype: dict
        """
        if platform is None:
            platform = options.PLATFORM

        defaults = dict()

        def_font_config = self.config_files(style).get('fonts', None)
        if not os.path.exists(def_font_config):
            log.error('config "%s" does not exist.' % def_font_config)
            return defaults

        parser = StyleParser(self)
        data = parser._parse_configs(def_font_config)
        data = parser._parse_platform_data(data)

        # substitute attribute names
        for attr, val in data.iteritems():
            attr = re.sub('-', '_', attr)
            defaults[attr] = val
        return defaults


class StyleParser(object):

    """
    The StyleParse class reads stylesheets, parses config files and does sass-style
    replacements for properties.
    """
    def __init__(self, parent, style=None, **kwargs):

        self.manager            = parent
        self.style              = style
        self.palette_style      = kwargs.get('palette_style', 'default')
        self.font_style         = kwargs.get('font_style', 'default')

        self._stylesheet        = None
        self._config_fonts      = None
        self._config_palette    = None

        self._data              = dict()

    def run(self, style='default', **kwargs):
        """
        Parse stylesheet data for a given style and substitute values 
        from config file data. 

        :param str style: style name to parse.
        :param dict kwargs: overrides.
        """
        palette_style = kwargs.get('palette_style', 'default')
        font_style = kwargs.get('font_style', 'default')

        stylesheet = self.manager._qss_files.get(style, None)

        #configs    = self.manager.config_files(style)
        config_palette = self.manager._config_files.get(palette_style).get('palette')
        config_fonts = self.manager._config_files.get(font_style).get('fonts')

        if stylesheet and os.path.exists(stylesheet):
            self._stylesheet = stylesheet

        if config_palette and os.path.exists(config_palette):
            self._config_palette = config_palette

        if config_fonts and os.path.exists(config_fonts):
            self._config_fonts = config_fonts

        if self._stylesheet is not None:
            self._data = self._parse_configs()

    def _parse_configs(self, configs=[]):
        """
        Parse config data into a dictionary.
        """
        data = dict()
        data.update(defaults=dict())

        if not configs:
            configs = [self._config_fonts, self._config_palette]

        if type(configs) in [str, unicode]:
            configs = [configs,]

        for config in configs:
            if not config or not os.path.exists(config):
                continue

            with open(config) as f:
                for line in f.readlines():
                    line = line.rstrip('\n')
                    rline = line.lstrip(' ')
                    rline = rline.rstrip()
                    smatch = re.search(regex.get('property'), rline)
                    if smatch:
                        match_data = smatch.groupdict()

                        platform = None
                        subclass = None
                        class_name = 'defaults'

                        match_groups = [k for k, v in match_data.iteritems() if v]
                        
                        if 'platform' in match_groups:
                            if match_data.get('platform'):
                                platform = match_data.get('platform')

                        if 'subclass' in match_groups:
                            if match_data.get('subclass'):
                                subclass = match_data.get('subclass')

                        # haxx
                        if platform is not None:
                            if subclass is not None:
                                tmp = platform
                                platform = subclass
                                subclass = tmp

                            class_name = platform

                        if class_name not in data:
                            data[class_name] = dict()

                        attr_name = match_data.get('attr')
                        attr_val = match_data.get('value')

                        attribute = attr_name
                        if subclass:
                            attribute = '%s:%s' % (attr_name, subclass)

                        if attr_val:
                            data[class_name][attribute] = attr_val
        return data


    def data(self, verbose=False, **kwargs):
        """
        Returns the raw stylesheet data with config values substituted.

        :returns: stylesheet data.
        :rtype: str
        """
        data = self._parse_platform_data(self._data, **kwargs)
       
        ff = open(self._stylesheet, 'r')
        ss_lines = ""
        for line in ff.readlines():
            if line:
                # fix some unicode errors
                line = str(line)
                if '@' in line:
                    if not '@STYLENAME' in line:
                        if line.count('@') > 1:
                            new_value = line
                            values = re.findall(regex.get('value'), line)
                            if values:                                
                                for value in values:
                                    new_value = re.sub('@%s' % str(value), str(data.get(value)), new_value)
                            
                            ss_lines += new_value
                            continue

                        smatch = re.search(regex.get('value'), line)
                        if smatch:
                            value = str(smatch.group('value'))
                            if value in data:
                                new_value = str(data.get(value))
                                ss_lines += '%s' % re.sub('@%s' % value, new_value, line)
                                continue

                ss_lines += '%s' % line
        return ss_lines

    def _parse_platform_data(self, data, platform=None, verbose=False, **kwargs):
        """
        Parse config data into platform defaults, etc.

        :param dict data: parsed config data.
        :returns: dictionary of parsed config data.
        """
        import copy
        result = dict()        

        if platform is None:
            platform = options.PLATFORM

        # copy the input data
        style_data = copy.deepcopy(data)

        for k, v in style_data.pop('defaults', {}).iteritems():
            result['%s' % k] = v

        if options.PLATFORM in style_data:
            platform_defaults = style_data.get(options.PLATFORM)

            for attr, val in platform_defaults.iteritems():
                result[attr] = val

        # kwarg overrides
        if kwargs:
            for kattr, kval in kwargs.iteritems():
                if kval:
                    attr_name = re.sub('_', '-', kattr)
                    if verbose:
                        print('# DEBUG: override "%s": ' % attr_name, kval)
                    result[attr_name] = kval

        #  derive subclasses
        for attr, val in result.iteritems():

            if ':' in attr:
                transform = eval(val)
                ttype = type(transform)
                parent_attr, subclass = attr.split(':')
                parent_value = result.get(parent_attr)

                if ttype in [int, float]:
                    nmatch = re.search(regex.get('numeric'), parent_value)
                    if nmatch:
                        parent_value = float(nmatch.group('num'))
                        if ttype == int:
                            parent_value = int(parent_value)

                        derived_val = (parent_value + transform)

                        # this is kinda hacky, need to think of a better way to 
                        # translate the value back.
                        if 'font' in attr:
                            derived_val = '%dpt' % derived_val
                            result[attr] = derived_val
        return result


    def apply(self, stylesheet=None, style=None):
        """
        * Not used.        
        """
        from PySide import QtCore
        ssf = QtCore.QFile(default_stylesheet)
        ssf.open(QtCore.QFile.ReadOnly)
        self._ui.setStyleSheet(str(ssf.readAll()))
        attr_editor = self._ui.getAttributeEditorWidget()
        if attr_editor:
            attr_editor.setStyleSheet(str(ssf.readAll()))
        ssf.close()
