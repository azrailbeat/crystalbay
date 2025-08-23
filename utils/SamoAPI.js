const axios = require('axios');
const SettingsService = require('../models/SettingsService');

class SamoAPI {
    constructor() {
        this.baseUrl = 'https://booking.crystalbay.com/export/default.php';
        this.oauthToken = process.env.SAMO_OAUTH_TOKEN || '27bd59a7ac67422189789f0188167379';
        this.timeout = 30000;
        this.userAgent = 'Crystal Bay Travel Integration/1.0';
    }

    async makeRequest(action, additionalParams = {}) {
        const params = new URLSearchParams({
            samo_action: 'api',
            version: '1.0',
            type: 'json',
            action: action,
            oauth_token: this.oauthToken,
            ...additionalParams
        });

        try {
            const response = await axios.post(this.baseUrl, params, {
                headers: {
                    'User-Agent': this.userAgent,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout: this.timeout
            });

            return {
                success: true,
                data: response.data,
                status: response.status
            };
        } catch (error) {
            console.error(`SAMO API error for action ${action}:`, error.message);
            
            if (error.response) {
                if (error.response.status === 403) {
                    return {
                        success: false,
                        error: 'IP blocked or authentication failed',
                        status: 403,
                        message: 'IP заблокирован в SAMO API или проблема с токеном'
                    };
                }
                return {
                    success: false,
                    error: `HTTP ${error.response.status}: ${error.response.statusText}`,
                    status: error.response.status,
                    data: error.response.data
                };
            } else if (error.code === 'ECONNABORTED') {
                return {
                    success: false,
                    error: 'Request timeout',
                    message: 'Превышено время ожидания запроса'
                };
            } else {
                return {
                    success: false,
                    error: error.message,
                    message: 'Ошибка подключения к SAMO API'
                };
            }
        }
    }

    async getCurrencies() {
        return await this.makeRequest('SearchTour_CURRENCIES');
    }

    async getStates() {
        return await this.makeRequest('SearchTour_STATES');
    }

    async getTownFroms() {
        return await this.makeRequest('SearchTour_TOWNFROMS');
    }

    async getStars() {
        return await this.makeRequest('SearchTour_STARS');
    }

    async getMeals() {
        return await this.makeRequest('SearchTour_MEALS');
    }

    async searchTourPrices(searchParams) {
        const params = {
            requestid: searchParams.requestid || Date.now().toString(),
            stateid: searchParams.stateid || '',
            townfromid: searchParams.townfromid || '',
            checkin: searchParams.checkin || '',
            nights: searchParams.nights || '',
            adult: searchParams.adult || '2',
            child: searchParams.child || '0',
            childage1: searchParams.childage1 || '',
            childage2: searchParams.childage2 || '',
            childage3: searchParams.childage3 || '',
            hotelstars: searchParams.hotelstars || '',
            meals: searchParams.meals || '',
            pricemin: searchParams.pricemin || '',
            pricemax: searchParams.pricemax || '',
            currency: searchParams.currency || 'RUR'
        };

        return await this.makeRequest('SearchTour_TOURPRICES', params);
    }

    async getHotels(searchParams) {
        const params = {
            requestid: searchParams.requestid || Date.now().toString(),
            stateid: searchParams.stateid || '',
            townfromid: searchParams.townfromid || '',
            checkin: searchParams.checkin || '',
            nights: searchParams.nights || '',
            adult: searchParams.adult || '2',
            child: searchParams.child || '0',
            hotelstars: searchParams.hotelstars || '',
            meals: searchParams.meals || '',
            currency: searchParams.currency || 'RUR'
        };

        return await this.makeRequest('SearchTour_HOTELS', params);
    }

    async getTourInfo(searchParams) {
        const params = {
            requestid: searchParams.requestid || '',
            tourid: searchParams.tourid || '',
            checkin: searchParams.checkin || '',
            nights: searchParams.nights || '',
            adult: searchParams.adult || '2',
            child: searchParams.child || '0',
            currency: searchParams.currency || 'RUR'
        };

        return await this.makeRequest('SearchTour_TOURINFO', params);
    }

    async getActualization(searchParams) {
        const params = {
            requestid: searchParams.requestid || '',
            tourid: searchParams.tourid || '',
            subid: searchParams.subid || '',
            checkin: searchParams.checkin || '',
            nights: searchParams.nights || '',
            adult: searchParams.adult || '2',
            child: searchParams.child || '0',
            currency: searchParams.currency || 'RUR'
        };

        return await this.makeRequest('SearchTour_ACTUALIZATION', params);
    }

    // Test method for diagnostics
    async testConnection() {
        try {
            const result = await this.getCurrencies();
            return {
                connected: result.success,
                status: result.status || 'unknown',
                message: result.success ? 'Connected successfully' : result.error || 'Connection failed'
            };
        } catch (error) {
            return {
                connected: false,
                status: 'error',
                message: error.message
            };
        }
    }
}

module.exports = SamoAPI;