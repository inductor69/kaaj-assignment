from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class FloridaBusinessCrawler:
    BASE_URL = "https://search.sunbiz.org/Inquiry/CorporationSearch/ByName"
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox']
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.close()
        await self.playwright.stop()
    
    async def search_business(self, business_name: str) -> Optional[Dict]:
        page = None
        try:
            logger.info(f"Starting search for: {business_name}")
            page = await self.browser.new_page()
            
            # Navigate to search page
            await page.goto(self.BASE_URL)
            await page.fill("#SearchTerm", business_name)
            await page.click("input[value='Search Now']")
            
            # Wait for results table
            await page.wait_for_selector("table", timeout=30000)
            
            # Find active businesses
            results = []
            rows = await page.query_selector_all("table tbody tr")
            
            for row in rows:
                cells = await row.query_selector_all("td")
                if len(cells) < 3:
                    continue
                
                name = await cells[0].inner_text()
                status = await cells[2].inner_text()
                
                # Only process if status is Active and name closely matches search term
                if status.strip() == 'Active' and business_name.lower() in name.lower():
                    doc_number = await cells[1].inner_text()
                    detail_link = await cells[0].query_selector("a")
                    
                    if detail_link:
                        href = await detail_link.get_attribute("href")
                        if href:
                            detail_url = f"https://search.sunbiz.org{href}"
                            logger.info(f"Found active business: {name}")
                            
                            # Navigate to detail page
                            await page.goto(detail_url)
                            await page.wait_for_load_state('networkidle')
                            await page.wait_for_selector("div.detailSection", timeout=30000)
                            
                            # Extract details and filter for valid Business model fields
                            details = await self._extract_business_details(page)
                            if details:
                                # Only keep fields that are in the Business model
                                valid_fields = {
                                    'name': name,
                                    'status': status,
                                    'filing_date': details.get('filing_date'),
                                    'principals': details.get('principals', []),
                                    'registered_agent': details.get('registered_agent')
                                }
                                results.append(valid_fields)
                                break  # Stop after finding the first matching active business
            
            return results[0] if results else None
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            if page:
                await page.screenshot(path="/app/error.png")
            return None
        finally:
            if page:
                await page.close()
    
    async def _extract_business_details(self, page) -> Dict:
        try:
            await page.wait_for_selector("div.detailSection", timeout=30000)
            
            data = {
                "name": None,
                "status": None,
                "filing_date": None,
                "document_number": None,
                "fei_number": None,
                "state": None,
                "last_event": None,
                "last_event_date": None,
                "principal_address": None,
                "mailing_address": None,
                "registered_agent": {
                    "name": None,
                    "address": None,
                    "name_changed": None,
                    "address_changed": None
                },
                "principals": [],
                "annual_reports": [],
                "documents": []
            }
            
            # Get corporation name
            name_section = await page.query_selector("div.detailSection.corporationName p:last-child")
            if name_section:
                data["name"] = await self._get_text_direct(name_section)
            
            # Get filing information
            filing_info = await page.query_selector("div.filingInformation span div")
            if filing_info:
                data["document_number"] = await self._get_detail_text(filing_info, "Document Number")
                data["fei_number"] = await self._get_detail_text(filing_info, "FEI/EIN Number")
                data["filing_date"] = await self._get_detail_text(filing_info, "Date Filed")
                data["state"] = await self._get_detail_text(filing_info, "State")
                data["status"] = await self._get_detail_text(filing_info, "Status")
                data["last_event"] = await self._get_detail_text(filing_info, "Last Event")
                data["last_event_date"] = await self._get_detail_text(filing_info, "Event Date Filed")
            
            # Get principal address
            principal_section = await page.query_selector("div.detailSection:has(span:text('Principal Address'))")
            if principal_section:
                address_div = await principal_section.query_selector("div")
                if address_div:
                    data["principal_address"] = await self._get_text_direct(address_div)
            
            # Get mailing address
            mailing_section = await page.query_selector("div.detailSection:has(span:text('Mailing Address'))")
            if mailing_section:
                address_div = await mailing_section.query_selector("div")
                if address_div:
                    data["mailing_address"] = await self._get_text_direct(address_div)
            
            # Get registered agent
            agent_section = await page.query_selector("div.detailSection:has(span:text('Registered Agent Name'))")
            if agent_section:
                name_span = await agent_section.query_selector("span:nth-child(2)")
                address_div = await agent_section.query_selector("div")
                name_changed = await agent_section.query_selector("span:has-text('Name Changed:')")
                address_changed = await agent_section.query_selector("span:has-text('Address Changed:')")
                
                if name_span:
                    data["registered_agent"]["name"] = await self._get_text_direct(name_span)
                if address_div:
                    data["registered_agent"]["address"] = await self._get_text_direct(address_div)
                if name_changed:
                    data["registered_agent"]["name_changed"] = (await self._get_text_direct(name_changed)).replace("Name Changed: ", "")
                if address_changed:
                    data["registered_agent"]["address_changed"] = (await self._get_text_direct(address_changed)).replace("Address Changed: ", "")
            
            # Get officers/principals
            officer_section = await page.query_selector("div.detailSection:has(span:text('Officer/Director Detail'))")
            if officer_section:
                principals = []
                # Find all title elements
                title_elements = await officer_section.query_selector_all("span:has-text('Title')")
                
                for title_el in title_elements:
                    # Get the title text
                    title_text = await self._get_text_direct(title_el)
                    title = title_text.replace("Title", "").strip()
                    
                    # Find the name by looking for text after two <br> tags
                    name_element = await officer_section.evaluate("""(element, titleEl) => {
                        let br = titleEl.nextElementSibling;
                        if (br && br.nextElementSibling) {
                            br = br.nextElementSibling;
                            if (br.nextSibling && br.nextSibling.nodeType === 3) {
                                return br.nextSibling;
                            }
                        }
                        return null;
                    }""", title_el)
                    
                    if name_element:
                        name = await officer_section.evaluate("el => el.textContent", name_element)
                        
                        # Find the address div that follows
                        address_div = await officer_section.evaluate("""(element, titleEl) => {
                            let current = titleEl;
                            while (current) {
                                current = current.nextElementSibling;
                                if (current && current.tagName === 'DIV') {
                                    return current;
                                }
                            }
                            return null;
                        }""", title_el)
                        
                        address = None
                        if address_div:
                            address = await self._get_text_direct(address_div)
                        
                        principals.append({
                            "title": title,
                            "name": name.strip() if name else None,
                            "address": address
                        })
                
                data["principals"] = principals
            
            # Get annual reports
            report_section = await page.query_selector("div.detailSection:has(span:text('Annual Reports'))")
            if report_section:
                reports = []
                rows = await report_section.query_selector_all("table tr:not(:first-child)")
                for row in rows:
                    cells = await row.query_selector_all("td")
                    if len(cells) == 2:
                        year = await self._get_text_direct(cells[0])
                        date = await self._get_text_direct(cells[1])
                        reports.append({"year": year, "filed_date": date})
                data["annual_reports"] = reports
            
            # Get documents
            doc_section = await page.query_selector("div.detailSection:has(span:text('Document Images'))")
            if doc_section:
                documents = []
                rows = await doc_section.query_selector_all("table tr")
                for row in rows:
                    link = await row.query_selector("a")
                    if link:
                        doc_name = await self._get_text_direct(link)
                        doc_url = await link.get_attribute("href")
                        if doc_name and doc_url:
                            documents.append({
                                "name": doc_name,
                                "url": f"https://search.sunbiz.org{doc_url}"
                            })
                data["documents"] = documents
            
            logger.info(f"Extracted data: {data}")
            return data
            
        except Exception as e:
            logger.error(f"Error extracting details: {str(e)}")
            await page.screenshot(path="/app/detail_error.png")
            return None
    
    async def _get_detail_text(self, container, label: str) -> Optional[str]:
        try:
            selector = f"span:has-text('{label}:') + span"
            element = await container.wait_for_selector(selector, timeout=5000)
            if element:
                return (await element.inner_text()).strip()
        except Exception:
            return None
    
    async def _get_text_direct(self, element) -> Optional[str]:
        try:
            text = await element.inner_text()
            return text.strip()
        except Exception:
            return None
