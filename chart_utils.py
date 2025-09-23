# chart_utils.py
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def calculate_strike_range(current_price, strike_range_percentage):
    """Calculate strike range based on percentage of current price"""
    return current_price * (strike_range_percentage / 100.0)

def add_current_price_line(fig, current_price, chart_type, chart_text_size):
    """
    Adds a dashed white line at the current price to a Plotly figure.
    For horizontal bar charts, adds a horizontal line. For other charts, adds a vertical line.
    """
    if chart_type == 'Horizontal Bar':
        fig.add_hline(
            y=current_price,
            line_dash="dash",
            line_color="white",
            opacity=0.7
        )
    else:
        fig.add_vline(
            x=current_price,
            line_dash="dash",
            line_color="white",
            opacity=0.7,
            annotation_text=f"{current_price}",
            annotation_position="top",
            annotation=dict(
                font=dict(size=chart_text_size)
            )
        )
    return fig

def create_exposure_bar_chart(calls, puts, exposure_type, title, S, height=600, 
                              call_color='#00FF00', put_color='#FF0000', gex_type='Absolute',
                              show_calls=True, show_puts=True, show_net=True, chart_type='Bar',
                              strike_range_percentage=1.0, chart_text_size=12):
    # Filter out zero values
    calls_df = calls[['strike', exposure_type]].copy()
    calls_df = calls_df[calls_df[exposure_type] != 0]
    calls_df['OptionType'] = 'Call'

    puts_df = puts[['strike', exposure_type]].copy()
    puts_df = puts_df[puts_df[exposure_type] != 0]
    puts_df['OptionType'] = 'Put'

    # Calculate strike range around current price (percentage-based)
    strike_range = calculate_strike_range(S, strike_range_percentage)
    min_strike = S - strike_range
    max_strike = S + strike_range
    
    # Apply strike range filter
    calls_df = calls_df[(calls_df['strike'] >= min_strike) & (calls_df['strike'] <= max_strike)]
    puts_df = puts_df[(puts_df['strike'] >= min_strike) & (puts_df['strike'] <= max_strike)]

    # Filter the original dataframes for net exposure calculation
    calls_filtered = calls[(calls['strike'] >= min_strike) & (calls['strike'] <= max_strike)]
    puts_filtered = puts[(puts['strike'] >= min_strike) & (puts['strike'] <= max_strike)]

    # Calculate Net Exposure based on type using filtered data
    if exposure_type == 'GEX' or exposure_type == 'GEX_notional':
        if gex_type == 'Net':
            net_exposure = calls_filtered.groupby('strike')[exposure_type].sum() - puts_filtered.groupby('strike')[exposure_type].sum()
        else:  # Absolute
            calls_gex = calls_filtered.groupby('strike')[exposure_type].sum()
            puts_gex = puts_filtered.groupby('strike')[exposure_type].sum()
            net_exposure = pd.Series(index=set(calls_gex.index) | set(puts_gex.index))
            for strike in net_exposure.index:
                call_val = abs(calls_gex.get(strike, 0))
                put_val = abs(puts_gex.get(strike, 0))
                net_exposure[strike] = call_val if call_val >= put_val else -put_val
    elif exposure_type == 'DEX':
        net_exposure = calls_filtered.groupby('strike')[exposure_type].sum() + puts_filtered.groupby('strike')[exposure_type].sum()
    else:  # VEX, Charm, Speed, Vomma
        net_exposure = calls_filtered.groupby('strike')[exposure_type].sum() + puts_filtered.groupby('strike')[exposure_type].sum()

    # Calculate total Greek values
    total_call_value = calls_df[exposure_type].sum()
    total_put_value = puts_df[exposure_type].sum()

    # Update title to include total Greek values with colored values using HTML
    title_with_totals = (
        f"{title}     "
        f"<span style='color: {call_color}'>{total_call_value:,.0f}</span> | "
        f"<span style='color: {put_color}'>{total_put_value:,.0f}</span>"
    )

    fig = go.Figure()

    # Add calls if enabled
    if (show_calls):
        if chart_type == 'Bar':
            fig.add_trace(go.Bar(
                x=calls_df['strike'],
                y=calls_df[exposure_type],
                name='Call',
                marker_color=call_color
            ))
        elif chart_type == 'Horizontal Bar':
            fig.add_trace(go.Bar(
                y=calls_df['strike'],
                x=calls_df[exposure_type],
                name='Call',
                marker_color=call_color,
                orientation='h'
            ))
        elif chart_type == 'Scatter':
            fig.add_trace(go.Scatter(
                x=calls_df['strike'],
                y=calls_df[exposure_type],
                mode='markers',
                name='Call',
                marker=dict(color=call_color)
            ))
        elif chart_type == 'Line':
            fig.add_trace(go.Scatter(
                x=calls_df['strike'],
                y=calls_df[exposure_type],
                mode='lines',
                name='Call',
                line=dict(color=call_color)
            ))
        elif chart_type == 'Area':
            fig.add_trace(go.Scatter(
                x=calls_df['strike'],
                y=calls_df[exposure_type],
                mode='lines',
                fill='tozeroy',
                name='Call',
                line=dict(color=call_color, width=0.5),
                fillcolor=call_color
            ))

    # Add puts if enabled
    if show_puts:
        if chart_type == 'Bar':
            fig.add_trace(go.Bar(
                x=puts_df['strike'],
                y=puts_df[exposure_type],
                name='Put',
                marker_color=put_color
            ))
        elif chart_type == 'Horizontal Bar':
            fig.add_trace(go.Bar(
                y=puts_df['strike'],
                x=puts_df[exposure_type],
                name='Put',
                marker_color=put_color,
                orientation='h'
            ))
        elif chart_type == 'Scatter':
            fig.add_trace(go.Scatter(
                x=puts_df['strike'],
                y=puts_df[exposure_type],
                mode='markers',
                name='Put',
                marker=dict(color=put_color)
            ))
        elif chart_type == 'Line':
            fig.add_trace(go.Scatter(
                x=puts_df['strike'],
                y=puts_df[exposure_type],
                mode='lines',
                name='Put',
                line=dict(color=put_color)
            ))
        elif chart_type == 'Area':
            fig.add_trace(go.Scatter(
                x=puts_df['strike'],
                y=puts_df[exposure_type],
                mode='lines',
                fill='tozeroy',
                name='Put',
                line=dict(color=put_color, width=0.5),
                fillcolor=put_color
            ))

    # Add Net if enabled
    if show_net and not net_exposure.empty:
        if chart_type == 'Bar':
            fig.add_trace(go.Bar(
                x=net_exposure.index,
                y=net_exposure.values,
                name='Net',
                marker_color=[call_color if val >= 0 else put_color for val in net_exposure.values]
            ))
        elif chart_type == 'Horizontal Bar':
            fig.add_trace(go.Bar(
                y=net_exposure.index,
                x=net_exposure.values,
                name='Net',
                marker_color=[call_color if val >= 0 else put_color for val in net_exposure.values],
                orientation='h'
            ))
        elif chart_type in ['Scatter', 'Line']:
            positive_mask = net_exposure.values >= 0
            
            # Plot positive values
            if any(positive_mask):
                fig.add_trace(go.Scatter(
                    x=net_exposure.index[positive_mask],
                    y=net_exposure.values[positive_mask],
                    mode='markers' if chart_type == 'Scatter' else 'lines',
                    name='Net (Positive)',
                    marker=dict(color=call_color) if chart_type == 'Scatter' else None,
                    line=dict(color=call_color) if chart_type == 'Line' else None
                ))
            
            # Plot negative values
            if any(~positive_mask):
                fig.add_trace(go.Scatter(
                    x=net_exposure.index[~positive_mask],
                    y=net_exposure.values[~positive_mask],
                    mode='markers' if chart_type == 'Scatter' else 'lines',
                    name='Net (Negative)',
                    marker=dict(color=put_color) if chart_type == 'Scatter' else None,
                    line=dict(color=put_color) if chart_type == 'Line' else None
                ))
        elif chart_type == 'Area':
            positive_mask = net_exposure.values >= 0
            
            # Plot positive values
            if any(positive_mask):
                fig.add_trace(go.Scatter(
                    x=net_exposure.index[positive_mask],
                    y=net_exposure.values[positive_mask],
                    mode='lines',
                    fill='tozeroy',
                    name='Net (Positive)',
                    line=dict(color=call_color, width=0.5),
                    fillcolor=call_color
                ))
            
            # Plot negative values
            if any(~positive_mask):
                fig.add_trace(go.Scatter(
                    x=net_exposure.index[~positive_mask],
                    y=net_exposure.values[~positive_mask],
                    mode='lines',
                    fill='tozeroy',
                    name='Net (Negative)',
                    line=dict(color=put_color, width=0.5),
                    fillcolor=put_color
                ))

    # Calculate y-axis range with improved padding
    y_values = []
    for trace in fig.data:
        if hasattr(trace, 'y') and trace.y is not None:
            y_values.extend([y for y in trace.y if y is not None and not np.isnan(y)])
    
    if y_values:
        y_min = min(y_values)
        y_max = max(y_values)
        y_range = y_max - y_min
        
        # Ensure minimum range and add padding
        if abs(y_range) < 1:
            y_range = 1
        
        # Add 15% padding on top and bottom
        padding = y_range * 0.15
        y_min = y_min - padding
        y_max = y_max + padding
    else:
        # Default values if no valid y values
        y_min = -1
        y_max = 1

    # Update layout with calculated y-range
    padding = strike_range * 0.1
    if chart_type == 'Horizontal Bar':
        fig.update_layout(
            title=dict(
                text=title_with_totals,
                xref="paper",
                x=0,
                xanchor='left',
                font=dict(size=chart_text_size + 8)  # Title slightly larger
            ),
            xaxis_title=dict(
                text=title,
                font=dict(size=chart_text_size)
            ),
            yaxis_title=dict(
                text='Strike Price',
                font=dict(size=chart_text_size)
            ),
            legend=dict(
                font=dict(size=chart_text_size)
            ),
            barmode='relative',
            hovermode='y unified',
            xaxis=dict(
                autorange=True,
                tickfont=dict(size=chart_text_size)
            ),
            yaxis=dict(
                autorange=True,
                tickfont=dict(size=chart_text_size)
            ),
            height=height
        )
    else:
        fig.update_layout(
            title=dict(
                text=title_with_totals,
                xref="paper",
                x=0,
                xanchor='left',
                font=dict(size=chart_text_size + 8)  # Title slightly larger
            ),
            xaxis_title=dict(
                text='Strike Price',
                font=dict(size=chart_text_size)
            ),
            yaxis_title=dict(
                text=title,
                font=dict(size=chart_text_size)
            ),
            legend=dict(
                font=dict(size=chart_text_size)
            ),
            barmode='relative',
            hovermode='x unified',
            xaxis=dict(
                autorange=True,
                tickfont=dict(size=chart_text_size)
            ),
            yaxis=dict(
                autorange=True,
                tickfont=dict(size=chart_text_size)
            ),
            height=height
        )

    fig = add_current_price_line(fig, S, chart_type, chart_text_size)
    return fig
