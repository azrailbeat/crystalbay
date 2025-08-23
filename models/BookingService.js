const { supabase, memoryStorage, isSupabaseAvailable } = require('./index');

class BookingService {
    static async createBooking(bookingData) {
        const booking = {
            ...bookingData,
            created_at: new Date().toISOString()
        };

        if (isSupabaseAvailable()) {
            try {
                const { data, error } = await supabase
                    .from('bookings')
                    .insert([booking])
                    .select();
                
                if (error) throw error;
                return data[0];
            } catch (error) {
                console.error('Error creating booking in database:', error);
                return this.createBookingFallback(booking);
            }
        } else {
            return this.createBookingFallback(booking);
        }
    }

    static createBookingFallback(bookingData) {
        const booking = {
            ...bookingData,
            id: (memoryStorage.bookings.length + 1).toString()
        };
        
        memoryStorage.bookings.push(booking);
        console.log('Used fallback storage to create booking:', booking.id);
        return booking;
    }

    static async getBookings(limit = 100, status = null) {
        if (isSupabaseAvailable()) {
            try {
                let query = supabase
                    .from('bookings')
                    .select('*')
                    .limit(limit)
                    .order('created_at', { ascending: false });

                if (status) {
                    query = query.eq('status', status);
                }

                const { data, error } = await query;
                if (error) throw error;
                return data || [];
            } catch (error) {
                console.error('Error getting bookings from database:', error);
                return this.getBookingsFallback(limit, status);
            }
        } else {
            return this.getBookingsFallback(limit, status);
        }
    }

    static getBookingsFallback(limit = 100, status = null) {
        let filteredBookings = [...memoryStorage.bookings];

        if (status) {
            filteredBookings = filteredBookings.filter(booking => booking.status === status);
        }

        // Sort by created_at, newest first
        filteredBookings.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        return filteredBookings.slice(0, limit);
    }

    static async getBooking(bookingId) {
        if (isSupabaseAvailable()) {
            try {
                const { data, error } = await supabase
                    .from('bookings')
                    .select('*')
                    .eq('id', bookingId)
                    .single();
                
                if (error) throw error;
                return data;
            } catch (error) {
                console.error('Error getting booking from database:', error);
                return memoryStorage.bookings.find(booking => booking.id === bookingId) || null;
            }
        } else {
            return memoryStorage.bookings.find(booking => booking.id === bookingId) || null;
        }
    }

    static async updateBookingStatus(bookingId, status) {
        const updateData = {
            status,
            updated_at: new Date().toISOString()
        };

        if (isSupabaseAvailable()) {
            try {
                const { data, error } = await supabase
                    .from('bookings')
                    .update(updateData)
                    .eq('id', bookingId)
                    .select();
                
                if (error) throw error;
                return data[0];
            } catch (error) {
                console.error('Error updating booking status in database:', error);
                return this.updateBookingFallback(bookingId, updateData);
            }
        } else {
            return this.updateBookingFallback(bookingId, updateData);
        }
    }

    static updateBookingFallback(bookingId, updateData) {
        const bookingIndex = memoryStorage.bookings.findIndex(booking => booking.id === bookingId);
        if (bookingIndex !== -1) {
            memoryStorage.bookings[bookingIndex] = {
                ...memoryStorage.bookings[bookingIndex],
                ...updateData
            };
            return memoryStorage.bookings[bookingIndex];
        }
        return null;
    }

    static formatStatus(status) {
        const statusMap = {
            'pending': 'В ожидании',
            'confirmed': 'Подтверждено',
            'cancelled': 'Отменено'
        };
        return statusMap[status] || status;
    }
}

module.exports = BookingService;