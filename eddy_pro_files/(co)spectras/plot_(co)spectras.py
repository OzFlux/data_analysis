'''
This script identifies all timestamps with a Foken flag 0 and plots the
corresponding (co)spectras including lowess fits.
Daniel Metzen, 23/07/2019
'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
from tqdm import tqdm
from statsmodels.nonparametric.smoothers_lowess import lowess


def get_good_files(ep_output_folder):
    """
    Function extract all time when the CO2 flux Foken-flag was 0.

    Parameters
    ----------
    ep_output_folder: string
        path to folder containing EddyPro output files

    Returns:
    --------
    good_files: np.array
        Array with filenames when qc_co2_flux was 0.
    """
    # read full_output file
    full_output_file = glob(f'{ep_output_folder}/**full_output*.csv*')[0]
    df = pd.read_csv(full_output_file, skiprows=[0, 2])
    # filter for Foken flag of 0 and return raw input filenames
    df = df.query('qc_co2_flux == 0')
    good_files = df['filename'].values
    return good_files


def merge_good_files(good_files, ep_output_folder):
    """
    Function to build single dataframe merging all spectras and cospectras with
    Foken flag 0 in EddyPro output folder.

    Parameters
    ----------
    good_files: iterable
        iterable containing raw 10Hz filenames when qc_co2_flux was 0
    ep_output_folder: string
        path to EddyPro output folder

    Returns:
    --------
    good_spectras, good_cospectras: tuple
        Dataframes with frequency as index and spectras or cosepctras of each
        file as columns
    """
    good_spectras = pd.DataFrame()
    good_cospectras = pd.DataFrame()
    # append data from files as columns with timestamp as name
    for f in tqdm(good_files):
        pattern = f'{f[5:13]}-{f[-8:-4]}'
        # for some reason not all qc = 0 timestamps have a full_spectra file
        try:
            full_sectra_file = glob(
                f'{ep_output_folder}/eddypro_full_cospectra/*{pattern}*.csv')[0]
        except IndexError as ie:
            #print(f'no file for {pattern} found in cospectra folder. skipping timestamp.')
            continue
        df = pd.read_csv(full_sectra_file, skiprows=12, index_col=0,
                         na_values=-9999)
        df = df.dropna()
        good_spectras[pattern] = df['f_nat*spec(ts)']
        good_cospectras[pattern] = df['f_nat*cospec(w_ts)']
    return good_spectras, good_cospectras


def plot_spectras(df, outfile=None):
    """
    Function to plot spectras.

    Parameters
    ----------
    df: pd.DataFrame
        dataframe containing spectras
    outfile (optional): string
        filepath for saving plot

    Returns:
    --------
    Pyplot figure and optionally saves figure to file
    """
    # plot data
    spectra_fig = plt.figure(1)
    plt.plot(df.median(axis=1), 'k.', alpha=.05,
             label='median data with QC flag 0')
    # plot loess smoothed line
    smoothed = lowess(df.median(axis=1).values, df.index, is_sorted=True,
                      frac=0.01, it=0)
    plt.plot(smoothed[40:, 0], smoothed[40:, 1], 'b', label='lowess fit')
    # tweak plot
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('f (Hz)')
    plt.ylabel('spectra (T)')
    plt.legend()
    plt.tight_layout()
    # save plot if desired
    if outfile:
        plt.savefig(outfile, dpi=300, bbox_inches='tight')


def plot_cospectras(df, outfile=None):
    """
    Function to plot cospectras.

    Parameters
    ----------
    df: pd.DataFrame
        dataframe containing cospectras
    outfile (optional): string
        filepath for saving plot

    Returns:
    --------
    Pyplot figure and optionally saves figure to file
    """
    # plot data
    cospectra_fig = plt.figure(2)
    plt.plot(df.median(axis=1), 'k.', alpha=.05,
             label='median data with QC flag 0')
    # plot loess smoothed line
    smoothed = lowess(df.median(axis=1).values, df.index, is_sorted=True,
                      frac=0.05, it=0)
    plt.plot(smoothed[:, 0], smoothed[:, 1], 'b', label='lowess fit')
    # plot ideal slope
    x = np.linspace(0.2, 5)
    y1 = .006*x**(-4/3)
    plt.plot(x, y1, 'r--', label='-4/3 slope')
    # tweak plot
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('f (Hz)')
    plt.ylabel('cospectra (w/T)')
    plt.legend()
    plt.tight_layout()
    # save plot if desired
    if outfile:
        plt.savefig(outfile, dpi=300, bbox_inches='tight')


def main():
    good_files = get_good_files(
        r'E:\flux_data_processing\10hz_data\MOFO_understory\ep_output\13m_canopy_height')
    good_spectras, good_cospectras = merge_good_files(
        good_files, r'E:\flux_data_processing\10hz_data\MOFO_understory\ep_output\13m_canopy_height')
    plot_spectras(good_spectras)
    plot_cospectras(good_cospectras)
    plt.show()


if __name__ == '__main__':
    main()
