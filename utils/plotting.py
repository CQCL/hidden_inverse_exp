from pytket.backends.backendresult import BackendResult
import matplotlib.pyplot as plt


def plot_results(result: BackendResult, n_strings=4) -> None:
    """
    Plots results in a barchart given a BackendResult. the number of stings displayed
    can be specified with the n_strings argument.
    """
    counts_dict = result.get_counts()
    sorted_shots = counts_dict.most_common()
    max_value = sorted_shots[0][1]

    n_most_common_strings = sorted_shots[:n_strings]
    x_axis_values = [str(entry[0]) for entry in n_most_common_strings]  # basis states
    y_axis_values = [entry[1] for entry in n_most_common_strings]  # counts

    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1.5, 1])
    color_list = ["orange"] * len(x_axis_values)
    ax.bar(
        x=x_axis_values,
        height=y_axis_values,
        color=color_list,
    )
    ax.set_title(label="Results")
    plt.ylim([0, 2 * max_value])
    plt.xlabel("Basis State")
    plt.ylabel("Number of Shots")
    plt.show()
