
import PyPDF2
import urllib.parse as urlparse


def extract_article_url(url):    
    try:
        parsed = urlparse.urlparse(url)
        
        # If it's a Google Alert share URL
        if "google.com/alerts/share" in url:
            query_params = urlparse.parse_qs(parsed.query)
            if 'ru' in query_params:
                return query_params['ru'][0]
                
        # If it's a Google redirect URL
        elif "google.com/url" in url:
            query_params = urlparse.parse_qs(parsed.query)
            if 'url' in query_params:
                return query_params['url'][0]
                
        # If it's already a direct article URL (not Google-related)
        elif not any(x in url.lower() for x in [
            "google.com/alerts/edit",
            "google.com/alerts/feed",
            "google.com/alerts"
        ]):
            return url
            
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")
    
    return None


def extract_links_from_pdf(file_path):
    links = []
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                if '/Annots' in page:
                    annotations = page['/Annots']
                    if hasattr(annotations, "get_object"):
                        annotations = annotations.get_object()
                    
                    for annotation in annotations:
                        if hasattr(annotation, "get_object"):
                            annotation = annotation.get_object()
                        
                        if annotation.get('/Subtype', '') == '/Link':
                            if '/A' in annotation and '/URI' in annotation['/A']:
                                links.append(annotation['/A']['/URI'])
                
        return links
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return []
    
def filter_article_links(links):
    article_links = []
    
    for link in links:
        article_url = extract_article_url(link)
        if article_url:
            article_links.append(article_url)
    
    # Remove duplicates and write to file
    unique_articles = list(set(article_links))
            
    return unique_articles

def main():
    links = extract_links_from_pdf(r"data\Jan 31 Google Alert  Daily Digest.pdf")
    filtered = filter_article_links(links)
    print(len(filtered))
    return filtered

if __name__ == "__main__":
    main()
