/**
 * Crystal Bay Travel Lead Capture Widget
 * Embeddable widget for capturing leads from external websites
 */

(function() {
    'use strict';
    
    // Configuration
    const WIDGET_CONFIG = {
        apiUrl: 'https://your-domain.replit.app/api/leads/import/widget',
        cssFramework: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'
    };
    
    // Widget HTML template
    const WIDGET_HTML = `
        <div id="crystal-bay-widget" class="card shadow-sm" style="max-width: 400px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">🏖️ Планируете отпуск?</h5>
                <small>Получите персональное предложение</small>
            </div>
            <div class="card-body">
                <form id="crystal-bay-form">
                    <div class="mb-3">
                        <label for="cb-name" class="form-label">Ваше имя *</label>
                        <input type="text" class="form-control" id="cb-name" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label for="cb-email" class="form-label">Email *</label>
                        <input type="email" class="form-control" id="cb-email" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="cb-phone" class="form-label">Телефон</label>
                        <input type="tel" class="form-control" id="cb-phone" name="phone" placeholder="+7 (xxx) xxx-xx-xx">
                    </div>
                    <div class="mb-3">
                        <label for="cb-message" class="form-label">Что вас интересует?</label>
                        <textarea class="form-control" id="cb-message" name="message" rows="3" placeholder="Расскажите о ваших планах на отпуск..."></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary w-100" id="cb-submit">
                        Получить предложение
                    </button>
                    <div id="cb-status" class="mt-2" style="display: none;"></div>
                </form>
            </div>
            <div class="card-footer text-muted text-center">
                <small>Powered by <strong>Crystal Bay Travel</strong></small>
            </div>
        </div>
    `;
    
    // Widget functionality
    class CrystalBayWidget {
        constructor(containerId, options = {}) {
            this.containerId = containerId;
            this.options = {
                ...WIDGET_CONFIG,
                ...options
            };
            this.init();
        }
        
        init() {
            this.loadCSS();
            this.renderWidget();
            this.attachEventListeners();
            this.trackPageView();
        }
        
        loadCSS() {
            if (!document.querySelector('link[href*="bootstrap"]')) {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = this.options.cssFramework;
                document.head.appendChild(link);
            }
        }
        
        renderWidget() {
            const container = document.getElementById(this.containerId);
            if (container) {
                container.innerHTML = WIDGET_HTML;
            } else {
                console.error(`Container ${this.containerId} not found`);
            }
        }
        
        attachEventListeners() {
            const form = document.getElementById('crystal-bay-form');
            if (form) {
                form.addEventListener('submit', (e) => this.handleSubmit(e));
            }
        }
        
        async handleSubmit(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('cb-submit');
            const statusDiv = document.getElementById('cb-status');
            
            // Disable submit button
            submitBtn.disabled = true;
            submitBtn.textContent = 'Отправляем...';
            
            try {
                const formData = new FormData(e.target);
                const data = {
                    name: formData.get('name'),
                    email: formData.get('email'),
                    phone: formData.get('phone'),
                    message: formData.get('message'),
                    widget_id: 'crystal_bay_widget_v1',
                    page_url: window.location.href,
                    page_title: document.title,
                    referrer: document.referrer,
                    utm_source: this.getUrlParam('utm_source'),
                    utm_campaign: this.getUrlParam('utm_campaign'),
                    utm_medium: this.getUrlParam('utm_medium'),
                    timestamp: new Date().toISOString()
                };
                
                const response = await fetch(this.options.apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    this.showSuccess();
                    this.trackConversion();
                } else {
                    this.showError(result.error || 'Произошла ошибка');
                }
                
            } catch (error) {
                console.error('Widget submission error:', error);
                this.showError('Не удалось отправить запрос. Попробуйте позже.');
            } finally {
                // Re-enable submit button
                submitBtn.disabled = false;
                submitBtn.textContent = 'Получить предложение';
            }
        }
        
        showSuccess() {
            const statusDiv = document.getElementById('cb-status');
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    ✅ Спасибо! Ваш запрос отправлен. Мы свяжемся с вами в течение 24 часов.
                </div>
            `;
            statusDiv.style.display = 'block';
            
            // Clear form
            document.getElementById('crystal-bay-form').reset();
        }
        
        showError(message) {
            const statusDiv = document.getElementById('cb-status');
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    ❌ ${message}
                </div>
            `;
            statusDiv.style.display = 'block';
        }
        
        getUrlParam(param) {
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.get(param) || '';
        }
        
        trackPageView() {
            // Simple analytics tracking
            if (typeof gtag !== 'undefined') {
                gtag('event', 'widget_view', {
                    event_category: 'crystal_bay_widget',
                    event_label: window.location.href
                });
            }
        }
        
        trackConversion() {
            // Track successful form submission
            if (typeof gtag !== 'undefined') {
                gtag('event', 'conversion', {
                    event_category: 'crystal_bay_widget',
                    event_label: 'lead_generated'
                });
            }
        }
    }
    
    // Auto-initialize if container exists
    document.addEventListener('DOMContentLoaded', function() {
        if (document.getElementById('crystal-bay-lead-widget')) {
            new CrystalBayWidget('crystal-bay-lead-widget');
        }
    });
    
    // Export for manual initialization
    window.CrystalBayWidget = CrystalBayWidget;
    
})();