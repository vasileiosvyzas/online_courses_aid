import streamlit as st

def display_search_results():
    # Define a list of search results
    search_results = [
        {
            'title': 'Result 1',
            'link': 'https://example.com/result1',
            'details': ['Detail 1', 'Detail 2', 'Detail 3']
        },
        {
            'title': 'Result 2',
            'link': 'https://example.com/result2',
            'details': ['Detail A', 'Detail B', 'Detail C']
        },
        {
            'title': 'Result 3',
            'link': 'https://example.com/result3',
            'details': ['Detail X', 'Detail Y', 'Detail Z']
        }
    ]

    # Display search results
    for result in search_results:
        st.write(f'[{result["title"]}](<{result["link"]}>)')

def display_details(details):
    # Display details in bullet point format
    st.write('### Details')
    st.markdown('- ' + '\n- '.join(details))

# Main page
st.title('Search Results')

# Display search results
display_search_results()

# Get user input for the selected link
selected_link = st.selectbox('Select a link', [result['title'] for result in search_results])

# Find the selected result based on the link title
selected_result = next(result for result in search_results if result['title'] == selected_link)

# Display details for the selected link
display_details(selected_result['details'])
