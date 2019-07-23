import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from tqdm import tqdm


def build_ogive_df(path_to_ogive_folder, ogive='og(w_ts)'):
    """
    Function to build single dataframe merging all ogives in EddyPro output
    folder.

    Parameters
    ----------
    path_to_ogive_folder: string
        path to folder containing ogive files
    ogive (optional): string
        columnname of ogive to merge

    Returns:
    --------
    df: pd.DataFrame
        Dataframe with frequency as index and ogives of each file as columns
    """
    path_to_ogive_folder = Path(path_to_ogive_folder)
    df_out = pd.DataFrame()
    # append data from files as columns with timestamp as name
    for f in tqdm(path_to_ogive_folder.glob('*binned_ogives*.csv')):
        obs_time = f.stem[:13]
        _df = pd.read_csv(f, skiprows=11, index_col=1, na_values=-9999)
        _df = _df.dropna(subset=[ogive])
        df_out[obs_time] = _df[ogive]
    return df_out


def plot_ogives(df, outfile=None):
    """
    Function to plot oviges contained in Dataframe.

    Parameters
    ----------
    df: pd.DataFrame
        dataframe containing ogives
    outfile (optional): string
        filepath for saving plot

    Returns:
    --------
    Pyplot figure and optionally saves figure to file
    """
    # plot data
    plt.plot(df.median(axis=1), 'k-', label='median')
    plt.fill_between(df.index, df.quantile(q=.95, axis=1),
                     df.quantile(q=.05, axis=1), color='k', alpha=.1,
                     label='5th-95th percentile')
    # plot indicator lines for 30, 60 and 120min
    plt.axvline((1/(30*60)), c='.5', ls=':', label='30 min')
    plt.axvline(1/(60*60), c='.5', ls='-.', label='60 min')
    plt.axvline(1/(120*60), c='.5', ls='--', label='120 min')
    # tweak plot
    plt.legend()
    plt.xscale('log')
    plt.xlabel('f (Hz)')
    plt.ylabel('ogives')
    plt.tight_layout()
    plt.show()
    # save plot if desired
    if outfile:
        plt.savefig(outfile, dpi=300, bbox_inches='tight')


def main():
    df = build_ogive_df(
        r'E:\flux_data_processing\10hz_data\MOFO_understory\ep_output\ogive_check\eddypro_binned_ogives')
    plot_ogives(df)


if __name__ == '__main__':
    main()
