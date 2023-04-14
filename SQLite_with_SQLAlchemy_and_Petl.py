"""Create cookbook and meal plan generator"""
from collections import OrderedDict
import sqlite3

import pandas as pd
import petl
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy import ForeignKey

engine = create_engine('sqlite:///meals.db', echo=True)
conn = sqlite3.connect('meals.db')
meta = MetaData()

recipes = Table(
    'recipes', meta,
    Column('r_id', Integer, primary_key=True, autoincrement=True),
    Column('r_name', String),
    Column('r_instructions', String),)
ingredients = Table(
    'ingredients', meta,
    Column('i_id', Integer, primary_key=True, autoincrement=True),
    Column('i_name', String),)
uom = Table(
    'uom', meta,
    Column('u_id', Integer, primary_key=True, autoincrement=True),
    Column('u_name', String),)
r_i_join = Table(
    'r_i_join', meta,
    Column('j_id', Integer, primary_key=True, autoincrement=True),
    Column('i_id', Integer, ForeignKey('ingredients.i_id')),
    Column('r_id', Integer, ForeignKey('recipes.r_id')),
    Column('u_id', Integer, ForeignKey('uom.u_id')),
    Column('qty', Integer))
dow_tbl = Table(
    'dow',meta,
    Column('d_id', Integer, primary_key=True, autoincrement=True),
    Column('r_id', Integer, ForeignKey('recipes.r_id')),
    Column('dow',String(25)),
    Column('meal',String(25)))

meta.create_all(engine)

recs = [['r_name', 'r_instructions'],
        ['Cake', 'Bake.'],
        ['Pie', 'Fill!'],
        ['Coffee', 'Percolate.']]
ings = [['i_name'],
        ['Flour'],
        ['Milk'],
        ['Coffee']]
join_list = [['j_id','r_id','i_id','u_id','qty'],
        [1,1,1,3,5],
        [2,1,2,1,7],
        [3,1,3,1,1],
        [4,2,2,2,3],
        [5,2,3,3,5.5],
        [6,3,1,2,6]]
uom_list = [['u_name'],
            ['ea'],
            ['lbs'],
            ['gal']]
dow_list = [['d_id','r_id','dow','meal'],
            [1,1,'mon','Dinner'],
            [2,None,'tue','Dinner'],
            [3,2,'wed','Dinner'],
            [4,None,'thu','Dinner'],
            [5,None,'fri','Dinner'],
            [6,3,'sat','Dinner'],
            [7,2,'sun','Dinner'],
            [8,None,'mon','Lunch'],
            [9,1,'tue','Lunch'],
            [10,None,'wed','Lunch'],
            [11,3,'thu','Lunch'],
            [12,2,'fri','Lunch'],
            [13,None,'sat','Lunch'],
            [14,None,'sun','Lunch'],
            [15,1,'mon','Breakfast'],
            [16,3,'tue','Breakfast'],
            [17,2,'wed','Breakfast'],
            [18,2,'thu','Breakfast'],
            [19,3,'fri','Breakfast'],
            [20,1,'sat','Breakfast'],
            [21,3,'sun','Breakfast']]
    

petl.todb(recs,conn,'recipes')
petl.todb(ings,conn,'ingredients')
petl.todb(join_list,conn,'r_i_join')
petl.todb(uom_list,conn,'uom')
petl.todb(dow_list,conn,'dow')

def print_toc():
    """Print table of contents for cookbook"""
    query_toc = """SELECT recipes.r_name as Recipe
    FROM recipes"""
    toc_table=petl.fromdb(conn,query_toc)
    toc = petl.sort(toc_table, 'Recipe')
    print(toc)
def print_cookbook():
    """Print all recipes in cookbook"""
    query_cookbook = """SELECT
        recipes.r_name AS Recipe,
        ingredients.i_name AS Ingredient,        
        r_i_join.qty as QTY,
        uom.u_name AS UOM,
        recipes.r_instructions AS Instructions        
    FROM
        ingredients
        INNER JOIN r_i_join ON r_i_join.i_id = ingredients.i_id
        INNER JOIN recipes ON recipes.r_id = r_i_join.r_id
        INNER JOIN uom ON uom.u_id = r_i_join.u_id;"""
    table_cook=petl.fromdb(conn,query_cookbook)    
    cook = petl.sort(table_cook, key=['Recipe', 'Ingredient'])
    print(cook)
def search_cookbook(): #still needs better way to parse out recipes
    """Print recipes matching search input"""
    cookbook_search = input('What recipe are you looking for: ')
    query_search = f"""SELECT
        recipes.r_name AS Recipe,
        ingredients.i_name AS Ingredient,        
        r_i_join.qty as QTY,
        uom.u_name AS UOM,
        recipes.r_instructions AS Instructions
    FROM
        ingredients
        INNER JOIN r_i_join ON r_i_join.i_id = ingredients.i_id
        INNER JOIN recipes ON recipes.r_id = r_i_join.r_id
        INNER JOIN uom ON uom.u_id = r_i_join.u_id
    WHERE recipes.r_name LIKE '%{cookbook_search}%';"""
    rec_search=petl.fromdb(conn,query_search)
    search_sorted = petl.sort(rec_search, key=['Recipe','Ingredient'])
    table2 = petl.addfield(search_sorted, 'Ing', lambda rec: (rec['Ingredient'], rec['QTY'], rec['UOM']))
    print(table2)
def show_mealplan():
    """Print out the week's meal plan"""
    dinnerplan_qry = """SELECT
        dow.dow AS DOW,
        recipes.r_name AS Dinner         
    FROM
        dow
        LEFT JOIN recipes ON recipes.r_id = dow.r_id
    WHERE dow.meal =='Dinner';"""
    lunchplan_qry = """SELECT
        dow.dow AS DOW,
        recipes.r_name AS Lunch
    FROM
        dow
        LEFT JOIN recipes ON recipes.r_id = dow.r_id
    WHERE dow.meal =='Lunch';"""
    breakfastplan_qry = """SELECT
        dow.dow AS DOW,
        recipes.r_name AS Breakfast
    FROM
        dow
        LEFT JOIN recipes ON recipes.r_id = dow.r_id
    WHERE dow.meal =='Breakfast';"""
    dinner_plan = petl.fromdb(conn,dinnerplan_qry)
    lunch_plan = petl.fromdb(conn,lunchplan_qry)
    breakfast_plan = petl.fromdb(conn,breakfastplan_qry)
    meal_plan = petl.join(breakfast_plan,lunch_plan,key='DOW')
    meal_plan = petl.join(breakfast_plan,lunch_plan,key='DOW')
    weekly_plan = petl.join(meal_plan,dinner_plan,key='DOW') 
    panda_week = petl.todataframe(weekly_plan)
    cats = ['mon',
            'tue',
            'wed',
            'thu',
            'fri',
            'sat',
            'sun']
    panda_week['DOW'] = pd.Categorical(panda_week['DOW'],categories=cats, ordered=True)
    panda_week = panda_week.sort_values('DOW')
    print(panda_week)
    
#print_toc()
#print_cookbook()
#search_cookbook()
show_mealplan()
