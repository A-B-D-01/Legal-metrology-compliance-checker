# MetaMark Hardware-Free Demo Script

## 1. Flow Overview
Demonstrate full end-to-end Legal Metrology compliance checks without any physical hardware dependencies.

## 2. Walkthrough Steps
1. **User Auth:** Log in / Sign up as Seller/Customer in web app popup.
2. **Seller Pre-Check (Software Replacement):** 
   - Navigate to `/seller-verification` (or `/seller-precheck`).
   - Upload product image & description[cite: 1].
   - Manually type actual weight (e.g., `250g`) and dimensions (e.g., `10x5x2 cm`) into text inputs[cite: 1].
3. **Compliance Report Generation:** 
   - Trigger analysis; review Grade, Legal Metrology field extraction, and violation flags[cite: 1].
4. **Chatbot Support:** 
   - Query legal metrology rules using RAG chatbot[cite: 1].
5. **Reward Redemption:** 
   - Check Meta-Token balance and redeem a reward[cite: 1].

## 3. Hardware-Free Verification Checklist
- [x] Zero ESP32 gateway network requests[cite: 1].
- [x] Zero physical sensor/load cell dependencies[cite: 1].
- [x] Pure software form input for weight/dimensions[cite: 1].