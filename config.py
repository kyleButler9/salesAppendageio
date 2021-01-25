from configparser import ConfigParser


def config(ini_file='database.ini', ini_section='local_distribution_sheet'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(ini_file)

    # get section, default to postgresql
    db = {}
    if parser.has_section(ini_section):
        params = parser.items(ini_section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(ini_file_section, filename))

    return db
