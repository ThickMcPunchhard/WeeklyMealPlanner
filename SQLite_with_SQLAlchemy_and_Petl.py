#import sqlalchemy
from sqlalchemy import select
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy import distinct, func
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy import ForeignKey
#from sqlalchemy.orm import Session
import petl as etl
import sqlite3
from collections import OrderedDict

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

etl.todb(recs,conn,'recipes')
etl.todb(ings,conn,'ingredients')
etl.todb(join_list,conn,'r_i_join')
etl.todb(uom_list,conn,'uom')

def print_toc():
    query_toc = """SELECT recipes.r_name as Recipe
    FROM recipes"""
    toc=etl.fromdb(conn,query_toc)
    print(toc)
def print_cookbook():
    query_cookbook = """SELECT    
        recipes.r_name AS Recipe,
        ingredients.i_name AS Ingredient,    
        recipes.r_instructions AS Instructions,
        uom.u_name AS UOM
    FROM
        ingredients
        INNER JOIN r_i_join ON r_i_join.i_id = ingredients.i_id
        INNER JOIN recipes ON recipes.r_id = r_i_join.r_id
        INNER JOIN uom ON uom.u_id = r_i_join.u_id;"""
    cook=etl.fromdb(conn,query_cookbook)
    print(cook)

cookbook_search = input('What recipe are you looking for: ')
query_search = f"""SELECT
    recipes.r_name AS Recipe,
    ingredients.i_name AS Ingredient,
    recipes.r_instructions AS Instructions,
    uom.u_name AS UOM
FROM
    ingredients
    INNER JOIN r_i_join ON r_i_join.i_id = ingredients.i_id
    INNER JOIN recipes ON recipes.r_id = r_i_join.r_id
    INNER JOIN uom ON uom.u_id = r_i_join.u_id
WHERE recipes.r_name LIKE '%{cookbook_search}%';"""

rec_search=etl.fromdb(conn,query_search)
print(rec_search)

aggregation = OrderedDict()
aggregation['inglist'] = 'Ingredient', list
#aggregation['recinst'] = 'Instruction', list
#aggregation['inguom'] = ('Ingredient', 'UOM'), list
agg_rec = etl.aggregate(rec_search,'Recipe',aggregation)
print(agg_rec)

grouping_by = etl.rowgroupby(rec_search,'Recipe','Ingredient')
for key,group in grouping_by:
    print(key, list(group))
