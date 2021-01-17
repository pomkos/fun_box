import streamlit as st
import sqlalchemy as sq
import datetime as dt
import string 
import random
import re
    
st.set_page_config(page_title='Suggestion Box', page_icon="📦")

def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))

class dbStuff():
    def __init__(self):
        '''
        Initialize the sqlite database
        '''
        # initialize engine
        engine = sq.create_engine(f'sqlite:///data/fun_box.db')
        cnx = engine.connect()
        meta = sq.MetaData()
        meta.reflect(bind=engine)
        
        self.cnx = cnx
        self.table = meta.tables['suggestions']

    def save_table(self, new_info):
        '''
        Saves information to database
        '''
        conn = self.cnx
        conn.execute(self.table.insert(), [new_info])

    def show_table(self):
        
        import pandas as pd
        table = self.table
        request = sq.select([table])
        resultset = self.cnx.execute(request).fetchall()
        df = pd.DataFrame(resultset)
        df.columns = resultset[0].keys()
        return df
    
def sanity_checker(description, category, url, date, rando_key):
    '''
    Checks for proper formatting of user inputs
    '''
    if rando_key in d.show_table()['rando_key']:
        st.error("No spamming the submit button please :)") # doesnt work cuz streamlit refreshes each time. Right idea tho.
        st.stop()
    if url: # make sure its a proper url
        if len(url) > 100:
            st.error("The URL is too long! Please shorten using bitly or something.")
            st.stop()
        if ('http' not in url) or (re.search('\s', url)):
            st.error("Wait a second, this isn't a proper uniform resource locator! [1](https://en.wikipedia.org/wiki/URL)")
            st.stop()
    if description: # limit descriptions to alphanumerical and 100 chars max
        if len(description) >100:
            st.error("That's too long! Please be more concise :)")
            st.stop()
        elif len(description) < 5:
            st.error("That's too short! Please be more descriptive :)")
            st.stop()
        result = all(c.isnumeric() or c.isalpha() or re.search('\s',c) or re.search('\.',c) or re.search('\,',c) for c in description)
        if result == False:
            st.error("Illegal characters detected. Please try again, and tell Russ that 1 hack = 2 trolls!")
            st.stop()
    else:
        st.error("Please write a brief description.")
        st.stop()
        
d = dbStuff()

### GUI ###
st.title("Suggestion Box!")
st.write("Pete is looking for a new data science project! What's something cool you would like to see an in-depth analysis of?")
st.write("The more challenging the better.")

with st.beta_expander("More info"):
    st.write("""Pete wants to analyze the heck out of something cool to include in his CV. Some of the stuff he's looking for:

1. A cognitive (multifaceted question) or coding (ex: scrape multiple sites to gather data) __challenge__
2. Good candidate for using __machine learning__ to predict things (ex: predict life expectancy based on various factors)
3. Topic that is __fun__ to study 🎉
    """)

colm, colt = st.beta_columns(2)

with colm:
    describe = st.text_input("Brief description*")
    
with colt:
    options = ['Leisure','Friends','Politics','Health/Fitness','Travel (US/World)','Covid','Finance']
    options.sort()
    options += ['Other']
    tag = st.selectbox("Category*", options=options, index = 2)

url = st.text_input("Website URL with more data (Optional)")

submit = st.button("Submit")
new_info = {
    'description':describe,
    'category':tag,
    'url':url,
    'date':dt.datetime.now(),
    'rando_key': random_char(7) # added to prevent spam, but doesnt work
}

success = st.empty()
table_area = st.empty() # take reserve empty space to update table
table_area.table(d.show_table().drop('rando_key',axis=1)) # drop random key col

### Spam Remover ###
# df = d.show_table()
# df = df.iloc[0:8,:]
# df.to_sql('suggestions',d.cnx, if_exists='replace',index=False)

if submit:
    sanity_checker(**new_info)
    try:
        d.save_table(new_info) # save info into db
        success.success('Thank you!!')
        table_area.table(d.show_table().drop('rando_key',axis=1)) # update the shown table
        st.balloons()
    except:
        st.error('Something bad happened, tell Pete quick!!')
