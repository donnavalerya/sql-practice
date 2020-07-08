#!/usr/bin/env python
# coding: utf-8

# ## Import Packages and create db connection

# Things to do to practice.
# 
# (i) Display the names of the tables in the database.
# 
# (ii) Display the names of the columns in the table Master. 
# 
# (iii) Display the number of rows in the table Master.
# 
# (iv) Display the nameFirst and nameLast for players whose weight is greater than 280. 

# In[1]:


import sqlite3
import pandas as pd
import numpy as np
import seaborn as sb


# In[2]:


from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None


# In[3]:


database = "/Users/dbenit/sql-practice/lahman2016.db"  # Update this to where the directory of your lahman2016.db file
 
# create a database connection
conn = create_connection(database)
cursor = conn.cursor()


# In[4]:


#i display table names
for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';"):
    print(row)


# In[5]:


#i
cursor.execute("SELECT * FROM Master")
columns = cursor.description
for col in columns:
    print(col[0])


# In[6]:


#iii
cursor.execute("SELECT COUNT(*) from Master")
print ("The number of rows in the Master table are:",cursor.fetchall()[0])


# In[7]:


#iv
cursor.execute("SELECT nameFIRST, nameLAST FROM Master WHERE weight>280 ")
cursor.fetchall()


# ## More practice

# (i) Group players in the Master table with the same birthyear, and report the birthyear, the average height, and the number of players for each birthyear. Order the results by birthyear ascending. Save the results into a Pandas DataFrame. 
# 
# (ii) Plot the results in (i) using a lineplot with the average height on the y axis and year on the x-axis. 
# 
# 
# (iii) Do the same as in (i), but now only include groups with an average height > 70. 
# 
# (iv) Plot the results as in Part (ii)

# In[8]:


#i
master = pd.read_sql_query("SELECT birthYear,avg(height), COUNT(*)FROM Master GROUP BY birthYear", conn)
master.fillna(0)


# In[9]:


#iv
sb.lineplot(master['birthYear'],master["avg(height)"])


# In[10]:


#iii
master_htgt70 = pd.read_sql_query("SELECT birthYear,avg(height), COUNT(*)FROM Master GROUP BY birthYear HAVING avg(height) > 70", conn)


# In[11]:


master_htgt70


# In[12]:


#iv
sb.lineplot(master_htgt70['birthYear'],master_htgt70["avg(height)"])


# ## Part III

# (i) Find the namefirst, namelast, playerid and yearid of all players who were successfully inducted into the Hall of Fame in descending order of yearid. Save the results into a Pandas DataFrame.
# 
# (ii) Display the first 10 rows of the dataframe in (i). 
# 
# (iii) Display the total number of rows of the dataframe in (i).
# 
# 
# (iv) Find the people who were successfully inducted into the Hall of Fame and played in college at a school located in the state of California. For each person, return their namefirst, namelast, playerid, school name (name_full), and yearid in descending order of yearid. Break ties on yearid by school name (ascending). yearid refers to the year of induction into the Hall of Fame. Save the results in a dataframe and display the entire dataframe. 

# In[13]:


#i 
result = pd.read_sql_query("SELECT M.nameFirst, M.nameLast, H.playerID, H.yearID FROM Master as M, HallofFame as H WHERE H.inducted = 'Y' and M.playerID=H.playerID ORDER BY H.yearID DESC", conn )


# In[14]:


#ii
result.head(10)


# In[15]:


#iii
result


# In[16]:


print("The number of rows in the dataframe: ", result.shape[0])


# In[17]:


#iv
result_distinct = pd.read_sql_query("select distinct M.nameFirst,M.nameLast, H.playerID, S.name_full, H.yearID from CollegePlaying C inner join Schools S on C.schoolID = S.schoolID inner join Master M on M.playerID = C.playerID inner join HallofFame H on M.playerID = H.playerID where H.inducted ='Y' and S.state = 'CA' order by H.yearID desc, S.name_full",conn)


# In[18]:


result_distinct


# In[19]:


result_nonDistinct = pd.read_sql_query("select M.nameFirst,M.nameLast, H.playerID, S.name_full, H.yearID from CollegePlaying C inner join Schools S on C.schoolID = S.schoolID inner join Master M on M.playerID = C.playerID inner join HallofFame H on M.playerID = H.playerID where H.inducted ='Y' and S.state = 'CA' order by H.yearID desc, S.name_full",conn)
result_nonDistinct


# ## Part IV

# Find the namefirst, namelast, playerid, yearid, and single-year slg (Slugging Percentage) of the players and save the results in a dataframe. For statistical significance, only include players with more than 50 at-bats in the season. Order the results by slg descending. 
# 
# Display the players with the 10 best annual Slugging Percentage recorded over all time. 
# 
# Slugging Percentage is not provided in the database. It can be computed using a formula given at https://en.wikipedia.org/wiki/Slugging_percentage and the data in the database. Note that there is one term in the formula that is not directly available as a column in the database. You will have to compute it using some of the columns. 
# 
# Also, you have to compute slg as a floating point number, so make sure to use SQL in a way to get this. 

# In[20]:


#number of singles = total hits - sum of doubles, triples and home runs
slg = pd.read_sql_query("select M.playerID, M.nameFirst ,M.nameLast, B.yearID,  ((cast ((B.H-(B.'2B'+B.'3B'+B.HR)) as float) + cast (2*B.'2B' as float) + cast(3*B.'3B' as float) + cast(4*B.HR as float))/ cast(B.AB as float)) as 'slg' from Master as M inner join Batting as B on M.playerID = B.playerID where B.AB > 50 order by slg desc",conn)
slg.head(10)


# ## Part V

# (i) Find the yearid, min, max, and average of all player salaries for each year recorded, ordered by yearid in ascending order. Save the results as a dataframe and display it. 
# 
# (ii) For the player salaries in 2016, display a histogram with 10 bins. You may use the dataframe.hist(bin=10) function to do this. Also, it may be nicer to divide the salaries by 1,000,000 to show the amounts in millions. 

# In[21]:


#i
salaries = pd.read_sql_query("select min(S.salary) as 'Minimum Salary', max(S.salary) as 'Maximum Salary', avg(S.salary) as 'Avg Salary', S.yearID from Salaries as S group by S.yearID order by S.yearID",conn)
salaries


# In[22]:


#ii
sal = pd.read_sql_query('select salary/1000000 from Salaries where yearID = "2016"',conn)
sal.hist(bins=10)


# ## Part VI

# Extract and display a facet of the dataset that you think is interesting. This should not be a facet from Parts I-V. 

# In[23]:


#displaying the players in descending order of the number of awards they have won
pd.read_sql_query("select  A.playerID, M.nameFirst, M.nameLast, count(A.awardID) as 'TotalAwards' from Awardsplayers as A inner join Master as M on A.playerID = M.playerID group by A.playerID order by TotalAwards desc", conn)


# In[ ]:




