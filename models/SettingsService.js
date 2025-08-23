const { supabase, memoryStorage, isSupabaseAvailable } = require('./index');

class SettingsService {
    static async getSamoSettings() {
        if (isSupabaseAvailable()) {
            try {
                const { data, error } = await supabase
                    .from('settings')
                    .select('*')
                    .eq('category', 'samo_api');
                
                if (error) throw error;
                
                if (data && data.length > 0) {
                    const settings = {};
                    data.forEach(item => {
                        settings[item.key] = item.value;
                    });
                    return settings;
                }
                return memoryStorage.settings.samo_api;
            } catch (error) {
                console.error('Error getting SAMO settings from database:', error);
                return memoryStorage.settings.samo_api;
            }
        } else {
            return memoryStorage.settings.samo_api;
        }
    }

    static async updateSamoSetting(key, value) {
        if (isSupabaseAvailable()) {
            try {
                // Check if setting exists
                const { data: existingData, error: selectError } = await supabase
                    .from('settings')
                    .select('id')
                    .eq('category', 'samo_api')
                    .eq('key', key);

                if (selectError) throw selectError;

                if (existingData && existingData.length > 0) {
                    // Update existing
                    const { error: updateError } = await supabase
                        .from('settings')
                        .update({ value: value.toString() })
                        .eq('category', 'samo_api')
                        .eq('key', key);
                    
                    if (updateError) throw updateError;
                } else {
                    // Insert new
                    const { error: insertError } = await supabase
                        .from('settings')
                        .insert([{
                            category: 'samo_api',
                            key,
                            value: value.toString(),
                            created_at: new Date().toISOString()
                        }]);
                    
                    if (insertError) throw insertError;
                }

                console.log(`SAMO setting updated: ${key} = ${value}`);
                return true;
            } catch (error) {
                console.error('Error updating SAMO setting:', error);
                // Fallback to memory storage
                memoryStorage.settings.samo_api[key] = value;
                return false;
            }
        } else {
            memoryStorage.settings.samo_api[key] = value;
            return true;
        }
    }

    static async getSetting(category, key, defaultValue = null) {
        if (category === 'samo_api') {
            const settings = await this.getSamoSettings();
            return settings[key] || defaultValue;
        }
        // Add other categories as needed
        return defaultValue;
    }

    static async getAiConfig() {
        if (isSupabaseAvailable()) {
            try {
                const { data, error } = await supabase
                    .from('settings')
                    .select('*')
                    .eq('category', 'ai_config');
                
                if (error) throw error;
                
                if (data && data.length > 0) {
                    const config = {};
                    data.forEach(item => {
                        try {
                            // Try to parse as JSON for complex values
                            config[item.key] = JSON.parse(item.value);
                        } catch {
                            // Use as string for simple values
                            config[item.key] = item.value;
                        }
                    });
                    return config;
                }
                return memoryStorage.aiConfig;
            } catch (error) {
                console.error('Error getting AI config from database:', error);
                return memoryStorage.aiConfig;
            }
        } else {
            return memoryStorage.aiConfig;
        }
    }

    static async updateAiConfig(config) {
        if (isSupabaseAvailable()) {
            try {
                for (const [key, value] of Object.entries(config)) {
                    const stringValue = typeof value === 'object' ? JSON.stringify(value) : value.toString();
                    
                    // Check if setting exists
                    const { data: existingData, error: selectError } = await supabase
                        .from('settings')
                        .select('id')
                        .eq('category', 'ai_config')
                        .eq('key', key);

                    if (selectError) throw selectError;

                    if (existingData && existingData.length > 0) {
                        // Update existing
                        const { error: updateError } = await supabase
                            .from('settings')
                            .update({ value: stringValue })
                            .eq('category', 'ai_config')
                            .eq('key', key);
                        
                        if (updateError) throw updateError;
                    } else {
                        // Insert new
                        const { error: insertError } = await supabase
                            .from('settings')
                            .insert([{
                                category: 'ai_config',
                                key,
                                value: stringValue,
                                created_at: new Date().toISOString()
                            }]);
                        
                        if (insertError) throw insertError;
                    }
                }

                console.log('AI config updated successfully');
                return true;
            } catch (error) {
                console.error('Error updating AI config:', error);
                // Fallback to memory storage
                Object.assign(memoryStorage.aiConfig, config);
                return false;
            }
        } else {
            Object.assign(memoryStorage.aiConfig, config);
            return true;
        }
    }
}

module.exports = SettingsService;