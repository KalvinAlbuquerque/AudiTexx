import axios from 'axios';

const API_URL = import.meta.env.VITE_REACT_APP_API_URL;

if (!API_URL) {
    console.error('VITE_REACT_APP_API_URL não está definido nas variáveis de ambiente.');
}

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    // Definir um timeout geral para todas as requisições se desejar, mas vamos focar na específica
    // timeout: 30000, // Exemplo: 30 segundos
});

export interface Lista {
    idLista: string;
    nomeLista: string;
    relatorioGerado?: boolean;
}

export interface ScanData {
    config_id?: string; // Propriedade de WAS Scan
    name: string;
    target?: string; // Propriedade de WAS Scan
    description?: string;
    created_at?: string; // Propriedade de WAS Scan
    last_scan?: { // Propriedade de WAS Scan (última varredura)
        scan_id?: string;
        uuid?: string;
        status?: string;
    };
    owner_id?: string; // Propriedade de WAS Scan
    owner?: { name: string };
    id?: string; // Propriedade de VM Scan (ID numérico principal)
    last_modification_date?: string; // Propriedade comum (pode vir de WAS ou VM)
    
    // --- INÍCIO DA CORREÇÃO APLICADA AQUI: Adicionando a propriedade 'history' ---
    history?: Array<{ // Propriedade específica de VM Scan (histórico de execuções)
        uuid: string; // O UUID do histórico de scan, usado para download
        scan_id?: string; // ID do scan dentro do histórico (pode ser o mesmo que o 'id' principal)
        status?: string; // Status da execução do histórico
        last_modification_date?: string; // Data de modificação do histórico (para encontrar o mais recente)
        // Adicione outras propriedades do objeto 'history' se forem relevantes
    }>;
    // --- FIM DA CORREÇÃO APLICADA AQUI ---
}

export interface Folder {
    id: string;
    name: string;
}

export interface ReportGenerated {
    id: string;
    nome: string;
}

export const listsApi = {
    getAllLists: async (): Promise<Lista[]> => {
        const response = await api.get('/lists/getTodasAsListas/');
        return response.data;
    },

    createList: async (nomeLista: string): Promise<{ message: string; idLista: string }> => {
        const response = await api.post('/lists/criarLista/', { nomeLista });
        return response.data;
    },

    editListName: async (id: string, novoNome: string): Promise<{ message: string }> => {
        const response = await api.post('/lists/editarNomeLista/', { id, novoNome });
        return response.data;
    },

    deleteList: async (idLista: string): Promise<{ message: string }> => {
        const response = await api.post('/lists/excluirLista/', { idLista });
        return response.data;
    },

    getWebAppScansFromList: async (nomeLista: string): Promise<string[]> => {
        const response = await api.post('/lists/getScansDeLista/', { nomeLista });
        return response.data;
    },

    addWebAppScanToList: async (nomeLista: string, scans: { items: ScanData[] }): Promise<{ message: string }> => {
        // Aumentando o timeout para 5 minutos (300000 ms) para esta operação
        const response = await api.post('/lists/adicionarWAPPScanALista/', { nomeLista, scans }, { timeout: 300000 });
        return response.data;
    },

    clearWebAppScansFromList: async (nomeLista: string): Promise<{ message: string }> => {
        const response = await api.post('/lists/limparScansDeLista/', { nomeLista });
        return response.data;
    },

    getVMScanFromList: async (nomeLista: string): Promise<[string, string] | null> => {
        try {
            const response = await api.post('/lists/getVMScansDeLista/', { nomeLista });
            return response.data;
        } catch (error: any) {
            if (axios.isAxiosError(error) && error.response?.status === 404) {
                return null;
            }
            throw error;
        }
    },

    addVMScanToList: async (nomeLista: string, idScan: string, nomeScan: string, criadoPor: string, idNmr: string): Promise<{ message: string }> => {
        const response = await api.post('/lists/adicionarVMScanALista/', { nomeLista, idScan, nomeScan, criadoPor, idNmr });
        return response.data;
    },

    clearVMScanFromList: async (nomeLista: string): Promise<{ message: string }> => {
        const response = await api.post('/lists/limparVMScansDeLista/', { nomeLista });
        return response.data;
    },
};

export const scansApi = {
    getWebAppScansFromFolder: async (nomeUsuario: string, nomePasta: string): Promise<ScanData[]> => {
        const response = await api.post('/scans/webapp/scansfromfolderofuser/', { nomeUsuario, nomePasta });
        return response.data.items;
    },

    downloadWebAppScans: async (scans: { items: ScanData[] }, usuario: string, nomePasta: string): Promise<{ message: string }> => {
        const response = await api.post('/scans/webapp/downloadscans/', { scans, usuario, nomePasta });
        return response.data;
    },

    getVMScanByName: async (name: string): Promise<ScanData | null> => {
        try {
            const response = await api.post('/scans/vm/getScanByName/', { name });
            return response.data;
        } catch (error: any) {
            if (axios.isAxiosError(error) && error.response?.status === 404) {
                return null;
            }
            throw error;
        }
    },

    downloadVMScan: async (nomeListaId: string, idScan: string, historyId: string): Promise<{ message: string }> => {
        const response = await api.post('/scans/vm/downloadscans/', { nomeListaId, idScan, historyId });
        return response.data;
    },
};

export const reportsApi = {
    getGeneratedReports: async (): Promise<ReportGenerated[]> => {
        const response = await api.get('/reports/getRelatoriosGerados/');
        return response.data;
    },

    deleteReport: async (relatorio_id: string): Promise<{ message: string }> => {
        const response = await api.delete(`/reports/deleteRelatorio/${relatorio_id}`);
        return response.data;
    },

    deleteAllReports: async (): Promise<{ message: string }> => {
        const response = await api.delete('/reports/deleteAllRelatorios/');
        return response.data;
    },

    generateReportForList: async (reportData: any): Promise<string> => {
        const response = await api.post('/reports/gerarRelatorioDeLista/', reportData);
        return response.data;
    },

    getMissingVulnerabilities: async (relatorioId: string, type: 'sites' | 'servers'): Promise<string[]> => {
        const response = await api.get(`/reports/getRelatorioMissingVulnerabilities?relatorioId=${relatorioId}&type=${type}`);
        return response.data.content;
    },

    downloadReportPdf: async (idRelatorio: string): Promise<Blob> => {
        const response = await api.post('/reports/baixarRelatorioPdf/', { idRelatorio }, { responseType: 'blob' });
        return response.data;
    },
};

export const vulnerabilitiesApi = {
    getAllVulnerabilities: async (type: 'sites' | 'servers'): Promise<any[]> => {
        const response = await api.get(`/vulnerabilities/getVulnerabilidades/?type=${type}`);
        return response.data;
    },

    addVulnerability: async (type: 'sites' | 'servers', data: any): Promise<{ message: string }> => {
        const response = await api.post('/vulnerabilities/addVulnerabilidade/', { type, data });
        return response.data;
    },

    updateVulnerability: async (type: 'sites' | 'servers', oldName: string, data: any): Promise<{ message: string }> => {
        const response = await api.put('/vulnerabilities/updateVulnerabilidade/', { type, oldName, data });
        return response.data;
    },

    deleteVulnerability: async (type: 'sites' | 'servers', name: string): Promise<{ message: string }> => {
        const response = await api.delete('/vulnerabilities/deleteVulnerabilidade/', { data: { type, name } });
        return response.data;
    },

    uploadImage: async (formData: FormData): Promise<{ message: string; imagePath: string }> => {
        const response = await api.post('/vulnerabilities/uploadImage/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    getDescriptiveVulnerabilities: async (type: 'sites' | 'servers'): Promise<any[]> => {
        const response = await api.get(`/vulnerabilities/getDescritivos/?type=${type}`);
        return response.data;
    },
};