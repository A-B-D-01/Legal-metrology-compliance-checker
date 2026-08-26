# MetaMark Software-Only QA Test Checklist

## 1. Input Validation & Edge Cases
- [ ] **Empty Input:** Submit forms with missing required fields (empty image, empty URL). Confirm graceful 400 response.
- [ ] **Invalid/Malformed Input:** Pass invalid URLs or corrupted files to `/api/scrape` and `/api/seller/check-upload-text`.
- [ ] **Oversized Input:** Upload image files exceeding size limits. Confirm client/server rejection message.
- [ ] **Messy Human Inputs:** Test manual weight/dimension fields with messy formats (e.g., `250g`, `0.25 kg`, `15x10x5cm`). Confirm normalizer handles without crashing.

## 2. API & Infrastructure Resilience
- [ ] **Backend API Failure:** Trigger request when backend is down. Confirm UI displays clear error overlay instead of blank screen.
- [ ] **Database Disconnection:** Simulate MySQL failure. Confirm API degrades gracefully with standard 500 error structure.
- [ ] **Vision / Gemini API Failure:** Simulate API timeout/quota exhaust. Confirm pipeline returns usable fallback status.
- [ ] **Expired Session:** Attempt protected actions with stale or missing cookies. Confirm redirect to login.

## 3. Extension & Scraping Stability
- [ ] **Scraped Page Structure Change:** Run scraper against modified page layout. Confirm timeout wrapper catches error without crashing Flask.
- [ ] **Rapid-Fire Requests:** Send duplicate consecutive calls to `/api/scrape`. Confirm request throttling/de-duplication.
- [ ] **Category Matrix Testing:** Run overlay on 5 Amazon/Flipkart URLs across Food, Skincare, Electronics, Book, and General.

## 4. Race Conditions
- [ ] **Concurrent Gift Redemption:** Execute simultaneous redemption requests for same user tokens (coordinated with Dev 5). Confirm atomic deduction prevents double spending.