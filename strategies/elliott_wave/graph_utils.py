import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random


def show_wave_point_in_original_line(sample_wave, original_point_list):
    print(sample_wave)
    df = pd.DataFrame([x.to_dict() for x in original_point_list])

    def get_next_level_subwaves(curr_wave_list):
        result_list = []
        for curr_wave in curr_wave_list:
            for sub_wave in curr_wave.sub_wave:
                if sub_wave is None:
                    continue
                result_list.append(sub_wave)
        return result_list
    
    wave_level_list = [[sample_wave]]
    while len(wave_level_list[-1]) > 0:
        wave_level_list.append(get_next_level_subwaves(wave_level_list[-1]))
    wave_level_list = wave_level_list[:-1]

    buttons = []
    all_shapes = []
    all_annotations = []
    all_traces = []
    for wave_level, sample_wave_list in enumerate(wave_level_list):
        for sample_wave in sample_wave_list:
            shape_dict = {
                "type": "line",
                "xref": "x", 
                "yref": "paper",
                "x0": sample_wave.point_list[0].time_offset,
                "y0": 0.1 + 0.01 * wave_level, 
                "x1": sample_wave.point_list[-1].time_offset, 
                "y1": 0.1 + 0.01 * wave_level,
                "line": dict(
                    color=plotly.colors.qualitative.Plotly[wave_level],
                    width=3,
                )
            }
            all_shapes.append(shape_dict)

            annotation_dict = {
                "xref": "x",
                "yref": "paper",
                "x": sample_wave.point_list[0].time_offset,
                "y": 0.1 + 0.03 * wave_level,
                "text": str(type(sample_wave)),
                "font_size": 15
            }
            all_annotations.append(annotation_dict)
            
            all_traces.append(go.Scatter(x=[p.time_offset for p in sample_wave.point_list], 
                                         y=[p.price for p in sample_wave.point_list],
                                            mode='markers',
                                            name=f"{wave_level}:{type(sample_wave)}"))
            
    shape_count = 0
    for wave_level, sample_wave_list in enumerate(wave_level_list):
        visible_dict_args = {}
        trace_visible_list = []
        for i in range(len(all_shapes)):
            visible = (i >= shape_count and i < (shape_count + len(sample_wave_list)))
            visible_dict_args.update({f"shapes[{i}].visible": visible})
            visible_dict_args.update({f"annotations[{i}].visible": visible})
            trace_visible_list.append(visible)
        trace_visible_list += [True]
        shape_count += len(sample_wave_list)
        buttons.append({
            "label": str(wave_level), 
            "method": "update", 
            "args": [{"visible": trace_visible_list}, visible_dict_args]
        })
        
    fig = go.Figure()

    for shape in all_shapes:
        fig.add_shape(**shape)
    for annotation in all_annotations:
        fig.add_annotation(**annotation)
    for trace in all_traces:
        fig.add_trace(trace)
    
    fig.add_trace(go.Scatter(x=df["time_offset"], y=df["price"],
                        mode='lines',
                        name='original'))
    
    wave_level_button = dict(active=1,
         buttons=buttons,
        )
    
    y_scale_button = dict(active=1,
             buttons=[
                dict(label='Log Scale',
                     method='update',
                     args=[{'visible': [True, True]},
                           {'yaxis': {'type': 'log'}}]),
                dict(label='Linear Scale',
                     method='update',
                     args=[{'visible': [True, False]},
                           {'yaxis': {'type': 'linear'}}])
                ],
            )

    fig.update_layout(updatemenus = list([
            y_scale_button,
            wave_level_button,
        ])
    )
    fig.show()
    