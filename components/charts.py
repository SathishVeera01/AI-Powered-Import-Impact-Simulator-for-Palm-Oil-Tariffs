import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Institutional palette (World Bank / IMF style) ─────────────────────────────
C = {
    'navy':    '#1B2A4A',
    'teal':    '#2E7D82',
    'teal2':   '#4A9FA5',
    'amber':   '#A0622A',
    'red':     '#B94040',
    'green':   '#2D6A4F',
    'bg':      'rgba(0,0,0,0)',
    'surface': '#FFFFFF',
    'grid':    '#E8ECF1',
    'border':  '#DDE1E7',
    'text':    '#1B2A4A',
    'muted':   '#6B7280',
    'faint':   '#9CA3AF',
}

# Legend always horizontal at bottom, outside plot area
LEGEND = dict(
    orientation='h',
    yanchor='bottom', y=-0.28,
    xanchor='center', x=0.5,
    bgcolor='rgba(0,0,0,0)',
    font=dict(size=10, color=C['muted']),
    tracegroupgap=0,
)

def _base(height=300):
    return dict(
        paper_bgcolor=C['bg'],
        plot_bgcolor=C['bg'],
        font=dict(color=C['text'], family='Source Sans 3, sans-serif', size=11),
        height=height,
        margin=dict(l=52, r=16, t=40, b=68),
        xaxis=dict(
            gridcolor=C['grid'], showgrid=True, zeroline=False,
            linecolor=C['border'], linewidth=1, showline=True,
            tickfont=dict(size=10, color=C['muted']),
            ticks='outside', ticklen=3, tickcolor=C['border'],
        ),
        yaxis=dict(
            gridcolor=C['grid'], showgrid=True, zeroline=False,
            linecolor=C['border'], linewidth=1, showline=False,
            tickfont=dict(size=10, color=C['muted']),
        ),
        legend=LEGEND,
    )

def _title(text):
    return dict(
        text=f'<b style="font-size:12px;color:{C["navy"]}">{text}</b>',
        x=0.0, xanchor='left',
        font=dict(family='Source Serif 4, serif', size=12, color=C['navy']),
        pad=dict(b=8)
    )

# ── 1. Import Volume vs Domestic Production ─────────────────────────────────────
def import_trend_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['import_volume_mt'],
        name='Import Volume (MT)',
        line=dict(color=C['teal'], width=2),
        fill='tozeroy',
        fillcolor='rgba(46,125,130,0.08)',
        mode='lines',
    ))
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['domestic_production_mt'],
        name='Domestic Production (MT)',
        line=dict(color=C['amber'], width=1.8, dash='dot'),
        mode='lines',
    ))
    fig.update_layout(**_base(), title=_title('Import Volume vs. Domestic Production'))
    return fig

# ── 2. Farmer Price vs Consumer Price ───────────────────────────────────────────
def price_trend_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['farmer_price_inr'],
        name='Farmer Gate Price (Rs/kg)',
        line=dict(color=C['amber'], width=2),
        mode='lines',
    ))
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['consumer_price_inr'],
        name='Consumer Retail Price (Rs/kg)',
        line=dict(color=C['red'], width=2),
        fill='tonexty',
        fillcolor='rgba(185,64,64,0.06)',
        mode='lines',
    ))
    layout = _base()
    layout['yaxis']['title'] = dict(text='Rs / kg', font=dict(size=10, color=C['muted']), standoff=8)
    fig.update_layout(**layout, title=_title('Farmer Gate Price vs. Consumer Retail Price'))
    return fig

# ── 3. Price Impact Bar Chart ───────────────────────────────────────────────────
def tariff_impact_bar(scenario_df):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=scenario_df['tariff_rate'],
        y=scenario_df['farmer_price_inr'],
        name='Farmer Gate Price (Rs/kg)',
        marker=dict(color=C['amber'], line=dict(width=0)),
    ))
    fig.add_trace(go.Bar(
        x=scenario_df['tariff_rate'],
        y=scenario_df['consumer_price_inr'],
        name='Consumer Retail Price (Rs/kg)',
        marker=dict(color=C['teal'], line=dict(width=0)),
    ))
    layout = _base()
    layout['margin']['b'] = 72
    fig.update_layout(
        **layout,
        title=_title('Price Impact by Tariff Scenario'),
        barmode='group',
        bargap=0.28,
        bargroupgap=0.06,
    )
    fig.update_xaxes(
        title_text='Customs Duty (%)',
        title_font=dict(size=10, color=C['muted']),
        title_standoff=10,
    )
    fig.update_yaxes(
        title_text='Price (Rs / kg)',
        title_font=dict(size=10, color=C['muted']),
        title_standoff=8,
    )
    return fig

# ── 4. Dependency — replaced by progress bar in app.py ─────────────────────────
#    Keeping a minimal version for gauge import compatibility
def dependency_gauge(import_dependency):
    # Simple horizontal bar indicator — no neon gauge
    bar_color = C['red'] if import_dependency > 88 else (C['amber'] if import_dependency > 75 else C['teal'])
    fig = go.Figure()
    # Background track
    fig.add_trace(go.Bar(
        x=[100], y=['Dependency'],
        orientation='h',
        marker=dict(color='#EBF0F5', line=dict(width=0)),
        showlegend=False, hoverinfo='skip',
    ))
    # Fill
    fig.add_trace(go.Bar(
        x=[import_dependency], y=['Dependency'],
        orientation='h',
        marker=dict(color=bar_color, line=dict(width=0)),
        text=[f"<b>{import_dependency:.1f}%</b>"],
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='white', size=14, family='Source Serif 4, serif'),
        showlegend=False,
    ))
    fig.update_layout(
        barmode='overlay',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=90,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(range=[0, 100], visible=False),
        yaxis=dict(visible=False),
    )
    return fig

# ── 5. Forward Forecast ─────────────────────────────────────────────────────────
def forecast_chart(forecast_df):
    fig = go.Figure()
    fig.add_shape(
        type='rect',
        x0=forecast_df['date'].min(), x1=forecast_df['date'].max(),
        y0=0, y1=forecast_df['import_volume_mt'].max() * 1.15,
        fillcolor='rgba(46,125,130,0.03)',
        line=dict(width=0),
    )
    fig.add_trace(go.Scatter(
        x=forecast_df['date'],
        y=forecast_df['import_volume_mt'],
        mode='lines',
        line=dict(color=C['teal'], width=2, dash='dash'),
        fill='tozeroy',
        fillcolor='rgba(46,125,130,0.07)',
        showlegend=False,
    ))
    layout = _base()
    layout['margin']['b'] = 36
    layout['yaxis']['title'] = dict(text='MT', font=dict(size=10, color=C['muted']), standoff=8)
    fig.update_layout(**layout, title=_title(f'Import Volume Forecast — Forward Projection'))

    # Add annotation instead of legend
    fig.add_annotation(
        x=forecast_df['date'].iloc[-1], y=forecast_df['import_volume_mt'].iloc[-1],
        text='Forecast', showarrow=False,
        font=dict(size=9, color=C['teal']),
        xanchor='right', yanchor='bottom',
    )
    return fig

# ── 6. Scenario Heatmap ─────────────────────────────────────────────────────────
def scenario_heatmap(scenario_df):
    metrics = ['import_volume_mt', 'farmer_price_inr', 'consumer_price_inr',
               'import_dependency_pct', 'cultivation_area_mha']
    labels  = ['Import Vol', 'Farmer Price', 'Consumer Price', 'Import Dep. %', 'Cultivation']
    z = scenario_df[metrics].values.T

    # Institutional colorscale: white → teal → navy
    colorscale = [
        [0.0,  '#FFFFFF'],
        [0.3,  '#C2DCE0'],
        [0.65, '#2E7D82'],
        [1.0,  '#1B2A4A'],
    ]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=[f"{t}%" for t in scenario_df['tariff_rate']],
        y=labels,
        colorscale=colorscale,
        text=z.round(2),
        texttemplate='%{text}',
        textfont=dict(size=10),
        showscale=True,
        colorbar=dict(
            thickness=10,
            outlinewidth=0,
            tickfont=dict(size=9, color=C['muted']),
            len=0.9,
        ),
    ))
    layout = _base(height=280)
    layout['margin']['r'] = 60
    layout['margin']['b'] = 28
    layout['legend']['visible'] = False
    fig.update_layout(**layout, title=_title('Scenario Impact Matrix'))
    return fig