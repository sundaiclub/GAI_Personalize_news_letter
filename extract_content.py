import requests
from bs4 import BeautifulSoup
import argparse
import sys

def clean_text(text):
    """
    Clean extracted text by removing extra whitespace and empty lines.
    """
    # Remove extra whitespace and empty lines
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    return '\n'.join(lines)

# TODO: this doesn't work for all websites, need to find a better way to extract the main content for dynamically loaded content
def extract_main_content(url):
    """
    Extract the main content from a given URL while filtering out advertisements
    and irrelevant content.
    
    Args:
        url (str): The URL of the webpage to extract content from
        
    Returns:
        tuple: (title, text) containing the article title and main content
    """
    try:
        # Fetch the webpage
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get the title
        title = soup.title.string if soup.title else ''
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 
                                    'iframe', 'aside', 'form', 'button']):
            element.decompose()
            
        # Try to find the main content
        main_content = None
        
        # Look for common content containers
        content_candidates = [
            soup.find('main'),
            soup.find('article'),
            soup.find('div', class_=['content', 'main-content', 'post-content', 'article-content']),
            soup.find(id=['content', 'main-content', 'post-content', 'article-content'])
        ]
        
        # Use the first valid content container found
        for candidate in content_candidates:
            if candidate:
                main_content = candidate
                break
        
        # If no specific content container found, use body as fallback
        if not main_content:
            main_content = soup.find('body')
        
        # Extract and clean text
        if main_content:
            content = clean_text(main_content.get_text())
        else:
            content = clean_text(soup.get_text())
        
        return title, content
    
    except Exception as e:
        print(f"Error processing URL: {str(e)}", file=sys.stderr)
        return None, None

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract main content from a webpage')
    parser.add_argument('url', help='URL of the webpage to extract content from')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    # Extract content
    title, content = extract_main_content(args.url)
    
    if title and content:
        # Prepare output
        output_text = f"Title: {title}\n\n{content}"
        
        # Write to file if output path is specified
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output_text)
                print(f"Content saved to {args.output}")
            except Exception as e:
                print(f"Error writing to file: {str(e)}", file=sys.stderr)
                print(output_text)
        else:
            # Print to console if no output file specified
            print(output_text)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
