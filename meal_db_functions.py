"""Create cookbook and meal plan generator"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('meals.db')
cur = conn.cursor()

def print_recipe(rec_id):
    """Print recipes"""
    query1 = f"""SELECT
            recipes.r_name AS Recipe,
            recipes.r_instructions AS Instructions
        FROM
            recipes
        WHERE recipes.r_id == {rec_id}"""
    cookbook_table = pd.read_sql(query1,conn)
    for ind in cookbook_table.index: 
        rname = cookbook_table['Recipe'][ind]
        print(rname)
        print('-----------------------------')
        access_sql =f"""SELECT         
            ingredients.i_name AS Ingredient,
            r_i_join.qty AS QTY,            
            uom.u_name AS UOM
        FROM ingredients
            INNER JOIN (
                recipes
            INNER JOIN (
                uom
            INNER JOIN
                [r_i_join]
                    ON uom.u_id = r_i_join.u_id)
                    ON recipes.r_id = r_i_join.r_id)
                    ON ingredients.i_id = r_i_join.i_id
        WHERE (((r_i_join.r_id)={rec_id}));"""
        subquery_1 = pd.read_sql(access_sql,conn)
        for rec in subquery_1.index:
            ing_name = subquery_1['Ingredient'][rec]
            qty_amt = subquery_1['QTY'][rec]
            uom_name = subquery_1['UOM'][rec]
            print(ing_name,",",qty_amt,uom_name)            
        print()
        print(cookbook_table['Instructions'][ind])
        print()

def print_toc():
    """Print table of contents for cookbook"""
    query_toc = """SELECT recipes.r_name as Recipe
    FROM recipes"""
    toc_table=pd.read_sql(query_toc,conn)
    toc = []
    for rec in toc_table['Recipe']:
        toc.append(rec)
    for item in sorted(toc):
        print(item)
    
def print_cookbook():
    """Print all recipes in cookbook"""    
    query1 = """SELECT
            recipes.r_id,
            recipes.r_name AS Recipe,
            recipes.r_instructions AS Instructions
        FROM
            recipes"""
    cookbook_table = pd.read_sql(query1,conn)    
    for ind in cookbook_table.index:
        rid = cookbook_table['r_id'][ind]
        print_recipe(rid)

def search_cookbook(): 
    """Print recipes matching search input"""
    cookbook_search = input('What recipe are you looking for: ')
    query_search = f"""SELECT
        recipes.r_name AS Recipe,
        recipes.r_id
    FROM
        recipes 
    WHERE recipes.r_name LIKE '%{cookbook_search}%';"""
    search_rec = pd.read_sql(query_search,conn)
    for ind in search_rec.index:
        rid = search_rec['r_id'][ind]
        print_recipe(rid)
        
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
    dinner_plan = pd.read_sql(dinnerplan_qry,conn) 
    lunch_plan = pd.read_sql(lunchplan_qry,conn)    
    breakfast_plan = pd.read_sql(breakfastplan_qry,conn)

    half_plan = breakfast_plan.merge(lunch_plan, on='DOW')
    full_plan = half_plan.merge(dinner_plan,on='DOW')
    cats = ['mon',
            'tue',
            'wed',
            'thu',
            'fri',
            'sat',
            'sun']
    full_plan['DOW'] = pd.Categorical(full_plan['DOW'],categories=cats, ordered=True)
    full_plan = full_plan.sort_values('DOW')
    print(full_plan)
    
def add_recipe():
    """Add recipe to database"""
    #insert recipe name + instructions
    ########################################################
    r_name_input = str(input('Recipe name:'))
    r_instr_input = str(input('Instructions:'))
    rec_check = cur.execute(f"""SELECT
            1
        FROM
            recipes
        WHERE
            recipes.r_name = '{r_name_input}';""").fetchall()
    select_ind_num = """SELECT MAX(r_id)
        FROM
            recipes"""
    last_ind_num = cur.execute(select_ind_num).fetchall()
    new_ind = int(last_ind_num[0][0])+1
    if not rec_check:
        rec_insert_qry = f"""INSERT INTO
                recipes
            VALUES
                ({new_ind},
                '{r_name_input}',
                '{r_instr_input}');"""
        recipe_insert_record = cur.execute(rec_insert_qry)
        conn.commit()
    if rec_check:
        print("Recipe already exists")
        
    #insert ingredients
    ####################################################
##    ing_lst_input = []
        #make list of ings to insert
        #check if ing name already exists
    
##    ing_insert_qry = f"""INSERT INTO ingredients
##            VALUES '{ing_lst_input}';"""
    
    #insert uoms
    ######################################################
##    uoms = []
        #check if uom exists
        #if not exist, then insert    
##    uom_insert_qry = f"""INSERT INTO uom
##            VALUES '{uoms}';"""
    
    #match all the insertion records to their IDs with QTY
    #######################################################
    
    #insert those IDs and QTY into the join table
    #######################################################

    #DONE-validation
    ######################################################
    strng_rec = """SELECT * from recipes"""
    strng_ing = """SELECT * from ingredients"""
    strng_uom = """SELECT * from uom"""
    strng_r_i_join = """SELECT * from r_i_join"""
    tablecheck_1 = pd.read_sql(strng_rec,conn)
    tablecheck_2 = pd.read_sql(strng_ing,conn)
    tablecheck_3 = pd.read_sql(strng_uom,conn)
    tablecheck_4 = pd.read_sql(strng_r_i_join,conn)
    print(tablecheck_1)
    print(tablecheck_2)
    print(tablecheck_3)
    print(tablecheck_4)
    
def change_meal():
    pass

#WIP 
########################
add_recipe()
change_meal()
##print_toc()
##print_cookbook()
##search_cookbook()
##show_mealplan()
