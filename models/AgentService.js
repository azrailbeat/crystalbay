const { supabase, memoryStorage, isSupabaseAvailable } = require('./index');

class AgentService {
    static async createAgent(agentData) {
        const agent = {
            ...agentData,
            created_at: new Date().toISOString()
        };

        if (isSupabaseAvailable()) {
            try {
                const { data, error } = await supabase
                    .from('agents')
                    .insert([agent])
                    .select();
                
                if (error) throw error;
                return data[0];
            } catch (error) {
                console.error('Error creating agent in database:', error);
                return this.createAgentFallback(agent);
            }
        } else {
            return this.createAgentFallback(agent);
        }
    }

    static createAgentFallback(agentData) {
        const agent = {
            ...agentData,
            id: (memoryStorage.agents.length + 1).toString()
        };
        
        memoryStorage.agents.push(agent);
        console.log('Used fallback storage to create agent:', agent.id);
        return agent;
    }

    static async getAgents(limit = 100, status = null) {
        if (isSupabaseAvailable()) {
            try {
                let query = supabase
                    .from('agents')
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
                console.error('Error getting agents from database:', error);
                return this.getAgentsFallback(limit, status);
            }
        } else {
            return this.getAgentsFallback(limit, status);
        }
    }

    static getAgentsFallback(limit = 100, status = null) {
        let filteredAgents = [...memoryStorage.agents];

        if (status) {
            filteredAgents = filteredAgents.filter(agent => agent.status === status);
        }

        // Sort by created_at, newest first
        filteredAgents.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        return filteredAgents.slice(0, limit);
    }

    static async getAgent(agentId) {
        if (isSupabaseAvailable()) {
            try {
                const { data, error } = await supabase
                    .from('agents')
                    .select('*')
                    .eq('id', agentId)
                    .single();
                
                if (error) throw error;
                return data;
            } catch (error) {
                console.error('Error getting agent from database:', error);
                return memoryStorage.agents.find(agent => agent.id === agentId) || null;
            }
        } else {
            return memoryStorage.agents.find(agent => agent.id === agentId) || null;
        }
    }

    static async updateAgent(agentId, updateData) {
        const data = {
            ...updateData,
            updated_at: new Date().toISOString()
        };

        if (isSupabaseAvailable()) {
            try {
                const { data: updatedData, error } = await supabase
                    .from('agents')
                    .update(data)
                    .eq('id', agentId)
                    .select();
                
                if (error) throw error;
                return updatedData[0];
            } catch (error) {
                console.error('Error updating agent in database:', error);
                return this.updateAgentFallback(agentId, data);
            }
        } else {
            return this.updateAgentFallback(agentId, data);
        }
    }

    static updateAgentFallback(agentId, updateData) {
        const agentIndex = memoryStorage.agents.findIndex(agent => agent.id === agentId);
        if (agentIndex !== -1) {
            memoryStorage.agents[agentIndex] = {
                ...memoryStorage.agents[agentIndex],
                ...updateData
            };
            return memoryStorage.agents[agentIndex];
        }
        return null;
    }

    static async deleteAgent(agentId) {
        if (isSupabaseAvailable()) {
            try {
                const { error } = await supabase
                    .from('agents')
                    .delete()
                    .eq('id', agentId);
                
                if (error) throw error;
                return true;
            } catch (error) {
                console.error('Error deleting agent from database:', error);
                return this.deleteAgentFallback(agentId);
            }
        } else {
            return this.deleteAgentFallback(agentId);
        }
    }

    static deleteAgentFallback(agentId) {
        const agentIndex = memoryStorage.agents.findIndex(agent => agent.id === agentId);
        if (agentIndex !== -1) {
            memoryStorage.agents.splice(agentIndex, 1);
            return true;
        }
        return false;
    }

    static formatRole(role) {
        const roleMap = {
            'admin': 'Администратор',
            'manager': 'Менеджер',
            'agent': 'Агент'
        };
        return roleMap[role] || role;
    }

    static formatStatus(status) {
        const statusMap = {
            'active': 'Активен',
            'inactive': 'Неактивен'
        };
        return statusMap[status] || status;
    }
}

module.exports = AgentService;