import requests
import difflib


def fetch_data(api_url):
    """
    Fetches data from the specified API endpoint.

    Args:
        api_url (str): The URL of the API endpoint.

    Returns:
        list: A list of dictionaries containing the fetched data.
    """
    data = []
    page = 1
    while True:
        # Fetch data from the API for the current page
        response = requests.get(f"{api_url}?page={page}")
        if response.status_code != 200:
            break
        page_data = response.json()
        if page_data['status'] != 'success':
            break
        items = page_data['data']['data'] 
        if not items:
            break
        # Append fetched items to the data list
        data.extend(items)
        page += 1
        
    return data


def identify_citations(response, sources):
    """
    Identifies citations for a given response from a list of sources.

    Args:
        response (str): The response text.
        sources (list): A list of dictionaries representing sources, each containing 'id' and 'context' keys.

    Returns:
        list: A list of dictionaries representing citations for the response.
    """
    citations = []
    for source in sources:
        if response in source['context']:
            # If response text is found in source context, consider it a citation
            citations.append(source)
        else:
            # Use difflib to find similarities between response and source context
            sequence_matcher = difflib.SequenceMatcher(None, response, source['context'])
            if sequence_matcher.ratio() > 0.5:  
                # If similarity ratio is above threshold, consider it a citation
                citations.append(source)
    return citations


def process_data(api_url):
    """
    Processes data fetched from the API by identifying citations for each response.

    Args:
        api_url (str): The URL of the API endpoint.

    Returns:
        list: A list of dictionaries containing processed data with citations.
    """
    data = fetch_data(api_url)
    results = []
    for item in data:
        try:
            response = item['response']
            sources = item['source']  
            citations = identify_citations(response, sources)
            # Append processed result to results list
            results.append({
                "response": response,
                "citations": citations
            })
        except TypeError as e:
            print(f"Error processing item: {item}, error: {e}")
            continue
    return results


def display_results(results):
    """
    Displays the processed results with citations.

    Args:
        results (list): A list of dictionaries containing processed data with citations.
    """
    for result in results:
        print(f"Response: {result['response']}")
        print("Citations:")
        for citation in result['citations']:
            print(f"  ID: {citation['id']}")
            print(f"  Context: {citation['context']}")
            if citation['link']:
                print(f"  Link: {citation['link']}")
            print()
        print("-" * 80)


if __name__ == "__main__":
    api_url = "https://devapi.beyondchats.com/api/get_message_with_sources"
    results = process_data(api_url)
    display_results(results)
