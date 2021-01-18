with open('default.par', 'r') as f:
    def_ = f.read()
    DEFAULT_PAR = {}
    for s in def_.split('\n')[:-1]:
        k = s.split('=')[0].strip()
        v = s.split('=')[1].strip()
        DEFAULT_PAR[k] = v

def run_sofia(par, par_file):
    """
    Runs SoFiA with parameters provided in dictionary par. It saves the
    parameters in par_file.

    Parameters
    ----------
    par : dict
        Dictionary of parameters. Example:
        par = {
                'input.data'                 :  'sofia_test_datacube.fits',
                'scaleNoise.mode'            :  'local',
                'scaleNoise.windowXY'        :  31,
                'scaleNoise.windowZ'         :  31,
                'scfind.kernelsXY'           :  '0, 5, 10',
                'scfind.threshold'           :  3.5,
                'reliability.enable'         :  'true',
                'reliability.fmin'           :  25.0,
                'output.directory'           :  'sofia_test',
                'output.filename'            :  'sofia_test_output',
                'output.writeMask'           :  'true',
                'output.writeMask2d'         :  'true',
                'output.writeMoments'        :  'true',
                'output.marginCubelets'      :  10,
                'output.overwrite'           :  'true'
            }

    par_file : str
        Name of the file to save the parameters into.

    Returns
    -------
    output : str
        STDOUT output produced by SoFiA.

    error : str
        STDERR output produced by SoFiA.

    """
    par_str = '\n'.join([k + " = " + str(par[k]) for k in par.keys()])

    f = open(par_file, "w")
    f.write(par_str)
    f.close()

    bashCommand = "sofia " + par_file

    if par['output.directory']:
        import os
        if not os.path.isdir(par['output.directory']):
            os.mkdir(par['output.directory'])

    import subprocess
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if output:
        output = output.decode('utf-8')
    if error:
        error = error.decode('utf-8')

    return output, error

def read_sofia_cat(cat_file_path):
    """
    Reads SoFiA generated catalog.

    Parameters
    ----------
    cat_file_path : str
        Name of the catalog file.

    Returns
    -------
    table : astropy.table.table.QTable
        Astropy Table with the catalog entries.

    """
    from astropy.table import QTable
    import astropy.units as u
    import numpy as np

    cat_file = open(cat_file_path, 'r')
    cat = cat_file.read().split('\n')

    vals = [[a[0]+' '+a[1]]+list(a)[2:] for a in map(lambda s: s.split(), cat[13:-1])]

    temp = np.array(vals).transpose()

    name = temp[0]
    ids = list(map(int, temp[1]))

    x = list(map(float, temp[2])) * u.pix
    y = list(map(float, temp[3])) * u.pix
    z = list(map(float, temp[4])) * u.pix

    x_min = list(map(int, temp[5])) * u.pix
    x_max = list(map(int, temp[6])) * u.pix
    y_min = list(map(int, temp[7])) * u.pix
    y_max = list(map(int, temp[8])) * u.pix
    z_min = list(map(int, temp[9])) * u.pix
    z_max = list(map(int, temp[10])) * u.pix

    n_pix = list(map(int, temp[11]))

    f_min = list(map(float, temp[12])) * u.Jy/u.beam
    f_max = list(map(float, temp[13])) * u.Jy/u.beam
    f_sum = list(map(float, temp[14])) * u.Jy/u.beam

    rel = list(map(float, temp[15]))
    flag = list(map(int, temp[16]))

    rms = list(map(float, temp[17])) * u.Jy/u.beam
    w20 = list(map(float, temp[18])) * u.pix
    w50 = list(map(float, temp[19])) * u.pix

    ell_maj = list(map(float, temp[20])) * u.pix
    ell_min = list(map(float, temp[21])) * u.pix
    ell_pa = list(map(float, temp[22])) * u.deg

    ell3s_maj = list(map(float, temp[23])) * u.pix
    ell3s_min = list(map(float, temp[24])) * u.pix
    ell3s_pa = list(map(float, temp[25])) * u.deg

    kin_pa = list(map(float, temp[26])) * u.deg

    err_x = list(map(float, temp[27])) * u.pix
    err_y = list(map(float, temp[28])) * u.pix
    err_z = list(map(float, temp[29])) * u.pix
    err_f_sum = list(map(float, temp[30])) * u.Jy/u.beam

    ra = list(map(float, temp[31])) * u.deg
    dec = list(map(float, temp[32])) * u.deg

    v_app = list(map(float, temp[33])) * u.m/u.s

    return QTable([name, ids, x, y, z, x_min, x_max, y_min, y_max, z_min, z_max, n_pix, f_min, f_max, f_sum, rel, flag,
                rms, w20, w50, ell_maj, ell_min, ell_pa, ell3s_maj, ell3s_min, ell3s_pa, kin_pa, err_x, err_y, err_z,
                err_f_sum, ra, dec, v_app],
                names = cat[10].split()[1:],
                meta = {'Name': cat[0][2:],
                        'Creator': cat[1].split(':')[1].strip(),
                        'Time': cat[2].split(':')[1].strip()
                       })

def read_SDC_cat(cat_file_path):
    """
    Reads catalog format provided by SDC2 challenge.

    Parameters
    ----------
    cat_file_path : str
        Name of the catalog file.

    Returns
    -------
    table : astropy.table.table.QTable
        Astropy Table with the catalog entries.

    """
    from astropy.io import ascii

    return ascii.read(cat_file_path)
