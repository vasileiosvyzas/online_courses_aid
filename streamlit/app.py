import streamlit as st
import sys
from elasticsearch import Elasticsearch
import utils
import templates

INDEX = 'udemy_data'
DOMAIN = '0.0.0.0'
es = Elasticsearch(host=DOMAIN)
utils.check_and_create_index(es, INDEX)

def main():
    st.title('Search a Udemy course')
    search = st.text_input('Enter search words:')
    
    if search:
        results = utils.index_search(es, INDEX, search, None, 0, 5)
        print(results)
        total_hits = results['aggregations']['match_count']['value']
        
        # search results
        # for i in range(len(results['hits']['hits'])):
        #     result = results['hits']['hits'][i]
        #     res = result['_source']
        #     res['url'] = result['_id']
        #     res['highlights'] = '...'.join(result['highlight']['content'])
        #     st.write(templates.search_result(i, **res), unsafe_allow_html=True)

if __name__ == '__main__':
    main()