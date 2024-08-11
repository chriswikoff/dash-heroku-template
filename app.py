import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

%%capture
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = '''
According to the [US Department of Labor](https://www.dol.gov/sites/dolgov/files/WB/equalpay/WB_issuebrief-undstg-wage-gap-v1.pdf), the gender wage gap refers to the fact that women, on average, are paid less than men. The gap between men and women is even wider when comparing white, non-hispanic men to women of color. These statistics are based on comparing men and women who work full-time, year-round jobs to account for differences in work hours. According to the [Pew Research Center](https://www.pewresearch.org/social-trends/2023/03/01/the-enduring-grip-of-the-gender-pay-gap/), women tend to begin their careers close to wage parity with men, but the gap increasingly widens as their careers progress. There are a number of factors leading to this gap, one of which that fathers are more likely to be a part of the labor force (and progress in income) than mothers are.

The [General Social Survey](https://gss.norc.org/about-the-gss) or GSS has been conducted since 1972 and gathers information about modern American society to track and analyze trends in opinions, attitudes, and behaviors. The data that is polled reveals the state of Americans across a number of variables, including socioeconomic status, sex, and income. According to [Wikipedia](https://en.wikipedia.org/wiki/General_Social_Survey), the GSS sample is taken from a random sample of voluntary participants that is intended to represent a wide spectrum of American individuals.
'''

gss_table = gss_clean.groupby('sex', sort=False).agg({'income':'mean',
                                    'job_prestige': 'mean',
                                     'socioeconomic_index':'mean',
                                    'education':'mean'})
gss_table = gss_table.reset_index()
gss_table = gss_table.rename({'sex':'Sex', 'income':'Mean Income', 'job_prestige': 'Mean Occupational Prestige',
                              'socioeconomic_index':'Mean Socioeconomic Index',
                           'education':'Mean Years of Education'}, axis=1) 
gss_table['Mean Income'] = round(gss_table['Mean Income'],2)
gss_table['Mean Occupational Prestige'] = round(gss_table['Mean Occupational Prestige'],2)
gss_table['Mean Socioeconomic Index'] = round(gss_table['Mean Socioeconomic Index'],2)
gss_table['Mean Years of Education'] = round(gss_table['Mean Years of Education'],2)
gss_table = gss_table.reset_index()

table = ff.create_table(gss_table)


gss_clean['male_breadwinner'] = gss_clean['male_breadwinner'].astype('category')
gss_clean['male_breadwinner'] = gss_clean['male_breadwinner'].cat.reorder_categories(['strongly agree',
                                                                       'agree',
                                                                       'disagree',
                                                                       'strongly disagree'])

gss_barplot = gss_clean.groupby(['sex', 'male_breadwinner']).size()
gss_barplot = gss_barplot.reset_index()
gss_barplot = gss_barplot.rename({0:'count'}, axis=1)

gss_barplot = gss_barplot.reset_index()
gss_barplot = gss_barplot.rename({'sex':'Sex', 'male_breadwinner':'Male Breadwinner Question Response'}, axis=1)

fig_bar = px.bar(gss_barplot, x='Male Breadwinner Question Response', y='count', color='Sex',
            labels={'Male Breadwinner Question':'Male Breadwinner Question Response',
                    'count':'Count'},
            hover_data = ['Sex', 'Male Breadwinner Question Response', 'count'],
            barmode = 'group')
fig_bar.update_layout(showlegend=True)

fig_scatter = px.scatter(gss_clean, x='job_prestige', y='income', 
                 color='sex', 
                 trendline='ols',
                 height=500, width=700,
                 hover_data=['education', 'socioeconomic_index'],
                 labels={
                     'job_prestige': 'Job Prestige',
                     'income': 'Income',
                     'sex': 'Sex'})

fig_box1 = px.box(gss_clean, x='sex', y = 'income', color = 'sex',
                   labels={'income':'Income', 'sex':''},)
fig_box1.update_layout(showlegend=False)

fig_box2 = px.box(gss_clean, x='sex', y = 'job_prestige', color = 'sex',
                   labels={'job_prestige':'Job Prestige', 'sex':''},)
fig_box2.update_layout(showlegend=False)

mycols = ['income','sex','job_prestige'] 
gss_new = gss_clean[mycols]
gss_new['Job Prestige Category'] = pd.cut(
    gss_new['job_prestige'], 
    bins=6, 
    labels=["1", "2", 
            "3", "4", 
            "5", "6"])
gss_new = gss_new.dropna()

fig_boxgrid = px.box(gss_new, x='sex', y='income', color='sex',
             facet_col='Job Prestige Category', 
             facet_col_wrap=3,
             color_discrete_map={'male': 'blue', 'female': 'red'},
             labels={'sex': 'Sex', 'income': 'Income'})
fig_boxgrid.update(layout=dict(title=dict(x=0.5)))
fig_boxgrid.update_layout(showlegend=False)

import pandas as pd
from dash import Dash, html, dcc
import plotly.express as px

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1("Exploring the Gender Wage Gap with GSS Data"),
        dcc.Markdown(children=markdown_text),
        html.H2("Comparing mean income, occupational prestige, socioeconomic index, and years of education by sex"),
        dcc.Graph(figure=table),
        
        html.H2("Responses to male_breadwinner Question by Sex"),
        dcc.Graph(figure=fig_bar),
        
        html.H2("Income vs. Job Prestige by Sex"),
        dcc.Graph(figure=fig_scatter),
        
        html.Div([
            html.H2("Income by Sex"),
            dcc.Graph(figure=fig_box1)
        ], style={'width': '48%', 'float': 'left'}),
        
        html.Div([
            html.H2("Job Prestige by Sex"),
            dcc.Graph(figure=fig_box2)
        ], style={'width': '48%', 'float': 'right'}),
        
        html.H2("Income by Sex Across Job Prestige Categories"),
        dcc.Graph(figure=fig_boxgrid),
    ]
)

app.run_server(debug=True, port=8051)
