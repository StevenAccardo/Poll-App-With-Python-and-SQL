import matplotlib.pyplot as plt


def create_pie_chart(options):
    restructured_options = []
    for option in options:
        restructured_options.append((option.text, option.vote_count))
        
    figure = plt.figure()
    axes = figure.add_subplot(1,1,1)

    axes.pie([option[1] for option in restructured_options],
             labels=[option[0] for option in restructured_options],
             autopct="%1.1f%%",
    )

    axes.legend()

    return figure