import requests
import json
import csv
import os
from datetime import datetime
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def scrape_page(self, url: str, selectors: dict = None) -> dict:
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = {'url': url, 'status_code': resp.status_code}
            
            if selectors:
                for name, selector in selectors.items():
                    try:
                        elements = soup.select(selector)
                        if elements:
                            results[name] = [elem.get_text(strip=True) for elem in elements]
                        else:
                            results[name] = []
                    except Exception as e:
                        results[name] = f"Error: {str(e)}"
            else:
                results['title'] = soup.title.string if soup.title else None
                results['headings'] = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
                results['links'] = [a['href'] for a in soup.find_all('a', href=True)]
            
            return results
        
        except Exception as e:
            return {'url': url, 'error': str(e)}
    
    def scrape_multiple_pages(self, urls: list, selectors: dict = None) -> list:
        results = []
        for url in urls:
            print(f"Scraping: {url}")
            result = self.scrape_page(url, selectors)
            results.append(result)
        return results
    
    def scrape_products(self, url: str) -> list:
        try:
            resp = self.session.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            products = []
            
            for item in soup.select('div.product-item, div.item, div.card, article.product'):
                product = {}
                
                title_elem = item.select_one('h2, h3, .product-title, .title')
                if title_elem:
                    product['title'] = title_elem.get_text(strip=True)
                
                price_elem = item.select_one('.price, .product-price, span.price')
                if price_elem:
                    product['price'] = price_elem.get_text(strip=True)
                
                link_elem = item.select_one('a')
                if link_elem and 'href' in link_elem.attrs:
                    product['link'] = link_elem['href']
                    if not product['link'].startswith('http'):
                        product['link'] = requests.compat.urljoin(url, product['link'])
                
                image_elem = item.select_one('img')
                if image_elem and 'src' in image_elem.attrs:
                    product['image'] = image_elem['src']
                
                if product:
                    products.append(product)
            
            return products
        
        except Exception as e:
            return [{'error': str(e)}]
    
    def save_to_csv(self, data: list, filename: str):
        if not data:
            print("No data to save")
            return
        
        headers = list(data[0].keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Data saved to {filename}")
    
    def save_to_json(self, data: list, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to {filename}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Web Scraper Tool')
    parser.add_argument('url', help='Target URL')
    parser.add_argument('--output', help='Output file (csv or json)')
    parser.add_argument('--action', choices=['page', 'products', 'list'], default='page')
    parser.add_argument('--urls', help='File with list of URLs')
    
    args = parser.parse_args()
    
    scraper = WebScraper()
    
    if args.action == 'page':
        result = scraper.scrape_page(args.url)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.action == 'products':
        products = scraper.scrape_products(args.url)
        print(f"Found {len(products)} products")
        
        if args.output:
            if args.output.endswith('.csv'):
                scraper.save_to_csv(products, args.output)
            else:
                scraper.save_to_json(products, args.output)
    
    elif args.action == 'list' and args.urls:
        with open(args.urls, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        results = scraper.scrape_multiple_pages(urls)
        
        if args.output:
            if args.output.endswith('.csv'):
                scraper.save_to_csv(results, args.output)
            else:
                scraper.save_to_json(results, args.output)
    
    else:
        print("Invalid action or missing arguments")

if __name__ == '__main__':
    main()