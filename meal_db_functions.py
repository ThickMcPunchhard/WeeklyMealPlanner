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
    
def add_recipe():
    """Add recipe to database"""
    def add_r_name():
        """Add to recipe table if not present"""
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
        new_r_id = int(last_ind_num[0][0])+1
        if not rec_check:
            rec_insert_qry = f"""INSERT INTO
                    recipes
                VALUES
                    ({new_r_id},
                    '{r_name_input}',
                    '{r_instr_input}');"""
            recipe_insert_record = cur.execute(rec_insert_qry)
            conn.commit()
        if rec_check:
            print("Recipe name already exists")
            
            
        rec_query_search = f"""SELECT
                    recipes.r_id
                FROM
                    recipes 
                WHERE
                    recipes.r_name = '{r_name_input}';"""
        rid_int = cur.execute(rec_query_search).fetchall()
        return rid_int
        
    def add_ingredients():
        """Create all needed ingr in ing table, uom in uom table, qty and rows for join table"""
        ing_lst_input = []
        ing_lst_ids = []  
        add_ing = 1
        while add_ing != '0':
            add_ing = input("Ingredient (Enter 0 to finish):")
            if add_ing != '0':
                add_uom = str(input("UOM:"))
                add_qty = float(input("QTY:"))            
                ing_lst_input.append((add_ing,add_uom,add_qty))
        
        def add_ing_name():
            """Add to ing table if not present"""
            list_names = list(zip(*ing_lst_input))[0]
            for item in list_names:
                item_0 =str(item)
                ing_search_qry = f"""SELECT
                        1
                    FROM
                        ingredients
                    WHERE
                        ingredients.i_name = '{item_0}';"""
                ing_check = cur.execute(ing_search_qry).fetchall()
                select_ind_num = """SELECT MAX(i_id)
                    FROM
                        ingredients"""
                last_ind_num = cur.execute(select_ind_num).fetchall()
                new_i_id = int(last_ind_num[0][0])+1
                if not ing_check:
                    ing_insert_qry = f"""INSERT INTO
                            ingredients
                        VALUES
                            ({new_i_id},
                            '{item}');"""
                    ing_insert_record = cur.execute(ing_insert_qry)
                    conn.commit()           
            
        def add_uom_name():
            """Add to uom table if not already present"""
            list_names = list(zip(*ing_lst_input))[1]
            for item in list_names:
                item_1 =str(item)
                uom_search_qry = f"""SELECT
                        1
                    FROM
                        uom
                    WHERE
                        uom.u_name = '{item_1}';"""
                uom_check = cur.execute(uom_search_qry).fetchall()
                select_ind_num = """SELECT MAX(u_id)
                    FROM
                        uom"""
                last_ind_num = cur.execute(select_ind_num).fetchall()
                new_u_id = int(last_ind_num[0][0])+1
                if not uom_check:
                    uom_insert_qry = f"""INSERT INTO
                            uom
                        VALUES
                            ({new_u_id},
                            '{item}');"""
                    uom_insert_record = cur.execute(uom_insert_qry)
                    conn.commit()
                    
        def return_ing_id():
            """Return list of all ing ids used"""
            iid_list = []
            for item in list(zip(*ing_lst_input))[0]:
                item_0 = str(item)
                query_search = f"""SELECT
                            ingredients.i_id
                       FROM
                            ingredients 
                        WHERE
                            ingredients.i_name = '{item_0}';"""
                search_iid = cur.execute(query_search).fetchall()
                iid_list.append(search_iid[0][0])
            return iid_list
            
        def return_uom_id():
            """Return list of all uom ids used"""
            uid_list = []
            for uom_item in list(zip(*ing_lst_input))[1]:
                item_1 = str(uom_item)
                query_search = f"""SELECT
                            uom.u_id
                       FROM
                            uom 
                        WHERE
                            uom.u_name = '{item_1}';"""
                search_uid = cur.execute(query_search).fetchall()
                uid_list.append(search_uid[0][0])
            return uid_list

        def return_qty():
            """Return list of all qtys used"""
            list_names = list(zip(*ing_lst_input))[2]
            return list_names
                    
        add_ing_name()        
        add_uom_name()
        print("ing_data input pre-zip")
        print(return_ing_id())
        print(return_uom_id())
        print(return_qty())

        ing_data = list(zip(return_ing_id(),return_uom_id(),return_qty()))
        return ing_data 
        
    def add_to_join(rid_int,ing_data):
        print(rid_int)
        print("ing_data input", ing_data)
        """Insert recipe into join table"""  
        select_j_ind_num = """SELECT MAX(j_id)
                        FROM
                            r_i_join"""
        last_j_ind_num = cur.execute(select_j_ind_num).fetchall()
        new_j_id = int(last_j_ind_num[0][0])
        j_data =[new_j_id]*int(len(list(ing_data)))
        r_data = [rid_int[0][0]]*int(len(list(ing_data)))
        join_new_list = []
        for i in list(ing_data):
            i = list(i)
            i.insert(0,rid_int[0][0])
            i.insert(0,new_j_id+1)
            new_j_id = new_j_id+1
            i = tuple(i)
            join_new_list.append(i)            
        print(join_new_list)
        j_insert_qry = f"""INSERT
                        INTO
                            r_i_join (j_id,r_id,i_id,u_id,qty)
                        VALUES
                            (?,?,?,?,?);"""
        cur.executemany(j_insert_qry,join_new_list)
        conn.commit()
    
    def add_validation():
        """Check tables to see if values were added"""
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

    add_to_join(add_r_name(),add_ingredients())
    add_validation()
    
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

def clear_all_meals():
    clear_meals_statement = """UPDATE dow SET r_id = NULL;"""
    conn.execute(clear_meals_statement)
    
def set_single_meal():
    ##Define meal
    ##Define DOW
    ##Define new recipe
    ##Find that record and update
    pass

def random_meal_plan():
    pass


#Complete 
########################
##print_toc()
##print_cookbook()
##add_recipe()
##search_cookbook()
##clear_all_meals()
##show_mealplan()

#WIP 
########################
set_single_meal()
random_meal_plan()
