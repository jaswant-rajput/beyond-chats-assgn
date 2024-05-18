import requests
import difflib


def fetch_data(api_url):
    data = []
    page = 1
    while True:

        response = requests.get(f"{api_url}?page={page}")
        if response.status_code != 200:
            break
        page_data = response.json()
        if page_data['status'] != 'success':
            break
        items = page_data['data']['data'] 
        if not items:
            break
        data.extend(items)
        page += 1
        if page == 1:
          break
        
    return data

def identify_citations(response, sources):
    citations = []
    for source in sources:
        if response in source['context']:
            citations.append(source)
        else:
            sequence_matcher = difflib.SequenceMatcher(None, response, source['context'])
            if sequence_matcher.ratio() > 0.5:  
                citations.append(source)
    return citations

def process_data(api_url):
    data = fetch_data(api_url)
    
    
    
    results = []
    for item in data:
        try:
            response = item['response']
            sources = item['source']  
            citations = identify_citations(response, sources)
            results.append({
                "response": response,
                "citations": citations
            })
        except TypeError as e:
            print(f"Error processing item: {item}, error: {e}")
            continue
    return results


def display_results(results):
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