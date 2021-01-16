import streamlit as st
import sqlalchemy as sq
import datetime as dt
    
st.set_page_config(page_title='Suggestion Box')

class dbStuff():
    def __init__(self):
        '''
        Initialize the sqlite database
        '''
        # initialize engine
        engine = sq.create_engine(f'sqlite:///data/box.db')
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
    
def sanity_checker(url: str, describe: str):
    '''
    Checks for proper formatting of user inputs
    '''
    if url:
        if 'https://' not in url:
            st.error("Wait a second, this isn't a proper uniform resource locator! [1](https://en.wikipedia.org/wiki/URL)")
            st.stop()
    if describe:
        if len(describe) >100:
            st.error("That's too long! Please be more concise :)")
            st.stop()
            
        result = all(c.isnumeric() or c.isalpha() for c in describe)
        if result == False:
            st.error("Illegal characters detected. Please try again, and tell Russ that 1 hack = 2 trolls!")
            st.stop()
            
        
d = dbStuff()

st.title("Suggestive  Box!")
st.write("Pete wants a new data science project. What's something cool you would like to see in-depth analysis of?")
st.write("The more complex the better.")

colm, colt = st.beta_columns(2)

with colm:
    describe = st.text_input("Brief description*")
    
with colt:
    options = ['Leisure','Friends','Politics','Health/Fitness','Travel (US/World)','Covid','Finance']
    options.sort()
    options += ['Other']
    tag = st.selectbox("Category*", options=options)

url = st.text_input("Website URL with more data (Optional)")
    
table_area = st.empty()
table_area.table(d.show_table())

submit = st.button("Submit")
new_info = {
    'description':describe,
    'category':tag,
    'url':url,
    'date':dt.datetime.now().date()
}


if submit:
    if url:
        sanity_checker(url, describe)
    else:
        sanity_checker(url=None, describe = describe)
        url = ''
    try:
        d.save_table(new_info)
        table_area.table(d.show_table())
        st.success('Thank you!!')
        st.balloons()
    except:
        st.error('Something bad happened, tell Pete quick!!')
