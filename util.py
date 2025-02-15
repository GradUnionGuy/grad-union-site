def make_dataframe(executed_query):
    import pandas as pd 
    df = pd.DataFrame(executed_query.fetchall())
    df.columns = ["col1", "col2", "col3"]
    return df