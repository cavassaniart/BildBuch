# Imports:
import configparser
import os
import PySimpleGUI as Itf
import datetime

# Configs:
config = configparser.ConfigParser()

if not os.path.isfile('config.ini'):
    buch_launch_layout = [[Itf.Text('Buch Path: ', size=(10, 0)),
                           Itf.Input('ex: C:/Pictures/Bildbuch', key='path'),
                           Itf.FolderBrowse('Browse', initial_folder='C:/Users/Default/')],
                          [Itf.Text('Buch name: ', size=(10, 0)),
                           Itf.Input('ex: Bildbuch', key='name')],
                          [Itf.Text('')],
                          [Itf.Button('Save', size=(15, 0)), Itf.Button('Cancel', size=(15, 0))]
                          ]
    buch_launch_window = Itf.Window('Buch Properties', buch_launch_layout, keep_on_top=True)
    event, values = buch_launch_window.read()

    if event is None or event == 'Cancel':
        buch_launch_window.close()
        exit()

    if event == 'Save':
        config['buch'] = {'buch_name': values['name'], 'buch_path': values['path']}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            buch_launch_window.close()


config.read('config.ini')
buch_name = config['buch']['buch_name']
buch_path = config['buch']['buch_path']

dat_file = '_dat.txt'


def _dat_exist():  # _dat_file and path exist/create
    _dat_exist_return = {}
    if not os.path.exists(buch_path):
        _dat_exist_return['path'] = False
        os.mkdir(buch_path, 0)
    else:
        _dat_exist_return['path'] = True

    for (dirpath, dirnames, filenames) in os.walk(buch_path):
        if not bool(str(filenames).count(dat_file)):
            _dat_exist_return[f'{dirpath}\\{dat_file}'] = False
            open(f'{dirpath}\\{dat_file}', 'x').close()

        else:
            _dat_exist_return[f'{dirpath}\\{dat_file}'] = True

    return _dat_exist_return


def _dat_load(path=buch_path, sub_path=False):  # _dat reader/loader
    _dat_loaded = []
    for (dirpath, dirnames, filenames) in os.walk(path):  # open dats
        dat_open = open(f'{dirpath}\\{dat_file}', 'r')

        dir_name = str(dirpath)  # getting dat paths
        while dir_name.count('\\'):
            dir_name = dir_name.removeprefix(dir_name[:(dir_name.index('\\')) + 1])

        for lines in dat_open:  # cleaning lines
            lines = str(lines).removesuffix('\n').removeprefix('<') \
                .replace("'", '').split('*')

            dict_temp = {}
            for l_pair in lines:  # breaking the line
                key = l_pair[:l_pair.index(':')]
                value = l_pair[l_pair.index(':') + 1:]
                dict_temp[key] = value
            _dat_loaded.append(dict_temp)
        dat_open.close()

        if not sub_path:
            break

    return _dat_loaded


def _file_load(path=buch_path, sub_path=False, reload=False):
    _dat_cache = []

    _dat_temp = {}
    _lines_cache = []

    for (dirpath, dirnames, filenames) in os.walk(path):  # reading paths and files
        _file_temp = []
        _file_temp.extend(filenames)
        _file_temp.remove(dat_file)
        _dat_temp[dirpath] = _file_temp
        if not sub_path:
            break

    for dat_path in _dat_temp:
        firs_line = True

        # Modelo: <name:value_name*date:yyyy.mm.dd*format:for*path:P:/Path/Subpath
        for file in _dat_temp[dat_path]:
            file = str(file)
            # Extension, file format:
            f_format = file[-file[::-1].index('.'):]

            # Name:
            name = file.removesuffix(f'.{f_format}')

            # Path:
            f_path = dat_path.replace('\\', '/')

            # Date(created):  # year = date[0:4]; month = date[5:7]; day = date[8:10];
            date = str(datetime.datetime.fromtimestamp
                       (os.stat(f'{dat_path}\\{file}').st_ctime))[0:10].replace("-", ".")

            # write line:
            l_dat = f'<name:{name}*date:{date}*format:{f_format.lower()}*path:{f_path}'

            if reload:
                if firs_line:
                    open(f'{dat_path}\\{dat_file}', 'w').write(f'{l_dat}')
                else:
                    open(f'{dat_path}\\{dat_file}', 'a').write(f'\n{l_dat}')

            l_dat = str(l_dat).removesuffix('\n').removeprefix('<') \
                .replace("'", '').replace('_', ' ').split('*')

            dict_temp = {}
            for l_pair in l_dat:
                key = l_pair[0:l_pair.index(':')]
                value = l_pair[l_pair.index(':') + 1:]
                dict_temp[key] = value

            _dat_exist()
            _dat_cache.append(dict_temp)
            firs_line = False

    return _dat_cache


def _dat_check(value='all', path=buch_path, sub_path=False):
    miss_all = {}
    duplicates = {}
    files = _dat_load(path, sub_path=sub_path)
    miss_files = []
    dats = _file_load(path, sub_path=sub_path)
    miss_dats = []
    check = files == dats

    if check:
        return check

    if value.count('all'):
        value = 'duplicates, files, dats'

    if value.count('duplicate'):
        index = 1
        for l_file in files:
            index += 1
            test = files.count(l_file)
            if test > 1:
                duplicates[f'{index}'] = l_file
        miss_all['duplicates'] = duplicates

    if value.count('file'):
        for l_file in files:
            test = dats.count(l_file)
            if not test:
                miss_files.append(l_file)
        miss_all['miss_file'] = miss_files

    if value.count('dat'):
        for l_file in dats:
            test = files.count(l_file)
            if not test:
                miss_dats.append(l_file)
        miss_all['miss_dat'] = miss_dats

    if not miss_all:
        raise ValueError('Error: Set "value=" as "all", "duplicates", "files" or "dats"')
    else:
        return miss_all


def _dat_append(lines):
    for l_dat in lines:
        path = f'{l_dat["path"]}\\{dat_file}'.replace('/', '\\')
        for key in l_dat:
            l_dat[key] = l_dat[key].replace(' ', '_')
        l_dat = f'\n<name:{l_dat["name"]}*date:{l_dat["date"]}*format:{l_dat["format"]}*path:{l_dat["path"]}'
        dat_open = open(path, 'a')
        dat_open.write(l_dat)
        dat_open.close()


def _dat_delete(lines, path=buch_path):  # maybe later:  'sub_path=False'
    dat = open(f'{path}\\{dat_file}', 'r+').read().split('\n')

    for item in lines:  # int -> line in dat
        if isinstance(item, int):
            if item > len(dat):
                lines.insert(lines.index(item), 'delete')
                lines.remove(item)

            elif item <= len(dat):
                lines.insert(lines.index(item), dat[item - 1])
                lines.remove(item)

    for item in lines:  # removing invalids
        if item == 'delete':
            lines.remove(item)

    for item in lines:  # removing lines
        for l_dat in dat:
            if l_dat.count(item):
                dat.remove(item)

    new_dat = open(f'{path}\\{dat_file}', 'r+')
    for item in dat:
        new_dat.write(item + '\n')

    new_dat.truncate()


_dat_exist()
_file_load(reload=True)

main_bild = True

_dat = _dat_load(sub_path=True)
dat_list = []
header_list = ['Name', 'Date', 'Format', 'Path']
first_load = True

for line in _dat:  # table organizer (maybe turn it into a function)
    dat_temp = []
    for pair in line:
        dat_temp.append(line[pair])
    first_load = False
    dat_list.append(dat_temp)

main_menu = [['&Buch', ['Properties::buch', '---', 'Exit'], ['asd']],
             ['&File', ['Open file']]]

main_bild_layout = [
    [Itf.Menu(main_menu, key='main_menu')],
    [Itf.Table(values=dat_list,
               headings=header_list,
               max_col_width=25,
               select_mode=Itf.TABLE_SELECT_MODE_BROWSE,  # select only 1
               auto_size_columns=True,
               justification='left',
               # alternating_row_color='lightblue', maybe use it later!
               num_rows=min(len(dat_list), 20),
               key='main_table',
               enable_events=True,
               bind_return_key=True
               )]]
main_buch_window = Itf.Window(config['buch']['buch_name'], main_bild_layout, grab_anywhere=False, finalize=True)

while main_bild:  # reading main_bild
    main_buch_window.TKroot.title(buch_name)
    main_buch_window['main_table'].update(values=dat_list)
    event, values = main_buch_window.read()

    if event in (Itf.WIN_CLOSED, 'Exit'):
        main_bild = False
        break

    if 'Open file' in event:  # open image - table
        f_open = values['main_table']
        if f_open:
            f_open = _dat[f_open[0]]
            os.startfile(f'{f_open["path"]}\\{f_open["name"]}.{f_open["format"]}')
        else:
            Itf.popup('There are no files selected', no_titlebar=True, keep_on_top=True)  # Centralizar botão

    if 'Properties::buch' in event:
        buch_prop_layout = [[Itf.Text("Buch Path: ", size=(10, 0)),
                             Itf.Input(buch_path, enable_events=True, key='path'),
                             Itf.FolderBrowse('Browse', initial_folder=buch_path)],
                            [Itf.Text("Buch name: ", size=(10, 0)),
                             Itf.Input(buch_name, enable_events=True, key='name')],
                            [Itf.Text('')],
                            [Itf.Button('Save', size=(15, 0)), Itf.Button('Cancel', size=(15, 0)),
                             Itf.Button('Apply', disabled=True, size=(15, 0))]
                            ]
        buch_prop_window = Itf.Window('Buch Properties', buch_prop_layout, keep_on_top=True)

        buch_prop_open = True

        while buch_prop_open:
            event, values = buch_prop_window.read()

            if event is None or event == 'Cancel':
                buch_prop_open = False
                buch_prop_window.close()
                break

            if values:
                buch_prop_window['Apply'].update(disabled=False)

            if event == 'Apply' or event == 'Save':
                buch_prop_window['Apply'].update(disabled=True)
                config['buch']['name'] = values['name']
                config['buch']['path'] = values['path']
                with open('../config.ini', 'w') as configfile:
                    config.write(configfile)

                buch_name = values['name']
                buch_path = values['path']

                if event == 'Save':
                    buch_prop_open = False
                    buch_prop_window.close()
