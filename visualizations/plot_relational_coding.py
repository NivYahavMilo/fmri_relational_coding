import os

import numpy as np
import matplotlib.pyplot as plt
import config
import data_normalizer.utils as utils
from data_center.static_data.static_data import StaticData


def plot_error_bar(data, roi, group, save_img):
    plt.errorbar([*range(19)],data)
    plt.title(f"Mean and Standard deviation of {roi} {group}")
    plt.xlabel("Rest TR")
    plt.ylabel("Correlation Value")
    fig1 = plt.gcf()
    plt.show()
    plt.draw()
    fig1.savefig(save_img, dpi=100)

def plot_pipe_avg(roi_name, group:str = ''):
    res_path = config.FMRI_RELATION_CODING_RESULTS_AVG.format(group=group.lower())
    data = utils.load_pkl(f"{res_path}\\{roi_name}.pkl")
    save_img = fr"{config.FMRI_RELATION_CODING_RESULTS_FIGURES.format(group=group)}\\{roi_name}.png"
    plot_error_bar(data['avg'], roi_name, group, save_img)

def gather_subjects_results(roi_name):
    res_path = config.FMRI_RELATION_CODING_RESULTS
    data = utils.load_pkl(f"{res_path}\\{roi_name}.pkl")
    rc_matrix = np.zeros((len(data), 19))
    ii=0
    for sub,l in data.items():
        rc_matrix[ii, :] += l
        ii+=1
    return rc_matrix

def plot_pipe(roi):
    rc_mat = gather_subjects_results(roi)
    rc_stats = {}
    rc_stats['mean'] = np.mean(rc_mat, axis=0)
    rc_stats['std'] = np.std(rc_mat, axis=0,ddof=1) // np.sqrt(rc_mat.shape[0])
    plot_error_bar(rc_stats, roi)

def plot_pipe_single_subject(roi, subject):
    res_path = config.FMRI_RELATION_CODING_RESULTS
    data = utils.load_pkl(f"{res_path}\\{roi}.pkl")
    sub_data = data[subject]
    plt.plot(sub_data)
    plt.title(f"Mean and Standard deviation of {roi}")
    plt.xlabel("Rest TR")
    plt.ylabel("Correlation Value")
    plt.show()


def plot_reg_and_avg_on_top():
    StaticData. inhabit_class_members()
    for roi in StaticData.ROI_NAMES:
        avg_path = config.FMRI_RELATION_CODING_RESULTS_AVG
        data_avg = utils.load_pkl(f"{avg_path}\\{roi}.pkl")
        data_avg['mean'] = data_avg.pop('avg')

        # avg after relational coding
        rc_mat = gather_subjects_results(roi)
        rc_stats = {}
        rc_stats['mean'] = np.mean(rc_mat, axis=0)
        rc_stats['std'] = np.std(rc_mat, axis=0, ddof=1) // np.sqrt(rc_mat.shape[0])

        color_lst = ['blue', 'red']
        rc = []

        data = {}
        data['bef'] = rc_stats['mean'].tolist()
        data['af'] = data_avg['mean']

        names = ['rc avg', 'signal avg']
        for _seq, _color, n in zip(data.values(), color_lst, names):
            rc.append({
                "name": f"{roi}: {n}",
                "x": _seq,
                "Y": [1, -1],
                'color':_color,
                'linewidth': 5,

            })

        fig, ax = plt.subplots(figsize=(20, 10), )

        for signal in rc:
            ax.plot(signal['x'],  # signal['y'],
                    color=signal['color'],
                    linewidth=signal['linewidth'],
                    label=signal['name'],
                    )

        # Enable legend
        ax.legend(loc="upper right")
        # avg before relational coding
        plt.title(f"Mean and Standard deviation of {roi}")
        plt.xlabel("Rest TR")
        plt.ylabel("Correlation Value")
        save_path = fr"{config.FMRI_RELATION_CODING_RESULTS_FIGURES}\\{roi}.png"
        if os.path.isfile(save_path):
            continue
        fig1 = plt.gcf()
        #plt.show()
        plt.draw()
        fig1.savefig(save_path, dpi=100)



if __name__ == '__main__':
    plot_pipe_avg()
    #plot_reg_and_avg_on_top()