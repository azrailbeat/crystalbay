# Crystal Bay IP Whitelist Request
## Запрос на добавление IP-адреса в белый список

**Дата**: 22 июля 2025  
**Система**: Crystal Bay Travel - SAMO API Integration  
**OAuth Token**: 27bd59a7ac67422189789f0188167379  

---

## 🔒 **CRITICAL: IP Address Needs Whitelisting**

### **Production Server IP Address to Whitelist:**
```
34.117.33.233
```

**Server Details:**
- **Platform**: Replit Production Deployment
- **Domain**: crystal-bay.replit.app
- **Region**: Global (Cloudflare CDN)
- **Purpose**: Production SAMO API integration for tour booking system

---

## 📊 **Current Status**

**✅ Working Components:**
- OAuth token authentication (27bd59a7ac67422189789f0188167379)
- API endpoint connectivity (https://booking-kz.crystalbay.com/export/default.php)
- Request formatting according to SAMO API documentation
- System deployed and operational

**❌ Blocked by IP Restriction:**
```
HTTP 403 Forbidden
Error: Client Error: Forbidden for url: https://booking-kz.crystalbay.com/export/default.php
```

---

## 🧪 **Test Requests Being Blocked**

The following legitimate API requests are currently blocked:

### 1. Departure Cities Request
```
POST https://booking-kz.crystalbay.com/export/default.php
Data: {
  "samo_action": "api",
  "version": "1.0", 
  "type": "json",
  "action": "SearchTour_TOWNFROMS",
  "oauth_token": "27bd59a7ac67422189789f0188167379"
}
```

### 2. Countries List Request  
```
POST https://booking-kz.crystalbay.com/export/default.php
Data: {
  "samo_action": "api",
  "version": "1.0",
  "type": "json", 
  "action": "SearchTour_COUNTRIES",
  "oauth_token": "27bd59a7ac67422189789f0188167379"
}
```

### 3. Tour Search Request
```
POST https://booking-kz.crystalbay.com/export/default.php
Data: {
  "samo_action": "api",
  "version": "1.0",
  "type": "json",
  "action": "SearchTour_TOURS",
  "oauth_token": "27bd59a7ac67422189789f0188167379",
  "STATEINC": "35",
  "TOWNFROMINC": "1"
}
```

---

## 📋 **Request Details for Crystal Bay Support**

**To Crystal Bay Technical Support:**

Please add the following IP address to the SAMO API whitelist for our production system:

**IP to Whitelist**: `34.117.33.233`

**Account Details:**
- OAuth Token: 27bd59a7ac67422189789f0188167379
- System: Crystal Bay Travel Multi-Channel Booking System
- Usage: Production tour search and booking integration

**Verification Steps After Whitelisting:**
1. We will test SearchTour_TOWNFROMS endpoint
2. We will test SearchTour_COUNTRIES endpoint  
3. We will verify tour search functionality
4. We will confirm booking creation capability

---

## 🔧 **Technical Integration Details**

**API Usage Pattern:**
- Standard SAMO API format with samo_action=api
- JSON response format (type=json)
- Version 1.0 compliance
- Proper OAuth token authentication
- All requests follow official SAMO documentation

**Expected Response After Whitelisting:**
Instead of 403 Forbidden, we should receive:
```json
{
  "result": "success",
  "data": [...],
  "error": ""
}
```

---

## 📞 **Contact Information**

**Development Team**: Crystal Bay Travel Integration Team  
**Urgency**: High Priority - Production system deployment blocked  
**Expected Resolution**: Within 24-48 hours  

Once IP is whitelisted, our production system will be fully operational for:
- Real-time tour searches
- Booking management
- Customer inquiries
- Multi-channel lead processing

---

**Please confirm when IP 34.117.33.233 has been added to the whitelist.**

*Request submitted: July 22, 2025*