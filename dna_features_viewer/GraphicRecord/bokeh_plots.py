try:
    from bokeh.plotting import figure, ColumnDataSource
    from bokeh.models import Range1d, HoverTool

    BOKEH_AVAILABLE = True
except ImportError:
    BOKEH_AVAILABLE = False

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

import matplotlib.pyplot as plt


class BokehPlottableMixin:
    def bokeh_feature_patch(
        self, start, end, strand, width=0.3, level=0, **kwargs
    ):
        """Return a dict with points coordinates of a Bokeh Feature arrow.

        Parameters
        ----------

        start, end, strand

        """
        hw = width / 2.0
        x1, x2 = (start, end) if (strand >= 0) else (end, start)
        if strand >= 0:
            head_base = max(
                x1, x2 - max(0.025 * self.sequence_length, 0.025 * (x2 - x1))
            )
        else:
            head_base = min(
                x1, x2 + max(0.025 * self.sequence_length, 0.025 * (x1 - x2))
            )
        result = dict(
            xs=[x1, x1, head_base, x2, head_base, x1],
            ys=[e + level for e in [-hw, hw, hw, 0, -hw, -hw]],
        )
        result.update(kwargs)
        return result

    def plot_with_bokeh(self, figure_width=5):
        """Plot the graphic record using Bokeh.

        Examples
        --------

        >>>


        """
        if not BOKEH_AVAILABLE:
            raise ImportError("``plot_with_bokeh`` requires Bokeh installed.")
        if not PANDAS_AVAILABLE:
            raise ImportError("``plot_with_bokeh`` requires Pandas installed.")

        # FIRST PLOT WITH MATPLOTLIB AND GATHER INFOS ON THE PLOT
        ax, (features_levels, plot_data) = self.plot(figure_width=figure_width)
        width, height = [int(100 * e) for e in ax.figure.get_size_inches()]
        plt.close(ax.figure)
        max_y = max(
            [data["annotation_y"] for f, data in plot_data.items()]
            + list(features_levels.values())
        )

        # BUILD THE PLOT ()
        hover = HoverTool(tooltips="@hover_html")
        plot = figure(
            plot_width=width,
            plot_height=height,
            tools=[hover, "xpan,xwheel_zoom,reset,tap"],
            x_range=Range1d(0, self.sequence_length),
            y_range=Range1d(-1, max_y + 1),
        )
        plot.patches(
            xs="xs",
            ys="ys",
            color="color",
            line_color="#000000",
            source=ColumnDataSource(
                pd.DataFrame.from_records(
                    [
                        self.bokeh_feature_patch(
                            feature.start,
                            feature.end,
                            feature.strand,
                            level=level,
                            color=feature.color,
                            label=feature.label,
                            hover_html=(
                                feature.html
                                if feature.html is not None
                                else feature.label
                            ),
                        )
                        for feature, level in features_levels.items()
                    ]
                )
            ),
        )

        if plot_data != {}:
            plot.text(
                x="x",
                y="y",
                text="text",
                text_align="center",
                text_font_size="12px",
                text_font="arial",
                text_font_style="normal",
                source=ColumnDataSource(
                    pd.DataFrame.from_records(
                        [
                            dict(
                                x=feature.x_center,
                                y=pdata["annotation_y"],
                                text=feature.label,
                                color=feature.color,
                            )
                            for feature, pdata in plot_data.items()
                        ]
                    )
                ),
            )
            plot.segment(
                x0="x0",
                x1="x1",
                y0="y0",
                y1="y1",
                line_width=0.5,
                color="#000000",
                source=ColumnDataSource(
                    pd.DataFrame.from_records(
                        [
                            dict(
                                x0=feature.x_center,
                                x1=feature.x_center,
                                y0=pdata["annotation_y"],
                                y1=pdata["feature_y"],
                            )
                            for feature, pdata in plot_data.items()
                        ]
                    )
                ),
            )

        plot.yaxis.visible = False
        plot.outline_line_color = None
        plot.grid.grid_line_color = None
        plot.toolbar.logo = None

        return plot
