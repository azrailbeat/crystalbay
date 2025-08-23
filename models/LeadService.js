const { supabase, memoryStorage, isSupabaseAvailable } = require('./index');

class LeadService {
    static async createLead(leadData) {
        const timestamp = new Date().toISOString();
        const lead = {
            ...leadData,
            created_at: timestamp,
            status: leadData.status || 'new'
        };

        if (isSupabaseAvailable()) {
            try {
                const { data, error } = await supabase
                    .from('leads')
                    .insert([lead])
                    .select();
                
                if (error) throw error;
                return data[0];
            } catch (error) {
                console.error('Error creating lead in database:', error);
                return this.createLeadFallback(lead);
            }
        } else {
            return this.createLeadFallback(lead);
        }
    }

    static createLeadFallback(leadData) {
        const lead = {
            ...leadData,
            id: (memoryStorage.leads.length + 1).toString()
        };
        
        memoryStorage.leads.push(lead);
        console.log('Used fallback storage to create lead:', lead.id);
        return lead;
    }

    static async getLeads(limit = 100, status = null, agentId = null) {
        if (isSupabaseAvailable()) {
            try {
                let query = supabase
                    .from('leads')
                    .select('*')
                    .limit(limit)
                    .order('created_at', { ascending: false });

                if (status) {
                    query = query.eq('status', status);
                }

                if (agentId) {
                    query = query.eq('agent_id', agentId);
                }

                const { data, error } = await query;
                if (error) throw error;
                return data || [];
            } catch (error) {
                console.error('Error getting leads from database:', error);
                return this.getLeadsFallback(limit, status, agentId);
            }
        } else {
            return this.getLeadsFallback(limit, status, agentId);
        }
    }

    static getLeadsFallback(limit = 100, status = null, agentId = null) {
        let filteredLeads = [...memoryStorage.leads];

        if (status) {
            filteredLeads = filteredLeads.filter(lead => lead.status === status);
        }

        if (agentId) {
            filteredLeads = filteredLeads.filter(lead => lead.agent_id === agentId);
        }

        // Sort by created_at, newest first
        filteredLeads.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        return filteredLeads.slice(0, limit);
    }

    static async getLead(leadId) {
        if (isSupabaseAvailable()) {
            try {
                const { data, error } = await supabase
                    .from('leads')
                    .select('*')
                    .eq('id', leadId)
                    .single();
                
                if (error) throw error;
                return data;
            } catch (error) {
                console.error('Error getting lead from database:', error);
                return this.getLeadFallback(leadId);
            }
        } else {
            return this.getLeadFallback(leadId);
        }
    }

    static getLeadFallback(leadId) {
        return memoryStorage.leads.find(lead => lead.id === leadId) || null;
    }

    static async updateLead(leadId, updateData) {
        const timestamp = new Date().toISOString();
        const data = {
            ...updateData,
            updated_at: timestamp
        };

        if (isSupabaseAvailable()) {
            try {
                const { data: updatedData, error } = await supabase
                    .from('leads')
                    .update(data)
                    .eq('id', leadId)
                    .select();
                
                if (error) throw error;
                return updatedData[0];
            } catch (error) {
                console.error('Error updating lead in database:', error);
                return this.updateLeadFallback(leadId, data);
            }
        } else {
            return this.updateLeadFallback(leadId, data);
        }
    }

    static updateLeadFallback(leadId, updateData) {
        const leadIndex = memoryStorage.leads.findIndex(lead => lead.id === leadId);
        if (leadIndex !== -1) {
            memoryStorage.leads[leadIndex] = {
                ...memoryStorage.leads[leadIndex],
                ...updateData
            };
            return memoryStorage.leads[leadIndex];
        }
        return null;
    }

    static async updateLeadStatus(leadId, status) {
        return this.updateLead(leadId, { status });
    }

    static async addLeadInteraction(leadId, interactionData) {
        const interaction = {
            ...interactionData,
            lead_id: leadId,
            created_at: new Date().toISOString()
        };

        if (isSupabaseAvailable()) {
            try {
                const { data, error } = await supabase
                    .from('lead_interactions')
                    .insert([interaction])
                    .select();
                
                if (error) throw error;
                return data[0];
            } catch (error) {
                console.error('Error adding interaction to database:', error);
                return this.addInteractionFallback(interaction);
            }
        } else {
            return this.addInteractionFallback(interaction);
        }
    }

    static addInteractionFallback(interactionData) {
        const interaction = {
            ...interactionData,
            id: (memoryStorage.leadInteractions.length + 1).toString()
        };
        
        memoryStorage.leadInteractions.push(interaction);
        console.log('Used fallback storage to add interaction for lead:', interaction.lead_id);
        return interaction;
    }

    static async getLeadInteractions(leadId) {
        if (isSupabaseAvailable()) {
            try {
                const { data, error } = await supabase
                    .from('lead_interactions')
                    .select('*')
                    .eq('lead_id', leadId)
                    .order('created_at', { ascending: false });
                
                if (error) throw error;
                return data || [];
            } catch (error) {
                console.error('Error getting interactions from database:', error);
                return this.getInteractionsFallback(leadId);
            }
        } else {
            return this.getInteractionsFallback(leadId);
        }
    }

    static getInteractionsFallback(leadId) {
        return memoryStorage.leadInteractions
            .filter(interaction => interaction.lead_id === leadId)
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }

    static async getLeadByExternalId(externalId, externalSource) {
        if (isSupabaseAvailable()) {
            try {
                const { data, error } = await supabase
                    .from('leads')
                    .select('*')
                    .eq('external_id', externalId)
                    .eq('external_source', externalSource)
                    .single();
                
                if (error) throw error;
                return data;
            } catch (error) {
                console.error('Error getting lead by external ID:', error);
                return memoryStorage.leads.find(lead => 
                    lead.external_id === externalId && lead.external_source === externalSource
                ) || null;
            }
        } else {
            return memoryStorage.leads.find(lead => 
                lead.external_id === externalId && lead.external_source === externalSource
            ) || null;
        }
    }

    static async deleteAllLeads() {
        memoryStorage.leads = [];
        
        if (isSupabaseAvailable()) {
            try {
                const { error } = await supabase
                    .from('leads')
                    .delete()
                    .neq('id', '0'); // Delete all leads
                
                if (error) throw error;
                console.log('All leads deleted from database');
                return true;
            } catch (error) {
                console.error('Error deleting leads from database:', error);
                return false;
            }
        }
        return true;
    }
}

module.exports = LeadService;