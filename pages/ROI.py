import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc
import dash_ag_grid as dag

dash.register_page(__name__, path = "/returnoninvestment")

superstore = pd.read_csv("data/Sample - Superstore.csv", encoding = "latin1")

superstore['Order Date'] = pd.to_datetime(superstore['Order Date'], format = "%m/%d/%Y")

# Sales by Category pie chart

categorysales = superstore.groupby('Category')['Sales'].sum().reset_index()

categorysalesdistribution = px.pie(categorysales, names = "Category", values = "Sales", hole = 0.7, color_discrete_sequence = px.colors.qualitative.Dark24_r)

categorysalesdistribution.update_layout(paper_bgcolor = "rgba(0, 0, 0, 0)", legend_font_color = "white")

totalsales = '${:,}'.format(round(categorysales['Sales'].sum(), 2))

categorysalesdistribution.add_annotation(text = "Total Sales by Category", showarrow = False, font = dict(color = "white", size = 14), y = 0.55)
categorysalesdistribution.add_annotation(text = totalsales, showarrow = False, font = dict(color = "white", size = 14), y = 0.45)


# Sales by Segment pie chart

segmentsales = superstore.groupby('Segment')['Sales'].sum().reset_index()

segmentsalesdistribution = px.pie(segmentsales, names = "Segment", values = "Sales", hole = 0.7, color_discrete_sequence = px.colors.qualitative.Dark24_r)

segmentsalesdistribution.update_layout(paper_bgcolor = "rgba(0, 0, 0, 0)", legend_font_color = "white")

segmentsalesdistribution.add_annotation(text = "Total Sales by Segment", showarrow = False, font = dict(color = "white", size = 14), y = 0.55)
segmentsalesdistribution.add_annotation(text = totalsales, showarrow = False, font = dict(color = "white", size = 14), y = 0.45)


# Segment Category sales sunburst

segmentcategorysales = superstore.groupby(['Segment', 'Category', 'Sub-Category'])['Sales'].sum().reset_index()

segmentcategorysalesdistribution = px.sunburst(segmentcategorysales, path = ['Segment', 'Category', 'Sub-Category'], values= "Sales", color_discrete_sequence = px.colors.qualitative.Dark24_r)

segmentcategorysalesdistribution.update_layout(title = "Categories and Sub-Categories Sales by Segment",
                                              title_font_color = 'White',
                                              paper_bgcolor = 'rgba(0,0,0,0)')

segmentcategorysalesdistribution.update_traces(marker_colors = px.colors.qualitative.Dark24_r)


# Top 5 customers by profit timeseries

totalprofitbycustomer = superstore.groupby(['Customer Name', 'Order Date'])['Profit'].sum().reset_index()

totalprofitbycustomer = totalprofitbycustomer.groupby('Customer Name')['Profit'].sum().reset_index()

totalprofitbycustomer_top5 = totalprofitbycustomer.nlargest(5, 'Profit')['Customer Name']

filtered_top5 = superstore[superstore['Customer Name'].isin(totalprofitbycustomer_top5)]

totalprofitovertime_top5 = filtered_top5.groupby(['Customer Name', filtered_top5['Order Date'].dt.year])['Profit'].sum().reset_index()

totalprofitovertime_top5_distribution = px.area(totalprofitovertime_top5, x = "Order Date", y = "Profit", color = "Customer Name", title = "Profits by top 5 customers over years")

totalprofitovertime_top5_distribution.update_layout(paper_bgcolor = "rgba(0, 0, 0, 0)", plot_bgcolor = "rgba(0, 0, 0, 0)", title_font_color = "white", legend_font_color = "white",
                                            xaxis_tickfont_color = 'White', xaxis_title = "", yaxis_title = "", yaxis_showticklabels = False)

totalprofitovertime_top5_distribution.update_yaxes(showgrid = False, zeroline = False)

totalprofitovertime_top5_distribution.update_xaxes(showgrid = False)

# Profit vs sales vs quantity

salesquantityprofit = superstore.groupby(pd.Grouper(key="Order Date", freq = "YE")).agg(
    {"Sales" : "sum", "Quantity" : "sum", "Profit" : "sum"}
).reset_index()

salesquantityprofitdistribution = go.Figure()

salesquantityprofitdistribution.add_trace(go.Scatter(x = salesquantityprofit['Order Date'], y = salesquantityprofit['Quantity'], mode = "lines", name = "Quantity"))
salesquantityprofitdistribution.add_trace(go.Scatter(x = salesquantityprofit['Order Date'], y = salesquantityprofit['Sales'], mode = "lines", name = "Sales"))
salesquantityprofitdistribution.add_trace(go.Scatter(x = salesquantityprofit['Order Date'], y = salesquantityprofit['Profit'], mode = "lines", name = "Profit"))

salesquantityprofitdistribution.update_layout(title = "Profit vs Sales vs Quantity", paper_bgcolor = "rgba(0, 0, 0, 0)", plot_bgcolor = "rgba(0, 0, 0, 0)", title_font_color = "white", legend_font_color = "white",
                                            xaxis_tickfont_color = 'White', xaxis_title = "", yaxis_title = "", yaxis_showticklabels = False)

salesquantityprofitdistribution.update_yaxes(showgrid = False, zeroline = False)

salesquantityprofitdistribution.update_xaxes(showgrid = False)

# Profit vs sales vs quantity by segment

categorysalesquantity = superstore.groupby('Segment').agg({
    "Sales" : "sum",
    "Quantity" : "sum",
    "Profit" : "sum"
}).reset_index()

categorysalesquantitydistribution = px.scatter(categorysalesquantity, x = "Quantity", y = "Sales", color = "Segment", size = "Profit", title = "Segment Sales vs Quantity vs Profit")

categorysalesquantitydistribution.update_layout(paper_bgcolor = "rgba(0, 0, 0, 0)", plot_bgcolor = "rgba(0, 0, 0, 0)", title_font_color = "white", legend_font_color = "white",
                                            xaxis_tickfont_color = 'White', yaxis_tickfont_color = 'White', yaxis_titlefont_color = "white", xaxis_titlefont_color = "white")

categorysalesquantitydistribution.update_yaxes(showgrid = False, zeroline = False)

categorysalesquantitydistribution.update_xaxes(showgrid = False)

# Products table

columnDefs = [
    { 'field': 'Product ID'},
    { 'field': 'Product Name', 'filter': True},
    { 'field': 'Category', 'filter': True},
    { 'field': 'Sub-Category', 'filter': True},
]

productstable = dag.AgGrid(
    id="get-started-example-basic",
    rowData=superstore.to_dict("records"),
    columnDefs=columnDefs,
    dashGridOptions = {
        "pagination" : True
    },
    className = "ag-theme-alpine-dark"
)

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(figure = categorysalesdistribution, responsive = True)
                ),
                dbc.Col(
                    dcc.Graph(figure = segmentsalesdistribution, responsive = True)
                ),
                dbc.Col(
                    dcc.Graph(figure = segmentcategorysalesdistribution, responsive = True)
                ),        
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(figure = totalprofitovertime_top5_distribution, responsive = True),
                ),
                dbc.Col(
                    dcc.Graph(figure = salesquantityprofitdistribution, responsive = True)
                )     
            ]
        ),
        dbc.Row(
            dcc.Graph(figure = categorysalesquantitydistribution)
        ),
        dbc.Row(
            productstable
        ),
    ],
    fluid = True,
)